# I10 — MRI quality classification from published metrics

Exploratory custom IQM-classification slice, not raw-image inference or a new official benchmark result. Source: [Esteban et al. 2017](https://doi.org/10.1371/journal.pone.0184661); MRIQC tag0.10.5 commit c5767827abba6c1c01f7cc26b5fb1d0cd32a7fe8.

All600 ABIDE rows with nonmissing expert rater1 are training, all265 DS030 rater1 rows are test, one scan/participant. Innerjoin by cohort-local subject_id with unique rows. Numeric codes overlap between cohorts and are namespaced; this is not evidence of reused individuals. Cohort independence follows source study provenance, not globally unique codes. No ID/site/rater fields enter68 numeric IQMs. Verified original binary loader: rater1>=0 isinclude0; rater1=-1 isexclude1. Doubtful merged withaccept.

Primary balanced accuracy; macro-F1/accuracy secondary. Fixed local RF500 balanced, minleaf3, train-median imputation, seed20261030. Rescore archived2017 classifier predictions on exact265 DS030 rows separately; it used different rater-collapse/training/tuning history, so descriptive only. Current best unverified. Original feature loader excludes size/spacing; our declared68-feature diagnostic includes these geometry measurements, a documented deviation. Processed IQMs, no rawMRI/diagnosis/deployment claim. Keep rawtables cache-only; pinhashes.

Three Sol models, identical explicit prompt/schema, no tools/testlabels, highreasoning, onegenerationeach. Numericalbudget180seconds/oneCPUthread,<240lines, approx4GB unmeasured. Store predictions/failures/code/inputhashes. No testfeedback orrepair. Coarse cohort generalization is conditional on this slice and label policy.
