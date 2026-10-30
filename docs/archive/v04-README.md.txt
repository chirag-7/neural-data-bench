# Neural Data Bench

**A traceable evidence map and exploratory evaluation of general models on neuroscience lab tasks.** Research preview 0.4,30October 2026. Course context: [Liam Paninski's Statistical Analysis of Neural Data](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/).

[Interactive observatory](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site) · [Full release report](docs/release-v04.md) · [Results and interpretation](analysis/findings.md) · [Reproduce](docs/reproduce.md)

## What is completed

| Artifact | Current state |
|---|---|
| Evidence map |114 task-resource pairings across 14 families;180 sourceURLs, not 180 fully reviewed papers |
| Admission review | Every entry assessed:14 measured,57 source-only pending gates,43 deferred with reasons |
| Measured panel |14 task IDs across 11 families;3 requested Sol models;42 single-shot generated programs |
| Executions |54 model-slice attempts;53 numerically valid,1 program failure;120 model/reference records retained |
| References |Basic conventional baselines; historical Spikefinder, VASSI and MRIQC predictions rescored; deterministic and synthetic references labeled separately |
| Audit trail |Per-task source terms/manifests, frozen prompts/data/code hashes, programs, predictions, usage/tool counts, failures and scorer checks |
| Website |Category→task→overview/results/procedure/sources; bar and generation-line plots; reference-class filters, native-task scores and macro statistics |

This is **not a completed all-neuroscience study**.100 mapped entries have no model score; open-weight, native image/video/world models and stronger current specialists remain untested. Coverage and search are bounded, not exhaustive. No current-SOTA or universal superiority claim. Unknown remains unknown.

## Main findings

- GPT-6.1 improves on GPT-6 in 12 of 16 biological/semisynthetic slice comparisons and declines in 4;12 tasks across 9 families, excluding synthetic quadrature and deterministic file checks. Family-equal improvement fraction 0.667. One program per version; no stable scaling claim.
- Against 9 simple conventional baselines, point wins are 7/9,8/9,7/9 for GPT-5.6,6,6.1. This does not show superiority over current specialized methods.
- Against 7 historical-specialist slice references across 3 tasks, point wins are 2/7,1/7,5/7. C05 uses test-selected envelopes; VASSI/MRIQCtraining histories differ. Strict-format denominators and family-weighting are explicit in [analysis](analysis/summary.json).
- GPT-5.6 fails the legacyNWBfile extractor; GPT-6 and 6.1 match all 61 deterministic fields. Failures and format deviations remain visible.

[Complete 14-task native-score table, interpretation and limitations](analysis/findings.md). Native metric values are not averaged across tasks. These are constrained code-generation plus local-fitting experiments(T3), not native neural-data comprehension or a full autonomous scientist.

## Navigate the project

| Family | Mapped pairings | Measured task IDs | Source-only pending | Deferred |
|---|---:|---|---:|---:|
| [A](benchmarks/A/README.md) Behavior, kinematics and vocalization | 16 | A09, A14 | 11 | 3 |
| [B](benchmarks/B/README.md) Extracellular signal acquisition | 8 | None | 8 | 0 |
| [C](benchmarks/C/README.md) Calcium imaging and photometry | 9 | C05 | 8 | 0 |
| [D](benchmarks/D/README.md) Voltage, intracellular and dendrites | 4 | D02 | 0 | 3 |
| [E](benchmarks/E/README.md) Population activity and dynamics | 6 | E01 | 5 | 0 |
| [F](benchmarks/F/README.md) Sensory and behavioral encoding | 5 | F04 | 2 | 2 |
| [G](benchmarks/G/README.md) Intracortical BCI | 3 | None | 1 | 2 |
| [H](benchmarks/H/README.md) EEG, MEG, field signals and peripheral interfaces | 19 | H01, H16 | 5 | 12 |
| [I](benchmarks/I/README.md) Human and mesoscopic neuroimaging | 10 | I07, I10 | 1 | 7 |
| [J](benchmarks/J/README.md) Anatomy, histology and connectomics | 9 | None | 4 | 5 |
| [K](benchmarks/K/README.md) Cell types and molecular neuroscience | 6 | K01 | 4 | 1 |
| [L](benchmarks/L/README.md) Mechanistic and statistical inference | 6 | L04 | 3 | 2 |
| [M](benchmarks/M/README.md) Experimental design and control | 7 | M04 | 2 | 4 |
| [N](benchmarks/N/README.md) Scientific analysis workflows | 6 | N05 | 3 | 2 |


[Taxonomy and coverage justification](docs/taxonomy.md) · [Coverage maturity](docs/coverage-matrix.md) · [Methodology](docs/methodology.md) · [Main plan/release](docs/release-v04.md) · [Closest prior work](docs/prior-work.md) · [Macro-analysis policy](docs/macro-analysis-plan.md)

## Audit any task or claim

1. Start at `benchmarks/<family>/<ID>/`: overview, proposed methods, data description, references and actual worklog.
2. Check [admission evidence](registry/admission-decisions.json) and actual acquisition/license scope; only measured slices have executed data/scorer gates.
3. Follow `experiments/<ID>/` to the frozen protocol, prompts/run-spec, exact model submissions, generation provenance and execution worklog.
4. Re-score [stored predictions](results/predictions/) and compare [central JSONL](results/measurements.jsonl), [CSV](results/measurements.csv) and [validation](analysis/validation-expansion.json).
5. Inspect [aggregation code](scripts/summarize.py) and [derived summary](analysis/summary.json). All 20 VASSIruns and original failures remain available. D02/N05 share a file; repeated trials/neurons are not independent studies.

[Review protocol](docs/review-protocol.md) · [Source registry](literature/sources.json) · [Admission decisions](registry/admission-decisions.json) · [Current-best evidence ledger](registry/current-best.json) · [Data management](docs/data-management.md) · [Contributing](CONTRIBUTING.md)

Nearest prior work includes BrainWideBench,NeuralBench,NeuroDiscoveryBench/NeuroClaw,SciVid andEEGAgentBench; this project builds on a substantial existing field. A paper needs a narrowly justified contribution, external expert coverage review, repeated generations, stronger matched specialists and prospectively frozen independent cases. No assertion that nothing is missing.

Code/documentation MIT; third-party data/artifacts retain upstream terms. Raw data cache and supplied lecturePDFs are not redistributed. Repository and hosted dashboard preserve their private audiences.
