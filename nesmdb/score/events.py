def rawsco_to_events(rawsco):
  clock, rate, nsamps, rawsco, sweeps = rawsco
  assert rate == 44100
  assert rawsco.shape[0] == nsamps

  print sweeps

  return (clock, rate, nsamps, rawsco, sweeps)

def events_to_rawsco(events):
  return events
