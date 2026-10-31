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

## v 0.4 expanded protocols

Install repository requirements plus `h5py==3.15.1` for the N05 file reader. Data preparation is task-specific, uses public source downloads and writes ignored `data/cache/<ID>/` arrays. Read each protocol/license before acquisition. Use a new checkout/run directory to preserve original result artifacts; do not regenerate frozen prompts/specifications or replace original submissions.

```sh
# Most adapters expose prepare() through their module entrypoint.
python experiments/H01/adapter.py
python experiments/H16/adapter.py
python experiments/I07/adapter.py
python experiments/I10/adapter.py
python experiments/K01/adapter.py
python experiments/D02/adapter.py
python experiments/A09/adapter.py
python experiments/A14/adapter.py
python experiments/F04/adapter.py
python experiments/L04/adapter.py
# E01requires the pinned official NWB-reader preparation stack:
python -m pip install -r experiments/E01/requirements-prepare.txt
python experiments/E01/adapter.py
# N05reuses the D02rawfile; see its source-specific preparation script:
python experiments/N05/prepare.py
```

Preparation must reproduce declared source checksums/selection. Exact prepared NPZhashes can be sensitive to serialization/library versions; a hash mismatch deliberately prevents silently evaluating a changed frozen input. Inspect semantic arrays and record a new explicit reproduction run rather than modifying original specifications to hide mismatch. E01's preparation-only older NWB dependencies may need a separate virtual environment; generated-model evaluation uses the repository scientific stack.

```sh
# Execute already-frozen model code, no model calls. TASK is an admitted array task.
python scripts/expansion.py evaluate TASK
python scripts/workflow.py evaluate  # N05, after source fixture preparation
# Restore archived refs after rerunning the primary A09/I10model/reference records:
python scripts/integrate_references.py
python scripts/release_registry.py
python scripts/summarize.py
python scripts/validate.py
python scripts/validate_expansion.py
python scripts/build_website.py
python scripts/check_repository.py
node scripts/check_site.mjs
```

`integrate_references.py` reuses the committed aligned VASSIpredictions; its original source retrieval/alignment steps are in `experiments/A09/specialized_reference.py` and the specialist selection/alignment files. I10 archived CSV is acquired by its adapter. `validate_expansion.py` only re-scores stored predictions; it does not retrain or contact a model. Portable CI checks metadata, linked files, prediction hashes and static-source routes without acquiring raw data. Source-render checks are not browser layout/interaction QA.

## Preview 0.5 additions

Use `scripts/release_registry.py` for the current 96-entry active map. `integrate_admissions.py` is a historical v0.4 normalizer and must not reconstruct the current active panel. Raw data stay ignored. All acquisition/preparation commands below can download substantial public data; read the per-task protocol and terms first. Do not run `freeze` again for the original release.

```sh
# Prepare new bounded tasks; B01 needs its separate pinned specialist stack.
python experiments/B01/adapter.py
python experiments/G01/adapter.py
python experiments/H08/adapter.py
python experiments/J08/adapter.py
# E01 source preparation uses its pinned preparation environment.
python experiments/E01/slices/area2_bump/adapter.py
python experiments/E01/slices/dmfc_rsg/adapter.py
# Execute frozen programs, no new model calls.
python scripts/spikes.py evaluate
python scripts/expansion.py evaluate G01
python scripts/expansion.py evaluate H08
python scripts/expansion.py evaluate J08
python scripts/transfer.py evaluate area2_bump
python scripts/transfer.py evaluate dmfc_rsg
```

B01 acquisition/scoring requires `experiments/B01/requirements.txt`; source MEArec/SpikeInterface compatibility is separate from the model's allowed general-package environment. The adapter prepares the MountainSort5 reference events; scorer uses pinned SpikeInterface 0.105.4. E01/G01 source preparation requirements are declared in their experiment directories. Core general-model evaluation uses root `requirements.txt`. H08 preparation uses MNE; the YASA reference uses a separate environment to prevent specialist dependencies changing the general-model evaluation stack.

For specialist reproduction, use a separate virtual environment with `yasa==0.8.1`, `pyriemann==0.12`, `mne==1.13.2`, `lightgbm==4.7.0`, `numpy==2.5.4`, `scipy==1.18.1`, `scikit-learn==1.9.1`, `pandas==3.1.0`, `antropy==0.2.3`, `numba==0.68.1`; the exact runtime identities and checkpoint hashes are in per-task specialist runtime JSON. These are the observed release versions, not a claim about universal compatibility.

```sh
# Separate specialist environment; train-only selection, no model calls.
python experiments/H01/specialist_riemann.py
python experiments/H01/specialist_aligned_riemann.py
python experiments/H08/specialist_yasa.py
python experiments/H08/verify_yasa.py
# Return to the core science environment for scoring/integration.
python scripts/integrate_specialists.py
python scripts/release_registry.py
python scripts/summarize.py
python scripts/validate.py
python scripts/validate_expansion.py
python scripts/build_website.py
python scripts/check_repository.py
node scripts/check_site.mjs
```

The original H01 selection outputs include all out-of-fold predictions and a separate verification record. J08's author StarDist masks are archived predictions, not locally executed inference; source code and all aligned human masks are retained in acquisition evidence. A14's optional DISK transformer archive was inspected and rejected because its downloaded, publisher-hash-matching weight ZIP lacks a readable central directory; it is not a scored specialist.

E01 extra sources reuse the exact original generated programs. The original prompt describes MC_Maze_Small dimensions, so this is a deliberately disclosed frozen-program portability test, not a matched fresh-prompt comparison. DMFC preserves official masked target coordinates. Prepared data hashes and source preparation seals must match; never fix a mismatch by silently changing an original run-spec.

Scoring checks need acquired arrays. Portable CI uses no raw-data downloads or provider calls and verifies metadata, links, frozen source/prompt/code identities and stored prediction hashes. Browser verification is recorded separately; source-VM checks alone do not establish layout or click behavior.

## Preview 0.6 ERP and metric sensitivity

H02 uses a separately licensed source (original Brain Invaders 2012, CC BY 4.0). Its preparation acquires all 25 original ZIPs (~677 MB), validates publisher MD5s and independent MAT/CSV markers, and writes ignored prepared arrays. The frozen original programs can be evaluated without calling any model. Read the task protocol before acquisition; do not rerun `freeze` or replace original submissions.

```sh
python experiments/H02/adapter.py
# Separate specialist environment: pyriemann==0.12 and declared runtime stack.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/H02/specialist.py
# Core numerical environment; fixed model programs plus both references.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python scripts/erp.py evaluate
# SpikeInterface 0.105.4 environment, no fitting or new model calls.
python experiments/B01/secondary_audit.py
# Return to core environment to rebuild current central artifacts.
python scripts/release_registry.py
python scripts/summarize.py
python scripts/validate.py
python scripts/validate_expansion.py
python scripts/build_website.py
python scripts/check_repository.py
node scripts/check_site.mjs
```

H02's training-group argument is explicit and identical across methods. The independent person-level AUC verification uses float64 rank accumulation; the originally stored LDA scores can be float32. Stored prediction identity and rank order are unchanged. Its source author-code license is retained in `experiments/H02/UPSTREAM_LICENSE.txt`.

The B01 event-accounting script is **post-hoc** and adds secondary fields only. It preserves original predictions, primary scores, tolerance and unit mapping. `posthoc_all_event_f1`, precision and recall are exported in the central CSV; other tasks have no value in those columns. They are not silently substituted into the macro score policy.
