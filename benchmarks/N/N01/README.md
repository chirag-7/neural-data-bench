# N01 — End-to-end neuroscience data analysis QA

[Family](../README.md) · [Project](../../../README.md) · [Methods](methods.md) · [Worklog](worklog.md)

**Resource:** NeuroDiscoveryBench

**State:** not evaluated; candidate_pending_validation. Mapped resource only; license, acquisition, split, scorer and baseline gates are not yet all validated.

## Scientific use

Input: Real atlas/cohort files and question prompts

Target/ground truth: Expert quantitative/text/figure answers

Specialist candidates: Expert reference workflow; published agent baseline

General-model route: General coding agent

## Execution and performance

No experiment admitted yet. All measurements are centralized in [results](../../../results/). Current best: **not verified**. Missing scores are unknown, not zero. Literature resources are not newly executed results.

## Limitations

Original tasks have public answers; model judge is fallible

## Sources

- [https://github.com/allenai/neurodiscoverybench](https://github.com/allenai/neurodiscoverybench)

## v0.4 admission and execution

Decision: **candidate_pending_validation** (2026-10-30). Official repository provides workflow metadata, expert answers, dataset loader and eval code. This batch has not frozen an eligible neuroscience question subset, run its large-source data loader or replicated text/figure rubric evaluation. Needs task-specific numeric checks and, where the official evaluator uses an LLM judge, recorded judge model/version/prompt and access. No surrogate blind-judge scores supplied.

[Source-linked admission evidence](../../../literature/admission-v04-cell-workflow.json). This endpoint was not run in this release; absence is unknown, not zero or proof of poor data.

## v0.5 execution status

candidate_pending_validation. Official repository provides workflow metadata, expert answers, dataset loader and eval code. This batch has not frozen an eligible neuroscience question subset, run its large-source data loader or replicated text/figure rubric evaluation. Needs task-specific numeric checks and, where the official evaluator uses an LLM judge, recorded judge model/version/prompt and access. No surrogate blind-judge scores supplied.

[Admission/source evidence](../../../literature/admission-v04-cell-workflow.json).
