# H01 acquisition and preparation worklog

2026-10-30:

1. Read the original PhysioNet EEGMMI version 1.0.0 record, its access policy and ODC-By-1.0 attribution terms; checked original subject file listing and MOABB's PhysionetMI documentation.
2. Selected participants 1–5 for training and 6–8 for held-out evaluation, and runs 4/8/12 before any evaluated-model programs were requested. Selected the delayed 1–4 second task interval and pooled balanced accuracy before measuring the fixed baseline.
3. Downloaded 24 original EDF+ files to `data/cache/H01/raw/`. Original binary labels are obtained from their embedded annotations, not from pseudo-labels or another algorithm. Each source URL, byte size and SHA-256 is recorded.
4. Installed MNE 1.10.2 and its absent reader dependencies into the separate `work/eeg-deps` directory. The first preparation attempt failed because Matplotlib was missing from MNE's eager import path; numerical data were not changed. After repairing this preparation environment, the unchanged acquisition/split logic was rerun.
5. Implemented EDF reader checks for all files: 160 Hz, 64 identical channel labels, finite epochs, task duration >= 4 seconds, exactly 480 samples per epoch, both classes in each split, and no subject overlap. Prepared arrays, subject IDs, trial IDs and metadata are stored in the ignored cache.

No evaluated-model calls or submission scoring were performed by the data-admission subtask. Later release-level generation and evaluation records must state their actual outcomes separately.

6. Preparation completed with 225 training epochs and 135 held-out epochs. Fixed CSP+LDA pooled balanced accuracy was 0.5464426877470356. Per-participant scores and exact array shapes are in verification.json; this value is a local baseline check, not current SOTA. No hyperparameters were changed after scoring.

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: balanced_accuracy=0.648880105402; formatting compliant.
- gpt-6-sol: balanced_accuracy=0.71837944664; formatting compliant.
- gpt-6.1-sol: balanced_accuracy=0.697957839262; formatting compliant.

Reference: task-baseline; Local conventional task baseline; strongest specialist unverified. Current strongest specialist unverified. [Full result records](../../results/H01.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/H01/). No statistical significance claim.

Some submitted programs infer subject block lengths or adapt using unlabeled test inputs; inspect exact code. Subject-held-out labels remain hidden, but inner-validation/group information and adaptation differ between programs/reference. Do not call this a matched-procedure comparison.
