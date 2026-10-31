# Preview 0.8: two more real-data candidates executed

This release adds **K04 cortical-layer transfer** and **M01 conditional mouse-choice prediction**, with original data, biological grouping, named references and exact scorers. Both are custom research diagnostics. The first-submission panel now contains **21 tasks and 81 model–slice attempts: 79 valid predictions and two unrepaired failures**. It has 162 total model/reference records. All six new model submissions satisfy the format and runtime requirements.

The separate H02 repeated-generation study remains outside these macro denominators. Earlier measurements are unchanged.

## Results

| Task / native metric | GPT-5.6 Sol | GPT-6 Sol | GPT-6.1 Sol | Named reference |
|---|---:|---:|---:|---:|
| K04: section-equal, seven-class macro-F1 ↑ | 0.505071 | 0.531942 | 0.550550 | SingleR: **0.554585** |
| M01: mouse-equal binary log-loss ↓ | 0.436515 | 0.437584 | 0.436634 | Paper-inspired behavioral GLM: **0.463877** |

K04 uses all 12 original DLPFC count matrices: two training donors with eight sections, and one held-out donor with four sections. Each spot has 500 training-selected expression features. Curated layer labels use histology and expression assistance. This is supervised expression-to-layer transfer, not unsupervised spatial clustering. The official SingleR implementation uses training-only donor-layer reference profiles and the same 500 features. It leads all three models on the mean point score, although GPT-6.1 leads on two of four sections. Those four sections are one person, so this does not establish population equivalence or superiority.

M01 uses all 100 animals in the original CC BY 4.0 IBL 2019 archive: 83 training and 17 held-out mice, across nine overlapping labs. Latest complete sessions and disjoint six-trial blocks give 7,696 training and 1,842 test examples. Inputs include the known experimenter block prior and five observed past choices/feedbacks. No evaluated target appears in another example's history. This measures conditional forecasting with known context, not autonomous rollout or transfer to a new laboratory. All three models beat this source-inspired GLM, on 14/17, 13/17 and 14/17 mice respectively. Differences between the Sol versions are tiny and nonmonotonic. The reference is not an established strongest specialist.

## Auditing and changes

- Scientific contract commit `74b8244` predates all new model generations and fitted-method test scores. No repairs or test-based method selection followed.
- Independent checks verify all 12 count-source hashes, author donor metadata, all curated target joins, 36 spot normalizations and the exact 500 genes chosen using training data only. Every one of the 9,538 behavioral examples independently matches the original arrays; target and history trial sets are disjoint.
- All ten new prediction files were independently rescored. Nine agree within 1e−12. The float32 GLM reference differs from independent float64 loss arithmetic by 9.07e−9 in the mean and at most 5.42e−8 per mouse, below one float32 epsilon. Frozen scores and predictions are retained. An initial reversed annotation-join key in the independent verifier was corrected without changing scientific artifacts.
- The entire 0.7 first-submission panel is preserved byte-for-byte in the [historical snapshot](../results/archive/v07-measurements.jsonl). New task rows extend the current panel; integrity checks require all earlier records to remain unchanged. The current panel and separate H02 follow-up contain 163 unique stored prediction files.
- Source and score provenance, every new model generation log, unchanged programs and reference definitions remain inspectable in the [K04 worklog](../experiments/K04/worklog.md) and [M01 worklog](../experiments/M01/worklog.md). [Paired unit diagnostics](../analysis/v08-unit-comparisons.json) are descriptive, not significance tests.

## Additional candidates screened

B06's current full ephys-atlas tables require authenticated source access; public software test fixtures were not substituted. L01's listed ETH mirror returned HTTP 403; other mirrors were not exhaustively tried. MODA provides public annotations, but its original MASS PSG records require a separate authorized data request, so that H18 extension was not scored. These remain pending/deferred candidates with source-specific reasons. [Admission evidence](../literature/admission-v08.json).

The active catalog remains at 96 entries: **21 measured, 47 pending validation and 28 deferred**. Another 18 historical candidates remain archived. No task was selected or dropped because of its resulting model score. Independent sources, repeated generations on other tasks, stronger specialist configurations and prospective task selection remain necessary. This is not an exhaustive review or a paper-ready comparison across all neuroscience.

[Current findings](../analysis/findings.md) · [Coverage](coverage-matrix.md) · [Reproduction](reproduce.md) · [Previous release](release-v07.md)
