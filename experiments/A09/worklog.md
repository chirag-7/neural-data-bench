# Acquisition and preparation log

2026-10-30: Queried primary CaltechDATA record, downloaded API metadata and official readme. Downloaded 457,357,950 byte official Task 1 archive and validated publisher MD5. Documented current CC BY 4.0 record versus paper noncommercial-sharealike discrepancy; no raw files are to be committed. Defined fixed 3Hz sampling without test-score access and retained official train/test animal split. Wrote streaming per-sequence JSON reader to avoid materializing multi-gigabyte release as Python nested objects. Prepared all recordings with sequence IDs and center-frame provenance. This adapter does not use TREBA task-program features or MARS supervised action features.

Archived specialist follow-up: acquired VASSI version 1.0 predictions and source archives (Edmond DOI10.17617/3.3R0QYI), validated publisher checksums and exact source-file matches. Selected run 00 before rescoring, preserved all 20 runs. All original 262107 frame labels, zero-based timestamps and frozen 26162 centerIDs align exactly. Four-class macroF1 for preselectedrun 00 is 0.8695177327504425. Full-frame domainfeature/optimization budgets differ; archived reference is excluded from strict equal-budget superiority. Frozenadapter andrun-spec hashes unchanged. See archived-vassi/README.md and source-manifest.json.

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: macro_f 1=0.868971950573; formatting compliant.
- gpt-6-sol: macro_f 1=0.875946306706; formatting compliant.
- gpt-6.1-sol: macro_f 1=0.880696015491; formatting compliant.

Reference: vassi-run-00; Archived VASSI run 00, selected before rescoring; unequal full-frame inputs/training/tuning. Current strongest specialist unverified. [Full result records](../../results/A09.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/A09/). No statistical significance claim.
