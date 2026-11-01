# Methods: four-model extension

The current display includes pinned GPT-4.1-2025-04-14 and GPT-5-2025-08-07 API snapshots plus the existing GPT-5.6Sol and GPT-6.1Sol procedures. GPT-6 Sol is retained in historical artifacts, not the current comparison.

## Estimand and exclusions

Thirty tasks span fourteen categories and 37 evaluation slices per model. Each task uses its existing primary metric and direction. A model’s task score is the equal-slice native mean only if every slice is valid. Failed/missing scores are incomplete; zero is never substituted. Six ordered model pairs are compared by the sign of their task-native mean difference, with numerical tolerance 1e-9. Metric magnitudes are never pooled across tasks. Family-balanced signed direction first averages signs within family, excluding incomplete pairs, then averages families with a valid pair; coverage is retained. This is not a significance test.

The observed-data sensitivity excludes B01, B03, L06, M04 (fully synthetic), B08 (protocol ambiguity) and N05 (single-file correctness). The default final usability view applies documented repairs to existing selected Sol procedures and separately versioned API-generation repairs, while the first-attempt sensitivity retains original failures. Original frozen measurements, summary, catalog and historical analyses are not changed. Missing C05 archived reference predictions remain unresolved and are not padded or imputed.

## Interpretation limits

Model order is an ordinal display convention, not training compute, size, release-time spacing or a scaling-law independent variable. End-point slopes are descriptive only. One new program per task/model and existing selectively repaired older procedures do not support unbiased population claims about model generations. GPT-4.1/GPT-5 are direct API calls whereas the Sol runs used the Codex environment. Wrapper instructions, exposed tools, reasoning budgets and execution histories can confound model differences; inspect the extension provider metadata and execution seal. No model-selection oracle should be treated as deployable performance.

Native ties are numerical, not demonstrated practical equivalence. A higher correlation can coexist with worse calibration; near-chance C2ST and nearly identical numerical estimators require special care. Reusing the frozen tested references makes extension comparisons consistent, but does not establish current specialist state of the art. Review links identify candidates, not unexecuted best scores. No broad replacement recommendation or future crossover forecast is justified.

## Provenance

Input SHA256 hashes, extension metadata, retained code and scored-output hashes are recorded in generation-comparison.json and the extension record. Runtime/library/shape fixes, optimizer changes for the same training objective, and AST-identical formatting are recorded separately. No test-label or test-score-based model search is performed. Scores of manually repaired procedures cannot establish what the original model would do autonomously. No new measured score is invented. Historical GPT-6 results remain accessible through the prior report. Regenerate with python3 scripts/build_generation_comparison_v2.py after all 74 extension rows exist; run python3 scripts/check_generation_comparison_v2.py for structural checks.
