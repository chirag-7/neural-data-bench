# Preview 0.10: real-voltage lossless compression

**B07 is fully executed on all 16 original AIND/IBL experimental recordings**, one fixed 4096 sample chunk and all 384 channels per recording. This adds a practical lab-storage task to the existing research panel. Sixteen recordings represent 14 source animal identifiers; no biological confidence interval is claimed.

## Frozen procedure

[Protocol](../experiments/B07/protocol.md), [source manifest](../data/manifests/B07.json), prompt, adapter, scorer, codec references and runner were frozen in commit `1ab99b1` before model generation and any real-slice method score. Each chunk has 3,145,728 bytes; 50,331,648 input bytes total. HTTP 206, exact Content-Range, ETag guards and acquired SHA256s pin the selected ranges. ETags are not full-file checksums. Original metadata and clocks are retained; no resampling or signal processing discards bytes.

All three requested Sol versions generate one high-effort, no-tool program under the same explicit prompt, general Python/scientific libraries plus standard compression modules, below 240 lines and 180 seconds for all 16 encode/decode calls. No repairs or score feedback. Decoder namespaces start fresh and every emitted blob byte counts. Model code, original generation events, usage and hashes are retained. Provider checkpoint identity and identical hidden context remain unverified.

WavPack 5.8.0 lossless very-high mode and temporal-delta/channel-major Blosc/Zstd 9 bitshuffle are fixed before outcomes; raw zlib 9 is the conventional baseline. These codecs are adopted for neural-data storage; WavPack is an audio codec and Blosc/Zstd is general-purpose compression with a fixed signal transform, not a trained neuroscience model. WavPack remains the primary scientific comparator even if another inspected codec has a better point result. These are local codec family reproductions, not current global best, matched implementation effort or the original paper's full-stream benchmark. No published lossy hybrid score is inserted into these strict-lossless charts.

## Results

| Method | Encoded bits/sample ↓ | Raw/encoded ratio ↑ | Encode + decode seconds |
|---|---:|---:|---:|
| gpt-5.6-sol | 7.019830 | 2.279 | 15.458 |
| gpt-6-sol | 6.901698 | 2.318 | 9.023 |
| gpt-6.1-sol | 7.214589 | 2.218 | 9.619 |
| WavPack 5.8.0 lossless very-high | 7.690052 | 2.081 | 4.614 |
| Delta + Blosc/Zstd9 bitshuffle | 7.683237 | 2.082 | 2.060 |
| Raw zlib9 | 11.412251 | 1.402 | 2.183 |


All three generated programs compress fewer bytes than both frozen codec references on this exact slice. GPT-6 has the smallest point size; GPT-6.1 is larger than both earlier versions. Header/chunk overhead and signal-adaptive predictors can affect this ordering. These results support no current-global-best or stable model-version trend. 

Primary is equal-recording mean encoded bits per scalar int16 sample, lower better; raw storage is 16 bits/sample. All successful methods must reconstruct every byte. Execution seconds sum all 16 codec calls and include WavPack process startup; they are single-run local measurements, not a controlled streaming-throughput study. See [all per-recording scores](../experiments/B07/recording-scores.csv) and [method records](../results/B07.json).

## Independent audit and interpretation

The [audit](../experiments/B07/verification.json) verifies original chunk/metadata/frozen hashes, every successful saved payload, exact reconstruction with a fresh decoder namespace, every raw-byte hash and primary size arithmetic. It never reruns an encoder or calls a model. 96 compressed payloads and 6 output manifests are retained. These additional binary payloads are not separate model attempts, tasks or independent cohorts.

Only roughly 0.137 seconds per recording are evaluated. Long recordings, changing noise/drift, chunk-size sensitivity, disk/cloud I/O, full container deployment, neural compression latents and lossy spike-preservation are outside this contract. A successful codec does not establish neural understanding. General programs and specialist libraries have unequal implementation histories. One generation and this fixed source collection support descriptive results only.

The previous release's central records are preserved exactly in [v09-measurements.jsonl](../results/archive/v09-measurements.jsonl); the H02 follow-up remains separate. Current totals: **23 tasks across 14 families, 87 first-submission attempts (85 valid, 2 failures), 173 model/reference records**. The active map remains 96 candidates; 45 pending and 28 deferred means 73 still unrun. The 212-URL inventory is not a count of fully reviewed papers or proof of exhaustive coverage.

## Sources and reproduction

- Buccino et al. (2023), [Compression strategies for large-scale electrophysiology data](https://doi.org/10.1088/1741-2552/acf5a4): original compression study and motivation for codec references.
- [Original source inventory/data documentation](https://allenneuraldynamics.github.io/data.html), [pinned author benchmark code](https://github.com/AllenNeuralDynamics/ephys-compression/tree/c89e8e481435f39e3bf041bfc0eaac5ef6d93900) and [original CC BY4 open-data registry](https://github.com/awslabs/open-data-registry/blob/main/datasets/allen-nd-ephys-compression.yaml).
- [WavPack vendor](https://www.wavpack.com/) and [numcodecs Blosc documentation](https://numcodecs.readthedocs.io/en/stable/compression/blosc.html).
- [Reproduction steps](reproduce.md), [worklog](../experiments/B07/worklog.md), [runtime/archive/binary hashes](../experiments/B07/runtime.json), [acquisition](../scripts/acquire_compression.py), [independent verifier](../scripts/verify_compression.py).

Both website plots name the specialists and their values directly. WavPack and delta–Blosc/Zstd are dashed lines; raw zlib is dotted. All three reference bars remain visible by default. The default observed-data macro view now includes this infrastructure endpoint; synthetic-inclusive views retain prior exclusions/policies. Neither native scores nor incompatible metric deltas are pooled across tasks.
