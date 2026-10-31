# C06 acquisition worklog

31 October 2026. Reviewed C01/C06 admission cards, C05 transfer protocol, J08 adapter/scorer and generic expansion runner. Original CASCADE source shows DS04 comprises 15 newly recorded OGB1 zebrafish neurons (81 minutes); exclude all other source families to avoid overlap with C05. Downloaded every DS04 MAT file and verified publisher Git blob SHA1 plus local SHA256.

Acquisition: `python experiments/C06/adapter.py` (curl network access required only if cache missing). Preparation uses NumPy and SciPy; existing bundled Python plus `PYTHONPATH=../../work/pilot-deps` supplies dependencies in this workspace. Acquisition initially revealed a fluorescence array longer than its timestamps in one source; preparation matches publisher loader by dropping that untimed tail. All 45 recordings retained.

Validation: `python experiments/C06/verify_adapter.py` passed. Every prepared fluorescence sequence matches the unmodified upstream loader. Verified valid masks, target binning/smoothing conservation, disjoint neuron/specimen split, byte and hash integrity. No method was executed and no real-slice score was computed. No model calls, frozen artifacts, central registry, website, or Git commits changed.

Ready for scientific review then freeze. Remaining limitations: only four acute specimens/two heldout; filename-based specimen identity; native-rate/split/scoring differs from paper; GPL repository with no separate data-specific license declaration; OASIS is a conventional fixed reference, not CASCADE/SOTA. Do not use public global CASCADE weights trained on DS04 test cells.
