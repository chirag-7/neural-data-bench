# Best observed general code versus specialists

[Methods and limitations](methods.md) · [Per-task CSV](task-comparisons.csv) · [Source-bound JSON](comparison.json)

This is analysis code generation with local execution/fitting, not direct inference by a pretrained neural-data model. Best is selected post hoc from measured procedures; current global SOTA is unverified.

## Specialist-only: 14 available comparisons; 16 unavailable

| Size filter | General better | Comparator better | Tie / within band | Unavailable | Not estimable |
|---|---:|---:|---:|---:|---:|
| raw | 10 | 4 | 0 | 16 | 0 |
| iqr_0.1 | 9 | 3 | 2 | 16 | 0 |
| iqr_0.5 | 3 | 1 | 10 | 16 | 0 |

## All references: 30 comparisons; includes ordinary baselines

| Size filter | General better | Comparator better | Tie / within band | Unavailable | Not estimable |
|---|---:|---:|---:|---:|---:|
| raw | 24 | 5 | 1 | 0 | 0 |
| iqr_0.1 | 20 | 3 | 7 | 0 | 0 |
| iqr_0.5 | 12 | 1 | 17 | 0 | 0 |

## Specialist task rows

| Task | Best general | Specialist | Signed gap / general-panel IQR | Raw | 0.1 IQR | 0.5 IQR |
|---|---|---|---:|---|---|---|
| A09 | gpt-6.1-sol: 0.880696 | vassi-run-15: 0.870279 | 0.408 | general_better | general_better | within_band |
| B01 | gpt-5.6-sol: 0.874991 | mountainsort5: 0.940896 | -0.091 | specialist_better | within_band | within_band |
| B03 | gpt-5.6-sol: 3.60416 | task-baseline: 4.85014 | 0.378 | general_better | general_better | within_band |
| B07 | gpt-4.1-2025-04-14: 6.63549 | delta-blosc-zstd: 7.68324 | 3.645 | general_better | general_better | general_better |
| B08 | gpt-5.6-sol: 7.5856 | spikepack: 8.14231 | 0.482 | general_better | general_better | within_band |
| C05 | gpt-6.1-sol: 0.467896 | rupprecht: 0.460598 | 0.078 | general_better | within_band | within_band |
| C06 | gpt-6.1-sol: 0.867592 | task-baseline: 0.715517 | 0.450 | general_better | general_better | within_band |
| H01 | gpt-6.1-sol: 0.697958 | pyriemann-aligned: 0.613966 | 0.928 | general_better | general_better | general_better |
| H02 | gpt-6.1-sol: 0.788537 | xdawn-tslr-tuned: 0.778541 | 0.160 | general_better | general_better | within_band |
| H08 | gpt-5.6-sol: 0.802716 | yasa-eeg: 0.764737 | 0.467 | general_better | general_better | within_band |
| I10 | gpt-5-2025-08-07: 0.670702 | mriqc-rfc-2017: 0.613684 | 4.962 | general_better | general_better | general_better |
| J08 | gpt-5.6-sol: 0.643368 | task-baseline: 0.862534 | -0.534 | specialist_better | specialist_better | specialist_better |
| K04 | gpt-6.1-sol: 0.55055 | singler: 0.554585 | -0.202 | specialist_better | specialist_better | within_band |
| L06 | gpt-6.1-sol: 0.5056 | polya-gamma: 0.4941 | -0.171 | specialist_better | specialist_better | within_band |

## Interpretation

The best retained general procedure exceeds the best complete scored specialist on 10/14 tasks numerically; 9/14 exceed 0.1 IQR and 3/14 exceed 0.5 IQR. Specialist advantages are 4, 3 and 1 respectively. Ten comparisons fall within the 0.5 band; this does not establish practical equivalence.

The 0.5-band general advantages are voltage compression (B07), EEG motor imagery (H01) and historical MRI quality classification (I10). Puncta segmentation (J08) is the corresponding specialist advantage. Native differences, unequal information/training and historical references remain central to interpretation.

Excluding L06, whose chance-target diagnostic complicates preferred-direction interpretation: raw 10 general / 3 specialist wins; 0.1 IQR gives 9 / 2 / 2 within; 0.5 IQR gives 3 / 1 / 9 within (13 comparisons).

Together with the earlier 28/30 GPT-6.1 versus GPT-4.1 endpoint improvement, this supports broader progress in code-generated neuroscience procedures while showing that specialist comparison is a separate question. Best-general selection uses older models on some tasks, so these 10 wins are not all GPT-6.1 wins. The 24/30 all-reference result must not be described as beating 24 specialists.

No result measures direct pretrained-model inference. No new training or model calls were performed for this analysis.
