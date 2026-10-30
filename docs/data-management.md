# Data, provenance and repository organization

- `registry/catalog.json`: canonical task-resource map; never infer scores from readiness.
- `registry/admission-decisions.json`: executed/candidate/deferred and reasons.
- `registry/current-best.json`: matched-current-best ledger; unknown scores are null.
- `literature/`: sources, exact available search log, bounded audits and exclusions.
- `benchmarks/<family>/<id>/`: decentralized task card, proposed methods, actual worklog, data and references. Family index links to each card.
- `experiments/<id>/`: frozen prompts, returned code, protocols and model provenance.
- `data/manifests/`: upstream release IDs, URLs, exact checksums, bytes and acquisition dates.
- `data/cache/`: ignored local data, downloaded/reconstructed by scripts. The single raw-data home is here; third-party data are not automatically relicensed or committed.
- `results/measurements.jsonl` and `.csv`: central long-form scalar measurements and per-unit arrays; only actual executions. `results/predictions/` retains model outputs; `results/execution/` retains controlled numerical execution logs.
- `analysis/summary.json`: derived paired descriptive statistics, references and denominators; `scripts/summarize.py` is the single derivation.
- `website/`: static navigable dashboard generated from registry/results; no hidden hand-entered scores.
- `docs/status.md`: central accomplishments, exclusions and remaining validity gates.

The original pilot-v1 folder is an immutable historical bundle whose scripts assumed the old workspace layout. Use the canonical `scripts/` entry points in this repository to acquire and reproduce it. Predictions and hashes are portable. No course PDFs, authentication files, provider credentials, machine-specific JSONL infrastructure events, package caches or raw downloads are pushed. Minimal sanitized generation metadata (usage, requested model, no-tool events, prompt/code hashes) is retained instead.

Repository code is MIT licensed. Dataset/prediction derivatives retain applicable upstream terms; repository licensing does not grant third-party data rights. Confirm use terms before redistribution or publication. Exact byte checksums verify artifacts, not scientific correctness. NumPy ZIP container bytes may change between regenerations even for identical arrays; input-array hashes also identify synthetic data semantically.
