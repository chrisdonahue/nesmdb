from collections import defaultdict, Counter
import math

import numpy as np
from scipy.stats import mode


def rawsco_to_exprsco(rawsco, midi_valid_range=(21, 108)):
  clock, rate, nsamps, rawsco = rawsco
  assert rate == 44100
  assert rawsco.shape[0] == nsamps

  nsamps = rawsco.shape[0]

  t = rawsco[:, :3, :2].astype(np.uint16)
  t = np.left_shift(t[:, :, 0], 8) + t[:, :, 1]
  t = t.astype(np.float32)

  t_p, t_tr = t[:, :2], t[:, 2:]

  f_p = clock / (16 * (t_p + 1))
  f_tr = clock / (32 * (t_tr + 1))
  f = np.concatenate([f_p, f_tr], axis=1)

  m = 69 + (12 * np.log(f / 440)) / np.log(2)
  m = np.round(m)

  # Clip notes to midi range
  m[np.where(m < midi_valid_range[0])] = 0
  m[np.where(m > midi_valid_range[1])] = 0
  m = m.astype(np.uint8)

  # Create output score
  exprsco = np.zeros((nsamps, 4, 3), dtype=np.uint8)

  # Set notes
  exprsco[:, :3, 0] = m
  exprsco[:, 3, 0] = rawsco[:, 3, 1]

  # Set velocity
  exprsco[:, :, 1] = np.where(exprsco[:, :, 0] > 0, rawsco[:, :, 2], 0)

  # Set extra
  exprsco[:, :, 2] = rawsco[:, :, 3]

  return (rate, nsamps, exprsco)


def exprsco_downsample(exprsco, rate, adaptive):
  rate_prev, nsamps, exprsco = exprsco
  assert abs(rate_prev - 44100.) < 1e-6
  if abs(rate - 44100.) < 1e-6:
    return (rate_prev, nsamps, exprsco)

  if rate is None:
    # Find note onsets
    ch_to_last_note = {ch:0 for ch in xrange(4)}
    ch_to_onsets = defaultdict(list)
    for i in xrange(exprsco.shape[0]):
      for j in xrange(4):
        last_note = ch_to_last_note[j]
        note = exprsco[i, j, 0]
        if note > 0 and note != last_note:
          ch_to_onsets[j].append(i)
        ch_to_last_note[j] = note

    # Find note intervals
    intervals = Counter()
    for _, onsets in ch_to_onsets.items():
      for i in xrange(1, len(onsets)):
        interval = onsets[i] - onsets[i - 1]
        # Minimum length 1ms
        if interval > 44:
          intervals[interval] += 1
    intervals_t = {i / 44100.:c for i, c in intervals.items()}

    # Raise error if we don't have enough info to estimate tempo
    num_intervals = sum(intervals.values())
    if num_intervals < 10:
      raise Exception('Too few intervals ({}) to estimate tempo'.format(num_intervals))

    # Determine how well each rate divides the intervals
    # TODO: Make 1/24/disc variables
    disc = 0.001
    rate_errors = []
    for rate in np.arange(1., 24. + disc, disc):
      error = 0.
      for interval, count in intervals_t.items():
        quotient = math.floor(interval * rate + 1e-8)
        remainder = interval - (quotient / rate)
        if remainder < 0 and abs(remainder) < 1e-8:
          remainder = 0
        assert remainder >= 0
        error += remainder * count
      rate_errors.append((rate, error))

    # Find best rate
    rate_errors = sorted(rate_errors, key=lambda x: x[1])
    rate = float(rate_errors[0][0])

  # Downsample
  rate = float(rate)
  ndown = int((nsamps / 44100.) * rate)
  score_low = np.zeros((ndown, 4, 3), dtype=np.uint8)
  for i in xrange(ndown):
    t_lo = i / rate
    t_hi = (i + 1) / rate
    # TODO: round these instead of casting?
    samp_lo, samp_hi = [int(t * 44100.) for t in [t_lo, t_hi]]
    score_slice = exprsco[samp_lo:samp_hi]
    for ch in xrange(4):
      score_slice_ch = score_slice[:, ch, :]
      on_frames = np.where(score_slice_ch[:, 0] != 0)[0]
      if len(on_frames) > 0:
        score_low[i, ch, :] = mode(score_slice_ch[on_frames])[0][0]
      else:
        score_low[i, ch, :2] = 0
        score_low[i, ch, 2] = mode(score_slice_ch[:, 2])[0][0]

  return (rate, nsamps, score_low)


def exprsco_to_rawsco(exprsco, clock=1789773.):
  rate, nsamps, exprsco = exprsco

  m = exprsco[:, :3, 0]
  m_zero = np.where(m == 0)

  m = m.astype(np.float32)
  f = 440 * np.power(2, ((m - 69) / 12))

  f_p, f_tr = f[:, :2], f[:, 2:]

  t_p = np.round((clock / (16 * f_p)) - 1)
  t_tr = np.round((clock / (32 * f_tr)) - 1)
  t = np.concatenate([t_p, t_tr], axis=1)

  t = t.astype(np.uint16)
  t[m_zero] = 0
  th = np.right_shift(np.bitwise_and(t, 0b11100000000), 8)
  tl = np.bitwise_and(t, 0b00011111111)

  rawsco = np.zeros((exprsco.shape[0], 4, 4), dtype=np.uint8)
  rawsco[:, :, 2:] = exprsco[:, :, 1:]
  rawsco[:, :3, 0] = th
  rawsco[:, :3, 1] = tl
  rawsco[:, 3, 1:] = exprsco[:, 3, :]

  return (clock, rate, nsamps, rawsco)
