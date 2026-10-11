# CLI reference

Run `epub-listener --help` or `python -m epub_listener --help` for argument syntax.
This reference describes repository behavior, including defaults from `Settings`.

## Paths, metadata, and execution

| Argument | Default and behavior |
| --- | --- |
| `input_epub` | Required existing file with an `.epub` suffix |
| `output_path` | Optional MP3 destination; otherwise use output directory and sanitized input stem |
| `--output-dir` | `outputs`; default filename ends in `_audiobook.mp3` |
| `--title` | Input filename stem, not EPUB title metadata |
| `--author` | `Michael Chen` |
| `--speed` | `+0%`; integer percentage from `-90%` through `+1500%`; use `--speed=-10%` for negative values |
| `--voice` | Edge: `en-US-AriaNeural`; Kokoro variants: `af_heart`; other engines: unset |
| `--resume-dir` | Unset; supplied path must already be a directory |
| `--no-transcript` | Capture and embedding are on unless disabled |
| `--concurrency` | `auto`; also accepts `sequential`, `async`, `parallel`, subject to backend support |
| `--max-workers` | 4; allowed range 1–64; sequential backends do not use a worker pool |
| `--log-level` | `INFO`; CLI accepts `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `-h`, `--help` | Print usage and exit before loading settings or conversion adapters |

An explicit output filename must end in `.mp3`.
Existing output is replaced after assembly validation.
A successful fresh build removes its temporary workspace.
A supplied resume directory remains after success or failure.
Final assembly runs even when all chapter audio is cached.

## Backend options

| Argument | Default and limits |
| --- | --- |
| `--engine` | `edge`; alternatives: `kokoro`, `kokoro-mlx`, `huggingface`, `command` |
| `--model` | Required for Hugging Face; Hub identifier or local directory |
| `--revision` | Unset; Hugging Face branch, tag, or commit |
| `--device` | `auto`; Hugging Face selects CUDA, then MPS, then CPU |
| `--dtype` | `auto`; also `float32`, `float16`, `bfloat16` |
| `--model-options` | JSON object or `@file`; namespaces: `pipeline`, `preprocess`, `forward`, `generate`; file limit 1 MiB |
| `--speaker-embedding` | Optional Hugging Face `.npy` or JSON numeric array |
| `--trust-remote-code` | Off; enables repository Python code for Hugging Face |
| `--local-files-only` | Off; enables offline Hub loading for Hugging Face |
| `--chunk-chars` | 500; 0 disables splitting; otherwise 100–100000; Hugging Face and command only |
| `--chunk-pause-ms` | 80; range 0–10000; Hugging Face and command only |
| `--model-command` | Required for command backend; must contain `{output}` |
| `--command-output-format` | `wav`; also `mp3`, `flac`, `ogg`; command only |
| `--model-timeout` | 1800 seconds per command chunk; range 1–86400; command only |
| `--kokoro-hybrid-mps` | Off; Kokoro parallel mode uses one MPS worker and one CPU worker |
| `--kokoro-preset` | FastKokoro preset; explicit values require the separate `fastkoko` package |

Model-loading flags belong to Hugging Face unless a row states otherwise.
Incompatible non-default options raise configuration errors.
A preset defaults to `ship-q8` when FastKokoro is available.
Without FastKokoro and without a requested preset, MLX uses `mlx-audio`.
Student presets require `af_heart` and exactly `+0%` speed.
Preset names do not establish relative speed or audio quality on this machine.

Edge supports `auto`, `async`, and `sequential`.
Kokoro supports `auto`, `parallel`, and `sequential`.
MLX, Hugging Face, and command support `auto` and `sequential` only.

## Compatibility and environment

`--use-kokoro` selects Kokoro when `--engine` is absent.
`--use-kokoro --kokoro-mlx` selects MLX; `--kokoro-mlx` alone does not select it.
`--engine kokoro-mlx` is the direct form.
`--kokoro-voice` overrides `--voice` for a Kokoro engine.
Conflicting engine selectors produce configuration errors.

Settings read `EPUB_LISTENER_<FIELD>` variables and a `.env` file in the current directory.
Explicit CLI values take precedence, followed by environment, `.env`, and defaults.
For example, `EPUB_LISTENER_LOG_LEVEL=DEBUG` sets the default log level.
`EPUB_LISTENER_TRANSCRIPT=false` disables transcripts through settings.
No CLI flag explicitly turns transcripts back on.
The legacy `EPUB_KOKORO_PRESET` also supplies a FastKokoro preset when no explicit preset exists.
External model libraries can have their own settings.

## Scraper

```sh
python -m epub_listener.scrapers.worm --output worm.epub
```

The scraper accesses remote pages and is separate from conversion.
It accepts `--delay` (default 1.5 seconds), `--start` (zero-based, default 0), and `--end` (exclusive).
By default, a failed chapter fetch aborts without publishing a partial EPUB.
`--allow-partial` permits escaped failure placeholders.
An empty selected range or a handled scrape error exits with status 1.
