from nesmdb.apu import *
from nesmdb.vgm.bintypes import *


def vgm_to_ndr(vgm):
  # Retrieve EOF offset
  eof_offset = offset(b2p(vgm[0x04:0x08]), 0x04)
  if b2bu(h2b(eof_offset)) != len(vgm):
    raise Exception('EOF offset does not match file size')

  # Retrieve version
  version = b2p(vgm[0x08:0x0c])[-3:]
  if version != '161':
    raise NotImplementedError('Invalid version {}'.format(version))

  # Retrieve GD3 metadata
  gd3_tag = read(vgm, offset(b2p(vgm[0x14:0x18]), 0x14))

  # Retrieve system clock
  clock = b2lu(vgm[0x84:0x88])
  use_fds = (clock & 0x80000000) != 0
  two_chips = (clock & 0x40000000) != 0
  if use_fds:
    raise Exception('Famicon Disk System unsupported')
  if two_chips:
    raise Exception('Multiple NES APUs unsupported')
  clock = clock & 0x3fffffff
  if clock not in [1662607, 1789772, 1789773]:
    raise Exception('Invalid NES APU Clock rate {}'.format(clock))

  # Find length
  total_nsamps = b2lu(vgm[0x18:0x1c])

  # Find loop offset
  # TODO: Put loop marker into output sequence
  loop_offset = offset(b2p(vgm[0x1c:0x20]), 0x1c)

  # Find loop samples
  loop_nsamps = b2lu(vgm[0x20:0x24])

  # Find rate
  global_rate = b2lu(vgm[0x24:0x28])
  if global_rate != 0:
    raise NotImplementedError('Global rate is {} (nonzero)'.format(global_rate))

  # Find data offset
  vgm_data_offset = offset(b2p(vgm[0x34:0x38]), 0x34)

  # Find volume
  volume = b2c(vgm[0x7c:0x7d])

  # Find loop base
  loop_base = b2c(vgm[0x7e:0x7f])

  # Find loop modifier
  loop_modifier = b2c(vgm[0x7f:0x80])

  # Read VGM data
  vgm_data = read(vgm, vgm_data_offset)

  # Parse VGM data
  i = 0
  ndr = [('clock', clock)]
  while i < len(vgm_data):
    byte = b2h(vgm_data[i])
    i += 1

    # Wait (long)
    if byte == '61':
      arg1 = vgm_data[i]
      i += 1
      arg2 = vgm_data[i]
      i += 1

      wlen = b2lus(arg1 + arg2)

      ndr.append(('wait', wlen))

    # Wait (1/60th second for NTSC)
    elif byte == '62':
      ndr.append(('wait', 735))

    # Wait (1/50th second for PAL)
    elif byte == '63':
      ndr.append(('wait', 882))

    # Halt
    elif byte == '66':
      break

    # Data block
    elif byte == '67':
      assert b2h(vgm_data[i]) == '66'
      i += 1
      data_type = b2h(vgm_data[i])
      i += 1

      # NES APU RAM write
      if data_type == 'c2':
        data_size = b2lu(vgm_data[i:i+4])
        i += 4
        ram_data = vgm_data[i:i+data_size]
        i += data_size

        ndr.append(('ram', data_type, ram_data))
      else:
        raise NotImplementedError()

    # Wait (short)
    elif byte[0] == '7':
      ndr.append(('wait', b2c(h2b('0' + byte[1])) + 1))

    # NES APU write
    elif byte == 'b4':
      reg = vgm_data[i]
      i += 1
      val = vgm_data[i]
      i += 1

      ndr.append(('apu', b2h(reg), b2h(val)))

    else:
      raise NotImplementedError(byte)

  nwaits_real = 0
  for co in ndr:
    if co[0] == 'wait':
      nwaits_real += co[1]
  assert nwaits_real == total_nsamps

  ndr_collapsed = []

  # Collapse adjacent waits
  comm_i = 0
  while comm_i < len(ndr):
    comm = ndr[comm_i]
    comm_i += 1

    if comm[0] == 'wait':
      wait_amt = comm[1]
      while comm_i < len(ndr) and ndr[comm_i][0] == 'wait':
        wait_amt += ndr[comm_i][1]
        comm_i += 1
      ndr_collapsed.append(('wait', wait_amt))
    else:
      ndr_collapsed.append(comm)

  return ndr_collapsed


def ndr_to_vgm(ndr):
  assert ndr[0][0] == 'clock'
  clock = ndr[0][1]

  ndr = ndr[1:]

  EMPTYBYTE = i2lub(0)
  flatten = lambda vgm: list(''.join(vgm))
  vgm = flatten([EMPTYBYTE] * 48)

  # VGM identifier
  vgm[:0x04] = [c2b(c) for c in [0x56, 0x67, 0x6d, 0x20]]
  # Version
  vgm[0x08:0x0c] = i2lub(0x161)
  # Clock rate
  vgm[0x84:0x88] = i2lub(clock)
  # Data offset
  vgm[0x34:0x38] = i2lub(0xc0 - 0x34)

  wait_sum = 0
  for comm in ndr:
    itype = comm[0]
    if itype == 'wait':
      amt = comm[1]
      wait_sum += amt

      while amt > 65535:
        vgm.append(c2b(0x61))
        vgm.append(i2lusb(65535))
        amt -= 65535

      vgm.append(c2b(0x61))
      vgm.append(i2lusb(amt))
    elif itype == 'apu':
      arg1 = h2b(comm[1])
      arg2 = h2b(comm[2])
      vgm.append(c2b(0xb4))
      vgm.append(arg1)
      vgm.append(arg2)
    elif itype == 'ram':
      raise NotImplementedError()
    else:
      raise NotImplementedError()

  # Halt
  vgm.append(c2b(0x66))
  vgm = flatten(vgm)

  # Total samples
  vgm[0x18:0x1c] = i2lub(wait_sum)
  # EoF offset
  vgm[0x04:0x08] = i2lub(len(vgm) - 0x04)

  vgm = ''.join(vgm)
  return vgm
