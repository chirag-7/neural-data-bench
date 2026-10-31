# Progress assessment

The repository is an auditable pilot, **not yet a paper-ready general-versus-specialist comparison**. Breadth of represented categories should not be mistaken for depth of evidence.

## What is established

- 19 measured task IDs span 14 families, with 75 original model–slice attempts from the three requested Sol versions. Of these, 73 return valid predictions and two fail; strict prompt compliance is a separate criterion.
- Data manifests, frozen prompts, generated programs, predictions, metrics and source links let a reader trace each result. The 0.6 release independently rescored 146 stored prediction files.
- Named reference methods appear in both line and bar plots, with numeric reference cards and direct labels. A reference's status distinguishes local fitting, historical archived output and task baselines.
- The B01 all-output spike event audit exposes a meaningful metric limitation: unmatched clusters can change the interpretation. The original endpoint is preserved and the new result is explicitly post-hoc.

## What remains weak

- Original results have one code generation per model/task. Variability, provider changes and prompt sensitivity are unmeasured across most tasks.
- Many endpoints use one dataset, a small number of people/animals or artificial corruption. Reused source slices are not independent replications.
- Specialist comparisons have uneven search effort, inputs and training regimes. Strongest available method is not established for every task; a simple baseline cannot certify general-model superiority.
- The current track measures generated analysis code fitted locally, rather than native multimodal or world-model ability. Open-weight models have not been evaluated.
- A 194-URL registry is a source inventory, not 194 fully reviewed papers. Coverage is an explicit working taxonomy, not proof of an exhaustive literature search. 77 active candidates remain unrun and exclusions remain auditable.
- Cross-task model-version trends are descriptive on a convenience sample with correlated tasks and differing metrics. They do not establish universal neuroscience capability or a time trend in general intelligence.

## Next evidence priorities

First measure repeated-generation variability and stronger train-only reference selection on an existing task. Then prioritize independent datasets/participants for promising endpoints, matched specialist effort and a predeclared suite with enough tasks per family. Broader model modalities should be a distinct track with its own input and resource rules. New categories alone will not repair these weaknesses.

The H02 [follow-up plan](../experiments/H02/replication-v1/amendment.md) addresses the first priority on one dataset. It is retrospective and cannot make the whole suite paper-ready.
