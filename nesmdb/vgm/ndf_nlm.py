from collections import defaultdict

from nesmdb.apu import func_to_offset


_DELETE = [
    'ch_dm',
    'fc_iq'
]


_VOLATILE = [
    'p1_ll',
    'p2_ll',
    'tr_ll',
    'no_ll',

    'ch_p1',
    'ch_p2',
    'ch_tr',
    'ch_no',

    'fc_mo'
]


def ndf_to_nlm(ndf):
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
      changed = func_to_val[func] != val

      preserve = func in _VOLATILE
      if func == 'p1_tl' and (func_to_val['p1_se'] == 1):
        preserve = True
      if func == 'p2_tl' and (func_to_val['p2_se'] == 1):
        preserve = True

      if (changed or preserve) and not delete:
        lm.append(comm)

      func_to_val[func] = val
    else:
      raise NotImplementedError()

  # Simplify syntax
  lm_nu = [ndf[0]]
  for comm in lm[1:]:
    if comm[0] == 'wait':
      lm_nu.append(('w', comm[1]))
    else:
      lm_nu.append(('{}_{}'.format(comm[1], comm[2]), comm[3]))

  return lm_nu


def nlm_to_ndf(lm):
  ndf = [lm[0]]

  offset_last = None
  natoms = 0
  atom_funcs = set()

  for comm in lm[1:]:
    if comm[0] == 'w':
      ndf.append(('wait', comm[1]))

      offset_last = None
      natoms = 0
      atom_funcs = set()
    else:
      ch, fu = comm[0].split('_')
      offset = func_to_offset(ch, fu)

      func = '{}_{}'.format(ch, fu)

      if offset_last is not None and offset_last != offset or func in atom_funcs:
        atom_funcs = set()
        natoms += 1
      atom_funcs.add(func)
      offset_last = offset

      ndf.append(('apu', ch, fu, comm[1], natoms, func_to_offset(ch, fu)))

  return ndf
