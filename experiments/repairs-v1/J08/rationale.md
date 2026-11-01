# Separate post-hoc repair v1

Two-line shape repair: flatten arrays before np.unique(return_inverse=True), so inverse labels and flattened pixel masks share dimensions under current NumPy. No thresholds, features, hyperparameters, labels, matching rules or scoring are changed.

This is repair-assisted performance, never a replacement for the original single-shot attempt. No new LLM call or test-label-dependent parameter tuning. Sealed before rescoring,180seconds and one numerical CPU thread per procedure. B08 additional fresh-process decoding is verification, separately timed.
