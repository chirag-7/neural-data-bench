# Neural Data Bench

**Traceable evidence and exploratory experiments on general coding models for neuroscience lab tasks.** Preview **0.8**, 30 October 2026. Course context: [Liam Paninski's Statistical Analysis of Neural Data](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/).

[Results explorer](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site) · [Current release and review](docs/release-v08.md) · [Results and limits](analysis/findings.md) · [Reproduce](docs/reproduce.md)

## Completed evidence

| Artifact | Current state |
|---|---|
| Active research map | 96 task–resource entries across 14 families; 18 further candidates archived with reasons; 114 historical entries preserved |
| First-submission panel | **21 task IDs**, 27 evaluation slices per model; 63 single-shot generated programs |
| First-submission executions | **81 attempts: 79 valid, 2 failures**; exact GPT-5.6 Sol, GPT-6 Sol, GPT-6.1 Sol |
| Audit artifacts | 162 model/reference records; 156 stored prediction records rescored; source/manifests, hashes, unchanged programs and generation provenance |
| H02 generation follow-up | Six fresh submissions, all strict-valid; three per model including the original, plus one train-only CV-selected specialist; kept outside original macro totals |
| Specialist evidence | MountainSort5, pyRiemann motor-imagery/xDAWN pipelines, YASA, SingleR and a source-inspired behavioral GLM; aligned archived StarDist, VASSI, Spikefinder and MRIQC predictions |
| Interface | Measured-first directory, category navigation, searchable tasks, graph/table controls; specialist names and values directly label horizontal lines |

Models **generate analysis code**, then saved programs train/predict locally. This is the T3 procedure, not native raw-signal comprehension or a full autonomous scientist. No Luna, open-weight, native image/video/world-model track or current-global-SOTA certification is included. **75 active entries remain unrun** (47 pending validation, 28 deferred). Representing 14 categories does not complete all their subfields. The source registry contains 201 associated URLs; this is a source inventory, not a count of fully reviewed papers.

[Candid progress assessment](docs/progress-assessment.md) · [H02 three-generation follow-up](experiments/H02/replication-v1/results.md)

## Why the latest review matters

- **Two new real-data endpoints:** SingleR leads all three Sol versions on donor-held-out cortical-layer transfer; all three beat a source-inspired GLM on mouse-held-out conditional choice prediction. [Exact scores, source checks and limits](docs/release-v08.md). Neither result establishes current global best.

- **Metric sensitivity:** GPT-6 nearly matches MountainSort5 on frozen per-GT-unit spike-sorting accuracy (0.940011 vs 0.940896). Counting all emitted spikes yields post-hoc event F1 **0.599751 vs 0.962060**, exposing excess spikes. Both views remain available; the original primary and macro scores are unchanged.
- **P300 replication:** three-attempt means are **0.752374 / 0.744027 / 0.784685**, versus train-only CV-selected xDAWN **0.778541**. All three GPT-6.1 attempts exceed this reference; minimum advantage is only 0.000754. Same dataset, retrospective follow-up, no global-superiority claim. Original endpoint below is preserved.
- **Original P300 experiment:** all 25 Brain Invaders 2012 people, 15 train/10 held-out. Person-equal ROC-AUC is **0.757195 /0.730548 /0.788537**, versus fixed xDAWN **0.761230**. Ten-person evaluation is stronger grouping depth than earlier pilots, but remains one public source and one generation.
- **Readability corrections:** current task-card/method headers no longer say “not evaluated” for measured tasks. Historical status remains dated. Methodology is consolidated; specialists, ordinary baselines and post-hoc metrics are visually distinct.
- **Mixed model progress:** GPT-6.1 improves on GPT-6 in 18 of 25 progress slices, declines in 6 and fails in 1; family-equal directional improvement fraction 0.615. This includes selected synthetic/semisynthetic tasks and supports no causal scaling claim.

[Full native-score table and caveats](analysis/findings.md). Native metric magnitudes are never averaged across unrelated tasks. Test-selected envelopes, historical/pretrained/local specialists, conventional references and failures have explicit policies and denominators.

## Navigate by category

| Family | Active entries | Measured IDs | Pending validation | Deferred |
|---|---:|---|---:|---:|
| [A](benchmarks/A/README.md) Behavior, kinematics and vocalization | 16 | A09, A14 | 11 | 3 |
| [B](benchmarks/B/README.md) Extracellular signal acquisition | 8 | B01 | 7 | 0 |
| [C](benchmarks/C/README.md) Calcium imaging and photometry | 9 | C05 | 8 | 0 |
| [D](benchmarks/D/README.md) Voltage, intracellular and dendrites | 3 | D02 | 0 | 2 |
| [E](benchmarks/E/README.md) Population activity and dynamics | 6 | E01 | 5 | 0 |
| [F](benchmarks/F/README.md) Sensory and behavioral encoding | 5 | F04 | 2 | 2 |
| [G](benchmarks/G/README.md) Intracortical BCI | 3 | G01 | 0 | 2 |
| [H](benchmarks/H/README.md) EEG, MEG, field signals and peripheral interfaces | 14 | H01, H02, H08, H16 | 1 | 9 |
| [I](benchmarks/I/README.md) Human and mesoscopic neuroimaging | 6 | I07, I10 | 0 | 4 |
| [J](benchmarks/J/README.md) Anatomy, histology and connectomics | 9 | J08 | 4 | 4 |
| [K](benchmarks/K/README.md) Cell types and molecular neuroscience | 5 | K01, K04 | 3 | 0 |
| [L](benchmarks/L/README.md) Mechanistic and statistical inference | 5 | L04 | 3 | 1 |
| [M](benchmarks/M/README.md) Experimental design and control | 4 | M01, M04 | 1 | 1 |
| [N](benchmarks/N/README.md) Scientific analysis workflows | 3 | N05 | 2 | 0 |

[Taxonomy](docs/taxonomy.md) · [Coverage and gaps](docs/coverage-matrix.md) · [Methodology](docs/methodology.md) · [Prior work](docs/prior-work.md) · [Macro policy](docs/macro-analysis-plan.md)

## Audit a result

1. Start at `benchmarks/<family>/<ID>/`: current overview, data, sources, proposed methods and actual worklog.
2. Follow `experiments/<ID>/`: frozen contract, source/input hashes, exact submissions, generation provenance and source-specific execution details. E01's extra sources reuse unchanged code.
3. Inspect [central JSONL](results/measurements.jsonl), [CSV](results/measurements.csv), [predictions](results/predictions/), [rescoring checks](analysis/validation-expansion.json), and [derived summaries](analysis/summary.json).
4. Check [admissions](registry/admission-decisions.json), [exclusions](registry/excluded-candidates.json), [sources](literature/sources.json) and [current-best ledger](registry/current-best.json). Unknown current global best remains unknown.

This is a bounded feasibility study, not an exhaustive literature review or paper-ready all-neuroscience conclusion. Closest prior work includes BrainWideBench, NeuralBench, NeuroDiscoveryBench/NeuroClaw, SciVid and EEGAgentBench; novelty needs explicit comparison. A paper requires independent sources, repeated generations, matched strong specialists, prospective selection and external scientific review.

Code/documentation MIT; third-party artifacts retain their original terms, including the H02 author code's retained license. Raw caches and supplied lecture PDFs are not redistributed. Repository and hosted site preserve their private audiences.
