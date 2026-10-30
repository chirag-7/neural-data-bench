# Evaluation methodology

## What is being evaluated

The scientific estimand is performance of a **specified model plus procedure** on a defined neural-data endpoint. T0 direct input/output, T1 frozen features, T2 adaptation, T3 generated code and T4 specialist-tool workflows answer different questions. A text model generating a gradient booster does not demonstrate a pretrained raw-signal encoder. v0.3 measures only constrained T3: a single no-tool code submission followed by local numerical execution. All models are closed hosted Sol models; open-weight, image/video, audio, world and neural-domain models are not yet evaluated.

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
