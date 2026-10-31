# K04 execution and audit log

Frozen local commit `74b8244` predates all new model generations and fitted-method test scores. Source-specific preparation and independent checks are in [protocol](protocol.md), [manifest](../../data/manifests/K04.json), [verification](verification.json) and [generation provenance](generation-provenance.json). One submission perrequested model, no tools or execution feedback; all three unchanged programs are under240lines and finish within180 seconds. Source arrays remain ignored local caches; public acquisition identities and minimal joins are retained.

| Method | Score | Execution seconds | Code lines |
|---|---:|---:|---:|
| singler | 0.554585005 | 0.319 | — |
| gpt-5.6-sol | 0.505071143 | 30.249 | 143 |
| gpt-6-sol | 0.531942043 | 0.852 | 91 |
| gpt-6.1-sol | 0.550550191 | 2.318 | 187 |
| task-baseline | 0.519326084 | 1.166 | — |

These are local measurements on a custom fixed split; current global best and equal total tuning/development effort remain unestablished. No model program, frozen input, primary metric or reference definition changed after scores. All predictions remain available in [central task records](../../results/K04.json).

All 12 original matrices were read directly, bypassing the previous R/Bioconductor loader dependency without changing the scientific source. All original gene axes agree; author donor metadata and annotation joins match. An independent implementation reproduces the top500 training-only gene selection and36 source-spot normalizations. One held-out donor underlies all four test sections. SingleR 0.5.1 was unavailable from the registry;0.5.0 was installed and tested on mock data before freezing the actual method. The first independent verifier reversed the barcode/section lookup key; only the verifier was corrected, with no change to prepared data or methods. GPT-6 uses a learnable-class-only criterion in inner validation when a donor lacks a class; the final scorer still includes all seven labels as frozen.
