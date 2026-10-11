# Model backends

## Engine matrix

| Engine | Model source | Default concurrency | Timing granularity | Install |
|---|---|---:|---|---|
| `edge` | Microsoft Edge service | async | word | base package |
| `kokoro` | `hexgrad/Kokoro-82M` through Kokoro | process pool | word | `.[kokoro]` |
| `kokoro-mlx` | FastKokoro or mlx-audio | sequential | word or sentence | `.[mlx]` |
| `huggingface` | Hub ID or local Transformers directory | sequential | sentence estimate | `.[huggingface]` |
| `command` | any local executable/model runtime | sequential | sentence estimate | base package |

The Hugging Face adapter supports models accepted by the installed Transformers `text-to-speech` pipeline. “All Hugging Face models” cannot literally include classifiers, language models, image generators, or TTS repositories that do not implement the Transformers pipeline contract; those are not interchangeable speech models. The `command` adapter covers other TTS runtimes without requiring project changes.

## Hugging Face

Minimum invocation:

```bash
epub-listener book.epub --engine huggingface --model facebook/mms-tts-eng
```

`--model` may be a Hub repository or local directory. `--revision` accepts a branch, tag, or commit. Pin a reviewed commit for reproducible builds. The adapter delegates Hub access to the installed libraries. This acceptance run does not exercise authenticated or remote model loading.

Device selection is `auto` by default: CUDA, then Apple MPS, then CPU. Override it with `--device`. Precision may be `auto`, `float32`, `float16`, or `bfloat16`. A `device_map` supplied in pipeline options takes precedence over the simple device selection and requires Accelerate.

### Model-specific options

`--model-options` accepts a JSON object with four optional namespaces:

```json
{
  "pipeline": {"device_map": "auto"},
  "preprocess": {"voice_preset": "v2/en_speaker_6"},
  "forward": {"speaker_id": 2},
  "generate": {"do_sample": false, "temperature": 0.7}
}
```

- `pipeline` is passed while the model is loaded.
- `preprocess`, `forward`, and `generate` are passed on every synthesis call.
- Dedicated security and identity fields (`model`, `revision`, `device`, `dtype`, `trust_remote_code`, and offline mode) cannot be overridden inside JSON.
- Use `@path.json` instead of inline JSON for complex settings.

SpeechT5-style speaker embeddings can be a finite numeric `.npy` or JSON array:

```bash
epub-listener book.epub --engine huggingface --model microsoft/speecht5_tts \
  --speaker-embedding narrator.npy
```

The `--voice` shortcut means a Bark voice preset or a numeric VITS speaker ID. There is no universal Transformers voice parameter, so Epub Listener rejects an ambiguous `--voice` for other architectures and points to `--model-options` rather than silently ignoring it.

Some repositories require extra Python packages named in their model card. Install those into the same environment. A repository that implements only a custom script—not the Transformers TTS pipeline—belongs behind the command adapter.

### Security and offline use

`--trust-remote-code` executes Python from a model repository on the local machine. It is off by default. Review the repository, pin `--revision` to a commit, and only then enable it.

Use `--local-files-only` with a cached Hub model or a local model directory to prevent downloads:

```bash
epub-listener book.epub --engine huggingface --model ./models/narrator \
  --local-files-only
```

## Local command protocol

The command is parsed with platform shell quoting and launched directly, never through a shell. It receives UTF-8 chapter/chunk text on stdin. These placeholders are allowed:

| Placeholder | Value |
|---|---|
| `{output}` | required temporary output audio path |
| `{text_file}` | optional UTF-8 file containing the same text as stdin |
| `{voice}` | `--voice`, or an empty string |

Example wrapper contract:

```bash
epub-listener book.epub --engine command \
  --model-command 'python local_tts.py --input {text_file} --output {output}' \
  --command-output-format wav --model-timeout 1800
```

The process must exit successfully and write non-empty, decodable WAV, MP3, FLAC, or Ogg audio. The adapter validates sample rate, shape, finite samples, duration, and the encoded MP3 before atomically replacing cached chapter audio. Output logs spill to a temporary file and only a bounded tail enters an error; a timeout or interrupt kills the command's POSIX process group while the parent remains active. Detached descendants are outside that guarantee. On an error, timeout, or interrupt, an existing chapter file is preserved.

`--chunk-chars 500` is the default for local engines. Splits prefer sentence boundaries, audio is written to a chapter WAV, and the Hugging Face pipeline is reused within its provider. Each returned chunk still occupies memory. Set it to `0` if a wrapper performs its own long-text processing. `--chunk-pause-ms` controls the inserted boundary pause.

## Kokoro and MLX details

Kokoro defaults to `af_heart`; its automatic mode uses a process pool.
Each worker can hold its own model copy.
`--kokoro-hybrid-mps` uses one MPS worker and one CPU worker.
This topology is not a measured speed guarantee for other hardware.

The MLX adapter prefers the separate `fastkoko` package when available.
It selects `ship-q8` by default and caches engines by preset.
`--kokoro-preset` or the legacy `EPUB_KOKORO_PRESET` can request another preset.
An explicit preset fails if FastKokoro is unavailable.
The MLX extra installs `mlx-audio==0.4.5`, not FastKokoro.
Without FastKokoro or an explicit preset, the adapter loads `mlx-community/Kokoro-82M-bf16` through mlx-audio.
That fallback applies a 2.7 dB gain and clips samples to the allowed range.
The FastKokoro path does not apply that gain.

The CLI restricts student presets to `af_heart` and exactly `+0%` speed.
Token cues are used when available; otherwise chunk spans produce sentence estimates.
No current acoustic or relative preset quality claim is established by the offline adapter tests.

## Resume identity

Generation keys combine backend identity, voice, and speed.
Hugging Face identity includes model, revision, device, dtype, loading policy, model options, local signatures, speaker embeddings, and chunk settings.
Command identity includes the template, detected executable/file arguments, output format, and chunk settings.
The command timeout does not change the audio identity.
Title, author, destination, and transcript enablement are not part of the generation key.
Enabling transcripts separately requires each cached transcript file to exist.

Large local files use signatures based on path metadata plus sampled beginning and ending content.
Files at most 128 KiB are read fully; larger files contribute the first and last 64 KiB.
Directory traversal stops after its file-count bound.
These signatures can miss changes and do not track every wrapper dependency or remote model revision change.
Pin model revisions and use a fresh workspace when dependencies change outside this scheme.

Backend settings use a short SHA-256 fingerprint in progress and transcript metadata.
This avoids storing full command options there; it is not encryption or a promise that other logs contain no sensitive data.
Cached chapter audio itself is checked for existence and nonzero size, not a content digest.
See [Troubleshooting](TROUBLESHOOTING.md#resume) before reusing modified workspace files.
