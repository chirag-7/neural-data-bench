# Extracellular benchmark admission evidence, v0.5

Reviewed 2026-10-30. The [canonical admission/provenance JSON](admission-v05-extracellular.json) records candidate decisions, actual access, data terms, source revision, hashes and the specialist-only reproduction. The [query log](searches-v05-extracellular.jsonl) preserves four exact searches. This was a bounded attempt to admit one CPU-sized ground-truth sorting case, not a full spike-sorting literature review.

## Admitted B01 slice

The [official SpikeInterface comparison example](https://spikeinterface.readthedocs.io/en/0.96.1/modules/comparison/plot_3_compare_sorter_with_ground_truth.html) names a ten-second MEArec simulation. Its [primary NeuralEnsemble source repository](https://gin.g-node.org/NeuralEnsemble/ephy_testing_data) supplied a credentialless 62,317,832-byte HDF5 download. The [pinned repository README](https://gin.g-node.org/NeuralEnsemble/ephy_testing_data/raw/71e5c5b04e34ab9e69533a4fb092a6ce4d244034/README.md) declares ODbL 1.0 database terms and links CC BY-SA 4.0 for individual contents. These data terms are preserved separately from code licensing.

The fixture contains 32 channels at 32 kHz, source-filtered 300–6000 Hz voltage in microvolts, electrode positions and exhaustive simulated spike truth. It is **not real paired intracellular/extracellular data** and has no drift. Generation version/seeds, timestamp checks and source hash are recorded in the [manifest](../data/manifests/B01.json). The [protocol](../experiments/B01/protocol.md) fixes an unsupervised whole-recording interface: programs receive voltage, sampling frequency and geometry, infer units from voltage, and return sample-index/cluster-ID events. Source truth, true unit count, templates and per-unit clean traces are withheld in separate inaccessible artifacts.

The single specialist configuration was frozen before scoring: MountainSort5 0.5.9 scheme 1 with SpikeInterface 0.105.4 whitening. The official scorer uses Hungarian matching, exhaustive truth and requested 0.4 ms event tolerance; the pinned implementation floors this to 12 samples, or 0.375 ms. Identity/empty cases verify scorer behavior, with the identity oracle explicitly excluded as a method result.

The reference's mean ground-truth-unit accuracy was 0.940896, with one redundant output unit. This is a local reproduced specialist, not verified current SOTA. Mean ground-truth-unit accuracy can hide unmatched extra output clusters, so unit/event counts, redundancy, false-positive/overmerged categories and per-unit scores must accompany it. The initial geometry-setter failure and distance-preserving repair occurred before any predictions; both are preserved in the audit trail. No general models were called by this admission worker.

## Alternatives and concrete remaining blockers

The [current SpikeForest repository](https://github.com/flatironinstitute/spikeforest) documents a subset release through kachery-cloud with client association to a Google user. Older SHA-1 pointer examples were located, but this screen did not establish current credentialless paired-file acquisition. That is an unresolved access path, not evidence that paired data do not exist. Underlying paired sources also retain separate rights.

The [author's Yger paired-retina page](https://www.yger.net/software/ground-truth-recordings/) describes simultaneous loose-patch and dense extracellular recordings. Specific smallest-file size, offsets, paired truth extraction and download terms were not validated here. It remains a promising real-data follow-up.

[SpikeInterface's earlier tutorial release](https://zenodo.org/records/4657314) documents a larger simulated tetrode file; the smaller standard fixture was selected instead. Its [real training collection](https://zenodo.org/records/20726062) includes multi-gigabyte recordings, but no independently matched spike-truth package was established from the release description. Neither alternative was rejected as bad data or universally infeasible.

This slice contributes a real **sorting operation** with synthetic ground truth. It does not establish drift robustness, paired-real validity, independent recording transfer or biological population uncertainty. Those remain explicit gaps after active-list pruning.
