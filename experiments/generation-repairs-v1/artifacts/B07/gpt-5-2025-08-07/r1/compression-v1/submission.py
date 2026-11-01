import numpy as np
import lzma
import struct

MAGIC = b'NPLC'  # Neuropixels Lossless Codec
VERSION = 1
# Flags bitfield
FLAG_T_DIFF = 1 << 0   # temporal first difference
FLAG_C_DIFF = 1 << 1   # channel first difference
FLAG_ZIGZAG = 1 << 2   # ZigZag signed->unsigned
FLAG_SHUFFLE = 1 << 3  # byte-shuffle (low bytes then high bytes)

# -------------------- Utility transforms --------------------

def _zigzag_encode_i16(x: np.ndarray) -> np.ndarray:
    # x: int16 -> return uint16 with ZigZag
    v = x.astype(np.int32, copy=False)
    u = (v << 1) ^ (v >> 15)  # arithmetic shift keeps sign; XOR yields ZigZag
    return u.astype(np.uint16, copy=False)


def _zigzag_decode_u16(u: np.ndarray) -> np.ndarray:
    # u: uint16 -> return int16
    u32 = u.astype(np.uint32, copy=False)
    # (u >> 1) ^ -(u & 1) in int32 domain
    e32 = ((u32 >> 1).astype(np.int32)) ^ (-(u32 & 1).astype(np.int32))
    return e32.astype(np.int16, copy=False)


def _byte_shuffle_u16_le(u: np.ndarray) -> bytes:
    # u is uint16, little-endian preferred
    b2 = u.view(np.uint8).reshape(-1, 2)
    low = b2[:, 0].tobytes()
    high = b2[:, 1].tobytes()
    return low + high


def _byte_unshuffle_u16_le(data: bytes, count: int) -> np.ndarray:
    # reconstruct uint16 array from byte-shuffled form
    low = memoryview(data)[:count]
    high = memoryview(data)[count:count*2]
    out = np.empty(count, dtype=np.dtype('<u2'))
    b2 = out.view(np.uint8).reshape(-1, 2)
    b2[:, 0] = np.frombuffer(low, dtype=np.uint8)
    b2[:, 1] = np.frombuffer(high, dtype=np.uint8)
    return out

# -------------------- Core codec --------------------

def compress(array: np.ndarray) -> bytes:
    # Ensure correct dtype and contiguity; treat data as little-endian int16
    a = np.asarray(array)
    if a.ndim != 2:
        raise ValueError('Input must be 2-D (time, channels).')
    a16 = np.ascontiguousarray(a.astype(np.dtype('<i2'), copy=False))

    # Temporal first-order difference along time (rows)
    t, c = a16.shape
    dt = np.empty_like(a16)
    dt[0] = a16[0]
    dt[1:] = (a16[1:].astype(np.int32) - a16[:-1].astype(np.int32)).astype(np.int16)

    # Channel first-order difference along channels (columns)
    dc = np.empty_like(dt)
    dc[:, 0] = dt[:, 0]
    dc[:, 1:] = (dt[:, 1:].astype(np.int32) - dt[:, :-1].astype(np.int32)).astype(np.int16)

    # ZigZag map to unsigned
    u16 = _zigzag_encode_i16(dc)

    # Byte-shuffle (low bytes then high bytes)
    payload = _byte_shuffle_u16_le(u16)

    # Compress with LZMA (XZ container). Preset 6 balances ratio and speed.
    comp = lzma.compress(payload, preset=6)

    # Header: MAGIC(4) | VER(1) | FLAGS(1)
    flags = FLAG_T_DIFF | FLAG_C_DIFF | FLAG_ZIGZAG | FLAG_SHUFFLE
    header = MAGIC + struct.pack('<BB', VERSION, flags)
    return header + comp


def decompress(blob: bytes, shape, dtype: str) -> np.ndarray:
    if dtype != '<i2' and dtype != 'int16' and dtype != np.dtype('<i2').str:
        # We only produce little-endian int16; accept alias 'int16' too.
        pass

    if len(blob) < 6:
        raise ValueError('Corrupt blob: too short')
    magic = blob[:4]
    if magic != MAGIC:
        raise ValueError('Bad magic header')
    ver, flags = struct.unpack('<BB', blob[4:6])
    if ver != VERSION:
        raise ValueError('Unsupported version')

    comp = blob[6:]
    payload = lzma.decompress(comp)

    t, c = int(shape[0]), int(shape[1])
    n = t * c
    if flags & FLAG_SHUFFLE:
        if len(payload) != 2 * n:
            raise ValueError('Size mismatch after decompression')
        u16 = _byte_unshuffle_u16_le(payload, n)
    else:
        # Not used in this version, but kept for forward-compat
        u16 = np.frombuffer(payload, dtype=np.dtype('<u2'), count=n)

    # Inverse ZigZag
    if flags & FLAG_ZIGZAG:
        e = _zigzag_decode_u16(u16)
    else:
        e = u16.view(np.int16)

    # Inverse channel difference: prefix sum along axis=1
    if flags & FLAG_C_DIFF:
        e32 = e.reshape((t, c)).astype(np.int32)
        y = np.cumsum(e32, axis=1).astype(np.int16)
    else:
        y = e

    # Inverse temporal difference: prefix sum along axis=0
    if flags & FLAG_T_DIFF:
        y32 = y.astype(np.int32)
        x = np.cumsum(y32, axis=0).astype(np.dtype('<i2'))
    else:
        x = y.astype(np.dtype('<i2'))

    # Ensure shape/dtype
    x = x.reshape((t, c)).astype(np.dtype('<i2'), copy=False)
    return x
