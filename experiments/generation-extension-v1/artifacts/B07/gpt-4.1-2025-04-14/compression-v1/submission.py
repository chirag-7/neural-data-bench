
import numpy as np
import struct
import zlib
import bz2
import lzma
import io

# Codec header format:
# 4 bytes magic identifier, 1 byte codec selector, 0/1 byte predictor type, then the rest
MAGIC = b'NPX4'
CODEC_IDS = {'z': 0, 'b': 1, 'l': 2}
CODEC_NAMES = ['z', 'b', 'l']
PREDICTOR_DELTA = 0 # currently only one, simple per-channel delta predictor

# Helper: delta encode along axis=0 (time), in-place for speed
# Stores first row verbatim, then diffs
# shape (4096, 384), dtype '<i2'
def delta_encode(arr):
    first_row = arr[0].copy()
    diffs = np.diff(arr, axis=0).astype(np.int16)
    return first_row, diffs

def delta_decode(first_row, diffs):
    # Reconstruct along axis=0
    output = np.empty((diffs.shape[0]+1, diffs.shape[1]), dtype=np.int16)
    output[0] = first_row
    np.cumsum(diffs, axis=0, out=output[1:])
    output[1:] += first_row  # broadcast first_row
    return output

# Try all compressors, return best (zlib, bz2, lzma)
def best_compressor(data):
    cz = zlib.compress(data, level=9)
    cb = bz2.compress(data)
    cl = lzma.compress(data, preset=9 | lzma.PRESET_EXTREME)
    blobs = [cz, cb, cl]
    idx = int(np.argmin([len(cz), len(cb), len(cl)]))
    return CODEC_NAMES[idx], blobs[idx]

def compress(array):
    # Expect shape (4096,384), dtype '<i2', C-contiguous
    assert array.dtype == np.dtype('<i2')
    assert array.shape == (4096, 384)
    predictor_id = PREDICTOR_DELTA
    first_row, diffs = delta_encode(array)
    # Pack first row and diffs
    packed = first_row.tobytes(order='C') + diffs.tobytes(order='C')
    codec_name, blob = best_compressor(packed)
    codec_id = CODEC_IDS[codec_name]
    # Header: magic(4), codec(1), predictor(1)
    header = MAGIC + struct.pack('BB', codec_id, predictor_id)
    return header + blob

def decompress(blob, shape, dtype):
    # shape is (4096,384), dtype is '<i2' (int16-little)
    assert dtype == '<i2'
    assert shape == (4096, 384)
    # Parse header
    if blob[:4] != MAGIC:
        raise ValueError('Invalid codec magic')
    codec_id, predictor_id = struct.unpack('BB', blob[4:6])
    codec_name = CODEC_NAMES[codec_id]
    data = blob[6:]
    if codec_name == 'z':
        raw = zlib.decompress(data)
    elif codec_name == 'b':
        raw = bz2.decompress(data)
    elif codec_name == 'l':
        raw = lzma.decompress(data)
    else:
        raise ValueError('Invalid codec')
    # Unpack first row, then diffs
    ch = shape[1]
    first_row_bytes = ch * 2
    first_row = np.frombuffer(raw[:first_row_bytes], dtype=np.int16)
    diffs = np.frombuffer(raw[first_row_bytes:], dtype=np.int16).reshape(shape[0]-1, ch)
    arr = delta_decode(first_row, diffs)
    arr = np.ascontiguousarray(arr, dtype=dtype)
    return arr

# Example usage (commented out since no I/O or data):
# array = np.random.randint(-32768, 32767, (4096,384), dtype='<i2')
# blob = compress(array)
# restored = decompress(blob, (4096,384), '<i2')
# assert np.array_equal(restored, array)
