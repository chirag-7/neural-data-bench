# E01 execution

Read [protocol](protocol.md), [metadata](metadata.json), [actual acquisition manifest](data-manifest.json), and [worklog](worklog.md). `adapter.prepare()` uses pinned official NLB tensor code; `adapter.load()` returns training/test arrays; `adapter.baseline()` implements the fixed conventional readout; `adapter.score()` is exact official NLB bits/spike. This is a custom supervised diagnostic with an explicit99trial training pool, not a full official leaderboard reproduction. Arrays/raw inputs stay in ignored `data/cache/E01/`.

Preparation dependencies: pynwb2.8.3, hdmf3.14.6, h5py3.15.1, ruamel.yaml0.18.17; scientific stack from the repository requirements. Isolated compatibility installation used during this run is `work/population-deps/compat`, plus `work/population-deps`, plus `work/pilot-deps` in PYTHONPATH, in that order. These dependency folders are not committed. Standard clean installations do not need those local paths.

`python experiments/E01/verify_adapter.py` reproduces independent raw-count and scorerchecks from the prepared cache (requires h5py). It never fits models. All original downloads are validated against fixed SHA256 values before preparation.
