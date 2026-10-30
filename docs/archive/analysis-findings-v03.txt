# Exploratory findings and practical interpretation

This release contains **one biological benchmark and one synthetic recovery task**, not an all-neuroscience evaluation. All numbers below are derived from [central measurements](../results/measurements.jsonl) by [summarize.py](../scripts/summarize.py). One generated program per model/task, no repeated-generation uncertainty; differences are descriptive.

## C05: calcium-to-spike inference

Native primary metric is median per-neuron Pearson after official 40-ms binning, higher is better. Each frozen program is fitted on the preparation’s training neurons and evaluated on its original different test neurons. Preparation 1 had been inspected in the original pilot. Preparations 2–5 are a subsequent frozen-program portability audit with no reprompting or code repair.

| Preparation | GPT-5.6 Sol † | GPT-6 Sol | GPT-6.1 Sol | Best available inspected archive | Complete archive candidates |
|---|---:|---:|---:|---|---:|
| 1 | 0.578914 | 0.600762 | 0.604587 | deneux / 0.611641 | 4 |
| 2 | 0.407814 | 0.441131 | 0.457172 | deneux / 0.455379 | 3 |
| 3 | 0.408966 | 0.397117 | 0.440321 | rupprecht / 0.433586 | 4 |
| 4 | 0.389759 | 0.367991 | 0.391995 | friedrich / 0.380251 | 3 |
| 5 | 0.475528 | 0.409526 | 0.445404 | rupprecht / 0.495829 | 2 |

Mean of the five preparation medians: GPT-5.6 0.452196; GPT-6 0.443305; GPT-6.1 0.467896. Preparation-equal weighting avoids giving a preparation with more neurons a larger weight, but does not establish an animal-level estimand. Test-neuron counts and every cell score are retained in the measurement records. No animal IDs are available for cluster confidence intervals.

GPT-6.1 improves on GPT-6 in **5/5** preparations. GPT-6 improves on GPT-5.6 in **2/5**; GPT-6.1 improves on GPT-5.6 in **4/5**. These observations contradict a simple monotonic 5.6→6→6.1 progress story. They are comparisons of three particular generated estimators, not direct signal inference or causal effects of model size/training compute.

Against the available historical envelope, GPT-6.1 has 3/5 point-score wins, GPT-6 0/5, GPT-5.6 1/5. The envelope is selected using test scores among up to four inspected archives; availability is **4/3/4/3/2**. It is not a current specialist optimum or matched-training-budget reference. Four incomplete archive attempts are excluded from the complete-target envelope and retained as failures. Missing references could change the envelope.

† GPT-5.6’s C05 code exceeded the requested <180-line constraint; all five uses inherit this protocol deviation. All its C05 comparisons above are exploratory. Strict-format C05 eligible denominators are 0 for GPT-5.6, 5 for GPT-6 and 5 for GPT-6.1. Valid numerical completion and strict formatting are distinct outcomes.

## M04: synthetic cognitive parameter recovery

The task supplies exact two-action Q-learning equations and asks for alpha/beta recovery from 24 simulated agents. All three programs implement essentially the same uniform-prior posterior-median estimator. Primary normalized MAE:

- GPT-5.6: 0.058222606
- GPT-6: 0.058219401
- GPT-6.1: 0.058221490
- Frozen local multistart MLE: 0.070696459
- Post-hoc independent posterior-median reference: 0.058222869
- Constant midpoint: 0.218003324

The ~1e-6 differences among model programs and the matched posterior reference are numerical integration effects; they do **not** support a capability ranking. The posterior audit’s 257→513-grid refinement changes normalized estimates by up to 4.20e-5 and changes aggregate loss by ~1.63e-6, comparable to the model ordering. The reference uses the same allowed-bound uniform prior, not the hidden simulator’s narrower generating distribution. It is objective-aligned, not Bayes-optimal under the actual generator.

All generated estimators beat this local MLE on parameter MAE, but MLE optimizes likelihood, a different objective. Finite-sample shrinkage and estimator choice explain this without a generalist-superiority claim. The added posterior-median audit is explicitly **post hoc**; frozen MLE and model results remain unchanged. Optimizer convergence on all 24 agents is a diagnostic, not proof of global optimality. Likelihood here is in-sample, not held-out prediction. This is a known-equation inference sanity check, not discovery of cognitive mechanisms or validation on real participants.

## What a neuroscience researcher can take from this

For processed calcium traces under these offline conditions, a strong general code model can construct a useful conventional numerical estimator. This is promising for bootstrapping an analysis, but validate it against paired truth and preserve specialist tools: preparation shift can reverse rankings, the strongest current specialist is unverified, and the generated trees do not replace raw-movie processing or online control.

For known cognitive equations, all three models can express a standard likelihood/Bayesian estimation procedure. Once they implement the same algorithm, a newer language model need not yield better numerical recovery. The experiment mainly tests correct method construction, while data informativeness, objective choice and numerical accuracy govern the final error.

Hypotheses for future testing: general code agents may help most when tasks have explicit equations, small processed arrays and mature general scientific libraries; specialists may retain advantages when inputs are large raw sensor streams, geometry/physics matter, online guarantees are essential, or domain-specific pretraining/ground truth is scarce. These are hypotheses, not measured cross-domain moderators.

## Macro claims deliberately withheld

Do not pool five C05 preparations and one synthetic task into six independent task wins. Do not average Pearson and parameter MAE. No universal ranking, superiority percentage, current SOTA, biological uncertainty, open-vs-closed conclusion or broad scaling trend is supported. The dashboard shows actual coverage, per-task trajectories, per-reference evidence classes and complete paired native deltas. The [macro analysis plan](../docs/macro-analysis-plan.md) describes family balancing and controls for a future sufficiently broad panel.
