use std::collections::VecDeque;
use std::path::PathBuf;
use std::sync::{
    atomic::{AtomicBool, AtomicUsize, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::Duration;

use cpal::{
    traits::{DeviceTrait, HostTrait, StreamTrait},
    FromSample, Sample, SampleFormat, SizedSample,
};

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
            other => Err(format!(
                "unknown monitor mode '{other}'; expected dry, tuned, both, or muted"
            )),
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

pub fn run_live(config: LiveConfig) -> Result<(), String> {
    let host = cpal::default_host();
    let input_device = select_cpal_device(&host, true, &config.input_device)?;
    let output_device = select_cpal_device(&host, false, &config.output_device)?;
    crate::recorder::LiveRecorder::preflight(
        config.record_dry.as_ref(),
        config.record_wet.as_ref(),
    )?;

    let input_config = resolve_device_config(&input_device, true, &config)?;
    let output_config = resolve_device_config(&output_device, false, &config)?;

    let input_queue = Arc::new(Mutex::new(VecDeque::<f32>::with_capacity(
        config.sample_rate as usize,
    )));
    let output_queue = Arc::new(Mutex::new(VecDeque::<f32>::with_capacity(
        config.sample_rate as usize,
    )));
    let recorder = Arc::new(Mutex::new(crate::recorder::LiveRecorder::new(
        input_config.stream.sample_rate.0,
        config.record_dry.clone(),
        config.record_wet.clone(),
    )));
    let running = Arc::new(AtomicBool::new(true));
    let dropouts = Arc::new(AtomicUsize::new(0));
    let stream_error = Arc::new(Mutex::new(None::<String>));

    let input_queue_for_callback = Arc::clone(&input_queue);
    let input_running = Arc::clone(&running);
    let input_stream_error = Arc::clone(&stream_error);
    let input_stream = build_input_stream_for_format(
        &input_device,
        input_config.sample_format,
        &input_config.stream,
        input_queue_for_callback,
        input_running,
        input_stream_error,
    )
    .map_err(|err| {
        format!(
            "failed to build input stream for {} Hz, {} channel(s): {err}\nSupported input formats:\n{}{}",
            input_config.stream.sample_rate.0,
            input_config.stream.channels,
            input_config.formats,
            wsl_audio_hint()
        )
    })?;

    let output_queue_for_callback = Arc::clone(&output_queue);
    let dropouts_for_callback = Arc::clone(&dropouts);
    let output_running = Arc::clone(&running);
    let output_stream_error = Arc::clone(&stream_error);
    let output_stream = build_output_stream_for_format(
        &output_device,
        output_config.sample_format,
        &output_config.stream,
        output_queue_for_callback,
        dropouts_for_callback,
        output_running,
        output_stream_error,
    )
    .map_err(|err| {
        format!(
            "failed to build output stream for {} Hz, {} channel(s): {err}\nSupported output formats:\n{}{}",
            output_config.stream.sample_rate.0,
            output_config.stream.channels,
            output_config.formats,
            wsl_audio_hint()
        )
    })?;

    let running_for_ctrlc = Arc::clone(&running);
    ctrlc::set_handler(move || {
        running_for_ctrlc.store(false, Ordering::SeqCst);
    })
    .map_err(|err| format!("failed to install Ctrl-C handler: {err}"))?;

    let mut tuner =
        crate::dsp::StreamingTuner::new(input_config.stream.sample_rate.0, config.tuner.clone());
    let block_size = live_block_size(input_config.stream.sample_rate.0, &config.tuner);
    input_stream
        .play()
        .map_err(|err| format!("failed to start input stream: {err}"))?;
    prime_output_queue(
        &input_queue,
        &output_queue,
        &recorder,
        &mut tuner,
        &config,
        input_config.stream.sample_rate.0,
        block_size,
    );
    output_stream
        .play()
        .map_err(|err| format!("failed to start output stream: {err}"))?;
    eprintln!("live vocal tuner running; press Ctrl-C to stop");

    while running.load(Ordering::SeqCst) {
        let block = pop_block(&input_queue, block_size);
        if block.is_empty() {
            thread::sleep(Duration::from_millis(2));
            continue;
        }
        process_live_block(
            &block,
            &output_queue,
            &recorder,
            &mut tuner,
            &config,
            input_config.stream.sample_rate.0 as usize,
        );
    }

    drop(input_stream);
    drop(output_stream);

    let recorder = Arc::try_unwrap(recorder)
        .map_err(|_| "failed to close recorder because it is still in use".to_string())?
        .into_inner()
        .map_err(|_| "failed to close recorder lock".to_string())?;
    let finalize_result = recorder.finalize();

    if let Some(err) = stream_error
        .lock()
        .map_err(|_| "failed to read stream error state".to_string())?
        .take()
    {
        finalize_result?;
        return Err(err);
    }

    finalize_result?;

    eprintln!(
        "live session ended; output dropouts: {}",
        dropouts.load(Ordering::Relaxed)
    );
    Ok(())
}

fn select_cpal_device(
    host: &cpal::Host,
    input: bool,
    requested: &str,
) -> Result<cpal::Device, String> {
    if requested == "default" {
        return if input {
            host.default_input_device()
                .ok_or_else(|| "no default input device found; run vocal-tuner devices".to_string())
        } else {
            host.default_output_device().ok_or_else(|| {
                "no default output device found; run vocal-tuner devices".to_string()
            })
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
    Err(format!(
        "{kind} device '{requested}' was not found; run vocal-tuner devices"
    ))
}

#[derive(Debug, Clone)]
struct ResolvedDeviceConfig {
    stream: cpal::StreamConfig,
    sample_format: SampleFormat,
    formats: String,
}

fn resolve_device_config(
    device: &cpal::Device,
    input: bool,
    config: &LiveConfig,
) -> Result<ResolvedDeviceConfig, String> {
    let ranges = if input {
        device
            .supported_input_configs()
            .map_err(|err| format!("failed to inspect input formats: {err}{}", wsl_audio_hint()))?
            .collect::<Vec<_>>()
    } else {
        device
            .supported_output_configs()
            .map_err(|err| {
                format!(
                    "failed to inspect output formats: {err}{}",
                    wsl_audio_hint()
                )
            })?
            .collect::<Vec<_>>()
    };
    let formats = describe_formats(&ranges);
    let requested_rate = cpal::SampleRate(config.sample_rate);

    let resolved = best_supported_config(&ranges, config.channels, requested_rate)
        .ok_or_else(|| {
            let kind = if input { "input" } else { "output" };
            format!(
                "unsupported {kind} stream request: {} Hz, {} channel(s)\nSupported {kind} formats:\n{}",
                config.sample_rate, config.channels, formats
            )
        })?;

    let sample_format = resolved.sample_format();
    let mut stream = resolved.config();
    if let Some(buffer_size) = config.buffer_size {
        stream.buffer_size = cpal::BufferSize::Fixed(buffer_size);
    }

    Ok(ResolvedDeviceConfig {
        stream,
        sample_format,
        formats,
    })
}

fn best_supported_config(
    ranges: &[cpal::SupportedStreamConfigRange],
    channels: u16,
    sample_rate: cpal::SampleRate,
) -> Option<cpal::SupportedStreamConfig> {
    ranges
        .iter()
        .filter(|range| {
            is_supported_sample_format(range.sample_format())
                && range.channels() == channels
                && range.min_sample_rate() <= sample_rate
                && sample_rate <= range.max_sample_rate()
        })
        .min_by_key(|range| sample_format_rank(range.sample_format()))
        .cloned()
        .map(|range| range.with_sample_rate(sample_rate))
}

fn wsl_audio_hint() -> &'static str {
    if std::path::Path::new("/mnt/wslg/PulseServer").exists() {
        "\nWSL hint: WSLg PulseAudio is present, but ALSA may need libasound2-plugins plus a Pulse default in ~/.asoundrc. See the README WSL Audio Setup section."
    } else {
        ""
    }
}

fn live_block_size(sample_rate: u32, config: &TunerConfig) -> usize {
    let frame_len = ((sample_rate as f32 * config.frame_ms / 1000.0).round() as usize).max(512);
    let min_pitch_len = (sample_rate as f32 / config.min_frequency).ceil() as usize + 3;
    frame_len.max(min_pitch_len)
}

fn live_prefill_samples(sample_rate: u32) -> usize {
    (sample_rate as usize / 4).max(1024)
}

fn prime_output_queue(
    input_queue: &Arc<Mutex<VecDeque<f32>>>,
    output_queue: &Arc<Mutex<VecDeque<f32>>>,
    recorder: &Arc<Mutex<crate::recorder::LiveRecorder>>,
    tuner: &mut crate::dsp::StreamingTuner,
    config: &LiveConfig,
    sample_rate: u32,
    block_size: usize,
) {
    let target_samples = live_prefill_samples(sample_rate);
    let deadline = std::time::Instant::now() + Duration::from_secs(2);

    while output_queue
        .lock()
        .map(|queue| queue.len() < target_samples)
        .unwrap_or(false)
        && std::time::Instant::now() < deadline
    {
        let block = pop_block(input_queue, block_size);
        if block.is_empty() {
            thread::sleep(Duration::from_millis(2));
            continue;
        }
        process_live_block(
            &block,
            output_queue,
            recorder,
            tuner,
            config,
            sample_rate as usize,
        );
    }
}

fn process_live_block(
    block: &[f32],
    output_queue: &Arc<Mutex<VecDeque<f32>>>,
    recorder: &Arc<Mutex<crate::recorder::LiveRecorder>>,
    tuner: &mut crate::dsp::StreamingTuner,
    config: &LiveConfig,
    max_output_samples: usize,
) {
    let wet = tuner.process_block(block);
    if let Ok(mut recorder) = recorder.lock() {
        recorder.push_dry(block);
        recorder.push_wet(&wet);
    }
    let monitor = mix_monitor(config.monitor, block, &wet);
    if let Ok(mut queue) = output_queue.lock() {
        queue.extend(monitor);
        while queue.len() > max_output_samples {
            queue.pop_front();
        }
    }
}

fn is_supported_sample_format(format: SampleFormat) -> bool {
    matches!(
        format,
        SampleFormat::F32
            | SampleFormat::F64
            | SampleFormat::I8
            | SampleFormat::I16
            | SampleFormat::I32
            | SampleFormat::U8
            | SampleFormat::U16
            | SampleFormat::U32
    )
}

fn sample_format_rank(format: SampleFormat) -> u8 {
    match format {
        SampleFormat::F32 => 0,
        SampleFormat::I16 => 1,
        SampleFormat::F64 => 2,
        SampleFormat::I32 => 3,
        SampleFormat::U16 => 4,
        SampleFormat::U32 => 5,
        SampleFormat::I8 => 6,
        SampleFormat::U8 => 7,
        _ => 8,
    }
}

fn describe_formats(ranges: &[cpal::SupportedStreamConfigRange]) -> String {
    if ranges.is_empty() {
        return "  <none>".to_string();
    }

    ranges
        .iter()
        .map(|range| {
            format!(
                "  {} channel(s), {}-{} Hz, {}",
                range.channels(),
                range.min_sample_rate().0,
                range.max_sample_rate().0,
                range.sample_format()
            )
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn build_input_stream_for_format(
    device: &cpal::Device,
    sample_format: SampleFormat,
    stream_config: &cpal::StreamConfig,
    queue: Arc<Mutex<VecDeque<f32>>>,
    running: Arc<AtomicBool>,
    stream_error: Arc<Mutex<Option<String>>>,
) -> Result<cpal::Stream, cpal::BuildStreamError> {
    match sample_format {
        SampleFormat::I8 => {
            build_input_stream::<i8>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::F32 => {
            build_input_stream::<f32>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::F64 => {
            build_input_stream::<f64>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::I16 => {
            build_input_stream::<i16>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::I32 => {
            build_input_stream::<i32>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::U8 => {
            build_input_stream::<u8>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::U16 => {
            build_input_stream::<u16>(device, stream_config, queue, running, stream_error)
        }
        SampleFormat::U32 => {
            build_input_stream::<u32>(device, stream_config, queue, running, stream_error)
        }
        other => unreachable!("unsupported input sample format selected: {other}"),
    }
}

fn build_input_stream<T>(
    device: &cpal::Device,
    stream_config: &cpal::StreamConfig,
    queue: Arc<Mutex<VecDeque<f32>>>,
    running: Arc<AtomicBool>,
    stream_error: Arc<Mutex<Option<String>>>,
) -> Result<cpal::Stream, cpal::BuildStreamError>
where
    T: Sample + SizedSample,
    f32: FromSample<T>,
{
    let channels = stream_config.channels as usize;
    let max_samples = stream_config.sample_rate.0 as usize;
    let error_running = Arc::clone(&running);
    device.build_input_stream(
        stream_config,
        move |data: &[T], _| {
            if let Ok(mut queue) = queue.try_lock() {
                push_input_data(data, channels, max_samples, &mut queue);
            }
        },
        move |err| {
            if let Ok(mut slot) = stream_error.lock() {
                *slot = Some(format!("input stream error: {err}"));
            }
            error_running.store(false, Ordering::SeqCst);
        },
        None,
    )
}

fn build_output_stream_for_format(
    device: &cpal::Device,
    sample_format: SampleFormat,
    stream_config: &cpal::StreamConfig,
    queue: Arc<Mutex<VecDeque<f32>>>,
    dropouts: Arc<AtomicUsize>,
    running: Arc<AtomicBool>,
    stream_error: Arc<Mutex<Option<String>>>,
) -> Result<cpal::Stream, cpal::BuildStreamError> {
    match sample_format {
        SampleFormat::I8 => build_output_stream::<i8>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::F32 => build_output_stream::<f32>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::F64 => build_output_stream::<f64>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::I16 => build_output_stream::<i16>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::I32 => build_output_stream::<i32>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::U8 => build_output_stream::<u8>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::U16 => build_output_stream::<u16>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        SampleFormat::U32 => build_output_stream::<u32>(
            device,
            stream_config,
            queue,
            dropouts,
            running,
            stream_error,
        ),
        other => unreachable!("unsupported output sample format selected: {other}"),
    }
}

fn build_output_stream<T>(
    device: &cpal::Device,
    stream_config: &cpal::StreamConfig,
    queue: Arc<Mutex<VecDeque<f32>>>,
    dropouts: Arc<AtomicUsize>,
    running: Arc<AtomicBool>,
    stream_error: Arc<Mutex<Option<String>>>,
) -> Result<cpal::Stream, cpal::BuildStreamError>
where
    T: Sample + SizedSample + FromSample<f32>,
{
    let channels = stream_config.channels as usize;
    let error_running = Arc::clone(&running);
    device.build_output_stream(
        stream_config,
        move |data: &mut [T], _| {
            write_output_data(data, channels, &queue, &dropouts);
        },
        move |err| {
            if let Ok(mut slot) = stream_error.lock() {
                *slot = Some(format!("output stream error: {err}"));
            }
            error_running.store(false, Ordering::SeqCst);
        },
        None,
    )
}

fn push_input_data<T>(data: &[T], channels: usize, max_samples: usize, queue: &mut VecDeque<f32>)
where
    T: Sample,
    f32: FromSample<T>,
{
    for frame in data.chunks(channels) {
        while queue.len() >= max_samples {
            queue.pop_front();
        }
        let mono = frame
            .iter()
            .map(|sample| f32::from_sample(*sample))
            .sum::<f32>()
            / channels as f32;
        queue.push_back(mono);
    }
}

fn write_output_data<T>(
    output: &mut [T],
    channels: usize,
    queue: &Arc<Mutex<VecDeque<f32>>>,
    dropouts: &AtomicUsize,
) where
    T: Sample + FromSample<f32>,
{
    if let Ok(mut queue) = queue.try_lock() {
        for frame in output.chunks_mut(channels) {
            let sample = queue.pop_front().unwrap_or_else(|| {
                dropouts.fetch_add(1, Ordering::Relaxed);
                0.0
            });
            let sample = T::from_sample(sample);
            for channel in frame {
                *channel = sample;
            }
        }
    } else {
        for sample in output {
            *sample = T::from_sample(0.0);
        }
    }
}

fn pop_block(queue: &Arc<Mutex<VecDeque<f32>>>, size: usize) -> Vec<f32> {
    let mut block = Vec::with_capacity(size);
    if let Ok(mut queue) = queue.lock() {
        if queue.len() < size {
            return block;
        }
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

    #[test]
    fn live_block_size_supports_default_low_pitch_detection() {
        let config = TunerConfig::default();
        let block_size = live_block_size(48_000, &config);

        assert!(block_size > (48_000.0 / config.min_frequency).ceil() as usize + 2);
    }

    #[test]
    fn live_prefill_uses_quarter_second_latency_floor() {
        assert_eq!(live_prefill_samples(48_000), 12_000);
        assert_eq!(live_prefill_samples(2_000), 1024);
    }

    #[test]
    fn best_supported_config_prefers_sixteen_bit_over_u8() {
        let ranges = vec![
            cpal::SupportedStreamConfigRange::new(
                1,
                cpal::SampleRate(48_000),
                cpal::SampleRate(48_000),
                cpal::SupportedBufferSize::Unknown,
                SampleFormat::U8,
            ),
            cpal::SupportedStreamConfigRange::new(
                1,
                cpal::SampleRate(48_000),
                cpal::SampleRate(48_000),
                cpal::SupportedBufferSize::Unknown,
                SampleFormat::I16,
            ),
        ];

        let config = best_supported_config(&ranges, 1, cpal::SampleRate(48_000)).unwrap();

        assert_eq!(config.sample_format(), SampleFormat::I16);
    }

    #[test]
    fn input_queue_drops_old_samples_before_push_when_full() {
        let mut queue = VecDeque::from(vec![1.0, 2.0, 3.0]);

        push_input_data(&[4.0_f32, 5.0], 1, 3, &mut queue);

        assert_eq!(queue.into_iter().collect::<Vec<_>>(), vec![3.0, 4.0, 5.0]);
    }

    #[test]
    fn pop_block_waits_for_full_block() {
        let queue = Arc::new(Mutex::new(VecDeque::from(vec![1.0, 2.0])));

        let block = pop_block(&queue, 3);

        assert!(block.is_empty());
        assert_eq!(queue.lock().unwrap().len(), 2);
    }

    #[test]
    fn pop_block_returns_full_block() {
        let queue = Arc::new(Mutex::new(VecDeque::from(vec![1.0, 2.0, 3.0, 4.0])));

        let block = pop_block(&queue, 3);

        assert_eq!(block, vec![1.0, 2.0, 3.0]);
        assert_eq!(
            queue.lock().unwrap().iter().copied().collect::<Vec<_>>(),
            vec![4.0]
        );
    }
}
