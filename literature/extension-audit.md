# Bounded literature extension and coverage review

Review date: 2026-10-30. Input: v0.2 evidence map, 102 task-resource entries. This extension recommends **12 additional task-resource entries** and logs **6 scope/execution exclusions**. It does not certify universal coverage, ready-to-run status or current SOTA. No new model scores are reported.

## High-value additions

### A15 — Animal vocalization event segmentation and syllable labeling
**Resource:** DAS multi-species annotated acoustic datasets. **Readiness:** B (evidence-map classification; executable admission pending).

Adds acoustic communication used by social/ethology labs; video action labels do not test it.
Input/truth: Single/multi-channel raw audio and human annotations; Manual acoustic events/segments.
Proposed score and split: Event precision/recall/F1; onset/offset error; published match tolerance. Published splits first; additional held-out recording/animal, never random adjacent audio crops.
References: DAS; TweetyNet; WhisperSeg (separate domain-adapted pretrained comparator). General route: General audio features/readout or bounded code synthesis; audio-native foundation model.
Critical limit: Ultrasound sample rates exceed speech frontends; species and segment matching differ; tune thresholds only on validation. Rights: Not independently reviewed.
Sources: [source 1](https://elifesciences.org/articles/68837), [source 2](https://data.goettingen-research-online.de/dataverse/das), [source 3](https://janclemenslab.org/das/), [source 4](https://github.com/nianlonggu/WhisperSeg)

### A16 — Caller localization and vocalization attribution
**Resource:** Vocal Call Locator (VCL) Benchmark. **Readiness:** B (evidence-map classification; executable admission pending).

Separates who emitted a call from detecting that a call occurred.
Input/truth: Synchronized multi-microphone audio with overhead video-derived source positions; 2D source positions, including controlled speaker conditions.
Proposed score and split: Localization error; published uncertainty/calibration and attribution endpoint. Official recording/condition split; group all snippets from same sound and session.
References: VCL localization models; classical sound source localization. General route: Generic audio model or code-agent localization under fixed calibration information.
Critical limit: Speaker-ground-truth and freely moving animals are distinct conditions; paper revisions report differing event totals, so pin release. Rights: Not independently reviewed.
Sources: [source 1](https://proceedings.nips.cc/paper_files/paper/2024/hash/c00d37d6b04d73b870b963a4d70051c1-Abstract-Datasets_and_Benchmarks_Track.html), [source 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC11430026/), [source 3](https://github.com/neurostatslab/vocalocator)

### E06 — Whole-brain neural activity forecasting
**Resource:** ZAPBench (ICLR 2025). **Readiness:** B (evidence-map classification; executable admission pending).

Important omitted whole-brain forecasting resource and a concrete world/video-model task.
Input/truth: Larval zebrafish light-sheet volumes and extracted cellular traces; Future measured calcium activity.
Proposed score and split: Official forecasting losses at fixed horizons and stimulus conditions; maintain trace/video tracks. Official temporal/stimulus-condition splits, including held-out condition.
References: Published naive, time-series and volumetric video baselines. General route: General time-series/world/video models; code agents in separate track.
Critical limit: One brain cannot establish cross-animal generalization; 70k neurons do not equal 70k independent subjects; anatomical pairing was future-facing in original paper. Rights: CC BY 4.0 explicitly stated in official dataset README.
Sources: [source 1](https://google-research.github.io/zapbench/), [source 2](https://arxiv.org/abs/2503.02618), [source 3](https://zapbench-release.storage.googleapis.com/volumes/README.html)

### H17 — Cross-laboratory rodent sleep staging
**Resource:** Mouse Sleep Staging Validation dataset (MSSV), OpenNeuro ds006366. **Readiness:** D (evidence-map classification; executable admission pending).

Adds animal sleep rather than assuming human EEG staging covers laboratory mouse sleep.
Input/truth: Mouse EEG/EMG, expert stage annotations; Expert sleep scores from 92 healthy mice across five labs.
Proposed score and split: Macro-F1, balanced accuracy, per-stage recall and transition errors. Held-out mouse and held-out laboratory; keep whole light/dark recordings grouped.
References: Published mouse sleep staging methods; simple spectral-feature baseline. General route: General time-series features or code-generated classifier.
Critical limit: Rodent stages, epoch lengths and recording setups must be specified; human sleep foundation-model scores cannot transfer directly. Rights: CC0 shown by NEMAR; original dataset version must be pinned separately from mirror.
Sources: [source 1](https://nemar.org/dataset/on006366), [source 2](https://doi.org/10.18112/openneuro.ds006366.v1.0.1)

### H18 — Sleep microevent detection
**Resource:** DREAMS microevent annotations; MODA consensus as a separately versioned extension. **Readiness:** B (evidence-map classification; executable admission pending).

Sleep staging does not cover spindle/K-complex microevents needed in sleep and memory labs.
Input/truth: Human EEG with spindle and K-complex intervals; Individual expert labels with disagreement.
Proposed score and split: Event F1 at fixed IoU/tolerance; temporal error; per-expert and consensus results separately. Held-out subject; freeze usable annotation intervals and scorer.
References: SUMO/SUMOv2; published spindle detector baselines. General route: General signal/audio feature or code-agent event detector.
Critical limit: DREAMS repository explicitly warns expert 1 spindle counts stop after 1000 seconds; censor unannotated periods rather than scoring them negative; MODA and DREAMS are not interchangeable. Rights: Not independently reviewed.
Sources: [source 1](https://zenodo.org/records/2650142), [source 2](https://www.nature.com/articles/s41598-026-53891-9), [source 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC10762090/)

### H19 — Real physiological artifact detection and type identification
**Resource:** DREAMS Artifacts database. **Readiness:** D (evidence-map classification; executable admission pending).

Complements H16 repair with detection on real artifact labels and metadata-aware exclusion.
Input/truth: PSG excerpts with expert artifact labels; Expert temporal annotations in 20 fifteen-minute excerpts.
Proposed score and split: Event/timewise macro-F1, artifact-type confusion, clean-signal retention. Group by source recording/person; validation threshold selection only.
References: Signal-processing detectors; declared artifact classification baseline. General route: Generic signal classifier or code agent.
Critical limit: Small single-annotator corpus; do not confuse real artifact detection with EEGdenoiseNet semi-synthetic signal repair. Rights: Not independently reviewed.
Sources: [source 1](https://zenodo.org/records/2650142)

### J07 — Multi-neuron instance segmentation in light microscopy
**Resource:** FISBe / FlyLight Instance Segmentation Benchmark. **Readiness:** B (evidence-map classification; executable admission pending).

EM connectomics and isolated-neuron tracing do not cover dense multicolor light-microscopy disentangling.
Input/truth: 3D multicolor fruit-fly neuronal microscopy volumes; Expert pixel-wise neuron instances.
Proposed score and split: Official S ranking score; avF1, coverage, false merges/splits and clDice. Official image split; completely and partly labeled images need separate valid-mask policy.
References: PatchPerPix; flood-filling networks; color clustering. General route: General vision segmentation backbone; 3D generic model; code-agent pipeline.
Critical limit: Thin interwoven neurites require topology-sensitive scoring; pixel Dice alone insufficient; full dataset ~21.6 GB. Rights: CC BY 4.0 on dataset record.
Sources: [source 1](https://kainmueller-lab.github.io/fisbe/), [source 2](https://zenodo.org/records/10875063), [source 3](https://github.com/Kainmueller-Lab/evaluate-instance-segmentation)

### J08 — Fluorescent synaptic puncta segmentation and quantification
**Resource:** SynAPSeg training and multi-rater benchmark datasets. **Readiness:** B (evidence-map classification; executable admission pending).

Adds light-microscopy synaptic protein quantification beyond EM synapse detection.
Input/truth: 2D/3D confocal synaptic marker images; Pixel-wise instance annotations; five raters for three held-out benchmark images.
Proposed score and split: Object F1/IoU with declared matching; counts/density, centroid and boundary error; inter-rater range. Keep original whole benchmark images held out; never mix training 3D slices into test.
References: Published custom StarDist and Cellpose comparisons. General route: Generic microscopy/vision segmentation model; bounded code agent.
Critical limit: Tiny benchmark image count limits independent sampling; synaptic puncta are marker-based proxies for synapses; data license field was not resolved in rendered record. Rights: Repository code BSD-3-Clause; dataset license must be independently resolved before redistribution.
Sources: [source 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC13432752/), [source 2](https://github.com/pascalschamber/SynAPSeg), [source 3](https://zenodo.org/records/18988899)

### J09 — Multiscale X-ray brain region and microstructure classification
**Resource:** MTNeuro. **Readiness:** B (evidence-map classification; executable admission pending).

Adds X-ray mesoscopic anatomy and vasculature/cell/axon operations missing from current modality map.
Input/truth: Mouse brain X-ray microtomography with regional and pixel labels; Brain-region and cell/axon/vasculature labels.
Proposed score and split: Published region-classification accuracy and semantic segmentation metrics, reported as separate endpoints. Official task splits; contiguous volume blocks must not leak across train/test.
References: Published supervised and self-supervised 2D/3D baselines. General route: Generic vision embeddings/readout or 3D segmentation.
Critical limit: Same underlying sample across endpoints; count shared dataset once for macro independence; X-ray contrasts differ from EM/fluorescence. Rights: MIT software; CC BY 4.0 image dataset on project page.
Sources: [source 1](https://mtneuro.github.io/), [source 2](https://github.com/MTNeuro/MTNeuro)

### K04 — Spatial cortical-domain assignment
**Resource:** spatialLIBD DLPFC cortical-layer annotations. **Readiness:** D (evidence-map classification; executable admission pending).

Cell-type transfer/integration does not cover spatial laminar domain recovery.
Input/truth: Human DLPFC Visium gene counts, spot positions and histology; Expert layer/white-matter annotation informed by cytoarchitecture and marker genes.
Proposed score and split: ARI/NMI and spatial boundary metrics; matched-label accuracy only with explicit mapping policy. Hold out donor, then section; adjacent sections from same donor stay grouped.
References: Published spatial clustering methods; simple non-spatial clustering baseline. General route: Generic tabular/spatial model or code-generated pipeline.
Critical limit: Only three original donors; labels partially derived from expression, limiting independence; specify whether histology is available to each method. Rights: Not independently reviewed.
Sources: [source 1](https://research.libd.org/spatialLIBD/), [source 2](https://github.com/LieberInstitute/spatialLIBD), [source 3](https://doi.org/10.1038/s42003-024-07001-y)

### K05 — Bulk brain transcriptome cellular deconvolution
**Resource:** Human DLPFC multi-assay deconvolution benchmark / DeconvoBuddies. **Readiness:** B (evidence-map classification; executable admission pending).

Adds tissue mixture estimation against an orthogonal assay, beyond labeling single cells.
Input/truth: Bulk RNA-seq, reference snRNA-seq and orthogonal RNAScope/IF fractions; Cell fractions estimated by orthogonal RNAScope/IF from matched tissue blocks.
Proposed score and split: Per-type correlation and absolute/compositional error; donor-grouped uncertainty. Hold out donor/tissue block; RNA extraction/library technical variants stay together.
References: Six published algorithms including Bisque and hspe; reproduce exact reference/marker policy. General route: General constrained regression/tabular method; code agent.
Critical limit: Adjacent-section proxy truth has measurement error; 110 RNA-seq samples do not imply 110 independent donors; same DLPFC resource family overlaps K04. Rights: Not independently reviewed.
Sources: [source 1](https://doi.org/10.1186/s13059-025-03552-3), [source 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC11978107/), [source 3](https://github.com/LieberInstitute/Human_DLPFC_Deconvolution), [source 4](https://research.libd.org/DeconvoBuddies/reference/fetch_deconvo_data.html)

### K06 — Extracellular cell-type inference from ground-truth cell metrics
**Resource:** CellExplorer ground-truth cell metrics. **Readiness:** D (evidence-map classification; executable admission pending).

Patch-seq intracellular type inference does not cover extracellular deployment from ground-truth cell metrics.
Input/truth: Waveform/firing metrics and optotagged/identified cell classes; Curated PV, SST, pyramidal, axo-axonic, VGAT and VIP identities.
Proposed score and split: Macro-F1, class-balanced accuracy, calibration; hierarchical labels if classes overlap. Hold out contributing lab/animal/session; preserve provenance and avoid waveform windows as independent samples.
References: CellExplorer feature-based classification; declared supervised baseline. General route: Generic tabular estimator or code agent.
Critical limit: Optotagging can include indirect responses; class labels are uneven and partly nested; small class counts and uncertain raw-data provenance need inspection. Rights: Not independently reviewed.
Sources: [source 1](https://cellexplorer.org/publicdata/ground-truth-data/), [source 2](https://cellexplorer.org/tutorials/ground-truth-tutorial/), [source 3](https://alleninstitute.github.io/openscope_databook/optotagging/)

## Screening decisions and intentional blanks

- **X-EXT-01 OpenBHB age prediction/debiasing: retain scope boundary; exclude immediate execution.** Strong normative/developmental MRI benchmark, but exact IEEE Dataport access, license and release/split not verified; do not replace original data with a convenient other cohort. [source](https://github.com/baobablab/bhb/blob/gh-pages/dataset.md) [source](https://github.com/Duplums/SMLvsDL)
- **X-EXT-02 DARELA dopamine release/reuptake models: exclude immediate empirical benchmark.** Verified mechanistic code exists; a pinned raw FSCV dataset, independent concentration labels and standard test split/scorer were not established here. Could support explicitly synthetic parameter-recovery research later. [source](https://github.com/DSulzerLab/DARELA) [source](https://doi.org/10.1093/pnasnexus/pgad044)
- **X-EXT-03 SPARC autonomic/peripheral neuroscience portal: exclude portal as benchmark.** Open PNS/organ physiology data clearly exists, but portal-level inclusion is not an executable endpoint. Select a specific licensed dataset with known intervention/input and outcome, then define protocol before admitting it. [source](https://sparc.science/) [source](https://registry.opendata.aws/sparc/)
- **X-EXT-04 Biodenoising validation: exclude immediate suite.** Useful 62-pair animal-audio denoising task, but record limits use to educational/noncommercial purposes and mixture provenance must be reviewed. Audio denoising is lower priority than lab-specific caller attribution and segmentation. [source](https://zenodo.org/records/13736465)
- **X-EXT-05 CogBench (Coda-Forno et al. 2024): related work; exclude lab-analysis leaderboard.** Phenotypes an LLM acting as an experimental subject across seven psychology experiments. This differs from analyzing neural data or recovering human cognitive parameters. It is useful prior art for multilevel model-family comparisons. [source](https://proceedings.mlr.press/v235/coda-forno24a.html)
- **X-EXT-06 Generic proteomics / protein structure tasks: out of operational scope until neuroscience-specific endpoint selected.** No sufficiently scoped, easy-to-reuse neural proteomics benchmark was confirmed in this bounded audit. SynAPSeg covers protein-marker puncta imagery, not the entire proteomics perspective. Do not treat it as filling that gap. 

## Closest umbrella work and cautious novelty statement

**BrainWideBench** already addresses fragmented neural evaluation with three suites (behavior, dynamics and anatomy) over IBL Neuropixels recordings. Its breadth within a shared data ecosystem is strong prior art, so this project cannot claim to introduce multi-task neural benchmarking. The additional contribution here would be a cross-modality evidence map and explicitly separated generalist evaluation tracks across acquisition, anatomy, modeling and workflows. [Official IBL overview](https://www.iblcore.org/resources/benchmarking/ibl-brainwidebench/).
**NeuralBench** provides broad neurophysiology evaluation infrastructure and shared handling of tasks/datasets; it is closer to a reusable numerical modeling suite than a literature-only survey. A new observatory should reuse its exact evaluation definitions where suitable rather than silently inventing near-duplicates. [Official docs](https://facebookresearch.github.io/neuroai/neuralbench/index.html).
**NeuroDiscoveryBench** is direct prior art for evaluating general agents on practical neuroscience workflows. The novelty must therefore be a controlled comparison of *different assistance/adaptation tracks* and *matched specialist baselines*, with source/data/harness provenance, not the claim that general agents have never been evaluated in neuroscience. [Official repository](https://github.com/allenai/neurodiscoverybench).
**ZAPBench, MTNeuro, VCL and DAS** demonstrate that specialized benchmark design already spans whole-brain dynamics, multiscale anatomy and acoustic social behavior. Their official tasks should enter this registry as reused protocols. **WhisperSeg** is particularly important: it transfers a generally pretrained speech transformer into animal segmentation, but domain fine-tuning makes it an *adapted general backbone*, not an off-the-shelf zero-shot baseline. [WhisperSeg code](https://github.com/nianlonggu/WhisperSeg).
**CogBench** evaluates LLM cognitive phenotypes, which is related but distinct from neuroscience data analysis. Its multilevel treatment of model-family dependence is relevant to macro analyses. **Centaur/Psych-101**, already mapped in M01, also makes a blanket novelty claim about general models predicting cognition untenable. [CogBench](https://proceedings.mlr.press/v235/coda-forno24a.html), [Centaur primary record](https://pubmed.ncbi.nlm.nih.gov/40604288/).

## What a defensible completeness argument can say

The modality taxonomy is a navigation device, not a proof of completeness. Cross it with scientific operation (QC, detection/reconstruction, encoding/decoding, forecasting, statistical/mechanistic inference, intervention, control, reproducibility), preparation/species, truth type and transfer axis. The present additions repair visible gaps in acoustic behavior, whole-brain optical forecasting, rodent sleep, microevents, X-ray anatomy and spatial molecular inference. They do not close neural proteomics, autonomic organ control, clinical prognosis or every mechanistic theory question.
Paper-level scope should be **auditable representative tasks with accessible data and objective scores**. Keep the broad registry distinct from the executable suite; exclude unclear downloads/rights/scorers from the latter without erasing their exclusion records. Obtain expert review in behavior, experimental neurophysiology, human imaging and computational theory before claiming field-level adequacy. Resource counts are not a diversity metric: several tasks share DLPFC tissue, DREAMS recordings or one zebrafish.

## Evidence-to-execution gate

Every new entry above still requires: pin version; verify rights and byte access; acquire and hash input/labels separately; inspect grouping identifiers; specify input/preprocessing/adaptation budget; freeze scorer; reproduce a baseline; then freeze the test slice before general-model calls. Published baselines are not automatically current best. Small image or subject counts must remain visible.

## Actual search log

The exact search queries below were run through the web search tool on the review date. Candidate source pages, papers, code and availability statements were opened where listed above. Queries yielding no usable candidate remain in the log. This is a gap audit search record, not a PRISMA flow or exhaustive result export. One oversized VCL PDF could not be fetched; its primary PMC manuscript and proceedings page were located instead. A guessed DAS tutorial path failed; the official navigation resolved the correct tutorial.

- EXT-Q01 (2026-10-30): `DAS deep audio segmenter benchmark animal vocalizations annotated dataset eLife`
- EXT-Q02 (2026-10-30): `VocalBench benchmark animal vocalization dataset machine learning`
- EXT-Q03 (2026-10-30): `FSCAV dopamine FSCV benchmark dataset DeepLabCut deep learning voltammetry neuroscience open data`
- EXT-Q04 (2026-10-30): `SPARC benchmark autonomic neuroscience datasets ECG respiration open`
- EXT-Q05 (2026-10-30): `FSCV benchmark dopamine concentration dataset machine learning public GitHub voltammetry`
- EXT-Q06 (2026-10-30): `optoelectrophysiology perturbation benchmark dataset causal neural Neuropixels open IBL`
- EXT-Q07 (2026-10-30): `sleep animal sleep staging benchmark dataset SleepSEEG neuroscience open dataset`
- EXT-Q08 (2026-10-30): `spatial transcriptomics neuroscience benchmark cell segmentation MERFISH challenge dataset`
- EXT-Q09 (2026-10-30): `FISBe dataset github neuron light microscopy benchmark instances`
- EXT-Q10 (2026-10-30): `sleep spindle detection benchmark DREAMS MODA dataset expert labels official`
- EXT-Q11 (2026-10-30): `high frequency oscillation detection benchmark HFO challenge dataset github open`
- EXT-Q12 (2026-10-30): `DLPFC spatial transcriptomics benchmark spatialLIBD cortical layers dataset Maynard 2021`
- EXT-Q13 (2026-10-30): `neuroscience open dataset optogenetic perturbation prediction benchmark CEBRA ZAPBench`
- EXT-Q14 (2026-10-30): `ZAPBench zebrafish activity prediction benchmark perturbation dataset`
- EXT-Q15 (2026-10-30): `FSCV machine learning concentration prediction dataset github voltammetry dopamine serotonin benchmark`
- EXT-Q16 (2026-10-30): `spike optotagging benchmark ground truth dataset cell type classification Allen visual coding`
- EXT-Q17 (2026-10-30): `mouse ultrasound sound source localization benchmark dataset SLIM NeurIPS 2024 dataset`
- EXT-Q18 (2026-10-30): `WhisperSeg animal vocalization segmentation benchmark github datasets`
- EXT-Q19 (2026-10-30): `cognitive computational neuroscience benchmark tasks psychological modeling CogBench Psych101 benchmark`
- EXT-Q20 (2026-10-30): `neuroscience benchmark proteomics synapse image dataset segmentation SynapseNet`
- EXT-Q21 (2026-10-30): `OpenBHB brain age benchmark github dataset access 5000`
- EXT-Q22 (2026-10-30): `Benchmark Cellular Deconvolution Methods Multi-Assay Reference Dataset Postmortem Human Prefrontal Cortex data github`
- EXT-Q23 (2026-10-30): `Mouse Sleep Staging Validation dataset MSSV expert five laboratories paper benchmark`
- EXT-Q24 (2026-10-30): `Vocal Call Locator benchmark github download dataset`
- EXT-Q25 (2026-10-30): `"VCL" "Benchmark" "github" Peterson Tanelus`
- EXT-Q26 (2026-10-30): `"MODA" "sleep" "Zenodo" dataset Lacourse`
- EXT-Q27 (2026-10-30): `"Vocal Call Locator" dataset download`
- EXT-Q28 (2026-10-30): `"Vocal Call Locator" "github.com"`
- EXT-Q29 (2026-10-30): `"DAS" "data.goettingen-research-online.de/dataverse/das"`
- EXT-Q30 (2026-10-30): `"DeconvoBuddies" "Human_DLPFC_Deconvolution"`
