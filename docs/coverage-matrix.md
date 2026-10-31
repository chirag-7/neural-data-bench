# Coverage and maturity

21measured IDs represent 14 families through narrow selected slices, not complete coverage. Counts describe task–resource associations, not independent datasets.

| Family | Active entries | Measured IDs | Pending validation | Deferred |
|---|---:|---|---:|---:|
| [A](../benchmarks/A/README.md) Behavior, kinematics and vocalization | 16 | A09, A14 | 11 | 3 |
| [B](../benchmarks/B/README.md) Extracellular signal acquisition | 8 | B01 | 7 | 0 |
| [C](../benchmarks/C/README.md) Calcium imaging and photometry | 9 | C05 | 8 | 0 |
| [D](../benchmarks/D/README.md) Voltage, intracellular and dendrites | 3 | D02 | 0 | 2 |
| [E](../benchmarks/E/README.md) Population activity and dynamics | 6 | E01 | 5 | 0 |
| [F](../benchmarks/F/README.md) Sensory and behavioral encoding | 5 | F04 | 2 | 2 |
| [G](../benchmarks/G/README.md) Intracortical BCI | 3 | G01 | 0 | 2 |
| [H](../benchmarks/H/README.md) EEG, MEG, field signals and peripheral interfaces | 14 | H01, H02, H08, H16 | 1 | 9 |
| [I](../benchmarks/I/README.md) Human and mesoscopic neuroimaging | 6 | I07, I10 | 0 | 4 |
| [J](../benchmarks/J/README.md) Anatomy, histology and connectomics | 9 | J08 | 4 | 4 |
| [K](../benchmarks/K/README.md) Cell types and molecular neuroscience | 5 | K01, K04 | 3 | 0 |
| [L](../benchmarks/L/README.md) Mechanistic and statistical inference | 5 | L04 | 3 | 1 |
| [M](../benchmarks/M/README.md) Experimental design and control | 4 | M01, M04 | 1 | 1 |
| [N](../benchmarks/N/README.md) Scientific analysis workflows | 3 | N05 | 2 | 0 |

## Removed from the active map

18 candidates were archived with explicit reactivation requirements in the [exclusion ledger](../registry/excluded-candidates.json); all historical cards and the [114-entry snapshot](../registry/catalog-history/v04-114.json) remain. Reasons include unclear data rights, required data applications, unfrozen constructed tasks, duplicated workflow definitions and unconfirmed releases. These are project-level admission decisions, not assertions that a scientific task is impossible or its data are inherently bad. No measured task was dropped because of a poor general-model score. [Pruning review](../literature/active-pruning-v05.md).

## Material gaps

- B01 is a ten-second stationary simulation: biological extracellular voltage, drift, collisions and multi-hour stability remain unmeasured.
- J08 has two 2 D fields: 3 D microscopy, EM connectomics, registration, tractography and independent-specimen replication remain unmeasured.
- G01 is offline monkey finger-velocity decoding across four recording days: clinical speech BCI, online control, adaptation latency and human safety remain unmeasured.
- H08 has three held-out first nights from healthy volunteers; clinical disorders, sites, demographics and full polysomnography generalization remain unmeasured. MEG, seizure detection and other electrophysiology endpoints remain candidates.
- Calcium motion correction/segmentation, whole-brain fMRI encoding, broader molecular/spatial omics, causal perturbation inference, mechanistic simulator fitting, active experiment design and embodied control have little or no execution here.
- K04 adds supervised layer transfer from spatial expression, but only one test donor and no spatial context; independent spatial truth, broader molecular mapping and spatial clustering remain gaps.
- M01 adds real conditional choice prediction with observed histories and known blockprior; unseen labs, autonomous policies and richer cognitive tasks remain gaps.
- M04 is synthetic cognitive parameter recovery; L04 measures one real cell's encoding, not full goodness-of-fit or causal identification. N05 is one deterministic file fixture.
- Every measured model is a constrained general coding model. Native image/video/world models, open-weight models, retrieval-assisted agents and unconstrained autonomous lab workflows are not compared.

The [taxonomy](taxonomy.md) and [review protocol](review-protocol.md) provide systematic axes and bounded searches. External neuroscience expert review and prospective validation on independent resources remain necessary. A claim that nothing is missing would be unjustified.

## ERP addition in preview 0.6

H02 adds one 25-person P300 source with 15/10 subject split; it does not complete other ERPparadigms, online BCI or clinical generalization. Earlier BNCI 2014_008 assessment remains historical; its data were not substituted into the new endpoint.
