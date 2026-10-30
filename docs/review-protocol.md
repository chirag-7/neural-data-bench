# Literature review and screening protocol v0.3

This is an auditable **evidence map with bounded primary-source gap audits**, not a completed systematic review. Earlier discovery searches were not completely logged; they cannot be retrospectively described as PRISMA-compliant. No exhaustive PubMed/Scopus/Web of Science screening or dual independent human screening was performed.

## Research question

For reproducible neuroscience laboratory analysis and computational-model validation operations, which public benchmarks/datasets support comparison of general pretrained models, neural-domain pretrained models and specialist methods under controlled input, adaptation and resource regimes?

## Search and evidence strategy

The original 90-entry discovery map was expanded by a 12-entry operation-focused audit and a 12-entry primary-source extension audit (114 pairings). The extension searched benchmark papers, author project pages, code/data releases and reporting guidance, including terms for animal acoustics, sleep, artifacts, whole-brain dynamics, microscopy and spatial molecular data. Actual queries are retained in [search-log](../literature/search-log.json) and [extension audit](../literature/extension-audit.json); source associations are in [sources](../literature/sources.json). These are a bounded search trail, not a complete search export or PRISMA flow count. Discovery of a URL is distinguished from full-text assessment, download, rights check and execution.

A confirmatory scoping review should prospectively search PubMed/Europe PMC, arXiv/bioRxiv, NeurIPS/ICLR and domain venues, OpenNeuro, DANDI, CRCNS, Allen, IBL, PhysioNet and relevant challenge portals; export records, deduplicate DOIs/resources/cohorts, perform two human screens, resolve disagreements, record reasons and update until a defined cutoff. Suggested search grammar: (neuroscience OR neural OR brain OR electrophysiology OR calcium OR behavior OR connectomics) AND (benchmark OR challenge OR ground truth OR dataset) AND each operation/modality synonym. The listed databases are a plan, not sources fully screened in this release.

## Inclusion and execution gates

Include in the evidence map when a neuroscience-relevant input/output task and primary resource can be identified. Admit to execution only after verifying lawful use/access, finite data slice, label availability, scientific grouping/split, executable scorer, baseline and feasible resource budget. Split benchmark suites into endpoint/release cards before execution. Exclude generic ML or medical tasks without a stated neural/lab rationale; do not include a tool as if it were labeled benchmark data.

Defer high-setup resources, proposed constructions and unconfirmed releases/rights from the lightweight execution release. Keep their cards and reasons in [admission decisions](../registry/admission-decisions.json). Do not delete historical candidates to inflate completion rate. Missing scores never become zeros. No arbitrary count target is a completeness criterion.

## Current-best extraction

A numeric best row requires a primary table/leaderboard, retrieval date, exact dataset/split/preprocessing/scorer version, metric direction, label/pretraining regime, budget and uncertainty. Keep official held-out, archived predictions, published reimplementation and local reproduction distinct. The [current-best ledger](../registry/current-best.json) deliberately contains null scores when no matched verification exists. A candidate baseline name or a recent paper is not a current-best finding.

## External review needed

Seek domain review across systems ephys/optical, behavior, human neuroimaging/BCI, molecular/anatomy and theory. Expert coverage review and independent execution audit remain pending. [PRISMA-ScR](https://www.prisma-statement.org/scoping), [PRISMA-S](https://pmc.ncbi.nlm.nih.gov/articles/PMC8270366/) and [neuroimaging benchmark recommendations](https://doi.org/10.1016/j.neuroimage.2022.119298) guide the next review; compliance is not claimed.
