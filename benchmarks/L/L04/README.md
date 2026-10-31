# L04 — Point-process estimation and goodness of fit

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Kramer real place-cell case study; custom count-encoding diagnostic

**State:** measured. Current status for this exact task-resource slice; current global best remains unverified.

## Scientific use

Input: Real rat hippocampal spike counts and position/velocity

Target/ground truth: Measured extracellular spike counts

Mapped specialist candidates (not all evaluated): Poisson GLM; history GLM; Bayesian fit

General-model route: General sequence model; code agent

## Execution and performance

**Executed slice:** One rat place cell: 20 ms spike counts predicted from position and velocity; chronological 60/40 split with a one-second gap.

[Frozen protocol and artifacts](../../../experiments/L04). [Measured scores and references](../../../results/L04.json). [Central data](../../../results/measurements.csv). Missing or failed outputs are retained.

## Limitations

No known generating parameters; no animal generalization or completed time-rescaling calibration

## Sources

- [https://neurallatents.github.io/](https://neurallatents.github.io/)
- [https://github.com/snel-repo/ComputationThroughDynamicsToolkit](https://github.com/snel-repo/ComputationThroughDynamicsToolkit)
- [https://mark-kramer.github.io/Case-Studies-Python/09.html](https://mark-kramer.github.io/Case-Studies-Python/09.html)
- [https://github.com/Mark-Kramer/Case-Studies-Python](https://github.com/Mark-Kramer/Case-Studies-Python)

Source associations include historical alternatives; actual acquired files are identified in the executed protocol/manifest.

## Historical v0.4 admission and execution

Decision: **measured** (2026-10-30). Constructed an explicit real place-cell count-encoding diagnostic from author-released data, replacing only the execution slice of the earlier proposed simulation. Chronological60/40split plus1sbuffer; train-mean-null bits/spike; no parameter-recovery/calibration claim.

[Source-linked admission evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol and artifacts](../../../experiments/L04). [Central task results](../../../results/L04.json).

## Current admission and execution

Preview 0.10: measured. Constructed an explicit real place-cell count-encoding diagnostic from author-released data, replacing only the execution slice of the earlier proposed simulation. Chronological60/40split plus1sbuffer; train-mean-null bits/spike; no parameter-recovery/calibration claim.

[Admission/source evidence](../../../literature/admission-v04-inference-control.json). [Actual protocol/worklog](../../../experiments/L04). [Task measurements](../../../results/L04.json).
