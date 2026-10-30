# Evaluation methodology

## What is being evaluated

The scientific estimand is performance of a **specified model plus procedure** on a defined neural-data endpoint. T0 direct input/output, T1 frozen features, T2 adaptation, T3 generated code and T4 specialist-tool workflows answer different questions. A text model generating a gradient booster does not demonstrate a pretrained raw-signal encoder. v 0.4 measures only constrained T3: a single no-tool code submission followed by local numerical execution. All models are closed hosted Sol models; open-weight, image/video, audio, world and neural-domain models are not yet evaluated.

## Controls and provenance

Use the same explicit user prompt, schema, reasoning setting, permitted imports and numerical budget within an experiment. Fresh CLI processes use empty working directories, no retained chat history, ephemeral sessions, ignore-user-config and no model tool calls. Provider/CLI-supplied system instructions may differ by model; token counts differ and a byte-identical full effective context is not guaranteed. Requested IDs are recorded; internal provider checkpoint resolution is not independently observable. No test data/labels are in the generation prompt. Public historical test labels may be in pretraining. Never interpret “not supplied” as proof of no contamination.

Freeze protocol and code before scoring, hash prompt/code/input/prediction files, save raw predictions and errors. Log actual generation usage and zero-tool events. The controller can see scoring labels but does not repair submissions based on them. Dependency/harness repairs are distinct from model changes and are logged. The first local Git protocol commit is `410397c`; three M04 submissions were frozen in `41e627e` before evaluation. These are timestamped exploratory records, not an external preregistration or independent audit.

Only reviewed generated code is executed. AST checks restrict obvious I/O/imports, but are not a secure sandbox for arbitrary submissions. The local harness uses subprocess timeout 180 seconds and one numerical thread; it does not enforce/measure the approximate memory request. Full estimator time, generation token counts and failure reasons are retained. Subscription use is not converted to invented API dollar costs. Code length is a formatting constraint: GPT-5.6 Sol C05 exceeded it and is explicitly excluded from strict format-compliant claims; its unmodified exploratory score remains visible.

## Data and scorers

C05 uses original Spikefinder preparations 1–5, pinned archive commit and official 40-ms correlation operation. Preparation 1 is previously observed pilot/development evidence. Preparations 2–5 are a frozen-program transfer audit; the original prompt described preparation 1’s approximate shape. Same code is fitted independently to each preparation’s train neurons. This is not five independent benchmark families. It is offline/acausal and cannot support online BCI claims. Neurons are not independent animals; identities needed for animal-level inference are unavailable.

M04 uses a custom synthetic Q-learning recovery wrapper motivated by [Wilson & Collins](https://doi.org/10.7554/eLife.49547). The known equations are explicitly supplied to models. The 24 agents are independent draws from one specified simulator regime, not real subjects. Primary range-normalized parameter MAE and secondary in-sample likelihood address different endpoints. A canonical MLE can have worse parameter error than a regularized posterior summary because finite-sample estimation and likelihood optimization differ. Do not call a loss improvement a discovery of neural mechanisms. No held-out likelihood claim is made.

## Specialist comparisons

For C05, archived Deneux/Speiser/Friedrich/Rupprecht predictions are rescored on identical targets; OASIS default AR1 is locally reproduced. Best of those four archives is only a limited historical reference; original training/tuning budgets differ and current global SOTA is unverified. For M04, the local correctly specified grid+multistart MLE is a mathematical fitting baseline, not a published best model. It has identical observed data but a different estimator/prior and optimization budget. Report descriptive deltas, never a matched-total-effort superiority claim.

## Confirmatory upgrade

Use biologically grouped held-out cases and multiple independent model generations; freeze validation search budgets and failure scoring; include matched label/compute regimes; independently reimplement scorers; evaluate contamination-resistant private/new cases where permitted. Report cluster intervals by animal/person/lab, not windows or neurons. Multimodal models need comparable input access and signal-preserving conversion. Auditing costs, scientific interpretation and safe control requires distinct endpoints. [Leakage evidence](https://www.nature.com/articles/s41467-024-46150-w) and [BetterBench](https://proceedings.neurips.cc/paper_files/paper/2024/file/26889e8359e7ef8a7f5d77457364ca55-Paper-Datasets_and_Benchmarks_Track.pdf) motivate these controls.

## Post-hoc reference audit

A separate posterior-median reference was added after observing nearly identical Bayesian estimators in all three M04 submissions. It retains the frozen MLE reference and is documented in `experiments/M04/posthoc-amendment.md`. The 257→513-grid refinement tests numerical convergence. It uses uniform priors over prompt bounds, not oracle knowledge of the hidden generating distribution. Tiny model differences are treated as quadrature effects. Local MLE convergence does not certify a global optimum.

## v 0.4 expansion and procedure amendments

The current release measures 14 task IDs across 11 families. Twelve new frozen protocols are documented under `experiments/<ID>/protocol.md`; [release report](release-v04.md) and [findings](../analysis/findings.md) supersede the earlier two-task status. T3 remains the measured track; N05 permits reading exactly one provided HDF5/NWB fixture at execution, while generation remains no-tool. All other new models receive training arrays/targets and unlabeled test inputs, never test targets. Publicly available labels and raw targets used by the scorer remain a contamination risk.

New protocol prompts/adapters/prepared-input hashes were sealed before each generation. Each model submits one program with high reasoning, deterministic seeds requested, permitted general libraries and no execution feedback.42 programs supply 54 slice executions, because C05 refits one program on five preparations. Fourteen task IDs are not fourteen independent datasets: D02/N05 share a file, K01 shares the broader Allen collection, and within-source neurons/repeats/windows are correlated. F04 requires identical rates for identical repeated testimages; all stored predictions passed that check. The centralization script preserves missing/failed records.

Some H01/I07 programs infer subject block structure or use unlabeled input alignment; the baseline and generated code use different inner-validation grouping policies. Test labels remain withheld, but this is not a matched-information or matched-adaptation comparison. Model-specific adaptations must be inspected in the exact submitted code. H16 is semisynthetic signal repair, A14 artificial gaps in real mocap, E01a supervised population-readout slice, L04 real count encoding rather than full statistical calibration, and I10 processed IQMs rather than raw MRI. These boundaries constrain the claims.

K01 harness repair: predictions from valid global classes were initially rejected within single-class donor subgroups. The scorer now validates against the fixed global label set and reports single-class group accuracy. Initial logs retained; unchanged programs rerun. This is distinct from N05 GPT-5.6's preserved program failure. No program was edited after score feedback. New format limit<240 lines differs from the original C05<180 line contract; strict compliance is evaluated per original task request.

References are stratified: conventional local baselines, historical specialist predictions, synthetic objective-mismatched MLE, deterministic correctness and post-hoc objective-aligned audits. A09 VASSIrun 00 selection predates rescoring; all 20 runs retained. I10 original classifier predictions align one-to-one to 265 DS030 scans with verified exclude 1 labels, but training/rater/feature histories differ. No current strongest matched specialist is verified. Numerically rescoring every stored prediction and source/hash alignment is necessary, but not an external expert audit or proof that a custom diagnostic measures the full scientific task.

## Preview 0.5 additions

Four new protocols and two E01 unchanged-program source transfers are recorded in [release 0.5](release-v05.md). B01 uses separately hidden event truth and official unit matching; H08 uses label-independent clock selection; J08 preserves independent raters and instance matching; G01 uses trial-reset causal features and date-heldout evaluation. H01 post-hoc pyRiemann references and historical test-selected envelopes are explicitly labeled. Two failures and strict line-limit deviations remain. [Findings](../analysis/findings.md).
