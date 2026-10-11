# Read-along evidence scope

## Historical material

`listen-check.json` contains ten historical transcription observations.
It has no audio, model revision, executed command, or reproducible acoustic reference in this checkout.
Retain it as historical data; do not use its `match` fields as a current quality gate.
This cleanup does not delete or rewrite those observations.

The previous narrative ledger mixed producer work, consumer work, browser claims, and acoustic measurements.
Its old text remains in Git history.
Current documentation removes those unsupported verification claims rather than asserting that they still hold.
No other application is inspected or changed for this work.

## Current producer evidence

The retained offline suite checks transcript schema, cue mapping, capture adapters, embedding failures, and chapter-frame preservation.
Some adapter tests use fake model or network results; those are contract tests, not acoustic measurements.
The live accuracy gate remains available under `tests/integration/test_accuracy_gate.py`.
It is not executed as part of this local acceptance run.

The local performance work uses synthetic EPUBs, genuine installed Samantha speech, and FFmpeg.
It checks exact decoded PCM, transcript data, chapter markers, and resume invariants against original outputs.
Its final expectations come from the original source before checking the retained implementation.
See [Performance](../PERFORMANCE.md) for boundaries and limits.

The Edge adapter retains its existing 100 ms word-boundary correction.
Offline cue tests check that arithmetic; they do not establish current acoustic accuracy.
Neither this note nor the transcript schema certifies a consumer application, universal model compatibility, or listening quality.
