use serde::{Deserialize, Serialize};

#[cfg(test)]
use crate::curve::round_ratio_nearest_away;
pub use crate::curve::{CurveInterpolation, CurveKey, PlannedCurve, PropertyCurve};
use crate::curve::{Scalar, evaluate, normalize_property, normalized, validate_keys};
use crate::{Opacity, PicturePlacement, PixelRect, Result, StudioError};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PictureMotion {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub x: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub y: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub width: Option<PropertyCurve<u32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub height: Option<PropertyCurve<u32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub opacity: Option<PropertyCurve<Opacity>>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "u32", into = "u32")]
pub struct OpacityQ16(u32);

impl OpacityQ16 {
    pub fn new(weight: u32) -> Result<Self> {
        if weight > 65536 {
            return Err(invalid("Q16 opacity must be within zero and 65536"));
        }
        Ok(Self(weight))
    }

    pub fn weight(self) -> u32 {
        self.0
    }
}

impl TryFrom<u32> for OpacityQ16 {
    type Error = StudioError;

    fn try_from(weight: u32) -> Result<Self> {
        Self::new(weight)
    }
}

impl From<OpacityQ16> for u32 {
    fn from(value: OpacityQ16) -> Self {
        value.weight()
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedPictureMotion {
    pub x: PlannedCurve<i32>,
    pub y: PlannedCurve<i32>,
    pub width: PlannedCurve<u32>,
    pub height: PlannedCurve<u32>,
    pub opacity_q16: PlannedCurve<OpacityQ16>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct ResolvedPlacement {
    pub destination: PixelRect,
    pub opacity_q16: OpacityQ16,
}

impl ResolvedPlacement {
    pub(crate) fn from_static(placement: &PicturePlacement) -> Result<Self> {
        placement.validate()?;
        Ok(Self {
            destination: placement.destination.clone(),
            opacity_q16: OpacityQ16::new(placement.opacity.weight())?,
        })
    }

    pub(crate) fn as_static(&self) -> Result<PicturePlacement> {
        Ok(PicturePlacement {
            destination: self.destination.clone(),
            opacity: Opacity::new(f64::from(self.opacity_q16.weight()) / 65536.0)?,
        })
    }
}

fn invalid(detail: impl Into<String>) -> StudioError {
    StudioError::new("invalid_picture_motion", detail)
}

pub(crate) fn normalize_motion(
    motion: &PictureMotion,
    base: &PicturePlacement,
    clip_frames: u64,
) -> Result<PlannedPictureMotion> {
    normalize_motion_cancellable(motion, base, clip_frames, || Ok(()))
}

pub(crate) fn normalize_motion_cancellable(
    motion: &PictureMotion,
    base: &PicturePlacement,
    clip_frames: u64,
    mut check: impl FnMut() -> Result<()>,
) -> Result<PlannedPictureMotion> {
    check()?;
    if clip_frames == 0 || clip_frames > crate::model::MAX_TIMELINE_FRAMES {
        return Err(invalid(
            "Motion clip length must be within the timeline frame limit",
        ));
    }
    if motion.x.is_none()
        && motion.y.is_none()
        && motion.width.is_none()
        && motion.height.is_none()
        && motion.opacity.is_none()
    {
        return Err(invalid(
            "Picture motion must contain at least one property curve",
        ));
    }
    base.validate()?;
    let opacity = motion
        .opacity
        .as_ref()
        .map(|curve| {
            validate_keys(&curve.keys, clip_frames)?;
            curve
                .keys
                .iter()
                .map(|key| {
                    Ok(CurveKey {
                        frame: key.frame,
                        value: OpacityQ16::new(key.value.weight())?,
                        to_next: key.to_next,
                    })
                })
                .collect::<Result<Vec<_>>>()
        })
        .transpose()?;
    let planned = PlannedPictureMotion {
        x: normalize_property(motion.x.as_ref(), base.destination.x, clip_frames)?,
        y: normalize_property(motion.y.as_ref(), base.destination.y, clip_frames)?,
        width: normalize_property(motion.width.as_ref(), base.destination.width, clip_frames)?,
        height: normalize_property(motion.height.as_ref(), base.destination.height, clip_frames)?,
        opacity_q16: normalized(opacity, OpacityQ16::new(base.opacity.weight())?),
    };
    for frame in 0..clip_frames {
        check()?;
        planned.evaluate(frame)?;
    }
    Ok(planned)
}

impl Scalar for OpacityQ16 {
    fn wide(&self) -> i128 {
        i128::from(self.weight())
    }
    fn narrow(value: i128) -> Result<Self> {
        Self::new(u32::try_from(value).map_err(|_| invalid("Motion opacity exceeds Q16 bounds"))?)
    }
}

impl PlannedPictureMotion {
    pub(crate) fn evaluate(&self, local_frame: u64) -> Result<ResolvedPlacement> {
        let resolved = ResolvedPlacement {
            destination: PixelRect {
                x: evaluate(&self.x, local_frame)?,
                y: evaluate(&self.y, local_frame)?,
                width: evaluate(&self.width, local_frame)?,
                height: evaluate(&self.height, local_frame)?,
            },
            opacity_q16: evaluate(&self.opacity_q16, local_frame)?,
        };
        resolved.destination.validate()?;
        Ok(resolved)
    }
}

pub(crate) fn resolve(use_: &crate::VideoUse, local_frame: u64) -> Result<ResolvedPlacement> {
    if local_frame >= use_.timeline_frames.length {
        return Err(invalid("Motion frame exceeds its clip interval"));
    }
    match (&use_.motion, &use_.placement) {
        (Some(motion), None) => motion.evaluate(local_frame),
        (None, Some(placement)) => ResolvedPlacement::from_static(placement),
        _ => Err(invalid(
            "Layer use requires exactly one static placement or motion program",
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_independent_golden_curve_and_rounding_vector_matches() {
        let vectors: serde_json::Value = serde_json::from_slice(include_bytes!(
            "../tests/fixtures/motion/evaluation-vectors-a01.json"
        ))
        .unwrap();
        for round in vectors["rounds"].as_array().unwrap() {
            let numerator: i128 = round["numerator"].as_str().unwrap().parse().unwrap();
            let expected: i128 = round["expected"].as_str().unwrap().parse().unwrap();
            assert_eq!(
                round_ratio_nearest_away(numerator, round["denominator"].as_u64().unwrap())
                    .unwrap(),
                expected
            );
        }
        for case in vectors["cases"].as_array().unwrap() {
            let motion: PictureMotion = serde_json::from_value(case["motion"].clone()).unwrap();
            let base: PicturePlacement = serde_json::from_value(case["base"].clone()).unwrap();
            let planned =
                normalize_motion(&motion, &base, case["clip_frames"].as_u64().unwrap()).unwrap();
            for (frame, expected) in case["expected"].as_array().unwrap().iter().enumerate() {
                let resolved = planned.evaluate(frame as u64).unwrap();
                assert_eq!(
                    serde_json::to_value(resolved.destination).unwrap(),
                    expected["destination"],
                    "{} frame {}",
                    case["name"],
                    frame
                );
                assert_eq!(
                    resolved.opacity_q16.weight(),
                    expected["opacity_q16"].as_u64().unwrap() as u32,
                    "{} frame {}",
                    case["name"],
                    frame
                );
            }
        }
    }

    fn base() -> PicturePlacement {
        PicturePlacement {
            destination: PixelRect {
                x: 0,
                y: 0,
                width: 8,
                height: 4,
            },
            opacity: Opacity::new(1.0).unwrap(),
        }
    }

    fn author(value: serde_json::Value) -> PictureMotion {
        serde_json::from_value(value).unwrap()
    }

    #[test]
    fn signed_rounding_uses_the_complete_value_and_full_integer_bounds() {
        for (numerator, denominator, expected) in [
            (1, 2, 1),
            (-1, 2, -1),
            (3, 2, 2),
            (-3, 2, -2),
            (1, 3, 0),
            (-1, 3, 0),
            (2, 3, 1),
            (-2, 3, -1),
            (i128::MAX, 1, i128::MAX),
            (i128::MIN, 1, i128::MIN),
        ] {
            assert_eq!(
                round_ratio_nearest_away(numerator, denominator).unwrap(),
                expected
            );
        }
        assert!(round_ratio_nearest_away(0, 0).is_err());
        let motion = author(serde_json::json!({"x":{"keys":[
            {"frame":0,"value":i32::MIN,"to_next":"linear"},
            {"frame":3,"value":i32::MAX}
        ]}}));
        let planned = normalize_motion(&motion, &base(), 4).unwrap();
        assert_eq!(
            (0..4)
                .map(|frame| planned.evaluate(frame).unwrap().destination.x)
                .collect::<Vec<_>>(),
            vec![i32::MIN, -715827883, 715827882, i32::MAX]
        );
    }

    #[test]
    fn independent_opacity_keys_do_not_change_position_rounding() {
        let motion = author(serde_json::json!({
            "x":{"keys":[{"frame":0,"value":0,"to_next":"linear"},{"frame":3,"value":2}]},
            "opacity":{"keys":[{"frame":0,"value":0.0,"to_next":"linear"},{"frame":1,"value":0.5,"to_next":"linear"},{"frame":3,"value":1.0}]}
        }));
        let planned = normalize_motion(&motion, &base(), 4).unwrap();
        assert_eq!(
            (0..4)
                .map(|frame| planned.evaluate(frame).unwrap().destination.x)
                .collect::<Vec<_>>(),
            vec![0, 1, 1, 2]
        );
        assert_eq!(
            (0..4)
                .map(|frame| planned.evaluate(frame).unwrap().opacity_q16.weight())
                .collect::<Vec<_>>(),
            vec![0, 32768, 49152, 65536]
        );
    }

    #[test]
    fn step_and_final_hold_accept_short_constant_and_one_frame_programs() {
        let motion = author(
            serde_json::json!({"x":{"keys":[{"frame":0,"value":-50,"to_next":"step"},{"frame":2,"value":50}]}}),
        );
        let planned = normalize_motion(&motion, &base(), 6).unwrap();
        assert_eq!(
            (0..6)
                .map(|frame| planned.evaluate(frame).unwrap().destination.x)
                .collect::<Vec<_>>(),
            vec![-50, -50, 50, 50, 50, 50]
        );
        let constant = author(serde_json::json!({"opacity":{"keys":[{"frame":0,"value":1.0}]}}));
        let planned = normalize_motion(&constant, &base(), 1).unwrap();
        assert_eq!(
            planned.evaluate(0).unwrap(),
            ResolvedPlacement::from_static(&base()).unwrap()
        );
        let roundtrip: PlannedPictureMotion =
            serde_json::from_slice(&serde_json::to_vec(&planned).unwrap()).unwrap();
        assert_eq!(planned, roundtrip);
    }

    #[test]
    fn malformed_authoring_and_resolved_extents_are_rejected() {
        for value in [
            serde_json::json!({}),
            serde_json::json!({"x":{"keys":[]}}),
            serde_json::json!({"x":{"keys":[{"frame":1,"value":0}]}}),
            serde_json::json!({"x":{"keys":[{"frame":0,"value":0,"to_next":"linear"}]}}),
            serde_json::json!({"x":{"keys":[{"frame":0,"value":0},{"frame":1,"value":1}]}}),
            serde_json::json!({"x":{"keys":[{"frame":0,"value":0,"to_next":"linear"},{"frame":0,"value":1}]}}),
            serde_json::json!({"x":{"keys":[{"frame":0,"value":0,"to_next":"linear"},{"frame":4,"value":1}]}}),
            serde_json::json!({"width":{"keys":[{"frame":0,"value":0}]}}),
            serde_json::json!({"width":{"keys":[{"frame":0,"value":u32::MAX}]}}),
        ] {
            assert!(normalize_motion(&author(value), &base(), 4).is_err());
        }
        assert!(
            serde_json::from_value::<PictureMotion>(
                serde_json::json!({"opacity":{"keys":[{"frame":0,"value":1.1}]}})
            )
            .is_err()
        );
        let one = author(serde_json::json!({"x":{"keys":[{"frame":0,"value":0}]}}));
        assert!(normalize_motion(&one, &base(), 0).is_err());
    }

    #[test]
    fn q16_json_is_bounded_integer_and_static_conversion_has_exact_weights() {
        assert!(serde_json::from_str::<OpacityQ16>("65537").is_err());
        assert!(serde_json::from_str::<OpacityQ16>("-1").is_err());
        assert!(serde_json::from_str::<OpacityQ16>("0.5").is_err());
        for weight in [0, 1, 32768, 65535, 65536] {
            let value = OpacityQ16::new(weight).unwrap();
            let bytes = serde_json::to_vec(&value).unwrap();
            assert_eq!(serde_json::from_slice::<OpacityQ16>(&bytes).unwrap(), value);
            let resolved = ResolvedPlacement {
                destination: base().destination,
                opacity_q16: value,
            };
            assert_eq!(resolved.as_static().unwrap().opacity.weight(), weight);
        }
    }
}
