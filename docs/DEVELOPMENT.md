# Development

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,kokoro]' types-requests
```

The offline model-adapter tests need PyTorch and Hub support supplied with the Kokoro setup.
The mypy check also needs the requests stubs from `types-requests`.
Add `huggingface` or `mlx` when working with those real engines.
`requirements-dev.txt` installs development tools and Kokoro; install the requests stubs separately.
Install FFmpeg and ffprobe for the default suite's local media checks.

## Required checks

```sh
python -m black --check epub_listener tests
python -m ruff check epub_listener tests
python -m mypy epub_listener
python -m pytest -q
git diff --check
```

The default suite selects `not live` through `pyproject.toml`.
The current suite has 235 selected cases and 11 live cases.
The original performance baseline has 196 selected cases.
The 39 added parser cases characterize malformed and ordinary markup.
No cases are removed during cleanup.

Offline tests include real FFmpeg processing of synthetic audio.
They also use fake external models, services, and failures to test specific contracts.
Those fakes do not establish synthesis performance or acoustic quality.
Run `python -m pytest -m live` only with suitable models, hardware, and network authorization.
Live tests can download models, call external services, or fetch remote pages.
They are not part of the reported local acceptance run.

Do not regenerate expected outputs merely because a test fails.
Preserve parser fixtures and transcript fixtures when refactoring.
Tests cover durable output, error propagation, callback ordering, cancellation, resume identity, and transcript validation.
When auditing tests, keep regression and boundary cases unless surviving coverage proves them redundant.
An injected wrong alignment result must make retained transcript tests fail.
Resume tests must have valid cache settings and transcripts before testing other invalidation guards.

## Build and installed smoke

Use a separate environment for packaging tools:

```sh
python -m pip install build wheel
python -m build
python3 -m venv /path/to/empty-smoke-env
/path/to/empty-smoke-env/bin/python -m pip install dist/epub_listener-2.1.0-py3-none-any.whl
/path/to/empty-smoke-env/bin/epub-listener --help
```

Run installed commands from a directory outside the source checkout.
Confirm imports resolve inside the smoke environment.
Check the wheel and source archive contents, package metadata, and installed dependencies.
Perform a synthetic EPUB conversion and resume through a real installed backend.
Compare decoded audio, chapter markers, transcript data, and errors with known outputs.
A help-only smoke does not prove conversion works.

Builds and checks create `build/`, `dist/`, `*.egg-info/`, bytecode, and tool caches.
Git ignores these generated paths.
Remove only artifacts you own; preserve environments, books, and audit evidence.
For a clean checkout, build from a task-owned source copy and direct logs outside the repository.

## Extending adapters

Implement `TTSProvider` from `infrastructure/tts/ports.py` for a new transport.
For waveform engines, subclass `WaveformTTSProvider` and implement `synthesize_chunk` returning `AudioChunk`.
Register backend selection in `create_tts_batch_generator()`.
Keep model-specific work outside the application layer.

The waveform base supplies chunking, format checks, pause insertion, speed filters, transcript estimates, and chapter publication.
A provider must complete durable output before reporting its duration.
Batch callbacks run serially and must identify submitted chapters exactly once.
A failure must prevent assembly of a partial book.

Include output-affecting options in the backend identity and test invalidation.
The existing identity scheme has limits described in [Models](MODELS.md#resume-identity).
Do not assume it is a content-addressed cache.
Direct use-case callers own workspace lifecycle and must place tracker state beside chapter audio.

## Scrapers

Implement `NovelScraper` and provide an explicit entry point.
The current Worm scraper has offline request-failure and output-publication tests.
Those tests do not prove the current remote website still matches its selectors.

## Specialized repair script

`scripts/repair_lord_of_the_mysteries.py` is a separate, book-specific utility.
It expects a 1,409-chapter PDF and an EPUB missing exactly ten numbered chapters.
It needs PyMuPDF, which is not a declared converter dependency.
Its arguments are `source_epub source_pdf output_epub --report report.json`.
It writes a repaired EPUB and a report at the supplied destinations.
It is not a generic repair command, installed entry point, or part of the converter's correctness claim.
The cleanup retains it because lack of internal callers does not establish that its user workflow is obsolete.
No private input is used to execute it during acceptance.

## Performance evidence

See [Performance](PERFORMANCE.md) for measured boundaries and limitations.
Use completed work, excluded warmups, repeated samples, and recorded power/load conditions for comparisons.
Keep performance evidence outside the source tree.
Do not interpret unit-test durations, stub synthesis, or instrumented profiles as production throughput.
