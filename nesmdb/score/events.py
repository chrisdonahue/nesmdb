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
  last_update = 0
  totwaits = 0

  for samp in xrange(nsamps):
    new_events = []

    for i, ch in enumerate(['p1', 'p2', 'tr', 'no']):
      # Pitch changes
      timer = (rawsco[samp, i, 0] << 8) + rawsco[samp, i, 1]
      if timer != ch_to_timer[ch]:
        if ch == 'p1' or ch == 'p2':
          if ch_to_sweep[ch][0] == 0:
            new_events.append((ch, 'perd', timer))
        else:
          new_events.append((ch, 'perd', timer))
        ch_to_timer[ch] = timer

      if ch != 'tr':
        # Volume changes
        vol = rawsco[samp, i, 2]
        if vol != ch_to_vol[ch] and (ch == 'no' or ch_to_sweep[ch][0] == 0):
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
        if samp in sweeps[ch]:
          ch_sweep = sweeps[ch][samp]
          if ch_sweep != ch_to_sweep[ch]:
            # If we're switching sweep enable
            if ch_to_sweep[ch][0] != ch_sweep[0]:
              new_events.append((ch, 'swep') + ch_sweep)
            ch_to_sweep[ch] = ch_sweep

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


def events_to_rawsco(events):
  clock = events[0][1]
  events = events[1:]

  nsamps = sum([w[1] for w in filter(lambda x: x[0] == 'w', events)])
  rate = 44100

  rawsco = np.zeros((nsamps, 4, 4), dtype=np.uint8)
  ch_to_timer = {'p1': 0, 'p2': 0, 'tr': 0, 'no': 0}
  ch_to_sweep = {'p1': (0, 0, 0, 0), 'p2': (0, 0, 0, 0)}
  sweeps = {'p1': {}, 'p2': {}}
  sweeps_overrides = {'p1': {}, 'p2': {}}

  samp = 0
  for event in events:
    if event[0] == 'w':
      w_nsamps = event[1]
      rawsco[samp:samp+w_nsamps] = rawsco[samp][np.newaxis]
      samp += w_nsamps
    else:
      ch, event_type = event[0:2]
      ch_id = ['p1', 'p2', 'tr', 'no'].index(ch)

      if event_type == 'perd':
        t11 = event[2]
        ch_to_timer[ch] = t11
        th = (t11 & 0b11100000000) >> 8
        tl = (t11 & 0b00011111111)
        rawsco[samp, ch_id, 0] = th
        rawsco[samp, ch_id, 1] = tl
        if ch == 'p1' or ch == 'p2' and ch_to_sweep[ch][0] == 1:
          sweeps_overrides[ch][samp] = t11
      elif event_type == 'volu':
        rawsco[samp, ch_id, 2] = event[2]
      elif event_type == 'tmbr':
        rawsco[samp, ch_id, 3] = event[2]
      else:
        sweep = event[2:]
        ch_to_sweep[ch] = sweep
        sweeps[ch][samp] = sweep

  return (clock, rate, nsamps, rawsco, sweeps, sweeps_overrides)
