# E02 — Recovery of computational dynamics

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** Computation-through-Dynamics Benchmark

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Synthetic spikes from task-trained networks

Target/ground truth: Ground-truth simulated dynamics and states

Specialist candidates: LFADS; sequential autoencoders

General-model route: General sequence/world model

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Good neural prediction does not guarantee correct dynamical mechanism

## Sources

- [https://github.com/snel-repo/ComputationThroughDynamicsToolkit](https://github.com/snel-repo/ComputationThroughDynamicsToolkit)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). CtDB can supply synthetic mechanistic dynamics groundtruth and known task variables. Needs pinned generator, stimulus/trajectory/seed split and metric for actual recovered dynamics, not arbitrary latent-coordinateRMSE. Synthetic extension remains useful but unprepared.

[Source-linked admission evidence](../../../literature/admission-v04-behavior-population.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. CtDB can supply synthetic mechanistic dynamics groundtruth and known task variables. Needs pinned generator, stimulus/trajectory/seed split and metric for actual recovered dynamics, not arbitrary latent-coordinateRMSE. Synthetic extension remains useful but unprepared.

[Admission/source evidence](../../../literature/admission-v04-behavior-population.json).
