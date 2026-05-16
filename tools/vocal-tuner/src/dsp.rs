use crate::audio::AudioBuffer;
use crate::music::{hz_to_midi, midi_to_hz, Key};

#[derive(Debug, Clone)]
pub struct TunerConfig {
    pub key: Key,
    pub concert_a: f32,
    pub retune_speed: f32,
    pub correction_amount: f32,
    pub dry_wet: f32,
    pub humanize: f32,
    pub preserve_vibrato: f32,
    pub min_frequency: f32,
    pub max_frequency: f32,
    pub frame_ms: f32,
    pub hop_ms: f32,
    pub formant_preserve: bool,
    pub min_confidence: f32,
    pub transient_protection: f32,
    pub consonant_protection: f32,
    pub min_voiced_ratio: f32,
    pub output_ceiling: f32,
}

impl Default for TunerConfig {
    fn default() -> Self {
        Self {
            key: Key::parse("C", "major").expect("valid default key"),
            concert_a: 440.0,
            retune_speed: 0.35,
            correction_amount: 1.0,
            dry_wet: 1.0,
            humanize: 0.08,
            preserve_vibrato: 0.65,
            min_frequency: 70.0,
            max_frequency: 900.0,
            frame_ms: 46.0,
            hop_ms: 10.0,
            formant_preserve: true,
            min_confidence: 0.68,
            transient_protection: 0.55,
            consonant_protection: 0.55,
            min_voiced_ratio: 0.35,
            output_ceiling: 0.98,
        }
    }
}

#[derive(Debug, Clone, Default)]
pub struct TuningReport {
    pub frames: usize,
    pub voiced_frames: usize,
    pub protected_frames: usize,
    pub low_confidence_frames: usize,
    pub average_correction_cents: f32,
    pub max_correction_cents: f32,
    pub peak: f32,
    pub rms: f32,
    pub clipped_samples: usize,
    pub warnings: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct StreamingTuner {
    sample_rate: u32,
    config: TunerConfig,
    smoothed_ratio: f32,
}

impl StreamingTuner {
    pub fn new(sample_rate: u32, config: TunerConfig) -> Self {
        Self {
            sample_rate,
            config,
            smoothed_ratio: 1.0,
        }
    }

    pub fn process_block(&mut self, input: &[f32]) -> Vec<f32> {
        if input.is_empty() {
            return Vec::new();
        }

        let metrics = segment_metrics(input);
        let (pitch_hz, confidence) = detect_pitch_yin(
            input,
            self.sample_rate,
            self.config.min_frequency,
            self.config.max_frequency,
        );
        let pitch_hz =
            pitch_hz.filter(|_| confidence >= self.config.min_confidence && metrics.rms > 0.0005);
        let raw_ratio = pitch_hz
            .map(|pitch| correction_ratio(pitch, &self.config))
            .unwrap_or(1.0);
        let response = self.config.retune_speed.clamp(0.0, 1.0);
        self.smoothed_ratio = self.smoothed_ratio * (1.0 - response) + raw_ratio * response;

        let wet = if let Some(pitch_hz) = pitch_hz {
            let shifted =
                pitch_shift_segment(input, self.smoothed_ratio, pitch_hz, self.sample_rate);
            if self.config.formant_preserve {
                restore_spectral_tilt(input, &shifted)
            } else {
                shifted
            }
        } else {
            input.to_vec()
        };

        let mut output: Vec<f32> = input
            .iter()
            .zip(wet.iter())
            .map(|(dry, wet)| dry * (1.0 - self.config.dry_wet) + wet * self.config.dry_wet)
            .collect();
        normalize_soft(&mut output, self.config.output_ceiling);
        output
    }
}

#[derive(Debug, Clone)]
struct PitchFrame {
    start: usize,
    end: usize,
    pitch_hz: Option<f32>,
    shift_ratio: f32,
    confidence: f32,
    protected: bool,
    low_confidence: bool,
}

pub fn tune(audio: &AudioBuffer, config: &TunerConfig) -> (AudioBuffer, TuningReport) {
    let mut tuned_channels = Vec::new();
    let mut reports = Vec::new();

    for channel_index in 0..audio.channels as usize {
        let channel = audio.channel(channel_index);
        let (tuned, report) = tune_channel(&channel, audio.sample_rate, config);
        tuned_channels.push(tuned);
        reports.push(report);
    }

    let mut report = TuningReport::default();
    for item in reports {
        report.frames += item.frames;
        report.voiced_frames += item.voiced_frames;
        report.protected_frames += item.protected_frames;
        report.low_confidence_frames += item.low_confidence_frames;
        report.average_correction_cents +=
            item.average_correction_cents * item.voiced_frames as f32;
        report.max_correction_cents = report.max_correction_cents.max(item.max_correction_cents);
    }
    if report.voiced_frames > 0 {
        report.average_correction_cents /= report.voiced_frames as f32;
    }

    let output = AudioBuffer::from_channels(audio.sample_rate, &tuned_channels);
    add_render_diagnostics(&output.samples, config, &mut report);
    (output, report)
}

fn tune_channel(input: &[f32], sample_rate: u32, config: &TunerConfig) -> (Vec<f32>, TuningReport) {
    let frames = analyze_frames(input, sample_rate, config);
    let mut output = vec![0.0_f32; input.len()];
    let mut weights = vec![0.0_f32; input.len()];
    let mut report = TuningReport {
        frames: frames.len(),
        ..TuningReport::default()
    };

    for frame in &frames {
        if frame.protected {
            report.protected_frames += 1;
        }
        if frame.low_confidence {
            report.low_confidence_frames += 1;
        }
        if frame.pitch_hz.is_some() && !frame.protected {
            report.voiced_frames += 1;
            let cents = frame.shift_ratio.log2().abs() * 1200.0;
            report.average_correction_cents += cents;
            report.max_correction_cents = report.max_correction_cents.max(cents);
        }

        let segment = &input[frame.start..frame.end];
        let shifted = if let Some(pitch_hz) = frame.pitch_hz.filter(|_| !frame.protected) {
            let trusted_ratio = 1.0 + (frame.shift_ratio - 1.0) * frame.confidence.clamp(0.0, 1.0);
            let shifted = pitch_shift_segment(segment, trusted_ratio, pitch_hz, sample_rate);
            if config.formant_preserve {
                restore_spectral_tilt(segment, &shifted)
            } else {
                shifted
            }
        } else {
            segment.to_vec()
        };

        for (index, sample) in shifted.iter().enumerate() {
            let target_index = frame.start + index;
            if target_index >= output.len() {
                break;
            }
            let window = hann(index, shifted.len());
            output[target_index] += sample * window;
            weights[target_index] += window;
        }
    }

    if report.voiced_frames > 0 {
        report.average_correction_cents /= report.voiced_frames as f32;
    }

    for index in 0..output.len() {
        let wet = if weights[index] > 0.00001 {
            output[index] / weights[index]
        } else {
            input[index]
        };
        output[index] = input[index] * (1.0 - config.dry_wet) + wet * config.dry_wet;
    }

    normalize_soft(&mut output, config.output_ceiling);
    (output, report)
}

fn analyze_frames(input: &[f32], sample_rate: u32, config: &TunerConfig) -> Vec<PitchFrame> {
    let frame_len = ((sample_rate as f32 * config.frame_ms / 1000.0).round() as usize).max(512);
    let hop_len = ((sample_rate as f32 * config.hop_ms / 1000.0).round() as usize).max(64);
    let mut frames = Vec::new();
    let mut smoothed_ratio = 1.0_f32;
    let mut start = 0;
    let mut previous_rms = 0.0_f32;

    while start < input.len() {
        let end = (start + frame_len).min(input.len());
        if end - start < frame_len / 2 {
            break;
        }
        let segment = &input[start..end];
        let metrics = segment_metrics(segment);
        let protected = is_protected_frame(&metrics, previous_rms, config);
        previous_rms = metrics.rms;

        let (mut pitch_hz, confidence) = detect_pitch_yin(
            segment,
            sample_rate,
            config.min_frequency,
            config.max_frequency,
        );
        let low_confidence = pitch_hz.is_some() && confidence < config.min_confidence;
        if low_confidence || protected {
            pitch_hz = None;
        }

        let raw_ratio = pitch_hz
            .map(|pitch| correction_ratio(pitch, config))
            .unwrap_or(1.0);
        let response = config.retune_speed.clamp(0.0, 1.0);
        smoothed_ratio = smoothed_ratio * (1.0 - response) + raw_ratio * response;

        frames.push(PitchFrame {
            start,
            end,
            pitch_hz,
            shift_ratio: smoothed_ratio,
            confidence,
            protected,
            low_confidence,
        });

        start += hop_len;
    }

    frames
}

#[derive(Debug, Clone, Copy)]
struct SegmentMetrics {
    rms: f32,
    zero_crossing_rate: f32,
}

fn segment_metrics(segment: &[f32]) -> SegmentMetrics {
    if segment.is_empty() {
        return SegmentMetrics {
            rms: 0.0,
            zero_crossing_rate: 0.0,
        };
    }

    let mut crossings = 0_usize;
    for pair in segment.windows(2) {
        if pair[0].signum() != pair[1].signum() {
            crossings += 1;
        }
    }

    SegmentMetrics {
        rms: (segment.iter().map(|sample| sample * sample).sum::<f32>() / segment.len() as f32)
            .sqrt(),
        zero_crossing_rate: crossings as f32 / segment.len().max(1) as f32,
    }
}

fn is_protected_frame(metrics: &SegmentMetrics, previous_rms: f32, config: &TunerConfig) -> bool {
    let transient_threshold = 1.0 + config.transient_protection.clamp(0.0, 1.0) * 4.0;
    let consonant_threshold = 0.34 - config.consonant_protection.clamp(0.0, 1.0) * 0.2;
    let transient = previous_rms > 0.001 && metrics.rms > previous_rms * transient_threshold;
    let noisy_consonant = metrics.zero_crossing_rate > consonant_threshold && metrics.rms > 0.005;
    transient || noisy_consonant
}

fn correction_ratio(pitch_hz: f32, config: &TunerConfig) -> f32 {
    let midi = hz_to_midi(pitch_hz, config.concert_a);
    let target_midi = config.key.nearest_midi(midi);
    let detune = target_midi - midi;
    let deadband = config.humanize.clamp(0.0, 1.0) * 35.0 / 100.0;
    let effective_detune = if detune.abs() < deadband {
        0.0
    } else {
        detune.signum() * (detune.abs() - deadband)
    };
    let vibrato_scale = 1.0 - config.preserve_vibrato.clamp(0.0, 1.0) * 0.25;
    let corrected_midi =
        midi + effective_detune * config.correction_amount.clamp(0.0, 1.0) * vibrato_scale;
    midi_to_hz(corrected_midi, config.concert_a) / pitch_hz
}

fn pitch_shift_segment(segment: &[f32], ratio: f32, pitch_hz: f32, sample_rate: u32) -> Vec<f32> {
    if (ratio - 1.0).abs() < 0.0001 {
        return segment.to_vec();
    }

    let input_period = (sample_rate as f32 / pitch_hz).clamp(24.0, 1200.0);
    let output_period = (input_period / ratio).clamp(24.0, 1200.0);
    let half_window = (input_period * 0.5).round() as isize;
    let window_len = (half_window * 2).max(32) as usize;
    let mut output = vec![0.0_f32; segment.len()];
    let mut weights = vec![0.0_f32; segment.len()];
    let mut output_mark = input_period;

    while output_mark < segment.len() as f32 {
        let source_mark = output_mark * ratio;
        if source_mark >= segment.len() as f32 {
            break;
        }

        let out_center = output_mark.round() as isize;
        let src_center = source_mark.round() as isize;

        for window_index in 0..window_len {
            let offset = window_index as isize - half_window;
            let out_index = out_center + offset;
            let src_index = src_center + offset;
            if out_index < 0
                || src_index < 0
                || out_index >= output.len() as isize
                || src_index >= segment.len() as isize
            {
                continue;
            }
            let weight = hann(window_index, window_len);
            output[out_index as usize] += segment[src_index as usize] * weight;
            weights[out_index as usize] += weight;
        }

        output_mark += output_period;
    }

    for index in 0..output.len() {
        output[index] = if weights[index] > 0.00001 {
            output[index] / weights[index]
        } else {
            segment[index]
        };
    }
    output
}

fn restore_spectral_tilt(original: &[f32], shifted: &[f32]) -> Vec<f32> {
    let original_tilt = high_low_energy_ratio(original);
    let shifted_tilt = high_low_energy_ratio(shifted);
    if original_tilt <= 0.0 || shifted_tilt <= 0.0 {
        return shifted.to_vec();
    }

    let correction = (original_tilt / shifted_tilt).sqrt().clamp(0.75, 1.33);
    let mut output = Vec::with_capacity(shifted.len());
    let mut previous = 0.0_f32;
    for sample in shifted {
        let high = *sample - previous;
        let low = *sample - high;
        output.push(low + high * correction);
        previous = *sample;
    }
    output
}

fn high_low_energy_ratio(samples: &[f32]) -> f32 {
    if samples.len() < 2 {
        return 0.0;
    }
    let mut low_energy = 0.0;
    let mut high_energy = 0.0;
    let mut previous = samples[0];
    for sample in samples.iter().skip(1) {
        let high = *sample - previous;
        let low = *sample - high;
        high_energy += high * high;
        low_energy += low * low;
        previous = *sample;
    }
    high_energy / low_energy.max(0.0000001)
}

fn detect_pitch_yin(
    segment: &[f32],
    sample_rate: u32,
    min_frequency: f32,
    max_frequency: f32,
) -> (Option<f32>, f32) {
    let min_tau = (sample_rate as f32 / max_frequency).floor().max(2.0) as usize;
    let max_tau = (sample_rate as f32 / min_frequency).ceil() as usize;
    if segment.len() <= max_tau + 2 {
        return (None, 0.0);
    }

    let energy = segment.iter().map(|sample| sample * sample).sum::<f32>() / segment.len() as f32;
    if energy < 0.0000005 {
        return (None, 0.0);
    }

    let mut diff = vec![0.0_f32; max_tau + 1];
    for tau in 1..=max_tau {
        let mut sum = 0.0;
        for index in 0..(segment.len() - tau) {
            let delta = segment[index] - segment[index + tau];
            sum += delta * delta;
        }
        diff[tau] = sum;
    }

    let mut running_sum = 0.0;
    let mut best_tau = 0;
    let mut best_value = f32::INFINITY;
    for (tau, diff_at_tau) in diff.iter().enumerate().take(max_tau + 1).skip(1) {
        running_sum += *diff_at_tau;
        if running_sum == 0.0 {
            continue;
        }
        let value = *diff_at_tau * tau as f32 / running_sum;
        if tau >= min_tau && value < best_value {
            best_value = value;
            best_tau = tau;
        }
    }

    if best_tau == 0 || best_value > 0.28 {
        return (None, 1.0 - best_value.min(1.0));
    }

    let refined_tau = parabolic_tau(&diff, best_tau);
    let frequency = sample_rate as f32 / refined_tau;
    (Some(frequency), 1.0 - best_value.min(1.0))
}

fn parabolic_tau(values: &[f32], tau: usize) -> f32 {
    if tau == 0 || tau + 1 >= values.len() {
        return tau as f32;
    }
    let left = values[tau - 1];
    let center = values[tau];
    let right = values[tau + 1];
    let denominator = left - 2.0 * center + right;
    if denominator.abs() < 0.000001 {
        tau as f32
    } else {
        tau as f32 + 0.5 * (left - right) / denominator
    }
}

fn hann(index: usize, len: usize) -> f32 {
    if len <= 1 {
        return 1.0;
    }
    0.5 - 0.5 * (2.0 * std::f32::consts::PI * index as f32 / (len - 1) as f32).cos()
}

fn normalize_soft(samples: &mut [f32], ceiling: f32) {
    let peak = samples
        .iter()
        .fold(0.0_f32, |peak, sample| peak.max(sample.abs()));
    let ceiling = ceiling.clamp(0.1, 1.0);
    if peak > ceiling {
        let gain = ceiling / peak;
        for sample in samples {
            *sample *= gain;
        }
    }
}

fn add_render_diagnostics(samples: &[f32], config: &TunerConfig, report: &mut TuningReport) {
    report.peak = samples
        .iter()
        .fold(0.0_f32, |peak, sample| peak.max(sample.abs()));
    report.rms = if samples.is_empty() {
        0.0
    } else {
        (samples.iter().map(|sample| sample * sample).sum::<f32>() / samples.len() as f32).sqrt()
    };
    report.clipped_samples = samples
        .iter()
        .filter(|sample| sample.abs() >= 0.999)
        .count();

    if report.frames == 0 {
        report
            .warnings
            .push("no analysis frames produced".to_string());
    }
    let voiced_ratio = if report.frames == 0 {
        0.0
    } else {
        report.voiced_frames as f32 / report.frames as f32
    };
    if voiced_ratio < config.min_voiced_ratio {
        report.warnings.push(format!(
            "low voiced-frame ratio: {:.1}% below {:.1}% target",
            voiced_ratio * 100.0,
            config.min_voiced_ratio * 100.0
        ));
    }
    if report.clipped_samples > 0 {
        report.warnings.push(format!(
            "{} clipped samples detected",
            report.clipped_samples
        ));
    }
    if report.peak > config.output_ceiling + 0.001 {
        report.warnings.push(format!(
            "output peak {:.3} exceeded ceiling {:.3}",
            report.peak, config.output_ceiling
        ));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::music::Key;

    #[test]
    fn detects_basic_sine_pitch() {
        let sample_rate = 48_000;
        let frequency = 220.0;
        let samples: Vec<f32> = (0..4096)
            .map(|i| {
                (2.0 * std::f32::consts::PI * frequency * i as f32 / sample_rate as f32).sin() * 0.5
            })
            .collect();
        let (pitch, confidence) = detect_pitch_yin(&samples, sample_rate, 70.0, 900.0);

        assert!(confidence > 0.7);
        assert!((pitch.unwrap() - frequency).abs() < 2.0);
    }

    #[test]
    fn tuning_reports_voiced_frames() {
        let sample_rate = 48_000;
        let frequency = 230.0;
        let samples: Vec<f32> = (0..sample_rate / 2)
            .map(|i| {
                (2.0 * std::f32::consts::PI * frequency * i as f32 / sample_rate as f32).sin() * 0.3
            })
            .collect();
        let audio = AudioBuffer {
            sample_rate,
            channels: 1,
            samples,
        };
        let config = TunerConfig {
            key: Key::parse("A", "minor").unwrap(),
            retune_speed: 1.0,
            humanize: 0.0,
            preserve_vibrato: 0.0,
            ..TunerConfig::default()
        };

        let (tuned, report) = tune(&audio, &config);
        assert_eq!(tuned.samples.len(), audio.samples.len());
        assert!(report.voiced_frames > 10);
        assert!(report.max_correction_cents > 1.0);
    }

    #[test]
    fn pitch_shifter_moves_sine_toward_ratio() {
        let sample_rate = 48_000;
        let source_frequency = 230.0;
        let target_frequency = 220.0;
        let samples: Vec<f32> = (0..4096)
            .map(|i| {
                (2.0 * std::f32::consts::PI * source_frequency * i as f32 / sample_rate as f32)
                    .sin()
                    * 0.4
            })
            .collect();

        let shifted = pitch_shift_segment(
            &samples,
            target_frequency / source_frequency,
            source_frequency,
            sample_rate,
        );
        let (pitch, _) = detect_pitch_yin(&shifted, sample_rate, 70.0, 900.0);

        let detected = pitch.unwrap();
        assert!(
            (detected - target_frequency).abs() < 5.0,
            "detected {detected}, expected {target_frequency}"
        );
    }

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

    #[test]
    fn streaming_tuner_keeps_constant_state_size() {
        let sample_rate = 48_000;
        let mut tuner = StreamingTuner::new(sample_rate, TunerConfig::default());
        let block = vec![0.0_f32; 512];

        for _ in 0..100 {
            let output = tuner.process_block(&block);
            assert_eq!(output.len(), block.len());
        }

        assert!(tuner.smoothed_ratio.is_finite());
    }
}
