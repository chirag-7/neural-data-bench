# Three complementary task facets (v1)

The existing 14 scientific categories stay unchanged. Three additional facets answer **what data enters the procedure, what it computes, and where it must generalize**. They are author-assigned, literature-informed annotations of this catalog, not an adopted international ontology or evidence that neuroscience coverage is complete.

[All 92 assignments (CSV)](assignments.csv) · [Versioned registry and definitions](../../registry/task-facets-v1.json) · [Website copy](../../website/data/task-facets.json)

## Why these three

| Facet | Question | Why it adds information beyond category |
| --- | --- | --- |
| Input data type | What does the evaluated procedure actually receive? | Distinguishes raw movies from extracted coordinates or numerical features. This is essential when interpreting general-model ability. |
| Analysis task | What operation must it perform? | The same operation recurs across lab domains: segmentation in microscopy and MRI, reconstruction in calcium and EEG, decoding in behavior and BCI. |
| Generalization setting | What changes between fitting and evaluation? | A result on new frames, a new animal, a new day and another acquisition site support different practical claims. This is more useful for choosing a lab tool than another biological label. |

The third facet was chosen over output data type because outputs often repeat the operation (segmentation → masks, classification → labels). Output remains in protocols and metrics. Lab type is many-to-many, changes with scientific practice and largely overlaps the existing categories; arbitrary lab labels would suggest unsupported divisions. Workflow stage is useful but overlaps operation. Species, scale, modality details, supervision, budgets, acquisition conditions and uncertainty remain important protocol metadata, not four more navigation controls. No single three-facet representation can substitute for them.

The vocabulary deliberately combines molecular expression and other numerical feature tables; their original categories preserve the biological difference. Audio remains separate from physiological signals because it is a recognizable acquisition channel and supports future audio/neural combinations. All physiological traces are pooled at this coarse level: EEG + EMG does not create a new combination merely because two electrical channels differ. Input representation and original acquisition modality are different concepts.

## Literature basis and limits

This is a targeted primary-source synthesis, not a systematic review claiming to exhaust the literature. Sources informed the design; none validates this exact three-facet vocabulary.

1. [Paninski & Cunningham, 2018, *Neural data science: accelerating the experiment-analysis-theory cycle in large-scale neuroscience*](https://pubmed.ncbi.nlm.nih.gov/29738986/) motivates organizing analysis in relation to scientific workflows and experiments, rather than by model architecture alone.
2. [Kriegeskorte & Douglas, 2019, *Interpreting encoding and decoding models*](https://arxiv.org/abs/1812.00278) explicitly ties interpretation to the achieved level of generalization. Encoding and decoding also illustrate that the same numerical machinery can address different scientific directions. This is the main justification for choosing transfer setting as the third facet.
3. [Rübel et al., 2022, *The Neurodata Without Borders ecosystem for neurophysiological data science*](https://pubmed.ncbi.nlm.nih.gov/36193886/) supports separating data representations and scientific metadata. NWB is a data standard; the labels here do not claim to be its ontology.
4. [BIDS derivatives documentation](https://bids.neuroimaging.io/getting_started/folders_and_files/derivatives.html) distinguishes acquired data and derived representations. Our MRIQC example makes that distinction explicit: numerical quality features are not an MRI-vision test.
5. [FALCON](https://snel-repo.github.io/falcon/) makes new-day decoding and calibration central to BCI evaluation. It illustrates why a task name alone does not specify a useful transfer claim; our reduced G01 split is annotated from its local protocol, not equated with the official FALCON protocol.
6. [Liang et al., 2023, *Holistic Evaluation of Language Models*](https://arxiv.org/abs/2211.09110) separates evaluation scenarios and metrics, reports coverage gaps and makes evidence auditable. We follow that separation without claiming that grouping tasks makes their native metrics interchangeable.

Reviewed 2026-11-01. Exact vocabulary definitions are in the versioned registry. Source URLs for each task are retained with its local annotation.

## Annotation unit and decision rules

One record is one **active catalog task**, not an entire published dataset. There are 92 records: 30 **executed** contracts and 62 **proposed** contracts (33 pending validation, 29 deferred). Historical archived proposals are excluded. Proposed inputs/operations are planning decisions, not evidence of accessible data or a completed evaluation. Unfixed transfer boundaries stay **Not yet specified**.

For executed tasks, inspect the frozen local input contract, target, scorer and split, rather than copying the resource's broad description or recommended future split. Each record has a protocol/admission path and SHA-256, a plain-language rationale, original source URLs and review date. Each task also has its own annotation file here (for example [A09](A09.md), [F04](F04.md), [I10](I10.md), [N05](N05.md)). This layer leaves sealed protocols, predictions, scores and previous analyses unchanged.

### Input and multimodal combinations

- Assign the representation actually consumed by the generated program. The current models generate code; the code processes these inputs locally. This does not claim direct native image/audio ingestion by an LLM.
- Multimodal means two or more **coarse input types jointly used**, not simply that the dataset contains many kinds of files.
- Supervision-only targets, annotation masks, timestamps, geometry/calibration, fixed design matrices, priors, donor IDs and instructions do not alone create another modality. Input covariates that carry a jointly modeled predictive stream do count.
- Multiple cameras or MRI contrasts are images/video, not new coarse types. Multiple physiological sensors remain physiological signals. A finer acquisition-modality ontology could be added later without multiplying the main filter now.
- The nested selector uses an exact, order-independent set of coarse components: audio + images differs from audio + physiological signals. New combinations can be added without adding main dropdown categories. Current active proposals include images + motion, images + tables, images + signals, and spike events + tables.
- **No current measured contract is jointly multimodal under this definition.** F04 has images → neural targets; G01 has spikes → movement targets; H16 receives one contaminated channel. These are cross-domain prediction/reconstruction tasks, not joint-input multimodal evaluations. The interface makes this coverage gap visible instead of assigning misleading labels.

### Operation and output

One primary operation follows the scored objective, not the architecture used. Classification/decoding includes sequence-symbol outputs and choice probabilities; continuous prediction includes neural encoding and forecasting. Signal/latent recovery includes denoising, imputation, demixing and spike-source recovery. Compression and file workflows get separate labels because fidelity/schema checks have a different objective from supervised prediction. A future task with independently scored objectives should be split into contracts instead of silently attaching conflicting labels.

### Transfer setting

Generalization is a set, not a ranked difficulty ladder. New subjects and sites may co-occur; neither automatically implies the other. New observations are not automatically new conditions. New simulated cases do not establish biological generalization. **No trained-transfer test** covers unsupervised per-recording sorting, direct posterior computation, codec round trips and schema extraction; it does not imply these tasks have no scientific value.

E06 contains both within-condition forecasting and an unseen-condition slice. Either transfer filter selects the **whole original task**, retaining both slices and their original aggregation. This is task-level navigation, not a new slice-specific performance analysis. An explicit note on analysis pages states this limitation.

## Using filters without manufacturing findings

Filters intersect across the three facets; the existing category filter also intersects. Any listed transfer label can match. Each task counts once even with multiple transfer tags. Benchmark search/result-availability controls continue to apply. Empty combinations show zero tasks, not zero performance. Multimodal has no measured scores because no executed contract qualifies.

Current analysis pages recompute descriptive endpoint counts, trajectories and lag tables from the selected task rows, preserving better-score direction and existing task means. Lag normalizations retain each task's original four-model IQR. Filtered comparisons do not recompute historical inferential tests, select slices, re-fit models, or prove a causal explanation. Downloads of original result payloads remain full-panel and are labeled accordingly. Frozen historical reports remain full-panel snapshots.

These post-hoc subsets can be tiny, dependent and confounded by representation, supervision, dataset, operation and transfer. Do not treat a filtered fraction as an estimated success probability for that input type, evidence of a scaling law or a recommendation to replace specialists. Inspect native scores and matched specialist evidence. Further work requires preregistered strata, independent datasets/subjects, repeated generations and matched budgets.

## Maintenance and validation

Update this overlay when a contract changes; proposed tags must be re-reviewed at admission. New vocabularies require a new version, a migration rationale and stable prior artifacts. Do not change labels because a model wins or loses. Another annotator should independently review assignments before publication as a validated taxonomy; inter-rater agreement has **not** been measured.

Run `python3 scripts/check_task_facets.py` and `node scripts/check_site.mjs`. Checks require exact active-ID coverage, valid labels, sorted multimodal components, source hashes, executed/proposed status, byte-identical website data, key target/input counterexamples, intersecting filters, empty subsets and direction-correct descriptive aggregation. Automated checks cannot replace expert semantic review.
