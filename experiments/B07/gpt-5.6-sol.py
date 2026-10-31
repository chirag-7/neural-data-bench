import numpy as np
import lzma
import bz2


def _cost(v):
    a = np.abs(v.astype(np.int32))
    return np.log1p(a).sum(axis=0)


def _pred(y1, y2, qa, qb):
    num = y1.astype(np.int32) * qa + y2.astype(np.int32) * qb
    return (num + 8) // 16


def compress(array):
    x = np.asarray(array, dtype='<i2', order='C')
    t, c = x.shape

    mean = np.rint(x.astype(np.float64).mean(axis=0)).astype(np.int32)
    y = (x.astype(np.int32) - mean).astype(np.int16)

    y1 = y[1:-1].astype(np.int64)
    y2 = y[:-2].astype(np.int64)
    yt = y[2:].astype(np.int64)

    s11 = np.sum(y1 * y1, axis=0, dtype=np.int64).astype(np.float64)
    s22 = np.sum(y2 * y2, axis=0, dtype=np.int64).astype(np.float64)
    s12 = np.sum(y1 * y2, axis=0, dtype=np.int64).astype(np.float64)
    b1 = np.sum(yt * y1, axis=0, dtype=np.int64).astype(np.float64)
    b2 = np.sum(yt * y2, axis=0, dtype=np.int64).astype(np.float64)
    den = s11 * s22 - s12 * s12
    good = den > 1e-10 * np.maximum(1.0, s11 * s22)

    af = np.zeros(c, dtype=np.float64)
    bf = np.zeros(c, dtype=np.float64)
    af[good] = (b1[good] * s22[good] - b2[good] * s12[good]) / den[good]
    bf[good] = (b2[good] * s11[good] - b1[good] * s12[good]) / den[good]
    qa = np.clip(np.rint(16.0 * af), -32, 32).astype(np.int32)
    qb = np.clip(np.rint(16.0 * bf), -32, 32).astype(np.int32)

    rr = (yt - _pred(y1, y2, qa, qb)).astype(np.int16)
    best = _cost(rr)
    fixed = ((0, 0), (8, 0), (12, 0), (16, 0),
             (8, -4), (12, -4), (16, -4), (16, -8))
    for aa, bb in fixed:
        cand = (yt - _pred(y1, y2, aa, bb)).astype(np.int16)
        cc = _cost(cand)
        take = cc < best
        qa[take] = aa
        qb[take] = bb
        best[take] = cc[take]

    r = np.empty_like(y)
    r[:2] = y[:2]
    r[2:] = (yt - _pred(y1, y2, qa, qb)).astype(np.int16)

    z = r.copy()
    smode = np.zeros(c, dtype=np.uint8)
    best = _cost(r)

    cand = (r[:, 1:].astype(np.int32) -
            r[:, :-1].astype(np.int32)).astype(np.int16)
    cc = _cost(cand)
    take = cc < best[1:]
    idx = np.nonzero(take)[0] + 1
    z[:, idx] = cand[:, take]
    smode[idx] = 1
    best[idx] = cc[take]

    if c > 2:
        cand = (r[:, 2:].astype(np.int32) -
                r[:, :-2].astype(np.int32)).astype(np.int16)
        cc = _cost(cand)
        take = cc < best[2:]
        idx = np.nonzero(take)[0] + 2
        z[:, idx] = cand[:, take]
        smode[idx] = 2
        best[idx] = cc[take]

        av = (r[:, 1:-1].astype(np.int32) +
              r[:, :-2].astype(np.int32)) // 2
        cand = (r[:, 2:].astype(np.int32) - av).astype(np.int16)
        cc = _cost(cand)
        take = cc < best[2:]
        idx = np.nonzero(take)[0] + 2
        z[:, idx] = cand[:, take]
        smode[idx] = 3
        best[idx] = cc[take]

    v = z.astype(np.int32)
    u = ((v << 1) ^ (v >> 15)).astype(np.uint16)
    ut = np.ascontiguousarray(u.T)
    lo = (ut & 255).astype(np.uint8).tobytes()
    hi = (ut >> 8).astype(np.uint8).tobytes()

    meta = (mean.astype('<i2').tobytes() +
            qa.astype(np.int8).tobytes() +
            qb.astype(np.int8).tobytes() +
            smode.tobytes())
    payload = meta + lo + hi

    a = lzma.compress(payload, format=lzma.FORMAT_XZ,
                      preset=6 | lzma.PRESET_EXTREME)
    b = bz2.compress(payload, compresslevel=9)
    return b if len(b) < len(a) else a


def decompress(blob, shape, dtype):
    raw = bz2.decompress(blob) if blob[:3] == b'BZh' else lzma.decompress(blob)
    t, c = tuple(shape)
    n = t * c
    off = 0

    mean = np.frombuffer(raw, dtype='<i2', count=c, offset=off).astype(np.int32)
    off += 2 * c
    qa = np.frombuffer(raw, dtype=np.int8, count=c, offset=off).astype(np.int32)
    off += c
    qb = np.frombuffer(raw, dtype=np.int8, count=c, offset=off).astype(np.int32)
    off += c
    smode = np.frombuffer(raw, dtype=np.uint8, count=c, offset=off)
    off += c

    lo = np.frombuffer(raw, dtype=np.uint8, count=n, offset=off)
    off += n
    hi = np.frombuffer(raw, dtype=np.uint8, count=n, offset=off)
    u = (lo.astype(np.uint16) | (hi.astype(np.uint16) << 8))
    u = u.reshape(c, t).T.copy()
    z = ((u >> 1).astype(np.int32) ^
         -(u & 1).astype(np.int32)).astype(np.int16)

    r = np.empty_like(z)
    for j in range(c):
        mode = int(smode[j])
        if mode == 0:
            r[:, j] = z[:, j]
        elif mode == 1:
            r[:, j] = (z[:, j].astype(np.int32) +
                       r[:, j - 1].astype(np.int32)).astype(np.int16)
        elif mode == 2:
            r[:, j] = (z[:, j].astype(np.int32) +
                       r[:, j - 2].astype(np.int32)).astype(np.int16)
        else:
            p = (r[:, j - 1].astype(np.int32) +
                 r[:, j - 2].astype(np.int32)) // 2
            r[:, j] = (z[:, j].astype(np.int32) + p).astype(np.int16)

    y = np.empty_like(r)
    y[:2] = r[:2]
    for k in range(2, t):
        p = _pred(y[k - 1], y[k - 2], qa, qb)
        y[k] = (r[k].astype(np.int32) + p).astype(np.int16)

    out = (y.astype(np.int32) + mean).astype(np.int16)
    return np.ascontiguousarray(out.reshape(shape).astype(np.dtype(dtype), copy=False))