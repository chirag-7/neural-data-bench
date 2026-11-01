import numpy as np
import lzma

# Fixed quantization grid (50 microseconds)
_TICK_S = 5e-5
_INV_TICK = 1.0 / _TICK_S  # 20000.0
# Small bias in tick units to avoid rare floor-underflow at boundaries
_FLOOR_BIAS = 1e-7

# Varint helpers (LEB128) with ZigZag for signed
class _BW:
    def __init__(self):
        self.b = bytearray()
    def put_u(self, x):
        x = int(x)
        while x >= 0x80:
            self.b.append((x & 0x7F) | 0x80)
            x >>= 7
        self.b.append(x & 0x7F)
    def put_s(self, y):
        # ZigZag: map signed to unsigned
        z = (y << 1) ^ (y >> 63)
        # Python ints are unbounded; >> keeps sign for negatives
        self.put_u(z)

class _BR:
    def __init__(self, data):
        self.d = data
        self.i = 0
        self.n = len(data)
    def get_u(self):
        x = 0
        shift = 0
        d = self.d
        i = self.i
        n = self.n
        while True:
            if i >= n:
                raise ValueError('Truncated varint')
            b = d[i]
            i += 1
            x |= (b & 0x7F) << shift
            if b < 0x80:
                break
            shift += 7
        self.i = i
        return x
    def get_s(self):
        z = self.get_u()
        return (z >> 1) ^ -(z & 1)


def compress(times, labels):
    """Compress globally sorted float64 times (s) and int32 labels to bytes."""
    t = np.asarray(times, dtype=np.float64)
    lb = np.asarray(labels, dtype=np.int32)
    if t.ndim != 1 or lb.ndim != 1 or t.size != lb.size or t.size == 0:
        raise ValueError('times and labels must be 1D, same length, non-empty')
    n = int(t.size)

    # Quantize to ticks with monotone floor
    ticks = np.floor(t * _INV_TICK + _FLOOR_BIAS).astype(np.int64)
    if np.any(np.diff(ticks) < 0):
        # Should not happen for nondecreasing input; guard against FP anomalies
        ticks = np.maximum.accumulate(ticks)

    # Label palette and indices
    palette = np.unique(lb)
    u = int(palette.size)
    # Map labels to indices via searchsorted (palette is sorted)
    idx = np.searchsorted(palette, lb).astype(np.int64)

    # Byte buffer
    bw = _BW()
    # Counts
    bw.put_u(n)
    bw.put_u(u)
    # Palette: delta + zigzag
    p0 = int(palette[0])
    bw.put_s(p0)
    for i in range(1, u):
        bw.put_s(int(palette[i]) - int(palette[i - 1]))

    # Time ticks: first absolute (signed), then unsigned deltas
    bw.put_s(int(ticks[0]))
    if n > 1:
        dt = np.diff(ticks)
        # Ensure nonnegative
        if np.any(dt < 0):
            # Fallback safety: enforce monotone deltas
            dt = np.maximum(dt, 0)
        for d in dt:
            bw.put_u(int(d))

    # Label indices as minimal fixed-width bytes
    if u <= 256:
        bpi = 1
        idx_bytes = idx.astype(np.uint8).tobytes()
    elif u <= 65536:
        bpi = 2
        idx_bytes = idx.astype(np.uint16).tobytes()
    else:
        bpi = 4
        idx_bytes = idx.astype(np.uint32).tobytes()
    # Append index bytes
    bw.b.extend(idx_bytes)

    payload = bytes(bw.b)
    blob = lzma.compress(payload, format=lzma.FORMAT_XZ, preset=6)
    return blob


def decompress(blob):
    """Decompress bytes back to (times float64, labels int32)."""
    payload = lzma.decompress(blob, format=lzma.FORMAT_XZ)
    br = _BR(payload)

    n = br.get_u()
    u = br.get_u()
    if n <= 0 or u <= 0:
        raise ValueError('Invalid counts')

    # Reconstruct palette
    palette = np.empty(u, dtype=np.int64)
    cur = br.get_s()
    palette[0] = cur
    for i in range(1, u):
        cur = cur + br.get_s()
        palette[i] = cur
    palette = palette.astype(np.int32)

    # Reconstruct ticks
    t0 = br.get_s()
    if n > 1:
        dt_list = [0] * (n - 1)
        for i in range(n - 1):
            dt_list[i] = br.get_u()
        dt = np.frombuffer(np.array(dt_list, dtype=np.int64), dtype=np.int64)
        ticks = np.empty(n, dtype=np.int64)
        ticks[0] = int(t0)
        ticks[1:] = ticks[0] + np.cumsum(dt)
    else:
        ticks = np.array([int(t0)], dtype=np.int64)

    # Remaining bytes are label indices
    bpi = 1 if u <= 256 else (2 if u <= 65536 else 4)
    byte_pos = br.i
    need = n * bpi
    if byte_pos + need != len(payload):
        # Allow exact read; if extra bytes exist or insufficient, it's malformed
        if byte_pos + need > len(payload):
            raise ValueError('Truncated label bytes')
    idx_bytes = memoryview(payload)[byte_pos:byte_pos + need]
    if bpi == 1:
        idx = np.frombuffer(idx_bytes, dtype=np.uint8, count=n)
    elif bpi == 2:
        idx = np.frombuffer(idx_bytes, dtype='<u2', count=n)
    else:
        idx = np.frombuffer(idx_bytes, dtype='<u4', count=n)

    # Map indices back to labels
    labels = palette[idx].astype(np.int32, copy=False)

    # Convert ticks back to times
    times = ticks.astype(np.float64) * _TICK_S
    # Enforce nondecreasing numerically (should already hold)
    if np.any(np.diff(times) < 0):
        times = np.maximum.accumulate(times)

    return times, labels
