from collections import defaultdict


_DELETE = [
    'ch_dm',
    'fc_iq'
]


_VOLATILE = [
    'p1_tl',
    'p1_ll',
    'p1_th',

    'p2_tl',
    'p2_th',
    'p2_ll',

    'tr_tl',
    'tr_th',
    'tr_ll',

    'no_ll',

    'ch_p1',
    'ch_p2',
    'ch_tr',
    'ch_no',

    'fc_mo'
]


def ndf_to_lm(ndf):
  func_to_val = defaultdict(int)
  func_to_val['ch_p1'] = 1
  func_to_val['ch_p2'] = 1
  func_to_val['ch_tr'] = 1
  func_to_val['ch_no'] = 1
  func_to_val['ch_dm'] = 1

  funcs = set()

  lm = [ndf[0]]
  natom = 0
  for comm in ndf[1:]:
    if comm[0] == 'wait':
      lm.append(comm)
      natom = 0
    elif comm[0] == 'apu':
      ch = comm[1]
      fu = comm[2]
      val = comm[3]
      natom = comm[4]
      offset = comm[5]

      func = '{}_{}'.format(ch, fu)
      reg = '{}_{}'.format(ch, offset)

      funcs.add(func)

      delete = func in _DELETE
      preserve = func in _VOLATILE or func_to_val[func] != val

      if preserve and not delete:
        lm.append(comm)
        func_to_val[func] = val
    else:
      raise NotImplementedError()

  return lm


def lm_to_ndf(lm):
  ndf = lm
  return ndf
