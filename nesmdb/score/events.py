import numpy as np

def rawsco_to_events(rawsco):
  clock, rate, nsamps, rawsco, sweeps, sweeps_overrides = rawsco
  assert rate == 44100
  assert rawsco.shape[0] == nsamps

  events = [('clock', int(clock))]
  ch_to_timer = {'p1': 0, 'p2': 0, 'tr': 0, 'no': 0}
  ch_to_vol = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_timbre = {'p1': 0, 'p2': 0, 'no': 0}
  ch_to_sweep = {'p1': (0, 0, 0, 0), 'p2': (0, 0, 0, 0)}
  # Handling rawsco edge case where initial t11 value is set one sample *after* starting the sweep
  ch_to_sweep_enable_hist = {'p1': 0, 'p2': 0}
  last_update = 0
  totwaits = 0

  for samp in xrange(nsamps):
    new_events = []

    for i, ch in enumerate(['p1', 'p2', 'tr', 'no']):
      # Pitch changes
      timer = (rawsco[samp, i, 0] << 8) + rawsco[samp, i, 1]
      if timer != ch_to_timer[ch]:
        if ch == 'p1' or ch == 'p2':
          if ch_to_sweep[ch][0] == 0 or ch_to_sweep_enable_hist[ch] == 1:
            new_events.append((ch, 'perd', timer))
        else:
          new_events.append((ch, 'perd', timer))
        ch_to_timer[ch] = timer

      if ch != 'tr':
        # Volume changes
        vol = rawsco[samp, i, 2]
        if vol != ch_to_vol[ch]:
          if vol == 0 and (len(new_events) == 0 or new_events[-1] != (ch, 'perd', 0)):
            new_events.append((ch, 'perd', 0))
          new_events.append((ch, 'volu', vol))
          ch_to_vol[ch] = vol

        # Timbre changes
        timbre = rawsco[samp, i, 3]
        if timbre != ch_to_timbre[ch]:
          new_events.append((ch, 'tmbr', timbre))
          ch_to_timbre[ch] = timbre

      # Sweep changes
      if ch == 'p1' or ch == 'p2':
        ch_sweep = (0, 0, 0, 0)
        if samp in sweeps[ch]:
          ch_sweep = sweeps[ch][samp]
          if ch_sweep != ch_to_sweep[ch]:
            new_events.append((ch, 'swep') + ch_sweep)
            ch_to_sweep[ch] = ch_sweep

        ch_to_sweep_enable_hist[ch] = ch_sweep[0]

        if samp in sweeps_overrides[ch]:
          assert ch_to_sweep[ch][0] == 1
          new_events.append((ch, 'perd', sweeps_overrides[ch][samp]))

    if len(new_events) > 0:
      wait = samp - last_update
      if wait > 0:
        events.append(('w', wait))
        totwaits += wait
      events.extend(new_events)
      last_update = samp

  if nsamps - last_update > 0:
    events.append(('w', nsamps - last_update))

  return events


def events_to_ndf(events):
  clock = events[0][1]
  events = events[1:]

  ch_names = ['p1', 'p2', 'tr', 'no']

  # ('apu', ch, func, func_val, which command this wait, which register of 4)
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
  ch_to_last_t11 = {ch:0 for ch in ['p1', 'p2', 'tr']}
  ch_to_last_tl = {ch:0 for ch in ['p1', 'p2', 'tr']}
  ch_to_last_th = {ch:0 for ch in ['p1', 'p2', 'tr']}
  ch_to_sweeping = {'p1': False, 'p2': False}
  last_no_np = 0

  for event in events:
    if event[0] == 'w':
      w_nsamps = event[1]
      ndf.append(('wait', w_nsamps))
    else:
      ch, event_type = event[0:2]
      ch_id = ch_names.index(ch)

      # Handle complex timer change events for p1/p2/tr
      if event_type == 'perd' and ch != 'no':
        t11 = event[2]
        th = (t11 & 0b11100000000) >> 8
        tl = (t11 & 0b00011111111)
        last_t11 = ch_to_last_t11[ch]
        last_th = ch_to_last_th[ch]
        last_tl = ch_to_last_tl[ch]

        retrigger = False
        sweeping = False if ch == 'tr' else ch_to_sweeping[ch]
        if last_t11 == 0 and t11 != 0:
          ndf.append(('apu', 'ch', ch, 1, 0, 0))
          retrigger = True
        elif last_t11 != 0 and t11 == 0:
          ndf.append(('apu', 'ch', ch, 0, 0, 0))

        if sweeping or tl != last_tl:
          ndf.append(('apu', ch, 'tl', tl, 0, 2))
        if sweeping or retrigger or th != ch_to_last_th[ch]:
          ndf.append(('apu', ch, 'th', th, 0, 3))
          ch_to_last_th[ch] = th

        ch_to_last_t11[ch] = t11
        ch_to_last_th[ch] = th
        ch_to_last_tl[ch] = tl

      # Handle other event types for all channels
      if ch == 'p1' or ch == 'p2':
        if event_type == 'perd':
          pass
        elif event_type == 'volu':
          ndf.append(('apu', ch, 'vo', event[2], 0, 0))
        elif event_type == 'tmbr':
          ndf.append(('apu', ch, 'du', event[2], 0, 0))
        elif event_type == 'swep':
          se, sp, sn, ss = event[2:]
          sweeping = bool(se)
          if sweeping:
            ndf.append(('apu', ch, 'se', 1, 0, 1))
            ndf.append(('apu', ch, 'sp', sp, 0, 1))
            ndf.append(('apu', ch, 'sn', sn, 0, 1))
            ndf.append(('apu', ch, 'ss', ss, 0, 1))
          else:
            ndf.append(('apu', ch, 'se', 0, 0, 1))
            ndf.append(('apu', ch, 'sp', 0, 0, 1))
            ndf.append(('apu', ch, 'sn', 1, 0, 1))
            ndf.append(('apu', ch, 'ss', 7, 0, 1))
          ch_to_sweeping[ch] = sweeping
        else:
          raise ValueError()
      elif ch == 'tr':
        if event_type == 'perd':
          pass
        else:
          raise ValueError()
      elif ch == 'no':
        if event_type == 'perd':
          no_np = event[2]
          retrigger = False
          if last_no_np == 0 and no_np != 0:
            ndf.append(('apu', 'ch', 'no', 1, 0, 0))
            retrigger = True
          elif last_no_np != 0 and no_np == 0:
            ndf.append(('apu', 'ch', 'no', 0, 0, 0))

          if no_np > 0 and no_np != last_no_np:
            ndf.append(('apu', 'no', 'np', 16 - no_np, 0, 2))
            ndf.append(('apu', 'no', 'll', 0, 0, 3))

          last_no_np = no_np
        elif event_type == 'volu':
          ndf.append(('apu', 'no', 'vo', event[2], 0, 0))
        elif event_type == 'tmbr':
          ndf.append(('apu', 'no', 'nl', event[2], 0, 2))
        else:
          raise ValueError()
      else:
        raise ValueError()

  return ndf


def events_to_txt(events):
  return '\n'.join([','.join([str(i) for i in e]) for e in events])


def txt_to_events(txt):
  events = []
  for line in txt.splitlines():
    if len(line.strip()) == 0:
      continue

    tokens = line.strip().split(',')
    if tokens[0] == 'clock':
      events.append(('clock', int(tokens[1])))
    elif tokens[0] == 'w':
      events.append(('w', int(tokens[1])))
    elif tokens[0] in ['p1', 'p2', 'tr', 'no']:
      events.append(tuple([tokens[0], tokens[1]] + [int(t) for t in tokens[2:]]))
    else:
      raise ValueError()

  return events
