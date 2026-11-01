import numpy as np
import zlib
import struct
import io

# Quantization grid (<=50 μs allowed error)
QUANT = 1e-5  # 10 microseconds
INV_QUANT = 1e5

# Helper: encode uint64 as varint stream
def encode_varints_uint64(arr):
    out = bytearray()
    for x in arr:
        while x >= 0x80:
            out.append((x & 0x7F) | 0x80)
            x >>= 7
        out.append(x & 0x7F)
    return bytes(out)

def decode_varints_uint64(byts, n):
    arr = np.empty(n, dtype=np.uint64)
    offset = 0
    for i in range(n):
        shift = 0
        val = 0
        while True:
            b = byts[offset]
            offset += 1
            val |= (b & 0x7F) << shift
            if not (b & 0x80): break
            shift += 7
        arr[i] = val
    return arr, offset

# Compress routine
def compress(times, labels):
    times = np.asarray(times, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int32)
    assert len(times) == len(labels)
    n = len(times)
    if n == 0:
        # Write an empty header and return
        return struct.pack('<Qdd', 0, 0.0, QUANT)
    # Time delta coding: quantize to grid
    # First store t0
    t0 = times[0]
    t_quantized = np.round((times - t0) * INV_QUANT).astype(np.uint64)
    deltas = np.empty(n, dtype=np.uint64)
    deltas[0] = t_quantized[0]
    deltas[1:] = t_quantized[1:] - t_quantized[:-1]
    varint_times = encode_varints_uint64(deltas)
    labels_raw = labels.astype(np.int32).tobytes()
    # Header: n (events, QWord), t0 (float64), quant (float64), section lengths (2x QWord)
    hdr = struct.pack('<QddQQ', n, t0, QUANT, len(varint_times), len(labels_raw))
    payload = varint_times + labels_raw
    cmpd = zlib.compress(payload, level=9)
    return hdr + cmpd

# Decompress routine
def decompress(blob):
    # Header: n, t0, quant, l_varint, l_labels
    hdrsize = struct.calcsize('<QddQQ')
    n, t0, quant, l_varint, l_labels = struct.unpack('<QddQQ', blob[:hdrsize])
    if n == 0:
        return np.zeros(0, dtype=np.float64), np.zeros(0, dtype=np.int32)
    decomp = zlib.decompress(blob[hdrsize:])
    varint_bytes = decomp[:l_varint]
    label_bytes = decomp[l_varint:l_varint + l_labels]
    deltas, _ = decode_varints_uint64(varint_bytes, n)
    tgrid = np.cumsum(deltas)
    times = t0 + tgrid * quant
    labels = np.frombuffer(label_bytes, dtype=np.int32)
    return times, labels
