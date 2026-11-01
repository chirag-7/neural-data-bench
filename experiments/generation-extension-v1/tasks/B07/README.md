# B07: older-model extension

Category B; original contract: [task folder](../../../B07/). Exact prompt: [prompt.txt](../../../../experiments/B07/prompt.txt).

Prompt SHA256: `777c70b21cad61c1d9f3e6570eeead07001eb8cbeead506c3bcaf2354f5ce0b0`. One unchanged program per model, reused across 1 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | compression-v1 | measured | 6.63548723856608 | True | [record](../../../../experiments/generation-extension-v1/artifacts/B07/gpt-4.1-2025-04-14/compression-v1/result.json) |
| gpt-5-2025-08-07 | compression-v1 | failed | missing | True | [record](../../../../experiments/generation-extension-v1/artifacts/B07/gpt-5-2025-08-07/compression-v1/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/B07/), [slice artifacts and logs](../../artifacts/B07/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
