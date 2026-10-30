# Spikefinder dataset-1 pilot

Research preview v0.2 · 30 October 2026

Three requested Codex model IDs (`gpt-6.1-sol`, `gpt-6-sol`, `gpt-5.6-sol`) each generated one estimator program under the same task prompt and high reasoning setting. GPT-6.1 Sol matches the model ID recorded for the parent chat; the measured submission is a fresh CLI instance, not a retrospective score assigned to the conversation.

This is **single-shot code synthesis with external supervised fitting**, a constrained T3 track. It is not direct neural-signal inference inside the language model and not a full iterative agent benchmark. No generation tools or test labels were supplied. The model event logs record zero tool calls. Public benchmark material may still exist in pretraining.

## Data and split

Original Spikefinder dataset 1: 11 paired training neurons, five original held-out test neurons. Arrays are at 100 Hz, with trailing NaNs for shorter recordings. Neither animal IDs nor independent subject counts are inferred from neuron counts. Test labels are loaded only by the external scorer after inference.

The data are acquired from the public original S3 archive and a pinned commit of the official analysis repository. Raw recordings are not redistributed in this bundle. Check original data terms and cite the originating work before new use or redistribution.

## Metric

Per-neuron Pearson correlation after summing four adjacent samples into non-overlapping 40-ms bins. The primary displayed aggregate is the median across the five neurons, with mean and every cell score also reported. This subset aggregate is not the full original challenge score. Summing versus averaging bins has identical Pearson correlation. Constant predictions score zero by the pilot convention.

The scorer is checked against extracted official `_downsample`/`_corr` functions and the five published archived Deneux values. Preserve the original source attribution: [Berens et al., community-based spike inference benchmark](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006157); [official analysis repository](https://github.com/berenslab/spikefinder_analysis); [data documentation](https://github.com/codeneuro/spikefinder-datasets).

## References in the comparison

- **Deneux archived predictions:** highest mean and median among complete five-neuron submissions in `results_30_06_17.csv` for dataset 1 test. Predictions are rescored locally. This is an archived best-on-slice reference, not a verified current SOTA claim.
- Archived Speiser, Friedrich and Rupprecht predictions are also rescored.
- **OASIS 0.3.2:** locally rerun default AR(1) deconvolution with automatic baseline/noise/AR estimation and penalty 1, independently on each test trace. This unsupervised default is not claimed to be a tuned best specialist. [OASIS source](https://github.com/j-friedrich/OASIS).
- Raw fluorescence is included as a simple baseline.

Newer CASCADE/GCaMP8 evaluations concern different indicators, noise settings, sampling rates and targets; their numeric results are not interchangeable with this slice. [Current CASCADE research resources](https://github.com/HelmchenLabSoftware/Cascade).

## Reproduce

Use Python 3.12. Place this directory at `outputs/spikefinder-pilot` inside a research project folder, matching the bundle layout.

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r outputs/spikefinder-pilot/requirements.txt
python outputs/spikefinder-pilot/acquire_data.py
python outputs/spikefinder-pilot/verify_scorer.py
python outputs/spikefinder-pilot/evaluate.py
```

`evaluate.py` sets one-thread numerical environment variables for its subprocesses and enforces a 180-second wall-clock timeout per program. It retains unmodified returned programs, raw predictions, native scores, hashes and dependency versions. The approximate 3-GB memory request was not independently measured or enforced.

Generation used the signed-in Codex CLI, ephemeral fresh contexts, read-only sandbox, `--ignore-user-config`, exact requested `--model`, `-c model_reasoning_effort=high`, `--output-schema response_schema.json`, and the identical `prompt.txt` on stdin. The exact provider-internal checkpoint behind each CLI model ID is not directly observable. Token usage is preserved in `results.json`; no API dollar cost is inferred from subscription usage.

## Protocol and infrastructure notes

- The prompt requested fewer than 180 code lines. GPT-5.6 Sol returned 188 including blanks. Its unmodified program is scored, with a disclosed formatting deviation; do not label it an unqualified strict protocol pass.
- Missing shared environment dependencies initially blocked scikit-learn imports. The environment was repaired and the unchanged submissions rerun; no feedback or repaired code was returned to any model.
- `gc` is accepted as a standard Python memory utility. No specialist imports are permitted to model submissions.
- Generation was one-shot. There are no repeated-generation uncertainty estimates or population-level significance claims.
- Different specialist pretraining/tuning histories mean equal model-code constraints do not establish equal total training effort.

## Files

`prompt.txt`, `response_schema.json`, model response JSON and extracted Python, `evaluate.py`, `verify_scorer.py`, `acquire_data.py`, `requirements.txt`, predictions, scores and `results.json` provide the reproducible numerical artifact. No credentials or raw private data are included.
