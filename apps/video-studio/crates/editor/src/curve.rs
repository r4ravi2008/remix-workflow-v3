use crate::{Result, StudioError};
use serde::{Deserialize, Serialize};

fn invalid(detail: impl Into<String>) -> StudioError {
    StudioError::new("invalid_picture_motion", detail)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CurveInterpolation {
    Step,
    Linear,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CurveKey<T> {
    pub frame: u64,
    pub value: T,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub to_next: Option<CurveInterpolation>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PropertyCurve<T> {
    pub keys: Vec<CurveKey<T>>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum PlannedCurve<T> {
    Constant { value: T },
    Keyed { keys: Vec<CurveKey<T>> },
}

pub(crate) fn validate_keys<T>(keys: &[CurveKey<T>], clip_frames: u64) -> Result<()> {
    if keys.is_empty()
        || keys.len() as u64 > clip_frames
        || keys.first().is_none_or(|key| key.frame != 0)
    {
        return Err(invalid(
            "A curve must start at local frame zero and contain at least one key",
        ));
    }
    for (index, key) in keys.iter().enumerate() {
        if key.frame >= clip_frames
            || (index != 0 && keys[index - 1].frame >= key.frame)
            || key.to_next.is_some() != (index + 1 < keys.len())
        {
            return Err(invalid(
                "Curve frames must increase within the clip; only nonfinal keys specify interpolation",
            ));
        }
    }
    Ok(())
}

pub(crate) fn normalized<T: Clone + Eq>(
    keys: Option<Vec<CurveKey<T>>>,
    base: T,
) -> PlannedCurve<T> {
    match keys {
        Some(keys) if keys.iter().any(|key| key.value != keys[0].value) => {
            PlannedCurve::Keyed { keys }
        }
        Some(keys) => PlannedCurve::Constant {
            value: keys[0].value.clone(),
        },
        None => PlannedCurve::Constant { value: base },
    }
}

pub(crate) fn normalize_property<T: Clone + Eq>(
    curve: Option<&PropertyCurve<T>>,
    base: T,
    clip_frames: u64,
) -> Result<PlannedCurve<T>> {
    let keys = curve
        .map(|curve| -> Result<Vec<CurveKey<T>>> {
            validate_keys(&curve.keys, clip_frames)?;
            Ok(curve.keys.clone())
        })
        .transpose()?;
    Ok(normalized(keys, base))
}

pub(crate) fn round_ratio_nearest_away(numerator: i128, denominator: u64) -> Result<i128> {
    if denominator == 0 {
        return Err(invalid("Curve interpolation denominator must be positive"));
    }
    let divisor = i128::from(denominator);
    let quotient = numerator / divisor;
    let remainder = numerator % divisor;
    if remainder.unsigned_abs() >= u128::from(denominator).div_ceil(2) {
        quotient
            .checked_add(numerator.signum())
            .ok_or_else(|| invalid("Curve interpolation overflow"))
    } else {
        Ok(quotient)
    }
}

pub(crate) trait Scalar: Clone {
    fn wide(&self) -> i128;
    fn narrow(value: i128) -> Result<Self>;
}

impl Scalar for i32 {
    fn wide(&self) -> i128 {
        i128::from(*self)
    }
    fn narrow(value: i128) -> Result<Self> {
        Self::try_from(value).map_err(|_| invalid("Motion position exceeds signed integer bounds"))
    }
}

impl Scalar for u32 {
    fn wide(&self) -> i128 {
        i128::from(*self)
    }
    fn narrow(value: i128) -> Result<Self> {
        Self::try_from(value).map_err(|_| invalid("Motion extent exceeds unsigned integer bounds"))
    }
}

pub(crate) fn evaluate<T: Scalar>(curve: &PlannedCurve<T>, frame: u64) -> Result<T> {
    let keys = match curve {
        PlannedCurve::Constant { value } => return Ok(value.clone()),
        PlannedCurve::Keyed { keys } => keys,
    };
    let end = keys.partition_point(|key| key.frame <= frame);
    let left = end
        .checked_sub(1)
        .and_then(|index| keys.get(index))
        .ok_or_else(|| invalid("Motion frame precedes the first key"))?;
    let Some(right) = keys.get(end) else {
        return Ok(left.value.clone());
    };
    match left.to_next {
        Some(CurveInterpolation::Step) => Ok(left.value.clone()),
        Some(CurveInterpolation::Linear) => {
            let length = right
                .frame
                .checked_sub(left.frame)
                .filter(|length| *length != 0)
                .ok_or_else(|| invalid("Motion key interval is invalid"))?;
            let elapsed = frame - left.frame;
            let numerator = left
                .value
                .wide()
                .checked_mul(i128::from(length))
                .and_then(|base| {
                    right
                        .value
                        .wide()
                        .checked_sub(left.value.wide())?
                        .checked_mul(i128::from(elapsed))?
                        .checked_add(base)
                })
                .ok_or_else(|| invalid("Motion interpolation arithmetic overflow"))?;
            T::narrow(round_ratio_nearest_away(numerator, length)?)
        }
        None => Err(invalid("Motion segment lacks interpolation")),
    }
}
