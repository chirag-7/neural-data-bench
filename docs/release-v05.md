# Research preview 0.5 — plan, execution and limits

The project asks whether general coding models can construct useful algorithms for neuroscience lab tasks, where they approach specialist tools, and whether newer model versions improve under fixed task contracts. This release implements an auditable feasibility panel and evidence map. It is not yet a definitive neuroscience-wide comparison or a finished paper.

## Study design

1. Map neuroscience by **data modality × scientific operation × generalization split × ground-truth source × lab use**. Fourteen families are navigational units, not a claim that disciplines partition cleanly. [Taxonomy](taxonomy.md).
2. Search primary task papers, benchmark sites, author repositories and data-release records; record inherited versus newly verified evidence. Distinguish a named benchmark from a custom derived slice. [Review protocol](review-protocol.md), [prior work](prior-work.md), [sources](../literature/sources.json).
3. Admit only a bounded endpoint with usable rights/access, input–target pairing, sufficient independent units, computable metric and tractable protocol. Preserve candidate/deferred/archived distinctions. Never drop a task because a model performs poorly.
4. Freeze input hashes, adapter, explicit prompt, allowed packages, code interface and scoring before new generation. One generation for each exact model, high reasoning effort, no observed model tool calls, no execution feedback. Keep all failures. Programs fit under 180 seconds and one numerical thread; requested memory budgets are not enforced.
5. Add exact-slice specialist reproductions or archived predictions where supportable. Label historical test selection, unmatched training/input access, post-hoc selection and conventional baselines. Unknown global best stays unknown.
6. Retain all model/reference records centrally; use native metrics, task/family-balanced directional summaries, failure denominators and strict-format sensitivities. Avoid a single mixed-metric score.

## Release changes

Four new task IDs: B01 stationary simulated spike sorting, G01 offline cross-day monkey BCI, H08 sleep staging, J08 2D microscopy instance segmentation. New E01 Area2_Bump/DMFC_RSG slices reuse unchanged programs. New references include MountainSort5, EEG-only YASA, pyRiemann SVM variants and author StarDist masks. See [findings](../analysis/findings.md) and [executed panel](execution-panel.md).

Active map: 96 entries, 18 measured, 49 pending validation, 29 deferred. The earlier 114-entry map is preserved; 18 candidates are archived for concrete admission/definition issues. License uncertainty is not solved by inferring that a related paper's open license covers its dataset. Registration/DUA requirements are not bypassed. [Exclusions](../registry/excluded-candidates.json), [pruning review](../literature/active-pruning-v05.md).

54 generated programs produce 72 model–slice attempts; 70 valid, 2 failed. 147 records retain references and unusable historical artifacts; 141 prediction records pass rescoring. Three exact requested models only. The site opens on measured benchmarks and provides category navigation, graph/table controls, native scores, specialist overlays in both plot types, sources and downloadable central data.

## What is sufficient and what is not

This is sufficient to demonstrate a working research pipeline, identify practical counterexamples, and test the feasibility of selected task contracts. It does not justify exhaustive coverage, global SOTA, a universal model ranking or matched-total-effort superiority. Fourteen represented categories do not eliminate unmeasured subfields. The review is bounded, not the entire literature, and no independent domain-expert audit is complete. Dataset/pretraining overlap remains possible.

For a paper, choose an explicit target population of tasks; freeze a prospective sampling/admission policy; add multiple independent datasets and generations; compare strong specialists with matched tuning/data access; report compute and costs under common accounting; include open-weight and native modality tracks if claimed; conduct leakage review; and solicit neuroscience expert coverage review. The current 78 unrun active entries are a screened backlog, not results and not a promise that each can pass execution gates.

## Prior work and contribution

[Prior-work review](prior-work.md) covers broad neural foundation-model and agent benchmarks, domain-specific challenges and scientific workflow evaluation. Closest resources include BrainWideBench, NeuralBench, NeuroDiscoveryBench/NeuroClaw, SciVid and EEGAgentBench. Novelty cannot be claimed merely from crossing modalities. A defensible prospective contribution would be reproducible task admission, frozen general-code protocols, exact-slice specialist evidence and failure-aware comparisons across lab operations; establish this against prior work before submission.

## Audit entry points

- Overall results: [findings](../analysis/findings.md), [summary JSON](../analysis/summary.json), [central CSV](../results/measurements.csv).
- Per-area work: [benchmarks](../benchmarks), [experiments](../experiments), [admissions](../registry/admission-decisions.json).
- Source evidence: [literature](../literature), [data manifests](../data/manifests), [current-best ledger](../registry/current-best.json).
- Verification: [reproduce](reproduce.md), [validation](../analysis/validation-expansion.json), [portable repository checks](../scripts/check_repository.py).

All documents and scores are exploratory. Revisions to reference classes, pruning and macro weighting made after some scores were known are disclosed; no retroactive preregistration claim.

## Publication verification

The [deployment receipt](../analysis/deployment-v05.json) records the exact owner-private Sites version, canonical research/source commits and GitHub integrity run. [Real-browser QA](../analysis/browser-qa-v05.json) covers representative desktop/mobile interactions; [source checks](../analysis/site-source-checks.json) cover all rendered routes and 18 plot pairs. [Screenshot of both plot types and the named specialist](assets/explorer-v05.jpg). The earlier local-preview block was resolved by using the normally authenticated published URL; no URL-policy bypass was used.
