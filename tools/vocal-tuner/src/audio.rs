use std::fmt;

#[derive(Debug, Clone)]
pub struct AudioBuffer {
    pub sample_rate: u32,
    pub channels: u16,
    pub samples: Vec<f32>,
}

impl AudioBuffer {
    pub fn frame_count(&self) -> usize {
        self.samples.len() / self.channels as usize
    }

    pub fn duration_seconds(&self) -> f32 {
        self.frame_count() as f32 / self.sample_rate as f32
    }

    pub fn channel(&self, channel: usize) -> Vec<f32> {
        let channels = self.channels as usize;
        self.samples
            .chunks_exact(channels)
            .map(|frame| frame[channel])
            .collect()
    }

    pub fn from_channels(sample_rate: u32, channel_data: &[Vec<f32>]) -> Self {
        let channels = channel_data.len() as u16;
        let frames = channel_data.first().map_or(0, Vec::len);
        let mut samples = Vec::with_capacity(frames * channels as usize);

        for frame in 0..frames {
            for channel in channel_data {
                samples.push(channel[frame]);
            }
        }

        Self {
            sample_rate,
            channels,
            samples,
        }
    }
}

#[derive(Debug)]
pub enum AudioError {
    Io(std::io::Error),
    Format(String),
    Command(String),
}

impl fmt::Display for AudioError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AudioError::Io(err) => write!(f, "{err}"),
            AudioError::Format(message) => f.write_str(message),
            AudioError::Command(message) => f.write_str(message),
        }
    }
}

impl std::error::Error for AudioError {}

impl From<std::io::Error> for AudioError {
    fn from(value: std::io::Error) -> Self {
        AudioError::Io(value)
    }
}
