# Repair-assisted sensitivity track

This post-hoc debugging track considers all eight original failed measurement records. It preserves the original programs, protocols, scoring code, first-attempt result files and measurement ledger. It made no new model calls. These results are separate from single-shot results and are excluded from the original macro analysis.

The machine-readable deliverable is `results/repairs-v1.json`, an object with `attempts`, `latest_successes` and `unresolved`. Each latest success identifies its original measurement key, repair type and revision, score, metric, direction, code and prediction paths and SHA256 hashes, sealed run-spec hash, and line-limit compliance. The seven latest successes comprise four recovered runtime failures and three B08 controls. N05 remains above the original line limit, so only three recovered failures meet that format requirement.

| Task | Method | Change | Repair-assisted score |
| --- | --- | --- | ---: |
| B08 | GPT-5.6 Sol | Permit heapq in harness; program unchanged | 7.585598308443002 bits/event |
| B08 | GPT-6 Sol | Permit heapq in harness; program unchanged | 7.693066944185707 bits/event |
| B08 | GPT-6.1 Sol | Common-procedure control; program unchanged | 8.636801620045114 bits/event |
| B08 | Spikepack | Common-procedure reference control | 8.142312213400157 bits/event |
| B08 | zlib task baseline | Common-procedure reference control | 11.918156003544585 bits/event |
| J08 | GPT-6.1 Sol | Flatten both arrays before unique/inverse indexing | 0.57563018487252 instance F1 |
| N05 | GPT-5.6 Sol | Traverse legacy HDF5 metadata aliases | 1.0 field accuracy (61/61) |

B08 bits/event is lower-is-better and equally averages the seven recording scores. All five methods processed all seven recordings. Every one of the 35 retained payloads passed an additional independent fresh-process decode without invoking its encoder. Original successful control scores and payloads match. Generated B08 programs remain byte-identical. Runs retained the 180-second limit and one numeric CPU thread.

J08 changes only the two inputs to `np.unique` to their flattened forms. This restores the shape assumed by the existing flat masks and leaves the algorithm and scorer intact. Its saved two-image prediction has shape `(2, 727, 546)` and finite nonnegative integer instance labels.

N05 follows internal HDF5 hard/soft aliases recursively, rejects external links and prevents ancestor cycles by object address. It discovers stimulus/response roles from metadata; no expected numerical answers are introduced. The first traversal revision still failed and remains in the attempt history. Revision 2 recovers all 61 fields. The original program had 249 lines and the repaired copy has 265: its numerical recovery does not establish original line-limit compliance.

Four C05 archives remain unresolved: Speiser preparations 2, 4 and 5, and Deneux preparation 5. They lack finite predictions on observed input support. Numeric CSV headers are present and the published processing notebook provides no invertible header, orientation or shift correction. The official legacy scorer permits partial coverage by masking unavailable predictions/targets and truncating after downsampling; adopting that behavior would change this benchmark's complete-output contract. No unavailable predictions were filled, and no alternate-contract score replaces an original failure. Source pins, coverage counts and hashes are in `C05/diagnosis.json`, `C05/source-evidence.json` and `C05/source-notebook-evidence.json`.

`verification.json` records original-file preservation, sealed source hashes, saved payload identity checks and metric arithmetic, J08 output validity, and N05 field accuracy. It identifies the final results hash. `original-preservation.json` fixes the original ledger/result hashes. The report-only `scripts/finalize_repairs.py` assembles retained outputs and does not execute scientific methods, encoders or decoders.

Intermediate failures remain visible in `results/repairs-v1/round-1.json`, the attempt history, execution logs and `bookkeeping-error.json`. Patches, rationales and pre-execution run-specs are retained in each task directory. See `worklog.md` for the execution sequence.
