# B08: spike-event compression with fixed timing tolerance

## Original data and source deviation

Use all seven previously acquired CC BY 4.0 FALCON M2 calibration runs from DANDI 000953: four recording days, 96 units per run, one monkey, 1,052,545 events. The [manifest](../../data/manifests/B08.json) pins prepared arrays, original component byte hashes and immutable DANDI assets. Full NWB hashes are provider-reported, not independently verified full-file downloads. Original spike-time, unit-ID and ragged-index arrays match previous independently checked extraction hashes. Expand unit labels and apply a stable global time sort, preserving every original float64 timestamp and corresponding int32 label. No input quantization or selected high-quality event subset.

This is an explicit alternate to the proposed IBL source. Anonymous access to the first IBL benchmark insertion metadata returned HTTP403; authenticated original IBL acquisition was not established. FALCON source access/terms are already verified. These are the same recordings as G01: a new endpoint is not an independent dataset or animal cohort.

## Fidelity contract and interface

Implement compress(times, labels) returning bytes and decompress(blob) returning (times, labels). Each input is one complete recording, globally time-sorted float64 seconds and corresponding int32 recorded unit IDs. Decoder receives only the blob and a fresh implementation namespace, no encoder state, input arrays, files or external metadata. Every emitted byte including headers, origin, counts and codec selectors counts. Implementation code is shared and not charged per recording.

**Timing is intentionally lossy:** preserve all events and labels in the same order, nondecreasing decoded times and absolute timing error at most 50 microseconds/event (numerical allowance 1e-10 seconds). Labels remain exact; no dropping, merging or inventing events, including events quantized to the same tick. Spikepack's 100-microsecond grid does not preserve exact original timing. General programs may retain higher precision. No neural interpretation, spike-sorting accuracy or unknown biological timing truth is scored.

Allowed general libraries: NumPy/SciPy/scikit-learn, ordinary utilities and standard zlib/bz2/lzma/struct/json/io/base64. No specialist libraries, pretrained assets, file/network/subprocess access, dynamic execution or source-specific lookup. One high-effort no-tool generation per exact GPT-5.6 Sol, GPT-6 Sol and GPT-6.1 Sol; unchanged programs, no feedback/repairs, below 240 total lines. 180 seconds total for seven encode/decode calls; one numerical CPU thread; 4 GB requested but not enforced. No supervised training/calibration split; codecs adapt only to each input.

## Fixed references, metrics and audit

Primary: mean encoded bits/event across seven recordings, lower better, conditional on every recording passing fidelity. Unequal event counts do not make the primary event-pooled. Total encoded bytes, maximum timing errors and encode/decode call times are descriptive secondary measures. Failures receive no fabricated zero score.

Use original **Spikepack 0.1.0** source at commit 30ab06ff7794d89cab17cb54338db869ad90d036; MIT code retained under upstream. Its unchanged Blosc-directory writer uses 100-us quantization, narrow integer deltas and Blosc/Zstd with shuffle. Transport files in a transparent name/length frame; count every original metadata/payload byte plus framing. Decoder restores the directory and uses the original reader. Temporary filesystem and compiled codec overhead differ from general in-memory programs and are included in call times. This is local original-code execution on another source, not its eleven-IBL-insertion benchmark or current global best.

The conventional baseline uses the first timestamp as origin, 100-us quantization, uint64 temporal deltas, raw int32 labels and zlib9. Both references are fixed before model calls or any real-source method size/score. API preflight uses unrelated synthetic arrays only. Implementation and research effort differ.

Retain successful compressed blobs, exact labels/time hashes, maximum errors and generation events. Independent audit decodes saved blobs in fresh namespaces, checks every label/timing bound, recomputes per-record size and mean primary, and checks source/prepared/frozen hashes. No outcome-based pruning. [Codec source](https://github.com/int-brain-lab/spikepack), [DANDI](https://dandiarchive.org/dandiset/000953), [original acquisition and terms](../../data/manifests/G01.json).
