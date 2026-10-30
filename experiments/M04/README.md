# M04 — cognitive parameter-recovery mini-benchmark

[Task card](../../benchmarks/M/M04/README.md) · [Frozen protocol](protocol.md) · [Prompt](prompt.txt) · [Post-hoc amendment](posthoc-amendment.md) · [Measurements](../../results/M04.json) · [Synthetic data manifest](../../data/manifests/cognitive.json) · [Generation provenance](generation-provenance.json)

## Completed procedure

1. Commit equations, simulator regime, held-back seed/parameters, bounds, primary recovery loss, secondary observed-history likelihood, numerical budget and MLE reference plan before generation/scoring.
2. Request one program from each exact Sol ID in a fresh ephemeral no-tool CLI process, using identical explicit prompt/schema and high reasoning. Commit exact returned JSON before scoring; `.py` files extract identical returned code for readability. Provider instructions may differ.
3. Generate 24 independent agents × 240 trials with deterministic seed 20261030. Hide generating parameters from model programs; supply only choices/rewards. Primary loss normalizes alpha/beta errors by prompt-allowed ranges.
4. Execute reviewed unchanged programs under one numerical thread and 180-second per-program timeout. Preserve predictions, code/data hashes, scores, timings and per-agent errors.
5. Reproduce a correctly specified deterministic grid+four-start local MLE fit and constant midpoint baseline. All MLE optimizers report convergence, which does not prove global optimality.
6. After observing nearly identical uniform-prior posterior-median code in the three submissions, add an **explicitly post-hoc** independent posterior-median reference with 257/513-grid convergence check. Preserve original MLE and model scores; use allowed-bound uniform prior, never oracle hidden generator bounds.
7. Validate a hand-calculated likelihood fixture and recompute all per-agent errors from stored predictions and known synthetic truth. Centralize results; keep simulation separate from biological inference.

All three model algorithms essentially coincide. Small score differences are numerical integration effects. MLE has a different objective, so a lower recovery MAE is not evidence for general-over-specialist superiority. This custom wrapper tests supplied-equation inference construction; it does not implement all cognitive model-recovery tasks in the broader catalog card, and it does not validate mechanisms on real participants.
