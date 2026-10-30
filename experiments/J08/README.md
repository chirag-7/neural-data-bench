# J08 SynAPSeg 2D execution endpoint

Read [protocol](protocol.md), [model-facing metadata](metadata.json), [acquisition manifest](data-manifest.json), [worklog](worklog.md) and [source manifest](source-manifest.json).

`adapter.prepare()` acquires or verifies original public archives and prepares a fixed train-field → benchmark-field instance segmentation endpoint. `adapter.load()` returns training images, manual training labels, test images and the five separate expert test masks. `adapter.baseline()` returns the original author’s archived StarDist masks, explicitly a different optimization/information budget. `adapter.score()` computes the declared multi-rater object F1. No general model has been called by this preparation task.

Preparation additionally needs `tifffile==2026.10.15` and `imagecodecs==2026.10.10`; evaluation needs the repository NumPy/SciPy stack. Raw archives and prepared arrays live in ignored `data/cache/J08/`. Do not upload the raw archives by default. The data license is CC BY 4.0; cite Schamber and colleagues (2026) and the pinned Zenodo record.
