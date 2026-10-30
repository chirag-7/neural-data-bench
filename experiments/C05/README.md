# C05 — five-preparation Spikefinder audit

[Task card](../../benchmarks/C/C05/README.md) · [Frozen transfer protocol](phase2-protocol.md) · [Original pilot](pilot-v1/README.md) · [Measurements](../../results/C05.json) · [Input manifest](../../data/manifests/spikefinder.json) · [Generation provenance](generation-provenance.json)

## Completed procedure

1. Preserve the three original no-tool single-shot programs and original preparation-1 pilot unchanged in `pilot-v1/`.
2. Commit the transfer-audit protocol before acquiring/scoring preparations 2–5. Remove Luna per user instruction before any numerical Luna execution.
3. Acquire original train/test fluorescence, train/test spike labels, pinned official scorer/result table and four historical reference prediction sets for each preparation. Hash 43 acquired/extracted files in the shared manifest.
4. Pass only train fluorescence/spikes and test fluorescence to each reviewed model program. Fit independently per preparation. Numerical thread count 1, wall timeout 180 seconds; no model feedback or code repair. All 15 model/preparation calls return valid outputs.
5. Reproduce OASIS default AR1, raw-fluorescence baseline and score complete archived predictions. Four archive attempts fail the complete-target contract and remain recorded.
6. Save every valid prediction under `results/predictions/C05/`, all statuses/errors under `results/C05.json`, execution records, code/input/prediction hashes and centralized JSONL/CSV.
7. Check official scorer equivalence for complete predictions and archived cell-score agreement; preparation-1 outputs agree with the historical pilot. Derive preparation-equal summaries and paired deltas without animal-level inference.

## Interpretation

This tests frozen-program portability across five preparations of one public benchmark. It is not five task families, a full challenge aggregate, a native signal-model test or current specialist SOTA verification. GPT-5.6’s original code has the disclosed 188-line formatting deviation. Preparation 1 is prior pilot/development evidence; dimensions in the common prompt describe it. Complete archive availability is 4/3/4/3/2; the plotted reference is a limited test-selected envelope, with unequal original supervision/tuning history.

Raw data reside in the ignored shared cache and can be reacquired by `scripts/acquire_spikefinder.py`; use terms remain upstream. Portable reproduction entry points are `scripts/evaluate.py`, `scripts/summarize.py` and `scripts/validate.py`, not the archived bundle’s old workspace paths.
