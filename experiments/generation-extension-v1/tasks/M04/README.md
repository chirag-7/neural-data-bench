# M04: older-model extension

Category M; original contract: [task folder](../../../M04/). Exact prompt: [prompt.txt](../../../../experiments/M04/prompt.txt).

Prompt SHA256: `a2dabc0280992e3d59521b83b15b027437590d02e2e116b6e5788a8229e24600`. One unchanged program per model, reused across 1 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | synthetic-v1 | measured | 0.07069645781617521 | True | [record](../../../../experiments/generation-extension-v1/artifacts/M04/gpt-4.1-2025-04-14/synthetic-v1/result.json) |
| gpt-5-2025-08-07 | synthetic-v1 | measured | 0.07069656357491515 | True | [record](../../../../experiments/generation-extension-v1/artifacts/M04/gpt-5-2025-08-07/synthetic-v1/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/M04/), [slice artifacts and logs](../../artifacts/M04/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
