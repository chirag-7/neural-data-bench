# H02 follow-up results

Retrospective replication on the same frozen Brain Invaders 2012 split. Original plus two fresh, no-feedback submissions per model. Equal-person ROC-AUC; larger is better. Means include every numerically valid attempt; failures and format compliance are shown separately. No best-of-three model selection.

| Model | Valid | Strict valid | Mean | Range | Attempts > fixed specialist | Attempts > tuned specialist |
|---|---:|---:|---:|---:|---:|---:|
| gpt-5.6-sol | 3/3 | 3/3 | 0.752374 | 0.746444–0.757195 | 0 | 0 |
| gpt-6-sol | 3/3 | 3/3 | 0.744027 | 0.730548–0.761932 | 1 | 0 |
| gpt-6.1-sol | 3/3 | 3/3 | 0.784685 | 0.779295–0.788537 | 3 | 3 |

Original fixed xDAWN reference: **0.761230**. Tuned reference status: **measured**. Tuned xDAWN test score: **0.778541**, chosen configuration `{"nfilter": 4, "classes": [0, 1], "C": 10}`; total selection/refit/inference 56.72s. The choice used only five-fold training-person validation, not the test score.

This study adds six generation attempts and one specialist attempt separately from the original suite. It adds no dataset, cohort, task or family. Original 75-attempt macro comparisons retain their frozen scores and reference policy. Three generations do not establish a stable population ranking; this task and follow-up plan were selected after seeing the original results.

[All attempts and references](../../../results/replications/H02.json) · [CSV](../../../results/replications/H02.csv) · [Frozen amendment](amendment.md) · [Verification](verification.json) · [Generation provenance](generation-provenance.json)
