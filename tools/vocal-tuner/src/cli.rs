use std::path::PathBuf;

use crate::dsp::{tune, TunerConfig};
use crate::music::Key;
use crate::wav::{read_audio, write_audio};

pub fn run() -> Result<(), String> {
    run_with_args(std::env::args().skip(1).collect())
}

pub fn run_with_args(raw: Vec<String>) -> Result<(), String> {
    match Command::parse(raw)? {
        Command::Help => {
            print_help();
            Ok(())
        }
        Command::Render(args) => run_render(args),
        Command::Devices => crate::devices::print_devices().map_err(|err| err.to_string()),
        Command::Live(args) => crate::live::run_live(args.into()),
    }
}

fn run_render(args: RenderArgs) -> Result<(), String> {
    let audio = read_audio(&args.input).map_err(|err| format!("failed to read input: {err}"))?;
    let (tuned, report) = tune(&audio, &args.config);
    write_audio(&args.output, &tuned).map_err(|err| format!("failed to write output: {err}"))?;
    if let Some(report_path) = &args.report {
        std::fs::write(report_path, render_report_json(&args, &tuned, &report))
            .map_err(|err| format!("failed to write report: {err}"))?;
    }
    if args.fail_on_warnings && !report.warnings.is_empty() {
        return Err(format!(
            "render completed with quality warnings: {}",
            report.warnings.join("; ")
        ));
    }

    if !args.quiet {
        eprintln!(
            "wrote {} ({:.1}s, {} Hz, {} channel(s)); voiced frames: {}/{}; protected: {}; low-confidence: {}; avg correction: {:.1} cents; max: {:.1} cents; peak: {:.3}; warnings: {}",
            args.output.display(),
            tuned.duration_seconds(),
            tuned.sample_rate,
            tuned.channels,
            report.voiced_frames,
            report.frames,
            report.protected_frames,
            report.low_confidence_frames,
            report.average_correction_cents,
            report.max_correction_cents,
            report.peak,
            report.warnings.len()
        );
    }

    Ok(())
}

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
struct RenderArgs {
    input: PathBuf,
    output: PathBuf,
    report: Option<PathBuf>,
    config: TunerConfig,
    quiet: bool,
    fail_on_warnings: bool,
}

impl RenderArgs {
    fn parse(raw: Vec<String>) -> Result<Self, String> {
        let mut input = None;
        let mut output = None;
        let mut report = None;
        let mut tuning_args = Vec::new();
        let mut quiet = false;
        let mut fail_on_warnings = false;
        let mut index = 0;

        while index < raw.len() {
            match raw[index].as_str() {
                "-i" | "--input" => {
                    index += 1;
                    input = Some(PathBuf::from(value(&raw, index, "--input")?));
                }
                "-o" | "--output" => {
                    index += 1;
                    output = Some(PathBuf::from(value(&raw, index, "--output")?));
                }
                "--report" => {
                    index += 1;
                    report = Some(PathBuf::from(value(&raw, index, "--report")?));
                }
                "--fail-on-warnings" => {
                    fail_on_warnings = true;
                }
                "--quiet" | "-q" => {
                    quiet = true;
                }
                other => {
                    tuning_args.push(other.to_string());
                    if option_takes_value(other) {
                        index += 1;
                        tuning_args.push(value(&raw, index, other)?.to_string());
                    } else if other != "--no-formant-preserve" {
                        return Err(format!("unknown argument '{other}'"));
                    }
                }
            }
            index += 1;
        }

        Ok(Self {
            input: input.ok_or("missing required --input")?,
            output: output.ok_or("missing required --output")?,
            report,
            config: parse_tuning_config(tuning_args)?,
            quiet,
            fail_on_warnings,
        })
    }
}

#[derive(Debug)]
struct LiveArgs {
    input_device: String,
    output_device: String,
    sample_rate: u32,
    channels: u16,
    buffer_size: Option<u32>,
    monitor: crate::live::MonitorMode,
    record_dry: Option<PathBuf>,
    record_wet: Option<PathBuf>,
    config: TunerConfig,
}

impl LiveArgs {
    fn parse(raw: Vec<String>) -> Result<Self, String> {
        let mut input_device = "default".to_string();
        let mut output_device = "default".to_string();
        let mut sample_rate = 48_000;
        let mut channels = 1;
        let mut buffer_size = None;
        let mut monitor = crate::live::MonitorMode::Tuned;
        let mut record_dry = None;
        let mut record_wet = None;
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
                    if !matches!(channels, 1 | 2) {
                        return Err("--channels must be 1 or 2".to_string());
                    }
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
                other => {
                    tuning_args.push(other.to_string());
                    if option_takes_value(other) {
                        index += 1;
                        tuning_args.push(value(&raw, index, other)?.to_string());
                    } else if other != "--no-formant-preserve" {
                        return Err(format!("unknown argument '{other}'"));
                    }
                }
            }
            index += 1;
        }

        Ok(Self {
            input_device,
            output_device,
            sample_rate,
            channels,
            buffer_size,
            monitor,
            record_dry,
            record_wet,
            config: parse_tuning_config(tuning_args)?,
        })
    }
}

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

fn parse_tuning_config(raw: Vec<String>) -> Result<TunerConfig, String> {
    let mut root = "C".to_string();
    let mut scale = "major".to_string();
    let mut config = TunerConfig::default();
    let mut index = 0;

    while index < raw.len() {
        match raw[index].as_str() {
            "--key" => {
                index += 1;
                root = value(&raw, index, "--key")?.to_string();
            }
            "--scale" => {
                index += 1;
                scale = value(&raw, index, "--scale")?.to_string();
            }
            "--preset" => {
                index += 1;
                apply_preset(&mut config, value(&raw, index, "--preset")?)?;
            }
            "--concert-a" => {
                index += 1;
                config.concert_a = parse_f32(
                    value(&raw, index, "--concert-a")?,
                    "--concert-a",
                    400.0,
                    480.0,
                )?;
            }
            "--retune-speed" => {
                index += 1;
                config.retune_speed = parse_f32(
                    value(&raw, index, "--retune-speed")?,
                    "--retune-speed",
                    0.0,
                    1.0,
                )?;
            }
            "--amount" => {
                index += 1;
                config.correction_amount =
                    parse_f32(value(&raw, index, "--amount")?, "--amount", 0.0, 1.0)?;
            }
            "--mix" => {
                index += 1;
                config.dry_wet = parse_f32(value(&raw, index, "--mix")?, "--mix", 0.0, 1.0)?;
            }
            "--humanize" => {
                index += 1;
                config.humanize =
                    parse_f32(value(&raw, index, "--humanize")?, "--humanize", 0.0, 1.0)?;
            }
            "--preserve-vibrato" => {
                index += 1;
                config.preserve_vibrato = parse_f32(
                    value(&raw, index, "--preserve-vibrato")?,
                    "--preserve-vibrato",
                    0.0,
                    1.0,
                )?;
            }
            "--min-f0" => {
                index += 1;
                config.min_frequency =
                    parse_f32(value(&raw, index, "--min-f0")?, "--min-f0", 40.0, 500.0)?;
            }
            "--max-f0" => {
                index += 1;
                config.max_frequency =
                    parse_f32(value(&raw, index, "--max-f0")?, "--max-f0", 100.0, 1600.0)?;
            }
            "--frame-ms" => {
                index += 1;
                config.frame_ms =
                    parse_f32(value(&raw, index, "--frame-ms")?, "--frame-ms", 10.0, 120.0)?;
            }
            "--hop-ms" => {
                index += 1;
                config.hop_ms = parse_f32(value(&raw, index, "--hop-ms")?, "--hop-ms", 2.0, 40.0)?;
            }
            "--min-confidence" => {
                index += 1;
                config.min_confidence = parse_f32(
                    value(&raw, index, "--min-confidence")?,
                    "--min-confidence",
                    0.0,
                    1.0,
                )?;
            }
            "--transient-protection" => {
                index += 1;
                config.transient_protection = parse_f32(
                    value(&raw, index, "--transient-protection")?,
                    "--transient-protection",
                    0.0,
                    1.0,
                )?;
            }
            "--consonant-protection" => {
                index += 1;
                config.consonant_protection = parse_f32(
                    value(&raw, index, "--consonant-protection")?,
                    "--consonant-protection",
                    0.0,
                    1.0,
                )?;
            }
            "--min-voiced-ratio" => {
                index += 1;
                config.min_voiced_ratio = parse_f32(
                    value(&raw, index, "--min-voiced-ratio")?,
                    "--min-voiced-ratio",
                    0.0,
                    1.0,
                )?;
            }
            "--output-ceiling" => {
                index += 1;
                config.output_ceiling = parse_f32(
                    value(&raw, index, "--output-ceiling")?,
                    "--output-ceiling",
                    0.1,
                    1.0,
                )?;
            }
            "--no-formant-preserve" => {
                config.formant_preserve = false;
            }
            unknown => return Err(format!("unknown argument '{unknown}'")),
        }
        index += 1;
    }

    if config.min_frequency >= config.max_frequency {
        return Err("--min-f0 must be lower than --max-f0".to_string());
    }
    config.key = Key::parse(&root, &scale)?;
    Ok(config)
}

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

fn apply_preset(config: &mut TunerConfig, preset: &str) -> Result<(), String> {
    match preset.trim().to_ascii_lowercase().as_str() {
        "natural" | "transparent" => {
            config.retune_speed = 0.22;
            config.correction_amount = 0.72;
            config.dry_wet = 0.9;
            config.humanize = 0.16;
            config.preserve_vibrato = 0.9;
            config.transient_protection = 0.75;
            config.consonant_protection = 0.75;
        }
        "pop" | "modern" => {
            config.retune_speed = 0.62;
            config.correction_amount = 1.0;
            config.dry_wet = 1.0;
            config.humanize = 0.04;
            config.preserve_vibrato = 0.5;
            config.transient_protection = 0.55;
            config.consonant_protection = 0.6;
        }
        "hard" | "hard-tune" | "effect" => {
            config.retune_speed = 1.0;
            config.correction_amount = 1.0;
            config.dry_wet = 1.0;
            config.humanize = 0.0;
            config.preserve_vibrato = 0.0;
            config.transient_protection = 0.35;
            config.consonant_protection = 0.45;
        }
        other => {
            return Err(format!(
                "unknown preset '{other}'; expected natural, pop, or hard"
            ))
        }
    }
    Ok(())
}

fn value<'a>(args: &'a [String], index: usize, name: &str) -> Result<&'a str, String> {
    args.get(index)
        .map(String::as_str)
        .ok_or_else(|| format!("missing value for {name}"))
}

fn parse_f32(value: &str, name: &str, min: f32, max: f32) -> Result<f32, String> {
    let parsed = value
        .parse::<f32>()
        .map_err(|_| format!("{name} must be a number"))?;
    if !(min..=max).contains(&parsed) {
        return Err(format!("{name} must be between {min} and {max}"));
    }
    Ok(parsed)
}

fn render_report_json(
    args: &RenderArgs,
    audio: &crate::AudioBuffer,
    report: &crate::TuningReport,
) -> String {
    format!(
        concat!(
            "{{\n",
            "  \"input\": \"{}\",\n",
            "  \"output\": \"{}\",\n",
            "  \"sample_rate\": {},\n",
            "  \"channels\": {},\n",
            "  \"duration_seconds\": {:.6},\n",
            "  \"key\": \"{}\",\n",
            "  \"scale\": \"{}\",\n",
            "  \"concert_a\": {:.3},\n",
            "  \"retune_speed\": {:.6},\n",
            "  \"amount\": {:.6},\n",
            "  \"mix\": {:.6},\n",
            "  \"humanize\": {:.6},\n",
            "  \"preserve_vibrato\": {:.6},\n",
            "  \"formant_preserve\": {},\n",
            "  \"min_f0\": {:.3},\n",
            "  \"max_f0\": {:.3},\n",
            "  \"frame_ms\": {:.3},\n",
            "  \"hop_ms\": {:.3},\n",
            "  \"min_confidence\": {:.6},\n",
            "  \"transient_protection\": {:.6},\n",
            "  \"consonant_protection\": {:.6},\n",
            "  \"min_voiced_ratio\": {:.6},\n",
            "  \"output_ceiling\": {:.6},\n",
            "  \"frames\": {},\n",
            "  \"voiced_frames\": {},\n",
            "  \"protected_frames\": {},\n",
            "  \"low_confidence_frames\": {},\n",
            "  \"average_correction_cents\": {:.6},\n",
            "  \"max_correction_cents\": {:.6},\n",
            "  \"peak\": {:.6},\n",
            "  \"rms\": {:.6},\n",
            "  \"clipped_samples\": {},\n",
            "  \"warnings\": [{}]\n",
            "}}\n"
        ),
        json_escape(&args.input.display().to_string()),
        json_escape(&args.output.display().to_string()),
        audio.sample_rate,
        audio.channels,
        audio.duration_seconds(),
        args.config.key.root,
        args.config.key.scale,
        args.config.concert_a,
        args.config.retune_speed,
        args.config.correction_amount,
        args.config.dry_wet,
        args.config.humanize,
        args.config.preserve_vibrato,
        args.config.formant_preserve,
        args.config.min_frequency,
        args.config.max_frequency,
        args.config.frame_ms,
        args.config.hop_ms,
        args.config.min_confidence,
        args.config.transient_protection,
        args.config.consonant_protection,
        args.config.min_voiced_ratio,
        args.config.output_ceiling,
        report.frames,
        report.voiced_frames,
        report.protected_frames,
        report.low_confidence_frames,
        report.average_correction_cents,
        report.max_correction_cents,
        report.peak,
        report.rms,
        report.clipped_samples,
        report
            .warnings
            .iter()
            .map(|warning| format!("\"{}\"", json_escape(warning)))
            .collect::<Vec<_>>()
            .join(", ")
    )
}

fn json_escape(value: &str) -> String {
    value
        .chars()
        .flat_map(|ch| match ch {
            '"' => "\\\"".chars().collect::<Vec<_>>(),
            '\\' => "\\\\".chars().collect::<Vec<_>>(),
            '\n' => "\\n".chars().collect::<Vec<_>>(),
            '\r' => "\\r".chars().collect::<Vec<_>>(),
            '\t' => "\\t".chars().collect::<Vec<_>>(),
            other => vec![other],
        })
        .collect()
}

fn print_help() {
    println!(
        r#"vocal-tuner

Offline key-aware vocal pitch correction for acapella recordings.

Usage:
  vocal-tuner render --input vocal.wav --output tuned.wav --key C --scale minor [options]
  vocal-tuner --input vocal.wav --output tuned.wav --key C --scale minor [options]
  vocal-tuner devices
  vocal-tuner live --input-device default --output-device default --key A --scale minor [options]

Required:
  -i, --input <FILE>          Input vocal/acapella file. WAV is native; other formats require ffmpeg.
  -o, --output <FILE>         Output file. WAV is native; other formats require ffmpeg.
      --report <FILE>         Optional JSON render report for pipeline integration.
      --key <NOTE>            Root note: C, C#, Db, D, Eb, E, F, F#, G, Ab, A, Bb, B.
      --scale <SCALE>         major, minor, chromatic, pentatonic-major, pentatonic-minor.

Controls:
      --preset <NAME>         natural, pop, or hard. Later flags override preset values.
      --retune-speed <0..1>   Correction response. 1.0 is hard-tune, 0.2 is natural. Default: 0.35.
      --amount <0..1>         Pitch correction amount. Default: 1.0.
      --mix <0..1>            Wet/dry blend. Default: 1.0.
      --humanize <0..1>       Keeps small pitch variation around target notes. Default: 0.08.
      --preserve-vibrato <0..1>
                              Reduces correction depth on expressive motion. Default: 0.65.
      --concert-a <HZ>        Tuning reference. Default: 440.
      --min-f0 <HZ>           Lowest expected vocal pitch. Default: 70.
      --max-f0 <HZ>           Highest expected vocal pitch. Default: 900.
      --frame-ms <MS>         Analysis frame length. Default: 46.
      --hop-ms <MS>           Analysis hop length. Default: 10.
      --min-confidence <0..1> Minimum pitch confidence before correction. Default: 0.68.
      --transient-protection <0..1>
                              Protects attacks from tuning artifacts. Default: 0.55.
      --consonant-protection <0..1>
                              Protects noisy consonants from tuning artifacts. Default: 0.55.
      --min-voiced-ratio <0..1>
                              Warning threshold for tunable voiced frames. Default: 0.35.
      --output-ceiling <0.1..1>
                              Peak ceiling after processing. Default: 0.98.
      --no-formant-preserve   Disable spectral-tilt restoration after pitch shifting.
      --fail-on-warnings      Return a non-zero exit after writing output/report if quality warnings occur.
  -q, --quiet                 Suppress render summary.

Live:
      --input-device <NAME|default>
                              Microphone device. Default: default.
      --output-device <NAME|default>
                              Monitor output device. Default: default.
      --sample-rate <HZ>      Live stream sample rate. Default: 48000.
      --channels <1|2>        Device channels; tuning is mono internally. Default: 1.
      --buffer-size <FRAMES>  Optional fixed device buffer size.
      --monitor <MODE>        dry, tuned, both, or muted. Default: tuned.
      --record-dry <FILE>     Write raw microphone input WAV at shutdown.
      --record-wet <FILE>     Write tuned output WAV at shutdown.

  -h, --help                  Print help.
"#
    );
}

#[cfg(test)]
mod tests {
    use super::*;

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

    #[test]
    fn parses_live_subcommand_options() {
        let command = Command::parse(vec![
            "live".into(),
            "--input-device".into(),
            "USB Mic".into(),
            "--output-device".into(),
            "Studio Out".into(),
            "--sample-rate".into(),
            "44100".into(),
            "--channels".into(),
            "2".into(),
            "--buffer-size".into(),
            "256".into(),
            "--monitor".into(),
            "both".into(),
            "--record-dry".into(),
            "dry.wav".into(),
            "--record-wet".into(),
            "wet.wav".into(),
            "--key".into(),
            "A".into(),
            "--scale".into(),
            "minor".into(),
        ])
        .unwrap();

        match command {
            Command::Live(args) => {
                assert_eq!(args.input_device, "USB Mic");
                assert_eq!(args.output_device, "Studio Out");
                assert_eq!(args.sample_rate, 44_100);
                assert_eq!(args.channels, 2);
                assert_eq!(args.buffer_size, Some(256));
                assert_eq!(args.monitor, crate::live::MonitorMode::Both);
                assert_eq!(args.record_dry, Some(PathBuf::from("dry.wav")));
                assert_eq!(args.record_wet, Some(PathBuf::from("wet.wav")));
                assert_eq!(args.config.key.root.to_string(), "A");
                assert_eq!(args.config.key.scale.to_string(), "minor");
            }
            other => panic!("expected live command, got {other:?}"),
        }
    }

    #[test]
    fn rejects_invalid_live_channels() {
        let err = Command::parse(vec!["live".into(), "--channels".into(), "3".into()]).unwrap_err();

        assert!(err.contains("--channels"));
        assert!(err.contains("1 or 2"));
    }

    #[test]
    fn parses_full_cli() {
        let args = RenderArgs::parse(vec![
            "--input".into(),
            "in.wav".into(),
            "--output".into(),
            "out.wav".into(),
            "--key".into(),
            "Bb".into(),
            "--scale".into(),
            "minor".into(),
            "--retune-speed".into(),
            "0.8".into(),
            "--mix".into(),
            "0.6".into(),
        ])
        .unwrap();

        assert_eq!(args.input, PathBuf::from("in.wav"));
        assert_eq!(args.output, PathBuf::from("out.wav"));
        assert!((args.config.retune_speed - 0.8).abs() < f32::EPSILON);
        assert!((args.config.dry_wet - 0.6).abs() < f32::EPSILON);
    }

    #[test]
    fn preset_can_be_overridden() {
        let args = RenderArgs::parse(vec![
            "--input".into(),
            "in.wav".into(),
            "--output".into(),
            "out.wav".into(),
            "--preset".into(),
            "hard".into(),
            "--retune-speed".into(),
            "0.5".into(),
        ])
        .unwrap();

        assert!((args.config.correction_amount - 1.0).abs() < f32::EPSILON);
        assert!((args.config.preserve_vibrato - 0.0).abs() < f32::EPSILON);
        assert!((args.config.retune_speed - 0.5).abs() < f32::EPSILON);
    }

    #[test]
    fn rejects_invalid_ranges() {
        let err = RenderArgs::parse(vec![
            "--input".into(),
            "in.wav".into(),
            "--output".into(),
            "out.wav".into(),
            "--retune-speed".into(),
            "2.0".into(),
        ])
        .unwrap_err();
        assert!(err.contains("--retune-speed"));
    }

    #[test]
    fn renders_wav_and_report_end_to_end() {
        let dir = std::env::temp_dir().join(format!("vocal-tuner-cli-test-{}", std::process::id()));
        let _ = std::fs::create_dir_all(&dir);
        let input = dir.join("input.wav");
        let output = dir.join("output.wav");
        let report = dir.join("report.json");
        let sample_rate = 48_000;
        let samples: Vec<f32> = (0..sample_rate / 3)
            .map(|i| {
                (2.0 * std::f32::consts::PI * 230.0 * i as f32 / sample_rate as f32).sin() * 0.25
            })
            .collect();

        crate::wav::write_wav(
            &input,
            &crate::AudioBuffer {
                sample_rate,
                channels: 1,
                samples,
            },
        )
        .unwrap();

        run_with_args(vec![
            "--input".into(),
            input.display().to_string(),
            "--output".into(),
            output.display().to_string(),
            "--report".into(),
            report.display().to_string(),
            "--key".into(),
            "A".into(),
            "--scale".into(),
            "minor".into(),
            "--preset".into(),
            "pop".into(),
            "--quiet".into(),
        ])
        .unwrap();

        let rendered = crate::wav::read_wav(&output).unwrap();
        let report_text = std::fs::read_to_string(&report).unwrap();
        let _ = std::fs::remove_dir_all(dir);

        assert_eq!(rendered.sample_rate, sample_rate);
        assert_eq!(rendered.channels, 1);
        assert!(report_text.contains("\"key\": \"A\""));
        assert!(report_text.contains("\"voiced_frames\""));
        assert!(report_text.contains("\"warnings\""));
        assert!(report_text.contains("\"protected_frames\""));
    }

    #[test]
    fn fail_on_warnings_returns_error_after_report() {
        let dir =
            std::env::temp_dir().join(format!("vocal-tuner-warning-test-{}", std::process::id()));
        let _ = std::fs::create_dir_all(&dir);
        let input = dir.join("input.wav");
        let output = dir.join("output.wav");
        let report = dir.join("report.json");

        crate::wav::write_wav(
            &input,
            &crate::AudioBuffer {
                sample_rate: 48_000,
                channels: 1,
                samples: vec![0.0; 4096],
            },
        )
        .unwrap();

        let err = run_with_args(vec![
            "--input".into(),
            input.display().to_string(),
            "--output".into(),
            output.display().to_string(),
            "--report".into(),
            report.display().to_string(),
            "--min-voiced-ratio".into(),
            "0.9".into(),
            "--fail-on-warnings".into(),
            "--quiet".into(),
        ])
        .unwrap_err();

        let report_text = std::fs::read_to_string(&report).unwrap();
        let _ = std::fs::remove_dir_all(dir);

        assert!(err.contains("quality warnings"));
        assert!(report_text.contains("low voiced-frame ratio"));
    }
}
