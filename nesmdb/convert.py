import cPickle as pickle
import os

import numpy as np
from scipy.io.wavfile import write as wavwrite
from scipy.misc import imsave as imwrite

import nesmdb.vgm
#import nesmdb.representations


def _verify_type(fp, expected):
  fn = os.path.basename(fp)
  num_ext = expected.count('.')
  failed = False

  try:
    fp_exts = fn.rsplit('.', num_ext)[-num_ext:]
    expected_exts = expected.rsplit('.', num_ext)[-num_ext:]
    assert fp_exts == expected_exts
  except:
    raise Exception('Expected {} filetype; specified {}'.format(expected, fp))


def vgm_to_nrlr(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  nrlr = nesmdb.vgm.vgm_to_nrlr(vgm)

  with open(out_fp, 'wb') as f:
    pickle.dump(nrlr, f)


def vgm_to_nrlf(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  nrlr = nesmdb.vgm.vgm_to_nrlr(vgm)
  nrlf = nesmdb.vgm.nrlr_to_nrlf(nrlr)

  with open(out_fp, 'wb') as f:
    pickle.dump(nrlf, f)


def nrlf_to_vgm(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    nrlf = pickle.load(f)

  nrlr = nesmdb.vgm.nrlf_to_nrlr(nrlf)
  vgm = nesmdb.vgm.nrlr_to_vgm(nrlr)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


def nrlr_to_txt(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    nrlr = pickle.load(f)

  txt = nesmdb.vgm.nrl_to_txt(nrlr)

  with open(out_fp, 'w') as f:
    f.write(txt)


def nrlf_to_txt(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    nrlf = pickle.load(f)

  txt = nesmdb.vgm.nrl_to_txt(nrlf)

  with open(out_fp, 'w') as f:
    f.write(txt)


def txt_to_nrlf(in_fp, out_fp):
  with open(in_fp, 'r') as f:
    txt = f.read()

  nrlf = nesmdb.vgm.txt_to_nrl(txt)

  with open(out_fp, 'wb') as f:
    pickle.dump(nrlf, f)


def vgm_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def nrlf_to_perfscore(in_fp, out_fp, nrlf_to_perfscore_rate):
  with open(in_fp, 'rb') as f:
    nrlf = pickle.load(f)

  tscore = nesmdb.representations.nrlf_to_tscore(nrlf)
  mscore = nesmdb.representations.tscore_to_mscore(tscore)
  perfscore = nesmdb.representations.mscore_downsample(mscore, nrlf_to_perfscore_rate, False)

  with open(out_fp, 'wb') as f:
    pickle.dump(perfscore, f)


def perfscore_to_img(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    perfscore = pickle.load(f)

  img = nesmdb.representations.mscore_to_img_np(perfscore)

  imwrite(out_fp, img)


def perfscore_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    perfscore = pickle.load(f)

  tscore = nesmdb.representations.mscore_to_tscore(perfscore)
  nrlf = nesmdb.representations.tscore_to_nrlf(tscore)
  nrlr = nesmdb.vgm.nrlf_to_nrlr(nrlf)
  vgm = nesmdb.vgm.nrlr_to_vgm(nrlr)

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def perfscore_to_vgm(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    perfscore = pickle.load(f)

  tscore = nesmdb.representations.mscore_to_tscore(perfscore)
  nrlf = nesmdb.representations.tscore_to_nrlf(tscore)
  nrlr = nesmdb.vgm.nrlf_to_nrlr(nrlf)
  vgm = nesmdb.vgm.nrlr_to_vgm(nrlr)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


def compscore_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    compscore = pickle.load(f)

  perfscore = nesmdb.representations.compscore_to_perfscore(compscore)
  tscore = nesmdb.representations.mscore_to_tscore(perfscore)
  nrlf = nesmdb.representations.tscore_to_nrlf(tscore)
  nrlr = nesmdb.vgm.nrlf_to_nrlr(nrlf)
  vgm = nesmdb.vgm.nrlr_to_vgm(nrlr)

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def perfscore_to_compscore(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    perfscore = pickle.load(f)

  compscore = nesmdb.representations.perfscore_to_compscore(perfscore)

  with open(out_fp, 'wb') as f:
    pickle.dump(compscore, f)


def compscore_to_perfscore(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    compscore = pickle.load(f)

  perfscore = nesmdb.representations.compscore_to_perfscore(compscore)

  with open(out_fp, 'wb') as f:
    pickle.dump(perfscore, f)


def flatscore_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    flatscore = pickle.load(f)

  perfscore = nesmdb.representations.flatscore_to_perfscore(flatscore)
  tscore = nesmdb.representations.mscore_to_tscore(perfscore)
  nrlf = nesmdb.representations.tscore_to_nrlf(tscore)
  nrlr = nesmdb.vgm.nrlf_to_nrlr(nrlf)
  vgm = nesmdb.vgm.nrlr_to_vgm(nrlr)

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def vgm_shorten(in_fp, out_fp, vgm_shorten_start, vgm_shorten_nmax):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  vgm = nesmdb.vgm.vgm_shorten(vgm, vgm_shorten_nmax, vgm_shorten_start)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


def vgm_simplify(in_fp, out_fp, vgm_simplify_nop1, vgm_simplify_nop2, vgm_simplify_notr, vgm_simplify_nono):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  vgm, _ = nesmdb.vgm.vgm_simplify(vgm, vgm_simplify_nop1, vgm_simplify_nop2, vgm_simplify_notr, vgm_simplify_nono)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


if __name__ == '__main__':
  import argparse
  import os
  import sys
  import traceback

  from tqdm import tqdm

  parser = argparse.ArgumentParser()

  conversion_to_types = {
      'vgm_to_nrlr': ('.vgm', '.nrlr.pkl'),
      'vgm_to_nrlf': ('.vgm', '.nrlf.pkl'),
      'nrlf_to_vgm': ('.nrlf.pkl', '.nrlf.vgm'),
      'nrlr_to_txt': ('.nrlr.pkl', '.nrlr.txt'),
      'nrlf_to_txt': ('.nrlf.pkl', '.nrlf.txt'),
      'txt_to_nrlf': ('.nrlf.txt', '.nrlf.pkl'),
      'vgm_to_wav': ('.vgm', '.wav'),
      'nrlf_to_perfscore': ('.nrlf.pkl', '.perfscore.pkl'),
      'perfscore_to_img': ('.perfscore.pkl', '.png'),
      'perfscore_to_wav': ('.perfscore.pkl', '.wav'),
      'perfscore_to_vgm': ('.perfscore.pkl', '.vgm'),
      'flatscore_to_wav': ('.flatscore.pkl', '.wav'),
      'compscore_to_wav': ('.compscore.pkl', '.wav'),
      'perfscore_to_compscore': ('.perfscore.pkl', '.compscore.pkl'),
      'compscore_to_perfscore': ('.compscore.pkl', '.perfscore.pkl'),
      'vgm_shorten': ('.vgm', '.short.vgm'),
      'vgm_simplify': ('.vgm', '.simp.vgm'),
  }

  conversion_to_kwargs = {
      'nrlf_to_perfscore': ['nrlf_to_perfscore_rate'],
      'vgm_shorten': ['vgm_shorten_start', 'vgm_shorten_nmax'],
      'vgm_simplify': ['vgm_simplify_nop1', 'vgm_simplify_nop2', 'vgm_simplify_notr', 'vgm_simplify_nono']
  }

  parser.add_argument('conversion', type=str, choices=conversion_to_types.keys())
  parser.add_argument('fps', type=str, nargs='+')
  parser.add_argument('--out_dir', type=str)
  parser.add_argument('--skip_verify', action='store_true', dest='skip_verify')
  parser.add_argument('--vgm_shorten_start', type=int)
  parser.add_argument('--vgm_shorten_nmax', type=int)
  parser.add_argument('--vgm_simplify_nop1', action='store_true', dest='vgm_simplify_nop1')
  parser.add_argument('--vgm_simplify_nop2', action='store_true', dest='vgm_simplify_nop2')
  parser.add_argument('--vgm_simplify_notr', action='store_true', dest='vgm_simplify_notr')
  parser.add_argument('--vgm_simplify_nono', action='store_true', dest='vgm_simplify_nono')
  parser.add_argument('--nrlf_to_perfscore_rate', type=float)

  parser.set_defaults(
      conversion=None,
      fps=None,
      out_dir=None,
      skip_verify=False,
      vgm_shorten_start=None,
      vgm_shorten_nmax=1024,
      vgm_simplify_nop1=False,
      vgm_simplify_nop2=False,
      vgm_simplify_notr=False,
      vgm_simplify_nono=False,
      nrlf_to_perfscore_rate=None)

  args = parser.parse_args()

  in_type, out_type = conversion_to_types[args.conversion]
  fps = args.fps

  if len(fps) > 1 and args.out_dir is None:
    raise Exception('Must specify output directory for batch mode')

  if len(fps) == 1 and args.out_dir is None:
    out_fps = [fps[0].replace(in_type, out_type)]
  else:
    out_fns = [os.path.basename(fp).replace(in_type, out_type) for fp in fps]
    out_fps = [os.path.join(args.out_dir, fn) for fn in out_fns]

    if os.path.exists(args.out_dir):
      print 'WARNING: Output directory {} already exists'.format(args.out_dir)
    else:
      os.makedirs(args.out_dir)

  for in_fp, out_fp in tqdm(zip(fps, out_fps)):
    if not args.skip_verify:
      _verify_type(in_fp, in_type)
      _verify_type(out_fp, out_type)

    kwargs = {}
    if args.conversion in conversion_to_kwargs:
      kwargs = {kw:getattr(args, kw) for kw in conversion_to_kwargs[args.conversion]}

    try:
      globals()[args.conversion](in_fp, out_fp, **kwargs)
    except:
      print '-' * 80
      print in_fp
      traceback.print_exc()
