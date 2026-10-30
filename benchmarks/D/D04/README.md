# D04 — Physiological validation of mechanistic models

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** HippoUnit / SciUnit

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Biophysical neuron models and stimulation protocols

Target/ground truth: Experimental feature distributions and held-out physiological protocols

Specialist candidates: Published NEURON models and HippoUnit tests

General-model route: Code agent constructs/fits a model, external physiological tests

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

One fitted trace does not validate a mechanism

## Sources

- [https://doi.org/10.1371/journal.pcbi.1008114](https://doi.org/10.1371/journal.pcbi.1008114)

## v0.4 admission and execution

Decision: **deferred** (2026-10-30). Primary HippoUnit repository requires simulation-capable model interfaces, NEURON/eFEL/SciUnit and standalone model adaptation. Published validation target features and model outputs are available, but no new generated mechanistic model plus independent held-out tests was implemented in this CPU/lightweight estimator batch. Do not substitute recalculating published outputs for new agent performance.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.
