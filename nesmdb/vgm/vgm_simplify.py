from nesmdb.vgm.bintypes import *
from nesmdb.vgm import vgm_to_ndr, ndr_to_vgm


def vgm_simplify(vgm, nop1=False, nop2=False, notr=False, nono=False, nodm=True):
  # Clear loop
  vgm = list(vgm)
  vgm[0x1c:0x20] = i2lub(0)
  vgm[0x20:0x24] = i2lub(0)
  vgm[0x24:0x28] = i2lub(0)

  # Simplify rate
  clock = b2lu(''.join(vgm[0x84:0x88])) & 0x3fffffff
  vgm[0x84:0x88] = i2lub(clock)

  # Clear volume
  vgm[0x7c:0x80] = i2lub(0)

  # Filter out some channels
  valid_registers = ['15', '17']
  if not nop1:
    valid_registers.extend(['00', '01', '02', '03'])
  if not nop2:
    valid_registers.extend(['04', '05', '06', '07'])
  if not notr:
    valid_registers.extend(['08', '09', '0a', '0b'])
  if not nono:
    valid_registers.extend(['0c', '0d', '0e', '0f'])
  if not nodm:
    valid_registers.extend(['10', '11', '12', '13'])
  valid_registers = set(valid_registers)

  # Gather writes to DMC and expansion chips
  i = 0xc0
  delidxs = []
  delcmds = 0
  while True:
    b = vgm[i]
    bhex = b2h(b)
    if bhex == '54':
      delidxs.extend(range(i, i + 3))
      i += 3
    elif bhex == '61':
      i += 3
    elif bhex == '62' or bhex == '63':
      i += 1
    elif bhex == '66':
      break
    elif bhex == '67':
      data_size = b2lu(''.join(vgm[i+3:i+7]))
      delidxs.extend(range(i, i + 3 + 4 + data_size))
      delcmds += 1
      i += 3 + 4 + data_size
    elif bhex[0] == '7':
      i += 1
    elif bhex == 'a0':
      delidxs.extend(range(i, i + 3))
      i += 3
    elif bhex == 'b4':
      arg1 = vgm[i+1]
      arg1hex = b2h(arg1)
      if arg1hex not in valid_registers:
        delidxs.extend(range(i, i + 3))
        delcmds += 1
      i += 3
    else:
      context = b2h(''.join(vgm[i - 8:i+8]))
      raise NotImplementedError('Unknown VGM command {}, context {}'.format(bhex, context))

  # Delete these extracurricular writes
  for i in sorted(delidxs, reverse=True):
    del vgm[i]
  eof_offset = b2lu(''.join(vgm[0x04:0x08]))
  eof_offset -= len(delidxs)
  vgm[0x04:0x08] = i2lub(eof_offset)

  vgm = ''.join(vgm)

  return vgm, delcmds


def vgm_shorten(vgm, nmax, start=None):
  ndr = vgm_to_ndr(vgm)

  meta = ndr[:1]
  ndr = ndr[1:]

  if start is not None:
    ndr = ndr[start:]
  ndr = ndr[:nmax]

  vgm = ndr_to_vgm(meta + ndr)

  return vgm
