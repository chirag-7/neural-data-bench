# Progress assessment

The repository is an auditable pilot, **not yet a paper-ready general-versus-specialist comparison**. Breadth of represented categories should not be mistaken for depth of evidence.

## What is established

- 23 measured task IDs span 14 families, with 87 first-submission model–slice attempts from the three requested Sol versions. Of these, 85 return valid predictions and two fail; strict prompt compliance is a separate criterion.
- Data manifests, frozen prompts, generated programs, predictions, metrics and source links let a reader trace each result. The 0.6 release independently rescored 146 stored prediction files.
- Named reference methods appear in both line and bar plots, with numeric reference cards and direct labels. A reference's status distinguishes local fitting, historical archived output and task baselines.
- The B01 all-output spike event audit exposes a meaningful metric limitation: unmatched clusters can change the interpretation. The original endpoint is preserved and the new result is explicitly post-hoc.

## What remains weak

- Original results have one code generation per model/task. Variability, provider changes and prompt sensitivity are unmeasured across most tasks.
- Many endpoints use one dataset,  a small number of people/animals or artificial corruption. Reused source slices are not independent replications.
- Specialist comparisons have uneven search effort, inputs and training regimes. Strongest available method is not established for every task; a simple baseline cannot certify general-model superiority.
- The current track measures generated analysis code fitted locally, rather than native multimodal or world-model ability. Open-weight models have not been evaluated.
- A 212-URL registry is a source inventory, not a count of fully reviewed papers. Coverage is an explicit working taxonomy, not proof of an exhaustive literature search. 73 active candidates remain unrun and exclusions remain auditable.
- Cross-task model-version trends are descriptive on a convenience sample with correlated tasks and differing metrics. They do not establish universal neuroscience capability or a time trend in general intelligence.

## Next evidence priorities

H02 now has three code generations per model and an additional training-only CV-selected xDAWN reference; all six new submissions pass strict execution/format rules. This addresses generation variability on one dataset only. The remaining 22 tasks still have one original program per model. [Detailed results](../experiments/H02/replication-v1/results.md).

Extend repeated-generation variability and stronger train-only reference selection to other existing tasks. Then prioritize independent datasets/participants for promising endpoints, matched specialist effort and a predeclared suite with enough tasks per family. Broader model modalities should be a distinct track with its own input and resource rules. New categories alone will not repair these weaknesses.

The H02 [completed follow-up plan](../experiments/H02/replication-v1/amendment.md) addresses the first priority on one dataset. It is retrospective and cannot make the whole suite paper-ready.

Preview 0.8 adds two real-data tasks rather than new categories: curated molecular layer transfer and conditional mouse-choice forecasting. This reduces two specific gaps, while one test donor for K04 and a source-inspired GLM reference for M01 limit the conclusions. [Evidence and exact scope](release-v08.md).

Preview 0.9 adds posterior sampling on ten original GLM simulations and separates observed-data versus synthetic-inclusive aggregate views. All three models return valid samplers, but this favorable known-likelihood synthetic model and a CPU-sized classifier diagnostic do not establish arbitrary posterior calibration or biological inference. Original and local reference MCMC are related, and near-chance classifier differences are not stable model ranks. [Detailed scope](release-v09.md).

Preview 0.10 adds real-voltage lossless compression on sixteen fixed short chunks. Every successful bitstream is independently decoded and compared byte-for-byte. This covers one practical storage endpoint; it does not repair the gaps in long-recording throughput, drift-aware sorting, broad modalities or repeated-generation uncertainty. [Exact scope](release-v10.md).
