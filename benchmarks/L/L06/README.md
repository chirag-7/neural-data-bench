# L06 — Calibrated statistical neural inference

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** sbibm Bernoulli GLM; likelihood-informed posterior-sampling code generation

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Known100x10 causal design,ten100-bin observed synthetic spike trains,zero-mean Gaussian prior precision; hidden reference draws scorer-only

Target/ground truth: Finite author Polya-Gamma MCMC posterior samples for ten simulated observations, not biological truth or analytic exact distributions

Mapped specialist candidates (not all evaluated): Published SBI algorithms and classical inference

General-model route: General inference or code agent

## Execution and performance

**Executed slice:** All ten original sbibm Bernoulli GLM observations; ten parameters,100 bins,10000 posterior draws per observation; custom likelihood-informed track.

[Frozen protocol and artifacts](../../../experiments/L06). [Measured scores and references](../../../results/L06.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

Synthetic shared-design GLM; known likelihood changes original SBI information access. Custom2000draw C2ST and near-chance variation are not original leaderboard scores or superiority evidence. PG comparator is related to archived reference, shorter local chains have unproven convergence, one code generation/model.

## Sources

- [https://github.com/sbi-benchmark/sbibm](https://github.com/sbi-benchmark/sbibm)
- [https://proceedings.mlr.press/v130/lueckmann21a.html](https://proceedings.mlr.press/v130/lueckmann21a.html)
- [https://github.com/sbi-benchmark/sbibm/tree/f0bc44039e6b7e095c18d4e9e64819d75be76587](https://github.com/sbi-benchmark/sbibm/tree/f0bc44039e6b7e095c18d4e9e64819d75be76587)
- [https://github.com/sbi-benchmark/sbibm/blob/f0bc44039e6b7e095c18d4e9e64819d75be76587/sbibm/metrics/c2st.py](https://github.com/sbi-benchmark/sbibm/blob/f0bc44039e6b7e095c18d4e9e64819d75be76587/sbibm/metrics/c2st.py)
- [https://github.com/zoj613/polyagamma](https://github.com/zoj613/polyagamma)
- [https://arxiv.org/abs/1205.0310](https://arxiv.org/abs/1205.0310)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Official MIT sbibm repository and GLM task exist. Requires frozen observations/simulation budget, posterior-sample interface and reference posterior/calibration scorer; array prediction harness cannot validly replace posterior evaluation.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## Current admission and execution

Preview 0.9: measured. Source-specific rights/data/scorer checks and frozen model procedure completed for the explicit custom slice; no broader resource or current-SOTA claim.

[Admission/source evidence](../../../experiments/L06/protocol.md). [Actual protocol/worklog](../../../experiments/L06). [Task measurements](../../../results/L06.json).
