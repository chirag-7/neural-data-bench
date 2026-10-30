> Historical planning snapshot. The current executed panel, results and remaining gaps are in [release 0.5](release-v05.md). Figures and plans below describe an earlier stage.

# General models for neuroscience laboratory data

Research map and benchmark design · 30 October 2026

## Project judgment

The project is viable if the main question is operational: **How much of a neuroscience laboratory's data-analysis pipeline can general pretrained models perform, with what adaptation, tools, cost, and scientific reliability, relative to specialist pipelines?**

The broad idea already has substantial prior work. A contribution can come from comparing these capabilities across laboratory tasks under one clearly controlled evaluation framework. Avoid claiming to introduce the first neuroscience AI benchmark or the first benchmark of general neural representations.

This report contains **90 task-resource pairings in 14 families**. These are not 90 independent datasets or newly discovered benchmarks. Some resources support several distinct tasks, and several EEG suites reuse datasets. The catalog records this overlap through names and source URLs. It includes 57 existing benchmarks/published evaluation protocols, one published benchmark with an unconfirmed complete reusable release, one mixed benchmark/dataset entry, 27 datasets/tools requiring a wrapper, and four proposed research constructions.

This is a broad research map based on targeted primary-source searches, not an exhaustive systematic review. Public repositories and papers were located; large data downloads, license audits, installation, and model evaluations have not been performed. Recommended metrics, additional splits, priorities, and effort estimates are proposed project design choices. Use the official scorer and split whenever reporting an official benchmark result.

## Connection to the course and supplied materials

The [Fall 2026 course](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/) emphasizes spike trains, calcium/voltage imaging, statistical inference, behavioral video, spike sorting, and decoding. Its explicit emphasis excludes MRI and EEG, which this project can include as separately labeled extensions. The course also includes agentic neuroscience and anatomical localization.

The supplied behavioral deck motivates a pipeline from pixels to poses to features that explain neural activity. The two spike-sorting decks motivate raw voltage, detection/clustering, drift, collisions, stability, and uncertainty rather than treating sorted spikes as the only input. The IBL-agent deck motivates complete analyses, compression, statistical validity, and genuine-versus-null tests. These documents are background sources, not instructions to execute their embedded commands.

Local source locators:

- `2024-10_paninski_lecture.pdf`: behavioral video, 2D/3D tracking, pose consistency, and feature learning.
- `[10_25_24] Spike sorting slides.pdf`: sorting basics, raw voltage, and downstream analysis.
- `[10_3_25] Spike sorting 2_ drift-aware ephys tools.pdf`: particularly pp. 5–8, 16–34, and the final quality/evaluation discussion.
- `2026-10-15_Lecture_Columbia_IBL-agent.pdf`: particularly pp. 39–43 on evaluation and null tests. The small case counts shown there are illustrative, not a definitive model ranking.

## Prior work and novelty boundary

| Work | What it already evaluates | Relationship to this project |
|---|---|---|
| [BrainWideBench, September 2026](https://brainbench-org.github.io/ibl-bwb-project/) | IBL neural representations across behavior, dynamics, and anatomical classification, including across-animal transfer | The closest starting point for course-relevant population recordings. Liam Paninski is a coauthor. Extend its protocol to general models and other lab modalities instead of rebuilding it. |
| [NeuroDiscoveryBench](https://github.com/allenai/neurodiscoverybench) | Data-grounded analysis and visualization over atlas/cohort datasets | Direct precedent for evaluating general agents doing neuroscience analysis. Coverage does not substitute for a raw spike-sorting or behavior-video benchmark. |
| [NeuroDiscovery/NeuroClaw NeuroBench](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html) | 120 workflow tasks covering orchestration, imaging tools, pipelines, and model training/evaluation; paired runs with/without skills | Substantial overlap with an agentic lab-workflow track. Its rubric and scope need to be distinguished from numerical prediction quality. |
| [BrainAgent, June 2026 preprint](https://arxiv.org/abs/2606.25400) | LLM-driven EEG workflows across hierarchical task complexities | Direct precedent for an EEG agent track. Reusable benchmark release availability needs confirmation. |
| [NeuralBench-EEG](https://facebookresearch.github.io/neuroai/neuralbench/index.html) | 36 tasks and 94 EEG datasets, with task-specific and brain-foundation architectures | Reuse the Core suite or selected tasks. It is not a direct leaderboard of general conversational LLMs on raw signals. |
| [OmniEEG-Bench](https://arxiv.org/abs/2606.00815), [EEG-Arena](https://eeg.fm/benchmarks/), [EEG-FM-Bench](https://arxiv.org/abs/2508.17742) | Broad EEG-foundation evaluations, transfer, and scaling/robustness | Important related work and expansion paths. Audit shared datasets before pooling results. |
| [MABe 22](https://arxiv.org/abs/2207.10553) | Behavioral representation transfer across species and downstream tasks | Close precedent for generic video/trajectory representations versus animal-specific methods. |
| [Segment Anything for Microscopy](https://www.nature.com/articles/s41592-024-02580-4) | General segmentation model adaptation to microscopy, including EM | Direct evidence about general visual pretraining versus domain adaptation, but not proof of complete neural movie demixing. |
| [BrainBench](https://www.nature.com/articles/s41562-024-02046-9) | Predicting experimental results from scientific descriptions | Relevant to reasoning, but it tests a different capability from analyzing supplied neural recordings. |
| [ScienceAgentBench](https://arxiv.org/abs/2410.05080) | Publication-derived scientific data analysis, including cognitive-neuroscience/EEG cases | Reuse relevant task/evaluation design, with a neuroscience-only subset. |
| [Many AI analysts, one dataset](https://arxiv.org/abs/2602.18710) | Variation among autonomous analysis pipelines and auditing of methodological validity | Important for measuring reliability across repeated analyses, rather than ranking a single attractive answer. |

**A defensible novelty claim:** a controlled comparison of general models across neural laboratory modalities, separating direct analysis, representation transfer, code generation, and specialist tool use, with domain-shift and scientific-validity tests. The sources above establish close overlap; this search does not prove that no paper already implements every part of that combined design.

Name collisions matter: BrainBench, BrainWideBench, NeuralBench, the NeuroClaw NeuroBench, and [NeuroBench for neuromorphic computing](https://github.com/NeuroBench/neurobench) are different resources. Always record a URL and version, not just a short name.

## A classification that works for experimental evaluation

Classify each case on multiple axes. A modality-only list hides the difference between raw-data cleanup and scientific interpretation; a task-only list hides very different input constraints.

1. **Input modality and level:** raw voltage, sorted spikes, fluorescence movie, extracted trace, behavior video, pose coordinates, EEG/MEG/ECoG/LFP, MRI/BOLD, morphology, molecular table, or multimodal combination. Raw and processed versions of the same recording are separate input conditions.
2. **Operation:** quality control, denoising/registration, detection/segmentation, tracking/identity, latent inference, encoding, decoding, forecasting, mechanistic inference, experimental design, or end-to-end scientific analysis.
3. **Biological generalization:** new time block, recording day, animal/person, lab/site, brain area, species, sensor/indicator, stimulus domain, or intervention. These are different transfer claims.
4. **Evidence and supervision:** measured paired ground truth, expert labels, behavioral target, simulation truth, or proxy/consensus. Record whether the task has an identifiable correct answer.
5. **Model access and adaptation:** base checkpoint, allowed input conversion, training labels, fitting/finetuning, external tools, and causal versus acausal context.

An evaluation case is the tuple **dataset version × task × input level × split × metric × permitted adaptation/tools**. Model performance is meaningful only relative to that tuple.

For example, predicting a mouse's choice from a processed spike-count matrix, recovering neuron identities from raw voltage, and writing code that invokes a sorter are three different tasks even when the recordings come from the same mouse.

### Task-family map

| Family | Input data | Tasks | Course relationship |
|---|---|---|---|
| A. Behavior video and kinematics | RGB/IR/depth videos, calibrated multiview video, pose trajectories | Detection, segmentation, identity tracking, 2D/3D keypoints, pose imputation, action labels, behavioral representations | Core |
| B. Extracellular signal acquisition | Raw multichannel voltage, waveforms, spike events, probe geometry | Spike detection/sorting, collision recovery, drift, curation/QC, longitudinal matching, compression | Core |
| C. Calcium imaging and photometry | 1P/2P/3D calcium movies, fluorescence traces, reference photometry channels | Motion correction, denoising, ROI segmentation, demixing, deconvolution, cell registration, event analysis | Core |
| D. Voltage, intracellular and dendrites | Voltage movies, patch clamp current/voltage traces, dendritic morphologies | Spike extraction, subthreshold recovery, current-to-voltage prediction, dendritic smoothing, parameter fitting | Core |
| E. Population activity and dynamics | Spike trains/count tensors, calcium activity, covariates | Rate inference, co-smoothing, forecasting, latent dynamics, anatomy from activity, transfer | Core |
| F. Sensory and behavioral encoding | Image/audio/video stimuli or behavior aligned to neural responses | Stimulus-to-neural response prediction, receptive fields, neural encoding of movement | Core |
| G. Intracortical BCI | Human/primate spikes, threshold crossings, ECoG where available | Motor decoding, adaptation, handwriting, attempted speech, causal streaming inference | Extension |
| H. EEG, MEG, field signals and peripheral interfaces | EEG/MEG/LFP/ECoG time series, ERP, sEMG, montage and event metadata | Motor imagery, ERP/SSVEP, sleep, seizure, artifacts, cognition, speech/image retrieval, peripheral decoding | Extension |
| I. Human and mesoscopic neuroimaging | fMRI BOLD, MRI k-space/volumes, fNIRS, functional ultrasound | Encoding/decoding, reconstruction, segmentation, hemodynamic activity analysis | Extension |
| J. Anatomy, histology and connectomics | Histology/light-sheet/EM volumes, skeletons, atlases, probe tracks | Registration, region localization, cell identification, tracing, synapses, connectivity graphs | Core-adjacent |
| K. Cell types and molecular neuroscience | Patch-seq, scRNA/scATAC, spatial transcriptomics, morphology | Cell type mapping, multimodal prediction, batch integration, spatial/cell abundance analysis | Extension |
| L. Mechanistic and statistical inference | Spike/calcium/voltage observations, simulated circuits, trial tables | Connectivity, biophysical parameters, uncertainty, confounding, hypothesis tests, null calibration | Core |
| M. Experimental design and control | Simulators, psychophysics trials, actions/interventions, neural feedback | Adaptive stimuli, power/sample design, optimal control, behavioral model fitting | Research extension |
| N. Scientific analysis workflows | NWB/BIDS files, data dictionaries, analysis code and reports | Data loading/QC, complete analyses, figure reproduction, valid inference and reproducibility | Core |

BCI is an application domain spanning several modalities, not a single input type. Motor-imagery EEG, intracortical reaching, attempted speech, and ECoG decoding need different outputs and protocols. EMG is a useful peripheral interface extension and must be labeled as such. Cognitive task simulation is relevant to computational neuroscience but is not itself analysis of a neural recording.

## Which models count as general?

Use two independent labels: **pretraining domain** and **evaluation procedure**.

| Model group | Examples of intended capability | How to use it |
|---|---|---|
| General language/multimodal model | Instructions, images/videos, code generation, scientific reasoning | Direct structured outputs where the interface supports the data; standardized code-agent evaluation for numeric recordings |
| General vision/video model | Image/video embeddings, segmentation, tracking | Frozen features plus a controlled readout, or promptable masks/keypoints; record any animal/neuro finetuning |
| General time-series model | Numeric forecasting or transferable signal representations | Fixed resampling/channel adapter and explicit rate/output head; check multivariate and sampling-rate support |
| General 3D/world/embodied model | Dynamics, geometry, novel views, control | Use only where its supported inputs and outputs match a defined task; distinguish learned state from rendered appearance |
| Neuroscience/animal-domain foundation model | EEG, spiking populations, animal pose, neural response pretraining | A separate comparator group: POYO/NDT variants, EEG FMs, SuperAnimal, and neural visual-cortex FMs |
| Specialist method | A purpose-built estimator or pipeline | Both a strong traditional baseline and a strong recent task-specific baseline |

Open/closed access is another axis. Record open weights, code availability, training-data disclosure, license, and reproducible version identifiers separately. Open weights do not necessarily mean fully open source or known pretraining data.

Do not force every model onto every modality. A chat model without a numerical encoder is not a native high-rate multichannel signal model. Its native inapplicability, the cost of converting data to an image, and performance of an authorized code tool are distinct observations. A raster-plot test primarily measures perception of that visualization, not lossless use of the underlying spikes.

### Separate evaluation tracks

| Track | Allowed procedure | Claim supported |
|---|---|---|
| T0: direct pretrained inference | Frozen model; fixed documented prompts and formatting; no task-label fitting | Direct off-the-shelf capability on supported inputs |
| T1: fixed representation transfer | Frozen backbone plus a prespecified linear/small readout; equal label budgets | Transferability of general features |
| T2: bounded adaptation | Matched finetuning/adapter budget and validation search | Adaptation efficiency |
| T3: code agent with general libraries | Same runtime, files, NumPy/SciPy/sklearn/PyTorch availability; no specialist solver or existing solution code | Ability to construct a working analysis |
| T4: agent with neuroscience tools | Same specialist tools and documentation available to all agents | Workflow selection, execution, and interpretation |

Record pretrained model domain within every track. A neuroscience-pretrained model can participate in T0–T2, but its results remain a separate group from general pretraining. Record pretrained inference versus per-recording test-time optimization even when labels are absent. Specialist reference runs should be deterministic where possible and have comparable tuning effort.

## What existing results actually establish

No new model scores are reported here. The following are literature results under their authors' settings, not a new common leaderboard or necessarily the latest score for the named system.

| Evidence | Reported finding | Interpretation for this project |
|---|---|---|
| [Ai 2 NeuroDiscoveryBench release, December 2025](https://allenai.org/blog/neurodiscoverybench) | GPT-5.1 medium reasoning: 6% no-data, 8% no-data with search, and 35% with DataVoyager executing analyses | Data access and executed analysis help substantially. This is not a specialist-prediction parity result or a causal estimate of model scaling. |
| [NeuroClaw NeuroBench](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html) | Claude Opus 4.6: 69.12 without skills and 72.10 with skills, on its reported percentage rubric | Scaffolding affects the score. Keep skills/tool access fixed across models and do not interpret rubric points as neural decoding accuracy. |
| [NeuralBench white paper, May 2026](https://arxiv.org/abs/2605.08495) | Brain-foundation models only marginally outperform task-specific models in its EEG evaluation; many tasks remain challenging | Domain pretraining does not uniformly eliminate specialist models. This does not directly evaluate general LLMs. |
| [BrainWideBench paper](https://arxiv.org/abs/2609.22064) | Pretraining improves matched single-session baselines, with strongly task-dependent transfer and no approach uniformly best across all three suites | Cross-task generality remains an empirical question. Include decoding, activity prediction, and anatomical information separately. |
| [NDT3 study](https://papers.nips.cc/paper_files/paper/2025/file/a00000e6a2208172700510bcd69d48e9-Paper-Conference.pdf) | A generalist intracortical motor decoder benefits from pretraining, while its NLB analysis reports poor competitiveness for low-level neural-rate modeling | Better behavior decoding does not imply better neural generative modeling. NDT3 is a neural-domain model. |
| [SuperAnimal](https://www.nature.com/articles/s41467-024-48792-2) | Strong zero-shot and low-label animal-pose transfer, including performance close to supervised references on some datasets | Transfer can be highly useful, but this animal-domain result should not be attributed to an unrestricted general VLM. |
| [Micro-SAM](https://www.nature.com/articles/s41592-024-02580-4) | Domain-adapted generalist microscopy models improve over default SAM on evaluated microscopy images | Generic visual pretraining is useful, with domain adaptation still consequential. Segmentation quality does not establish correct event extraction. |
| [Algonauts 2025 submission study](https://arxiv.org/abs/2510.06235) | Evaluates off-the-shelf, stimulus-tuned, and finetuned features for predicting fMRI responses | A useful setting for general multimodal representations with a fitted readout; it is not zero-shot neural response prediction. |

The evidence supports a mixed picture: general representations and agents already help, domain models show transfer benefits, and specialist methods remain important. This review does not establish that a general conversational model matches Kilosort, calcium deconvolution, or streaming BCI decoders across standardized tests.

### How to measure whether models are improving

Chronological publication order is insufficient. To claim progress, rerun older and newer immutable checkpoints under the same cases, agent harness, prompt, tool/library versions, inference budget, adaptation labels, and scoring. Compare model-family changes separately from harness improvements. Closed API endpoints require dated version IDs where available; record when a provider changes the endpoint and a result cannot be exactly reproduced.

Use four trend plots later: native task performance versus release date; specialist gap versus release date; performance versus adaptation labels; and performance versus total cost. Report uncertainty and per-family results. Model size and data diversity associations, such as those examined in [OmniEEG-Bench](https://arxiv.org/abs/2606.00815), are useful evidence about domain-model scaling but do not prove time-based improvement of general LLMs.

## A practical first experiment suite

The full catalog is a long-term map. For a course project, begin with **six anchors**, retaining their official definitions where available:

| Anchor | First task | Why start here | Main comparison |
|---|---|---|---|
| A01 Lightning Pose / IBL | Pupil or paw keypoints on a held-out session | Clear labels; directly tied to behavior measurement | Generic vision features + fixed head against Lightning Pose/DLC; optional direct VLM coordinate track |
| C05 Spikefinder | Fluorescence trace to spike-rate estimate | Small numeric task with paired recording truth | Generic sequence approach/agent against OASIS and a strong released baseline |
| E01 NLB | Held-out-neuron co-smoothing on one dataset | Established scoring for neural population models | General sequence architecture/pretraining against GPFA and strong neural models |
| E03 BrainWideBench TS1 | One decoding endpoint with the fixed animal split | Course/IBL alignment and existing transfer baselines | General time-series representations against released BWB methods |
| N01 NeuroDiscoveryBench | A frozen small raw/processed task subset | Direct precedent for language-agent data analysis | Same agent harness across open-weight and closed models |
| L03 IBL null tests | One genuine analysis plus many hidden null cases | Tests whether apparently successful analysis is statistically trustworthy | General-library agent, specialist-tool agent, and prespecified expert analysis |

Add **B01 SpikeForest** when a paired/synthetic subset downloads and runs reliably, and **H01 MOABB motor imagery** for a noninvasive BCI extension. Add **C01 Neurofinder** if image segmentation should be in the first round. These are expansion anchors, not requirements to run the entire 90-entry map this semester.

Begin with one affordable pilot case per anchor, verify baselines and scorers, then expand to biologically independent held-out recordings. A sensible first full comparison is two closed model versions, two open-weight versions with distinct sizes, one or two relevant general vision/time-series backbones, and specialist references. Select exact available checkpoints and budgets only when execution resources are known. Do not assume every model participates in all tracks.

### Example benchmark cards to make the next step concrete

**Calcium trace card:** fluorescence, time base, indicator metadata, and allowed calibration labels are inputs; predicted nonnegative rate is the output. Preserve the Spikefinder metric/binning and report any added event metric separately. Split complete cells/recordings, fit normalization on train data, and include both a specialist estimator and a simple baseline. Evaluate general direct inference only if the model has a valid numerical input interface; separately evaluate code it writes.

**IBL choice-decoding card:** specify prediction cutoff and allowed spikes/covariates. Output a trial probability, score the exact benchmark metric, and split by the published animal/session structure. Include a prior-only baseline and prevent post-choice movement or future spikes from entering an anticipatory decoding task. Report full-trial decoding as a different condition if permitted.

**Scientific-validity card:** the agent receives trials and spikes from genuine or blinded null conditions. Require a machine-readable effect estimate, uncertainty, test definition, and conclusion. Score power on valid positive cases and false-positive rate on null cases. Null generation must preserve the task's temporal/behavioral dependencies; trial-history-aware resampling may be required. A hand-designed simple simulated null provides a useful sanity check before applying the real-data null protocol.

**Behavior card:** provide a fixed camera image/video, keypoint schema, coordinate system, and permitted training labels. Output coordinates/confidences, then score on held-out manually labeled frames. Aggregate by complete session/animal, not individual adjacent frames. If neural prediction is a secondary endpoint, use one locked readout for all pose/feature sources.

## Evaluation rules that change the scientific conclusion

1. **Keep the test set outside the agent workspace.** Hide labels, gold scripts, reference answers, and repository history containing solutions. Public benchmarks can be memorized; use unpublished or newly generated held-out cases where possible, and record unknown pretraining exposure.
2. **Split at the biological unit.** Thousands of cells from one donor or frames from one mouse are not thousands of independent experiments. Use animal/participant/session/site splits appropriate to the claim and clustered bootstrap intervals over those units.
3. **Distinguish causal streaming from offline smoothing.** Restrict future frames, spikes, behavioral events, and adaptation labels in an online BCI task. Record prediction latency and preprocessing latency.
4. **Preserve useful signals.** Denoising/registration/compression must also be scored by recovered events or downstream inference. Nice images and low pixel loss are insufficient evidence of accurate neural analysis.
5. **Match adaptation and tuning budgets.** Report label count, labels used for prompt selection, unsupervised test-time fitting, training FLOPs/GPU time, and validation search. Do not label a trained neural-input adapter as zero-shot.
6. **Use both simple and strong specialist references.** Mean/rate, ridge/GLM, linear dynamics, interpolation, and stimulus/behavior-only baselines detect problems and quantify actual added value.
7. **Use deterministic numerical scoring where possible.** Grade numeric arrays, masks, spike times, invariants, and held-out predictions directly. LLM judging can supplement interpretation, with expert auditing on a sample and on borderline/high-impact conclusions.
8. **Score failure and abstention explicitly.** Track unsupported input, format failure, invalid analysis, runtime failure, resource-budget failure, and low predictive performance separately. Missing results remain missing, not numeric zero. Abstention can be useful, but must be scored against coverage.
9. **Repeat stochastic runs.** For a pilot, use at least several seeds/runs where affordable; expand based on variability. A prespecified experiment-level bootstrap is more useful than treating repeated agent runs as independent animals.
10. **Keep dependence-aware nulls and an untouched confirmation stage.** Avoid trying windows or seeds until significance appears. Measure false positives, statistical assumption violations, uncertainty coverage, and replication of conclusions.

### Comparing across tasks

Keep native scores primary and do not average correlations, F1, bits/spike, WER, and statistical false-positive rates. A comparative plot can use specialist-relative skill after fixing a meaningful baseline:

- For higher-is-better scores: `(model_score - simple_baseline) / (specialist_score - simple_baseline)`.
- For lower-is-better errors: `(simple_baseline_error - model_error) / (simple_baseline_error - specialist_error)`.

A value of 1 matches the chosen specialist, 0 matches the simple baseline, negative is worse than the simple baseline, and above 1 exceeds that specialist. This is an optional display normalization, not an official benchmark metric. Do not compute it when the specialist does not improve on the baseline, or when the gap is too small relative to uncertainty. Do not silently clip values. Aggregate only within defined task families with equal family weighting and disclose missing coverage. A family median plus intervals is more interpretable than a universal 'neuroscience intelligence' score.

Define 'close to specialists' before examining results, using a task-specific equivalence/noninferiority margin that matters scientifically. A 2-point pose mAP gap, a few extra BCI word errors, and a doubled false-positive rate have very different practical meaning.

### Run manifest

Save: case ID and dataset hash; model provider/checkpoint/version and release date; pretraining-domain category; open-weight/code/license status; input conversion; output adapter and its training data; track; prompt hash; allowed tools/library versions; train/validation/test animal/session IDs; label budget; causal context; random seeds; evaluation scorer version; all raw predictions; native metrics and uncertainty; wall time, peak memory, GPU hours, API/token cost; failure reason and statistical-validity audit. Keep literature-reported and newly reproduced results in separate fields.

## Resources that are not automatically easy benchmarks

Archives such as [DANDI](https://about.dandiarchive.org/), [CRCNS](https://crcns.org/data-sets), and [IBL public data](https://www.internationalbrainlab.com/data) provide valuable recordings, but each case still needs explicit inputs/targets, a split, truth provenance, a scorer, and baselines. Tools such as CellReg, GuPPy, Spikepack, and Jaxley are not automatically ready-made broad benchmarks either.

Harder gaps include real-data causal connectivity, chronic neuron identity without definitive truth, dendritic voltage reconstruction, unsupervised behavioral syllable validity, and adaptive experiments with biological interventions. These are important research questions, but they should not be advertised as datasets that can all be made into rigorous benchmarks easily. The catalog marks such limitations and places novel simulator protocols in a separate R class.

For functional connectivity, separate correlation/predictive coupling, directed statistical influence, and causal effects under intervention. For image/word reconstruction, separate retrieval from a known candidate gallery from unrestricted reconstruction, and include a no-neural-input control for semantic/language/generative priors.

## Detailed task-resource catalog

Legend: **B** existing benchmark or published evaluation protocol; **B*** published benchmark whose complete reusable release was not independently confirmed; **B/D** ready protocol for some tasks and a wrapper for others; **D** reusable data/tool needing a proposed wrapper; **R** a research construction. Low/Medium/High describe relative setup effort for a small slice, not measured compute or installation success. P1 entries are strong pilot candidates; P2 are expansions; P3 need more engineering or a research protocol.

Each entry in the workbook/JSON includes truth provenance, recommended metrics and split, specialist references, a general-model route, important limitations, and primary links. The following condensed tables support scanning; the editable catalog is the experiment-planning record.

### A. Behavior video and kinematics

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| A01 | **2D lab keypoints and pupil/paw tracking**. Lightning Pose datasets: IBL-pupil, IBL-paw, mirror-mouse/fish, CRIM13. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC12087009/) | B / Low; P1 | Truth: Human keypoint annotations. Metrics: Pixel/normalized error; PCK; temporal outliers. Split: Retain published splits; additional unseen lab/session split. | Frame-adjacent train/test leakage; pupil occlusion |
| A02 | **Cross-species 2D pose transfer**. AP-10K and DLC benchmark datasets. [source 1](https://arxiv.org/abs/2108.12617); [source 2](https://benchmark.deeplabcut.org/datasets.html) | B / Low; P2 | Truth: Human keypoint annotations. Metrics: OKS mAP or published normalized error. Split: Official splits; held-out species or lab. | Wild images differ from head-fixed laboratory footage |
| A03 | **Low-label lab pose adaptation**. SuperAnimal leave-one-dataset-out releases. [source 1](https://www.nature.com/articles/s41467-024-48792-2) | B / Low; P2 | Truth: Held-out human keypoints. Metrics: mAP; error versus annotation budget. Split: Use documented leave-one-out variants. | SuperAnimal is animal-domain pretraining, not a general-purpose model |
| A04 | **Single-animal 3D pose**. Rat 7M / DANNCE. [source 1](https://figshare.com/collections/Rat_7M/5295370/3); [source 2](https://www.nature.com/articles/s41592-025-02893-y) | B / Medium; P2 | Truth: Motion-capture landmarks; incomplete frames. Metrics: MPJPE in physical units; missing-point robustness. Split: Hold out animal/session; retain camera calibration. | Dense frames are correlated; mocap missingness |
| A05 | **Social multi-animal 3D pose**. PAIR-R24M. [source 1](https://olveczkylab.oeb.harvard.edu/publications/pair-r24m-dataset-multi-animal-3d-pose-estimation) | B / Medium; P2 | Truth: 3D motion capture and identities. Metrics: MPJPE; identity switches; occlusion strata. Split: Held-out pair/recording. | Large downloads; collisions; mocap-to-image correspondence |
| A06 | **3D pose and shape from one image**. Animal 3D. [source 1](https://arxiv.org/abs/2308.11737) | B / Medium; P2 | Truth: Annotated 2D/3D model-derived shape/pose. Metrics: Published pose/shape errors; reprojection error. Split: Official held-out images/species. | Fitted shape labels are not direct physical motion capture |
| A07 | **Data-efficient calibrated 3D lab pose**. Lightning Pose 3D evaluation datasets. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC13131684/) | B / Medium; P2 | Truth: Labeled 3D/multiview landmarks. Metrics: 3D error; per-view error; uncertainty calibration. Split: Published splits; unseen individuals. | Requires calibrations and synchronized cameras |
| A08 | **Animal identity tracking through occlusions**. idtracker.ai 2026 benchmark. [source 1](https://doi.org/10.7554/eLife.107602.3) | B / Medium; P2 | Truth: Human-validated trajectories. Metrics: IDF1; ID switches; runtime. Split: Hold out complete videos. | Mask tracking does not establish persistent identity |
| A09 | **Frame-level social behavior labels**. CalMS21. [source 1](https://arxiv.org/abs/2104.02710) | B / Low; P1 | Truth: Expert behavioral labels. Metrics: Macro F1; per-class precision/recall; event F1. Split: Official annotator and low-label tracks. | Annotator definitions differ; rare behaviors |
| A10 | **General behavioral representations**. MABe 22. [source 1](https://arxiv.org/abs/2207.10553) | B / Medium; P2 | Truth: Experimental metadata and behavioral annotations. Metrics: Official downstream task metrics; per-task macro scores. Split: Official task and recording splits. | One aggregate can hide failures by species or task |
| A11 | **Action recognition and temporal localization**. Animal Kingdom. [source 1](https://arxiv.org/abs/2204.08129) | B / Medium; P2 | Truth: Action labels, temporal segments, keypoints. Metrics: Action mAP; localization scores; pose metric. Split: Official split. | Ecological domain differs from neuroscience lab video |
| A12 | **Behavioral features for neural prediction**. BEAST released evaluation tasks. [source 1](https://arxiv.org/abs/2507.09513) | D / Medium; P2 | Truth: Keypoints/actions and measured neural responses. Metrics: Pose/action metrics; held-out neural encoding score. Split: Entire held-out recordings/animals. | Method evaluation suite needs a frozen common wrapper |
| A13 | **Dense 3D behavior representation**. BEAST3D / Pose Splatter released data and code. [source 1](https://arxiv.org/abs/2606.02937); [source 2](https://arxiv.org/abs/2505.18342) | D / High; P3 | Truth: Held-out camera images; selected pose/neural labels. Metrics: Novel-view PSNR/SSIM; 3D keypoint error; neural encoding. Split: Hold out camera and recording; prevent same-frame cross-view leakage. | Photorealistic rendering alone does not show correct neuroscience features |
| A14 | **Missing pose imputation**. DISK evaluation datasets. [source 1](https://www.nature.com/articles/s41592-025-02893-y) | B / Low; P2 | Truth: Observed positions hidden under known masks. Metrics: Position error by gap length; downstream behavior impact. Split: Mask only held-out trajectories; preserve published protocol. | Artificial missingness may understate occlusion difficulty |

### B. Extracellular signal acquisition

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| B01 | **Spike sorting and event detection**. SpikeForest available subset. [source 1](https://github.com/flatironinstitute/spikeforest); [source 2](https://elifesciences.org/articles/55167); [source 3](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html) | B / Medium; P1 | Truth: Paired recordings and/or simulated known spikes. Metrics: Matched-event precision/recall/F1; unit recovery. Split: Hold out recordings/probe types; separate truth types. | Current repo exposes subset; paired truth often only one neuron |
| B02 | **Drift-aware spike sorting**. SpikeInterface drifting generators / MEArec integration. [source 1](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html); [source 2](https://github.com/cwindolf/dartsort) | B / Medium; P2 | Truth: Known spike times, units and simulated motion. Metrics: Event F1; unit recovery versus drift/SNR. Split: Unseen seeds, templates and motion trajectories. | Simulation-to-real gap; do not reuse templates in test |
| B03 | **Probe motion estimation**. SpikeInterface motion benchmarks / DREDge. [source 1](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html); [source 2](https://github.com/evarol/dredge) | B / Medium; P2 | Truth: Known imposed/simulated displacement. Metrics: Motion MAE in micrometers; downstream sorting change. Split: Held-out recording/motion profile. | Real motion estimates are often proxy truth |
| B04 | **Collision recovery and sorting robustness**. SpikeInterface collision/hybrid evaluation. [source 1](https://spikeinterface.readthedocs.io/en/stable/modules/comparison.html); [source 2](https://spikeinterface.readthedocs.io/en/stable/modules/benchmark.html) | B / Medium; P2 | Truth: Injected events and templates. Metrics: Recall versus interspike lag; false detections. Split: Unseen templates and collision patterns. | Injected waveforms may make evaluation easier than real data |
| B05 | **Neuron matching across days**. UnitMatch released recordings. [source 1](https://www.nature.com/articles/s41592-024-02440-1) | D / Medium; P3 | Truth: Functional/stability proxies; curated matches. Metrics: Precision/recall where validated; match calibration. Split: Held-out animals and nonadjacent days. | No definitive ground truth for all chronic matches |
| B06 | **Brain-region/probe localization from ephys**. IBL Ephys Atlas feature release. [source 1](https://huggingface.co/int-brain-lab/ea-decoder-channel-xgboost) | D / Medium; P2 | Truth: Histology-aligned region labels. Metrics: Balanced accuracy; macro F1; spatial localization error. Split: Hold out animals/insertions, not adjacent channels. | Histological alignment is uncertain; rare regions |
| B07 | **Raw neural data compression**. AIND electrophysiology compression benchmark. [source 1](https://allenneuraldynamics.github.io/data.html) | B / Low; P2 | Truth: Original bytes or original downstream output. Metrics: Compression ratio; throughput; waveform/sorting distortion. Split: Held-out recordings and probe types. | Lossless byte equality differs from downstream-preserving lossy compression |
| B08 | **Spike train compression**. Spikepack plus public IBL spike trains. [source 1](https://github.com/int-brain-lab/spikepack); [source 2](https://www.internationalbrainlab.com/data) | D / Low; P2 | Truth: Original integer event arrays. Metrics: Exact round trip; bits/spike; throughput. Split: Held-out sessions; preserve timestamp quantization. | Codec/tool, not an established model benchmark; preserve timing |

### C. Calcium imaging and photometry

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| C01 | **Calcium ROI detection**. Neurofinder. [source 1](https://github.com/codeneuro/neurofinder-datasets); [source 2](https://github.com/codeneuro/neurofinder) | B / Low; P1 | Truth: Human cell-region annotations. Metrics: Matched ROI precision/recall/F1. Split: Official split; local held-out labeled sessions. | Old submission service not verified; silent/overlapping cells ambiguous |
| C02 | **Activity extraction and demixing**. CaImAn annotated nine-dataset corpus. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6342523/) | B / Medium; P2 | Truth: Consensus ROI annotations; not full true activity. Metrics: ROI F1; held-out residual/activity diagnostics. Split: Published train/test datasets. | Human masks do not establish correct recovered time courses |
| C03 | **Synthetic calcium pipeline with full truth**. NAOMi. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/) | D / Medium; P2 | Truth: Simulated masks, fluorescence, spikes and motion. Metrics: ROI F1; trace error; event metrics; motion error. Split: Unseen anatomies, optical settings and random seeds. | Simulator truth may not capture real tissue/indicator shift |
| C04 | **Calcium movie denoising**. DeepCAD / DeepCAD-RT evaluation data. [source 1](https://github.com/cabooster/DeepCAD/blob/master/dataset/README.md); [source 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC8217135/) | D / Medium; P2 | Truth: Simulated clean reference or paired acquisition proxy. Metrics: PSNR/SSIM when justified; trace/event preservation. Split: Held-out biological recording; noise-level shift. | Pleasing denoised movies can erase weak events |
| C05 | **Calcium-to-spike inference**. Spikefinder. [source 1](https://github.com/codeneuro/spikefinder-datasets); [source 2](https://github.com/berenslab/spikefinder_analysis) | B / Low; P1 | Truth: Simultaneous electrophysiological spike recordings. Metrics: Published binned correlation; add event PR at fixed tolerance. Split: Original split; additional leave-lab/indicator-out. | Published correlation is not millisecond spike-time accuracy |
| C06 | **Cross-preparation calcium deconvolution**. CASCADE ground-truth database. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC7611618/) | B / Low; P2 | Truth: Simultaneous electrophysiology. Metrics: Rate correlation; error; calibration by noise level. Split: Hold out preparation/cell/indicator. | CASCADE is domain trained; compare equal adaptation budgets |
| C07 | **Longitudinal calcium cell registration**. CellReg examples and released study data. [source 1](https://github.com/zivlab/CellReg) | D / Medium; P3 | Truth: Curated/proxy cell matches. Metrics: Match precision; recall on validated cells; uncertainty. Split: Held-out animal and session gap. | No universal true cell identity labels; add curated subset |
| C08 | **Fiber photometry cleanup and event analysis**. GuPPy sample data with artifacts. [source 1](https://github.com/LernerLab/GuPPy) | D / Low; P2 | Truth: Known analysis outputs; injected artifacts for stronger truth. Metrics: Artifact recovery; peri-event estimate error; reproducibility. Split: Hold out recording; inject blinded synthetic events. | Reference-channel correction can remove biology; samples are not a biological benchmark |
| C09 | **One-photon microendoscopic demixing**. CNMF-E published evaluation datasets. [source 1](https://elifesciences.org/articles/28728) | D / Medium; P2 | Truth: Simulated truth and expert/paired validation on selected examples. Metrics: ROI precision/recall; trace recovery where truth exists; background residuals. Split: Hold out recordings and background/noise conditions. | Strong out-of-focus background differs from two-photon data; truth varies |

### D. Voltage, intracellular and dendrites

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| D01 | **Voltage imaging spike and subthreshold extraction**. VolPy evaluation corpus. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC8075204/) | B / Medium; P2 | Truth: ROI labels; paired ephys and simulations on subsets. Metrics: Spike precision/recall/F1; trace error on paired subset. Split: Held-out preparation/indicator. | Not every movie has ephys truth; distinguish segmentation and spike scoring |
| D02 | **Current-to-voltage prediction**. Allen Cell Types Database. [source 1](https://brain-map.org/support/documentation/documentation-cell-types-database); [source 2](https://alleninstitute.github.io/AllenSDK/cell_types.html) | D / Low; P2 | Truth: Measured voltage and recorded stimulation. Metrics: Voltage RMSE; spike timing/count; held-out stimulus response. Split: Hold out complete cells and stimulation protocols. | Future current input may be known, future measured voltage is not |
| D03 | **Dendritic voltage/calcium recovery**. Jaxley examples and simulated dendritic recordings. [source 1](https://www.nature.com/articles/s41592-025-02895-w) | R / High; P3 | Truth: Known simulated compartment states; limited experimental truth. Metrics: Held-out voltage error; event propagation; posterior coverage. Split: Unseen morphologies and stimulation sites. | Requires designed simulator protocol; not ready-made benchmark |

### E. Population activity and dynamics

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| E01 | **Neural rate inference and co-smoothing**. Neural Latents Benchmark 2021. [source 1](https://neurallatents.github.io/) | B / Low; P1 | Truth: Held-out observed spikes; behavioral covariates. Metrics: Official co-bps; fp-bps; decoding/PSTH metrics as applicable. Split: Keep official held-in/out neurons, trials and binning. | EvalAI closed Jan 2026; test data public; guard test overfitting |
| E02 | **Recovery of computational dynamics**. Computation-through-Dynamics Benchmark. [source 1](https://github.com/snel-repo/ComputationThroughDynamicsToolkit) | B / Medium; P2 | Truth: Ground-truth simulated dynamics and states. Metrics: Provided dynamics/reconstruction metrics; fixed-point analysis. Split: Official canonical tasks; held-out seeds. | Good neural prediction does not guarantee correct dynamical mechanism |
| E03 | **Behavior decoding across animals**. BrainWideBench TS1. [source 1](https://brainbench-org.github.io/ibl-bwb/); [source 2](https://arxiv.org/abs/2609.22064) | B / Medium; P1 | Truth: Measured trial outcomes/behavior. Metrics: Official task-specific decoding metrics. Split: Official animal/pretraining/evaluation split. | Brain-pretrained models are domain comparators; preprocessing must match |
| E04 | **Masked/future neural activity prediction**. BrainWideBench TS2. [source 1](https://brainbench-org.github.io/ibl-bwb/); [source 2](https://arxiv.org/abs/2609.22064) | B / Medium; P1 | Truth: Held-out observed spikes. Metrics: Official likelihood/activity prediction scores. Split: Official masks and temporal evaluation protocol. | Do not conflate acausal infilling with causal forecasting |
| E05 | **Anatomy from neural activity**. BrainWideBench TS3. [source 1](https://brainbench-org.github.io/ibl-bwb/); [source 2](https://arxiv.org/abs/2609.22064) | B / Medium; P2 | Truth: Histology-derived region assignments. Metrics: Official region classification metrics. Split: Official unit/animal splits and allowed calibration. | Not the same task as histology probe registration |

### F. Sensory and behavioral encoding

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| F01 | **Static visual encoding**. Sensorium 2022. [source 1](https://sensorium-competition.net/) | B / Medium; P2 | Truth: Measured neural responses. Metrics: Official response correlation; noise-aware secondary metrics. Split: Official stimulus/mouse split and behavior-input track. | ImageNet features plus neural head are adapted models |
| F02 | **Dynamic visual encoding**. Sensorium 2023. [source 1](https://sensorium-competition.net/) | B / High; P2 | Truth: Measured held-out responses. Metrics: Official single-trial correlation. Split: Official videos/mice; separate stimulus and behavior inputs. | Temporal context and behavioral covariates affect fairness |
| F03 | **Receptive fields and sensory response prediction**. Allen Brain Observatory Visual Coding. [source 1](https://observatory.brain-map.org/visualcoding) | D / Medium; P2 | Truth: Neural responses and stimulus timings. Metrics: Held-out likelihood/correlation; receptive-field recovery proxies. Split: Hold out stimulus blocks and animals. | Large data; common stimulus repetitions can leak across splits |
| F04 | **Retinal or other sensory encoding**. CRCNS retinal datasets; selected sensory collections. [source 1](https://crcns.org/data-sets) | D / Medium; P2 | Truth: Measured spike trains with aligned stimuli. Metrics: Held-out Poisson likelihood; bits/spike; response correlation. Split: Contiguous held-out stimulus segments; held-out retina where feasible. | Verify stimulus licensing and download terms per dataset |
| F05 | **Behavior-to-widefield neural encoding**. Musall et al. public multimodal recordings. [source 1](https://repository.cshl.edu/38599/2/DataDescription_Musall.pdf) | D / Medium; P2 | Truth: Measured widefield activity and behavioral events. Metrics: Cross-validated explained variance; contribution of covariates. Split: Hold out contiguous trials and animals; use nested model comparisons. | Movement covariates and trial history are confounds; fluorescence is indirect |

### G. Intracortical BCI

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| G01 | **Robust cross-day motor decoding**. FALCON motor tracks. [source 1](https://snel-repo.github.io/falcon/) | B / Medium; P1 | Truth: Recorded kinematics on held-out days. Metrics: Official track metric; latency and adaptation labels. Split: Official calibration and held-out-day protocol. | Offline acausal prediction cannot count as online BCI control |
| G02 | **Handwriting/communication decoding**. FALCON communication tracks. [source 1](https://snel-repo.github.io/falcon/) | B / Medium; P2 | Truth: Recorded target character or vocal sequence labels. Metrics: Official track-specific error/quality metric. Split: Official few-shot/zero-shot held-out sessions. | Keep each track separate; language priors can dominate |
| G03 | **Attempted speech to text**. Brain-to-Text 2024 resources and 2025 competition. [source 1](https://github.com/fwillett/speechBCI); [source 2](https://www.kaggle.com/competitions/brain-to-text-25/overview) | B / Medium; P2 | Truth: Prompted attempted-speech text/phonemes. Metrics: WER; phoneme error; causal latency. Split: Official held-out days and sentence split. | Report neural-only/no-neural controls; competition access/rules may apply |

### H. EEG, MEG, field signals and peripheral interfaces

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| H01 | **Motor imagery and noninvasive BCI**. MOABB motor imagery datasets. [source 1](https://moabb.neurotechx.com/) | B / Low; P1 | Truth: Task labels. Metrics: Balanced accuracy or official dataset metric. Split: Within-session, cross-session and held-out-subject separately. | Random epoch splits inflate subject generalization |
| H02 | **ERP/P300 target decoding**. MOABB ERP/P300 datasets. [source 1](https://moabb.neurotechx.com/) | B / Low; P2 | Truth: Target/nontarget event labels. Metrics: ROC AUC; balanced accuracy; calibration. Split: Official evaluation paradigm; held-out subject/session. | Class imbalance; trial averaging must be identical |
| H03 | **SSVEP stimulus selection**. MOABB SSVEP datasets. [source 1](https://moabb.neurotechx.com/) | B / Low; P2 | Truth: Stimulus-frequency labels. Metrics: Accuracy; information transfer rate with explicit timing. Split: Official cross-session/subject protocols. | Stimulus timing and frequency metadata can be shortcuts |
| H04 | **EEG transfer under limited calibration**. BEETL. [source 1](https://beetl.ai/introduction) | B / Medium; P2 | Truth: Provided task labels. Metrics: Official competition metrics. Split: Original transfer learning tracks. | Historical challenge; evaluate locally if server unavailable |
| H05 | **Broad EEG model comparison**. NeuralBench-EEG Core / Full. [source 1](https://facebookresearch.github.io/neuroai/neuralbench/index.html) | B / Medium; P2 | Truth: Task-specific recorded labels. Metrics: Official per-task metrics; family-wise summary. Split: Official subject/session splits and adaptation modes. | Core is manageable subset; Full has large storage requirements |
| H06 | **EEG foundation model transfer roadmap**. OmniEEG-Bench. [source 1](https://arxiv.org/abs/2606.00815) | B / Medium; P2 | Truth: Dataset-specific signal/state/clinical/task labels. Metrics: Official metrics by task. Split: Official task cards and deployment settings. | Overlaps other EEG suites; do not count duplicates as independent evidence |
| H07 | **EEG scaling and robustness**. EEG-Arena. [source 1](https://eeg.fm/benchmarks/) | B / Medium; P2 | Truth: Dataset-specific labels. Metrics: Official task scores; channel/scaling protocols. Split: Official five evaluation protocols. | Dataset and model overlap with other EEG suites |
| H08 | **Sleep staging and sleep onset**. Sleep tasks in NeuralBench; 2026 foundation challenge. [source 1](https://facebookresearch.github.io/neuroai/neuralbench/index.html); [source 2](https://neural-interfaces26.github.io/) | B / Medium; P2 | Truth: Human sleep-stage labels. Metrics: Macro F1; Cohen kappa; onset error as track specifies. Split: Hold out subjects/nights; preserve temporal context. | PSG multimodal inputs must match; adjacent epoch leakage |
| H09 | **Seizure detection with useful event scoring**. SzCORE / CHB-MIT and supported corpora. [source 1](https://epilepsybenchmarks.com/framework/) | B / Medium; P2 | Truth: Expert event intervals. Metrics: Event sensitivity; false alarms/hour; latency. Split: Patient-held-out and causal event protocol. | Epoch accuracy can hide unacceptable false-alarm rates |
| H10 | **EEG abnormality, events, cognition and state**. Task subsets in NeuralBench / OmniEEG-Bench. [source 1](https://facebookresearch.github.io/neuroai/neuralbench/index.html); [source 2](https://arxiv.org/abs/2606.00815) | B / Medium; P2 | Truth: Expert/experimental labels depending on task. Metrics: Balanced accuracy/AUROC/F1 as task defines. Split: Patient/subject-held-out; hospital/site-held-out when available. | Abnormality is not disease diagnosis; demographic/site confounds |
| H11 | **Noninvasive speech decoding**. LibriBrain / PNPL 2025-2026. [source 1](https://libribrain.com/editions/2026/publications/) | B / Medium; P2 | Truth: Speech/phoneme/word timing and labels. Metrics: Official task classification and generalization scores. Split: Official single-subject and cross-subject tracks. | 2026 standings being verified; do not assume finalized winner |
| H12 | **Image/object retrieval from EEG/MEG**. THINGS EEG/MEG releases. [source 1](https://things-initiative.org/) | D / Medium; P2 | Truth: Image/concept identity and repeated trials. Metrics: Retrieval accuracy at fixed gallery; balanced classification. Split: Held-out subject and held-out concepts/images separately. | Closed image gallery is much easier than unrestricted reconstruction |
| H13 | **Neuromotor pose and typing from muscle signals**. emg 2 pose; related emg 2 qwerty resources. [source 1](https://github.com/facebookresearch/emg2pose) | B / Medium; P2 | Truth: Motion capture or keypress labels. Metrics: Official pose/typing errors; latency. Split: Official held-out users and conditions. | Peripheral interface extension; EMG is not a brain recording |
| H14 | **LFP oscillation and burst quantification**. Bycycle examples plus selected public LFP and synthetic controls. [source 1](https://github.com/bycycle-tools/bycycle); [source 2](https://about.dandiarchive.org/) | D / Medium; P2 | Truth: Injected known bursts; expert/proxy annotations for real events. Metrics: Burst event precision/recall; frequency/amplitude error; false positives. Split: Unseen recordings/noise profiles; lock event definition. | Oscillation/burst definitions are method dependent; real ground truth is limited |

### I. Human and mesoscopic neuroimaging

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| I01 | **Multimodal movie-to-fMRI encoding**. Algonauts 2025 / CNeuroMod. [source 1](https://algonautsproject.com/2025/challenge.html) | B / Medium; P2 | Truth: Measured held-out fMRI responses. Metrics: Official brain-response correlation and OOD score. Split: Official movie/subject split; account for HRF delay. | General features still need fitted brain alignment |
| I02 | **Image encoding/reconstruction from fMRI**. NSD / Algonauts 2023. [source 1](https://www.naturalscenesdataset.org/) | B/D / Medium; P2 | Truth: Stimulus identities and measured BOLD. Metrics: Encoding correlation; retrieval; reconstruction semantic and pixel metrics. Split: Official split; held-out images/subjects; gallery fixed. | NSD is a dataset; reconstruction needs a separately frozen protocol |
| I03 | **Human brain model alignment**. Brain-Score. [source 1](https://www.brain-score.org/) | B / Medium; P2 | Truth: Experimental neural/behavioral measurements. Metrics: Official noise-normalized predictivity and behavior scores. Split: Use benchmark-specific held-out stimulus split. | Brain similarity is distinct from useful raw-data analysis |
| I04 | **Cross-modal EEG/MEG/fMRI analysis**. Wakeman-Henson multimodal dataset. [source 1](https://www.nature.com/articles/sdata20151) | D / Medium; P2 | Truth: Stimulus labels; physiological recordings. Metrics: Decoding; cross-modal prediction; source-localization proxy. Split: Hold out participants and runs. | Source truth is not directly known; careful coregistration |
| I05 | **MRI reconstruction**. fastMRI brain. [source 1](https://fastmri.med.nyu.edu/) | B / High; P3 | Truth: Fully sampled/reference reconstructions. Metrics: Official SSIM/NMSE/PSNR with fixed masks. Split: Official patient/scan split and acceleration. | Natural-image generation without k-space consistency can invent anatomy |
| I06 | **Brain MRI lesion segmentation**. BraTS releases. [source 1](https://www.med.upenn.edu/cbica/brats/) | B / Medium; P3 | Truth: Expert tumor labels. Metrics: Dice; HD95; lesion-wise scores where required. Split: Use one named release and official subject split. | Clinical imaging extension beyond course; access rules vary by release |
| I07 | **fNIRS motor/hemodynamic decoding**. FRESH Motor dataset. [source 1](https://www.nemar.org/dataset/on005963) | D / Medium; P3 | Truth: Experimental event labels. Metrics: Balanced accuracy; held-out hemodynamic prediction. Split: Hold out participants/runs; define preprocessing. | Needs benchmark wrapper; hemodynamic lag and motion confounding |
| I08 | **Functional ultrasound analysis**. ConfUSIus collection. [source 1](https://registry.opendata.aws/confusius/) | D / High; P3 | Truth: Available task/region annotations vary. Metrics: Task decoding; response prediction; registration error on labeled subset. Split: Freeze one study and animal-held-out protocol. | Resource collection, not one ready-to-run benchmark |

### J. Anatomy, histology and connectomics

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| J01 | **EM neurite segmentation**. CREMI segmentation. [source 1](https://cremi.janelia.org/) | B / Medium; P2 | Truth: Expert instance labels. Metrics: Variation of information; Rand error; topology metrics. Split: Official volume split. | 2D masks alone do not preserve 3D neuron topology |
| J02 | **Synapse detection and partner identification**. CREMI synapse/connectivity categories. [source 1](https://cremi.janelia.org/) | B / Medium; P2 | Truth: Synapse and pre/post partner annotations. Metrics: Detection F1; partner-pair F1. Split: Official held-out volumes. | Detection and correct synaptic partners are different tasks |
| J03 | **3D neuron tracing and morphology**. BigNeuron gold 166 / DIADEM. [source 1](https://github.com/BigNeuron/Data/releases); [source 2](https://diadem.janelia.org/metric.html) | B / Medium; P2 | Truth: Gold/manual skeleton reconstructions. Metrics: DIADEM/topology score; spatial tracing error. Split: Held-out neurons, laboratories and morphologies. | Sparse manual traces are incomplete; topology matters |
| J04 | **Histology-to-atlas registration**. DeepSlice evaluation data. [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10514056/) | D / Medium; P2 | Truth: Expert alignment/landmarks. Metrics: Landmark error; region overlap; section orientation. Split: Hold out animals, stain and imaging site. | Expert alignment uncertainty; orientation mistakes can dominate |
| J05 | **Joint structure-function modeling**. MICrONS. [source 1](https://www.microns-explorer.org/) | D / High; P3 | Truth: Released proofread connectivity and activity. Metrics: Held-out connectivity/response prediction; tracing QC. Split: Held-out cells/volumes; freeze release and proofread status. | Evolving proofreading; adjacent neuron leakage; substantial data engineering |
| J06 | **Whole-brain neuron detection, identity and tracking**. WormID-Benchmark / WormND. [source 1](https://github.com/focolab/WormND) | B / Medium; P2 | Truth: Neuron positions, identities and tracks. Metrics: Detection F1; identity accuracy; tracking metrics. Split: Published cross-worm/cross-lab split. | Dense whole-brain labeling and worm posture variation |

### K. Cell types and molecular neuroscience

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| K01 | **Electrophysiological cell-type classification**. Allen Cell Types / Patch-seq resources. [source 1](https://brain-map.org/our-research/cell-types-taxonomies); [source 2](https://brain-map.org/support/documentation/documentation-cell-types-database) | D / Low; P2 | Truth: Published cell taxonomy labels. Metrics: Macro F1; hierarchical label accuracy; calibration. Split: Hold out cells/donors; define taxonomy level. | Taxonomy label uncertainty; donor and acquisition batch confounds |
| K02 | **Transcriptomic cell mapping and integration**. Allen Brain Cell Atlas plus scIB evaluation tools. [source 1](https://brain-map.org/our-research/cell-types-taxonomies); [source 2](https://scib.readthedocs.io/en/latest/) | D / Medium; P2 | Truth: Reference taxonomy and biological annotations. Metrics: Cell mapping F1; scIB biology/batch metrics. Split: Donor/site-held-out; preserve rare types. | Gene foundation models are domain-pretrained comparators; batch mixing alone is insufficient |
| K03 | **Molecular/pathology cohort analysis**. NeuroDiscoveryBench atlas/SEA-AD tasks. [source 1](https://github.com/allenai/neurodiscoverybench) | B / Low; P2 | Truth: Expert curated quantitative/text/figure answers. Metrics: Published rubric; numeric checks added where feasible. Split: Official task split; new donor analyses for stronger holdout. | Donor is the experimental unit; cells are not independent patient replicates |

### L. Mechanistic and statistical inference

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| L01 | **Functional connectivity recovery**. ChaLearn Connectomics Challenge. [source 1](https://connectomics.chalearn.org/help/data) | B / Medium; P2 | Truth: Known simulated connectivity. Metrics: AUROC and AUPRC; direction-specific recovery. Split: Official networks; unseen topology/noise. | Simulation connections do not establish causal connectivity in real recordings |
| L02 | **Biophysical parameter posterior inference**. sbi Hodgkin-Huxley example / Jaxley tasks. [source 1](https://sbi.readthedocs.io/en/latest/advanced_tutorials/21_diagnostics_misspecification_checks.html); [source 2](https://www.nature.com/articles/s41592-025-02895-w) | R / Medium; P3 | Truth: Known simulated parameters; multiple valid solutions. Metrics: Posterior predictive fit; coverage; calibration; simulation cost. Split: Unseen parameter seeds/stimuli; frozen priors. | Nonidentifiability makes single parameter error misleading |
| L03 | **Valid neural hypothesis testing**. IBL-agent genuine/null analysis tasks. [source 1](https://github.com/int-brain-lab/ibl-ai-agent); [source 2](https://www.internationalbrainlab.com/data) | D / Medium; P1 | Truth: Known randomized/null labels; expert analysis of genuine data. Metrics: False-positive rate; power; analysis validity; replication. Split: Blinded nulls; held-out mice; locked confirmatory analysis. | Naive permutation breaks trial history; significance shopping |
| L04 | **Point-process estimation and goodness of fit**. Proposed GLM/point-process task generator. [source 1](https://neurallatents.github.io/); [source 2](https://github.com/snel-repo/ComputationThroughDynamicsToolkit) | R / Low; P2 | Truth: Known generating process and held-out spikes. Metrics: Predictive log likelihood; time-rescaling calibration; interval coverage. Split: Unseen seeds/history kernels/covariates. | New benchmark requires tested generator and scorer; not an existing public suite |

### M. Experimental design and control

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| M01 | **Behavioral decision-model fitting**. IBL trial tables; Psych-101 cognitive tasks. [source 1](https://www.internationalbrainlab.com/data); [source 2](https://www.nature.com/articles/s41586-025-09215-4) | D / Medium; P2 | Truth: Recorded choices; synthetic recovery targets when added. Metrics: Held-out choice likelihood; parameter recovery on simulation. Split: Animal/participant-held-out; contiguous trial blocks. | Predicting choices is distinct from identifying a cognitive mechanism |
| M02 | **Adaptive experiment and stimulus design**. Proposed Jaxley/NeuroGym design environment. [source 1](https://www.nature.com/articles/s41592-025-02895-w); [source 2](https://github.com/neurogym/neurogym) | R / High; P3 | Truth: Known simulated system and experiment budget. Metrics: Information gain; prediction gain per trial; design regret. Split: Unseen simulated subjects; fixed budget and allowed actions. | Simulator results alone do not validate real biological interventions |
| M03 | **Closed-loop control policy evaluation**. NeuroGym task collection. [source 1](https://github.com/neurogym/neurogym) | D / Medium; P3 | Truth: Task rewards/targets; simulated feedback. Metrics: Success/reward; adaptation; real-time latency. Split: Held-out task variants and seeds. | Task collection requires a fixed suite; not evidence of real closed-loop BCI performance |

### N. Scientific analysis workflows

| ID | Task and resource | Readiness / effort | Truth and recommended evaluation | Main limitation |
|---|---|---|---|---|
| N01 | **End-to-end neuroscience data analysis QA**. NeuroDiscoveryBench. [source 1](https://github.com/allenai/neurodiscoverybench) | B / Low; P1 | Truth: Expert quantitative/text/figure answers. Metrics: Official scoring; numeric and statistical validity checks. Split: Freeze official version; separate raw/processed tracks. | Original tasks have public answers; model judge is fallible |
| N02 | **Agentic EEG workflow execution**. BrainAgent hierarchical benchmark. [source 1](https://arxiv.org/abs/2606.25400) | B* / Medium; P2 | Truth: Task completion and execution traces; output rubrics. Metrics: Completion rate plus independently checked scientific correctness. Split: Freeze toolset and tasks; confirm public task/data availability. | Paper located; complete reusable public release not independently confirmed |
| N03 | **Neuroimaging tool and training workflows**. NeuroDiscovery/NeuroClaw NeuroBench. [source 1](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html) | B / Medium; P2 | Truth: Task outputs, checks and rubric. Metrics: Executability; output validity; reproducibility; held-out predictive scores. Split: Paired with-skills/no-skills; freeze benchmark version. | Rubric-scored success differs from raw neural model accuracy; naming collisions |
| N04 | **Reproducing scientific analyses**. ScienceAgentBench neuroscience/EEG subset. [source 1](https://arxiv.org/abs/2410.05080) | B / Medium; P2 | Truth: Published reference results and task evaluators. Metrics: Official completion/output metric. Split: Freeze neuroscience subset and runtime budget. | Broad science benchmark; only relevant subset belongs in neuro score |
| N05 | **NWB data loading, units and reproducibility**. DANDI selected dandisets / IBL data. [source 1](https://about.dandiarchive.org/); [source 2](https://www.internationalbrainlab.com/data) | D / Low; P2 | Truth: Metadata invariants; known deterministic reference outputs. Metrics: Schema/units/timing correctness; reproducibility; QC issue recall. Split: Held-out dandisets/labs with locked answer files. | Archive is not benchmark; need curated cases and hidden answers |


## Deliverable use and unresolved checks

The workbook includes taxonomy, the task-resource catalog, prior work, and an unrun result template. Every result row starts as **Not run** and has no invented performance values. The JSON contains the same 90 catalog entries for future evaluation code. Before selecting a case for execution, confirm the specific dataset download, license, released labels/scorer, baseline checkpoint availability, and resource requirements, then freeze them in the run manifest.

The most useful next milestone is a working, independently checked evaluator for the six anchor tasks, followed by a small common-harness model comparison. Catalog completion and model evaluation are different milestones; this deliverable completes the first research map and proposes the protocol for the second.
