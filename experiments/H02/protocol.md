# H02 — Subject-held-out P300 target ranking

## Question and data

Can a single general coding-model submission learn to rank target versus nontarget EEG responses in **new people**, compared with a conventional shrinkage-LDA reference and a fixed published xDAWN/Riemannian pipeline?

Use all25 people in [Brain Invaders2012 v3](https://zenodo.org/records/2649069), DOI10.5281/zenodo.2649069, original publisher metadata **CC BY4.0**. This is a newly admitted alternative to the previously deferred BNCI2014_008 source; the prior rights/protocol assessment is retained and not retroactively changed. The [dataset paper](https://arxiv.org/abs/1905.05182) and [pinned author loader](source-record.json) document the source. Data download and hash verification precede model generation.

Use only each person's `training.mat` calibration run, not their online run or its performance. People01–15 train;16–25 test. Identifiers, not target prevalence or model scores, define the split; use all eligible flash events. This is a custom cross-person offline diagnostic, not the paper's within-person online-game benchmark, target-symbol selection accuracy or clinical evaluation.

## Fixed input preparation

The author loader defines20columns: time,17stored EEG signals, an all-flash marker, and a target marker. Its nominal17channel list includes Fz as ground; remove Fz to retain16physical signals. Use original128Hz sample clock, checked independently against MAT timestamps. The two binary marker columns yield class0 when a flash is nontarget and class1 when the target marker is present. The target marker is a subset of the all-flash marker. These marker columns, identifiers and time are **never predictors**.

Common-average reference across the16retained channels; fixed fourth-order Butterworth0.5–20Hz zero-phase SOS filtering on each person's calibration recording separately. Retain128samples from flash onset (0≤t<1second). Subtract the preceding26samples' per-channel mean. The resulting float32 arrays have shape(trials,16,128), in the original author/MOABB microvolt convention. Exclude only events lacking required pre/post geometric support, never by amplitude, class or model score. All counts/skips are recorded. Compare MAT and separately supplied CSV event/target columns on every person. The whole original ZIP publisher MD5 and independently calculated SHA256 are retained.

Successive EEG responses can overlap within a person; these are not independent trials for population inference. No raw recording spans people or crosses training/test. Filtering is explicitly acausal and supports no online-latency claim. Source-provided preprocessing and public-data contamination remain limitations.

## General-model contract

`fit_predict(train_x,train_y,test_x,train_groups)` returns a finite real vector of length n_test, with **higher score meaning more likely target**. Any finite score scale is allowed; probability calibration is not required. `train_groups` identifies training people so subject-disjoint validation is possible. All three models and references have the same training signal/labels/group information. Test people labels/groups are available only to the scorer; do not infer test-row boundaries or fit normalization, covariances, thresholds or weights on held-out test inputs. Fixed per-epoch transforms are allowed. Supervised fitting and tuning use training data only.

Allowed general libraries NumPy/SciPy/scikit-learn and standard math/collections/functools/itertools/statistics/gc. No tools during generation, files/network/process access in submitted programs, specialist packages or pretrained assets. Exact requested models GPT-5.6 Sol, GPT-6 Sol, GPT-6.1 Sol; one generation each, high reasoning, no execution feedback/repair. The fit/predict call gets180seconds, one numerical thread, <240code lines. Approximate4GBmemory is requested but not enforced. All failures/format deviations remain.

## Frozen metric and references

Primary **equal-person mean ROC-AUC** across ten held-out people. Compute each person's target1/nontarget0 ROC-AUC using continuous scores, then average ten values equally. Secondary pooled-trial ROC-AUC and per-person ROC-AUCs are descriptive. Constant scores yield0.5; perfect target ranking1.0. No threshold-selected balanced-accuracy result, class-ratio oracle, frame/epoch bootstrap significance or mixed-metric aggregation is reported.

Conventional reference:16nonoverlapping temporal-bin averages per channel, then fixed shrinkage LDA (`solver=lsqr,shrinkage=auto`), raw decision scores. No search. Specialist: pyRiemann0.12 xDAWN covariance (`nfilter=4,classes=[1],estimator=oas,xdawn_estimator=oas`), Riemannian tangent space (`tsupdate=False`), fixed training-fitted standardization and logistic regression (`C=1,class_weight=balanced,solver=liblinear,max_iter=1000`). All spatial filters, target ERP templates, covariance mean and classifier parameters fit on training people only. These are source-motivated frozen configurations, not tuned current global best. [Official implementation](https://pyriemann.readthedocs.io/en/latest/generated/pyriemann.estimation.XdawnCovariances.html), [author ERP example](https://pyriemann.readthedocs.io/en/latest/auto_examples/biosignal-erp/plot_classify_EEG_tangentspace.html).

The specialist runs in its separate declared package environment. Fitting budgets, library implementations and upstream optimization effort differ; no matched-total-effort superiority claim. Freeze both adapter and specialist code before model generation or calculating either reference score. No score-dependent data selection, channel rejection or hyperparameter search.

## Scope and limits

One public dataset, a fixed identifier split and one model generation cannot establish clinical robustness, general neural understanding or a stable scaling trend. Twenty-five people improve grouping depth relative to earlier pilots but do not establish cross-lab/stimulus generalization. P300 is one ERP paradigm. No behavior, ocular channels, online feedback or symbol-selection task is modeled. Biological uncertainty and generation uncertainty remain distinct; trial/epoch counts do not increase the number of independent people.
