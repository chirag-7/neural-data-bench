import struct, zlib, lzma, math
import numpy as np
_F = {'id': lzma.FILTER_LZMA2, 'dict_size': 1 << 20}
def _pack(b):
    options = [b'\x00' + b, b'\x01' + zlib.compress(b, 9)]
    if len(b) >= 64:
        f = dict(_F, preset=6, lc=0, lp=0, pb=0)
        options.append(b'\x02' + lzma.compress(b, format=lzma.FORMAT_RAW, filters=[f]))
    return min(options, key=len)
def _unpack(b):
    if b[0] == 0: return b[1:]
    if b[0] == 1: return zlib.decompress(b[1:])
    return lzma.decompress(b[1:], format=lzma.FORMAT_RAW, filters=[_F])
def _frame(parts):
    return struct.pack('<' + 'I' * len(parts), *map(len, parts)) + b''.join(parts)
def _parts(b, n):
    sizes = struct.unpack_from('<' + 'I' * n, b)
    p, out = 4 * n, []
    for size in sizes:
        out.append(b[p:p + size]); p += size
    return out
def _model(row):
    a = row.astype(np.int64)
    f = np.maximum(1, a * 4096 // int(a.sum()))
    f[a == 0] = 0
    difference = 4096 - int(f.sum())
    if difference > 0:
        f[int(np.argmax(a))] += difference
    while difference < 0:
        j = int(np.argmax(f)); take = min(int(f[j]) - 1, -difference)
        f[j] -= take; difference += take
    c = np.r_[0, np.cumsum(f[:-1])]
    return f.tolist(), c.tolist()
def _ans(s, hist, lengths):
    state, end, out = 1 << 23, len(s), bytearray()
    for g in range(len(lengths) - 1, -1, -1):
        start = end - int(lengths[g])
        f, c = _model(hist[g])
        for symbol in s[start:end][::-1]:
            symbol = int(symbol); frequency = f[symbol]
            threshold = frequency << 19
            while state >= threshold:
                out.append(state & 255); state >>= 8
            state = ((state // frequency) << 12) + state % frequency + c[symbol]
        end = start
    return struct.pack('<I', state) + bytes(out[::-1])
def _unans(b, hist, lengths):
    state = struct.unpack_from('<I', b)[0]
    p, position = 4, 0
    out = np.empty(int(np.sum(lengths)), dtype=np.uint16)
    for g, count in enumerate(lengths):
        f, c = _model(hist[g])
        table = np.repeat(np.arange(len(f), dtype=np.uint16), f).tolist()
        end = position + int(count)
        while position < end:
            slot = state & 4095; symbol = table[slot]
            out[position] = symbol; position += 1
            state = f[symbol] * (state >> 12) + slot - c[symbol]
            while state < (1 << 23):
                state = (state << 8) | b[p]; p += 1
    return out
def _cat(s, lengths):
    plain = b'\x00' + _pack(s.astype('<u2').tobytes())
    k = int(s.max()) + 1
    context = np.repeat(np.arange(len(lengths), dtype=np.int64), lengths)
    hist = np.bincount(context * k + s, minlength=len(lengths) * k)
    hist = hist.reshape(len(lengths), k).astype('<u4')
    coded = b'\x01' + struct.pack('<H', k) + _frame([
        _pack(hist.tobytes()), _ans(s, hist, lengths)])
    return min((plain, coded), key=len)
def _uncat(b, lengths):
    if b[0] == 0:
        return np.frombuffer(_unpack(b[1:]), dtype='<u2')
    k = struct.unpack_from('<H', b, 1)[0]
    h, a = _parts(b[3:], 2)
    hist = np.frombuffer(_unpack(h), dtype='<u4').reshape(len(lengths), k)
    return _unans(a, hist, lengths)
def _low(d, k):
    offsets = np.cumsum(k, dtype=np.int64) - k
    bits = np.empty(int(k.sum()), dtype=np.uint8)
    for j in range(int(k.max())):
        mask = k > j
        bits[offsets[mask] + j] = ((d[mask] >> j) & 1).astype(np.uint8)
    return np.packbits(bits, bitorder='little').tobytes()
def _unlow(b, k):
    bits = np.unpackbits(np.frombuffer(b, dtype=np.uint8), bitorder='little')
    offsets = np.cumsum(k, dtype=np.int64) - k
    out = np.zeros(len(k), dtype=np.int64)
    for j in range(int(k.max())):
        mask = k > j
        out[mask] |= bits[offsets[mask] + j].astype(np.int64) << j
    return out
def _encd(d, lengths, choices):
    e = np.maximum(np.frexp(d.astype(np.float64))[1] - 1, 0)
    edge = np.uint64(1) << e.astype(np.uint64)
    e = e - (d.astype(np.uint64) < edge)
    best = None
    for m in choices:
        k = np.maximum(e - m, 0).astype(np.int64)
        s = ((d >> k) + (1 << m) * k).astype(np.uint16)
        candidate = bytes([m]) + _frame([_cat(s, lengths), _pack(_low(d, k))])
        if best is None or len(candidate) < len(best): best = candidate
    return best
def _decd(b, lengths):
    m = b[0]; base = 1 << m
    symbols, lows = _parts(b[1:], 2)
    s = _uncat(symbols, lengths).astype(np.int64)
    k = np.maximum(s // base - 1, 0)
    return ((s - base * k) << k) + _unlow(_unpack(lows), k)
def _groups(q):
    e = np.flatnonzero(np.r_[True, q[1:] != q[:-1], True])
    return ((int(a), int(b)) for a, b in zip(e[:-1], e[1:]) if b - a > 1)
def _ties(q, labels):
    out, buffer, nbits = bytearray(), 0, 0
    for a, b in _groups(q):
        available = sorted(labels[a:b].tolist()); rank = 0
        for value in labels[a:b]:
            j = available.index(int(value))
            rank = rank * len(available) + j; available.pop(j)
        width = (math.factorial(b - a) - 1).bit_length()
        buffer |= rank << nbits; nbits += width
        while nbits >= 8:
            out.append(buffer & 255); buffer >>= 8; nbits -= 8
    if nbits: out.append(buffer & 255)
    return _pack(bytes(out))
def _unties(q, labels, encoded):
    data = _unpack(encoded); p, buffer, nbits = 0, 0, 0
    for a, b in _groups(q):
        m = b - a; width = (math.factorial(m) - 1).bit_length()
        while nbits < width:
            buffer |= data[p] << nbits; p += 1; nbits += 8
        rank = buffer & ((1 << width) - 1)
        buffer >>= width; nbits -= width
        digits = [0] * m
        for j in range(m - 1, -1, -1):
            rank, digits[j] = divmod(rank, m - j)
        available = labels[a:b].tolist()
        for j, digit in enumerate(digits): labels[a + j] = available.pop(digit)
    return labels
def compress(times, labels):
    times = np.asarray(times, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int32)
    n = len(times)
    if n == 0: return b'B8E'
    origin = float(times[0])
    q = np.rint((times - origin) * 10000.0).astype(np.int64)
    if not np.all(np.abs(origin + q / 10000.0 - times) <= 0.0000500001):
        return b'B8R' + _frame([_pack(times.astype('<f8').tobytes()),
                                  _pack(labels.astype('<i4').tobytes())])
    units, inv, counts = np.unique(labels, return_inverse=True, return_counts=True)
    metadata = struct.pack('<dI', origin, len(units))
    metadata += units.astype('<i4').tobytes() + counts.astype('<u4').tobytes()
    metadata = _pack(metadata)
    d = np.diff(q, prepend=np.int64(0))
    gt = _encd(d, np.array([n]), (2,))
    label_ans = b'\x01' + _ans(inv, counts.reshape(1, -1), [n])
    label_raw = b'\x00' + _pack(inv.astype('<u4').tobytes())
    global_blob = b'B8G' + _frame([metadata, gt, min((label_ans, label_raw), key=len)])
    order = np.argsort(inv, kind='stable'); grouped = q[order]
    starts = np.r_[0, np.cumsum(counts, dtype=np.int64)[:-1]]
    d = np.diff(grouped, prepend=np.int64(0)); d[starts] = grouped[starts]
    pt = _encd(d, counts, (1, 2, 3))
    unit_blob = b'B8P' + _frame([metadata, pt, _ties(q, labels)])
    return min((global_blob, unit_blob), key=len)
def decompress(blob):
    mode = blob[:3]
    if mode == b'B8E': return np.empty(0, np.float64), np.empty(0, np.int32)
    if mode == b'B8R':
        t, l = _parts(blob[3:], 2)
        return (np.frombuffer(_unpack(t), dtype='<f8').copy(),
                np.frombuffer(_unpack(l), dtype='<i4').copy())
    if mode not in (b'B8G', b'B8P'): raise ValueError('Invalid blob')
    meta, encoded, auxiliary = _parts(blob[3:], 3)
    meta = _unpack(meta); origin, u = struct.unpack_from('<dI', meta)
    units = np.frombuffer(meta, dtype='<i4', count=u, offset=12)
    counts = np.frombuffer(meta, dtype='<u4', count=u, offset=12 + 4 * u)
    n = int(counts.sum())
    if mode == b'B8G':
        q = np.cumsum(_decd(encoded, np.array([n])), dtype=np.int64)
        if auxiliary[0] == 1:
            inv = _unans(auxiliary[1:], counts.reshape(1, -1), [n])
        else: inv = np.frombuffer(_unpack(auxiliary[1:]), dtype='<u4')
        labels = units[inv].astype(np.int32)
    else:
        d = _decd(encoded, counts); q = np.empty(n, dtype=np.int64); p = 0
        for count in counts:
            end = p + int(count); q[p:end] = np.cumsum(d[p:end]); p = end
        order = np.argsort(q, kind='stable'); q = q[order]
        labels = np.repeat(units, counts)[order].astype(np.int32)
        labels = _unties(q, labels, auxiliary)
    return origin + q / 10000.0, labels
