# Literature and admission evidence

The source registry records associations, not an assertion that every paper was fully read or every dataset downloaded. The 114 task-resource map has 180 sourceURLs; counts include protocols, repositories and data records. This is a bounded evidence map with variable review depth, not an exhaustive systematic review.

- [Original search log](search-log.json), [review protocol](../docs/review-protocol.md), [source registry](sources.json), [original extension audit](extension-audit.md).
- [Behavior/anatomy/population review](v04-behavior-population-review.md), [entry decisions](admission-v04-behavior-population.json), [actual search/source actions](searches-v04-behavior-population.jsonl).
- [Electrical/neuroimaging review](v04-electrical-review.md), [entry decisions](admission-v04-electrical.json), [actual search/source actions](searches-v04-electrical.jsonl).
- [Cell/retina/workflow review](v04-cell-workflow-review.md), [entry decisions](admission-v04-cell-workflow.json), [actual queries](searches-v04-cell-workflow.jsonl).
- [Inference/control/MRIQC decisions](admission-v04-inference-control.json), [actual queries](searches-v04-inference-control.jsonl). Nature article redirects and an incorrect Psych-101GitHub candidate URL were access failures, not evidence that the underlying resource is unavailable. Primary simulator/repository sources were checked where available.

The normalized [central admission ledger](../registry/admission-decisions.json) has exactly one current decision for each mapped ID. Component reviews can overlap—for exampleF04 has a retinal licensing audit and broader sensory-encoding mapping. Source-only inherited URLs, direct page inspection, attempted access and acquired/hashed files are explicitly distinguished. No unperformed broad search or download failure is invented. Search records are not a PRISMA flow diagram; independent human domain review and full backward/forward citation screening remain outstanding.
