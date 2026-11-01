# B08: older-model extension

Category B; original contract: [task folder](../../../B08/). Exact prompt: [prompt.txt](../../../../experiments/B08/prompt.txt).

Prompt SHA256: `7572f4c6280846afd010cd76e368f64121dc1379dab09adb88f16d8c1fd40b6d`. One unchanged program per model, reused across 1 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | batch-v11 | measured | 10.79480738185973 | True | [record](../../../../experiments/generation-extension-v1/artifacts/B08/gpt-4.1-2025-04-14/batch-v11/result.json) |
| gpt-5-2025-08-07 | batch-v11 | measured | 8.1652552072995 | True | [record](../../../../experiments/generation-extension-v1/artifacts/B08/gpt-5-2025-08-07/batch-v11/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/B08/), [slice artifacts and logs](../../artifacts/B08/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
