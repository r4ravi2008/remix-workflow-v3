use serde::{Deserialize, Serialize};

use crate::composition::{Bounds, PictureWindow};
use crate::curve::{self, Scalar};
use crate::{OpacityQ16, PlannedCurve, PropertyCurve, Result, StudioError};

const ONE: u32 = 65536;

fn invalid(detail: impl Into<String>) -> StudioError {
    StudioError::new("invalid_picture_mask", detail)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MaskAxis {
    Horizontal,
    Vertical,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(try_from = "f64", into = "f64")]
pub struct MaskProgress(f64);

impl MaskProgress {
    pub fn new(value: f64) -> Result<Self> {
        if !value.is_finite() || !(0.0..=1.0).contains(&value) {
            return Err(invalid(
                "Mask progress must be finite and within zero and one",
            ));
        }
        Ok(Self(value))
    }
    pub fn value(self) -> f64 {
        self.0
    }
    fn quantized(self) -> MaskProgressQ16 {
        MaskProgressQ16((self.0 * f64::from(ONE)).round() as u32)
    }
}
impl TryFrom<f64> for MaskProgress {
    type Error = StudioError;
    fn try_from(value: f64) -> Result<Self> {
        Self::new(value)
    }
}
impl From<MaskProgress> for f64 {
    fn from(value: MaskProgress) -> Self {
        value.0
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress: PropertyCurve<MaskProgress>,
        inverted: bool,
    },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "u32", into = "u32")]
pub struct MaskProgressQ16(u32);

impl MaskProgressQ16 {
    pub fn new(value: u32) -> Result<Self> {
        if value > ONE {
            return Err(invalid("Q16 mask progress exceeds 65536"));
        }
        Ok(Self(value))
    }
    pub fn value(self) -> u32 {
        self.0
    }
}
impl TryFrom<u32> for MaskProgressQ16 {
    type Error = StudioError;
    fn try_from(value: u32) -> Result<Self> {
        Self::new(value)
    }
}
impl From<MaskProgressQ16> for u32 {
    fn from(value: MaskProgressQ16) -> Self {
        value.0
    }
}
impl Scalar for MaskProgressQ16 {
    fn wide(&self) -> i128 {
        i128::from(self.0)
    }
    fn narrow(value: i128) -> Result<Self> {
        Self::new(
            u32::try_from(value).map_err(|_| invalid("Mask interpolation exceeds Q16 range"))?,
        )
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PlannedPictureMask {
    AxisReveal {
        axis: MaskAxis,
        progress_q16: PlannedCurve<MaskProgressQ16>,
        inverted: bool,
    },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct ResolvedPictureMask {
    pub axis: MaskAxis,
    pub progress_q16: MaskProgressQ16,
    pub inverted: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub(crate) struct CoverageQ16(u32);
impl CoverageQ16 {
    pub(crate) fn value(self) -> u32 {
        self.0
    }
}

pub(crate) fn normalize_mask_cancellable(
    author: &PictureMask,
    clip_frames: u64,
    mut check: impl FnMut() -> Result<()>,
) -> Result<PlannedPictureMask> {
    check()?;
    if clip_frames == 0 || clip_frames > crate::model::MAX_TIMELINE_FRAMES {
        return Err(invalid("Mask clip length exceeds the timeline frame limit"));
    }
    let PictureMask::AxisReveal {
        axis,
        progress,
        inverted,
    } = author;
    curve::validate_keys(&progress.keys, clip_frames).map_err(|error| invalid(error.detail))?;
    let keys = progress
        .keys
        .iter()
        .map(|key| {
            check()?;
            Ok(crate::CurveKey {
                frame: key.frame,
                value: key.value.quantized(),
                to_next: key.to_next,
            })
        })
        .collect::<Result<Vec<_>>>()?;
    let first = keys[0].value;
    Ok(PlannedPictureMask::AxisReveal {
        axis: *axis,
        progress_q16: curve::normalized(Some(keys), first),
        inverted: *inverted,
    })
}

impl PlannedPictureMask {
    pub(crate) fn evaluate(&self, frame: u64) -> Result<ResolvedPictureMask> {
        let Self::AxisReveal {
            axis,
            progress_q16,
            inverted,
        } = self;
        Ok(ResolvedPictureMask {
            axis: *axis,
            progress_q16: curve::evaluate(progress_q16, frame)?,
            inverted: *inverted,
        })
    }
}

pub(crate) fn resolve_mask(
    use_: &crate::VideoUse,
    local_frame: u64,
) -> Result<Option<ResolvedPictureMask>> {
    if local_frame >= use_.timeline_frames.length {
        return Err(invalid("Mask frame exceeds its clip interval"));
    }
    use_.mask
        .as_ref()
        .map(|mask| mask.evaluate(local_frame))
        .transpose()
}

pub(crate) fn coverage_q16(
    mask: &ResolvedPictureMask,
    window: &PictureWindow,
    x: u32,
    y: u32,
) -> Result<CoverageQ16> {
    let (origin, length, coordinate) = match mask.axis {
        MaskAxis::Horizontal => (window.x, window.width, x),
        MaskAxis::Vertical => (window.y, window.height, y),
    };
    if length == 0 {
        return Err(invalid(
            "Mask picture window must have a positive axis length",
        ));
    }
    let offset = i128::from(coordinate) - i128::from(origin);
    let edge = i128::from(mask.progress_q16.value())
        .checked_mul(i128::from(length))
        .and_then(|edge| {
            offset
                .checked_mul(i128::from(ONE))
                .and_then(|offset| edge.checked_sub(offset))
        })
        .ok_or_else(|| invalid("Mask coverage arithmetic overflow"))?;
    let coverage = edge.clamp(0, i128::from(ONE)) as u32;
    Ok(CoverageQ16(if mask.inverted {
        ONE - coverage
    } else {
        coverage
    }))
}

pub(crate) fn effective_weight(opacity: OpacityQ16, coverage: CoverageQ16) -> Result<OpacityQ16> {
    let weight = (u64::from(opacity.weight()) * u64::from(coverage.value()) + u64::from(ONE / 2))
        / u64::from(ONE);
    OpacityQ16::new(weight as u32)
}

pub(crate) fn effective_bounds(
    mask: &ResolvedPictureMask,
    window: &PictureWindow,
    bounds: Option<&Bounds>,
    opacity: OpacityQ16,
) -> Result<Option<Bounds>> {
    let Some(bounds) = bounds else {
        return Ok(None);
    };
    let (start, length) = match mask.axis {
        MaskAxis::Horizontal => (bounds.x, bounds.width),
        MaskAxis::Vertical => (bounds.y, bounds.height),
    };
    let end = start
        .checked_add(length)
        .ok_or_else(|| invalid("Mask bounds overflow"))?;
    let positive = |coordinate| {
        let (x, y) = match mask.axis {
            MaskAxis::Horizontal => (coordinate, bounds.y),
            MaskAxis::Vertical => (bounds.x, coordinate),
        };
        Ok::<_, StudioError>(
            effective_weight(opacity, coverage_q16(mask, window, x, y)?)?.weight() != 0,
        )
    };
    let (mut low, mut high) = (start, end);
    while low < high {
        let middle = low + (high - low) / 2;
        let before_boundary = if mask.inverted {
            !positive(middle)?
        } else {
            positive(middle)?
        };
        if before_boundary {
            low = middle + 1;
        } else {
            high = middle;
        }
    }
    let (first, last) = if mask.inverted {
        (low, end)
    } else {
        (start, low)
    };
    if first == last {
        return Ok(None);
    }
    let mut clipped = bounds.clone();
    match mask.axis {
        MaskAxis::Horizontal => {
            clipped.x = first;
            clipped.width = last - first;
        }
        MaskAxis::Vertical => {
            clipped.y = first;
            clipped.height = last - first;
        }
    }
    Ok(Some(clipped))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn independent_curves_quantization_coverage_and_exhaustive_bounds_match() {
        let vectors: serde_json::Value = serde_json::from_slice(include_bytes!(
            "../tests/fixtures/masks/evaluation-vectors-a01.json"
        ))
        .unwrap();
        for control in vectors["quantization_controls"].as_array().unwrap() {
            assert_eq!(
                MaskProgress::new(control["input"].as_f64().unwrap())
                    .unwrap()
                    .quantized()
                    .value(),
                control["expected_q16"].as_u64().unwrap() as u32
            );
        }
        for case in vectors["cases"].as_array().unwrap() {
            let author: PictureMask = serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":case["axis"],"progress":case["progress"],"inverted":case["inverted"]})).unwrap();
            let planned =
                normalize_mask_cancellable(&author, case["clip_frames"].as_u64().unwrap(), || {
                    Ok(())
                })
                .unwrap();
            let w = &case["window"];
            let window = PictureWindow {
                x: w["x"].as_i64().unwrap(),
                y: w["y"].as_i64().unwrap(),
                width: w["width"].as_u64().unwrap() as u32,
                height: w["height"].as_u64().unwrap() as u32,
            };
            let opacity = OpacityQ16::new(case["opacity_q16"].as_u64().unwrap() as u32).unwrap();
            for expected in case["expected"].as_array().unwrap() {
                let resolved = planned
                    .evaluate(expected["frame"].as_u64().unwrap())
                    .unwrap();
                assert_eq!(
                    resolved.progress_q16.value(),
                    expected["progress_q16"].as_u64().unwrap() as u32
                );
                let bounds: Option<Bounds> = if expected["visible_bounds"].is_null() {
                    None
                } else {
                    let b = &expected["visible_bounds"];
                    Some(Bounds {
                        x: b["x"].as_u64().unwrap() as u32,
                        y: b["y"].as_u64().unwrap() as u32,
                        width: b["width"].as_u64().unwrap() as u32,
                        height: b["height"].as_u64().unwrap() as u32,
                    })
                };
                let mut positive = Vec::new();
                for pixel in expected["pixels"].as_array().unwrap() {
                    let (x, y) = (
                        pixel["x"].as_u64().unwrap() as u32,
                        pixel["y"].as_u64().unwrap() as u32,
                    );
                    let coverage = coverage_q16(&resolved, &window, x, y).unwrap();
                    assert_eq!(
                        coverage.value(),
                        pixel["coverage_q16"].as_u64().unwrap() as u32
                    );
                    let effective = effective_weight(opacity, coverage).unwrap().weight();
                    assert_eq!(effective, pixel["effective_q16"].as_u64().unwrap() as u32);
                    if effective != 0 {
                        positive.push((x, y));
                    }
                }
                let expected_bounds = (!positive.is_empty()).then(|| {
                    let x = positive.iter().map(|p| p.0).min().unwrap();
                    let y = positive.iter().map(|p| p.1).min().unwrap();
                    Bounds {
                        x,
                        y,
                        width: positive.iter().map(|p| p.0).max().unwrap() - x + 1,
                        height: positive.iter().map(|p| p.1).max().unwrap() - y + 1,
                    }
                });
                assert_eq!(
                    effective_bounds(&resolved, &window, bounds.as_ref(), opacity).unwrap(),
                    expected_bounds,
                    "{} frame{}",
                    case["name"],
                    expected["frame"]
                );
            }
        }
    }

    #[test]
    fn malformed_masks_and_cancellation_are_rejected() {
        for value in [
            serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[]},"inverted":false}),
            serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":1,"value":0.5}]},"inverted":false}),
        ] {
            let mask: PictureMask = serde_json::from_value(value).unwrap();
            assert!(normalize_mask_cancellable(&mask, 2, || Ok(())).is_err());
        }
        assert!(serde_json::from_str::<MaskProgressQ16>("65537").is_err());
        assert!(serde_json::from_str::<MaskProgressQ16>("true").is_err());
        assert!(MaskProgress::new(f64::NAN).is_err());
        let mask: PictureMask = serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":0,"value":0.0}]},"inverted":false})).unwrap();
        assert_eq!(
            normalize_mask_cancellable(&mask, 1, || Err(StudioError::new(
                "export_cancelled",
                "test"
            )))
            .unwrap_err()
            .code,
            "export_cancelled"
        );
    }
}
