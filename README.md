# EPUB Listener

Convert an EPUB into an MP3 with chapter markers and an optional transcript.
Choose Edge-TTS, Kokoro, MLX Kokoro, a Transformers TTS model, or a local command.
Player support for chapters and transcripts varies.

## Install

Use Python 3.10 or later and install FFmpeg, including `ffprobe`.
On macOS, install FFmpeg with `brew install ffmpeg`.
Kokoro also needs `espeak-ng` for phonemization.

```sh
git clone https://github.com/mchen04/epub-listener.git
cd epub-listener
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The base install includes Edge-TTS and the command adapter.
Install an extra for each local model adapter you need:

```sh
python -m pip install -e '.[kokoro]'
python -m pip install -e '.[huggingface]'
python -m pip install -e '.[mlx]'
```

The MLX extra installs `mlx-audio`; it does not install the separate `fastkoko` package.
Model adapters can download weights on first use.
`requirements.txt` installs the base package plus Kokoro.
`requirements-dev.txt` adds development tools and Kokoro.

## Convert

```sh
# Edge-TTS sends book text to an external service.
epub-listener book.epub

# Set output, metadata, voice, and speed.
epub-listener book.epub book.mp3 --author "Author Name" \
  --title "My Book" --voice en-GB-RyanNeural --speed +15%

# Local adapters
epub-listener book.epub --engine kokoro --voice af_heart
epub-listener book.epub --engine kokoro-mlx --voice af_heart
epub-listener book.epub --engine huggingface --model /models/narrator --local-files-only

# The executable receives text on stdin and writes WAV at {output}.
epub-listener book.epub --engine command \
  --model-command 'piper --model voice.onnx --output_file {output}'
```

`python -m epub_listener` uses the same entry point.
Without an output argument, files go to `outputs/<sanitized-input-stem>_audiobook.mp3`.
The title defaults to the input filename stem, and the author defaults to `Michael Chen`.
The converter does not infer these fields from EPUB metadata.
See the [complete CLI reference](docs/CLI.md) for defaults, limits, and compatibility flags.

## Resume and transcripts

Failed or interrupted conversions print a workspace path for `--resume-dir`.
A successful fresh build removes its temporary workspace.
To retain chapter files from the start, create a directory and pass it explicitly:

```sh
mkdir book-work
epub-listener book.epub --resume-dir book-work
```

Resume checks chapter text and generation settings before reusing chapter audio.
It still assembles the final MP3 with FFmpeg on every run.
Workspace files are trusted local build state, not a content-verified archive.
Do not share one workspace or destination between concurrent builds.
See [resume limits and errors](docs/TROUBLESHOOTING.md).

Transcript capture is on by default; `--no-transcript` disables capture and embedding.
Successful embedding adds a compressed ID3 frame and `<output-stem>.transcript.json`.
Word timings depend on the backend; sentence timings can be estimates.
These cues do not establish acoustic alignment accuracy.

## Other entry points

The [Worm scraper](docs/CLI.md#scraper) creates an EPUB from remote pages.
The repository also retains a specialized EPUB/PDF repair script.
That script is separate from conversion and needs PyMuPDF; see [Development](docs/DEVELOPMENT.md#specialized-repair-script).

## Documentation

- [CLI reference](docs/CLI.md)
- [Model backends](docs/MODELS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development and checks](docs/DEVELOPMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Transcript contract](docs/transcript-format.md)
- [Measured performance and limits](docs/PERFORMANCE.md)
- [Changelog](CHANGELOG.md)
