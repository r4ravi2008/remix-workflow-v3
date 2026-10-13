use serde::{Deserialize, Serialize};

use crate::{Result, StudioError};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Framing {
    pub fit: PictureFit,
    pub crop: NormalizedCrop,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PictureFit {
    Contain,
    Cover,
    Stretch,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NormalizedCrop {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
}

impl Framing {
    pub(crate) fn validate(&self) -> Result<()> {
        let crop = &self.crop;
        if [crop.x, crop.y, crop.width, crop.height]
            .iter()
            .any(|v| !v.is_finite())
            || crop.x < 0.0
            || crop.y < 0.0
            || crop.width <= 0.0
            || crop.height <= 0.0
            || crop.width > 1.0 - crop.x
            || crop.height > 1.0 - crop.y
            || crop.x > 1.0 - crop.width
            || crop.y > 1.0 - crop.height
        {
            return Err(StudioError::new(
                "invalid_framing",
                "Crop must be a finite positive rectangle inside the source",
            ));
        }
        Ok(())
    }
    pub(crate) fn validate_source_extent(&self, width: u32, height: u32) -> Result<()> {
        self.validate()?;
        let cropped_width = self.crop.width * f64::from(width);
        let cropped_height = self.crop.height * f64::from(height);
        if !cropped_width.is_finite()
            || !cropped_height.is_finite()
            || cropped_width < 1.0
            || cropped_height < 1.0
        {
            return Err(StudioError::new(
                "invalid_framing",
                "Crop must retain at least one source pixel in each dimension",
            ));
        }
        Ok(())
    }
}

pub(crate) fn apply(
    source: crate::pixels::Pixels,
    framing: Option<&Framing>,
    width: u32,
    height: u32,
) -> Result<crate::pixels::Pixels> {
    let Some(framing) = framing else {
        if source.width != width || source.height != height {
            return Err(StudioError::new(
                "explicit_framing_required",
                "Different source and canvas dimensions require an explicit framing operation",
            ));
        }
        return Ok(source);
    };
    framing.validate_source_extent(source.width, source.height)?;
    let size = crate::pixels::extent(width, height)?;
    if source.width == 0
        || source.height == 0
        || source.bytes.len() as u64 != u64::from(source.width) * u64::from(source.height) * 4
    {
        return Err(StudioError::new(
            "pixel_extent",
            "Unsupported framed canvas or source extent",
        ));
    }
    let crop = &framing.crop;
    let (sw, sh) = (f64::from(source.width), f64::from(source.height));
    let (cw, ch) = (crop.width * sw, crop.height * sh);
    let (dw, dh) = (f64::from(width), f64::from(height));
    let (scale_x, scale_y) = match framing.fit {
        PictureFit::Contain => {
            let scale = (dw / cw).min(dh / ch);
            (scale, scale)
        }
        PictureFit::Cover => {
            let scale = (dw / cw).max(dh / ch);
            (scale, scale)
        }
        PictureFit::Stretch => (dw / cw, dh / ch),
    };
    let (left, top) = ((dw - cw * scale_x) / 2.0, (dh - ch * scale_y) / 2.0);
    let min_x = (crop.x * sw - 0.5).ceil().clamp(0.0, sw - 1.0);
    let min_y = (crop.y * sh - 0.5).ceil().clamp(0.0, sh - 1.0);
    let max_x = (((crop.x + crop.width) * sw - 0.5).ceil() - 1.0).clamp(min_x, sw - 1.0);
    let max_y = (((crop.y + crop.height) * sh - 0.5).ceil() - 1.0).clamp(min_y, sh - 1.0);
    let mut bytes = vec![0; size];
    for pixel in bytes.chunks_exact_mut(4) {
        pixel[3] = 255;
    }
    for y in 0..height {
        let local_y = (f64::from(y) + 0.5 - top) / scale_y;
        if !(0.0..ch).contains(&local_y) {
            continue;
        }
        let sy = (crop.y * sh + local_y - 0.5).clamp(min_y, max_y);
        let y0 = sy.floor() as u32;
        let y1 = (y0 + 1).min(max_y as u32);
        let fy = sy - f64::from(y0);
        for x in 0..width {
            let local_x = (f64::from(x) + 0.5 - left) / scale_x;
            if !(0.0..cw).contains(&local_x) {
                continue;
            }
            let sx = (crop.x * sw + local_x - 0.5).clamp(min_x, max_x);
            let x0 = sx.floor() as u32;
            let x1 = (x0 + 1).min(max_x as u32);
            let fx = sx - f64::from(x0);
            for channel in 0..4 {
                let at = |xx: u32, yy: u32| {
                    f64::from(source.bytes[((yy * source.width + xx) * 4) as usize + channel])
                };
                let a = at(x0, y0) * (1.0 - fx) + at(x1, y0) * fx;
                let b = at(x0, y1) * (1.0 - fx) + at(x1, y1) * fx;
                bytes[((y * width + x) * 4) as usize + channel] =
                    (a * (1.0 - fy) + b * fy).round().clamp(0.0, 255.0) as u8;
            }
        }
    }
    Ok(crate::pixels::Pixels {
        width,
        height,
        bytes,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    fn crop() -> NormalizedCrop {
        NormalizedCrop {
            x: 0.0,
            y: 0.0,
            width: 1.0,
            height: 1.0,
        }
    }
    fn solid() -> crate::pixels::Pixels {
        crate::pixels::Pixels {
            width: 4,
            height: 2,
            bytes: [7, 19, 239, 255].repeat(8),
        }
    }
    #[test]
    fn contain_preserves_aspect_and_places_black_bars_on_the_canvas() {
        let frame = apply(
            solid(),
            Some(&Framing {
                fit: PictureFit::Contain,
                crop: crop(),
            }),
            4,
            4,
        )
        .unwrap();
        for y in 0..4 {
            for x in 0..4 {
                assert_eq!(
                    &frame.bytes[(y * 4 + x) * 4..(y * 4 + x + 1) * 4],
                    if y == 0 || y == 3 {
                        &[0, 0, 0, 255]
                    } else {
                        &[7, 19, 239, 255]
                    }
                );
            }
        }
    }
    #[test]
    fn crop_rejects_missing_pixels_and_implicit_scaling_is_never_applied() {
        assert_eq!(
            apply(solid(), None, 8, 4).err().unwrap().code,
            "explicit_framing_required"
        );
        assert_eq!(
            Framing {
                fit: PictureFit::Cover,
                crop: NormalizedCrop {
                    width: 2.0,
                    ..crop()
                }
            }
            .validate()
            .unwrap_err()
            .code,
            "invalid_framing"
        );
        assert_eq!(
            Framing {
                fit: PictureFit::Stretch,
                crop: NormalizedCrop {
                    width: f64::NAN,
                    ..crop()
                }
            }
            .validate()
            .unwrap_err()
            .code,
            "invalid_framing"
        );
    }
    #[test]
    fn rounded_outside_and_subpixel_crops_are_rejected_before_evaluation() {
        assert_eq!(
            Framing {
                fit: PictureFit::Cover,
                crop: NormalizedCrop {
                    x: f64::from_bits(1),
                    ..crop()
                }
            }
            .validate()
            .unwrap_err()
            .code,
            "invalid_framing"
        );
        let framing = Framing {
            fit: PictureFit::Cover,
            crop: NormalizedCrop {
                x: 1.0,
                width: f64::from_bits(1),
                ..crop()
            },
        };
        assert_eq!(framing.validate().unwrap_err().code, "invalid_framing");
        let framing = Framing {
            crop: NormalizedCrop {
                x: 0.0,
                ..framing.crop
            },
            ..framing
        };
        assert_eq!(
            framing.validate_source_extent(1920, 1080).unwrap_err().code,
            "invalid_framing"
        );
        assert_eq!(
            apply(solid(), Some(&framing), 4, 4).err().unwrap().code,
            "invalid_framing"
        );
    }
    #[test]
    fn excluded_edge_markers_never_bleed_into_any_fitted_crop() {
        for fit in [PictureFit::Contain, PictureFit::Cover, PictureFit::Stretch] {
            let mut bytes = vec![];
            for _ in 0..2 {
                for x in 0..4 {
                    bytes.extend_from_slice(if x == 0 || x == 3 {
                        &[0, 255, 0, 255]
                    } else {
                        &[0, 0, 255, 255]
                    });
                }
            }
            let source = crate::pixels::Pixels {
                width: 4,
                height: 2,
                bytes,
            };
            let framing = Framing {
                fit,
                crop: NormalizedCrop {
                    x: 0.25,
                    width: 0.5,
                    ..crop()
                },
            };
            let frame = apply(source, Some(&framing), 8, 6).unwrap();
            assert!(frame.bytes.chunks_exact(4).all(|pixel| pixel[1] == 0));
            assert!(frame.bytes.chunks_exact(4).any(|pixel| pixel[2] == 255));
        }
    }
}
