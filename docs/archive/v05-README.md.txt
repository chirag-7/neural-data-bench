# Neural Data Bench

**A traceable evidence map and exploratory evaluation of general coding models on neuroscience lab tasks.** Research preview **0.5**, 30 October 2026. Course context: [Liam Paninski's Statistical Analysis of Neural Data](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/).

[Interactive observatory](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site) · [Release and main plan](docs/release-v05.md) · [Results](analysis/findings.md) · [Reproduce](docs/reproduce.md)

## Completed evidence

| Artifact | Current state |
|---|---|
| Research map | 96 active task–resource pairings across 14 families; 18 further candidates archived with reactivation criteria; 114 historical entries preserved |
| Measured panel | 18 task IDs across all 14 families; 24 evaluation slices per model; 54 single-shot generated programs |
| Executions | 72 model–slice attempts: 70 numerically valid, 2 failures; 147 model/reference records; 141 stored predictions rescored |
| General models | Exact requested GPT-5.6 Sol, GPT-6 Sol, GPT-6.1 Sol; no Luna |
| Specialists | MountainSort5, pyRiemann, YASA; archived StarDist, VASSI, Spikefinder and MRIQC predictions; conventional baselines separately labeled |
| Audit trail | Frozen contracts, source/license evidence, hashes, unchanged submissions, predictions, failures, usage/tool counts and scorer checks |
| Interface | Measured benchmark directory, category sidebar, benchmark selector, graph/table views, named specialist overlays in both line and bar plots |

This remains an exploratory T3 code-generation-plus-fitting panel, not a completed all-neuroscience study. **78 active entries remain unrun** (49 pending validation, 29 deferred). Open-weight, native image/video/world models and most current strongest specialists remain untested. A measured family means at least one narrow slice, not complete coverage of its scientific questions. The source registry contains 190 URLs, not 190 fully read papers. No exhaustive-literature or current-global-SOTA claim.

## What changed and what the evidence says

- Added spike sorting (B01), cross-day intracortical BCI (G01), sleep staging (H08), and expert-labeled microscopy instance segmentation (J08). Refit unchanged E01 programs on Area2_Bump and DMFC_RSG as source-portability tests.
- MountainSort5 scores 0.940896 versus 0.874991 / 0.940011 / 0.750450 for the three models on one short stationary simulation. Archived StarDist scores 0.862534 versus 0.643368 / 0.492074 / **failure** on two microscopy fields. These are concrete specialist advantages with narrow scope.
- EEG-only pretrained YASA scores 0.764737 versus 0.802716 / 0.792675 / 0.792236 on three held-out Sleep-EDF nights. Training histories differ; GPT-5.6 exceeds the requested code-line limit and is excluded from the strict-format subset.
- GPT-6.1 improves over GPT-6 on 15 of 22 non-deterministic/non-quadrature slice comparisons, declines on 6, and fails on 1. Family-equal directional improvement fraction is 0.569. The aggregate includes selected synthetic and semisynthetic tasks and one generation per task/model; it is not a scaling law.

[Full native-score table and interpretation](analysis/findings.md). Native metric magnitudes are never averaged across different tasks. Historical test-selected envelopes, local specialists, pretrained specialists and conventional baselines have separate comparison classes and explicit denominators.

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
| [H](benchmarks/H/README.md) EEG, MEG, field signals and peripheral interfaces | 14 | H01, H08, H16 | 1 | 10 |
| [I](benchmarks/I/README.md) Human and mesoscopic neuroimaging | 6 | I07, I10 | 0 | 4 |
| [J](benchmarks/J/README.md) Anatomy, histology and connectomics | 9 | J08 | 4 | 4 |
| [K](benchmarks/K/README.md) Cell types and molecular neuroscience | 5 | K01 | 4 | 0 |
| [L](benchmarks/L/README.md) Mechanistic and statistical inference | 5 | L04 | 3 | 1 |
| [M](benchmarks/M/README.md) Experimental design and control | 4 | M04 | 2 | 1 |
| [N](benchmarks/N/README.md) Scientific analysis workflows | 3 | N05 | 2 | 0 |

[Taxonomy](docs/taxonomy.md) · [Coverage and remaining gaps](docs/coverage-matrix.md) · [Methodology](docs/methodology.md) · [Prior work](docs/prior-work.md) · [Macro-analysis policy](docs/macro-analysis-plan.md)

## Audit a result

1. Open `benchmarks/<family>/<ID>/` for scope, data, sources, proposed methods and actual worklog.
2. Follow `experiments/<ID>/` for the executed protocol, input/prompt/code identities and exact submissions. E01's additional sources have separate slice directories and reuse the original code.
3. Compare [central JSONL](results/measurements.jsonl), [CSV](results/measurements.csv), [stored predictions](results/predictions/), [score checks](analysis/validation-expansion.json) and [derived summaries](analysis/summary.json).
4. Inspect [admission decisions](registry/admission-decisions.json), [archived candidates](registry/excluded-candidates.json), [source registry](literature/sources.json) and [current-best ledger](registry/current-best.json). Unknown current best remains unknown.

[Review protocol](docs/review-protocol.md) · [Data management](docs/data-management.md) · [Contributing](CONTRIBUTING.md). Closest prior work includes BrainWideBench, NeuralBench, NeuroDiscoveryBench/NeuroClaw, SciVid and EEGAgentBench; this project does not claim to originate broad neuroscience evaluation. A paper needs repeated generations, stronger matched specialists, independent biological cases and external coverage review.

Code/documentation MIT; third-party data/artifacts retain upstream terms. Raw caches and supplied lecture PDFs are not redistributed. Repository and hosted dashboard retain their private audiences.
