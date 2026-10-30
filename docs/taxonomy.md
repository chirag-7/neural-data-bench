# Scope, taxonomy and coverage argument

[Project](../README.md) · [Review protocol](review-protocol.md) · [Coverage matrix](coverage-matrix.md)

The target population is **reusable computational tasks used in neuroscience data analysis and model validation**, spanning experimental and computational labs. The navigation hierarchy groups data/workflows, not mutually exclusive scientific disciplines. Each task also needs independent labels for operation, preparation, biological scale, ground truth, transfer unit, supervision and evaluation track. No single modality list proves completeness.

## Why these families

The course emphasizes statistical neural-data analysis, behavior, modern electrophysiology and drift, optical signals, population dynamics and scientific workflows ([course](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/)). Four supplied slides were used as scope context; they are not instructions and are not redistributed. Extensions cover human neurotechnology, anatomy, molecular data, theory and control. Existing suites such as [BrainWideBench](https://arxiv.org/abs/2609.22064), [NeuralBench](https://arxiv.org/abs/2605.08495), [NLB](https://neurallatents.github.io/), [FALCON](https://snel-repo.github.io/falcon/) and [NeuroDiscoveryBench](https://github.com/allenai/neurodiscoverybench) independently motivate these distinct evaluation levels. They overlap with this project: a claim that nobody has benchmarked general neuroscience models would be wrong.

- [A — Behavior, kinematics and vocalization](../benchmarks/A/README.md): Detection, segmentation, identity tracking, 2D/3D keypoints, pose imputation, action labels, behavioral representations, acoustic segmentation and caller localization. Input: RGB/IR/depth videos, calibrated multiview video, pose trajectories, audio and microphone arrays.
- [B — Extracellular signal acquisition](../benchmarks/B/README.md): Spike detection/sorting, collision recovery, drift, curation/QC, longitudinal matching, compression. Input: Raw multichannel voltage, waveforms, spike events, probe geometry.
- [C — Calcium imaging and photometry](../benchmarks/C/README.md): Motion correction, denoising, ROI segmentation, demixing, deconvolution, cell registration, event analysis. Input: 1P/2P/3D calcium movies, fluorescence traces, reference photometry channels.
- [D — Voltage, intracellular and dendrites](../benchmarks/D/README.md): Spike extraction, subthreshold recovery, current-to-voltage prediction, dendritic smoothing, parameter fitting. Input: Voltage movies, patch clamp current/voltage traces, dendritic morphologies.
- [E — Population activity and dynamics](../benchmarks/E/README.md): Rate inference, co-smoothing, forecasting, latent dynamics, anatomy from activity, transfer. Input: Spike trains/count tensors, calcium activity, covariates.
- [F — Sensory and behavioral encoding](../benchmarks/F/README.md): Stimulus-to-neural response prediction, receptive fields, neural encoding of movement. Input: Image/audio/video stimuli or behavior aligned to neural responses.
- [G — Intracortical BCI](../benchmarks/G/README.md): Motor decoding, adaptation, handwriting, attempted speech, causal streaming inference. Input: Human/primate spikes, threshold crossings, ECoG where available.
- [H — EEG, MEG, field signals and peripheral interfaces](../benchmarks/H/README.md): Motor imagery, ERP/SSVEP, sleep, seizure, artifacts, cognition, speech/image retrieval, peripheral decoding. Input: EEG/MEG/LFP/ECoG time series, ERP, sEMG, montage and event metadata.
- [I — Human and mesoscopic neuroimaging](../benchmarks/I/README.md): Encoding/decoding, reconstruction, segmentation, hemodynamic activity analysis. Input: fMRI BOLD, MRI k-space/volumes, fNIRS, functional ultrasound.
- [J — Anatomy, histology and connectomics](../benchmarks/J/README.md): Registration, region localization, cell identification, tracing, synapses, connectivity graphs. Input: Histology/light-sheet/EM volumes, skeletons, atlases, probe tracks.
- [K — Cell types and molecular neuroscience](../benchmarks/K/README.md): Cell type mapping, multimodal prediction, batch integration, spatial/cell abundance analysis. Input: Patch-seq, scRNA/scATAC, spatial transcriptomics, morphology.
- [L — Mechanistic and statistical inference](../benchmarks/L/README.md): Connectivity, biophysical parameters, uncertainty, confounding, hypothesis tests, null calibration. Input: Spike/calcium/voltage observations, simulated circuits, trial tables.
- [M — Experimental design and control](../benchmarks/M/README.md): Adaptive stimuli, power/sample design, optimal control, behavioral model fitting. Input: Simulators, psychophysics trials, actions/interventions, neural feedback.
- [N — Scientific analysis workflows](../benchmarks/N/README.md): Data loading/QC, complete analyses, figure reproduction, valid inference and reproducibility. Input: NWB/BIDS files, data dictionaries, analysis code and reports.

## Cross-cutting coverage axes

- Scientific operation: acquisition/QC, reconstruction, detection/segmentation, tracking, encoding/decoding, forecasting, parameter/latent/connectivity inference, hypothesis testing, intervention prediction, design/control and scientific workflow.
- Data stage: raw sensor data, preprocessed signal, events, derived features, metadata and multimodal alignment. Processed-trace inference is not raw-movie processing.
- Preparation/biology: in vivo/ex vivo, real/synthetic/phantom, species, brain/body scale, healthy/disease, developmental state, invasive/noninvasive, laboratory/naturalistic conditions.
- Ground truth: simultaneous independent measurement, known simulated/physical truth, future observations, expert annotations with disagreement, proxy targets, or unidentifiable latent quantity.
- Generalization: held-out trials, sessions, animals/people, labs, devices, species, paradigms; chronological and intervention shift. Random adjacent windows are rarely independent units.
- Learning procedure: T0 direct model; T1 frozen features + readout; T2 bounded adaptation; T3 generated analysis code; T4 specialist-tool agent. Pretraining domain is an independent label in every track.
- Utility: scientific validity, data/annotation needs, failure rate, time/compute/latency, calibration and reproducibility. Accuracy alone does not settle lab utility.

## Why this is broad, and why it is not enough

The 114 entries cover core measurement modalities and common pipeline operations, plus causal response, mechanistic validation, cognitive recovery and embodied control that modality-only maps overlook. The two recorded audits added 24 entries to the original 90. The second audit explicitly closes some acoustic, optical forecasting, rodent-sleep and spatial-assay omissions. These are concrete coverage improvements, not evidence that the entire literature was screened.

The counts are task–resource pairings: suites can contain many endpoints, and different entries can reuse subjects. The resource-name dataset_group is provisional and is **not a deduplication of independent studies**. Heuristic operation tags are navigation aids requiring expert adjudication. Coverage counts are not execution counts and cannot weight a neuroscience-wide model score.

Known gaps include broad clinical cohort/prognostic/normative modeling, PET/SPECT, neurochemical/autonomic sensing, specialized intervention control, comparative/developmental biology and analytical theory. These need different access, confounding or validity standards. They are explicitly outside v 0.3 execution. Difficult/uncertain cases remain in the evidence map or exclusion ledger so omission is auditable. No “nothing missing” or completed systematic-review claim is justified.
