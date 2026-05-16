# Live Vocal Tuner Design

## Goal

Add a terminal-first live mode to `tools/vocal-tuner` so a user can select a microphone, hear pitch-corrected vocals in real time, and optionally record the dry mic signal, the tuned signal, or both.

## Current State

`tools/vocal-tuner` is a Rust CLI that renders an input vocal file to an output file. The existing path reads audio from disk, runs the key-aware pitch correction DSP, writes the tuned file, and can emit a JSON report. The current DSP is deterministic and offline-oriented: it analyzes overlapping frames across a complete `AudioBuffer`.

## User Experience

The current file-render command remains supported. Live use adds two terminal workflows:

```bash
vocal-tuner devices
```

This lists available input and output devices with default markers.

```bash
vocal-tuner live --input-device default --output-device default \
  --key A --scale minor --preset hard --monitor tuned \
  --record-dry voice.wav --record-wet voice-tuned.wav
```

This starts mic input, applies the tuner continuously, sends the selected monitor signal to the output device, and writes optional recordings until the user presses Ctrl-C.

## CLI Shape

The CLI will support subcommands:

- `render`: explicit offline file render mode.
- `live`: real-time microphone mode.
- `devices`: list input/output audio devices.

For compatibility, calling `vocal-tuner --input in.wav --output out.wav ...` will continue to behave like `render`.

Live mode options:

- `--input-device <NAME|default>` selects the microphone.
- `--output-device <NAME|default>` selects the monitor output.
- `--sample-rate <HZ>` defaults to `48000`.
- `--channels <1|2>` defaults to `1`; live tuning is mono internally.
- `--buffer-size <FRAMES>` defaults to the device default, with optional manual override.
- `--monitor <dry|tuned|both|muted>` defaults to `tuned`.
- `--record-dry <FILE>` writes raw microphone input.
- `--record-wet <FILE>` writes tuned output.
- Existing tuning options are reused: `--key`, `--scale`, `--preset`, `--retune-speed`, `--amount`, `--mix`, `--humanize`, `--preserve-vibrato`, `--concert-a`, `--min-f0`, `--max-f0`, `--frame-ms`, `--hop-ms`, `--min-confidence`, `--transient-protection`, `--consonant-protection`, `--output-ceiling`, and `--no-formant-preserve`.

## Architecture

Use `cpal` for cross-platform audio device I/O. Keep the current WAV writer for recording so live mode does not add a second file-writing path.

New and modified files:

- `tools/vocal-tuner/Cargo.toml`: add `cpal` and `ctrlc`.
- `tools/vocal-tuner/src/cli.rs`: parse subcommands while preserving legacy render flags.
- `tools/vocal-tuner/src/devices.rs`: list and select input/output devices.
- `tools/vocal-tuner/src/live.rs`: own input stream, output stream, shared buffers, shutdown, and session diagnostics.
- `tools/vocal-tuner/src/recorder.rs`: collect dry/wet samples and write WAV files at shutdown.
- `tools/vocal-tuner/src/dsp.rs`: expose a streaming processor that can tune successive blocks using rolling analysis state.
- `tools/vocal-tuner/src/lib.rs`: export new modules.
- `tools/vocal-tuner/README.md`: document live usage, recording modes, and latency expectations.

## DSP Design

The live processor will use the same `TunerConfig` and pitch-correction behavior as offline rendering. It will keep a rolling mono buffer, accept input blocks from the audio callback, run analysis on available windows, and emit tuned blocks. The first implementation targets practical monitoring rather than plugin-grade zero latency. Expected latency is roughly the analysis frame plus device buffering, usually 20-60 ms with default settings.

The live path should avoid allocations in audio callbacks. Callbacks push and pop fixed-size blocks through preallocated ring buffers protected by short locks. Heavier tuning work happens outside the device callbacks where possible. If a buffer underruns, output silence for the missing frames and increment a dropout counter.

## Recording

Recording is optional and independent of monitoring. A user may monitor tuned audio while recording only dry voice, record tuned voice while monitoring muted, or record both dry and wet streams. Recordings are written as WAV files through the existing `write_wav` support at session end.

If recording cannot be created or written, live mode should fail before opening audio streams when possible. If shutdown write fails, return a non-zero error and print which recording failed.

## Error Handling

Device selection errors should list the attempted name and suggest `vocal-tuner devices`.

Unsupported device formats should report the requested sample rate/channels and the formats the device exposes.

Audio stream failures should stop the session, close any recordings cleanly, and return an error. Dropouts should be reported at the end but should not fail the command unless stream creation itself failed.

## Testing

Unit tests will cover CLI parsing, device selection logic with fake descriptors, recorder dry/wet output construction, monitor mixing, and streaming DSP block length/stability. Integration verification will run the existing `./verify.sh`. Real microphone testing remains manual because CI cannot rely on audio hardware.

Manual verification command:

```bash
cd tools/vocal-tuner
cargo run -- devices
cargo run -- live --input-device default --output-device default --key A --scale minor --preset pop --monitor tuned --record-dry /tmp/dry.wav --record-wet /tmp/wet.wav
```

Expected result: tuned monitoring is audible while the command runs, Ctrl-C exits cleanly, and both recordings exist with non-zero duration.

