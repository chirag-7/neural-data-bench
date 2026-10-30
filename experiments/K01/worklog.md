# K01 actual worklog

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: macro_f 1=0.940914510638; formatting compliant.
- gpt-6-sol: macro_f 1=0.940914510638; formatting compliant.
- gpt-6.1-sol: macro_f 1=0.943074240159; formatting compliant.

Reference: task-baseline; Local conventional task baseline; strongest specialist unverified. Current strongest specialist unverified. [Full result records](../../results/K01.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/K01/). No statistical significance claim.

Harness amendment: initial subgroup validator incorrectly demanded predictions belong to the labels present in each single-class donor. Corrected to fixed valid label set; single-class group reports accuracy. Original logs in [harness attempts](../../results/execution/harness-attempts/) and [attempt file](harness-attempt-1.json). Unchanged programs rerun; no model feedback/repair. Inner CV donor metadata differed between baseline and submissions.
