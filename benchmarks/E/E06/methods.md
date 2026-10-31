# E06 methods and admission checklist

[Task card](README.md)

## Proposed evaluation contract

- Native metric(s): Official forecasting losses at fixed horizons and stimulus conditions; maintain trace/video tracks
- Split/transfer: Official temporal/stimulus-condition splits, including held-out condition
- Ground truth: Future measured calcium activity
- Setup estimate: Medium; P2.

These catalog recommendations become an executable protocol only after choosing a specific endpoint/release. Do not silently combine all operations in this entry into one score.

## Required steps

1. Pin data release; verify access, use terms, consent constraints, unique subject/session grouping and checksums.
2. Choose one endpoint; freeze official scorer or document deviations and units.
3. Separate train/validation/test by the stated biological unit; prohibit tuning on test labels.
4. Reproduce a specialist and simple baseline on the identical slice. Search for comparable current best with date and exact source table.
5. Freeze model checkpoints/aliases, prompts, conversion, track, allowed libraries and budgets in Git.
6. Execute once under the frozen contract; retain failures, predictions, code and provenance; add repeated generations for confirmatory comparisons.
7. Re-score independently, document deviations and add eligible rows to the central results store.

An explicitly scoped exploratory slice has been executed; broader proposed operations above remain separate.

For unexecuted entries all seven gates remain pending; listing these steps is not a claim they were performed. The actual state is in [worklog](worklog.md).

## Current executed protocol

Preview 0.11: One zebrafish brain/session; 272 training windows, 43 temporal-tail tests and 12 unseen-taxis tests; same programs reused.

[Actual frozen contract and implementation](../../../experiments/E06). [Measured method/reference records](../../../results/E06.json). The proposed checklist above does not imply every broader operation or specialist was evaluated.
