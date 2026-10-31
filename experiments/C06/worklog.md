# C06 acquisition worklog

31 October 2026. Reviewed C01/C06 admission cards, C05 transfer protocol, J08 adapter/scorer and generic expansion runner. Original CASCADE source shows DS04 comprises 15 newly recorded OGB1 zebrafish neurons (81 minutes); exclude all other source families to avoid overlap with C05. Downloaded every DS04 MAT file and verified publisher Git blob SHA1 plus local SHA256.

Acquisition: `python experiments/C06/adapter.py` (curl network access required only if cache missing). Preparation uses NumPy and SciPy; existing bundled Python plus `PYTHONPATH=../../work/pilot-deps` supplies dependencies in this workspace. Acquisition initially revealed a fluorescence array longer than its timestamps in one source; preparation matches publisher loader by dropping that untimed tail. All 45 recordings retained.

Validation: `python experiments/C06/verify_adapter.py` passed. Every prepared fluorescence sequence matches the unmodified upstream loader. Verified valid masks, target binning/smoothing conservation, disjoint neuron/specimen split, byte and hash integrity. No method was executed and no real-slice score was computed. No model calls, frozen artifacts, central registry, website, or Git commits changed.

Ready for scientific review then freeze. Remaining limitations: only four acute specimens/two heldout; filename-based specimen identity; native-rate/split/scoring differs from paper; GPL repository with no separate data-specific license declaration; OASIS is a conventional fixed reference, not CASCADE/SOTA. Do not use public global CASCADE weights trained on DS04 test cells.

## Batch 0.11 completed outcome update

31 October 2026. This dated append follows the preparation-only notes above; it does not modify the frozen contract, programs, source arrays or scores.

All 15 CASCADE DS04 OGB1 zebrafish neurons/45 recordings; 7 neurons/21 train recordings from 2 fish, 8 neurons/24 test recordings from 2 other fish. Custom native-rate 200 ms-smoothed count/Pearson endpoint, not paper benchmark. Default AR1 OASIS with training count scaling; public CASCADE global weights include held-out source and are not used. Source repository GPL3; no separate data-specific license declaration located, so raw arrays stay local.

| Model/slice | Numeric status | Exact score | Lines / compliance |
|---|---|---:|---|
| gpt-5.6-sol/batch-v11 | measured | 0.8564154409076183 | 224 / True |
| gpt-6-sol/batch-v11 | measured | 0.8465793019998664 | 114 / True |
| gpt-6.1-sol/batch-v11 | measured | 0.8675919925239051 | 214 / True |
| task-baseline/batch-v11 | measured | 0.7155173445914688 | Reference or pre-execution rejection |

Saved-output/source audit: results/audits/C06-batch-v11.json. Read-only score-blinded static review: literature/batch-v11-code-review.json (21 total submissions). No predictive method was rerun for this documentation.

Correlation does not establish count calibration. Existing secondary worst-neuron signed relative biases are 7.489846901852644, 24.107274065282635, 16.54368744847144 for general models and 201.67902883234314 for OASIS. No primary metric changed.

Current-global-best and matched-effort superiority remain unestablished. One code generation/model and bounded/cohort-dependent source coverage limit interpretation. Central integration is once for all seven tasks; no per-task release or commit.
