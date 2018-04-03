import binascii
import struct

# Bytes to hex
b2h = lambda x: binascii.hexlify(x)
h2b = lambda x: binascii.unhexlify(x)

# Bytes to 4-byte ([l]ittle/[b]ig) unsigned ints
b2lu = lambda x: struct.unpack('<I', x)[0]
b2bu = lambda x: struct.unpack('>I', x)[0]
i2lub = lambda x: struct.pack('<I', x)
i2bub = lambda x: struct.pack('>I', x)

# Bytes to 2-byte ([l]ittle/[b]ig) unsigned shorts
b2lus = lambda x: struct.unpack('<H', x)[0]
b2bus = lambda x: struct.unpack('>H', x)[0]
i2lusb = lambda x: struct.pack('<H', x)
i2busb = lambda x: struct.pack('>H', x)

# String to 1-byte chars
b2c = lambda x: struct.unpack('B', x)[0]
c2b = lambda x: struct.pack('B', x)[0]

# Pointer arithmetic
b2p = lambda x: b2h(i2bub(b2lu(x)))
offset = lambda x, y: b2h(i2bub(b2bu(h2b(x)) + y))
read = lambda x, y: x[b2bu(h2b(y)):]
