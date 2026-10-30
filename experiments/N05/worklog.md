# N05 actual worklog

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: FAILED; see execution log and central reason; formatting deviation retained unchanged.
- gpt-6-sol: field_accuracy=1; formatting compliant.
- gpt-6.1-sol: field_accuracy=1; formatting compliant.

Reference: task-baseline; Audited deterministic reference, correct by construction. Current strongest specialist unverified. [Full result records](../../results/N05.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/N05/). No statistical significance claim.

GPT-5.6 raised ValueError distinguishing stimulus sweep 19; preserved as a model failure, not repaired.249 code lines also exceeds requested<240. Other two models and audited reference matched 61 fields. One file sharedD02.
