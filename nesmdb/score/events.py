def rawsco_to_events(rawsco):
  clock, rate, nsamps, rawsco, sweeps = rawsco
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
      if ch != 'no':
        timer = (rawsco[samp, i, 0] << 8) + rawsco[samp, i, 1]
        if timer != ch_to_timer[ch]:
          new_events.append((ch, 'timr', timer))
          ch_to_timer[ch] = timer

      if ch == 'p1' or ch == 'p2':
        if samp in sweeps[ch]:
          ch_sweep = sweeps[ch][samp]
          if ch_sweep != ch_to_sweep[ch]:
            # If we're switching sweep enable
            if ch_to_sweep[ch][0] != ch_sweep[0]:
              new_events.append((ch, 'swep') + ch_sweep)
            ch_to_sweep[ch] = ch_sweep

      if ch != 'tr':
        vol = rawsco[samp, i, 2]
        if vol != ch_to_vol[ch]:
          new_events.append((ch, 'volu', vol))
          ch_to_vol[ch] = vol

        timbre = rawsco[samp, i, 3]
        if timbre != ch_to_timbre[ch]:
          new_events.append((ch, 'tmbr', timbre))
          ch_to_timbre[ch] = timbre

    if len(new_events) > 0:
      wait = samp - last_update
      if wait > 0:
        events.append(('w', wait))
        totwaits += wait
      events.extend(new_events)
      last_update = samp

  if nsamps - last_update > 0:
    events.append(('w', nsamps - last_update))

  for event in events:
    print event

  return events


def events_to_rawsco(events):
  return events
