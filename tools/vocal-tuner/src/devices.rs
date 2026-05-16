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
    for device in devices
        .iter()
        .filter(|device| device.kind == DeviceKind::Input)
    {
        let marker = if device.is_default { " (default)" } else { "" };
        println!("  {}{}", device.name, marker);
    }
    println!("Output devices:");
    for device in devices
        .iter()
        .filter(|device| device.kind == DeviceKind::Output)
    {
        let marker = if device.is_default { " (default)" } else { "" };
        println!("  {}{}", device.name, marker);
    }
    if devices.is_empty() && is_wslg_audio_available() {
        println!();
        println!(
            "WSLg PulseAudio is present, but ALSA reported no devices. Install libasound2-plugins, alsa-utils, and pulseaudio-utils, then rerun vocal-tuner devices."
        );
    }
    Ok(())
}

pub fn list_devices() -> Result<Vec<DeviceInfo>, DeviceError> {
    let host = cpal::default_host();
    let default_input = host
        .default_input_device()
        .and_then(|device| device.name().ok());
    let default_output = host
        .default_output_device()
        .and_then(|device| device.name().ok());
    let mut devices = Vec::new();

    let inputs = host
        .input_devices()
        .map_err(|err| DeviceError(format!("failed to list input devices: {err}")))?;
    for device in inputs {
        let name = device
            .name()
            .unwrap_or_else(|_| "<unknown input>".to_string());
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
        let name = device
            .name()
            .unwrap_or_else(|_| "<unknown output>".to_string());
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
            .ok_or_else(|| {
                DeviceError(format!(
                    "no default {kind} device found; run vocal-tuner devices"
                ))
            });
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

fn is_wslg_audio_available() -> bool {
    std::path::Path::new("/mnt/wslg/PulseServer").exists()
}

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

        let selected =
            select_device_name(&devices, DeviceKind::Input, "Scarlett Solo USB").unwrap();
        assert_eq!(selected, "Scarlett Solo USB");
    }

    #[test]
    fn rejects_missing_name_with_devices_hint() {
        let devices = vec![DeviceInfo::new("Built-in Mic", DeviceKind::Input, true)];

        let err = select_device_name(&devices, DeviceKind::Input, "Missing Mic").unwrap_err();
        assert!(err.to_string().contains("Missing Mic"));
        assert!(err.to_string().contains("vocal-tuner devices"));
    }
}
