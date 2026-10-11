# Changelog

## Unreleased

- Extract ordinary ASCII EPUB markup through a restricted fast path, with BeautifulSoup fallback and 39 additional characterization cases.
- Defer configuration and backend imports until after CLI argument parsing.
- Remove an unused private alignment argument; keep public interfaces and all existing tests.
- Strengthen two resume test groups so unrelated cache invalidation cannot mask their intended checks.
- Ignore local environments and check caches; retain historical evidence and source fixtures.
- Update CLI, installation, backend, resume, transcript, architecture, development, and troubleshooting documentation.
- Replace unsupported performance and acoustic claims with bounded measurements and explicit limits.
- Completed resumes still reassemble through FFmpeg; the attempted assembly cache is rejected and reverted.

See [Performance](docs/PERFORMANCE.md) for measurements and [Development](docs/DEVELOPMENT.md) for retained checks.
The local run does not establish current live-service or neural-model correctness.

## 2.1.0 — 2026-08-09

### Added

- A unified `--engine` interface for Edge-TTS, Kokoro, MLX Kokoro, Hugging Face, and arbitrary local TTS commands.
- Hugging Face Hub and local-directory support for models accepted by the Transformers text-to-speech pipeline, including namespaced model options, speaker embeddings, revision pinning, offline loading, device selection, and explicit remote-code opt-in.
- A shell-free command adapter for other local model runtimes that write WAV, MP3, FLAC, or Ogg audio.
- Model documentation, packaging metadata, an MIT license, and source-distribution manifests.

### Changed

- Local waveform engines now share bounded sentence-aware chunking, disk-streamed audio assembly, portable speed conversion, transcript fallback, validation, and atomic MP3 commits.
- Heavy Kokoro, Hugging Face, and MLX dependencies are installable extras instead of default dependencies.
- Resume identities now include model configuration, loading policy, local artifact signatures, speaker embeddings, command dependencies, voice, and speed.
- Older Kokoro flags remain compatibility aliases while the implementation uses the unified backend selection path.

### Hardened

- Local commands run without a shell, use bounded diagnostic logs, enforce timeouts, and terminate descendant processes on POSIX.
- Hugging Face custom repository code is disabled by default, offline state is restored after loading, and model outputs are validated before encoding.
- Runtime preflight checks report missing FFmpeg, optional packages, and local executables before EPUB parsing or model downloads begin.

### Verification scope

The earlier release notes asserted live-model and acoustic results without reproducible receipts in this checkout.
Those assertions are removed from the current verification claim.
The historical transcript observation file remains labeled in [the evidence note](docs/evidence/read-along-ledger.md).
