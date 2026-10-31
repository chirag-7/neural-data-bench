import numpy as np
import zlib
import bz2
import lzma
import struct


def compress(array):
    x = np.asarray(array)
    t, c = x.shape
    a = x.astype(np.int32)
    d = np.empty_like(a)
    d[0] = a[0]
    d[1:] = a[1:] - a[:-1]

    best = np.full(c, np.inf)
    modes = np.zeros(c, dtype=np.uint8)
    centers = np.zeros(c, dtype=np.int16)
    residual = np.empty((t, c), dtype=np.int16)

    def consider(candidate, mode, invalid=0):
        r = candidate.astype(np.int16)
        center = np.median(r[::8], axis=0).astype(np.int16)
        centered = (r.astype(np.int32) - center).astype(np.int16)
        score = np.log2(np.abs(centered.astype(np.int32)) + 1).mean(axis=0)
        score[:invalid] = np.inf
        take = score < best
        best[take] = score[take]
        modes[take] = mode
        centers[take] = center[take]
        residual[:, take] = centered[:, take]

    consider(a, 0)
    consider(d, 1)
    candidate = np.empty_like(a)
    for k, lag in enumerate((1, 2, 4)):
        candidate[:, :lag] = a[:, :lag]
        candidate[:, lag:] = a[:, lag:] - a[:, :-lag]
        consider(candidate, 2 + 2 * k, lag)
        candidate[:, :lag] = d[:, :lag]
        candidate[:, lag:] = d[:, lag:] - d[:, :-lag]
        consider(candidate, 3 + 2 * k, lag)

    r = residual.astype(np.int32)
    mapped = ((r << 1) ^ (r >> 15)).astype(np.uint16)
    low = (mapped & 255).astype(np.uint8).T.tobytes()
    high = (mapped >> 8).astype(np.uint8).T.tobytes()
    payload = low + high
    meta = zlib.compress(modes.tobytes() + centers.astype('<i2').tobytes())
    choices = (zlib.compress(payload, 6),
               bz2.compress(payload, compresslevel=9),
               lzma.compress(payload, preset=4))
    codec = min(range(3), key=lambda i: len(choices[i]))
    return struct.pack('<BH', codec, len(meta)) + meta + choices[codec]


def decompress(blob, shape, dtype):
    t, c = shape
    codec, meta_len = struct.unpack_from('<BH', blob, 0)
    meta = zlib.decompress(blob[3:3 + meta_len])
    modes = np.frombuffer(meta[:c], dtype=np.uint8)
    centers = np.frombuffer(meta[c:c + 2 * c], dtype='<i2').astype(np.int32)
    data = blob[3 + meta_len:]
    if codec == 0:
        payload = zlib.decompress(data)
    elif codec == 1:
        payload = bz2.decompress(data)
    else:
        payload = lzma.decompress(data)

    n = t * c
    low = np.frombuffer(payload[:n], dtype=np.uint8).astype(np.int32)
    high = np.frombuffer(payload[n:], dtype=np.uint8).astype(np.int32)
    mapped = low | (high << 8)
    values = ((mapped >> 1) ^ -(mapped & 1)).reshape(c, t).T
    residual = values + centers[None, :]
    out = np.empty(shape, dtype=np.dtype(dtype))
    for j in range(c):
        mode = int(modes[j])
        if mode == 0:
            out[:, j] = residual[:, j]
        elif mode == 1:
            out[:, j] = np.cumsum(residual[:, j], dtype=np.int32)
        else:
            lag = (1, 2, 4)[(mode - 2) // 2]
            if mode & 1:
                value = np.cumsum(residual[:, j], dtype=np.int32)
            else:
                value = residual[:, j]
            out[:, j] = value + out[:, j - lag].astype(np.int32)
    return out