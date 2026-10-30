# Neural Data Bench

**A traceable evidence map and exploratory evaluation of general models on neuroscience laboratory tasks.** Research preview v0.3, 30 October 2026. Course project context: [Liam Paninski’s Statistical Analysis of Neural Data](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/).

[Interactive observatory](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site) (owner-private) · [Central status](docs/status.md) · [Taxonomy](docs/taxonomy.md) · [Methods](docs/methodology.md) · [Findings](analysis/findings.md) · [Reproduce](docs/reproduce.md) · [Next execution panel](docs/execution-panel.md)

## Main question and plan

When can an off-the-shelf general model perform a useful neuroscience analysis, and when does a specialist method remain necessary? Define a defensible task space first, reuse established benchmarks where possible, construct modest wrappers only when ground truth and scoring are clear, then compare **specified model-plus-procedure combinations** with specialist references under controlled conditions.

Separate direct model inference, frozen representation transfer, bounded adaptation, general-code construction and specialist-tool workflows. General text/code, image/video, audio/time-series/world and neuroscience-pretrained models do not have interchangeable interfaces. This release measures only single-shot **T3 code synthesis followed by local numerical fitting**, using GPT-5.6 Sol, GPT-6 Sol and GPT-6.1 Sol. No Luna model is evaluated. Open-weight and other model modalities remain untested.

## What is completed

| Artifact | v0.3 state |
|---|---|
| Evidence map | **114 task–resource pairings, 14 families, 134 source URLs**; not 114 unique datasets or runnable benchmarks |
| Distributed documentation | Each pairing has a task card, methods, actual worklog, data description and source associations |
| Literature provenance | Original detailed map, two gap audits, bounded extension search log, exclusions, admission and current-best ledgers |
| Execution admission | 2 tasks with measured slices; 96 candidates awaiting validation; 16 deferred from lightweight execution |
| Biological evaluation | Spikefinder preparations 1–5: same three frozen generated programs, refitted independently per preparation |
| Computational evaluation | New synthetic Q-learning parameter-recovery wrapper: 24 simulated agents, same three models |
| Central results | 18 model–slice attempts, 51 total model/reference records including 4 unusable archived reference attempts; predictions and hashes retained |
| Scientific checks | 43 acquired-file hashes; scorer equivalence for all complete Spikefinder predictions; 16 archived result sets agree with published cell values; original pilot reproduced |
| Dashboard | Category → task → overview/results/procedure/sources; bar and generation-line charts; cross-task denominators and downloads. 473 source-render checks pass; browser interaction/layout QA remains unverified due to a URL-policy block. |

**The full cross-domain evaluation is not completed.** There is one biological benchmark and one synthetic task; 112 mapped entries have no model scores. No exhaustive literature-review, universal coverage, current global SOTA or broad superiority claim is justified. Unknown values remain null. See [why this coverage is broad but insufficient](docs/taxonomy.md).

## Measured results

C05 primary score is each preparation’s median 40-ms-binned per-neuron Pearson correlation. The table averages those five preparation medians equally. M04 scores range-normalized parameter MAE, lower is better; it is not combined with Pearson.

| Generated analysis program | C05 mean of five medians ↑ | M04 normalized parameter MAE ↓ |
|---|---:|---:|
| GPT-5.6 Sol | 0.452196 † | 0.058223 |
| GPT-6 Sol | 0.443305 | 0.058219 |
| GPT-6.1 Sol | 0.467896 | 0.058221 |

† GPT-5.6’s original C05 submission exceeded the <180-line formatting request (188 lines). Its unchanged exploratory scores are retained; strict-format C05 comparisons exclude it. All 18 generated-program executions returned valid numerical outputs. One generated program per model/task does not establish a stable ranking.

GPT-6.1 exceeds GPT-6 on all five C05 preparations; GPT-6 exceeds GPT-5.6 on only two. GPT-6.1 beats the **best available complete prediction among up to four inspected historical submissions** on three preparations; complete reference counts vary 4/3/4/3/2. This does not establish superiority over current specialists or equal training/tuning effort. Preparation 1 was previously examined; preparations 2–5 are a frozen-program transfer audit.

The three M04 programs implement essentially the same uniform-prior posterior-median estimator. Their differences are on the order of numerical integration error. A post-hoc independently implemented posterior-median reference confirms that interpretation. The frozen MLE reference has a different estimation objective; lower parameter MAE against MLE is not evidence that general models beat the best specialist. [Full interpretation](analysis/findings.md).

## Browse the research space

| Family | Scientific perspective |
|---|---|
| [A](benchmarks/A/README.md) | Behavior, kinematics and vocalization |
| [B](benchmarks/B/README.md) | Extracellular acquisition, spike sorting, drift and QC |
| [C](benchmarks/C/README.md) | Calcium imaging and photometry |
| [D](benchmarks/D/README.md) | Voltage, intracellular and dendritic physiology |
| [E](benchmarks/E/README.md) | Population activity, dynamics and whole-brain forecasting |
| [F](benchmarks/F/README.md) | Sensory and behavioral encoding |
| [G](benchmarks/G/README.md) | Intracortical BCI |
| [H](benchmarks/H/README.md) | EEG, MEG, field signals, peripheral interfaces and sleep |
| [I](benchmarks/I/README.md) | Human and mesoscopic neuroimaging |
| [J](benchmarks/J/README.md) | Anatomy, histology and connectomics |
| [K](benchmarks/K/README.md) | Cell types, spatial and molecular neuroscience |
| [L](benchmarks/L/README.md) | Mechanistic/statistical inference and causal response |
| [M](benchmarks/M/README.md) | Cognitive modeling, experimental design and control |
| [N](benchmarks/N/README.md) | Scientific analysis workflows |

The modality hierarchy is supplemented by [operation/ground-truth/transfer axes](docs/taxonomy.md) and an explicitly provisional [coverage matrix](docs/coverage-matrix.md). A resource can appear in multiple scientific operations; it is not an independent-study count. Human domain review remains pending.

## How to audit a claim

1. Start at the task’s README and actual worklog under `benchmarks/<family>/<id>/`.
2. Check its [admission decision](registry/admission-decisions.json), data terms, pinned [manifest](data/manifests/) and frozen experiment protocol.
3. Inspect explicit prompts, exact returned programs and sanitized generation provenance under [experiments](experiments/).
4. Re-score the stored [predictions](results/predictions/) and compare [long-form JSONL](results/measurements.jsonl), [scalar CSV](results/measurements.csv) and [validation](analysis/validation.json).
5. Follow [summarize.py](scripts/summarize.py) to the [derived statistics](analysis/summary.json). Missing tasks are never zeros; incompatible native metrics are not averaged.

[Review/screening protocol](docs/review-protocol.md) · [Closest prior work](docs/prior-work.md) · [Macro-analysis plan](docs/macro-analysis-plan.md) · [Source registry](literature/sources.json) · [Exclusions](literature/exclusions.json) · [Data organization](docs/data-management.md) · [Contributing](CONTRIBUTING.md)

## Feasibility and next validity gates

This repository makes the project feasible and auditable, but a defensible paper needs a smaller, prospectively admitted multi-domain panel before expanding further. Start with task-specific rights/access and scorer validation; then add biologically independent cases, repeated model generations, strong current specialist reproductions, open-weight and modality-appropriate general models, and matched adaptation/resource tracks. Candidate names are not a promise that these checks will succeed. Drop or defer a task when the endpoint, data, rights or budget cannot be resolved; retain the reason in the ledger.

The closest prior work includes [BrainWideBench](https://arxiv.org/abs/2609.22064), [NeuralBench](https://arxiv.org/abs/2605.08495), [NeuroDiscoveryBench](https://github.com/allenai/neurodiscoverybench) and [NeuroClaw NeuroBench](https://cuhk-aim-group.github.io/NeuroDiscovery/neurobench.html). This project builds on existing neural-model and analysis-agent benchmarking; novelty requires a narrower supported contribution, not a claim that the area was unstudied.

Code/documentation: MIT. Third-party data and benchmark outputs retain upstream terms. Raw public downloads are acquired into the ignored `data/cache/` and are not automatically redistributed by this repository. Supplied lecture PDFs are not included.
