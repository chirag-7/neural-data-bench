# L06 execution worklog

## Admission before execution

- Acquired all ten original sbibm Bernoulli GLM observations and original reference draws from immutable author commit f0bc44039e6b7e095c18d4e9e64819d75be76587. Source bytes/hashes recorded; hidden true-parameter files not acquired.
- Read original likelihood, prior, reference sampler and C2ST scorer. This new interface supplies the likelihood and is not the original simulator-only SBI track.
- Preflight on unrelated synthetic data: 5,000 local Polya–Gamma Gibbs sweeps took about 0.12 seconds; a 2,000-draw C2ST took about 18.6 seconds. No original task method score selected these settings.
- Selected 2,500 warmup sweeps, thinning two, 10,000 retained draws for the comparator and fixed both references before generation and task scoring.
- Checked all 42 source hashes, every design entry against author seed42, ten raw spike sequences and their sufficient statistics.
- The first documentation-copy command used a relative path incorrectly and stopped. Corrected the documentation-copy path before model generation; prepared arrays and frozen science files did not change.

## Frozen generation and execution

The protocol, data, prompt, sampler references, scorer and runner are frozen in run-spec.json before any generation or method score. Later entries append outcomes without changing these contracts.

## Completed frozen execution

- All three first submissions have zero observed tool events and 160/110/160 code lines for 5.6/6/6.1. All three and both references complete the entire ten-observation sampling call in the fixed budget. No generated program was edited or rerun for repair.
- Full scorer runs separately after all methods produced samples. Each method retains10x10000x10 posterior values and ten sets of held-out classifier decisions.
- Independent verification checks every source hash, design/prior construction, observation/reference join, retained fold/accuracy arithmetic and all 128-direction secondary distances. It does not refit classifiers.
- Generic chain diagnostics cannot certify mixing:5.6 shuffles draws,6.1 combines multiple chains. This limitation is explicit in the release and methodology.

| Method | Primary C2ST accuracy ↓ | Secondary sliced W2 ↓ | Sampling seconds |
|---|---:|---:|---:|
| gpt-5.6-sol | 0.512500 | 0.014975 | 4.638 |
| gpt-6-sol | 0.497375 | 0.015708 | 0.867 |
| gpt-6.1-sol | 0.505600 | 0.016329 | 2.470 |
| Local Polya–Gamma Gibbs | 0.494100 | 0.016785 | 5.305 |
| Laplace approximation | 0.546250 | 0.078966 | 0.024 |

[Interpretation, scope filter and remaining gaps](../../docs/release-v09.md).

Raw pre-scoring sampler metadata are retained in `sampling-stage/`; their `sampled` status describes that intermediate stage. Final measured records and classifier audits are in `results/L06.json`. No sampling call is pending.
