# E06: older-model extension

Category E; original contract: [task folder](../../../E06/). Exact prompt: [prompt.txt](../../../../experiments/E06/prompt.txt).

Prompt SHA256: `a9b8184757172ae629aa1cdf93d53927bc420d61356e7d6b66dc8b239230727e`. One unchanged program per model, reused across 2 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | batch-v11 | measured | 0.0029698043013463623 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E06/gpt-4.1-2025-04-14/batch-v11/result.json) |
| gpt-4.1-2025-04-14 | taxis | measured | 0.0028552200507541564 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E06/gpt-4.1-2025-04-14/taxis/result.json) |
| gpt-5-2025-08-07 | batch-v11 | measured | 0.004904289673106005 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E06/gpt-5-2025-08-07/batch-v11/result.json) |
| gpt-5-2025-08-07 | taxis | measured | 0.003983327066272407 | True | [record](../../../../experiments/generation-extension-v1/artifacts/E06/gpt-5-2025-08-07/taxis/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/E06/), [slice artifacts and logs](../../artifacts/E06/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
