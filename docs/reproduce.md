# Reproduce the exploratory release

The frozen programs can be rerun without any model account. Model generation is a separate optional step and consumes the signed-in provider account’s usage.

```sh
git clone https://github.com/chirag-7/neural-data-bench.git
cd neural-data-bench
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/acquire_spikefinder.py
python scripts/evaluate.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python scripts/cognitive_reference_audit.py
python scripts/summarize.py
python scripts/validate.py
python scripts/build_website.py
python -m http.server 8765 --directory website --bind 127.0.0.1
```

The acquisition script downloads ~hundreds of MB from pinned public releases and writes checksums into `data/manifests/`. Check upstream data terms before use. `evaluate.py` enforces a 180-second subprocess wall limit for each estimator and sets numerical thread environment variables. It preserves failures. The post-hoc reference audit is a trusted project script with no model calls; its measured runtime includes both coarse and fine quadrature.

Expected scalar outputs are in `results/measurements.csv`; floating-point and runtime differences across platforms are possible. Prediction ZIP hashes may differ on regeneration even if array values match. Inputs and code hashes are the traceable identity, and scorer agreement is checked numerically. The validation script does not call models or retrain estimators. It needs acquired data and completed stored predictions; this is not a zero-data CI test.

The original `experiments/C05/pilot-v1` bundle preserves the previous workspace’s layout assumptions; use the canonical `scripts/` commands above after cloning. A full rerun replaces local result files; use a new checkout or commit before running if preserving prior measurements.

## Regenerate model submissions

The run used the installed Codex CLI, signed in through the local account. No API key is embedded. Use a fresh empty working directory and absolute paths for each model/task. Example with placeholders:

```sh
codex exec --ephemeral --ignore-user-config --skip-git-repo-check \
  --sandbox read-only --model gpt-6-sol \
  -c model_reasoning_effort=high \
  --output-schema /ABS/REPO/experiments/M04/response_schema.json \
  --output-last-message /ABS/NEW-RUN/gpt-6-sol.json \
  --json - < /ABS/REPO/experiments/M04/prompt.txt > /ABS/NEW-RUN/events.jsonl
```

Repeat for exact requested IDs `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol` and the chosen frozen task prompt. Availability and provider alias resolution may change. Do not overwrite the archived submission with a new generation and call it a reproduction: create a new run ID, preserve all attempts and record actual model/tool events. Explicit user prompts are identical within a task; CLI/provider instructions may differ between models. No model tool events were observed in the recorded runs.

Review code before local execution. The AST gate is not a security boundary for arbitrary contributed programs. External submissions need a genuine isolated execution service. No specialist code, test labels or execution feedback were supplied to the models during generation.
