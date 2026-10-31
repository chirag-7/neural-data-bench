import numpy as np
import zlib
import struct

_P = 8
_LAGS = (1, 2, 3, 4, 8, 16)
_B = 512
_G = 16
_R = 14
_TOT = 1 << _R
_LOW = 1 << 23


def _fit(v, spatial):
    v = v.astype(np.float64)
    t, c = v.shape
    if spatial:
        a = []
        for lag in _LAGS:
            w = np.zeros_like(v)
            if lag < c:
                w[:, lag:] = v[:, :-lag]
            a.append(w)
        y = v
    else:
        a = [v[_P-lag:t-lag] for lag in range(1, _P+1)]
        y = v[_P:]
    d = len(a)
    m = np.empty((c, d, d), dtype=np.float64)
    b = np.empty((c, d), dtype=np.float64)
    ridge = np.maximum(np.einsum('tc,tc->c', y, y), 1.0) * 0.0001
    for i in range(d):
        b[:, i] = np.einsum('tc,tc->c', a[i], y)
        for j in range(i+1):
            q = np.einsum('tc,tc->c', a[i], a[j])
            m[:, i, j] = q
            m[:, j, i] = q
        m[:, i, i] += ridge
    coef = np.linalg.solve(m, b[..., None])[..., 0]
    return np.clip(np.rint(coef * 4096), -32768, 32767).astype(np.int64)


def _models(symbols):
    n = len(symbols)
    indices = np.arange(n, dtype=np.int64)[:, None] * 64 + symbols
    hist = np.bincount(indices.ravel(), minlength=n*64).reshape(n, 64)
    x = np.sqrt(hist / float(_B))
    centers = np.empty((_G, 64), dtype=np.float64)
    nearest = np.full(n, np.inf)
    pick = int(np.argmax(np.sum((x-x.mean(axis=0))**2, axis=1)))
    for g in range(_G):
        centers[g] = x[pick]
        nearest = np.minimum(nearest, np.sum((x-centers[g])**2, axis=1))
        pick = int(np.argmax(nearest))
    for iteration in range(10):
        distances = (np.sum(x*x, axis=1)[:, None]
                     + np.sum(centers*centers, axis=1)[None, :]
                     - 2 * (x @ centers.T))
        labels = np.argmin(distances, axis=1)
        for g in range(_G):
            mask = labels == g
            if np.any(mask):
                centers[g] = x[mask].mean(axis=0)
    counts = np.zeros((_G, 64), dtype=np.int64)
    np.add.at(counts, labels, hist)
    frequencies = np.zeros_like(counts)
    for g, row in enumerate(counts):
        if not row.sum():
            frequencies[g, 0] = _TOT
            continue
        f = np.rint(row * (_TOT / float(row.sum()))).astype(np.int64)
        f = np.where(row > 0, np.maximum(f, 1), 0)
        f[int(np.argmax(row))] += _TOT - int(f.sum())
        frequencies[g] = f
    return labels.astype(np.uint8), frequencies


def _tables(frequencies):
    fs = frequencies.tolist()
    cs = []
    for row in fs:
        total = 0
        starts = []
        for f in row:
            starts.append(total)
            total += f
        cs.append(starts)
    return fs, cs


def _encode_ans(symbols, labels, frequencies):
    fs, cs = _tables(frequencies)
    state = _LOW
    output = bytearray()
    put = output.append
    for b in range(len(symbols)-1, -1, -1):
        group = int(labels[b])
        freq, starts = fs[group], cs[group]
        for symbol in symbols[b, ::-1].tolist():
            f = freq[symbol]
            limit = f << (23-_R+8)
            while state >= limit:
                put(state & 255)
                state >>= 8
            state = ((state // f) << _R) + state % f + starts[symbol]
    return state.to_bytes(4, 'little') + bytes(output[::-1])


def _decode_ans(stream, labels, frequencies):
    fs, cs = _tables(frequencies)
    lookup = []
    for row in fs:
        table = bytearray()
        for symbol, f in enumerate(row):
            table.extend(bytes([symbol]) * f)
        lookup.append(table)
    output = np.empty((len(labels), _B), dtype=np.uint8)
    state = int.from_bytes(stream[:4], 'little')
    pos = 4
    for b, group in enumerate(labels.tolist()):
        freq, starts, table = fs[group], cs[group], lookup[group]
        values = []
        append = values.append
        for i in range(_B):
            slot = state & (_TOT-1)
            symbol = table[slot]
            append(symbol)
            state = freq[symbol] * (state >> _R) + slot - starts[symbol]
            while state < _LOW:
                state = (state << 8) | stream[pos]
                pos += 1
        output[b] = values
    return output


def compress(array):
    x = np.asarray(array, dtype=np.int16).astype(np.int64)
    t, c = x.shape
    offsets = np.rint(x.mean(axis=0)).astype(np.int16)
    x = (x-offsets).astype(np.int16).astype(np.int64)
    temporal = _fit(x, False)
    p = np.zeros_like(x)
    for j in range(_P):
        lag = j+1
        p[lag:] += x[:-lag] * temporal[:, j]
    e = (x-((p+2048) >> 12)).astype(np.int16).astype(np.int64)
    spatial = _fit(e, True)
    p.fill(0)
    for j, lag in enumerate(_LAGS):
        if lag < c:
            p[:, lag:] += e[:, :-lag] * spatial[lag:, j]
    r = (e-((p+2048) >> 12)).astype(np.int16).T.ravel().astype(np.int32)
    n = r.size
    blocks = (n+_B-1) // _B
    r = np.pad(r, (0, blocks*_B-n)).reshape(blocks, _B)
    k = np.clip(np.floor(np.log2(np.mean(np.abs(r), axis=1)+1))-1, 0, 14).astype(np.int32)
    u = (r << 1) ^ (r >> 15)
    q = u >> k[:, None]
    exponent = np.maximum(np.frexp(q)[1].astype(np.int32)-1, 0)
    extra = np.where(q < 16, 0, exponent-2)
    symbols = np.where(q < 16, q, 16+(exponent-4)*4+((q >> np.maximum(exponent-2, 0)) & 3)).astype(np.uint8)
    labels, frequencies = _models(symbols)
    entropy = _encode_ans(symbols, labels, frequencies)
    widths = (k[:, None]+extra).ravel()
    flat = u.ravel()
    planes = []
    for bit in range(16):
        mask = widths > bit
        planes.append(np.packbits(((flat[mask] >> bit) & 1).astype(np.uint8), bitorder='little').tobytes())
    raw = b''.join(planes)
    packed = zlib.compress(raw, 1)
    flag = int(len(packed) < len(raw))
    if flag:
        raw = packed
    keys = ((labels.astype(np.int32) << 4) | k).astype(np.uint8)
    header = (bytes([flag]) + offsets.astype('<i2').tobytes()
              + temporal.astype('<i2').tobytes() + spatial.astype('<i2').tobytes()
              + keys.tobytes() + frequencies.astype('<u2').tobytes())
    header = zlib.compress(header, 9)
    return struct.pack('<II', len(header), len(entropy)) + header + entropy + raw


def decompress(blob, shape, dtype):
    t, c = map(int, shape)
    n = t*c
    blocks = (n+_B-1) // _B
    hlen, elen = struct.unpack_from('<II', blob)
    header = zlib.decompress(blob[8:8+hlen])
    pos = 1
    def take(dt, count):
        nonlocal pos
        result = np.frombuffer(header, dtype=dt, count=count, offset=pos).copy()
        pos += np.dtype(dt).itemsize * count
        return result
    offsets = take('<i2', c).astype(np.int64)
    temporal = take('<i2', c*_P).reshape(c, _P).astype(np.int64)
    spatial = take('<i2', c*len(_LAGS)).reshape(c, len(_LAGS)).astype(np.int64)
    keys = take('u1', blocks)
    k = (keys & 15).astype(np.int32)
    labels = keys >> 4
    frequencies = take('<u2', _G*64).reshape(_G, 64)
    start = 8+hlen
    symbols = _decode_ans(blob[start:start+elen], labels, frequencies).astype(np.int32)
    extra = np.where(symbols < 16, 0, 2+(symbols-16)//4)
    base = np.where(symbols < 16, symbols, (4+((symbols-16) & 3)) << extra)
    u = (base << k[:, None]).ravel()
    widths = (extra+k[:, None]).ravel()
    raw = blob[start+elen:]
    if header[0]:
        raw = zlib.decompress(raw)
    pos = 0
    for bit in range(16):
        mask = widths > bit
        count = int(np.count_nonzero(mask))
        size = (count+7)//8
        bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8, count=size, offset=pos), bitorder='little', count=count)
        u[mask] |= bits.astype(np.int32) << bit
        pos += size
    r = ((u >> 1) ^ -(u & 1))[:n].reshape(c, t).T.astype(np.int64)
    e = np.empty_like(r)
    for channel in range(c):
        p = np.zeros(t, dtype=np.int64)
        for j, lag in enumerate(_LAGS):
            if channel >= lag:
                p += e[:, channel-lag] * spatial[channel, j]
        e[:, channel] = (r[:, channel]+((p+2048) >> 12)).astype(np.int16)
    x = np.empty_like(e)
    for row in range(t):
        p = np.zeros(c, dtype=np.int64)
        for j in range(min(_P, row)):
            p += x[row-j-1] * temporal[:, j]
        x[row] = (e[row]+((p+2048) >> 12)).astype(np.int16)
    return np.ascontiguousarray((x+offsets).astype(np.dtype(dtype)).reshape(shape))
