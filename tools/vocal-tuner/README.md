# Vocal Tuner

`vocal-tuner` is a Rust CLI for offline and live key-aware pitch correction on vocal/acapella recordings. It is designed for the remix pipeline's vocal production stage: pass in an isolated vocal, choose a key and scale, and render a tuned vocal file, or monitor a microphone through the same tuner in real time.

This is a deterministic local DSP tool, not a licensed clone of Antares Auto-Tune. It implements the production controls expected from a vocal tuner while keeping offline render behavior stable for pipeline use.

## Features

- Key and scale constrained pitch correction
- Hard-tune through natural retune response
- Natural, modern pop, and hard-tune presets
- Correction amount, wet/dry mix, humanize, vibrato preservation, and tuning reference controls
- Transient and consonant protection to avoid tuning attacks, breaths, and noisy phonemes
- Pitch confidence gating, minimum voiced-frame QA, peak ceiling, and fail-on-warning mode
- YIN-based pitch tracking for monophonic vocals
- Multi-channel WAV read/write with PCM16, PCM24, PCM32, and float32 input support
- Optional FFmpeg decode/encode for MP3, FLAC, M4A, and other formats
- Render summary and optional JSON report with voiced-frame and correction statistics
- Terminal-first live microphone monitoring with optional dry/wet WAV recording
- Unit tests and verification script

## Build

```bash
cd tools/vocal-tuner
cargo build --release
```

## Usage

```bash
cargo run --release -- \
  render \
  --input /path/to/acapella.wav \
  --output /path/to/acapella-tuned.wav \
  --key C# \
  --scale minor \
  --preset pop \
  --retune-speed 0.65 \
  --amount 1.0 \
  --mix 1.0 \
  --humanize 0.05 \
  --preserve-vibrato 0.5 \
  --report /path/to/acapella-tuned-report.json
```

The `render` subcommand is optional for compatibility. Existing calls such as `vocal-tuner --input in.wav --output out.wav` still run offline render mode.

For non-WAV input or output, install FFmpeg and use the same command with `.mp3`, `.flac`, `.m4a`, or another FFmpeg-supported extension.

## Live Microphone Mode

List available audio devices:

```bash
cargo run -- devices
```

Start live tuned monitoring from the default microphone to the default output:

```bash
cargo run -- live \
  --input-device default \
  --output-device default \
  --key A \
  --scale minor \
  --preset pop \
  --monitor tuned
```

Record dry mic input and tuned output while monitoring the tuned signal:

```bash
cargo run -- live \
  --input-device default \
  --output-device default \
  --key A \
  --scale minor \
  --preset hard \
  --monitor tuned \
  --record-dry /tmp/voice-dry.wav \
  --record-wet /tmp/voice-tuned.wav
```

Monitor modes:

| Mode | Output |
| --- | --- |
| `dry` | Untuned microphone |
| `tuned` | Pitch-corrected microphone |
| `both` | Equal blend of dry and tuned |
| `muted` | No monitoring; recording still works |

Live mode is intended for terminal-first auditioning and recording. It is not a DAW plugin and does not provide plugin-host automation. Expected monitoring latency depends on the audio device and tuning frame settings; start with defaults, then lower `--frame-ms` or set `--buffer-size` only if the device remains stable.

### WSL Audio Setup

On WSL2, Windows audio devices are normally exposed through WSLg PulseAudio rather than as physical ALSA cards. Install the ALSA/Pulse bridge packages in the distro:

```bash
sudo apt-get update
sudo apt-get install -y libasound2-plugins alsa-utils pulseaudio-utils
```

Confirm WSLg exposes the Pulse server:

```bash
echo "$PULSE_SERVER"
pactl info
pactl list short sources
pactl list short sinks
```

If ALSA clients still cannot see the WSLg Pulse bridge, create `~/.asoundrc`:

```text
pcm.!default {
  type pulse
}

ctl.!default {
  type pulse
}
```

Then rerun `cargo run -- devices`. If Windows has multiple microphones or outputs, choose the active defaults in Windows Sound settings; WSLg may expose those as routed Pulse sources/sinks instead of one Linux device per physical Windows endpoint.

## Options

| Option | Default | Description |
| --- | ---: | --- |
| `--input <FILE>` | required | Input vocal/acapella file. WAV is native; other formats require FFmpeg. |
| `--output <FILE>` | required | Output file. WAV is native; other formats require FFmpeg. |
| `--report <FILE>` | off | Optional JSON render report for pipeline integration. |
| `--key <NOTE>` | `C` | Root note: `C`, `C#`, `Db`, `D`, `Eb`, `E`, `F`, `F#`, `Gb`, `G`, `Ab`, `A`, `Bb`, `B`. |
| `--scale <SCALE>` | `major` | `major`, `minor`, `chromatic`, `pentatonic-major`, `pentatonic-minor`. |
| `--preset <NAME>` | off | `natural`, `pop`, or `hard`. Later flags override preset values. |
| `--retune-speed <0..1>` | `0.35` | Correction response. Use `1.0` for hard-tune and lower values for smoother natural tuning. |
| `--amount <0..1>` | `1.0` | How much detected pitch is moved toward the target pitch. |
| `--mix <0..1>` | `1.0` | Wet/dry blend. |
| `--humanize <0..1>` | `0.08` | Leaves small deviations around target notes untouched. |
| `--preserve-vibrato <0..1>` | `0.65` | Reduces correction depth so expressive pitch motion survives. |
| `--concert-a <HZ>` | `440` | Tuning reference. |
| `--min-f0 <HZ>` | `70` | Lowest expected vocal pitch. |
| `--max-f0 <HZ>` | `900` | Highest expected vocal pitch. |
| `--frame-ms <MS>` | `46` | Pitch analysis frame size. |
| `--hop-ms <MS>` | `10` | Pitch analysis hop size. |
| `--min-confidence <0..1>` | `0.68` | Minimum pitch confidence before a frame is corrected. |
| `--transient-protection <0..1>` | `0.55` | Protects attacks from pitch-shift artifacts. |
| `--consonant-protection <0..1>` | `0.55` | Protects noisy consonants and breaths from pitch-shift artifacts. |
| `--min-voiced-ratio <0..1>` | `0.35` | Emits a warning if too few frames are tunable voiced vocal. |
| `--output-ceiling <0.1..1>` | `0.98` | Soft peak ceiling after processing. |
| `--no-formant-preserve` | off | Disables spectral-tilt restoration after pitch shifting. |
| `--fail-on-warnings` | off | Returns a non-zero exit after writing output/report if quality warnings occur. |
| `--quiet` | off | Suppress the render summary. |

Live-only options:

| Option | Default | Description |
| --- | ---: | --- |
| `--input-device <NAME|default>` | `default` | Microphone device for live mode. |
| `--output-device <NAME|default>` | `default` | Monitor output device for live mode. |
| `--sample-rate <HZ>` | `48000` | Live stream sample rate. |
| `--channels <1|2>` | `1` | Device channel count; tuning is mono internally. |
| `--buffer-size <FRAMES>` | device default | Optional fixed CPAL buffer size. |
| `--monitor <dry|tuned|both|muted>` | `tuned` | Signal routed to the output device. |
| `--record-dry <FILE>` | off | Write raw microphone input to a float32 WAV at shutdown. |
| `--record-wet <FILE>` | off | Write tuned output to a float32 WAV at shutdown. |

## Preset Starting Points

Natural lead vocal:

```bash
vocal-tuner -i vocal.wav -o vocal-tuned.wav --key A --scale minor \
  --preset natural
```

Modern pop:

```bash
vocal-tuner -i vocal.wav -o vocal-pop.wav --key E --scale major \
  --preset pop
```

Hard-tune effect:

```bash
vocal-tuner -i vocal.wav -o vocal-hard.wav --key C# --scale minor \
  --preset hard
```

## Quality Notes

Use clean monophonic acapella input for best results. The tool is intended for vocal lines, not full mixes or dense harmonies. For professional release work, audition the output in context, tune aggressive consonant artifacts with `--mix`, `--humanize`, and `--retune-speed`, and keep a dry copy for comping.

For automated pipelines, use `--report` with `--fail-on-warnings`. The report includes voiced/protected/low-confidence frame counts, correction range, peak/RMS, clipped-sample count, and warning strings. A warning is not always a bad render, but it is a signal that the input or settings need review before release.

## Tests

```bash
cd tools/vocal-tuner
./verify.sh
```

See [PRODUCTION.md](PRODUCTION.md) for the release gate, runtime gate, input contract, and report fields to review before publishing a tuned vocal.
