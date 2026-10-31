# H16 methods and admission checklist

[Task card](README.md)

## Proposed evaluation contract

- Native metric(s): Signal error; correlation; retained downstream decoding
- Split/transfer: Hold out source segments/subjects and contamination levels
- Ground truth: Curated clean reference under controlled synthetic contamination
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

Preview 0.6: EEGdenoiseNet: 2,000 training and 600 test clean-plus-EOG mixtures, with disjoint source components.

[Actual frozen contract and implementation](../../../experiments/H16). [Measured method/reference records](../../../results/H16.json). The proposed checklist above does not imply every broader operation or specialist was evaluated.
