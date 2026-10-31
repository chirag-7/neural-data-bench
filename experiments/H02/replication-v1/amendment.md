# H02 generation replication and tuned-specialist sensitivity

This follow-up was specified after inspecting the original H02 test results. It is **retrospective**, not an independent confirmatory experiment. Original prompt, preprocessing, programs, predictions, endpoint and primary macro records remain unchanged.

## Questions and fixed plan

1. How variable are fresh no-feedback code submissions? Generate exactly two additional submissions per requested model (replicates 2 and 3), with the original identical user prompt, response schema, high reasoning effort and fresh empty working directories. Keep all attempts; no best-of-three selection, repair or score feedback. Each program receives the original 180-second, one-thread numerical fitting limit and fewer-than-240-line rule. Record failures and format compliance separately.
2. Does train-only selection strengthen the xDAWN reference? On the original 15 training people, use deterministic five-fold GroupKFold. For every validation fold fit xDAWN covariance estimation, tangent reference, feature scaling and logistic regression using fold-training people only. Compare nfilter {2,4}, template classes {target only, both classes}, logistic C {0.1,1,10}: 12 configurations. Other settings match the original fixed reference. Average ROC-AUC equally over the 15 validation people; choose highest AUC, breaking exact ties by declared grid order. Refit that configuration on all training people. Test people never enter selection or transform fitting. Limit complete selection and final inference to 180 seconds on one numerical thread. If it fails, retain the failure rather than using a partially searched winner.

## Reporting and boundaries

Report every generated program, score, runtime, per-person score and compliance flag. Descriptive model summaries use all three planned attempts (original plus two new); report valid count and strict-valid count, mean and range of valid scores, and each attempt. Failed attempts have no numerical score, never an invented zero. Do not use the best attempt as model performance. The original generation occurred before this follow-up and is not exchangeable under a prospectively randomized generation schedule. Provider-side instructions/backend snapshots cannot be independently controlled; the explicit user prompt is identical.

The new specialist is an additional sensitivity reference, not a replacement for the original frozen primary comparator. Same numerical fitting timeout does not establish equal developer effort, hyperparameter search or training budget. No global strongest-method claim is supported. All test scores are revealed only after the complete candidate choice is persisted.

Three code generations are not three datasets, independent cohorts or new benchmark tasks. Keep replication records out of the original 75-attempt and 19-task macro analysis. Means/ranges over three generations are descriptive; no general model scaling or population-wide superiority inference follows. Ten test people support paired person-level diagnostics but do not resolve dataset selection or generation uncertainty.

## Provenance

Commit this plan, the runner, and the tuned-specialist implementation before generating any follow-up programs or fitting the tuned reference. Seal their SHA-256 hashes together with the original prompt, adapter and prepared data. Independently rescore saved predictions and confirm train/validation group disjointness before release.
