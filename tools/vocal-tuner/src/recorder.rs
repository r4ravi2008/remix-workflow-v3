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

    pub fn preflight(dry_path: Option<&PathBuf>, wet_path: Option<&PathBuf>) -> Result<(), String> {
        if let Some(path) = dry_path {
            validate_recording_path(path, "dry")?;
        }
        if let Some(path) = wet_path {
            validate_recording_path(path, "wet")?;
        }
        Ok(())
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

fn validate_recording_path(path: &PathBuf, label: &str) -> Result<(), String> {
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .map(|_| ())
        .map_err(|err| {
            format!(
                "failed to create {label} recording {}: {err}",
                path.display()
            )
        })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn records_dry_and_wet_samples_independently() {
        let mut recorder =
            LiveRecorder::new(48_000, Some("dry.wav".into()), Some("wet.wav".into()));

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

    #[test]
    fn preflight_rejects_unwritable_recording_path() {
        let path = std::env::temp_dir()
            .join(format!("vocal-tuner-missing-{}", std::process::id()))
            .join("dry.wav");

        let err = LiveRecorder::preflight(Some(&path), None).unwrap_err();

        assert!(err.contains("dry recording"));
        assert!(err.contains(&path.display().to_string()));
    }
}
