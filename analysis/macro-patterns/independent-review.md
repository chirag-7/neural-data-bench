# Independent read-only macro review

Reviewed the amended script and statistics snapshot on 31 October 2026. No submitted model/reference was executed and no source score, program or analysis script was edited. Independently reconstructed comparisons directly from the unchanged 208-row ledger using rational arithmetic, without importing the analysis implementation.

## Arithmetic and grouping

No arithmetic or grouping error found for the current ledger: unique task/slice/model keys; comparable metric/direction within pairs; 31 observed slices, 24 tasks and 13 families. Slices average within tasks, then tasks within families. The main failure-penalized statistic correctly gives a newer-only failure a loss, an older-only failure a win, and a tie zero.

| Contrast | Family-equal signed direction | Exact two-sided sign-flip p | Holm p, three contrasts |
|---|---:|---:|---:|
| 5.6 → 6 | −17/260 = −0.065385 | 207/256 = 0.808594 | 1.0 |
| 5.6 → 6.1 | 14/65 = 0.215385 | 851/2048 = 0.415527 | 1.0 |
| 6 → 6.1 | 17/78 = 0.217949 | 457/1024 = 0.446289 | 1.0 |

All 8,192 sign patterns were independently checked, including duplicate patterns induced by zero family contrasts. Exact enumeration needs no Monte Carlo plus-one correction. Holm implementation is correct. The exact-equality rank convention and 1e-9 directional tie convention produce no nonzero-but-tiny tie discrepancies in this observed panel.

## Export-policy correction verified

The earlier neutral-failure/main-label ambiguity was corrected before final reporting. The amended JSON now names historical output descriptive_denominator and intended tests main_conservative. Independently checked the new main-conservative-tasks.csv and main-conservative-families.csv against every corresponding JSON contribution; all values agree. The main slice export correctly marks newer-only J08 failure as a loss. Historical paired CSVs carry an explicit descriptive-denominator analysis_policy, and console output now selects the conservative main statistic and p-value. Source scores remain unchanged. No outstanding arithmetic/export blocker was found in the amended files.

## Patterns that survive descriptive sensitivities

The latest version has a positive finite-panel directional summary against either older version in complete-case, pairwise strict, common-three-model strict, synthetic-inclusive and leave-one-family-out views. Main leave-one-family-out net ranges are 0.150000–0.316667 against 5.6 and 0.152778–0.319444 against 6. The common-three-model strict panel contains 23 slices, 20 tasks and 12 families; net directions are 0.347222 and 0.319444. Its exclusion of failed J08 removes an entire family, so larger values are not stronger statistical evidence on an unchanged population.

No consistent 5.6-to-6 improvement survives: the main net is negative, pairwise strict and synthetic-inclusive nets are negative, and common strict is nearly zero (−0.006944). Complete-case family mean ranks are 2.164583 / 2.153472 / 1.681944, favoring the latest version descriptively; they use a different 23-task/12-family numerical-support panel and include noncompliant numeric submissions. Nine of 30 complete numerical slices are nondecreasing across all three versions; ties are permitted in that definition. Those slices are not independent replications.

None of these observations rejects the stated family sign-flip null after Holm correction. Positive leave-one-family-out direction is a composition-robust descriptive pattern, not evidence of stable performance across new code generations, new sources or providers. Failure to reject also does not establish equivalence or no improvement.

## Interpretation limits

- Sign-flip probabilities are computationally exact conditional on independent, symmetric family contrasts. The convenience taxonomy, shared source collections and observational model ordering do not establish those assumptions or randomization.
- Family-bootstrap intervals describe resampling benchmark families only. The script does not implement a separate task bootstrap; do not call averaging tasks task resampling. No biological or generation confidence interpretation is warranted.
- Reference classes contain different tasks and unequal training/search budgets. Their bars support stratified descriptions, not a causal reference-choice effect, matched-effort superiority or global-best claims.
- C06 correlation can coexist with severe count-scale errors; retain nonnegative relative count error alongside signed bias, which can cancel. B01's post-hoc event metric changes the scientific interpretation without replacing the frozen primary.
- E06 main/taxis ordering changes on dependent slices of one brain. Different target activity/variance means raw MSE differences do not estimate an isolated source-shift or generalization penalty.
- Keep B08's retrospective exclusion and A15's line-cap violation explicit. Sensitivities are not extra confirmatory tests to search for a favorable result. H02 repetitions remain a separate same-source generation-variability case.

Direct ledger checks confirm that GPT-6.1 beats both older versions on K01, K04, K05 and K06, with all four tasks present in the common-three-model strict support. Among the reported observed-data families, K is the largest family with positive task direction against each older version on every included task (4/4); this is a retrospective descriptive category signal, not a significance claim. SingleR still exceeds GPT-6.1 on K04 (0.554585005 versus 0.550550191), so this consistency does not establish specialist superiority.

Snapshot SHA256: 69f8e361cccb1206846f84ccc72b4460c58201da59d382e0a531d6b97b68ace9
