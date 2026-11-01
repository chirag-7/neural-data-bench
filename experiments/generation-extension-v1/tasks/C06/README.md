# C06: older-model extension

Category C; original contract: [task folder](../../../C06/). Exact prompt: [prompt.txt](../../../../experiments/C06/prompt.txt).

Prompt SHA256: `11593c2e786bc00f549dbd9cd16378f54c4ae312627a21ce2c5768b12ed32670`. One unchanged program per model, reused across 1 dependent slice(s). No test scores or execution feedback were passed to generation.

| Snapshot | Slice | Status | Native score | Within line limit | Initial result |
|---|---|---|---:|---|---|
| gpt-4.1-2025-04-14 | batch-v11 | failed | missing | True | [record](../../../../experiments/generation-extension-v1/artifacts/C06/gpt-4.1-2025-04-14/batch-v11/result.json) |
| gpt-5-2025-08-07 | batch-v11 | measured | 0.49931548987762076 | True | [record](../../../../experiments/generation-extension-v1/artifacts/C06/gpt-5-2025-08-07/batch-v11/result.json) |

## Steps and interpretation

1. Verify the original prompt and generation/execution seals.
2. Generate one structured program through the restricted API bridge; retain the original provider response and code.
3. Execute under the frozen runtime and time/format contract; preserve errors unchanged.
4. Independently re-score successful saved outputs, or freshly decode each successful compression payload.
5. Consolidate these rows once with the full panel; no missing score is imputed.

[Generation responses and programs](../../generation/C06/), [slice artifacts and logs](../../artifacts/C06/), [overall methods](../../../../docs/generation-extension.md), [current four-model report](../../../../analysis/generation-comparison-v1/report.md).

These are direct API generations; historical Sol programs used Codex. A numeric score does not override a format deviation, demonstrate current-specialist superiority, or establish a scaling law.
