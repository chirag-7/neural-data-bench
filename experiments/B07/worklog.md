# B07 experiment log

## Before freeze and generation

Selected all 16 source recordings already screened in release 0.9. Downloaded one fixed 4,096-sample range per recording and all 384 channels, retaining metadata, ETag identity guards and acquired byte hashes. Relaxed a metadata assertion from exactly 30000 Hz to a narrow nominal-30-kHz check after observing one original 30000.390639-Hz clock; did not resample or change indices.

A Python WavPack wrapper could not build without a system library. Built official WavPack 5.8.0 locally with threads disabled; cleaned stale objects before rebuilding. Synthetic-only preflight identified the vendor extended-channel raw-PCM switch and explicit pipe acknowledgement. All three fixed references then reconstructed an unrelated seeded synthetic int16 array exactly. No real-slice codec sizes or generated submissions were inspected before freeze. Package versions, archive/binary hashes and exact encoder flags are in [runtime.json](runtime.json). Upstream benchmark code and MIT license are retained under `upstream/` at the recorded commit.

## Frozen execution

Pending first submissions and independent bitstream verification. Updates below will preserve failures and the frozen protocol.

## Reference context

Buccino et al. (2023), [Compression strategies for large-scale electrophysiology data](https://doi.org/10.1088/1741-2552/acf5a4), studies full experimental/simulated Neuropixels compression. Our strict-lossless short chunk endpoint does not copy its lossy hybrid scores, full-stream compression ratios or runtime claims. Specialist codec families are motivated by that work; exact local settings and bytes determine our results.

## Execution and review

Three original high-effort/no-tool submissions retained; no repairs. 6 methods completed all 16 byte-exact roundtrips, retaining 96 compressed payloads. Independent decoding and size arithmetic passed. [All results](../../results/B07.json), [verification](verification.json), [recording CSV](recording-scores.csv), [release review](../../docs/release-v10.md). Original 0.9 central records remain unchanged.
