from collections import defaultdict, Counter

import numpy as np
from scipy.stats import mode

import nesmdb.apu


fs = 44100.
dt = 1. / fs


def ndf_to_rawsco(ndf):
  clock = float(ndf[0][1])
  if abs(clock - 1789773) < 2:
    # NTSC
    fc_rate_4 = 240.
    fc_rate_5 = 192.
  else:
    # PAL
    fc_rate_4 = 200.
    fc_rate_5 = 160.
  fc_rate_4_inv = 1. / fc_rate_4
  fc_rate_5_inv = 1. / fc_rate_5
  ndf = ndf[1:]

  # Gather timings
  samp_to_comms = defaultdict(list)
  nsamps = 0
  for comm in ndf:
    if comm[0] == 'wait':
      nsamps += comm[1]
    else:
      assert comm[0] == 'apu'
      samp_to_comms[nsamps].append(comm)

  # Set up APU register state
  ch_to_status = {'p1': 1, 'p2': 1, 'tr': 1, 'no': 1}
  ch_to_du = {'p1': 0, 'p2': 0}
  ch_to_lh = {'p1': 0, 'p2': 0, 'tr': 0, 'no': 0}
  ch_to_cv = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_vo = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_se = {'p1': 0, 'p2': 0}
  ch_to_sp = {'p1': 0, 'p2': 0}
  ch_to_sn = {'p1': 0, 'p2': 0}
  ch_to_ss = {'p1': 0, 'p2': 0}
  tr_lr = 0
  no_nl = 0
  no_np = 0

  # Set up APU auxiliary state
  ch_to_stimer = {'p1': 0, 'p2': 0}
  ch_to_timer = {'p1': 0, 'p2': 0, 'tr': 0}
  ch_to_timer_last = {'p1': 0, 'p2': 0, 'tr': 0}
  ch_to_length_counter = {'p1': 0, 'p2': 0, 'tr': 0, 'no': 0}
  ch_to_retrigger = {'p1': False, 'p2': False}
  ch_to_env = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_env_start_flag = {'p1': False, 'p2': False, 'no': False}
  ch_to_env_divider = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_env_decay_level = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_swe_divider = {'p1': 1, 'p2': 1}
  ch_to_swe_write = {'p1': False, 'p2': False}
  tr_linear_counter = 0
  tr_reload = False

  # Set up frame counter state
  fc_dt = fc_rate_4_inv
  fc_t = 0.
  fc_tick = 0
  fc_changed = False

  # Set up score state
  ch_to_midi = {'p1': 0, 'p2': 0, 'tr': 0, 'no': 0}
  rawsco = np.zeros((nsamps, 4, 4), dtype=np.uint8)

  # Set up function to sweep
  def sweep(ch):
    shifted = ch_to_timer[ch] >> ch_to_ss[ch]
    if ch == 'p1' and ch_to_sn[ch] == 1:
      shifted += 1
    shifted *= -1 if ch_to_sn[ch] == 1 else 1
    ch_to_stimer[ch] = ch_to_timer[ch] + shifted

  # Extract musical transcript by emulating APU
  for samp in xrange(nsamps):
    # Frame counter (in between samples)
    quarter_frame = False
    half_frame = False
    if fc_changed:
      quarter_frame = True
      half_frame = True
      fc_changed = False
    fc_t += dt
    if fc_t > fc_dt:
      quarter_frame = True
      half_frame = fc_tick % 2 == 1
      fc_t -= fc_dt
      fc_tick += 1

    if quarter_frame:
      # Update triangle linear counter
      if tr_reload:
        tr_linear_counter = tr_lr
      else:
        tr_linear_counter -= 1
      if ch_to_lh['tr'] == 0:
        tr_reload = False

      # Update envelopes
      for ch in ['p1', 'p2', 'no']:
        # https://wiki.nesdev.com/w/index.php/APU_Envelope
        # https://github.com/vgmrips/vgmplay/blob/master/VGMPlay/chips/np_nes_apu.c#L129
        divider = False
        if ch_to_env_start_flag[ch]:
          ch_to_env_start_flag[ch] = False
          ch_to_env_decay_level[ch] = 15
          ch_to_env_divider[ch] = 0
        else:
          ch_to_env_divider[ch] += 1
          if ch_to_env_divider[ch] > ch_to_vo[ch]:
            divider = True
            ch_to_env_divider[ch] = 0
        if divider:
          if ch_to_lh[ch] == 1 and ch_to_env_decay_level[ch] == 0:
            ch_to_env_decay_level[ch] = 15
          elif ch_to_env_decay_level[ch] > 0:
            ch_to_env_decay_level[ch] -= 1

    if half_frame:
      # Decrement counters
      for ch in ['p1', 'p2', 'tr', 'no']:
        if ch_to_lh[ch] == 0:
          ch_to_length_counter[ch] -= 1

      # Sweep updates
      # https://github.com/vgmrips/vgmplay/blob/master/VGMPlay/chips/np_nes_apu.c#L161
      for ch in ['p1', 'p2']:
        if ch_to_se[ch]:
          ch_to_swe_divider[ch] -= 1

          if ch_to_swe_divider[ch] <= 0:
            sweep(ch)
            if ch_to_timer[ch] >= 8 and ch_to_stimer[ch] < 0x800 and ch_to_ss[ch] > 0:
              ch_to_timer[ch] = 0 if ch_to_stimer[ch] < 0 else ch_to_stimer[ch]
            ch_to_swe_divider[ch] = ch_to_sp[ch] + 1

          if ch_to_swe_write[ch]:
            ch_to_swe_divider[ch] = ch_to_sp[ch] + 1
            ch_to_swe_write[ch] = False

    # Update state based on commands
    for comm in samp_to_comms[samp]:
      ch, fu, val = comm[1:4]
      if ch == 'dm' or fu == 'dm':
        continue

      if fu == 'du':
        ch_to_du[ch] = val
      elif fu == 'lh':
        ch_to_lh[ch] = val
      elif fu == 'cv':
        ch_to_cv[ch] = val
      elif fu == 'vo':
        ch_to_vo[ch] = val
      elif fu == 'se':
        ch_to_se[ch] = val
        ch_to_swe_write[ch] = True
        sweep(ch)
      elif fu == 'sp':
        ch_to_sp[ch] = val
      elif fu == 'sn':
        ch_to_sn[ch] = val
      elif fu == 'ss':
        ch_to_ss[ch] = val
      elif fu == 'th':
        ch_to_timer[ch] &= 0b00011111111
        ch_to_timer[ch] |= (val << 8)
        if ch == 'p1' or ch == 'p2':
          sweep(ch)
      elif fu == 'tl':
        ch_to_timer[ch] &= 0b11100000000
        ch_to_timer[ch] |= val
        if ch == 'p1' or ch == 'p2':
          sweep(ch)
      elif fu == 'll':
        if ch_to_status[ch] == 1:
          ch_to_length_counter[ch] = nesmdb.apu.length_counter_table[val]

        if ch == 'tr':
          tr_reload = True
        else:
          ch_to_retrigger[ch] = True
          ch_to_env_start_flag[ch] = True
      elif ch == 'ch':
        ch_to_status[fu] = val
        if val == 0:
          ch_to_length_counter[fu] = 0

      if ch == 'tr' and fu == 'lr':
        tr_lr = val

      if ch == 'no' and fu == 'nl':
        no_nl = val
      if ch == 'no' and fu == 'np':
        no_np = val

      if ch == 'fc' and fu == 'mo':
        fc_dt = fc_rate_5_inv if bool(val) else fc_rate_4_inv
        fc_t = 0.
        fc_tick = 0
        fc_changed = True

    # Fill in pulse score
    for i, ch in zip([0, 1], ['p1', 'p2']):
      if ch_to_length_counter[ch] > 0:
        vo = ch_to_vo[ch] if ch_to_cv[ch] else ch_to_env_decay_level[ch]
        if vo > 0 and ch_to_timer[ch] >= 8 and ch_to_stimer[ch] < 0x800:
          rawsco[samp, i, 0] = (ch_to_timer[ch] & 0b11100000000) >> 8
          rawsco[samp, i, 1] = (ch_to_timer[ch] & 0b00011111111)
          rawsco[samp, i, 2] = vo
      rawsco[samp, i, 3] = ch_to_du[ch]
      #rawsco[samp, i, 4] = int(ch_to_retrigger[ch])
      ch_to_retrigger[ch] = False

    # Fill in triangle score
    lc = min(ch_to_length_counter['tr'], tr_linear_counter)
    if lc > 0:
      rawsco[samp, 2, 0] = (ch_to_timer['tr'] & 0b11100000000) >> 8
      rawsco[samp, 2, 1] = (ch_to_timer['tr'] & 0b00011111111)
    #rawsco[samp, 2, 2] = 0
    #rawsco[samp, 2, 3] = 0

    # Fill in noise score
    if ch_to_length_counter['no'] > 0:
      vo = ch_to_vo['no'] if ch_to_cv['no'] else ch_to_env_decay_level['no']
      if vo > 0:
        #rawsco[samp, 3, 0] = 0
        rawsco[samp, 3, 1] = 16 - no_np
        rawsco[samp, 3, 2] = vo
    rawsco[samp, 3, 3] = no_nl

  return (clock, 44100, nsamps, rawsco)


def rawsco_to_ndf(rawsco):
  clock, rate, nsamps, score = rawsco

  if rate == 44100:
    ar = True
  else:
    ar = False

  max_i = score.shape[0]

  samp = 0
  t = 0.
  # ('apu', ch, func, func_val, natoms, offset)
  ndf = [
      ('clock', int(clock)),
      ('apu', 'ch', 'p1', 0, 0, 0),
      ('apu', 'ch', 'p2', 0, 0, 0),
      ('apu', 'ch', 'tr', 0, 0, 0),
      ('apu', 'ch', 'no', 0, 0, 0),
      ('apu', 'p1', 'du', 0, 1, 0),
      ('apu', 'p1', 'lh', 1, 1, 0),
      ('apu', 'p1', 'cv', 1, 1, 0),
      ('apu', 'p1', 'vo', 0, 1, 0),
      ('apu', 'p1', 'ss', 7, 2, 1), # This is necessary to prevent channel silence for low notes
      ('apu', 'p2', 'du', 0, 3, 0),
      ('apu', 'p2', 'lh', 1, 3, 0),
      ('apu', 'p2', 'cv', 1, 3, 0),
      ('apu', 'p2', 'vo', 0, 3, 0),
      ('apu', 'p2', 'ss', 7, 4, 1), # This is necessary to prevent channel silence for low notes
      ('apu', 'tr', 'lh', 1, 5, 0),
      ('apu', 'tr', 'lr', 127, 5, 0),
      ('apu', 'no', 'lh', 1, 6, 0),
      ('apu', 'no', 'cv', 1, 6, 0),
      ('apu', 'no', 'vo', 0, 6, 0),
  ]
  ch_to_last_tl = {ch:0 for ch in ['p1', 'p2']}
  ch_to_last_th = {ch:0 for ch in ['p1', 'p2']}
  ch_to_last_timer = {ch:0 for ch in ['p1', 'p2', 'tr']}
  ch_to_last_du = {ch:0 for ch in ['p1', 'p2']}
  ch_to_last_volume = {ch:0 for ch in ['p1', 'p2', 'no']}
  last_no_np = 0
  last_no_nl = 0

  for i in xrange(max_i):
    for j, ch in enumerate(['p1', 'p2']):
      th, tl, volume, du = score[i, j]
      timer = (th << 8) + tl
      last_timer = ch_to_last_timer[ch]

      # NOTE: This will never be perfect reconstruction because phase is not incremented when the channel is off
      retrigger = False
      if last_timer == 0 and timer != 0:
        ndf.append(('apu', 'ch', ch, 1, 0, 0))
        retrigger = True
      elif last_timer != 0 and timer == 0:
        ndf.append(('apu', 'ch', ch, 0, 0, 0))

      if du != ch_to_last_du[ch]:
        ndf.append(('apu', ch, 'du', du, 0, 0))
        ch_to_last_du[ch] = du

      if volume > 0 and volume != ch_to_last_volume[ch]:
        ndf.append(('apu', ch, 'vo', volume, 0, 0))
      ch_to_last_volume[ch] = volume

      if tl != ch_to_last_tl[ch]:
        ndf.append(('apu', ch, 'tl', tl, 0, 2))
        ch_to_last_tl[ch] = tl
      if retrigger or th != ch_to_last_th[ch]:
        ndf.append(('apu', ch, 'th', th, 0, 3))
        ch_to_last_th[ch] = th

      ch_to_last_timer[ch] = timer

    j = 2
    ch = 'tr'
    th, tl, _, _ = score[i, j]
    timer = (th << 8) + tl
    last_timer = ch_to_last_timer[ch]
    if last_timer == 0 and timer != 0:
      ndf.append(('apu', 'ch', ch, 1, 0, 0))
    elif last_timer != 0 and timer == 0:
      ndf.append(('apu', 'ch', ch, 0, 0, 0))
    if timer != last_timer:
      ndf.append(('apu', ch, 'tl', tl, 0, 2))
      ndf.append(('apu', ch, 'th', th, 0, 3))
    ch_to_last_timer[ch] = timer

    j = 3
    ch = 'no'
    _, np, volume, nl = score[i, j]
    if last_no_np == 0 and np != 0:
      ndf.append(('apu', 'ch', ch, 1, 0, 0))
    elif last_no_np != 0 and np == 0:
      ndf.append(('apu', 'ch', ch, 0, 0, 0))
    if volume > 0 and volume != ch_to_last_volume[ch]:
      ndf.append(('apu', ch, 'vo', volume, 0, 0))
    ch_to_last_volume[ch] = volume
    if nl != last_no_nl:
      ndf.append(('apu', ch, 'nl', nl, 0, 2))
      last_no_nl = nl
    if np > 0 and np != last_no_np:
      ndf.append(('apu', ch, 'np', 16 - np, 0, 2))
      ndf.append(('apu', ch, 'll', 0, 0, 3))
    last_no_np = np

    if ar:
      wait_amt = 1
    else:
      t += 1. / rate
      wait_amt = min(int(fs * t) - samp, nsamps - samp)

    ndf.append(('wait', wait_amt))
    samp += wait_amt

  remaining = nsamps - samp
  assert remaining >= 0
  if remaining > 0:
    ndf.append(('wait', remaining))

  return ndf
