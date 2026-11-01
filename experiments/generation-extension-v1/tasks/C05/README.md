# C05: older-model extension

Category C; original contract: [task folder](../../../C05/). Exact prompt: [prompt.txt](../../../../experiments/C05/pilot-v1/prompt.txt).

Prompt SHA256: `00b53eb24dffcad2a9f3d1c4696f7078165bd897b9bac2595f3fae5d2a784b5c`. One unchanged program per model, reused across 5 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | 1 | measured | 0.16330047113627907 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-4.1-2025-04-14/1/result.json) |
| gpt-4.1-2025-04-14 | 2 | measured | 0.17690287540577526 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-4.1-2025-04-14/2/result.json) |
| gpt-4.1-2025-04-14 | 3 | measured | 0.1700847934312566 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-4.1-2025-04-14/3/result.json) |
| gpt-4.1-2025-04-14 | 4 | measured | 0.22438365411304642 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-4.1-2025-04-14/4/result.json) |
| gpt-4.1-2025-04-14 | 5 | measured | 0.22188103727882047 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-4.1-2025-04-14/5/result.json) |
| gpt-5-2025-08-07 | 1 | measured | 0.5262673125438961 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-5-2025-08-07/1/result.json) |
| gpt-5-2025-08-07 | 2 | measured | 0.38747297558045757 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-5-2025-08-07/2/result.json) |
| gpt-5-2025-08-07 | 3 | measured | 0.3846425820908349 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-5-2025-08-07/3/result.json) |
| gpt-5-2025-08-07 | 4 | measured | 0.36158761058865024 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-5-2025-08-07/4/result.json) |
| gpt-5-2025-08-07 | 5 | measured | 0.44080952357720515 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C05/gpt-5-2025-08-07/5/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/C05/), [slice artifacts and logs](../../artifacts/C05/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
