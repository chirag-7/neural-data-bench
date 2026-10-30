> Historical planning snapshot. The current executed panel, results and remaining gaps are in [release 0.5](release-v05.md). Figures and plans below describe an earlier stage.

# Feasibility assessment and first measured pilot

30 October 2026 · research preview v 0.2

## What is feasible

A category browser, versioned task cards, data-acquisition scripts, exact scoring protocols and model comparisons are feasible. A rigorous representative suite can be assembled incrementally. Measuring every model on every catalog entry requires a sustained project: many raw-signal, 3D, imaging, control and mechanistic tasks have different input interfaces, training costs and ground-truth limitations.

The original 90-entry map was not a completed systematic review. A separate AI-assisted bounded audit identified important operational gaps. Version 0.2 adds 12 entries, bringing the evidence map to 102 pairings in 14 families. These are not 102 unique or execution-ready benchmarks. The audit and catalog preserve statuses and known omissions.

## Coverage corrections

Added: intervention-response prediction; HippoUnit physiological model validation; cognitive model/parameter recovery; BADS model fitting; MyoChallenge and FlyGym embodied control; EEG/MEG phantom source localization; diffusion tractography; EEG artifact repair; MRIQC; proposed blinded data-integrity faults; and reference-posterior GLM evaluation through sbibm.

The map now better reflects experimental, neuroimaging, behavioral and computational modeling perspectives. Pure analytical theory, formal proofs, specialized clinical/normative modeling, animal vocalization and several physiological modalities remain explicit scope boundaries. A paper should state its intended domain, log systematic searches and exclusions, deduplicate datasets/subjects, and seek expert review. No credible research map can guarantee that no reviewer will identify another task.

## Pilot methods

Task C05: calcium-to-spike inference, original Spikefinder dataset 1. Eleven paired training neurons and five original test neurons at 100 Hz. This is not a five-animal sample. Exact model IDs requested through Codex CLI: `gpt-6.1-sol` (the parent chat's recorded model), `gpt-6-sol`, and `gpt-5.6-sol`.

Each fresh context received the identical task prompt and high reasoning setting, with no tools, no raw test labels and one code submission. The external runner executed each unmodified estimator using general NumPy/SciPy/scikit-learn libraries, fitting on training data. Offline acausal test context was permitted. Generation logs record zero tool calls. Native model inference and iterative scientific-agent performance are different evaluation tracks.

Primary endpoint: median of five per-neuron Pearson correlations after 40-ms binning. Mean and all five cell scores are available in the measurement manifest. The scorer matches official downsampling/correlation functions and published archived values to numerical tolerance. Local execution used one numerical thread and a 180-second wall-clock limit per estimator.

## Measured results

| Method | Median correlation | Mean correlation | Evidence |
|---|---:|---:|---|
| Deneux specialist reference | 0.611641 | 0.601345 | Archived predictions rescored on the same five neurons |
| GPT-6.1 Sol generated estimator | 0.604587 | 0.599747 | New single-shot code submission and external execution |
| GPT-6 Sol generated estimator | 0.600762 | 0.594542 | New single-shot code submission and external execution |
| GPT-5.6 Sol generated estimator | 0.578914 | 0.580112 | New execution; code-length formatting deviation |
| OASIS 0.3.2 default AR(1) | 0.338756 | 0.328232 | New local unsupervised default run; not a tuned best specialist |
| Raw calcium baseline | 0.163300 | 0.191169 | Simple fluorescence correlation baseline |

The general models all produced trainable estimators. Their programs used multiscale fluorescence features and gradient-boosted regression; GPT-5.6 Sol also used a ridge blend. This demonstrates an executable, useful analysis-construction capability on one small task. It does not establish native signal understanding, statistical equivalence to specialists, or a universal generation-to-generation improvement trend.

## Important deviations and limits

- GPT-5.6 Sol returned 188 code lines including blanks, against a requested fewer-than-180 limit. Its unchanged numerical result is shown, with no unqualified strict protocol pass.
- Shared missing runtime dependencies were repaired before running unchanged submissions; no test feedback was sent to models.
- Approximate 3-GB memory was requested but not measured/enforced. Execution time and token counts are recorded; subscription tokens are not converted into invented dollar costs.
- One generated program per model, one dataset and five neurons do not support a stable ranking or population-level uncertainty estimate.
- Animal IDs and pretraining contamination are unresolved. Public test labels exist, although they were not supplied or accessed through tools during generation.
- Specialist methods differ in tuning and supervision histories. Similar point scores are not proof of matched total-effort superiority.

## What “current best” means here

Deneux has the highest mean and median among complete five-neuron archived submissions in the inspected original result table. This is an archived best-on-slice reference, not a verified current global SOTA.

Newer specialist work includes CASCADE and evaluations of GCaMP8 indicators. Those studies use different indicators, noise settings, sampling rates and target protocols; importing their scores into this five-neuron plot would be misleading. A current-best claim needs a per-task dated search and matched split/scorer/training regime. All unverified catalog entries retain “current best not verified.”

## Primary references and related benchmark perspectives

- [Spikefinder official data description](https://github.com/codeneuro/spikefinder-datasets)
- [Original challenge scoring, archived predictions and results](https://github.com/berenslab/spikefinder_analysis)
- [Community-based spike inference benchmark paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006157)
- [OASIS source](https://github.com/j-friedrich/OASIS)
- [Current CASCADE research and GCaMP8 resources](https://github.com/HelmchenLabSoftware/Cascade)
- [BrainWideBench](https://brainbench-org.github.io/ibl-bwb-project/), [NLB](https://neurallatents.github.io/), [NeuralBench](https://facebookresearch.github.io/neuroai/neuralbench/index.html): representation/dynamics/EEG benchmarks to reuse.
- [NeuroDiscoveryBench](https://github.com/allenai/neurodiscoverybench), [NeuroClaw NeuroBench](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html): direct prior work on analysis agents and workflows.
- [HippoUnit](https://doi.org/10.1371/journal.pcbi.1008114), [sbibm](https://github.com/sbi-benchmark/sbibm), [MyoChallenge](https://myosuite.org/myochallenge/): computational-model validation, calibrated inference and embodied control perspectives.
- [PRISMA-ScR](https://www.prisma-statement.org/scoping), [PRISMA-S](https://pmc.ncbi.nlm.nih.gov/articles/PMC8270366/): useful reporting standards for a future scoping review; compliance is not claimed for the initial discovery map.

The interactive browser exposes categories, readiness, source-linked task cards and the one measured comparison. The pilot bundle includes prompt, returned code, acquisition/scoring scripts, hashes, predictions, versions and results.
