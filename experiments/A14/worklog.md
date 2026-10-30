# Acquisition and preparation log

2026-10-30: Located primary DISK data-availability statement and followed concept record 15800034 to immutable version 18405201. Inspected CC BY4.0 metadata. Downloaded 246,184,002 byte raw Rat 7M mocap archive. Verified seven MAT recordings and mocap named landmark arrays, including naturally missing limb coordinates. Selected six measured head/spine markers and predefined whole-animal split 1–3 versus 4–5 before model generation. Defined nonoverlapping 31 frame windows with 60 frame stride; complete-window filter explicitly restricts population. Defined synthetic seven-frame HeadF mask with all targets from unchanged measured arrays. No model runs, tuning, or label-derived selection have occurred during preparation.

## v 0.4 execution record

Frozen task prompt/run-spec and adapter/fixture hashes were recorded before generation. Three exact requested model IDs, high reasoning, one no-tool CLI submission each, no test labels or execution feedback. Programs were reviewed and run unchanged with 180 sprocess limit/one numerical thread. All generated code and sanitized usage/tool events retained.

- gpt-5.6-sol: rmse_missing=0.448549356136; formatting compliant.
- gpt-6-sol: rmse_missing=0.436120867729; formatting compliant.
- gpt-6.1-sol: rmse_missing=0.450594888118; formatting compliant.

Reference: task-baseline; Local conventional task baseline; strongest specialist unverified. Current strongest specialist unverified. [Full result records](../../results/A14.json), [execution logs](../../results/execution/), [prediction artifacts](../../results/predictions/A14/). No statistical significance claim.
