# I07 worklog

2026-10-30:

1. Read the original NEMAR record, stable version listing, complete file manifest, source README, BIDS dataset license and participant table. Noted that the README is sparse and participant demographics contain placeholders, so did not infer demographics or hand labels from those fields.
2. Read all sub-01 session events/channel/acquisition sidecars and the author's validation notebook as documentation without executing it. Inspected an original SNIRF file with h5py: continuous-wave `dataType=1`, 136 positive-amplitude measurements, 760/850 nm, time in seconds,0.112 s spacing. Channel-table units are V.
3. Searched original FRESH materials to resolve condition semantics, then verified the organizer's original four-session task description and the FRESH publication. The session filenames can be mapped to known left/right two-second finger-tapping conditions. The generic `motor` event label by itself is insufficient.
4. Froze subject1–7 training/8–10 evaluation, only left2s/right2s sessions, dimensionless optical-density conversion, per-event baseline correction, eight delayed one-second bins, balanced-accuracy scoring and a fixed mean-response/shrinkage-LDA reference before evaluated-model calls.
5. Implemented original-file acquisition and manifests plus assertions for license, channel count/order/types/units/status, SNIRF-vs-BIDS event alignment, positive finite intensities, time spacing, valid epoch bounds and disjoint participants. Raw/prepared recordings remain in the ignored cache.

This is a subject-disjoint diagnostic, with explicit condition/session confounding. No evaluated-model calls are performed by this data-admission subtask; release-level model execution records document those separately.

6. Preparation completed with 378 training events and 166 held-out events. Every one of the 20 downloaded SNIRF SHA-256 checksums matched the publisher manifest. Frozen mean-OD/shrinkage-LDA pooled balanced accuracy was 0.48464912280701755; participant scores were 0.38, 0.573076923076923 and 0.5. No preprocessing or reference parameters were changed after this check; see verification.json.
