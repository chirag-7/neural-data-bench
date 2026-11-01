# Neural Data Bench

**Traceable evidence and exploratory experiments on general coding models for neuroscience lab tasks.** Preview **0.11**, 31 October 2026 (UTC). Course context: [Liam Paninski's Statistical Analysis of Neural Data](https://sites.stat.columbia.edu/liam/teaching/neurostat-fall26/).

[Results explorer](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site) · [Current release and review](docs/release-v11.md) · [Results and limits](analysis/findings.md) · [Reproduce](docs/reproduce.md)

## Macro findings and interactive navigation

[Current four-model comparison](analysis/generation-comparison-v1/report.md) · [Simple interpretation](analysis/generation-comparison-v1/plain-language.md) · [Extension methods and audit trail](docs/generation-extension.md). GPT-4.1 and GPT-5 now join GPT-5.6 Sol and GPT-6.1 Sol across all **30 tasks / 14 categories**; GPT-6 Sol remains historical. **60 new API generations, 74 slice attempts, 64 numeric successes and 10 retained failures**, with all 64 successful outputs independently audited. Conservative API cost: **$4.13**. GPT-6.1 versus GPT-4.1 is 23 better / 2 worse / 5 incomplete; versus GPT-5 it is 21 / 4 / 5. Nine tasks improve at every adjacent model step. This is a descriptive trend, not a scaling law or proof of current-specialist superiority; provider wrappers and selective historical repairs remain confounds.

The interactive explorer now uses these four models in its current line plots, bar charts and tables, with Category → Task navigation. Historical three-model analyses below retain their original measurements and denominators.


[Historical Sol panel: version progress, repaired runs and specialists](analysis/practical-review-2026-11-01/report.md) · [Interactive review](https://neural-data-benchmark-observatory-cc26.almondkoala21.chatgpt.site/#/analysis/practical) · [All 30 specialist reviews](analysis/practical-review-2026-11-01/specialist-matrix.csv). Updated 1 November 2026: four model execution failures recovered in a separate repair-assisted track (three meet the original line cap); four incomplete calcium reference archives remain unresolved. Across 30 repair-assisted numeric task means, GPT-6 vs 5.6 is 14 better / 14 worse / 2 ties; GPT-6.1 vs 5.6 is 20 better / 9 worse / 1 tie. Selective debugging is a usability sensitivity, not fresh single-shot model evidence. The first-attempt panel and its formal macro diagnostics stay unchanged. The fresh specialist review covers 137 candidate entries and 166 distinct source URLs, with no current global winner certified on these custom contracts.

[Read the macro synthesis](analysis/macro-patterns/report.md) · [Methods and assumptions](analysis/macro-patterns/methods.md) · [Independent review](analysis/macro-patterns/independent-review.md). Findings are separated into quantitative, qualitative and combined evidence. GPT-6.1 has a descriptive directional advantage; family-level diagnostics do not establish general superiority or an improvement law. Category-first website navigation now limits each task selector to its chosen category. No benchmark scores or original failures changed.

## Completed evidence

| Artifact | Current state |
|---|---|
| Active research map | 92 entries across 14 families; 22 archived with reactivation reasons; 114 historical entries preserved |
| First-submission panel | **30 task IDs**, 37 evaluation slices per model; 90 single-shot generated programs |
| First-submission executions | **111 attempts: 107 numerically valid, 4 execution failures**; strict-format-valid counts 28 / 36 / 36 for GPT-5.6 / GPT-6 / GPT-6.1 out of 37 each |
| Audit artifacts | 208 model/reference records; 200 unique central prediction/output manifests; source hashes, unchanged programs, generation provenance and independent saved-output audits |
| H02 generation follow-up | Six further programs and seven outputs, separate from first-submission macros; 96 programs and 207 output manifests across both panels |
| Repair-assisted sensitivity | Four model runtime failures recovered, three within the original line cap; seven successful repair/control artifacts; four incomplete C05 archives unresolved; original panel unchanged |
| Current-specialist review | All 30 measured tasks, 137 candidate entries and 166 distinct source URLs; exact-contract current global winners remain unverified |
| Specialist and domain references | SpikeInterface registration, Spikepack, OASIS, NLinear architecture, grouped molecular/cell classifiers, spectral acoustic classification, and prior named specialist references |
| Interface | Measured-first directory, category navigation, searchable tasks, native metric tables/plots and explicit compliance/aggregate-exclusion policies |

Models **generate analysis code**, then saved programs execute numerical procedures locally. This is the T3 procedure, not native raw-signal comprehension or a full autonomous scientist. No Luna, open-weight, native image/video/world-model track or current-global-SOTA certification is included. **62 active entries remain unrun** (33 pending validation, 29 deferred). Representing 14 categories does not complete all their subfields. The source registry contains 227 associated URLs; this is a source inventory, not a count of fully reviewed papers.

[Candid progress assessment](docs/progress-assessment.md) · [H02 three-generation follow-up](experiments/H02/replication-v1/results.md)

## Why the latest review matters

- **Seven-task parallel batch:** 21 new programs, eight evaluation slices and 24 model attempts add acoustic events, synthetic motion, event compression, calcium inference, population forecasting and two cell tasks. One consolidated registry/macro/site update. [Full report](docs/batch-v11.md).
- **Contract and calibration limits:** B08 import ambiguity excludes it from aggregate claims; both failures remain visible. A15 has one over-limit submission. C06 high correlation coexists with large count calibration error, now selectable in plots. All new outputs have independent audits.

- **Seven-task batch:** acoustic events, synthetic motion, spike-event compression, paired calcium/electrical inference, population forecasting, orthogonal molecular fractions and optotagged classes. B08 has an ambiguous whitelist exclusion; A15 GPT-5.6 violates the line cap despite a numeric result; C06 correlation hides count-scale errors. [Exact outcomes and limits](docs/release-v11.md).

- **Real-voltage lossless compression:** all 16 original source recordings, exact byte reconstruction, WavPack and delta–Blosc/Zstd references; every successful saved bitstream independently decoded. [Scores and limits](docs/release-v10.md).

- **New posterior-sampling endpoint:** all three generated samplers complete ten original synthetic spiking-neuron GLM posteriors; compare the frozen primary classifier diagnostic and secondary distribution distance against local Polya–Gamma/Laplace references. [Exact procedure and limits](docs/release-v09.md).
- **Explicit analysis scopes:** observed-data sources are the default; include fully synthetic tasks with one selector. Both views retain task/family denominators.

- **Earlier real-data additions:** SingleR leads all three Sol versions on donor-held-out cortical-layer transfer; all three beat a source-inspired GLM on mouse-held-out conditional choice prediction. [Exact scores, source checks and limits](docs/release-v08.md). Neither result establishes current global best.

- **Metric sensitivity:** GPT-6 nearly matches MountainSort5 on frozen per-GT-unit spike-sorting accuracy (0.940011 vs 0.940896). Counting all emitted spikes yields post-hoc event F1 **0.599751 vs 0.962060**, exposing excess spikes. Both views remain available; the original primary and macro scores are unchanged.
- **P300 replication:** three-attempt means are **0.752374 / 0.744027 / 0.784685**, versus train-only CV-selected xDAWN **0.778541**. All three GPT-6.1 attempts exceed this reference; minimum advantage is only 0.000754. Same dataset, retrospective follow-up, no global-superiority claim. Original endpoint below is preserved.
- **Original P300 experiment:** all 25 Brain Invaders 2012 people, 15 train/10 held-out. Person-equal ROC-AUC is **0.757195 /0.730548 /0.788537**, versus fixed xDAWN **0.761230**. Ten-person evaluation is stronger grouping depth than earlier pilots, but remains one public source and one generation.
- **Readability corrections:** current task-card/method headers no longer say “not evaluated” for measured tasks. Historical status remains dated. Methodology is consolidated; specialists, ordinary baselines and post-hoc metrics are visually distinct.
- **Mixed model progress:** In the current observed-data scope, GPT-6.1 improves on GPT-6 in 23 of 31 slices, declines in 7 and fails in 1; family-equal directional improvement fraction 0.609 across 24 tasks / 13 families. B08 is retrospectively excluded. This is descriptive, not a causal scaling claim.

[Full native-score table and caveats](analysis/findings.md). Native metric magnitudes are never averaged across unrelated tasks. Test-selected envelopes, historical/pretrained/local specialists, conventional references and failures have explicit policies and denominators.

## Navigate by category

| Family | Active entries | Measured IDs | Pending validation | Deferred |
|---|---:|---|---:|---:|
| [A](benchmarks/A/README.md) Behavior, kinematics and vocalization | 16 | A09, A14, A15 | 10 | 3 |
| [B](benchmarks/B/README.md) Extracellular signal acquisition | 7 | B01, B03, B07, B08 | 3 | 0 |
| [C](benchmarks/C/README.md) Calcium imaging and photometry | 7 | C05, C06 | 5 | 0 |
| [D](benchmarks/D/README.md) Voltage, intracellular and dendrites | 3 | D02 | 0 | 2 |
| [E](benchmarks/E/README.md) Population activity and dynamics | 6 | E01, E06 | 3 | 1 |
| [F](benchmarks/F/README.md) Sensory and behavioral encoding | 5 | F04 | 2 | 2 |
| [G](benchmarks/G/README.md) Intracortical BCI | 3 | G01 | 0 | 2 |
| [H](benchmarks/H/README.md) EEG, MEG, field signals and peripheral interfaces | 14 | H01, H02, H08, H16 | 1 | 9 |
| [I](benchmarks/I/README.md) Human and mesoscopic neuroimaging | 6 | I07, I10 | 0 | 4 |
| [J](benchmarks/J/README.md) Anatomy, histology and connectomics | 9 | J08 | 4 | 4 |
| [K](benchmarks/K/README.md) Cell types and molecular neuroscience | 5 | K01, K04, K05, K06 | 1 | 0 |
| [L](benchmarks/L/README.md) Mechanistic and statistical inference | 4 | L04, L06 | 1 | 1 |
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
