# Separate post-hoc repair v1

One-line metadata traversal repair: visititems deduplicates hard-linked HDF5 objects and misses stimulus aliases under the sweep path. visititems_links visits every hard-link path; resolve handle[name], then preserve original sweep/role/unit metadata logic. No expected numerical answers or source-specific measured values are introduced.

This is repair-assisted performance, never a replacement for the original single-shot attempt. No new LLM call or test-label-dependent parameter tuning. Sealed before rescoring,180seconds and one numerical CPU thread per procedure. B08 additional fresh-process decoding is verification, separately timed.
