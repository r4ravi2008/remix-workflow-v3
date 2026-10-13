use serde::{Deserialize, Serialize};
use std::sync::{
    Arc,
    atomic::{AtomicU64, Ordering},
};

use crate::{ExportPlan, Framing, PictureFit, Result, StudioError, pixels};

const WEIGHT_ONE: u32 = 65536;
pub(crate) const MAX_TRACKS: usize = 4;
pub(crate) const MAX_ADMITTED_BYTES: u64 = 512 * 1024 * 1024;

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PixelRect {
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
}

impl PixelRect {
    pub(crate) fn validate(&self) -> Result<()> {
        pixels::extent(self.width, self.height)?;
        Ok(())
    }
    pub(crate) fn canvas(width: u32, height: u32) -> Self {
        Self {
            x: 0,
            y: 0,
            width,
            height,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(try_from = "f64", into = "f64")]
pub struct Opacity(f64);

impl Opacity {
    pub fn new(value: f64) -> Result<Self> {
        if !value.is_finite() || !(0.0..=1.0).contains(&value) {
            return Err(StudioError::new(
                "invalid_opacity",
                "Opacity must be finite and within zero and one",
            ));
        }
        Ok(Self(value))
    }
    pub fn value(self) -> f64 {
        self.0
    }
    pub(crate) fn weight(self) -> u32 {
        (self.0 * f64::from(WEIGHT_ONE)).round() as u32
    }
}
impl TryFrom<f64> for Opacity {
    type Error = StudioError;
    fn try_from(value: f64) -> Result<Self> {
        Self::new(value)
    }
}
impl From<Opacity> for f64 {
    fn from(value: Opacity) -> Self {
        value.0
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PicturePlacement {
    pub destination: PixelRect,
    pub opacity: Opacity,
}
impl PicturePlacement {
    pub(crate) fn validate(&self) -> Result<()> {
        self.destination.validate()
    }
    pub(crate) fn canvas(width: u32, height: u32) -> Self {
        Self {
            destination: PixelRect::canvas(width, height),
            opacity: Opacity(1.0),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Bounds {
    pub x: u32,
    pub y: u32,
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct PictureWindow {
    pub x: i64,
    pub y: i64,
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct LayerObservation {
    pub placement: crate::motion::ResolvedPlacement,
    pub mask: Option<crate::mask::ResolvedPictureMask>,
    pub picture_window: Option<PictureWindow>,
    pub effective_bounds: Option<Bounds>,
}
impl Bounds {
    fn bytes(&self) -> Result<u64> {
        Ok(pixels::extent(self.width, self.height)? as u64)
    }
}

pub(crate) struct Mapping {
    pub bounds: Option<Bounds>,
    window: Option<PictureWindow>,
    crop_x: f64,
    crop_y: f64,
    scale_x: f64,
    scale_y: f64,
    left: f64,
    top: f64,
    min_x: f64,
    max_x: f64,
    min_y: f64,
    max_y: f64,
    source_width: u32,
    source_height: u32,
}

pub(crate) struct BilinearFootprintQ16 {
    pub(crate) x0: u32,
    pub(crate) x1: u32,
    pub(crate) y0: u32,
    pub(crate) y1: u32,
    fx: u32,
    fy: u32,
}

impl BilinearFootprintQ16 {
    pub(crate) fn weights(&self) -> [u64; 4] {
        let one = u64::from(WEIGHT_ONE);
        let fx = u64::from(self.fx);
        let fy = u64::from(self.fy);
        [
            (one - fx) * (one - fy),
            fx * (one - fy),
            (one - fx) * fy,
            fx * fy,
        ]
    }
}

impl Mapping {
    pub(crate) fn validate_source_extent(&self, width: u32, height: u32) -> Result<()> {
        if width != self.source_width || height != self.source_height {
            return Err(StudioError::new(
                "unsupported_picture_alpha",
                "Picture source extent differs from its immutable mapping",
            ));
        }
        Ok(())
    }

    pub(crate) fn new(
        source_width: u32,
        source_height: u32,
        framing: Option<&Framing>,
        placement: &PicturePlacement,
        canvas_width: u32,
        canvas_height: u32,
    ) -> Result<Self> {
        placement.validate()?;
        pixels::extent(source_width, source_height)?;
        pixels::extent(canvas_width, canvas_height)?;
        let destination = &placement.destination;
        let (sw, sh) = (f64::from(source_width), f64::from(source_height));
        let (dw, dh) = (f64::from(destination.width), f64::from(destination.height));
        let (crop_x, crop_y, cw, ch, fit) = if let Some(framing) = framing {
            framing.validate_source_extent(source_width, source_height)?;
            let crop = &framing.crop;
            (
                crop.x * sw,
                crop.y * sh,
                crop.width * sw,
                crop.height * sh,
                &framing.fit,
            )
        } else {
            if source_width != destination.width || source_height != destination.height {
                return Err(StudioError::new(
                    "explicit_framing_required",
                    "Different source and destination dimensions require explicit framing",
                ));
            }
            (0.0, 0.0, sw, sh, &PictureFit::Stretch)
        };
        let (scale_x, scale_y) = match fit {
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
        let dx = f64::from(destination.x);
        let dy = f64::from(destination.y);
        let left = dx + (dw - cw * scale_x) / 2.0;
        let top = dy + (dh - ch * scale_y) / 2.0;
        let intersection = |content_start: f64,
                            content_end: f64,
                            destination_start: f64,
                            destination_size: f64| {
            let begin = (content_start.max(destination_start) - 0.5).ceil() as i64;
            let end = (content_end.min(destination_start + destination_size) - 0.5).ceil() as i64;
            (begin, end)
        };
        let (start_x, end_x) = intersection(left, left + cw * scale_x, dx, dw);
        let (start_y, end_y) = intersection(top, top + ch * scale_y, dy, dh);
        let window = if start_x < end_x && start_y < end_y {
            Some(PictureWindow {
                x: start_x,
                y: start_y,
                width: u32::try_from(end_x - start_x).map_err(|_| {
                    StudioError::new("invalid_layer_window", "Picture window width overflow")
                })?,
                height: u32::try_from(end_y - start_y).map_err(|_| {
                    StudioError::new("invalid_layer_window", "Picture window height overflow")
                })?,
            })
        } else {
            None
        };
        let x = start_x.clamp(0, i64::from(canvas_width)) as u32;
        let right = end_x.clamp(0, i64::from(canvas_width)) as u32;
        let y = start_y.clamp(0, i64::from(canvas_height)) as u32;
        let bottom = end_y.clamp(0, i64::from(canvas_height)) as u32;
        let bounds = (x < right && y < bottom && placement.opacity.weight() != 0).then(|| Bounds {
            x,
            y,
            width: right - x,
            height: bottom - y,
        });
        let min_x = (crop_x - 0.5).ceil().clamp(0.0, sw - 1.0);
        let min_y = (crop_y - 0.5).ceil().clamp(0.0, sh - 1.0);
        Ok(Self {
            bounds,
            window,
            crop_x,
            crop_y,
            scale_x,
            scale_y,
            left,
            top,
            min_x,
            min_y,
            max_x: ((crop_x + cw - 0.5).ceil() - 1.0).clamp(min_x, sw - 1.0),
            max_y: ((crop_y + ch - 0.5).ceil() - 1.0).clamp(min_y, sh - 1.0),
            source_width,
            source_height,
        })
    }

    #[cfg(test)]
    pub(crate) fn rasterize(&self, source: &pixels::Pixels) -> Result<Option<Raster>> {
        self.rasterize_cancellable(source, || Ok(()))
    }

    pub(crate) fn rasterize_cancellable(
        &self,
        source: &pixels::Pixels,
        check: impl FnMut() -> Result<()>,
    ) -> Result<Option<Raster>> {
        self.rasterize_bounds_cancellable(source, self.bounds.as_ref(), check)
    }

    pub(crate) fn rasterize_bounds_cancellable(
        &self,
        source: &pixels::Pixels,
        bounds: Option<&Bounds>,
        mut check: impl FnMut() -> Result<()>,
    ) -> Result<Option<Raster>> {
        check()?;
        self.validate_source_extent(source.width, source.height)?;
        if source.bytes.len() != pixels::extent(source.width, source.height)?
            || source.bytes.chunks_exact(4).any(|pixel| pixel[3] != 255)
        {
            return Err(StudioError::new(
                "unsupported_picture_alpha",
                "Picture layers require complete opaque BGRA input",
            ));
        }
        let Some(bounds) = bounds else {
            return Ok(None);
        };
        self.validate_requested_bounds(bounds)?;
        let mut bytes = vec![0; bounds.bytes()? as usize];
        for y in 0..bounds.height {
            check()?;
            let sy = (self.crop_y + (f64::from(bounds.y + y) + 0.5 - self.top) / self.scale_y
                - 0.5)
                .clamp(self.min_y, self.max_y);
            let y0 = sy.floor() as u32;
            let y1 = (y0 + 1).min(self.max_y as u32);
            let fy = sy - f64::from(y0);
            for x in 0..bounds.width {
                let sx = (self.crop_x + (f64::from(bounds.x + x) + 0.5 - self.left) / self.scale_x
                    - 0.5)
                    .clamp(self.min_x, self.max_x);
                let x0 = sx.floor() as u32;
                let x1 = (x0 + 1).min(self.max_x as u32);
                let fx = sx - f64::from(x0);
                let output = ((y * bounds.width + x) * 4) as usize;
                for channel in 0..3 {
                    let at = |xx: u32, yy: u32| {
                        f64::from(source.bytes[((yy * source.width + xx) * 4) as usize + channel])
                    };
                    let a = at(x0, y0) * (1.0 - fx) + at(x1, y0) * fx;
                    let b = at(x0, y1) * (1.0 - fx) + at(x1, y1) * fx;
                    bytes[output + channel] =
                        (a * (1.0 - fy) + b * fy).round().clamp(0.0, 255.0) as u8;
                }
                bytes[output + 3] = 255;
            }
        }
        Ok(Some(Raster {
            bounds: bounds.clone(),
            bytes,
        }))
    }

    pub(crate) fn validate_requested_bounds(&self, bounds: &Bounds) -> Result<()> {
        if self.bounds.as_ref().is_none_or(|visible| {
            bounds.x < visible.x
                || bounds.y < visible.y
                || bounds.width == 0
                || bounds.height == 0
                || bounds
                    .x
                    .checked_add(bounds.width)
                    .is_none_or(|end| end > visible.x + visible.width)
                || bounds
                    .y
                    .checked_add(bounds.height)
                    .is_none_or(|end| end > visible.y + visible.height)
        }) {
            return Err(StudioError::new(
                "invalid_layer_raster",
                "Requested raster differs from visible source bounds",
            ));
        }
        Ok(())
    }

    pub(crate) fn bilinear_footprint_q16(
        &self,
        canvas_x: u32,
        canvas_y: u32,
    ) -> Result<BilinearFootprintQ16> {
        let visible = self.bounds.as_ref().ok_or_else(|| {
            StudioError::new(
                "invalid_layer_raster",
                "Picture mapping has no visible bounds",
            )
        })?;
        if canvas_x < visible.x
            || canvas_y < visible.y
            || canvas_x >= visible.x + visible.width
            || canvas_y >= visible.y + visible.height
        {
            return Err(StudioError::new(
                "invalid_layer_raster",
                "Sample coordinate differs from visible picture bounds",
            ));
        }
        let sy = (self.crop_y + (f64::from(canvas_y) + 0.5 - self.top) / self.scale_y - 0.5)
            .clamp(self.min_y, self.max_y);
        let sx = (self.crop_x + (f64::from(canvas_x) + 0.5 - self.left) / self.scale_x - 0.5)
            .clamp(self.min_x, self.max_x);
        let x0 = sx.floor() as u32;
        let y0 = sy.floor() as u32;
        let quantize = |fraction: f64| {
            (fraction * f64::from(WEIGHT_ONE))
                .round()
                .clamp(0.0, f64::from(WEIGHT_ONE)) as u32
        };
        Ok(BilinearFootprintQ16 {
            x0,
            x1: (x0 + 1).min(self.max_x as u32),
            y0,
            y1: (y0 + 1).min(self.max_y as u32),
            fx: quantize(sx - f64::from(x0)),
            fy: quantize(sy - f64::from(y0)),
        })
    }
}

pub(crate) struct Raster {
    pub bounds: Bounds,
    pub bytes: Vec<u8>,
}

pub(crate) fn evaluate_layer(
    plan: &ExportPlan,
    use_: &crate::VideoUse,
    local_frame: u64,
    source_width: u32,
    source_height: u32,
) -> Result<(Mapping, LayerObservation)> {
    let placement = crate::motion::resolve(use_, local_frame)?;
    let mapping = Mapping::new(
        source_width,
        source_height,
        use_.framing.as_ref(),
        &placement.as_static()?,
        plan.settings.width,
        plan.settings.height,
    )?;
    let mask = crate::mask::resolve_mask(use_, local_frame)?;
    let effective_bounds = match (&mask, &mapping.window) {
        (Some(mask), Some(window)) => crate::mask::effective_bounds(
            mask,
            window,
            mapping.bounds.as_ref(),
            placement.opacity_q16,
        )?,
        (Some(_), None) => None,
        (None, _) => mapping.bounds.clone(),
    };
    let observation = LayerObservation {
        placement,
        mask,
        picture_window: mapping.window.clone(),
        effective_bounds,
    };
    Ok((mapping, observation))
}

pub(crate) struct Budget {
    used: AtomicU64,
    maximum: AtomicU64,
    limit: u64,
}
impl Budget {
    pub(crate) fn new(limit: u64) -> Arc<Self> {
        Arc::new(Self {
            used: AtomicU64::new(0),
            maximum: AtomicU64::new(0),
            limit,
        })
    }
    pub(crate) fn reserve(self: &Arc<Self>, bytes: u64) -> Result<Permit> {
        let mut used = self.used.load(Ordering::Acquire);
        loop {
            let next = used
                .checked_add(bytes)
                .filter(|next| *next <= self.limit)
                .ok_or_else(|| {
                    StudioError::new(
                        "picture_budget_exhausted",
                        "Logical picture payload reservation exceeds admitted policy",
                    )
                })?;
            match self
                .used
                .compare_exchange_weak(used, next, Ordering::AcqRel, Ordering::Acquire)
            {
                Ok(_) => {
                    self.maximum.fetch_max(next, Ordering::AcqRel);
                    return Ok(Permit {
                        budget: self.clone(),
                        bytes,
                    });
                }
                Err(current) => used = current,
            }
        }
    }
    pub(crate) fn maximum(&self) -> u64 {
        self.maximum.load(Ordering::Acquire)
    }
    #[cfg(test)]
    pub(crate) fn current(&self) -> u64 {
        self.used.load(Ordering::Acquire)
    }
}
pub(crate) struct Permit {
    budget: Arc<Budget>,
    bytes: u64,
}
impl Drop for Permit {
    fn drop(&mut self) {
        self.budget.used.fetch_sub(self.bytes, Ordering::AcqRel);
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PictureExecutionEvidence {
    pub schema: u32,
    pub track_workers: usize,
    pub composed_frames: u64,
    pub peak_active_sources: usize,
    pub admitted_payload_bytes: u64,
    pub maximum_reserved_payload_bytes: u64,
    pub scope: String,
}
#[cfg(test)]
pub(crate) fn blend(canvas: &mut pixels::Pixels, raster: &Raster, opacity: Opacity) -> Result<()> {
    blend_cancellable(canvas, raster, opacity, || Ok(()))
}

#[cfg(test)]
pub(crate) fn blend_cancellable(
    canvas: &mut pixels::Pixels,
    raster: &Raster,
    opacity: Opacity,
    check: impl FnMut() -> Result<()>,
) -> Result<()> {
    let weight = opacity.weight();
    blend_with_weights(canvas, raster, |_, _| Ok(weight), check).map(|_| ())
}

pub(crate) fn blend_layer_cancellable(
    canvas: &mut pixels::Pixels,
    raster: &Raster,
    observation: &LayerObservation,
    check: impl FnMut() -> Result<()>,
) -> Result<u64> {
    if observation.effective_bounds.as_ref() != Some(&raster.bounds) {
        return Err(StudioError::new(
            "invalid_layer_raster",
            "Layer raster differs from resolved effective bounds",
        ));
    }
    let Some(mask) = &observation.mask else {
        let weight = observation.placement.as_static()?.opacity.weight();
        return blend_with_weights(canvas, raster, |_, _| Ok(weight), check);
    };
    let window = observation.picture_window.as_ref().ok_or_else(|| {
        StudioError::new(
            "invalid_layer_raster",
            "Masked raster has no picture window",
        )
    })?;
    blend_with_weights(
        canvas,
        raster,
        |x, y| {
            Ok(crate::mask::effective_weight(
                observation.placement.opacity_q16,
                crate::mask::coverage_q16(mask, window, x, y)?,
            )?
            .weight())
        },
        check,
    )
}

pub(crate) fn layer_weight(observation: &LayerObservation, x: u32, y: u32) -> Result<u32> {
    let Some(mask) = &observation.mask else {
        return Ok(observation.placement.as_static()?.opacity.weight());
    };
    let window = observation.picture_window.as_ref().ok_or_else(|| {
        StudioError::new(
            "invalid_layer_raster",
            "Masked raster has no picture window",
        )
    })?;
    Ok(crate::mask::effective_weight(
        observation.placement.opacity_q16,
        crate::mask::coverage_q16(mask, window, x, y)?,
    )?
    .weight())
}

fn blend_with_weights(
    canvas: &mut pixels::Pixels,
    raster: &Raster,
    weight_at: impl Fn(u32, u32) -> Result<u32>,
    mut check: impl FnMut() -> Result<()>,
) -> Result<u64> {
    check()?;
    let bounds = &raster.bounds;
    if canvas.bytes.len() != pixels::extent(canvas.width, canvas.height)?
        || bounds
            .x
            .checked_add(bounds.width)
            .is_none_or(|end| end > canvas.width)
        || bounds
            .y
            .checked_add(bounds.height)
            .is_none_or(|end| end > canvas.height)
        || raster.bytes.len() as u64 != bounds.bytes()?
        || raster.bytes.chunks_exact(4).any(|pixel| pixel[3] != 255)
    {
        return Err(StudioError::new(
            "invalid_layer_raster",
            "Layer pixels or bounds differ from the opaque canvas",
        ));
    }
    let mut positive = 0u64;
    for y in 0..bounds.height {
        check()?;
        for x in 0..bounds.width {
            let input = ((y * bounds.width + x) * 4) as usize;
            let output = (((bounds.y + y) * canvas.width + bounds.x + x) * 4) as usize;
            let weight = weight_at(bounds.x + x, bounds.y + y)?;
            positive += u64::from(weight != 0);
            for channel in 0..3 {
                canvas.bytes[output + channel] = ((u32::from(raster.bytes[input + channel])
                    * weight
                    + u32::from(canvas.bytes[output + channel]) * (WEIGHT_ONE - weight)
                    + WEIGHT_ONE / 2)
                    / WEIGHT_ONE) as u8;
            }
            canvas.bytes[output + 3] = 255;
        }
    }
    Ok(positive)
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub(crate) struct Admission {
    pub tracks: usize,
    pub peak_active_sources: usize,
    pub estimated_bytes: u64,
}

#[cfg(test)]
pub(crate) fn preflight(plan: &ExportPlan) -> Result<Admission> {
    preflight_cancellable(plan, || Ok(()))
}

pub(crate) fn preflight_cancellable(
    plan: &ExportPlan,
    mut check: impl FnMut() -> Result<()>,
) -> Result<Admission> {
    crate::plan::validate_picture_mapping_cancellable(plan, &mut check)?;
    let tracks = plan
        .timeline
        .video_tracks
        .iter()
        .filter(|track| !track.clips.is_empty())
        .count();
    if tracks == 0 || tracks > MAX_TRACKS {
        return Err(StudioError::new(
            "unsupported_picture_tracks",
            "Layer execution requires one to four nonempty picture tracks",
        ));
    }
    let canvas = pixels::extent(plan.settings.width, plan.settings.height)? as u64;
    let mut events = Vec::new();
    let mut frame_charges = vec![0u64; plan.timeline.frame_count as usize];
    let mut frame_sources = vec![0usize; plan.timeline.frame_count as usize];
    let mut coverage = vec![false; plan.timeline.frame_count as usize];
    let mut png_temporary = 0u64;
    for use_ in &plan.video {
        check()?;
        let asset = &plan.source_closure[&use_.asset];
        let (width, height) = asset.descriptor.picture_extent()?;
        let source_bytes = pixels::extent(width, height)? as u64;
        let end = use_.timeline_frames.end()?;
        if end > plan.timeline.frame_count
            || use_.presentation_ordinals.len() as u64 != use_.timeline_frames.length
        {
            return Err(StudioError::new(
                "invalid_layer_plan",
                "Layer span or source map differs from timeline extent",
            ));
        }
        let dynamic = matches!(plan.schema, 5..=7);
        let alpha = match &asset.descriptor {
            crate::MediaDescriptor::Image { alpha, .. } => alpha.as_ref(),
            _ => None,
        };
        let local_frames = if dynamic {
            use_.timeline_frames.length
        } else {
            1
        };
        for local in 0..local_frames {
            check()?;
            let (_, observation) = evaluate_layer(plan, use_, local, width, height)?;
            let raster_bytes = observation
                .effective_bounds
                .as_ref()
                .map_or(Ok(0), |bounds| {
                    if alpha.is_some() {
                        crate::alpha_picture::raster_bytes(bounds)
                    } else {
                        bounds.bytes()
                    }
                })?;
            let potential_coverage = raster_bytes != 0
                && alpha.is_none_or(|measurement| measurement.nonzero_pixels != 0);
            let charge = source_bytes.checked_add(raster_bytes).ok_or_else(|| {
                StudioError::new(
                    "picture_budget_overflow",
                    "Source and raster charge overflow",
                )
            })?;
            if dynamic {
                let frame = (use_.timeline_frames.start + local) as usize;
                frame_charges[frame] =
                    frame_charges[frame].checked_add(charge).ok_or_else(|| {
                        StudioError::new("picture_budget_overflow", "Frame charge overflow")
                    })?;
                frame_sources[frame] += 1;
                coverage[frame] |= potential_coverage;
            } else {
                events.push((use_.timeline_frames.start, i128::from(charge), 1i64));
                events.push((end, -i128::from(charge), -1i64));
                if potential_coverage {
                    coverage[use_.timeline_frames.start as usize..end as usize].fill(true);
                }
            }
        }
        if matches!(asset.descriptor, crate::MediaDescriptor::Image { .. }) {
            let reserve = source_bytes
                .checked_add(asset.bytes)
                .and_then(|value| value.checked_add(pixels::MAX_OWNED_FRAME_BYTES))
                .ok_or_else(|| {
                    StudioError::new("picture_budget_overflow", "PNG decoder charge overflow")
                })?;
            png_temporary = png_temporary.max(reserve);
        }
    }
    if coverage.contains(&false) {
        return Err(StudioError::new(
            "video_coverage",
            "Visible layer content does not cover every output frame",
        ));
    }
    events.sort_by_key(|event| event.0);
    let (mut current, mut active, mut peak, mut peak_active) = (0i128, 0i64, 0i128, 0i64);
    let mut next = 0;
    while next < events.len() {
        let frame = events[next].0;
        while next < events.len() && events[next].0 == frame {
            current += events[next].1;
            active += events[next].2;
            next += 1;
        }
        if current < 0 || active < 0 {
            return Err(StudioError::new(
                "invalid_layer_plan",
                "Layer admission sweep has invalid extents",
            ));
        }
        peak = peak.max(current);
        peak_active = peak_active.max(active);
    }
    if matches!(plan.schema, 5..=7) {
        peak = i128::from(frame_charges.into_iter().max().unwrap_or(0));
        peak_active = frame_sources.into_iter().max().unwrap_or(0) as i64;
    }
    let estimated_bytes = canvas
        .checked_mul(3)
        .and_then(|value| value.checked_add(u64::try_from(peak).ok()?))
        .and_then(|value| value.checked_add(png_temporary))
        .ok_or_else(|| {
            StudioError::new(
                "picture_budget_overflow",
                "Picture admission estimate overflow",
            )
        })?;
    if estimated_bytes > MAX_ADMITTED_BYTES {
        return Err(StudioError::new(
            "unsupported_picture_budget",
            "Layer admission estimate exceeds512MiB; native process memory is a separate measurement",
        ));
    }
    Ok(Admission {
        tracks,
        peak_active_sources: peak_active as usize,
        estimated_bytes,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::NormalizedCrop;

    #[test]
    fn independent_mask_reference_matches_every_preencode_pixel() {
        let vectors: serde_json::Value = serde_json::from_slice(include_bytes!(
            "../tests/fixtures/masks/pixel-vectors-a01.json"
        ))
        .unwrap();
        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema5.json"))
                .unwrap();
        plan.settings.width = vectors["canvas"]["width"].as_u64().unwrap() as u32;
        plan.settings.height = vectors["canvas"]["height"].as_u64().unwrap() as u32;
        for expected in vectors["expected"].as_array().unwrap() {
            let frame = expected["frame"].as_u64().unwrap();
            let background: Vec<u8> =
                serde_json::from_value(vectors["canvas"]["background"].clone()).unwrap();
            let mut canvas = pixels::Pixels {
                width: plan.settings.width,
                height: plan.settings.height,
                bytes: background.repeat((plan.settings.width * plan.settings.height) as usize),
            };
            for track in vectors["tracks"].as_array().unwrap() {
                for clip in track["clips"].as_array().unwrap() {
                    let start = clip["span"]["start"].as_u64().unwrap();
                    let length = clip["span"]["length"].as_u64().unwrap();
                    if !(start..start + length).contains(&frame) {
                        continue;
                    }
                    let source = &vectors["sources"][clip["source"].as_str().unwrap()];
                    let pixels = pixels::Pixels {
                        width: source["width"].as_u64().unwrap() as u32,
                        height: source["height"].as_u64().unwrap() as u32,
                        bytes: serde_json::from_value(source["bgra"].clone()).unwrap(),
                    };
                    let base: PicturePlacement =
                        serde_json::from_value(clip["base"].clone()).unwrap();
                    let motion = if clip["motion"].is_null() {
                        None
                    } else {
                        Some(
                            crate::motion::normalize_motion(
                                &serde_json::from_value(clip["motion"].clone()).unwrap(),
                                &base,
                                length,
                            )
                            .unwrap(),
                        )
                    };
                    let mask = if clip["mask"].is_null() {
                        None
                    } else {
                        Some(crate::mask::normalize_mask_cancellable(&serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":clip["mask"]["axis"],"progress":clip["mask"]["progress"],"inverted":clip["mask"]["inverted"]})).unwrap(),length,||Ok(())).unwrap())
                    };
                    let use_ = crate::VideoUse {
                        clip: crate::EntityId::parse(clip["id"].as_str().unwrap()).unwrap(),
                        track: crate::EntityId::parse(track["id"].as_str().unwrap()).unwrap(),
                        timeline_frames: crate::Span { start, length },
                        asset: crate::ContentHash::bytes(&pixels.bytes),
                        allowed_source_samples: crate::Span {
                            start: 0,
                            length: 1,
                        },
                        presentation_ordinals: vec![0; length as usize],
                        framing: Some(serde_json::from_value(clip["framing"].clone()).unwrap()),
                        placement: motion.is_none().then_some(base),
                        motion,
                        mask,
                    };
                    let (mapping, observation) =
                        evaluate_layer(&plan, &use_, frame - start, pixels.width, pixels.height)
                            .unwrap();
                    if let Some(raster) = mapping
                        .rasterize_bounds_cancellable(
                            &pixels,
                            observation.effective_bounds.as_ref(),
                            || Ok(()),
                        )
                        .unwrap()
                    {
                        blend_layer_cancellable(&mut canvas, &raster, &observation, || Ok(()))
                            .unwrap();
                    }
                }
            }
            let expected_bytes: Vec<u8> = serde_json::from_value(expected["bgra"].clone()).unwrap();
            assert_eq!(
                canvas.bytes, expected_bytes,
                "independent masked BGRA frame{frame}"
            );
        }
    }

    fn mask_plan() -> ExportPlan {
        let old = motion_plan();
        let mut timeline = old.timeline.clone();
        timeline.video_tracks[1].clips[0].mask = Some(serde_json::from_value(serde_json::json!({"kind":"axis_reveal","axis":"horizontal","progress":{"keys":[{"frame":0,"value":0.5}]},"inverted":false})).unwrap());
        let snapshot = crate::Snapshot {
            schema: 1,
            project: old.project.clone(),
            name: "Mask validation fixture".into(),
            parent: None,
            settings: old.settings.clone(),
            assets: old.source_closure.clone(),
            canonical_audio: old.canonical_audio.clone(),
            timelines: [(timeline.id.clone(), timeline)].into_iter().collect(),
        };
        let request = crate::ExportRequest {
            intent: crate::EntityId::parse("mask-validation").unwrap(),
            revision: crate::ContentHash::document(&snapshot).unwrap(),
            timeline: old.timeline.id,
            profile: old.profile,
        };
        crate::plan::compile(snapshot, &request).unwrap().plan
    }

    #[test]
    fn schema6_recompiles_masks_and_rejects_forged_or_legacy_shapes() {
        let valid = mask_plan();
        assert_eq!(valid.schema, 6);
        crate::plan::validate_picture_mapping(&valid).unwrap();
        preflight(&valid).unwrap();
        let index = valid
            .video
            .iter()
            .position(|use_| use_.mask.is_some())
            .unwrap();
        let mut wrong = valid.clone();
        let crate::PlannedPictureMask::AxisReveal { inverted, .. } =
            wrong.video[index].mask.as_mut().unwrap();
        *inverted = !*inverted;
        assert_eq!(
            crate::plan::validate_picture_mapping(&wrong)
                .unwrap_err()
                .code,
            "invalid_layer_plan"
        );
        wrong = valid.clone();
        wrong.video[index].mask = None;
        assert!(crate::plan::validate_picture_mapping(&wrong).is_err());
        wrong = valid.clone();
        wrong.schema = 5;
        assert!(crate::plan::validate_picture_mapping(&wrong).is_err());
        wrong = valid.clone();
        for track in &mut wrong.timeline.video_tracks {
            for clip in &mut track.clips {
                clip.mask = None;
            }
        }
        assert!(crate::plan::validate_picture_mapping(&wrong).is_err());
        wrong = valid.clone();
        wrong.video[index].presentation_ordinals[0] += 1;
        assert!(crate::plan::validate_picture_mapping(&wrong).is_err());
        let mut source = pixels::Pixels {
            width: 2,
            height: 2,
            bytes: vec![255; 16],
        };
        source.bytes[3] = 254;
        let mapping = Mapping::new(2, 2, None, &PicturePlacement::canvas(2, 2), 2, 2).unwrap();
        assert_eq!(
            mapping
                .rasterize_bounds_cancellable(&source, None, || Ok(()))
                .err()
                .unwrap()
                .code,
            "unsupported_picture_alpha"
        );
    }

    fn motion_plan() -> ExportPlan {
        let old: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema4.json"))
                .unwrap();
        let mut snapshot = crate::Snapshot {
            schema: 1,
            project: old.project.clone(),
            name: "Motion validation fixture".into(),
            parent: None,
            settings: old.settings.clone(),
            assets: old.source_closure.clone(),
            canonical_audio: old.canonical_audio.clone(),
            timelines: [(old.timeline.id.clone(), old.timeline.clone())]
                .into_iter()
                .collect(),
        };
        snapshot
            .timelines
            .get_mut(&old.timeline.id)
            .unwrap()
            .video_tracks[0]
            .clips[0]
            .motion = Some(
            serde_json::from_value(serde_json::json!({
                "x":{"keys":[{"frame":0,"value":0,"to_next":"linear"},{"frame":47,"value":2}]}
            }))
            .unwrap(),
        );
        let request = crate::ExportRequest {
            intent: crate::EntityId::parse("motion-validation").unwrap(),
            revision: crate::ContentHash::document(&snapshot).unwrap(),
            timeline: old.timeline.id,
            profile: old.profile,
        };
        crate::plan::compile(snapshot, &request).unwrap().plan
    }

    #[test]
    fn independent_fraction_reference_matches_every_preencode_bgra_byte() {
        let vectors: serde_json::Value = serde_json::from_slice(include_bytes!(
            "../tests/fixtures/motion/pixel-vectors-a01.json"
        ))
        .unwrap();
        let width = vectors["canvas"]["width"].as_u64().unwrap() as u32;
        let height = vectors["canvas"]["height"].as_u64().unwrap() as u32;
        for frame in 0..vectors["canvas"]["frames"].as_u64().unwrap() {
            let background: Vec<u8> =
                serde_json::from_value(vectors["canvas"]["background"].clone()).unwrap();
            let mut canvas = pixels::Pixels {
                width,
                height,
                bytes: background.repeat((width * height) as usize),
            };
            for track in vectors["tracks"].as_array().unwrap() {
                for clip in track["clips"].as_array().unwrap() {
                    let start = clip["span"]["start"].as_u64().unwrap();
                    let length = clip["span"]["length"].as_u64().unwrap();
                    if !(start..start + length).contains(&frame) {
                        continue;
                    }
                    let base: PicturePlacement =
                        serde_json::from_value(clip["base"].clone()).unwrap();
                    let placement = if clip["motion"].is_null() {
                        base
                    } else {
                        let motion: crate::PictureMotion =
                            serde_json::from_value(clip["motion"].clone()).unwrap();
                        crate::motion::normalize_motion(&motion, &base, length)
                            .unwrap()
                            .evaluate(frame - start)
                            .unwrap()
                            .as_static()
                            .unwrap()
                    };
                    let source = &vectors["sources"][clip["source"].as_str().unwrap()];
                    let source = pixels::Pixels {
                        width: source["width"].as_u64().unwrap() as u32,
                        height: source["height"].as_u64().unwrap() as u32,
                        bytes: serde_json::from_value(source["bgra"].clone()).unwrap(),
                    };
                    let framing: crate::Framing =
                        serde_json::from_value(clip["framing"].clone()).unwrap();
                    let mapping = Mapping::new(
                        source.width,
                        source.height,
                        Some(&framing),
                        &placement,
                        width,
                        height,
                    )
                    .unwrap();
                    if let Some(raster) = mapping.rasterize(&source).unwrap() {
                        blend(&mut canvas, &raster, placement.opacity).unwrap();
                    }
                }
            }
            let expected: Vec<u8> =
                serde_json::from_value(vectors["expected"][frame as usize]["bgra"].clone())
                    .unwrap();
            assert_eq!(canvas.bytes, expected, "pre-encode frame {frame}");
        }
    }

    #[test]
    fn schema5_rejects_forged_motion_source_maps_and_incompatible_legacy_forms() {
        let valid = motion_plan();
        assert_eq!(valid.schema, 5);
        preflight(&valid).unwrap();
        let mut changed = valid.clone();
        changed.video[0].placement = Some(PicturePlacement::canvas(320, 180));
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        changed.video[0].motion = None;
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        changed.video[0].motion.as_mut().unwrap().x = crate::PlannedCurve::Constant { value: 99 };
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        changed.schema = 4;
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        changed.video[0].presentation_ordinals[1] += 1;
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        let crate::MediaDescriptor::Movie { samples, .. } = &mut changed
            .source_closure
            .get_mut(&valid.video[0].asset)
            .unwrap()
            .descriptor
        else {
            panic!("movie expected")
        };
        samples[1].pts.ticks += 1;
        assert!(preflight(&changed).is_err());
        let mut changed = valid.clone();
        changed.timeline.video_tracks[0].clips[0]
            .motion
            .as_mut()
            .unwrap()
            .x
            .as_mut()
            .unwrap()
            .keys[1]
            .frame = 0;
        assert_eq!(
            preflight(&changed).unwrap_err().code,
            "invalid_picture_motion"
        );
        let mut json = serde_json::to_value(&valid).unwrap();
        json["video"][0]["motion"]["opacity_q16"] =
            serde_json::json!({"kind":"constant","value":65537});
        assert!(serde_json::from_value::<ExportPlan>(json).is_err());
    }

    #[test]
    fn preflight_and_each_raster_and_blend_row_observe_cancellation() {
        let plan = motion_plan();
        let control = crate::exports::ExportControl::test_active();
        let mut checks = 0;
        let error = preflight_cancellable(&plan, || {
            checks += 1;
            if checks == 12 {
                control.interrupt();
            }
            control.check()
        })
        .unwrap_err();
        assert_eq!(error.code, "export_interrupted");
        assert_eq!(checks, 12);
        let pixels = source(8, 8, [1, 2, 3, 255]);
        let mapping = Mapping::new(8, 8, None, &placement(0, 0, 8, 8, 1.0), 8, 8).unwrap();
        let mut checks = 0;
        let error = mapping
            .rasterize_cancellable(&pixels, || {
                checks += 1;
                if checks == 4 {
                    Err(crate::StudioError::new("forced_raster_cancel", "test"))
                } else {
                    Ok(())
                }
            })
            .err()
            .unwrap();
        assert_eq!(error.code, "forced_raster_cancel");
        assert_eq!(checks, 4);
        let raster = mapping.rasterize(&pixels).unwrap().unwrap();
        let mut canvas = source(8, 8, [0, 0, 0, 255]);
        let mut checks = 0;
        let error = blend_cancellable(&mut canvas, &raster, Opacity::new(1.0).unwrap(), || {
            checks += 1;
            if checks == 4 {
                Err(crate::StudioError::new("forced_blend_cancel", "test"))
            } else {
                Ok(())
            }
        })
        .unwrap_err();
        assert_eq!(error.code, "forced_blend_cancel");
        assert_eq!(canvas.bytes[..64], pixels.bytes[..64]);
        assert!(
            canvas.bytes[64..]
                .chunks_exact(4)
                .all(|pixel| pixel == [0, 0, 0, 255])
        );
    }

    fn source(width: u32, height: u32, color: [u8; 4]) -> pixels::Pixels {
        pixels::Pixels {
            width,
            height,
            bytes: color.repeat((width * height) as usize),
        }
    }
    fn framing(fit: PictureFit) -> Framing {
        Framing {
            fit,
            crop: NormalizedCrop {
                x: 0.0,
                y: 0.0,
                width: 1.0,
                height: 1.0,
            },
        }
    }
    fn placement(x: i32, y: i32, width: u32, height: u32, opacity: f64) -> PicturePlacement {
        PicturePlacement {
            destination: PixelRect {
                x,
                y,
                width,
                height,
            },
            opacity: Opacity::new(opacity).unwrap(),
        }
    }
    #[test]
    fn contained_overlay_preserves_lower_pixels_and_common_window() {
        let pixels = source(4, 2, [0, 0, 240, 255]);
        let placement = placement(1, 1, 4, 4, 1.0);
        let mapping =
            Mapping::new(4, 2, Some(&framing(PictureFit::Contain)), &placement, 6, 6).unwrap();
        assert_eq!(
            mapping.bounds,
            Some(Bounds {
                x: 1,
                y: 2,
                width: 4,
                height: 2
            })
        );
        let raster = mapping.rasterize(&pixels).unwrap().unwrap();
        let mut canvas = source(6, 6, [19, 80, 7, 255]);
        blend(&mut canvas, &raster, placement.opacity).unwrap();
        for y in 0..6 {
            for x in 0..6 {
                assert_eq!(
                    &canvas.bytes[(y * 6 + x) * 4..(y * 6 + x + 1) * 4],
                    if (1..5).contains(&x) && (2..4).contains(&y) {
                        &[0, 0, 240, 255]
                    } else {
                        &[19, 80, 7, 255]
                    }
                );
            }
        }
        let second =
            Mapping::new(4, 2, Some(&framing(PictureFit::Contain)), &placement, 6, 6).unwrap();
        assert_eq!(second.bounds, mapping.bounds);
    }
    #[test]
    fn signed_and_fifty_pixel_moves_clip_without_rescaling() {
        let mut pixels = source(8, 2, [0, 0, 0, 255]);
        for (index, pixel) in pixels.bytes.chunks_exact_mut(4).enumerate() {
            pixel[0] = (index % 8) as u8 * 20;
        }
        for (x, canvas_width, expected_start, expected_width) in [(-2, 6, 2, 6), (50, 54, 0, 4)] {
            let mapping =
                Mapping::new(8, 2, None, &placement(x, 0, 8, 2, 1.0), canvas_width, 2).unwrap();
            let raster = mapping.rasterize(&pixels).unwrap().unwrap();
            assert_eq!(raster.bounds.width, expected_width);
            for (index, pixel) in raster.bytes.chunks_exact(4).enumerate() {
                assert_eq!(
                    pixel[0],
                    (expected_start + index as u32 % expected_width) as u8 * 20
                );
            }
        }
    }
    #[test]
    fn opacity_endpoints_midpoint_and_track_order_have_exact_bytes() {
        let raster = Raster {
            bounds: Bounds {
                x: 0,
                y: 0,
                width: 1,
                height: 1,
            },
            bytes: vec![240, 20, 0, 255],
        };
        let mut canvas = source(1, 1, [0, 80, 240, 255]);
        blend(&mut canvas, &raster, Opacity::new(0.0).unwrap()).unwrap();
        assert_eq!(canvas.bytes, [0, 80, 240, 255]);
        blend(&mut canvas, &raster, Opacity::new(0.5).unwrap()).unwrap();
        assert_eq!(canvas.bytes, [120, 50, 120, 255]);
        blend(&mut canvas, &raster, Opacity::new(1.0).unwrap()).unwrap();
        assert_eq!(canvas.bytes, [240, 20, 0, 255]);
        let upper = Raster {
            bytes: vec![0, 200, 0, 255],
            ..raster
        };
        blend(&mut canvas, &upper, Opacity::new(0.5).unwrap()).unwrap();
        assert_eq!(canvas.bytes, [120, 110, 0, 255]);
    }
    #[test]
    fn zero_opacity_offscreen_content_and_contain_bars_do_not_claim_coverage() {
        let transparent = placement(0, 0, 10, 10, 0.0);
        assert!(
            Mapping::new(10, 10, None, &transparent, 10, 10)
                .unwrap()
                .bounds
                .is_none()
        );
        let bars_only = placement(0, -90, 10, 100, 1.0);
        assert!(
            Mapping::new(
                100,
                1,
                Some(&framing(PictureFit::Contain)),
                &bars_only,
                10,
                10
            )
            .unwrap()
            .bounds
            .is_none()
        );
        let outside = placement(i32::MAX, i32::MIN, 10, 10, 1.0);
        assert!(
            Mapping::new(10, 10, None, &outside, 10, 10)
                .unwrap()
                .bounds
                .is_none()
        );
    }
    #[test]
    fn crop_edges_alpha_and_wrong_source_extent_are_checked() {
        let mut pixels = source(4, 2, [0, 0, 255, 255]);
        for (index, pixel) in pixels.bytes.chunks_exact_mut(4).enumerate() {
            if index % 4 == 0 || index % 4 == 3 {
                pixel[1] = 255;
            }
        }
        for fit in [PictureFit::Contain, PictureFit::Cover, PictureFit::Stretch] {
            let mut framing = framing(fit);
            framing.crop.x = 0.25;
            framing.crop.width = 0.5;
            let mapping =
                Mapping::new(4, 2, Some(&framing), &placement(-2, 0, 8, 6, 1.0), 6, 6).unwrap();
            let raster = mapping.rasterize(&pixels).unwrap().unwrap();
            assert!(raster.bytes.chunks_exact(4).all(|pixel| pixel[1] == 0));
        }
        let mapping = Mapping::new(4, 2, None, &placement(0, 0, 4, 2, 1.0), 4, 2).unwrap();
        pixels.bytes[3] = 0;
        assert_eq!(
            mapping.rasterize(&pixels).err().unwrap().code,
            "unsupported_picture_alpha"
        );
        assert_eq!(
            mapping
                .rasterize(&source(2, 1, [0, 0, 0, 255]))
                .err()
                .unwrap()
                .code,
            "unsupported_picture_alpha"
        );
        assert!(Opacity::new(f64::NAN).is_err());
        assert!(Opacity::new(f64::INFINITY).is_err());
        assert!(Opacity::new(-0.01).is_err());
        assert!(Opacity::new(1.01).is_err());
        assert!(placement(0, 0, 0, 1, 1.0).validate().is_err());
    }
    #[test]
    fn reservations_enforce_logical_cap_release_and_high_watermark() {
        let budget = Budget::new(64);
        let first = budget.reserve(40).unwrap();
        assert_eq!(budget.maximum(), 40);
        assert_eq!(
            budget.reserve(32).err().unwrap().code,
            "picture_budget_exhausted"
        );
        drop(first);
        let full = budget.reserve(64).unwrap();
        assert_eq!(budget.maximum(), 64);
        drop(full);
        assert_eq!(budget.used.load(Ordering::Acquire), 0);
    }

    #[test]
    fn structural_validation_rejects_forged_uses_before_indexing_or_workers() {
        let mut valid: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema3.json"))
                .unwrap();
        valid.schema = 4;
        for use_ in &mut valid.video {
            use_.placement = Some(PicturePlacement::canvas(
                valid.settings.width,
                valid.settings.height,
            ));
        }
        preflight(&valid).unwrap();
        let mut changed = valid.clone();
        changed.video.clear();
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.video[0].presentation_ordinals[0] = u64::MAX;
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.video[0].clip = crate::EntityId::parse("unlisted-clip").unwrap();
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.video[0].asset = crate::ContentHash::parse("2".repeat(64)).unwrap();
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.video[0].placement.as_mut().unwrap().opacity = Opacity::new(0.5).unwrap();
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.video.push(valid.video[0].clone());
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.audio[0].clip.asset = crate::ContentHash::parse("3".repeat(64)).unwrap();
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid.clone();
        changed.timeline_sample_frames += 1;
        assert_eq!(preflight(&changed).unwrap_err().code, "invalid_layer_plan");
        let mut changed = valid;
        changed.schema = 3;
        assert_eq!(
            crate::plan::validate_picture_mapping(&changed)
                .unwrap_err()
                .code,
            "invalid_layer_plan"
        );
    }
}
