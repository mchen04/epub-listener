# Architecture

## Boundaries

`__main__.py` connects the CLI, settings, and adapters.
Argument parsing runs before configuration and conversion imports.
Thus `--help` and argument syntax errors avoid those imports.
Normal conversion still loads the required adapters.

`BuildAudiobookUseCase.execute(BuildAudiobookCommand)` coordinates interfaces in `application/ports.py`.
The application does not select backends or load models.
Domain modules hold chapters, audio segments, speed rules, transcript validation, and text alignment.
Infrastructure modules implement parsing, synthesis, persistence, metadata, and file operations.

## Conversion flow

1. Parse arguments, load settings, and check required executables and optional packages.
2. Configure console logging and `logs/epub_listener.log`.
3. Select a batch adapter and resolve the workspace.
4. Read EPUB document items in EbookLib item order, excluding navigation documents.
5. Extract text and titles, disambiguate titles, filter short text, and remove exact text duplicates.
6. Match progress entries to chapter checksums and generation settings.
7. Generate pending chapters and record each successful completion.
8. Write chapter metadata and assemble the final MP3 with FFmpeg.
9. Attempt transcript embedding and sidecar publication.
10. Remove an automatically created workspace after success.

`BuildWorkspace` creates the command and tracker with the same directory.
Direct application callers must preserve that relationship and own directory lifecycle.

## Parsing

EbookLib reads the archive and serializes document bodies.
A restricted ASCII markup path uses ElementTree to extract ordinary text.
Declarations, non-ASCII content, unsupported tags, and incompatible structures use BeautifulSoup.
The fast path preserves the characterized title and text output.

Titles come from the first `h1`, `h2`, or `title`, or `Unknown Chapter`.
The parser joins non-empty trimmed lines with blank lines.
It keeps text with at least 100 characters and assigns numeric chapter IDs.
It removes exact text duplicates after assigning IDs, so IDs can have gaps.
It does not promise full EPUB rendering or spine-order reconstruction.

## Synthesis and concurrency

| Engine | Automatic scheduling | Local state |
| --- | --- | --- |
| Edge | bounded async jobs | remote speech service |
| Kokoro | process pool | pipeline cache in each worker |
| MLX Kokoro | sequential | FastKokoro preset cache or mlx-audio model |
| Hugging Face | sequential | one lazy Transformers pipeline per provider |
| Command | sequential | one executable invocation per text chunk |

Batch adapters report completed jobs serially.
The use case preserves chapter order despite out-of-order completion.
Unknown, duplicate, missing, or invalid results fail the build.
Generation failure stops further scheduling; completed chapters remain available for resume.
Tests cover callback errors, cancellation, and timeouts through controlled external failures.
They do not prove every external service or model will remain responsive.

Hugging Face and command adapters share waveform chunking, format checks, pauses, speed filters, and MP3 publication.
Kokoro and MLX use their own streaming generation paths.
The command adapter uses an argument vector without a shell.
See [backend contracts](MODELS.md).

## Persistence and output

`JsonProgressTracker` stores text checksums, durations, and generation keys in `progress.json`.
The cache check requires matching settings, non-empty chapter audio, and a positive recorded duration.
With transcripts enabled, it also requires a chapter transcript file to exist.
It does not hash or revalidate all cached audio and transcript contents.
Malformed progress JSON raises `ResumeError`.

Generated chapter files and assembly output use temporary files and durable replacement.
Replacement synchronizes the temporary file, replaces the destination, then synchronizes its directory.
A directory synchronization error can occur after replacement; this is not a rollback guarantee.
There is no lock for concurrent builds sharing a workspace or destination.

Assembly always concatenates and re-encodes through `libmp3lame`, quality setting 2, with ID3v2.3 metadata.
Its timeout scales with recorded duration.
Chapter boundaries use measured segment durations, preferring libsndfile frame counts with an ffprobe fallback.
The implementation has no completed-output assembly cache.

Transcript capture writes per-chapter JSON before reporting chapter completion.
The embedder validates combined cues, updates ID3 tags, and then writes the sidecar.
Embedding errors produce warnings and do not turn a completed audio build into a reported failure.
Tag updates are not a transaction with sidecar publication.
See the [transcript format](transcript-format.md) for these limits.

## Workspace and errors

| Situation | Workspace behavior |
| --- | --- |
| Successful fresh build | auto-created directory removed |
| Failure after conversion starts | auto-created directory retained; retry path printed |
| Failure before conversion starts | auto-created directory removed if present |
| Interrupt | existing auto-created workspace retained; resume path printed |
| Explicit `--resume-dir` | must exist; never deleted by workspace cleanup |

Expected domain errors derive from `EpubListenerError`:
`ConfigurationError`, `ParseError`, `TTSGenerationError`, `AssemblyError`, `AudioProbeError`, `ResumeError`, and `TranscriptError`.
The CLI returns 1 for caught domain errors and 130 for a caught interrupt.
Argparse returns 2 for syntax errors and 0 for help.
Unexpected exceptions can still produce tracebacks.
