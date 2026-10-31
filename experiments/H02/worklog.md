# H02 preparation and execution log

2026-10-30 (America/New_York): Reviewed the old BNCI2014_008 deferral and searched primary ERP alternatives. Compared Brain Invaders2012/2013 releases; selected the complete smaller25-person2012 release, rather than a cherry-picked subset of larger2013 sessions. Original Zenodo API metadata explicitly identifies CC BY4.0. Pinned record2649069/v3, author-loader commit and file identities; did not infer data rights from a paper's license.

Acquired all25 original subject archives (~677MB), verified every publisher MD5 and computed SHA256. Inspected the first training matrix, original marker columns, timestamp spacing and independent CSV. The source loader lists17stored signal columns but excludes Fz as ground, giving16retained channels. Original markers identify768flash events/128targets for the first participant; this differs from a separate2013 protocol and was not silently substituted.

Defined all-source calibration-only input, subject01–15training versus16–25test, fixed filtering/baseline, no amplitude exclusion and only geometric-boundary skips, before any evaluated-model generation or reference score. Independently verified MAT/CSV flash and target columns across all25people and exact128Hz MAT clock. Prepared11,481training and7,663test epochs,16channels×128samples. Ten independent test people define primary aggregation, not7,663independent people.

Verified constant-score ROC-AUC0.5, perfect-ranking fixture1.0, and independent rank-sum equivalence with tied random scores. These are scorer fixtures, not scored model methods. Training-person identifiers are supplied equally to general models and references, so valid grouped validation is possible. Test identifiers and targets remain scorer-only. The published xDAWN configuration and conventional LDA configuration are fixed before generation.

A metadata export initially expected an optional `version` key absent from Zenodo's API; record identity and the publisher page's v3 label were used explicitly before preparation/model freeze. This was a metadata-handling repair, with no dataset/score selection. All subsequent source checksum and preparation checks passed.

Frozen contract and model execution outcomes are recorded in `run-spec.json`, exact submissions, generation provenance and the central task records. No unrecorded model generations or score-driven repairs are allowed. The evaluation section will be appended after all attempts finish.

## Completed evaluation

Frozen local commit `d0f636f` predates model generation. One successful no-tool generation per requested model, high reasoning; unchanged programs have154/115/190lines. All fit calls complete within180seconds.

- gpt-5.6-sol: measured, person-equal ROC-AUC=0.7571945899092973, execution seconds=1.3594105001538992.
- gpt-6-sol: measured, person-equal ROC-AUC=0.73054818684538, execution seconds=0.39200912485830486.
- gpt-6.1-sol: measured, person-equal ROC-AUC=0.7885365446735593, execution seconds=2.4475768750999123.
- task-baseline: measured, person-equal ROC-AUC=0.7218908794859147, execution seconds=0.14297358389012516.
- xdawn-tslr: measured, person-equal ROC-AUC=0.7612303198299977, execution seconds=3.4599052499979734.

All five predictions match stored hashes. Independent rank-sum person AUCs and group aggregation reproduce scores to1e−12. An initial independent verifier accumulated float32 ranks for the LDA baseline and differed by up to2.6e−8; using float64 rank accumulation resolved the verifier precision issue without changing predictions or scores. See[result verification](result-verification.json). No model repair, threshold selection or new data exclusion followed test scores.

## Retrospective 0.7 follow-up

After original scores were known, froze the unchanged-prompt two-generation follow-up and training-only specialist selection in commit `9c67ae9` before new generation or reference fitting. Six no-tool fresh submissions all pass format and runtime requirements. Five-fold grouped validation selects 4 filters, both templates, C=10; equal-person test AUC 0.7785407675. Original primary records were not replaced. All 12 H02 prediction records and all 12 specialist OOF candidate scores pass independent rank-based checks. [Every result and limits](replication-v1/results.md).
