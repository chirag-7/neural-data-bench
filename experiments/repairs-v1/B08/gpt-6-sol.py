import heapq
import struct
import numpy as np


def _lengths(counts):
    lengths = bytearray(len(counts))
    heap = [(int(count), i, i) for i, count in enumerate(counts) if count]
    if not heap:
        return lengths
    if len(heap) == 1:
        lengths[heap[0][2]] = 1
        return lengths
    heapq.heapify(heap)
    serial = len(counts)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, (a[0] + b[0], serial, (a[2], b[2])))
        serial += 1
    stack = [(heap[0][2], 0)]
    while stack:
        node, depth = stack.pop()
        if isinstance(node, int):
            lengths[node] = depth
        else:
            stack.append((node[0], depth + 1))
            stack.append((node[1], depth + 1))
    return lengths


def _codes(lengths):
    enc = [(0, 0)] * len(lengths)
    dec = {}
    code = 0
    previous = 0
    for width, symbol in sorted((width, symbol) for symbol, width in enumerate(lengths) if width):
        code <<= width - previous
        enc[symbol] = (code, width)
        dec[(width, code)] = symbol
        code += 1
        previous = width
    return enc, dec, previous


class _Writer:
    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.bits = 0

    def write(self, value, width):
        self.acc = (self.acc << width) | value
        self.bits += width
        while self.bits >= 8:
            self.bits -= 8
            self.out.append((self.acc >> self.bits) & 255)
            self.acc &= (1 << self.bits) - 1

    def finish(self):
        if self.bits:
            self.out.append(self.acc << (8 - self.bits))
        return bytes(self.out)


class _Reader:
    def __init__(self, data, table, max_width):
        self.data = data
        self.table = table
        self.max_width = max_width
        self.pos = 0
        self.acc = 0
        self.bits = 0

    def read(self, width):
        value = 0
        for _ in range(width):
            if not self.bits:
                self.acc = self.data[self.pos]
                self.pos += 1
                self.bits = 8
            self.bits -= 1
            value = (value << 1) | ((self.acc >> self.bits) & 1)
        return value

    def symbol(self):
        code = 0
        for width in range(1, self.max_width + 1):
            code = (code << 1) | self.read(1)
            symbol = self.table.get((width, code))
            if symbol is not None:
                return symbol
        raise ValueError('Invalid Huffman stream')


def compress(times, labels):
    times = np.asarray(times, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int32)
    n = len(times)
    if len(labels) != n:
        raise ValueError('Mismatched input lengths')
    origin = float(times[0]) if n else 0.0
    ticks = np.rint((times - origin) * 10000.0).astype(np.int64)
    gaps = np.empty(n, dtype=np.int64)
    if n:
        gaps[0] = ticks[0]
        gaps[1:] = np.diff(ticks)
    symbols = np.minimum(gaps, 256)
    ids, inverse = np.unique(labels, return_inverse=True)
    gap_lengths = _lengths(np.bincount(symbols, minlength=257))
    label_lengths = _lengths(np.bincount(inverse, minlength=len(ids)))
    gap_codes, _, _ = _codes(gap_lengths)
    label_codes, _, _ = _codes(label_lengths)

    gap_writer = _Writer()
    for symbol, gap in zip(symbols, gaps):
        symbol = int(symbol)
        code, width = gap_codes[symbol]
        gap_writer.write(code, width)
        if symbol == 256:
            value = int(gap)
            while value >= 128:
                gap_writer.write((value & 127) | 128, 8)
                value >>= 7
            gap_writer.write(value, 8)
    gap_stream = gap_writer.finish()

    label_writer = _Writer()
    for symbol in inverse:
        code, width = label_codes[int(symbol)]
        label_writer.write(code, width)
    label_stream = label_writer.finish()

    header = struct.pack('<4sQdH', b'S2C1', n, origin, len(ids))
    header += ids.astype('<i4', copy=False).tobytes()
    header += bytes(gap_lengths) + bytes(label_lengths)
    header += struct.pack('<II', len(gap_stream), len(label_stream))
    return header + gap_stream + label_stream


def decompress(blob):
    magic, n, origin, count = struct.unpack_from('<4sQdH', blob, 0)
    if magic != b'S2C1':
        raise ValueError('Invalid blob')
    offset = struct.calcsize('<4sQdH')
    ids = np.frombuffer(blob, dtype='<i4', count=count, offset=offset)
    offset += 4 * count
    gap_lengths = blob[offset:offset + 257]
    offset += 257
    label_lengths = blob[offset:offset + count]
    offset += count
    gap_size, label_size = struct.unpack_from('<II', blob, offset)
    offset += 8
    _, gap_table, gap_max = _codes(gap_lengths)
    _, label_table, label_max = _codes(label_lengths)
    gap_reader = _Reader(blob[offset:offset + gap_size], gap_table, gap_max)
    offset += gap_size
    label_reader = _Reader(blob[offset:offset + label_size], label_table, label_max)

    ticks = np.empty(n, dtype=np.int64)
    labels = np.empty(n, dtype=np.int32)
    current = 0
    for i in range(n):
        gap = gap_reader.symbol()
        if gap == 256:
            gap = 0
            shift = 0
            while True:
                byte = gap_reader.read(8)
                gap |= (byte & 127) << shift
                if byte < 128:
                    break
                shift += 7
        current += gap
        ticks[i] = current
        labels[i] = ids[label_reader.symbol()]
    times = origin + ticks.astype(np.float64) * 0.0001
    return times, labels