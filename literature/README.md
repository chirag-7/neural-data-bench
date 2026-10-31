# Literature and admission evidence

The source registry records associations, not an assertion that every paper was fully read or every dataset downloaded. The historical 114-entry task-resource map now has 96 active and 18 archived entries, with 190 associated source URLs; counts include protocols, repositories and data records. This is a bounded evidence map with variable review depth, not an exhaustive systematic review.

- [Original search log](search-log.json), [review protocol](../docs/review-protocol.md), [source registry](sources.json), [original extension audit](extension-audit.md).
- [Behavior/anatomy/population review](v04-behavior-population-review.md), [entry decisions](admission-v04-behavior-population.json), [actual search/source actions](searches-v04-behavior-population.jsonl).
- [Electrical/neuroimaging review](v04-electrical-review.md), [entry decisions](admission-v04-electrical.json), [actual search/source actions](searches-v04-electrical.jsonl).
- [Cell/retina/workflow review](v04-cell-workflow-review.md), [entry decisions](admission-v04-cell-workflow.json), [actual queries](searches-v04-cell-workflow.jsonl).
- [Inference/control/MRIQC decisions](admission-v04-inference-control.json), [actual queries](searches-v04-inference-control.jsonl). Nature article redirects and an incorrect Psych-101GitHub candidate URL were access failures, not evidence that the underlying resource is unavailable. Primary simulator/repository sources were checked where available.

The normalized [central admission ledger](../registry/admission-decisions.json) has exactly one current decision for each mapped ID. Component reviews can overlap—for exampleF04 has a retinal licensing audit and broader sensory-encoding mapping. Source-only inherited URLs, direct page inspection, attempted access and acquired/hashed files are explicitly distinguished. No unperformed broad search or download failure is invented. Search records are not a PRISMA flow diagram; independent human domain review and full backward/forward citation screening remain outstanding.

## Preview 0.5 source work

- [Extracellular sorting review](v05-extracellular-review.md), [admission evidence](admission-v05-extracellular.json), [queries and source actions](searches-v05-extracellular.jsonl).
- [BCI and EEG review](v05-bci-review.md), [BCI admission](admission-v05-bci.json), [search/source log](searches-v05-bci.jsonl), [P300 evidence](source-verification-v05-p300.json), [SSVEP rights limitation](source-verification-v05-ssvep.json).
- [Active-map pruning](active-pruning-v05.md), [entry-level decisions](active-pruning-v05.json). These decisions do not claim the scientific operations are impossible.
- Actual [SynAPSeg source record](../experiments/J08/source-record.json) and verification, [Sleep-EDF protocol and license](../experiments/H08/protocol.md), [E01 source-transfer preparation](../experiments/E01/slices/).

The new admissions resolve specific data/access/scorer questions, not every literature or current-SOTA question in a category. The stronger H01 specialist amendment is post-hoc and does not retroactively change the original experimental design.

## Preview 0.6 focused review

The review targets ambiguously labeled plots, stale current-status documents, metric sensitivity and one concrete ERP admission. It does not repeat or relabel earlier searches as exhaustive. [Review/release](../docs/release-v06.md), [bounded source log](searches-v06.jsonl), [H02 original source/license](../experiments/H02/source-record.json), [B01 post-hoc audit](../experiments/B01/secondary-amendment.md). H02's original source is separately licensed from the previously deferred BNCI proposal; all 25 original files were acquired and verified.
