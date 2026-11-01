# E01: older-model extension

Category E; original contract: [task folder](../../../E01/). Exact prompt: [prompt.txt](../../../../experiments/E01/prompt.txt).

Prompt SHA256: `5227b10093eb9498f09a5a8625440d8192a730e5b5fdf92bb88e1e97a2c34ba2`. One unchanged program per model, reused across 3 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | area2_bump | measured | -4.560678768423565 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-4.1-2025-04-14/area2_bump/result.json) |
| gpt-4.1-2025-04-14 | dmfc_rsg | measured | -5.751959064142394 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-4.1-2025-04-14/dmfc_rsg/result.json) |
| gpt-4.1-2025-04-14 | expansion-v1 | measured | -2.51557852619588 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-4.1-2025-04-14/expansion-v1/result.json) |
| gpt-5-2025-08-07 | area2_bump | measured | -0.5584337929752483 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-5-2025-08-07/area2_bump/result.json) |
| gpt-5-2025-08-07 | dmfc_rsg | measured | -0.039874517261521296 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-5-2025-08-07/dmfc_rsg/result.json) |
| gpt-5-2025-08-07 | expansion-v1 | measured | -7.044147899884546 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E01/gpt-5-2025-08-07/expansion-v1/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/E01/), [slice artifacts and logs](../../artifacts/E01/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
