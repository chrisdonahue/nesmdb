# System master clock rates by console region
ntsc_clock = (21477272. / 12.) # ~1789772.67
pal_clock = 1662607.


# Memory offset for each channel
register_memory_offsets = {
    'p1': 0x00,
    'p2': 0x04,
    'tr': 0x08,
    'no': 0x0c,
    'dm': 0x10,
    'ch': 0x15,
    'fc': 0x17
}


# Bitmasks for channel functions
register_function_bitmasks = {
  # P1/P2
  # du: duty
  # lh: length counter halt
  # cv: constant volume
  # vo: volume
  # se: sweep enable
  # sp: sweep period
  # sn: sweep negation
  # ss: sweep shift
  # tl: timer low
  # ll: length counter load
  # th: timer hi
  'p1': {
    0: [
      ('du', 0b11000000),
      ('lh', 0b00100000),
      ('cv', 0b00010000),
      ('vo', 0b00001111)
    ],
    1: [
      ('se', 0b10000000),
      ('sp', 0b01110000),
      ('sn', 0b00001000),
      ('ss', 0b00000111)
    ],
    2: [
      ('tl', 0b11111111)
    ],
    3: [
      ('ll', 0b11111000),
      ('th', 0b00000111)
    ]
  },
  # Triangle
  # lh: length counter halt / linear counter control
  # lr: linear counter load
  # tl: timer lo
  # ll: length counter load
  # th: timer hi
  'tr': {
    0: [
      ('lh', 0b10000000),
      ('lr', 0b01111111)
    ],
    1: [],
    2: [
      ('tl', 0b11111111)
    ],
    3: [
      ('ll', 0b11111000),
      ('th', 0b00000111)
    ]
  },
  # Noise
  # lh: length counter halt / envelope loop
  # cv: constant volume
  # vo: volume
  # nl: noise loop
  # np: noise period
  # ll: length counter load
  'no': {
    0: [
      ('lh', 0b00100000),
      ('cv', 0b00010000),
      ('vo', 0b00001111)
    ],
    1: [],
    2: [
      ('nl', 0b10000000),
      ('np', 0b00001111)
    ],
    3: [
      ('ll', 0b11111000)
    ]
  },
  # DMC
  # iq: irq enable
  # lo: loop
  # fr: frequency
  # lc: load counter
  # sa: sample address
  # sl: sample length
  'dm': {
    0: [
      ('iq', 0b10000000),
      ('lo', 0b01000000),
      ('fr', 0b00001111)
    ],
    1: [
      ('lc', 0b01111111)
    ],
    2: [
      ('sa', 0b11111111)
    ],
    3: [
      ('sl', 0b11111111)
    ]
  },
  # Channel status
  # dm: enable dmc
  # no: enable noise
  # tr: enable triangle
  # p2: enable p2
  # p1: enable p1
  'ch': {
    0: [
      ('dm', 0b00010000),
      ('no', 0b00001000),
      ('tr', 0b00000100),
      ('p2', 0b00000010),
      ('p1', 0b00000001)
    ]
  },
  # Frame counter
  # mo: mode
  # iq: irq inhibit flag
  'fc': {
    0: [
      ('mo', 0b10000000),
      ('iq', 0b01000000)
    ]
  }
}
register_function_bitmasks['p2'] = register_function_bitmasks['p1']


def func_to_bitmask(ch, fu):
  for offset, bitmasks in register_function_bitmasks[ch].items():
    for fu_name, bitmask in bitmasks:
      if fu_name == fu:
        return bitmask
  raise ValueError()


def func_to_max(ch, fu):
  bitmask = func_to_bitmask(ch, fu)
  mask_bin = '{:08b}'.format(bitmask)
  nbits = mask_bin.count('1')
  return (2 ** nbits)


def func_to_offset(ch, fu):
  for offset, bitmasks in register_function_bitmasks[ch].items():
    for fu_name, bitmask in bitmasks:
      if fu_name == fu:
        return offset
  raise ValueError()


# Number of frame counter ticks for various settings of the length counter
length_counter_table = [10, 254, 20, 2, 40, 4, 80, 6, 160, 8, 60, 10, 14, 12, 26, 14, 12, 16, 24, 18, 48, 20, 96, 22, 192, 24, 72, 26, 16, 28, 32, 30]
