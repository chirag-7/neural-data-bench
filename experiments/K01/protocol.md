# K01: physiology-to-morphology classification, frozen slice v1

This is a real-data, newly constructed supervised task. It asks whether electrophysiological features predict an independently annotated binary dendritic morphology class in previously unseen mice. It does not evaluate full cell taxonomy discovery or direct LLM classification. Model-generated programs fit estimators to supplied training arrays; root experiment harness records exact model/prompt/runtime budgets.

## Data and endpoint

[Allen Cell Types Database](https://celltypes.brain-map.org/) provides measured patch-clamp features and independently annotated morphology tags. [Primary API documentation](https://brain-map.org/support/documentation/cell-types-database-api) distinguishes electrophysiological features from morphology features and describes the dendrite annotations. The same API endpoint used by AllenSDK was downloaded in full on 2026-10-30: 2,333 records. Keep mouse cells annotated spiny or aspiny (1,813 cells, 904 donor IDs); exclude all 413 human cells and 107 sparsely-spiny mouse cells. The target is spiny=1, aspiny=0. Each cell contributes one row.

Inputs are the 11 named `ef__` summary electrophysiological features exposed by the primary metadata table. No dendrite, reconstruction, morphology, soma position, layer, genetic line, donor, specimen, filename, or species variable enters the feature matrix. Missing values remain NaN until an estimator imputes using training data. This deliberately narrow endpoint is different from transcriptomic label prediction.

## Split and leakage controls

Sort eligible records by numeric specimen ID. Split donors using sklearn GroupShuffleSplit(test_size=0.25, random_state=20261030), once. Cells from the same mouse never cross train/test. Test labels are held by the external scorer; prompts receive schema and train/test input shapes, not test labels. Imputation/model selection cannot fit on test cells. Donor groups and original specimen IDs remain in the ignored prepared cache for leakage audit and grouped uncertainty, and are not predictive features. A deterministic split chosen before baseline/model performance is observed is not subsequently revised to improve scores.

## Metric and reference

Primary metric is pooled test-cell macro-F1, with balanced accuracy a possible secondary metric. Any uncertainty should resample donor blocks, not treat cells as independent mice. The preregistered conventional baseline chooses between RandomForestClassifier and ExtraTreesClassifier (500 trees, balanced classes, seed 20261030, one CPU thread), each with train-only median imputation and missingness indicators, by mean macro-F1 in three GroupKFold training folds. Ties choose random forest. It then refits using all training cells and predicts held-out cells. No tuning uses test labels. This is a strong conventional tabular baseline, not a verified current neuroscience specialist SOTA; published scores with other endpoints/splits are not comparable.

## Interpretation limits

The narrow binary morphology task cannot establish that a general model matches molecular or multimodal cell-type classifiers. Genetically targeted collection and stimulus-selection confounds remain, even when such metadata are excluded. Source annotations may be imperfect. Single-institute held-out mice do not establish cross-lab transfer; publicly accessible data may have entered model pretraining. This slice must be counted once in cross-task analysis, with this cohort/dataset family explicit.

## Use terms and reproduction

The [Allen Institute Terms of Use](https://alleninstitute.org/terms-of-use/) allow research/noncommercial use with attribution. These data are not relicensed under the repository code license. Raw/prepared data remain in ignored `data/cache/K01`; the downloader, provenance URL, SHA-256, dataset attribution and preparation specification are tracked in `data/manifests/K01.json`. Run `python experiments/K01/adapter.py` with the pinned numerical environment to acquire/prepare. Frozen metadata and exact membership are regenerated deterministically from the raw snapshot; a source change will change its recorded hash.

## Worklog

- 2026-10-30: Read primary AllenSDK API/example documentation and Cell Types API documentation. Retrieved the complete metadata API response, checked its success/row counts, reviewed species/class counts and donor multiplicities. Also retrieved full EphysFeature table during discovery; it is not used because the 11 predeclared public summary features are sufficient and easier to audit.
- 2026-10-30: Wrote endpoint, features, split, baseline selection and scoring plan before running model programs or scoring the baseline. Prepared data with donor-overlap and unique-cell assertions. Further execution results are recorded separately by the central harness.
