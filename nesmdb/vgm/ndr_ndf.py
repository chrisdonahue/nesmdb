from collections import Counter, OrderedDict

from nesmdb.apu import *
from nesmdb.vgm.bintypes import *


def ndr_to_ndf(ndr):
  ndf = ndr[:1]
  ndr = ndr[1:]

  registers = {
      'p1': [0x00] * 4,
      'p2': [0x00] * 4,
      'tr': [0x00] * 4,
      'no': [0x00] * 4,
      'dm': [0x00] * 4,
      'ch': [0x00],
      'fc': [0x00]
  }

  # Expand
  natoms = 0
  for comm in ndr:
    if comm[0] == 'wait':
      ndf.append(comm)
      natoms = 0
    elif comm[0] == 'apu':
      reg = b2c(h2b(comm[1]))
      val = b2c(h2b(comm[2]))

      # Determine channel
      if reg >= 0x00 and reg < 0x04:
        ch = 'p1'
      elif reg >= 0x04 and reg < 0x08:
        ch = 'p2'
      elif reg >= 0x08 and reg < 0x0C:
        ch = 'tr'
      elif reg >= 0x0C and reg < 0x10:
        ch = 'no'
      elif reg >= 0x10 and reg < 0x14:
        ch = 'dm'
      elif reg == 0x15:
        ch = 'ch'
      elif reg == 0x17:
        ch = 'fc'
      else:
        raise NotImplementedError('Unknown register {}'.format(comm[1]))

      # Calculate offset for this channel
      offset = reg - register_memory_offsets[ch]
      assert offset >= 0

      # Log write to this register
      regtup = (ch, offset)
      ch_regs = registers[ch]

      # Mask register change to functional changes
      masks = register_function_bitmasks[ch][offset]
      for func, mask in masks:
        mask_bin = '{:08b}'.format(mask)
        nbits = mask_bin.count('1')
        shift = max(0, 7 - mask_bin.rfind('1')) % 8

        func_val = (val & mask) >> shift

        ndf.append(('apu', ch, func, func_val, natoms, offset))

      # Write value to register
      ch_regs[offset] = val
      assert ch_regs[offset] < 256
      natoms += 1
    elif comm[0] == 'ram':
      continue
    else:
      raise NotImplementedError(comm[0])

  # TODO: consider re-enabling compress
  #return ndf_compress(ndf)
  return ndf


def ndf_compress(ndf):
  ndf_out = []

  # Remove redundant commands
  comm_i = 0
  while comm_i < len(ndf):
    # Gather all atomic commands (within a wait)
    comm = (None,)
    atomic_comms = []
    while comm[0] != 'wait':
      if comm[0] is not None:
        atomic_comms.append(comm)
      comm = ndf[comm_i]
      comm_i += 1

      # If we're not ending on a wait, add last comm to atoms
      if comm[0] != 'wait' and comm_i == len(ndf):
        atomic_comms.append(comm)
        break

    # Store wait command
    if comm[0] == 'wait':
      wait_comm = comm
    else:
      wait_comm = None

    # Aggregate redundant commands
    ch_func_to_comms = OrderedDict()
    for comm in atomic_comms:
      ch_func = comm[1:3]

      if ch_func not in ch_func_to_comms:
        ch_func_to_comms[ch_func] = []
      ch_func_to_comms[ch_func].append(comm)

    # Output commands, removing redundant
    # Skips channel off commands from filtering because they set length counter to 0
    for comm in atomic_comms:
      if comm[1] == 'ch':
        ndf_out.append(comm)
      else:
        ch_func_comms = ch_func_to_comms[comm[1:3]]
        if comm == ch_func_comms[-1]:
          ndf_out.append(comm)

    # Output wait command
    if wait_comm is not None:
      ndf_out.append(wait_comm)

  ndf = ndf_out

  return ndf


def ndf_to_ndr(ndf):
  ndr = ndf[:1]
  ndf = ndf[1:]

  registers = {
      'p1': [0x00] * 4,
      'p2': [0x00] * 4,
      'tr': [0x00] * 4,
      'no': [0x00] * 4,
      'dm': [0x00] * 4,
      'ch': [0x00],
      'fc': [0x00]
  }

  # Convert commands to VGM
  regn_to_val = OrderedDict()
  for comm in ndf:
    itype = comm[0]
    if itype == 'wait':
      for _, (arg1, arg2) in regn_to_val.items():
        ndr.append(('apu', b2h(c2b(arg1)), b2h(c2b(arg2))))
      regn_to_val = OrderedDict()

      amt = comm[1]

      ndr.append(('wait', amt))
    elif itype == 'apu':
      dest = comm[1]
      param = comm[2]
      val = comm[3]
      natoms = comm[4]
      param_offset = comm[5]

      # Find offset/bitmask
      reg = registers[dest]
      param_bitmask = func_to_bitmask(dest, param)

      # Apply mask
      mask_bin = '{:08b}'.format(param_bitmask)
      nbits = mask_bin.count('1')
      if val < 0 or val >= (2 ** nbits):
        raise ValueError('{}, {} (0, {}]: invalid value specified {}'.format(comm[1], comm[2], (2 ** nbits), val))
      assert val >= 0 and val < (2 ** nbits)
      shift = max(0, 7 - mask_bin.rfind('1')) % 8
      val_old = reg[param_offset]
      reg[param_offset] &= (255 - param_bitmask)
      reg[param_offset] |= val << shift
      assert reg[param_offset] < 256
      val_new = reg[param_offset]

      arg1 = register_memory_offsets[dest] + param_offset
      arg2 = reg[param_offset]

      regn_to_val[(dest, param_offset, natoms)] = (arg1, arg2)
    elif itype == 'ram':
      # TODO
      continue
    else:
      raise NotImplementedError()

  for _, (arg1, arg2) in regn_to_val.items():
    ndr.append(('apu', b2h(c2b(arg1)), b2h(c2b(arg2))))

  return ndr
