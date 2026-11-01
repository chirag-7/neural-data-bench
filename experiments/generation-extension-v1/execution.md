# Execution extension: original data and scorer reuse

The standalone runner is `scripts/extension_evaluate.py`. It never writes original experiment, prediction or score-ledger paths. It runs the **same 37 slices** for each of `gpt-4.1-2025-04-14` and `gpt-5-2025-08-07` using one submission per task, including one C05 submission across five preparations and unchanged E01/E06 programs across dependent slices.

## Entry points

Use the bundled scientific Python and absolute `PYTHONPATH` entries for `work/cell-deps`, `work/pilot-deps` and `work/spike-deps`, in that order. Set `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, `MKL_NUM_THREADS` and `VECLIB_MAXIMUM_THREADS` to `1`.

- `python scripts/extension_evaluate.py --freeze`: once, before generation. Saves `execution-seal.json` containing original prompts, adapters, protocol/scorer source, local input/target files, source ledger, extension manifest, runner, Python executable and package-entry hashes plus runtime versions. Checks original `frozen_files` hashes before creating the seal. Does not execute a submission.
- `python scripts/extension_evaluate.py --check`: verifies all sealed inputs/runtime.
- `python scripts/extension_evaluate.py --one TASK SLICE MODEL`: consumes top-level `description`/`code` JSON from `submissions/TASK/MODEL.json`; final stdout line is a result object. Existing case directories cause an error; first failures cannot silently be overwritten.
- `python scripts/extension_evaluate.py --audit-saved TASK SLICE MODEL`: scorer-only rerun for retained numerical outputs, or independent decode audit for compression. Writes repeat evidence and logs under a unique `audits/UTC_TIMESTAMP/` directory, including L06 classifier audits. Does not replace the initial result, initial audit files or payloads. It is not another model attempt.

Outputs go to `artifacts/TASK/MODEL/SLICE/`. This includes started metadata, exact submitted source, prediction files or codec blobs, stdout/stderr logs, scoring evidence, initial failure traceback if applicable, and `result.json`. The parent orchestration collects per-case objects into the **object-shaped** `results/generation-extension-v1.json`; the original ledger is not rewritten.

## Execution and scoring

Procedure and scorer run in separate fresh subprocesses. The procedure has a **180 second wall limit including its setup/load**, one numerical thread; scoring has a separate 1800 second limit. Memory is requested, not enforced, as in the original study. No automatic code repair, regeneration or score feedback is allowed. AST checks enforce the import/call contract; they are **not a hostile-code security sandbox**.

Numerical predictions are retained before scoring. The scorer reuses the frozen task-specific adapter methods, the original C05/M04 scoring code, the original N05 deterministic scorer and the original L06 C2ST implementation. B01 keeps official SpikeInterface unit matching; E01 keeps original NaN-mask/count normalization; C05 keeps the original full-support/40ms-correlation contract. Thus numerical validation failures are preserved rather than patched or masked.

For B07/B08, every payload is saved and validated with a decoder in a new namespace during the procedure. Before a result becomes measured, **each blob is also decoded in its own fresh subprocess**, with checks against the unchanged original data. This additional audit does not permit a slower encoder or change the 180 second procedure allowance. All returned bytes count toward the original equal-recording mean size metric.

B08 explicitly adds only `heapq` to the ordinary allowed imports, matching the documented repaired harness used for the existing final panel. Original prompt bytes are unchanged; this amendment is recorded in the execution seal. Other import/line policies remain the original task policies. C05 is below 180 lines; all other tasks below 240. As in the previous ledger, over-limit valid numerical outputs retain their numerical score alongside a false format-compliance flag.

## Validation before generation

A scorer-only regression using original saved predictions matched **34/34 ordinary numerical/file slices exactly**, with zero score difference, including five C05 preparations and all E01/E06 transfer slices. No generated program was executed during this check. All 642 execution-seal candidate paths were present and all 164 embedded original `frozen_files` hashes matched. The B07 and B08 size formulas also reproduced their saved-payload ledger scores exactly (metric-only checks, not new decode checks). B07/B08 use the original metric formulas; their new submissions additionally require the fresh-process payload audit. The L06 saved-output C2ST check reproduced the aggregate score exactly (0.5125000059604645), and all five classifier-audit arrays matched the original byte-for-byte in numerical content. Its first test-harness report had a scratch-path bookkeeping exception after completing scoring; this did not affect C2ST and the reusable regression now directs its classifier audit to a repository-relative cache path.

The reusable regression is `tests/extension_scorer_regression.py --scratch ABSOLUTE_DIRECTORY`; add `--include-posterior` for L06. It verifies original saved prediction hashes, writes scratch copies and a scratch report (plus a repository-relative L06 audit cache when requested), and never adds model results.

## Interpretation

These are one generation per task through the public Responses API, versus earlier Codex/Sol wrappers. Explicit prompt bytes are identical, but provider/system wrapper and reasoning controls differ; GPT-4.1 has no matching reasoning-effort control. This extension adds useful historical comparison points, **not a controlled compute scaling law**. Preserve first-shot and any later repair-assisted evidence as distinct tracks. No global-best specialist claim follows from a local reference win.
