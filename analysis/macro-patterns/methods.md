# Macro analysis methods

This is an explicitly retrospective analysis of measurement snapshot 0.11. The script reads the exact frozen central ledger and summary, records their SHA256s, and checks they remain unchanged. It does not call models, alter submissions, fit references or rescore scientific outputs.

## Units, scopes and outcomes

Observed scope excludes B01/B03/L06/M04 (fully synthetic), N05 (deterministic correctness) and B08 (ambiguous utility-import contract). A14/H16 observed sources with artificial corruption remain included. That leaves 24 tasks, 13 families and 31 slices; not 24 independent biological cohorts. Synthetic-inclusive scope restores B01/B03/L06 but retains M04/N05/B08 exclusions. B08 exclusion was decided in the prior batch after its failure and remains explicitly retrospective.

A valid newer-minus-older metric delta is multiplied by +1 for higher-is-better and −1 for lower-is-better. Above 1e−9 is a point win, below −1e−9 a point loss, otherwise a numerical tie. No practical-equivalence margin was prospectively specified. Raw paired score margins, direction and metric units are exported; incompatible metric sizes are never averaged. Within-slice three-model ranks (1 best, average exact ties) are secondary complete-case descriptions, not another selected hypothesis test.

For directional win fractions, each slice is a win indicator; slices average within task, tasks within family and families equally. Denominator policy retains failed/missing pairs as nonwins, without a numeric score. The main signed diagnostic instead treats a newer-only numerical failure as a loss and older-only failure as a win; both failed is zero. Strict filters use code-format flags and explicitly report their reduced panel. Common-three-model strict complete support prevents pair-dependent panel composition. No source dataset, neuron, frame or parameter is counted as another task.

## Statistical diagnostics

Main statistic: equal-family mean of within-family mean task signed win fractions. Enumerate all 2^13 family sign reversals for a two-sided reference distribution; include null values whose absolute magnitude is at least the observed magnitude (1e−12 floating tolerance). This is exact enumeration under a symmetric independent-family null, not an exact randomized experiment. Family grouping reduces obvious within-category dependence but does not prove between-family independence. The three version contrasts are one retrospective family for Holm step-down adjustment. Alternative scopes, compliance filters, ranks and missingness policies are sensitivity descriptions, not searches for significance; Holm does not correct the entire historical research process.

Family-composition sensitivity: draw 20,000 bootstrap samples of 13 whole families with replacement (NumPy seed 20261031), averaging each sampled family's fixed directional win fraction. The 2.5/97.5 percentiles describe this empirical benchmark composition, not biological population, code-generation, prompt or provider confidence. Leave-one-family-out removes each whole family. These do not replace missing repeated generations or independent source cohorts.

Reference comparisons are stratified by the existing frozen/local/historical reference policy. Failure stays visible. Differences between strata are descriptive because the tasks, sample sizes, information and optimization histories differ. No causal specialist-class effect or current-SOTA advantage is estimated. No normalized native utility, pooled scientific effect, scaling law or moderator regression is fit.

## Reproduction

Run scripts/analyze_macro.py with NumPy, SciPy and Matplotlib, then scripts/write_macro_report.py. Numerical output is deterministic at the pinned seed; graphics/PDF container metadata can vary by library. Run scripts/check_macro.py for a separate standard-library recomputation of the paired counts, family arithmetic and exact conditional p-values. The independent review documents interpretation limits. Requirements in requirements.txt describe the successful runtime; source hashes are in statistics.json.
