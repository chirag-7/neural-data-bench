# E01: additional source portability

Two prepared official NLB sources extend the existing frozen E01 supervised population diagnostic. They retain the original generated program text and hyperparameters, refit coefficients on the new source training arrays, and report official bits/spike. These are **two source slices of E01**, not two new independent task IDs. No fresh evaluated-model calls were made during preparation.

| Source | Scientific task | Same-session identity | Train / test trials | Time bins | Held-in → held-out |
|---|---|---|---:|---:|---:|
| [Area2_Bump](area2_bump/protocol.md) | Somatosensory population during perturbed reaching | Han, 2017-12-07, Miller laboratory | 364 / 98 | 30 × 20ms | 49 → 16 |
| [DMFC_RSG](dmfc_rsg/protocol.md) | Frontal population during interval reproduction | Haydn, 2016-12-11, Jazayeri laboratory | 1006 / 283 | 75 × 20ms | 40 → 14 |

Each directory contains `adapter.py`, `metadata.json`, `protocol.md`, `source-record.json`, `source-assets.json`, `data-manifest.json`, `recording-identity.json`, `validation.json`, and a preparation seal. Cache arrays live under `data/cache/E01-<slice>/data.npz`. Both train and test group arrays carry the same biological session label; official trial partitions provide the evaluation separation. Additional acquisition/preparation/verification code lives here without modifying the frozen parent E01 adapter.

The authoritative [official test-truth archive](https://media.githubusercontent.com/media/neurallatents/nlb_tools/42f8410b88e12db136910fa2f888b025ea0aa2ae/data/eval_data_test.h5) is shared with base E01 under `data/cache/E01/raw/eval_data_test.h5` and hash-checked before preparing either slice. Independent raw-spike reconstruction exactly matches every held-in test count. Official scorer parity and complete exact target equality, including DMFC NaN masks, pass.

DMFC inputs are complete fixed windows; targets alone use a hidden jittered variable scoring window. Preserve official masks unchanged, supply neither masks nor hidden jitter/behavior to evaluated programs, and require finite outputs throughout. Public test NWB omits held-out neurons and original set-time, so raw held-out timing cannot independently be reconstructed. No target shifts, interpolation or filling were introduced.

These results can assess algorithm portability to new neural populations and tasks. They do not reproduce the full unsupervised NLB leaderboard and do not support a new-model-generation trend by themselves. The unchanged Gaussian+Ridge reference is transparent but is not current specialist SOTA.
