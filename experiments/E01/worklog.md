# Worklog

2026-10-30: Inspected official NLB dataset list and README; confirmed test groundtruth public since January 2026. Pinned nlb_tools 42f 8410b 88e 12 db 136910 fa 2f 888b 025 ea 0 aa 2 ae. Acquired its 101MB LFS evaluation file and published DANDI000140 version 0.220113.0408 train 29MB/test 689KB NWBs. Saved published metadata and CC BY4.0 terms. Verified all five vendored official Python files against pinned Git blob hashes; retained MIT license.

Preparation uses official readers/tensor makers,20 ms bins and movement alignment. Current PyNWB3.1.3 tried to write macOS home-cache path unavailable in sandbox; used compatible 2.8.3/HDMF3.14.6 in clean isolated dependency folder instead. Initial overlapping pip target upgrade left incomplete HDMF files; clean nested install resolved it. These were environment repairs, not changes to neural arrays or official source. Only NumPy/SciPy/sklearn needed for generated-model inference after acquisition.

Inspected trial IDs and found official default make_trial_data yields 74 of 75 training and 25 of 25 validation trials: final trial 199 has no valid aligned timepoints in imported continuous data. Retained exclusion explicitly; combined 99 training trials. Official test inputs 100 trials and public held-out targets 100 trials; dimensions 107 heldin/35 heldout/35 timebins. No generated-model runs or performance-guided changes during adapter preparation.

Independent validation: all 100×35×107 testinput counts exactly equal a second extraction directly from raw HDF5 spike timestamps, using 1 ms truncation and 20 ms bins. The primary scorer exactly matches officialNLB bits_per_spike on two deterministic prediction arrays; negative predictions fail. Pinned LFS objectSHA256 matches downloaded 101MB groundtruth. An attempted comparison to forecast targets was discarded because forecast spikes are intentionally withheld from the compressed testNWB timeline; this incorrect validation attempt did not alter any input/target arrays. Validation.json records checks.

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: bits_per_spike=0.237661980547; formatting compliant.
- gpt-6-sol: bits_per_spike=0.158604292724; formatting compliant.
- gpt-6.1-sol: bits_per_spike=0.242155255503; formatting compliant.

Reference: task-baseline; Local conventional task baseline; strongest specialist unverified. Current strongest specialist unverified. [Full result records](../../results/E01.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/E01/). No statistical significance claim.
