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


def vgm_to_ndr(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  ndr = nesmdb.vgm.vgm_to_ndr(vgm)

  with open(out_fp, 'wb') as f:
    pickle.dump(ndr, f)


def vgm_to_ndf(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  ndr = nesmdb.vgm.vgm_to_ndr(vgm)
  ndf = nesmdb.vgm.ndr_to_ndf(ndr)

  with open(out_fp, 'wb') as f:
    pickle.dump(ndf, f)


def ndf_to_vgm(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    ndf = pickle.load(f)

  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  vgm = nesmdb.vgm.ndr_to_vgm(ndr)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


def ndr_to_txt(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    ndr = pickle.load(f)

  txt = nesmdb.vgm.nd_to_txt(ndr)

  with open(out_fp, 'w') as f:
    f.write(txt)


def ndf_to_txt(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    ndf = pickle.load(f)

  txt = nesmdb.vgm.nd_to_txt(ndf)

  with open(out_fp, 'w') as f:
    f.write(txt)


def txt_to_ndf(in_fp, out_fp):
  with open(in_fp, 'r') as f:
    txt = f.read()

  ndf = nesmdb.vgm.txt_to_nd(txt)

  with open(out_fp, 'wb') as f:
    pickle.dump(ndf, f)


def vgm_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    vgm = f.read()

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def ndf_to_exprsco(in_fp, out_fp, ndf_to_exprsco_rate):
  with open(in_fp, 'rb') as f:
    ndf = pickle.load(f)

  tscore = nesmdb.representations.ndf_to_tscore(ndf)
  mscore = nesmdb.representations.tscore_to_mscore(tscore)
  exprsco = nesmdb.representations.mscore_downsample(mscore, ndf_to_exprsco_rate, False)

  with open(out_fp, 'wb') as f:
    pickle.dump(exprsco, f)


def exprsco_to_img(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    exprsco = pickle.load(f)

  img = nesmdb.representations.mscore_to_img_np(exprsco)

  imwrite(out_fp, img)


def exprsco_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    exprsco = pickle.load(f)

  tscore = nesmdb.representations.mscore_to_tscore(exprsco)
  ndf = nesmdb.representations.tscore_to_ndf(tscore)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  vgm = nesmdb.vgm.ndr_to_vgm(ndr)

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def exprsco_to_vgm(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    exprsco = pickle.load(f)

  tscore = nesmdb.representations.mscore_to_tscore(exprsco)
  ndf = nesmdb.representations.tscore_to_ndf(tscore)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  vgm = nesmdb.vgm.ndr_to_vgm(ndr)

  with open(out_fp, 'wb') as f:
    f.write(vgm)


def compsco_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    compsco = pickle.load(f)

  exprsco = nesmdb.representations.compsco_to_exprsco(compsco)
  tscore = nesmdb.representations.mscore_to_tscore(exprsco)
  ndf = nesmdb.representations.tscore_to_ndf(tscore)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  vgm = nesmdb.vgm.ndr_to_vgm(ndr)

  wav = nesmdb.vgm.vgm_to_wav(vgm)

  wav *= 32767.
  wav = np.clip(wav, -32767., 32767.)
  wav = wav.astype(np.int16)

  wavwrite(out_fp, 44100, wav)


def exprsco_to_compsco(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    exprsco = pickle.load(f)

  compsco = nesmdb.representations.exprsco_to_compsco(exprsco)

  with open(out_fp, 'wb') as f:
    pickle.dump(compsco, f)


def compsco_to_exprsco(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    compsco = pickle.load(f)

  exprsco = nesmdb.representations.compsco_to_exprsco(compsco)

  with open(out_fp, 'wb') as f:
    pickle.dump(exprsco, f)


def blndsco_to_wav(in_fp, out_fp):
  with open(in_fp, 'rb') as f:
    blndsco = pickle.load(f)

  exprsco = nesmdb.representations.blndsco_to_exprsco(blndsco)
  tscore = nesmdb.representations.mscore_to_tscore(exprsco)
  ndf = nesmdb.representations.tscore_to_ndf(tscore)
  ndr = nesmdb.vgm.ndf_to_ndr(ndf)
  vgm = nesmdb.vgm.ndr_to_vgm(ndr)

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
      'vgm_shorten': ('.vgm', '.short.vgm'),
      'vgm_simplify': ('.vgm', '.simp.vgm'),
      'vgm_to_wav': ('.vgm', '.wav'),
      'ndf_to_wav': ('.ndf', '.wav'),
      'vgm_to_ndr': ('.vgm', '.ndr.pkl'),
      'vgm_to_ndf': ('.vgm', '.ndf.pkl'),
      'ndf_to_vgm': ('.ndf.pkl', '.ndf.vgm'),
      'ndr_to_txt': ('.ndr.pkl', '.ndr.txt'),
      'ndf_to_txt': ('.ndf.pkl', '.ndf.txt'),
      'txt_to_ndf': ('.ndf.txt', '.ndf.pkl'),
      'ndf_to_exprsco': ('.ndf.pkl', '.exprsco.pkl'),
      'exprsco_to_img': ('.exprsco.pkl', '.png'),
      'exprsco_to_wav': ('.exprsco.pkl', '.wav'),
      'exprsco_to_vgm': ('.exprsco.pkl', '.vgm'),
      'blndsco_to_wav': ('.blndsco.pkl', '.wav'),
      'compsco_to_wav': ('.compsco.pkl', '.wav'),
      'exprsco_to_compsco': ('.exprsco.pkl', '.compsco.pkl'),
      'compsco_to_exprsco': ('.compsco.pkl', '.exprsco.pkl'),
  }

  conversion_to_kwargs = {
      'vgm_simplify': ['vgm_simplify_nop1', 'vgm_simplify_nop2', 'vgm_simplify_notr', 'vgm_simplify_nono'],
      'vgm_shorten': ['vgm_shorten_start', 'vgm_shorten_nmax'],
      'ndf_to_exprsco': ['ndf_to_exprsco_rate'],
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
  parser.add_argument('--ndf_to_exprsco_rate', type=float)

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
      ndf_to_exprsco_rate=None)

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
