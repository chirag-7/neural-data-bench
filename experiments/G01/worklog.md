# G01 data/admission worklog

2026-10-30:

1. Screened existing G01–G03 and original FALCON documentation, loaders, linear-decoder/filter reference and DANDI M1/M2/H1 asset metadata. Same-session NLB behavior decoding was considered but does not establish G01 cross-day robustness and was not relabeled as such.
2. Screened H1: public files are small, but original dataset description contains additional human-data nonredistribution terms despite CC-BY metadata. A single small source file was inspected in scratch; H1 was not selected for this release. No H1 participant arrays or predictions are tracked or used by G01.
3. Screened M2 minival: one original run contains only two trials; all seven files would yield 14 trials. This was rejected as too small for a useful new decoding slice. No minival file is included in the admitted arrays.
4. Identified that the much larger M2 calibration NWBs contain mostly unused fullband voltage. Verified anonymous HTTP byte-range access to a pinned1.88 GB file; its useful content includes248 trials and small spike/kinematic arrays. Selected all seven held-in-calibration files and froze a chronological Oct 19/20 training versusOct 27/28 evaluation split before any evaluated-model generation.
5. Pinned original asset UUID/blob identity, provider digests and FALCON source commit. Prepared local-only component extraction with per-buffer and per-NPZ SHA-256, explicitly distinguishing reported source full-file checksums from independently verified extracted content. No full-file checksum claim is made.
6. Checked96 unit identifiers, source velocity units/order, monotonic timestamps, trial membership, finite values, day/trial separation, masks and sufficient trials. Prepared70,989 training bins/1,169 trials and44,633 test bins/754 trials.
7. Compared count binning and causal filtering against pinned official FALCON functions on every original extraction: maximum float32 error below 1.7e-7. An initial AST-only reference-parity test wrapper failed because generated AST nodes lacked line locations; the wrapper was repaired, with no preparation algorithm or source-data changes.
8. Ran the frozen train-only standardized20 alpha ridge reference once: pooled variance-weighted R²=-0.22748267650604248; Oct 27=0.04468146339058876, Oct 28=-0.5470848679542542. No preprocessing, split or parameter was adjusted after observing these values. They illustrate this reference's transfer limitations, not a data-quality exclusion or current SOTA.

No evaluated-model calls were made by the acquisition/admission subtask. Release-level prompts, submissions and scores must be recorded separately.
