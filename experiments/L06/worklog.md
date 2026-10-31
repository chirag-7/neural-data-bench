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
