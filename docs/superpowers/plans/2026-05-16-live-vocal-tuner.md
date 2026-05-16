# Live Vocal Tuner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add terminal-first live microphone pitch correction to `tools/vocal-tuner`, with selectable devices, live monitoring, dry recording, and tuned recording.

**Architecture:** Preserve the current offline render path and add explicit `render`, `devices`, and `live` modes. Use `cpal` for live device I/O, reuse existing `TunerConfig` and WAV writing, and add a streaming tuner wrapper around the current DSP behavior.

**Tech Stack:** Rust 2021, existing `vocal-tuner` crate, `cpal` for audio I/O, `ctrlc` for terminal shutdown, existing WAV reader/writer, Cargo tests/clippy/fmt.

---

## File Structure

- Modify `tools/vocal-tuner/Cargo.toml`: add `cpal` and `ctrlc` dependencies.
- Modify `tools/vocal-tuner/src/lib.rs`: export `devices`, `live`, and `recorder`.
- Modify `tools/vocal-tuner/src/cli.rs`: introduce subcommand parsing, shared tuning option parsing, `devices` dispatch, and `live` dispatch while keeping legacy render flags working.
- Modify `tools/vocal-tuner/src/dsp.rs`: add a streaming processor API that accepts mono blocks and returns tuned mono blocks.
- Create `tools/vocal-tuner/src/devices.rs`: audio device listing and selection helpers.
- Create `tools/vocal-tuner/src/recorder.rs`: optional dry/wet recording buffers and WAV finalization.
- Create `tools/vocal-tuner/src/live.rs`: live session configuration, CPAL stream setup, monitor routing, recorder integration, and shutdown.
- Modify `tools/vocal-tuner/README.md`: document `devices` and `live` workflows.

---

### Task 1: Add CLI Mode Parsing Without Changing Render Behavior

**Files:**
- Modify: `tools/vocal-tuner/src/cli.rs`

- [ ] **Step 1: Write failing CLI tests**

Add these tests inside the existing `#[cfg(test)] mod tests` in `tools/vocal-tuner/src/cli.rs`:

```rust
#[test]
fn parses_explicit_render_subcommand() {
    let command = Command::parse(vec![
        "render".into(),
        "--input".into(),
        "in.wav".into(),
        "--output".into(),
        "out.wav".into(),
        "--key".into(),
        "Bb".into(),
        "--scale".into(),
        "minor".into(),
    ])
    .unwrap();

    match command {
        Command::Render(args) => {
            assert_eq!(args.input, PathBuf::from("in.wav"));
            assert_eq!(args.output, PathBuf::from("out.wav"));
            assert_eq!(args.config.key.root.to_string(), "Bb");
            assert_eq!(args.config.key.scale.to_string(), "minor");
        }
        other => panic!("expected render command, got {other:?}"),
    }
}

#[test]
fn parses_legacy_render_without_subcommand() {
    let command = Command::parse(vec![
        "--input".into(),
        "in.wav".into(),
        "--output".into(),
        "out.wav".into(),
    ])
    .unwrap();

    match command {
        Command::Render(args) => {
            assert_eq!(args.input, PathBuf::from("in.wav"));
            assert_eq!(args.output, PathBuf::from("out.wav"));
        }
        other => panic!("expected render command, got {other:?}"),
    }
}

#[test]
fn parses_devices_subcommand() {
    let command = Command::parse(vec!["devices".into()]).unwrap();
    assert!(matches!(command, Command::Devices));
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd tools/vocal-tuner
cargo test cli::tests::parses_explicit_render_subcommand cli::tests::parses_legacy_render_without_subcommand cli::tests::parses_devices_subcommand
```

Expected: FAIL because `Command` does not exist yet.

- [ ] **Step 3: Implement command enum and parser**

In `tools/vocal-tuner/src/cli.rs`, rename the current `Args` to `RenderArgs`, then add:

```rust
#[derive(Debug)]
enum Command {
    Render(RenderArgs),
    Devices,
    Live(LiveArgs),
    Help,
}

impl Command {
    fn parse(raw: Vec<String>) -> Result<Self, String> {
        if raw.iter().any(|arg| arg == "--help" || arg == "-h") {
            return Ok(Self::Help);
        }

        let mut args = raw;
        match args.first().map(String::as_str) {
            Some("render") => {
                args.remove(0);
                Ok(Self::Render(RenderArgs::parse(args)?))
            }
            Some("devices") => Ok(Self::Devices),
            Some("live") => {
                args.remove(0);
                Ok(Self::Live(LiveArgs::parse(args)?))
            }
            _ => Ok(Self::Render(RenderArgs::parse(args)?)),
        }
    }
}

#[derive(Debug)]
struct LiveArgs {
    input_device: String,
    output_device: String,
    config: TunerConfig,
}

impl LiveArgs {
    fn parse(raw: Vec<String>) -> Result<Self, String> {
        let mut input_device = "default".to_string();
        let mut output_device = "default".to_string();
        let mut tuning_args = Vec::new();
        let mut index = 0;

        while index < raw.len() {
            match raw[index].as_str() {
                "--input-device" => {
                    index += 1;
                    input_device = value(&raw, index, "--input-device")?.to_string();
                }
                "--output-device" => {
                    index += 1;
                    output_device = value(&raw, index, "--output-device")?.to_string();
                }
                other => {
                    tuning_args.push(other.to_string());
                    if option_takes_value(other) {
                        index += 1;
                        tuning_args.push(value(&raw, index, other)?.to_string());
                    }
                }
            }
            index += 1;
        }

        let config = parse_tuning_config(tuning_args)?;
        Ok(Self {
            input_device,
            output_device,
            config,
        })
    }
}
```

Extract the current tuning option parsing from `RenderArgs::parse` into `parse_tuning_config(raw: Vec<String>) -> Result<TunerConfig, String>`. Keep `--input`, `--output`, `--report`, `--quiet`, and `--fail-on-warnings` in `RenderArgs::parse`.

Add:

```rust
fn option_takes_value(option: &str) -> bool {
    matches!(
        option,
        "--key"
            | "--scale"
            | "--preset"
            | "--concert-a"
            | "--retune-speed"
            | "--amount"
            | "--mix"
            | "--humanize"
            | "--preserve-vibrato"
            | "--min-f0"
            | "--max-f0"
            | "--frame-ms"
            | "--hop-ms"
            | "--min-confidence"
            | "--transient-protection"
            | "--consonant-protection"
            | "--min-voiced-ratio"
            | "--output-ceiling"
    )
}
```

Update `run_with_args`:

```rust
pub fn run_with_args(raw: Vec<String>) -> Result<(), String> {
    match Command::parse(raw)? {
        Command::Help => {
            print_help();
            Ok(())
        }
        Command::Render(args) => run_render(args),
        Command::Devices => crate::devices::print_devices().map_err(|err| err.to_string()),
        Command::Live(args) => crate::live::run_live(args.into()).map_err(|err| err.to_string()),
    }
}
```

Move the current render body into:

```rust
fn run_render(args: RenderArgs) -> Result<(), String> {
    let audio = read_audio(&args.input).map_err(|err| format!("failed to read input: {err}"))?;
    let (tuned, report) = tune(&audio, &args.config);
    write_audio(&args.output, &tuned).map_err(|err| format!("failed to write output: {err}"))?;
    // keep existing report, fail-on-warning, and summary behavior unchanged
    Ok(())
}
```

- [ ] **Step 4: Run tests to verify pass**

Run:

```bash
cd tools/vocal-tuner
cargo test cli::tests::parses_explicit_render_subcommand cli::tests::parses_legacy_render_without_subcommand cli::tests::parses_devices_subcommand
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/vocal-tuner/src/cli.rs
git commit -m "feat: add vocal tuner command modes"
```

---

### Task 2: Add Device Listing And Selection

**Files:**
- Modify: `tools/vocal-tuner/Cargo.toml`
- Modify: `tools/vocal-tuner/src/lib.rs`
- Create: `tools/vocal-tuner/src/devices.rs`

- [ ] **Step 1: Write device helper tests**

Create `tools/vocal-tuner/src/devices.rs` with these tests first:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn selects_default_marker() {
        let devices = vec![
            DeviceInfo::new("Built-in Mic", DeviceKind::Input, false),
            DeviceInfo::new("USB Mic", DeviceKind::Input, true),
        ];

        let selected = select_device_name(&devices, DeviceKind::Input, "default").unwrap();
        assert_eq!(selected, "USB Mic");
    }

    #[test]
    fn selects_exact_name() {
        let devices = vec![
            DeviceInfo::new("Built-in Mic", DeviceKind::Input, true),
            DeviceInfo::new("Scarlett Solo USB", DeviceKind::Input, false),
        ];

        let selected = select_device_name(&devices, DeviceKind::Input, "Scarlett Solo USB").unwrap();
        assert_eq!(selected, "Scarlett Solo USB");
    }

    #[test]
    fn rejects_missing_name_with_devices_hint() {
        let devices = vec![DeviceInfo::new("Built-in Mic", DeviceKind::Input, true)];

        let err = select_device_name(&devices, DeviceKind::Input, "Missing Mic").unwrap_err();
        assert!(err.contains("Missing Mic"));
        assert!(err.contains("vocal-tuner devices"));
    }
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd tools/vocal-tuner
cargo test devices::tests
```

Expected: FAIL because `DeviceInfo`, `DeviceKind`, and `select_device_name` do not exist.

- [ ] **Step 3: Implement device module**

Add to `tools/vocal-tuner/Cargo.toml`:

```toml
[dependencies]
cpal = "0.15"
```

Add to `tools/vocal-tuner/src/lib.rs`:

```rust
pub mod devices;
```

Implement `tools/vocal-tuner/src/devices.rs`:

```rust
use std::fmt;

use cpal::traits::{DeviceTrait, HostTrait};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceKind {
    Input,
    Output,
}

impl fmt::Display for DeviceKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DeviceKind::Input => f.write_str("input"),
            DeviceKind::Output => f.write_str("output"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct DeviceInfo {
    pub name: String,
    pub kind: DeviceKind,
    pub is_default: bool,
}

impl DeviceInfo {
    pub fn new(name: impl Into<String>, kind: DeviceKind, is_default: bool) -> Self {
        Self {
            name: name.into(),
            kind,
            is_default,
        }
    }
}

#[derive(Debug)]
pub struct DeviceError(pub String);

impl fmt::Display for DeviceError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}

impl std::error::Error for DeviceError {}

pub fn print_devices() -> Result<(), DeviceError> {
    let devices = list_devices()?;
    println!("Input devices:");
    for device in devices.iter().filter(|device| device.kind == DeviceKind::Input) {
        let marker = if device.is_default { " (default)" } else { "" };
        println!("  {}{}", device.name, marker);
    }
    println!("Output devices:");
    for device in devices.iter().filter(|device| device.kind == DeviceKind::Output) {
        let marker = if device.is_default { " (default)" } else { "" };
        println!("  {}{}", device.name, marker);
    }
    Ok(())
}

pub fn list_devices() -> Result<Vec<DeviceInfo>, DeviceError> {
    let host = cpal::default_host();
    let default_input = host.default_input_device().and_then(|device| device.name().ok());
    let default_output = host.default_output_device().and_then(|device| device.name().ok());
    let mut devices = Vec::new();

    let inputs = host
        .input_devices()
        .map_err(|err| DeviceError(format!("failed to list input devices: {err}")))?;
    for device in inputs {
        let name = device.name().unwrap_or_else(|_| "<unknown input>".to_string());
        devices.push(DeviceInfo::new(
            name.clone(),
            DeviceKind::Input,
            default_input.as_deref() == Some(name.as_str()),
        ));
    }

    let outputs = host
        .output_devices()
        .map_err(|err| DeviceError(format!("failed to list output devices: {err}")))?;
    for device in outputs {
        let name = device.name().unwrap_or_else(|_| "<unknown output>".to_string());
        devices.push(DeviceInfo::new(
            name.clone(),
            DeviceKind::Output,
            default_output.as_deref() == Some(name.as_str()),
        ));
    }

    Ok(devices)
}

pub fn select_device_name(
    devices: &[DeviceInfo],
    kind: DeviceKind,
    requested: &str,
) -> Result<String, DeviceError> {
    if requested == "default" {
        return devices
            .iter()
            .find(|device| device.kind == kind && device.is_default)
            .map(|device| device.name.clone())
            .ok_or_else(|| DeviceError(format!("no default {kind} device found; run vocal-tuner devices")));
    }

    devices
        .iter()
        .find(|device| device.kind == kind && device.name == requested)
        .map(|device| device.name.clone())
        .ok_or_else(|| {
            DeviceError(format!(
                "{kind} device '{requested}' was not found; run vocal-tuner devices"
            ))
        })
}
```

- [ ] **Step 4: Run tests**

Run:

```bash
cd tools/vocal-tuner
cargo test devices::tests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/vocal-tuner/Cargo.toml tools/vocal-tuner/src/lib.rs tools/vocal-tuner/src/devices.rs
git commit -m "feat: list vocal tuner audio devices"
```

---

### Task 3: Add Recording Buffer For Dry And Wet WAV Output

**Files:**
- Modify: `tools/vocal-tuner/src/lib.rs`
- Create: `tools/vocal-tuner/src/recorder.rs`

- [ ] **Step 1: Write recorder tests**

Create `tools/vocal-tuner/src/recorder.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn records_dry_and_wet_samples_independently() {
        let mut recorder = LiveRecorder::new(
            48_000,
            Some("dry.wav".into()),
            Some("wet.wav".into()),
        );

        recorder.push_dry(&[0.1, 0.2]);
        recorder.push_wet(&[0.3, 0.4, 0.5]);

        assert_eq!(recorder.dry_sample_count(), 2);
        assert_eq!(recorder.wet_sample_count(), 3);
    }

    #[test]
    fn disabled_recorders_ignore_samples() {
        let mut recorder = LiveRecorder::new(48_000, None, None);

        recorder.push_dry(&[0.1, 0.2]);
        recorder.push_wet(&[0.3, 0.4]);

        assert_eq!(recorder.dry_sample_count(), 0);
        assert_eq!(recorder.wet_sample_count(), 0);
    }
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd tools/vocal-tuner
cargo test recorder::tests
```

Expected: FAIL because `LiveRecorder` is not implemented.

- [ ] **Step 3: Implement recorder**

Add to `tools/vocal-tuner/src/lib.rs`:

```rust
pub mod recorder;
```

Replace `tools/vocal-tuner/src/recorder.rs` with:

```rust
use std::path::PathBuf;

use crate::audio::AudioBuffer;
use crate::wav::write_wav;

#[derive(Debug)]
pub struct LiveRecorder {
    sample_rate: u32,
    dry_path: Option<PathBuf>,
    wet_path: Option<PathBuf>,
    dry_samples: Vec<f32>,
    wet_samples: Vec<f32>,
}

impl LiveRecorder {
    pub fn new(sample_rate: u32, dry_path: Option<PathBuf>, wet_path: Option<PathBuf>) -> Self {
        Self {
            sample_rate,
            dry_path,
            wet_path,
            dry_samples: Vec::new(),
            wet_samples: Vec::new(),
        }
    }

    pub fn push_dry(&mut self, samples: &[f32]) {
        if self.dry_path.is_some() {
            self.dry_samples.extend_from_slice(samples);
        }
    }

    pub fn push_wet(&mut self, samples: &[f32]) {
        if self.wet_path.is_some() {
            self.wet_samples.extend_from_slice(samples);
        }
    }

    pub fn dry_sample_count(&self) -> usize {
        self.dry_samples.len()
    }

    pub fn wet_sample_count(&self) -> usize {
        self.wet_samples.len()
    }

    pub fn finalize(self) -> Result<(), String> {
        if let Some(path) = self.dry_path {
            write_wav(
                &path,
                &AudioBuffer {
                    sample_rate: self.sample_rate,
                    channels: 1,
                    samples: self.dry_samples,
                },
            )
            .map_err(|err| format!("failed to write dry recording {}: {err}", path.display()))?;
        }

        if let Some(path) = self.wet_path {
            write_wav(
                &path,
                &AudioBuffer {
                    sample_rate: self.sample_rate,
                    channels: 1,
                    samples: self.wet_samples,
                },
            )
            .map_err(|err| format!("failed to write wet recording {}: {err}", path.display()))?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn records_dry_and_wet_samples_independently() {
        let mut recorder = LiveRecorder::new(48_000, Some("dry.wav".into()), Some("wet.wav".into()));
        recorder.push_dry(&[0.1, 0.2]);
        recorder.push_wet(&[0.3, 0.4, 0.5]);
        assert_eq!(recorder.dry_sample_count(), 2);
        assert_eq!(recorder.wet_sample_count(), 3);
    }

    #[test]
    fn disabled_recorders_ignore_samples() {
        let mut recorder = LiveRecorder::new(48_000, None, None);
        recorder.push_dry(&[0.1, 0.2]);
        recorder.push_wet(&[0.3, 0.4]);
        assert_eq!(recorder.dry_sample_count(), 0);
        assert_eq!(recorder.wet_sample_count(), 0);
    }
}
```

- [ ] **Step 4: Run tests**

Run:

```bash
cd tools/vocal-tuner
cargo test recorder::tests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/vocal-tuner/src/lib.rs tools/vocal-tuner/src/recorder.rs
git commit -m "feat: add vocal tuner live recorder"
```

---

### Task 4: Add Streaming Tuner API

**Files:**
- Modify: `tools/vocal-tuner/src/dsp.rs`

- [ ] **Step 1: Write streaming DSP tests**

Add to `tools/vocal-tuner/src/dsp.rs` tests:

```rust
#[test]
fn streaming_tuner_returns_same_block_length() {
    let sample_rate = 48_000;
    let mut tuner = StreamingTuner::new(sample_rate, TunerConfig::default());
    let block = vec![0.0_f32; 512];

    let output = tuner.process_block(&block);

    assert_eq!(output.len(), block.len());
}

#[test]
fn streaming_tuner_processes_voiced_signal_without_nan() {
    let sample_rate = 48_000;
    let mut tuner = StreamingTuner::new(
        sample_rate,
        TunerConfig {
            key: Key::parse("A", "minor").unwrap(),
            retune_speed: 1.0,
            humanize: 0.0,
            preserve_vibrato: 0.0,
            ..TunerConfig::default()
        },
    );
    let block: Vec<f32> = (0..2048)
        .map(|i| {
            (2.0 * std::f32::consts::PI * 230.0 * i as f32 / sample_rate as f32).sin() * 0.25
        })
        .collect();

    let output = tuner.process_block(&block);

    assert_eq!(output.len(), block.len());
    assert!(output.iter().all(|sample| sample.is_finite()));
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd tools/vocal-tuner
cargo test dsp::tests::streaming_tuner_returns_same_block_length dsp::tests::streaming_tuner_processes_voiced_signal_without_nan
```

Expected: FAIL because `StreamingTuner` does not exist.

- [ ] **Step 3: Implement minimal streaming wrapper**

Add this public struct near `TuningReport` in `tools/vocal-tuner/src/dsp.rs`:

```rust
#[derive(Debug, Clone)]
pub struct StreamingTuner {
    sample_rate: u32,
    config: TunerConfig,
    history: Vec<f32>,
    max_history: usize,
}

impl StreamingTuner {
    pub fn new(sample_rate: u32, config: TunerConfig) -> Self {
        let max_history = ((sample_rate as f32 * config.frame_ms / 1000.0).round() as usize)
            .max(512)
            * 4;
        Self {
            sample_rate,
            config,
            history: Vec::with_capacity(max_history),
            max_history,
        }
    }

    pub fn process_block(&mut self, input: &[f32]) -> Vec<f32> {
        self.history.extend_from_slice(input);
        if self.history.len() > self.max_history {
            let remove_count = self.history.len() - self.max_history;
            self.history.drain(0..remove_count);
        }

        let audio = AudioBuffer {
            sample_rate: self.sample_rate,
            channels: 1,
            samples: self.history.clone(),
        };
        let (tuned, _) = tune(&audio, &self.config);
        let start = tuned.samples.len().saturating_sub(input.len());
        let mut output = tuned.samples[start..].to_vec();
        output.resize(input.len(), 0.0);
        output
    }
}
```

This first version reuses the proven offline path for correctness. A later optimization can replace the cloned history render with true incremental frame processing after live mode is functional.

- [ ] **Step 4: Run streaming tests**

Run:

```bash
cd tools/vocal-tuner
cargo test dsp::tests::streaming_tuner_returns_same_block_length dsp::tests::streaming_tuner_processes_voiced_signal_without_nan
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/vocal-tuner/src/dsp.rs
git commit -m "feat: add streaming vocal tuner processor"
```

---

### Task 5: Add Live Mode Configuration And Monitor Mixing

**Files:**
- Modify: `tools/vocal-tuner/src/lib.rs`
- Modify: `tools/vocal-tuner/src/cli.rs`
- Create: `tools/vocal-tuner/src/live.rs`

- [ ] **Step 1: Write live config tests**

Create `tools/vocal-tuner/src/live.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn monitor_tuned_returns_wet_signal() {
        let dry = [0.1, 0.2];
        let wet = [0.3, 0.4];
        assert_eq!(mix_monitor(MonitorMode::Tuned, &dry, &wet), vec![0.3, 0.4]);
    }

    #[test]
    fn monitor_both_averages_dry_and_wet() {
        let dry = [0.2, 0.4];
        let wet = [0.6, 0.8];
        assert_eq!(mix_monitor(MonitorMode::Both, &dry, &wet), vec![0.4, 0.6]);
    }

    #[test]
    fn monitor_muted_returns_silence() {
        let dry = [0.2, 0.4];
        let wet = [0.6, 0.8];
        assert_eq!(mix_monitor(MonitorMode::Muted, &dry, &wet), vec![0.0, 0.0]);
    }
}
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
cd tools/vocal-tuner
cargo test live::tests
```

Expected: FAIL because `MonitorMode` and `mix_monitor` are missing.

- [ ] **Step 3: Implement live data types and monitor mixing**

Add to `tools/vocal-tuner/src/lib.rs`:

```rust
pub mod live;
```

Implement in `tools/vocal-tuner/src/live.rs`:

```rust
use std::path::PathBuf;

use crate::dsp::TunerConfig;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MonitorMode {
    Dry,
    Tuned,
    Both,
    Muted,
}

impl MonitorMode {
    pub fn parse(value: &str) -> Result<Self, String> {
        match value {
            "dry" => Ok(Self::Dry),
            "tuned" => Ok(Self::Tuned),
            "both" => Ok(Self::Both),
            "muted" => Ok(Self::Muted),
            other => Err(format!("unknown monitor mode '{other}'; expected dry, tuned, both, or muted")),
        }
    }
}

#[derive(Debug, Clone)]
pub struct LiveConfig {
    pub input_device: String,
    pub output_device: String,
    pub sample_rate: u32,
    pub channels: u16,
    pub buffer_size: Option<u32>,
    pub monitor: MonitorMode,
    pub record_dry: Option<PathBuf>,
    pub record_wet: Option<PathBuf>,
    pub tuner: TunerConfig,
}

pub fn mix_monitor(mode: MonitorMode, dry: &[f32], wet: &[f32]) -> Vec<f32> {
    let len = dry.len().min(wet.len());
    match mode {
        MonitorMode::Dry => dry[..len].to_vec(),
        MonitorMode::Tuned => wet[..len].to_vec(),
        MonitorMode::Both => dry[..len]
            .iter()
            .zip(&wet[..len])
            .map(|(dry, wet)| (dry + wet) * 0.5)
            .collect(),
        MonitorMode::Muted => vec![0.0; len],
    }
}

pub fn run_live(_config: LiveConfig) -> Result<(), String> {
    Err("live audio streaming is not implemented yet".to_string())
}
```

Update `LiveArgs` in `cli.rs` to include:

```rust
sample_rate: u32,
channels: u16,
buffer_size: Option<u32>,
monitor: crate::live::MonitorMode,
record_dry: Option<PathBuf>,
record_wet: Option<PathBuf>,
```

Parse live-only flags:

```rust
"--sample-rate" => {
    index += 1;
    sample_rate = value(&raw, index, "--sample-rate")?
        .parse::<u32>()
        .map_err(|_| "--sample-rate must be an integer".to_string())?;
}
"--channels" => {
    index += 1;
    channels = value(&raw, index, "--channels")?
        .parse::<u16>()
        .map_err(|_| "--channels must be an integer".to_string())?;
}
"--buffer-size" => {
    index += 1;
    buffer_size = Some(
        value(&raw, index, "--buffer-size")?
            .parse::<u32>()
            .map_err(|_| "--buffer-size must be an integer".to_string())?,
    );
}
"--monitor" => {
    index += 1;
    monitor = crate::live::MonitorMode::parse(value(&raw, index, "--monitor")?)?;
}
"--record-dry" => {
    index += 1;
    record_dry = Some(PathBuf::from(value(&raw, index, "--record-dry")?));
}
"--record-wet" => {
    index += 1;
    record_wet = Some(PathBuf::from(value(&raw, index, "--record-wet")?));
}
```

Implement:

```rust
impl From<LiveArgs> for crate::live::LiveConfig {
    fn from(value: LiveArgs) -> Self {
        Self {
            input_device: value.input_device,
            output_device: value.output_device,
            sample_rate: value.sample_rate,
            channels: value.channels,
            buffer_size: value.buffer_size,
            monitor: value.monitor,
            record_dry: value.record_dry,
            record_wet: value.record_wet,
            tuner: value.config,
        }
    }
}
```

- [ ] **Step 4: Run tests**

Run:

```bash
cd tools/vocal-tuner
cargo test live::tests cli::tests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/vocal-tuner/src/lib.rs tools/vocal-tuner/src/cli.rs tools/vocal-tuner/src/live.rs
git commit -m "feat: parse vocal tuner live mode"
```

---

### Task 6: Implement Live Microphone Monitoring

**Files:**
- Modify: `tools/vocal-tuner/src/live.rs`

- [ ] **Step 1: Add `ctrlc` dependency**

Modify `tools/vocal-tuner/Cargo.toml`:

```toml
[dependencies]
cpal = "0.15"
ctrlc = "3"
```

- [ ] **Step 2: Implement live streaming**

Replace `run_live` in `tools/vocal-tuner/src/live.rs` with CPAL stream setup:

```rust
pub fn run_live(config: LiveConfig) -> Result<(), String> {
    use std::collections::VecDeque;
    use std::sync::{
        atomic::{AtomicBool, AtomicUsize, Ordering},
        Arc, Mutex,
    };
    use std::thread;
    use std::time::Duration;

    use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};

    let host = cpal::default_host();
    let input_device = select_cpal_device(&host, true, &config.input_device)?;
    let output_device = select_cpal_device(&host, false, &config.output_device)?;

    let stream_config = cpal::StreamConfig {
        channels: config.channels,
        sample_rate: cpal::SampleRate(config.sample_rate),
        buffer_size: config
            .buffer_size
            .map(cpal::BufferSize::Fixed)
            .unwrap_or(cpal::BufferSize::Default),
    };

    let input_queue = Arc::new(Mutex::new(VecDeque::<f32>::with_capacity(config.sample_rate as usize)));
    let output_queue = Arc::new(Mutex::new(VecDeque::<f32>::with_capacity(config.sample_rate as usize)));
    let recorder = Arc::new(Mutex::new(crate::recorder::LiveRecorder::new(
        config.sample_rate,
        config.record_dry.clone(),
        config.record_wet.clone(),
    )));
    let running = Arc::new(AtomicBool::new(true));
    let dropouts = Arc::new(AtomicUsize::new(0));

    let input_queue_for_callback = Arc::clone(&input_queue);
    let recorder_for_input = Arc::clone(&recorder);
    let input_channels = stream_config.channels as usize;
    let input_stream = input_device
        .build_input_stream(
            &stream_config,
            move |data: &[f32], _| {
                let mono = downmix_to_mono(data, input_channels);
                if let Ok(mut recorder) = recorder_for_input.lock() {
                    recorder.push_dry(&mono);
                }
                if let Ok(mut queue) = input_queue_for_callback.lock() {
                    queue.extend(mono);
                    while queue.len() > 48_000 {
                        queue.pop_front();
                    }
                }
            },
            move |err| eprintln!("input stream error: {err}"),
            None,
        )
        .map_err(|err| format!("failed to build input stream: {err}"))?;

    let output_queue_for_callback = Arc::clone(&output_queue);
    let dropouts_for_callback = Arc::clone(&dropouts);
    let output_channels = stream_config.channels as usize;
    let output_stream = output_device
        .build_output_stream(
            &stream_config,
            move |data: &mut [f32], _| {
                let frames = data.len() / output_channels;
                let mut mono = vec![0.0_f32; frames];
                if let Ok(mut queue) = output_queue_for_callback.lock() {
                    for sample in &mut mono {
                        if let Some(value) = queue.pop_front() {
                            *sample = value;
                        } else {
                            dropouts_for_callback.fetch_add(1, Ordering::Relaxed);
                            *sample = 0.0;
                        }
                    }
                }
                write_mono_to_output(&mono, data, output_channels);
            },
            move |err| eprintln!("output stream error: {err}"),
            None,
        )
        .map_err(|err| format!("failed to build output stream: {err}"))?;

    let running_for_ctrlc = Arc::clone(&running);
    ctrlc::set_handler(move || {
        running_for_ctrlc.store(false, Ordering::SeqCst);
    })
    .map_err(|err| format!("failed to install Ctrl-C handler: {err}"))?;

    let mut tuner = crate::dsp::StreamingTuner::new(config.sample_rate, config.tuner.clone());
    input_stream.play().map_err(|err| format!("failed to start input stream: {err}"))?;
    output_stream.play().map_err(|err| format!("failed to start output stream: {err}"))?;
    eprintln!("live vocal tuner running; press Ctrl-C to stop");

    while running.load(Ordering::SeqCst) {
        let block = pop_block(&input_queue, 512);
        if block.is_empty() {
            thread::sleep(Duration::from_millis(2));
            continue;
        }

        let wet = tuner.process_block(&block);
        if let Ok(mut recorder) = recorder.lock() {
            recorder.push_wet(&wet);
        }
        let monitor = mix_monitor(config.monitor, &block, &wet);
        if let Ok(mut queue) = output_queue.lock() {
            queue.extend(monitor);
            while queue.len() > config.sample_rate as usize {
                queue.pop_front();
            }
        }
    }

    drop(input_stream);
    drop(output_stream);

    let recorder = Arc::try_unwrap(recorder)
        .map_err(|_| "failed to close recorder because it is still in use".to_string())?
        .into_inner()
        .map_err(|_| "failed to close recorder lock".to_string())?;
    recorder.finalize()?;

    eprintln!(
        "live session ended; output dropouts: {}",
        dropouts.load(Ordering::Relaxed)
    );
    Ok(())
}
```

Add helpers in the same file:

```rust
fn select_cpal_device(
    host: &cpal::Host,
    input: bool,
    requested: &str,
) -> Result<cpal::Device, String> {
    use cpal::traits::{DeviceTrait, HostTrait};

    if requested == "default" {
        return if input {
            host.default_input_device()
                .ok_or_else(|| "no default input device found; run vocal-tuner devices".to_string())
        } else {
            host.default_output_device()
                .ok_or_else(|| "no default output device found; run vocal-tuner devices".to_string())
        };
    }

    let devices = if input {
        host.input_devices()
            .map_err(|err| format!("failed to list input devices: {err}"))?
            .collect::<Vec<_>>()
    } else {
        host.output_devices()
            .map_err(|err| format!("failed to list output devices: {err}"))?
            .collect::<Vec<_>>()
    };

    for device in devices {
        let name = device.name().unwrap_or_default();
        if name == requested {
            return Ok(device);
        }
    }

    let kind = if input { "input" } else { "output" };
    Err(format!("{kind} device '{requested}' was not found; run vocal-tuner devices"))
}

fn downmix_to_mono(data: &[f32], channels: usize) -> Vec<f32> {
    data.chunks(channels)
        .map(|frame| frame.iter().copied().sum::<f32>() / channels as f32)
        .collect()
}

fn write_mono_to_output(mono: &[f32], output: &mut [f32], channels: usize) {
    for (frame, sample) in output.chunks_mut(channels).zip(mono.iter().copied()) {
        for channel in frame {
            *channel = sample;
        }
    }
}

fn pop_block(queue: &std::sync::Arc<std::sync::Mutex<std::collections::VecDeque<f32>>>, size: usize) -> Vec<f32> {
    let mut block = Vec::with_capacity(size);
    if let Ok(mut queue) = queue.lock() {
        while block.len() < size {
            if let Some(sample) = queue.pop_front() {
                block.push(sample);
            } else {
                break;
            }
        }
    }
    block
}
```

- [ ] **Step 3: Run compile and unit tests**

Run:

```bash
cd tools/vocal-tuner
cargo test
```

Expected: PASS. If CPAL reports an API mismatch, adjust signatures to the installed `cpal` version and rerun.

- [ ] **Step 4: Commit**

```bash
git add tools/vocal-tuner/Cargo.toml tools/vocal-tuner/src/live.rs
git commit -m "feat: stream live tuned microphone audio"
```

---

### Task 7: Document Live Usage

**Files:**
- Modify: `tools/vocal-tuner/README.md`

- [ ] **Step 1: Add README live section**

Add after the existing Usage section:

```markdown
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
```

- [ ] **Step 2: Run README command smoke test**

Run:

```bash
cd tools/vocal-tuner
cargo run -- --help >/tmp/vocal-tuner-help.txt
cargo run -- devices >/tmp/vocal-tuner-devices.txt
```

Expected: help command exits 0. Devices command exits 0 on machines with a supported audio host; if CI lacks an audio host, document the exact error in the verification notes.

- [ ] **Step 3: Commit**

```bash
git add tools/vocal-tuner/README.md
git commit -m "docs: document live vocal tuner mode"
```

---

### Task 8: Full Verification

**Files:**
- No code changes expected.

- [ ] **Step 1: Run existing verification**

Run:

```bash
cd tools/vocal-tuner
./verify.sh
```

Expected: `cargo fmt --check`, `cargo test`, `cargo clippy -- -D warnings`, and `cargo run -- --help >/dev/null` all pass.

- [ ] **Step 2: Run live manual smoke test**

Run:

```bash
cd tools/vocal-tuner
cargo run -- live \
  --input-device default \
  --output-device default \
  --key A \
  --scale minor \
  --preset pop \
  --monitor tuned \
  --record-dry /tmp/vocal-tuner-dry.wav \
  --record-wet /tmp/vocal-tuner-wet.wav
```

Speak or sing for 5-10 seconds, then press Ctrl-C.

Expected:

- Tuned monitoring is audible while running.
- The process exits cleanly after Ctrl-C.
- `/tmp/vocal-tuner-dry.wav` exists.
- `/tmp/vocal-tuner-wet.wav` exists.
- Both WAV files have non-zero duration.

- [ ] **Step 3: Inspect recordings**

Run:

```bash
ffprobe -hide_banner /tmp/vocal-tuner-dry.wav
ffprobe -hide_banner /tmp/vocal-tuner-wet.wav
```

Expected: both files report `Audio: pcm_f32le`, `48000 Hz`, and non-zero duration.

- [ ] **Step 4: Final commit if verification required fixes**

If verification required fixes:

```bash
git add tools/vocal-tuner
git commit -m "fix: stabilize live vocal tuner verification"
```

If no fixes were required, do not create an empty commit.

