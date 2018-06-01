import numpy as np

import nesmdb.vgm
import nesmdb.score


def _cycle_ndr(ndr):
  return ndr


def _cycle_ndf(ndr):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_nlm(ndr):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  nlm = nesmdb.vgm.ndf_to_nlm(ndf)
  ndf = nesmdb.vgm.nlm_to_ndf(nlm)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_rawsco(ndr):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  rawsco = nesmdb.score.ndf_to_rawsco(ndf)
  ndf = nesmdb.score.rawsco_to_ndf(rawsco)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_exprsco(ndr, rate):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  rawsco = nesmdb.score.ndf_to_rawsco(ndf)
  exprsco = nesmdb.score.rawsco_to_exprsco(rawsco)
  exprsco = nesmdb.score.exprsco_downsample(exprsco, rate, False)
  rawsco = nesmdb.score.exprsco_to_rawsco(exprsco)
  ndf = nesmdb.score.rawsco_to_ndf(rawsco)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_seprsco(ndr, rate):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  rawsco = nesmdb.score.ndf_to_rawsco(ndf)
  exprsco = nesmdb.score.rawsco_to_exprsco(rawsco)
  exprsco = nesmdb.score.exprsco_downsample(exprsco, rate, False)
  seprsco = nesmdb.score.exprsco_to_seprsco(exprsco)
  exprsco = nesmdb.score.seprsco_to_exprsco(seprsco)
  rawsco = nesmdb.score.exprsco_to_rawsco(exprsco)
  ndf = nesmdb.score.rawsco_to_ndf(rawsco)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_blndsco(ndr, rate):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  rawsco = nesmdb.score.ndf_to_rawsco(ndf)
  exprsco = nesmdb.score.rawsco_to_exprsco(rawsco)
  exprsco = nesmdb.score.exprsco_downsample(exprsco, rate, False)
  blndsco = nesmdb.score.exprsco_to_blndsco(exprsco)
  exprsco = nesmdb.score.blndsco_to_exprsco(blndsco)
  rawsco = nesmdb.score.exprsco_to_rawsco(exprsco)
  ndf = nesmdb.score.rawsco_to_ndf(rawsco)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def _cycle_midi(ndr, rate):
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)
  rawsco = nesmdb.score.ndf_to_rawsco(ndf)
  exprsco = nesmdb.score.rawsco_to_exprsco(rawsco)
  midi = nesmdb.score.exprsco_to_midi(exprsco)
  exprsco = nesmdb.score.midi_to_exprsco(midi)
  exprsco = nesmdb.score.exprsco_downsample(exprsco, rate, False)
  rawsco = nesmdb.score.exprsco_to_rawsco(exprsco)
  ndf = nesmdb.score.rawsco_to_ndf(rawsco)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  return ndr


def vgm_cycle(source_vgm, representation='ndf', keep_wav=False, **kwargs):
  # Cycle
  source_ndr = nesmdb.vgm.vgm_to_ndr(source_vgm)
  if representation == 'ndr':
    cycle_ndr = _cycle_ndr(source_ndr)
  elif representation == 'ndf':
    cycle_ndr = _cycle_ndf(source_ndr)
  elif representation == 'nlm':
    cycle_ndr = _cycle_nlm(source_ndr)
  elif representation == 'rawsco':
    cycle_ndr = _cycle_rawsco(source_ndr)
  elif representation == 'exprsco':
    cycle_ndr = _cycle_exprsco(source_ndr, rate=kwargs['score_rate'])
  elif representation == 'seprsco':
    cycle_ndr = _cycle_seprsco(source_ndr, rate=kwargs['score_rate'])
  elif representation == 'blndsco':
    cycle_ndr = _cycle_blndsco(source_ndr, rate=kwargs['score_rate'])
  elif representation == 'midi':
    cycle_ndr = _cycle_midi(source_ndr, rate=kwargs['score_rate'])
  else:
    raise NotImplementedError()
  cycle_vgm = nesmdb.vgm.ndr_to_vgm(cycle_ndr)

  return cycle_vgm


def vgm_dist(a_vgm, b_vgm):
  import librosa

  # Convert to wav
  a_wav = nesmdb.vgm.vgm_to_wav(a_vgm)
  b_wav = nesmdb.vgm.vgm_to_wav(b_vgm)
  assert a_wav.shape == b_wav.shape

  # Compute distance in log-Mel spectrogram space
  a_spec = librosa.feature.melspectrogram(a_wav, sr=44100, n_mels=128)
  b_spec = librosa.feature.melspectrogram(b_wav, sr=44100, n_mels=128)
  a_spec = np.log(a_spec + 1e-8)
  b_spec = np.log(b_spec + 1e-8)
  dist = np.mean(np.square(a_spec - b_spec))

  return dist, a_wav, b_wav


if __name__ == '__main__':
  import argparse
  import os
  import sys
  import traceback

  from tqdm import tqdm

  parser = argparse.ArgumentParser()

  parser.add_argument('representation', type=str, choices=['ndr', 'ndf', 'nlm', 'rawsco', 'exprsco', 'seprsco', 'blndsco', 'midi'])
  parser.add_argument('fps', type=str, nargs='+')
  parser.add_argument('--keep_vgm', action='store_true', dest='keep_vgm')
  parser.add_argument('--keep_wav', action='store_true', dest='keep_wav')
  parser.add_argument('--score_rate', type=float)
  parser.add_argument('--quiet', action='store_true', dest='quiet')

  parser.set_defaults(
      fps=None,
      representation='ndf',
      keep_vgm=False,
      keep_wav=False,
      score_rate=None,
      quiet=False)

  args = parser.parse_args()

  if args.representation not in ['ndr', 'ndf', 'nlm', 'rawsco'] and args.score_rate is None:
    print 'Must specify --score_rate'
    sys.exit(1)

  kwargs = {'score_rate': args.score_rate}

  progress_fps = args.fps if args.quiet else tqdm(args.fps)

  vgm_fp_to_dist = {}
  for vgm_fp in progress_fps:
    with open(vgm_fp, 'rb') as f:
      vgm = f.read()

    source_vgm, delcmds = nesmdb.vgm.vgm_simplify(vgm)

    try:
      cycle_vgm = vgm_cycle(source_vgm, representation=args.representation, **kwargs)
    except:
      print '-' * 80
      print vgm_fp
      print traceback.print_exc()
      continue

    dist, source_wav, cycle_wav = vgm_dist(source_vgm, cycle_vgm)
    vgm_fp_to_dist[vgm_fp] = dist
    
    if args.keep_vgm:
      with open(vgm_fp.replace('.vgm', '.source.vgm'), 'wb') as f:
        f.write(source_vgm)
      with open(vgm_fp.replace('.vgm', '.cycle.vgm'), 'wb') as f:
        f.write(cycle_vgm)

    if args.keep_wav:
      nesmdb.vgm.save_vgmwav(vgm_fp.replace('.vgm', '.source.wav'), source_wav)
      nesmdb.vgm.save_vgmwav(vgm_fp.replace('.vgm', '.cycle.wav'), cycle_wav)

  dists = vgm_fp_to_dist.values()
  print 'Mean distance (n={}): {} (std={})'.format(len(dists), np.mean(dists), np.std(dists))

  if not args.quiet:
    print '-' * 40 + ' Worst ' + '-' * 40
    for vgm_fp, dist in sorted(vgm_fp_to_dist.items(), key=lambda x:-x[1])[:8]:
      print '{:.8f}: {}'.format(dist, vgm_fp)

    print '-' * 40 + ' Best ' + '-' * 40
    for vgm_fp, dist in sorted(vgm_fp_to_dist.items(), key=lambda x:x[1])[:8]:
      print '{:.8f}: {}'.format(dist, vgm_fp)
