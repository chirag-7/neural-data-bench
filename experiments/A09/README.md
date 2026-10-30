# A09 execution adapter

See [protocol](protocol.md), [model-facing metadata](metadata.json), [actual acquisition manifest](data-manifest.json), and [worklog](worklog.md).

`adapter.prepare()` reacquires and validates original public files and freezes the documented slice; `adapter.load()` returns train_x, train_y, test_x, test_y; `adapter.baseline(...)` is a conventional matched reference, not verified specialist SOTA. Raw and prepared arrays live in ignored `data/cache/A09/`. Generated programs and results are added only by the central experiment runner.

An additional archived specialist reference is now available: [VASSI methods and caveats](archived-vassi/README.md), [all run summaries](archived-vassi/summary.json), [alignment verification](specialist-alignment.json), and [source search](specialist-search-review.md). The original run-00 selection plan is preserved unchanged from before scoring; its then-pending status describes that earlier admission stage.
