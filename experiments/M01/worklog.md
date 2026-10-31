# M01 execution and audit log

Frozen local commit `74b8244` predates all new model generations and fitted-method test scores. Source-specific preparation and independent checks are in [protocol](protocol.md), [manifest](../../data/manifests/M01.json), [verification](verification.json) and [generation provenance](generation-provenance.json). One submission perrequested model, no tools or execution feedback; all three unchanged programs are under240lines and finish within180 seconds. Source arrays remain ignored local caches; public acquisition identities and minimal joins are retained.

| Method | Score | Execution seconds | Code lines |
|---|---:|---:|---:|
| gpt-5.6-sol | 0.436515244 | 63.722 | 191 |
| gpt-6-sol | 0.437584086 | 1.145 | 120 |
| gpt-6.1-sol | 0.436633931 | 4.529 | 173 |
| task-baseline | 0.693080246 | 0.000 | — |
| behavioral-glm | 0.463877001 | 0.008 | — |

These are local measurements on a custom fixed split; current global best and equal total tuning/development effort remain unestablished. No model program, frozen input, primary metric or reference definition changed after scores. All predictions remain available in [central task records](../../results/M01.json).

All 100 source animals are retained; all 9538 selected targets and permitted histories independently match source members. Every target/history block is disjoint, and mouse partitions match the predeclared hash rule. The pooled paper-inspired GLM returns float32 probabilities; frozen sklearn loss therefore uses float32 arithmetic. Independent float64 rescoring differs by9.07e-9 in the mean and at most5.42e-8 for a mouse, below one float32 epsilon. Original predictions and primary score are retained; all other new numerical scores independently agree to1e-12. This precision effect does not affect the reported method ordering.
