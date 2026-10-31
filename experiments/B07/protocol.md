# B07: lossless compression of real Neuropixels voltage

## Source and fixed slice

Use **all 16 experimental raw recordings** in the original [AIND compression benchmark](https://allenneuraldynamics.github.io/data.html): four AIND NP1, eight AIND NP2 and four IBL NP1. Original author [benchmark code](https://github.com/AllenNeuralDynamics/ephys-compression/tree/c89e8e481435f39e3bf041bfc0eaac5ef6d93900) identifies the same sessions. The original [AWS data registry](https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml) states CC BY 4.0; retain attribution to AIND/IBL and Buccino et al. The [manifest](../../data/manifests/B07.json) identifies exact objects, sizes, ETags, HTTP ranges, metadata and acquired SHA256s. S3 multipart ETags are identity guards, **not full-file SHA256s**. No full raw-file hash is claimed.

For every recording, select cached time samples `[1000000:1004096)` and **all 384 channels** in original time-major little-endian signed int16 order. Each chunk is 3,145,728 bytes. Total input is 50,331,648 bytes. Exactly 4,096 samples per recording (~0.137 seconds at nominal 30 kHz) is a short-chunk diagnostic, not the paper's full streaming/storage benchmark. No outcome, amplitude or signal-quality selection. Two animals recur across recordings/probes: 16 recordings represent 14 source animal identifiers, not 16 independent animals. No animal-level confidence intervals.

Original metadata are checked for 384 channels, signed little-endian int16, time-axis zero and file-offset zero. One IBL recording reports 30000.390639 Hz, others 30000 Hz; sample indices are fixed and no resampling occurs. The integer 30000 in the WavPack raw-PCM container is a common codec header convention, not replacement of original acquisition metadata. Metadata and physical calibration are not compressed in this numerical-byte task.

## Interface and allowed information

Generated code implements `compress(array) -> bytes` and `decompress(blob, shape, dtype) -> ndarray`. Each source array has shape `(4096,384)`, dtype `'<i2'`. Shape and dtype are common decoder arguments supplied equally to all methods. Every byte emitted by the encoder, including its headers/mode selectors, counts. Codec source code is a shared implementation and not charged per chunk. All array bytes must be reconstructed exactly in original order. No lossy filtering, common-average referencing, rescaling, quantization or discarded channel/time samples. Integer reversible transforms and data-dependent selection among allowed codecs are permitted within budget.

The generated compressor has no training labels or calibration set. It may adapt to the currently supplied input as any lossless codec does. This is not a supervised held-out-animal generalization experiment. Encoders receive no source/session identities. The decoder runs from a **fresh code namespace**, without encoder input/state. Independent verification later decodes saved blobs without first loading raw inputs into decoder state. Global input caches are not an admissible codec.

Allowed: NumPy, SciPy, scikit-learn and the existing standard utility modules, plus standard-library `zlib`, `bz2`, `lzma`, `struct`, `json`, `io` and `base64`. No WavPack, numcodecs, specialist packages, pretrained assets, file/network/subprocess access or dynamic execution in generated code. One high-effort no-tool generation per requested Sol model, identical explicit prompt, no execution feedback or repairs. Under 240 total lines. One numerical CPU thread; **180 seconds total to encode and decode all 16 chunks**, approximately 4 GB requested memory (not enforced). Deterministic output required. This measures model-generated codec programs with general libraries, not native model token compression.

## Frozen references

1. **WavPack 5.8.0 lossless very-high mode** (`-hh`, MD5 enabled, no lossy `-b`): official vendor source built under the workspace with `--disable-threads`. Uses the vendor extended-channel raw-PCM option `--raw-pcm-ex=30000,16,384` and pipe acknowledgement `-y`, raw PCM on stdin and compressed bytes on stdout; decoder produces raw PCM. All emitted container bytes count. Process startup is included in reported codec times. This is a domain-aligned reference from the original paper's codec family, not proof of current global best or an exact paper-runtime reproduction.
2. **Temporal delta + channel-major Blosc/Zstd9 bitshuffle**: modular int16 differences along time, retaining each channel's first value; transpose to channel-major and encode with numcodecs Blosc, Zstd level9, bitshuffle. Decode applies the exact inverse cumulative sum modulo int16. One Blosc thread. This is a fixed local preprocessing/codec combination, not a test-selected best configuration.
3. **Raw zlib9**: conventional task baseline without signal preprocessing.

All settings, input bytes, prompt, scorer and implementations are frozen before generation and any real-slice method score. Only unrelated synthetic byte arrays are used for dependency/API preflight. WavPack compiled code and specialist package access differ from general programs; research/implementation effort and I/O deployment histories are not matched.

## Metrics and artifacts

Primary: mean across all 16 recordings of `8 * encoded_blob_bytes / (4096 * 384)`, **encoded bits per raw scalar sample**, lower better. All chunks have equal shape. Original storage is 16 bits/sample. Full primary requires every chunk to decode byte-exactly; partial/inexact methods are recorded as failures and receive no invented numeric score. Keep partial logs/artifacts if any failure occurs.

Secondary: overall raw/encoded byte ratio, per-record compression and decompression elapsed times, and throughput. Reported `seconds` sums codec function time over the entire 16-recording call; no model-generation cost or full-dataset streaming/disk benchmark is implied. The subprocess timeout also bounds setup, verification and artifact writes. Shared shape/dtype are excluded equally; WavPack's unavoidable in-container metadata are included. No practical/significance equivalence threshold or population inference is declared.

Retain every encoded blob, its byte size/SHA256 and fresh-decoder raw-byte SHA256 in per-method output manifests, plus generated programs, raw generation logs, source manifests and execution records. An independent audit verifies source metadata and hashes, decodes every retained bitstream, compares **all raw bytes**, recomputes primary/secondary size arithmetic and checks freeze/provenance identities. This task is a lab infrastructure endpoint; codec success does not establish spike detection, neural interpretation or preservation under lossy compression.

[Worklog](worklog.md) · [run specification](run-spec.json) · [results](../../results/B07.json) · [release review](../../docs/release-v10.md).
