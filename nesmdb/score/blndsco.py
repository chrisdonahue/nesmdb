import numpy as np


def exprsco_to_blndsco(exprsco):
  rate, nsamps, score = exprsco

  blndsco = []
  for i in range(score.shape[0]):
    score_slice = list(score[i, :3, 0])
    score_slice = sorted([x for x in score_slice if x > 0])
    blndsco.append(score_slice)

  return (rate, nsamps, blndsco)


def blndsco_to_exprsco(blndsco):
  rate, nsamps, score = blndsco

  score_len = len(score)

  exprsco = np.zeros((score_len, 4, 3), dtype=np.uint8)

  for i, frame in enumerate(score):
    for j, note in enumerate(frame[:3]):
      exprsco[i, j, 0] = note
      exprsco[i, j, 1] = 0 if j == 2 else 15

  return (rate, nsamps, exprsco)
