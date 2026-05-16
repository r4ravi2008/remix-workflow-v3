use std::fs::File;
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::Path;
use std::process::Command;

use crate::audio::{AudioBuffer, AudioError};

pub fn read_audio(path: &Path) -> Result<AudioBuffer, AudioError> {
    if path
        .extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case("wav"))
    {
        return read_wav(path);
    }

    read_with_ffmpeg(path)
}

pub fn write_audio(path: &Path, audio: &AudioBuffer) -> Result<(), AudioError> {
    if path
        .extension()
        .and_then(|ext| ext.to_str())
        .is_some_and(|ext| ext.eq_ignore_ascii_case("wav"))
    {
        return write_wav(path, audio);
    }

    let wav_path = path.with_extension("vocal-tuner-tmp.wav");
    write_wav(&wav_path, audio)?;
    let status = Command::new("ffmpeg")
        .arg("-y")
        .arg("-hide_banner")
        .arg("-loglevel")
        .arg("error")
        .arg("-i")
        .arg(&wav_path)
        .arg(path)
        .status()
        .map_err(|err| AudioError::Command(format!("failed to run ffmpeg: {err}")))?;
    let _ = std::fs::remove_file(&wav_path);

    if status.success() {
        Ok(())
    } else {
        Err(AudioError::Command(format!(
            "ffmpeg failed while encoding {}",
            path.display()
        )))
    }
}

fn read_with_ffmpeg(path: &Path) -> Result<AudioBuffer, AudioError> {
    let tmp = std::env::temp_dir().join(format!("vocal-tuner-{}-decode.wav", std::process::id()));
    let status = Command::new("ffmpeg")
        .arg("-y")
        .arg("-hide_banner")
        .arg("-loglevel")
        .arg("error")
        .arg("-i")
        .arg(path)
        .arg("-ar")
        .arg("48000")
        .arg("-acodec")
        .arg("pcm_f32le")
        .arg(&tmp)
        .status()
        .map_err(|err| AudioError::Command(format!("failed to run ffmpeg: {err}")))?;

    if !status.success() {
        return Err(AudioError::Command(format!(
            "ffmpeg failed while decoding {}",
            path.display()
        )));
    }

    let decoded = read_wav(&tmp);
    let _ = std::fs::remove_file(tmp);
    decoded
}

pub fn read_wav(path: &Path) -> Result<AudioBuffer, AudioError> {
    let mut file = File::open(path)?;
    let mut riff = [0_u8; 12];
    file.read_exact(&mut riff)?;
    if &riff[0..4] != b"RIFF" || &riff[8..12] != b"WAVE" {
        return Err(AudioError::Format("not a RIFF/WAVE file".to_string()));
    }

    let mut channels = 0_u16;
    let mut sample_rate = 0_u32;
    let mut bits_per_sample = 0_u16;
    let mut audio_format = 0_u16;
    let mut data = Vec::new();

    loop {
        let mut header = [0_u8; 8];
        match file.read_exact(&mut header) {
            Ok(()) => {}
            Err(err) if err.kind() == std::io::ErrorKind::UnexpectedEof => break,
            Err(err) => return Err(err.into()),
        }
        let chunk_size = u32::from_le_bytes(header[4..8].try_into().unwrap()) as usize;
        match &header[0..4] {
            b"fmt " => {
                let mut fmt = vec![0_u8; chunk_size];
                file.read_exact(&mut fmt)?;
                if fmt.len() < 16 {
                    return Err(AudioError::Format("invalid fmt chunk".to_string()));
                }
                audio_format = u16::from_le_bytes([fmt[0], fmt[1]]);
                channels = u16::from_le_bytes([fmt[2], fmt[3]]);
                sample_rate = u32::from_le_bytes([fmt[4], fmt[5], fmt[6], fmt[7]]);
                bits_per_sample = u16::from_le_bytes([fmt[14], fmt[15]]);
            }
            b"data" => {
                data.resize(chunk_size, 0);
                file.read_exact(&mut data)?;
            }
            _ => {
                file.seek(SeekFrom::Current(chunk_size as i64))?;
            }
        }

        if chunk_size % 2 == 1 {
            file.seek(SeekFrom::Current(1))?;
        }
    }

    if channels == 0 || sample_rate == 0 || data.is_empty() {
        return Err(AudioError::Format("missing WAV audio data".to_string()));
    }

    let samples = decode_samples(audio_format, bits_per_sample, &data)?;
    Ok(AudioBuffer {
        sample_rate,
        channels,
        samples,
    })
}

pub fn write_wav(path: &Path, audio: &AudioBuffer) -> Result<(), AudioError> {
    let mut file = File::create(path)?;
    let data_bytes = audio.samples.len() * 4;
    let riff_size = 4 + (8 + 16) + (8 + data_bytes);
    let byte_rate = audio.sample_rate * audio.channels as u32 * 4;
    let block_align = audio.channels * 4;

    file.write_all(b"RIFF")?;
    file.write_all(&(riff_size as u32).to_le_bytes())?;
    file.write_all(b"WAVE")?;
    file.write_all(b"fmt ")?;
    file.write_all(&16_u32.to_le_bytes())?;
    file.write_all(&3_u16.to_le_bytes())?;
    file.write_all(&audio.channels.to_le_bytes())?;
    file.write_all(&audio.sample_rate.to_le_bytes())?;
    file.write_all(&byte_rate.to_le_bytes())?;
    file.write_all(&block_align.to_le_bytes())?;
    file.write_all(&32_u16.to_le_bytes())?;
    file.write_all(b"data")?;
    file.write_all(&(data_bytes as u32).to_le_bytes())?;
    for sample in &audio.samples {
        file.write_all(&sample.clamp(-1.0, 1.0).to_le_bytes())?;
    }
    Ok(())
}

fn decode_samples(format: u16, bits: u16, data: &[u8]) -> Result<Vec<f32>, AudioError> {
    match (format, bits) {
        (1, 16) => Ok(data
            .chunks_exact(2)
            .map(|chunk| i16::from_le_bytes([chunk[0], chunk[1]]) as f32 / i16::MAX as f32)
            .collect()),
        (1, 24) => Ok(data
            .chunks_exact(3)
            .map(|chunk| {
                let value = i32::from_le_bytes([
                    chunk[0],
                    chunk[1],
                    chunk[2],
                    if chunk[2] & 0x80 == 0 { 0 } else { 0xff },
                ]);
                value as f32 / 8_388_607.0
            })
            .collect()),
        (1, 32) => Ok(data
            .chunks_exact(4)
            .map(|chunk| i32::from_le_bytes(chunk.try_into().unwrap()) as f32 / i32::MAX as f32)
            .collect()),
        (3, 32) => Ok(data
            .chunks_exact(4)
            .map(|chunk| f32::from_le_bytes(chunk.try_into().unwrap()).clamp(-1.0, 1.0))
            .collect()),
        other => Err(AudioError::Format(format!(
            "unsupported WAV format: format={}, bits={}",
            other.0, other.1
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn writes_and_reads_float_wav() {
        let path =
            std::env::temp_dir().join(format!("vocal-tuner-test-{}.wav", std::process::id()));
        let audio = AudioBuffer {
            sample_rate: 48_000,
            channels: 1,
            samples: vec![0.0, 0.25, -0.25, 0.5, -0.5],
        };

        write_wav(&path, &audio).unwrap();
        let decoded = read_wav(&path).unwrap();
        let _ = std::fs::remove_file(path);

        assert_eq!(decoded.sample_rate, 48_000);
        assert_eq!(decoded.channels, 1);
        assert_eq!(decoded.samples.len(), audio.samples.len());
        assert!((decoded.samples[3] - 0.5).abs() < 0.0001);
    }
}
