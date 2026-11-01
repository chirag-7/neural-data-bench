# Adding GPT-4.1 and GPT-5

The requested current comparison is GPT-4.1, GPT-5, GPT-5.6 Sol and GPT-6.1 Sol. GPT-6 Sol remains in the historical source ledger and earlier reports. The new experiment reuses all 30 existing tasks, covering 14 categories and 37 slices per model; it does not expand neuroscience coverage.

## What is held fixed

Each new model receives the exact saved original task prompt, without test labels, previous code, previous scores or execution feedback. One API generation produces one program, reused unchanged across that task's dependent slices. The model snapshots are `gpt-4.1-2025-04-14` and `gpt-5-2025-08-07`. GPT-5 uses high reasoning; GPT-4.1 has no corresponding setting. Both use structured JSON output, no tools and `store:false`. The original prompts occasionally mention the original Sol study; their bytes are retained, while the requested and returned API model IDs establish the new model's identity.

[Prospective plan](../experiments/generation-extension-v1/plan.md), [task/prompt manifest](../experiments/generation-extension-v1/manifest.json), [generation seal](../experiments/generation-extension-v1/generation-seal.json), [execution seal](../experiments/generation-extension-v1/execution-seal.json) and [execution details](../experiments/generation-extension-v1/execution.md) distinguish preparations from completed measurements. The manifest's preparation status is historical and sealed; final completion belongs in a separate run-status file.

## Reproducibility and failures

Every provider request, response, program and provenance record is retained under `experiments/generation-extension-v1/generation/{task}/{snapshot}/`. Every evaluated slice retains its code, procedure log, scored output, result and hashes under `artifacts/{task}/{snapshot}/{slice}/`. These decentralized records supply task-level detail; the consolidated result and comparison report supply the overall picture.

The sealed evaluator uses the original data, adapters and metrics. Program execution has a 180-second wall limit including setup; scoring has a separate 1,800-second limit. Compression outputs require independent decoding in fresh processes. Numeric results that exceed the original line limit remain visibly noncompliant. Syntax errors, missing values, timeouts and method failures remain failures; they are not repaired into the first-attempt result.

A local sandbox initially blocked 28 loopback client invocations before they reached the bridge. Their records are preserved in `transport-failures/`, with an explicit [transport amendment](../experiments/generation-extension-v1/transport-amendment.json). Identical sealed requests resume with network permission; these local failures are not model generations or scientific failures. API request IDs and the bridge ledger establish actual provider calls. Disjoint tasks may run concurrently; CPU evaluation is limited to two cases at a time with numerical-library threads fixed to one.

## Spending and access

The user approved a dedicated restricted API key and a conservative $15 application ceiling. The bridge reserves the maximum allowed request cost before dispatch and substitutes token-usage cost on completion. It never purchases additional credit or recharges the account. [The cost ledger](../experiments/generation-extension-v1/api-cost-ledger.json) records nonsecret request metadata and conservative cost using uncached token rates. The credential is held only in local-process memory and is not part of the repository or website.

## What the comparison can establish

The new API calls and historical Codex Sol procedures have different provider wrappers, reasoning settings and histories. Selective repairs to historical programs are reported as a separate final-usability sensitivity, with the original first-attempt comparison retained. This is an exploratory comparison of generated analysis programs on fixed custom contracts, not a controlled estimate of generation effects, native raw-data intelligence or an autonomous scientist.

Task-native differences, all six model-pair directions and category-balanced directional summaries are appropriate descriptive outcomes. Scores from different metrics cannot be averaged directly. Model order does not measure training compute; four ordered points cannot establish a scaling law or forecast when specialists will be surpassed. Existing tested references and current-specialist literature candidates are distinct: an unexecuted literature model never becomes a plotted measured score.

After all attempts and audits finish, regenerate the current website data once with `scripts/build_generation_comparison.py` and validate it with `scripts/check_generation_comparison.py`. The original sealed ledgers and earlier macro reports remain intact.
