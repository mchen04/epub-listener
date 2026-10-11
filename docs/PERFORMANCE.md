# Performance measurements and limits

These results describe bounded synthetic workloads on one MacBook Pro.
They do not promise a speed increase for every book, backend, or machine.

## Retained changes

The parser uses a restricted ElementTree path for ordinary ASCII markup.
BeautifulSoup remains the fallback for other content.
The CLI defers configuration and backend imports until after argument parsing.
Normal conversion still loads its required adapters.
Completed resumes still run FFmpeg assembly.

| Attempt | A median ms | B median ms | Reduction ms | A range ms | B range ms | Frozen noise ms | Result |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| EPUB chapter extraction | 138.551 | 21.736 | 116.815 | 43.991 | 12.964 | 91.943 | Retained |
| CLI help startup | 311.884 | 67.970 | 243.914 | 173.975 | 39.331 | 186.694 | Retained |
| Completed resume assembly cache | 97.460 | 79.832 | 17.628 | 31.062 | 30.831 | 50.000 | Rejected and reverted |

Each comparison has ten interleaved measurements per side after an excluded warmup per side.
Range means maximum minus minimum.
The original baseline has twenty measured samples.
Its useful-gain rule is `max(50 ms, 10% of the original median)`.
Noise is the larger of useful gain and original range.
Acceptance requires a reduction above both frozen noise and the current A range.

The extraction comparison starts from `8a143fd` and produces `7d5f787`.
The startup comparison starts from `7d5f787` and produces `0007f4f`.
The rejected cache starts from `0007f4f` and produces no commit.
Its additional concurrency test demonstrates stale output publication during a chapter update.
Its speed reduction also misses the acceptance threshold.
No cache code or cache files ship from that attempt.

## Timing boundaries

The parser fixture contains 120 synthetic chapters with 48 paragraphs each.
Timing includes archive reading, extraction, filtering, deduplication, and materialized chapter output.
It excludes imports, fixture construction, and comparisons against expected output.
The parser's share of a complete large-book narration is unknown.
The held-out Unicode fixture uses the conservative fallback and shows no qualifying parser speed increase.

Startup measures a new Python process completing `python -m epub_listener --help`.
It does not measure model startup or time to first audio.
Speech and resume measurements complete the application use case, including final output publication and transcript embedding.
Output comparisons occur outside the timing boundary.
Speech uses genuine installed Samantha synthesis through `/usr/bin/say`, with real FFmpeg encoding.
The command voice uses 24 kHz WAV, sequential execution, 800-character chunks, and 80 ms pauses.
These measurements do not use simulated synthesis as a performance substitute.

## Conditions and correctness

Both sides run on mbp-main: Mac17,9, 15 logical CPUs, 24 GiB, macOS 26.4.
Python is 3.12.8; FFmpeg and ffprobe are 7.1.
Valid windows use AC power, power mode 0, and no reported thermal warning.
One-minute load stays within 2.0 of each window's start.
Inconclusive windows remain in external receipts and are not pooled into valid results.

Checks compare ordered chapter content, decoded PCM, durations, chapter markers, transcript structure, and resume reuse.
The held-out book has 37 chapters with 73 paragraphs; its three-chapter speech case runs at +25% speed.
The untouched final case has 81 chapters with 31 paragraphs; its one-chapter speech case runs at -10% speed.
Final expectations come from original `8a143fd` before checking the retained implementation.

Secondary metrics remain within their frozen limits; those wide limits can hide small regressions.
For example, tuning speech increases by 50.406 ms in the extraction comparison and 61.998 ms in the startup comparison.
No general narration speed increase is established.
No external service, neural model, private book, live scraper, acoustic word alignment, or browser playback is measured here.

Raw commands, source snapshots, samples, failures, and final check receipts remain in the external task evidence directory.
They are local records, not a portable benchmark suite or an independent production certification.
