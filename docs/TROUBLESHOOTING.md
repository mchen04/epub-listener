# Troubleshooting

## Resume

Use the path printed after an interrupted or failed build:

```sh
epub-listener book.epub --resume-dir /path/to/existing-workspace
```

The directory must exist.
It contains `progress.json`, chapter MP3s, chapter transcripts, and metadata.
A successful fresh build removes its automatic workspace.
An explicit resume directory remains.

Changed chapter text, voice, speed, or backend identity can regenerate chapter audio.
Missing or empty chapter audio also requires generation.
Enabling transcripts regenerates cached chapters that lack transcript files.
Changing title, author, or destination rebuilds final output metadata without requiring new narration.

Resume trusts recorded durations and existing non-empty chapter files.
It does not detect every byte replacement, damaged transcript, changed external model, or concurrent write.
Local model signatures sample large files; they are not complete content hashes.
Use a new workspace if cached files are suspect.
Do not run concurrent builds against one workspace or destination.
A malformed progress file produces a resume error; preserve it for diagnosis.

Final output is always assembled again, including completed resumes.
No assembly cache marker or reuse lock is created.

## Missing tools or models

Check that `ffmpeg` and `ffprobe` are in `PATH`.
On macOS, `brew install ffmpeg` installs both.

Install the selected optional adapter with `python -m pip install -e '.[kokoro]'`, `'.[huggingface]'`, or `'.[mlx]'`.
The MLX extra provides `mlx-audio`, not FastKokoro.
An explicit FastKokoro preset fails if that separate package is absent.
Kokoro may also need `espeak-ng`.

Model weights can require a download on first use.
Hugging Face `--local-files-only` requires an already cached model or a complete local model directory.
A repository must support the installed Transformers TTS pipeline.
Additional model inputs belong in `--model-options` or `--speaker-embedding`.
Review repository code before enabling `--trust-remote-code`.

## Resource or model failures

Reduce Kokoro workers or use `--concurrency sequential` to limit model copies.
Hybrid MPS mode requires the Kokoro engine and parallel or automatic scheduling.
Hugging Face, MLX, and commands use sequential scheduling.
For Hugging Face device errors, try `--device cpu --dtype float32`.
For input limits, reduce `--chunk-chars`; character limits do not guarantee model token limits.
A value of 0 delegates long-input handling to the model or wrapper.

## Command failures

The template requires `{output}`; `{text_file}` and `{voice}` are optional.
Text arrives on stdin and in the temporary text file.
The executable must exit zero and write decodable audio in the declared format.
The command runs without shell expansion, pipes, or redirects.
Use a wrapper for operations that require a shell.

`--model-timeout` applies to each command chunk.
Timeout handling terminates the command process group on POSIX while the parent process remains active.
Detached descendants are outside that guarantee.
Error messages include a bounded diagnostic tail.
Failed generation preserves the previous chapter output until a validated replacement is ready.
A directory synchronization failure can occur after replacement.

## Chapters, transcripts, and logs

Chapter navigation depends on the player's ID3 support.
Inspect chapter metadata with `ffprobe` if the player shows no chapters.
The parser excludes navigation documents, short text below 100 characters, and exact duplicate text.
It reads document item order rather than reconstructing all EPUB reading-order rules.

Transcript embedding errors warn and leave the build reported as successful.
Check `logs/epub_listener.log` for missing or invalid chapter transcript files.
The sidecar path is `<output-stem>.transcript.json`.
A failed embed or `--no-transcript` does not delete an older sidecar at that path.
Treat the MP3's embedded frame as authoritative.
Sentence estimates are not word-level acoustic alignment.

Logging uses a console handler and a rotating file in the current working directory.
The root level follows `--log-level`; the console handler accepts INFO and above.
Caught domain errors exit 1, syntax errors exit 2, and caught interrupts exit 130.
Unexpected errors can still show a traceback.
Edge requires network access; service failures are not covered by offline checks.
