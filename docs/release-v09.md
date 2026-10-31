# Preview 0.9: posterior inference and explicit data scopes

One additional candidate is fully executed: **L06, posterior sampling for a spiking-neuron Bernoulli GLM**, across all ten original sbibm observations. All three requested models and two frozen references return valid outputs within the 180-second sampling budget. One task contains ten observations; they do not become ten macro tasks.

## What was frozen and measured

The [protocol](../experiments/L06/protocol.md), original-source hashes, data, explicit prompt, scorer, local PG/Laplace implementations and runner were sealed in commit `93c6a9824916b57105063cdc41b234ae6782f2de` before any generation or method score. Forty-two original files are verified; all design entries match the author's fixed stimulus, the ten raw observations match their sufficient statistics, and all archived posterior CSVs match the prepared arrays. True-parameter files were not acquired. Each program receives observations, design and prior precision only. Raw no-tool generation events and unmodified programs are retained.

This is **likelihood-informed code construction**, not the original simulator-only SBI comparison. The original author reference uses longer Polya–Gamma MCMC initialized at truth. The local PG implementation starts from the observed-data MAP, uses 2,500 warmup and thinning two and has no hidden parameter/reference access. It uses the same algorithm family as the original reference and a compiled specialist package. These differences are explicit; this is not matched total research effort or a global-best search.

## Results

| Method | Primary C2ST accuracy ↓ | Secondary sliced W2 ↓ | Sampling seconds |
|---|---:|---:|---:|
| gpt-5.6-sol | 0.512500 | 0.014975 | 4.638 |
| gpt-6-sol | 0.497375 | 0.015708 | 0.867 |
| gpt-6.1-sol | 0.505600 | 0.016329 | 2.470 |
| Local Polya–Gamma Gibbs | 0.494100 | 0.016785 | 5.305 |
| Laplace approximation | 0.546250 | 0.078966 | 0.024 |

Primary values average five-fold classifier accuracy over all ten observations. The classifier sees 2,000 evenly spaced draws from each 10,000-draw posterior; the original benchmark uses a different/full scoring protocol. Near 0.5 is the chance target: tiny differences between near-chance methods do not establish superiority, and a below-chance point does not indicate superhuman posterior quality. One fixed classifier seed and one code generation per version do not establish stable ranks. Secondary sliced W2 uses all draws, 128 frozen directions and prior-whitened coordinates; its native values cannot be averaged with unrelated task metrics.

The PG classifier mean is below chance, which is sampling/classifier variation rather than better-than-ideal inference. All three general samplers have smaller secondary sliced-distance point values than this local PG chain; that does not establish superiority over a domain sampler because both the reference distribution and compared outputs are finite Monte Carlo samples. No robust version-improvement conclusion follows.

These ten simulations share one stimulus and model family. They do not establish biological generalization, unknown-likelihood SBI capability, intervention identification, full coverage calibration or arbitrary multimodal/multimode posterior inference. The logistic posterior here is log-concave under a proper Gaussian prior; this is a favorable numerical inference case.

Generic split-chain and lag-one diagnostics operate on returned draw order. GPT-5.6 explicitly shuffles its output; GPT-6.1 combines multiple chains. Those returned-order diagnostics are not valid independent-chain mixing certification. Samples are not treated as independent biological replicates.

## Verification and reproducibility

[Independent audit](../experiments/L06/verification.json) checks source and frozen hashes, every raw observation/reference join, every held-out classifier decision and fold allocation (200,000 decisions across the five methods), all ten primary accuracies per method and all secondary sliced distances. It does not refit the classifiers a second time. The original training/scoring code and held-out decisions are retained for reruns. [Reproduce](reproduce.md), [worklog](../experiments/L06/worklog.md), [results](../results/L06.json), [per-observation CSV](../experiments/L06/observation-scores.csv), [manifest](../data/manifests/L06.json), [sampling/scoring runner](../scripts/posterior_candidates.py).

All 0.8 central records remain identical, with the snapshot retained at [v08-measurements.jsonl](../results/archive/v08-measurements.jsonl). The H02 repeated-generation follow-up remains separate and unchanged. No poor prior result was removed.

## Website and macro interpretation

The task page shows both bar and connected-version plots with an explicitly named PG line and numeric reference cards, plus the Laplace approximation. Select any of ten observations or the all-ten mean, and switch between the primary C2ST and secondary sliced W2. Those exploratory controls do not change directory scores or macro denominators.

One scope selector now applies to both reference and version-change tables. Default **observed-data sources** excludes fully synthetic B01/L06/M04 and deterministic file task N05. A14/H16 still use observed sources with artificial corruption and are explicitly identified. **Include fully synthetic tasks** restores the eligible synthetic-inclusive comparisons. M04 quadrature and N05 correctness remain outside version-change aggregates. This is a retrospective display/policy refinement; historical records are unchanged. Counts and per-task/family summaries for both views are exported in [summary.json](../analysis/summary.json). Numerical wins remain descriptive under the old 1e−9 rule, not significance/equivalence claims.

## Candidate review and remaining work

The [bounded three-candidate screen](../literature/admission-v09.json) also revisited L01 and B07. Duke/NYU connectomics mirrors returned HTTP403, joining the prior ETH access result. Authorized Kaggle access is unestablished; no universal-inaccessibility claim. For B07, original public S3 metadata identifies 16 experimental raw files; original open-data registry states CC BY 4.0. Raw chunk acquisition, codec contract and specialist execution are still pending. Public access alone is not a completed compression benchmark.

The current panel has **22 measured task IDs, 84 first-submission model–slice attempts and 167 model/reference records**. The active map remains 96 entries across 14 families, with 46 pending validation and 28 deferred; 74 entries remain unrun. The 207-URL source inventory is not a count of fully reviewed papers. Native multimodal/open-weight models, broad specialist matching, repeated generations and independent biological cohorts remain substantial gaps.

## Primary sources

- Lueckmann et al. (2021), [Benchmarking Simulation-Based Inference](https://proceedings.mlr.press/v130/lueckmann21a.html): original task/procedure and metric context.
- [Pinned original task and reference-sampler implementation](https://github.com/sbi-benchmark/sbibm/blob/f0bc44039e6b7e095c18d4e9e64819d75be76587/sbibm/tasks/bernoulli_glm/task.py).
- [Pinned original classifier-test implementation](https://github.com/sbi-benchmark/sbibm/blob/f0bc44039e6b7e095c18d4e9e64819d75be76587/sbibm/metrics/c2st.py).
- Polson, Scott and Windle (2013), [Bayesian inference for logistic models using Polya–Gamma latent variables](https://arxiv.org/abs/1205.0310): methodological basis of the domain-specific Gibbs reference.
- [polyagamma author repository](https://github.com/zoj613/polyagamma): separate local specialist sampler, version 2.0.2.
- [Original connectivity challenge data page](https://connectomics.chalearn.org/help/data) and [AIND original compression-data documentation](https://allenneuraldynamics.github.io/data.html): bounded candidate access checks.

Live-browser review verified the metric/observation selectors and both data scopes. It prompted a wording correction to label table times as the full ten-posterior sampling call; scoring time is separate. No scientific contract, generated code, prediction or score changed.
