# K01: older-model extension

Category K; original contract: [task folder](../../../K01/). Exact prompt: [prompt.txt](../../../../experiments/K01/prompt.txt).

Prompt SHA256: `e25facd2e8f286ab6593c710ead89f41b411934a38b0668bcc054f1d7e50ceb7`. One unchanged program per model, reused across 1 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | expansion-v1 | measured | 0.9277844018905058 | True | [record](../../../../experiments/generation-extension-v1/artifacts/K01/gpt-4.1-2025-04-14/expansion-v1/result.json) |
| gpt-5-2025-08-07 | expansion-v1 | measured | 0.9321663019693655 | True | [record](../../../../experiments/generation-extension-v1/artifacts/K01/gpt-5-2025-08-07/expansion-v1/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/K01/), [slice artifacts and logs](../../artifacts/K01/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
