use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::{Result, StudioError};

pub(crate) const MAX_TIMELINE_FRAMES: u64 = 100000;

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct ContentHash(String);

impl ContentHash {
    pub fn parse(value: impl Into<String>) -> Result<Self> {
        let value = value.into();
        if value.len() != 64
            || !value
                .bytes()
                .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
        {
            return Err(StudioError::new(
                "invalid_hash",
                "Expected 64 lowercase hexadecimal characters",
            ));
        }
        Ok(Self(value))
    }
    pub fn as_str(&self) -> &str {
        &self.0
    }
    pub(crate) fn bytes(bytes: &[u8]) -> Self {
        Self(format!("{:x}", Sha256::digest(bytes)))
    }
    pub(crate) fn document(value: &impl Serialize) -> Result<Self> {
        Ok(Self::bytes(&serde_json::to_vec(value)?))
    }
}
impl TryFrom<String> for ContentHash {
    type Error = StudioError;
    fn try_from(v: String) -> Result<Self> {
        Self::parse(v)
    }
}
impl From<ContentHash> for String {
    fn from(v: ContentHash) -> Self {
        v.0
    }
}

#[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct EntityId(String);

impl EntityId {
    pub fn parse(value: impl Into<String>) -> Result<Self> {
        let value = value.into();
        if value.is_empty()
            || value.len() > 128
            || !value
                .bytes()
                .all(|c| c.is_ascii_alphanumeric() || b"-_.".contains(&c))
            || value == "."
            || value == ".."
        {
            return Err(StudioError::new(
                "invalid_id",
                "IDs require 1..128 ASCII letters, digits, hyphens, underscores or dots",
            ));
        }
        Ok(Self(value))
    }
    pub fn as_str(&self) -> &str {
        &self.0
    }
}
impl TryFrom<String> for EntityId {
    type Error = StudioError;
    fn try_from(v: String) -> Result<Self> {
        Self::parse(v)
    }
}
impl From<EntityId> for String {
    fn from(v: EntityId) -> Self {
        v.0
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Rate {
    pub numerator: u32,
    pub denominator: u32,
}
impl Rate {
    pub fn validate(&self) -> Result<()> {
        if self.numerator == 0 || self.denominator == 0 {
            return Err(StudioError::new("invalid_rate", "Rate must be positive"));
        }
        let (mut a, mut b) = (self.numerator, self.denominator);
        while b != 0 {
            (a, b) = (b, a % b);
        }
        if a != 1 {
            return Err(StudioError::new("invalid_rate", "Rate must be reduced"));
        }
        Ok(())
    }
    pub fn samples_at_frame(&self, frame: u64, sample_rate: u32) -> Result<u64> {
        self.validate()?;
        let value = u128::from(frame) * u128::from(self.denominator) * u128::from(sample_rate);
        let divisor = u128::from(self.numerator);
        if value % divisor != 0 {
            return Err(StudioError::new(
                "fractional_sample_boundary",
                "Frame boundary does not map to an integer sample",
            ));
        }
        u64::try_from(value / divisor)
            .map_err(|_| StudioError::new("time_overflow", "Sample boundary overflow"))
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Span {
    pub start: u64,
    pub length: u64,
}
impl Span {
    pub fn end(&self) -> Result<u64> {
        if self.length == 0 {
            return Err(StudioError::new(
                "empty_range",
                "Range length must be positive",
            ));
        }
        self.start
            .checked_add(self.length)
            .ok_or_else(|| StudioError::new("time_overflow", "Range endpoint overflow"))
    }
    pub(crate) fn within(&self, limit: u64) -> Result<()> {
        if self.end()? > limit {
            return Err(StudioError::new(
                "source_bounds",
                "Range exceeds measured source or timeline extent",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct MediaTime {
    pub ticks: i64,
    pub timescale: u32,
}
impl MediaTime {
    pub(crate) fn compare(&self, other: &Self) -> std::cmp::Ordering {
        (i128::from(self.ticks) * i128::from(other.timescale))
            .cmp(&(i128::from(other.ticks) * i128::from(self.timescale)))
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Settings {
    pub width: u32,
    pub height: u32,
    pub frame_rate: Rate,
    pub audio_rate: u32,
    pub channels: u32,
    pub working_color: String,
}
impl Settings {
    pub(crate) fn validate(&self) -> Result<()> {
        self.frame_rate.validate()?;
        if self.width == 0
            || self.height == 0
            || self.width > 8192
            || self.height > 8192
            || self.audio_rate == 0
            || self.audio_rate > 192000
            || !(1..=8).contains(&self.channels)
            || self.working_color.is_empty()
        {
            return Err(StudioError::new(
                "invalid_settings",
                "Invalid canvas, audio clock, channel count or working color",
            ));
        }
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MediaKind {
    Movie,
    Audio,
    Image,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SourceRange {
    pub asset: ContentHash,
    pub range: Span,
    pub stream: MediaKind,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Origin {
    Imported {
        external_source: String,
        role: String,
    },
    Extracted {
        source: SourceRange,
        recipe: ContentHash,
    },
    Derived {
        inputs: Vec<SourceRange>,
        recipe: ContentHash,
        receipt: ContentHash,
    },
    Generated {
        inputs: Vec<SourceRange>,
        attempt: EntityId,
        workflow: ContentHash,
        model: ContentHash,
        provider_receipt: ContentHash,
        transfer_receipt: ContentHash,
    },
}
impl Origin {
    pub(crate) fn sources(&self) -> Vec<&SourceRange> {
        match self {
            Self::Imported { .. } => Vec::new(),
            Self::Extracted { source, .. } => vec![source],
            Self::Derived { inputs, .. } | Self::Generated { inputs, .. } => {
                inputs.iter().collect()
            }
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AssetImport {
    pub path: PathBuf,
    pub expected_hash: ContentHash,
    pub expected_bytes: u64,
    pub media_kind: MediaKind,
    pub origin: Origin,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub previous_measurement: Option<ContentHash>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SampleTiming {
    pub ordinal: u64,
    pub pts: MediaTime,
    pub dts: Option<MediaTime>,
    pub duration: MediaTime,
    pub sync_sample: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub encoded_time: Option<EncodedTiming>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EncodedTiming {
    pub pts: MediaTime,
    pub duration: MediaTime,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub dts: Option<MediaTime>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MediaDescriptor {
    Image {
        format: String,
        width: u32,
        height: u32,
        rgba_sha256: ContentHash,
        warnings: Vec<String>,
        #[serde(default, skip_serializing_if = "Option::is_none")]
        alpha: Option<ImageAlphaV1>,
    },
    Movie {
        codec: String,
        width: u32,
        height: u32,
        samples: Vec<SampleTiming>,
        native_decode: bool,
        decode_error: Option<String>,
        warnings: Vec<String>,
    },
    Audio {
        codec: String,
        rate: u32,
        channels: u32,
        sample_frames: u64,
        bits: u32,
        format_flags: u32,
        measured_channel_labels: Option<Vec<String>>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImageAlphaV1 {
    pub schema: u32,
    pub alpha_sha256: ContentHash,
    pub minimum: u8,
    pub maximum: u8,
    pub nonzero_pixels: u64,
    pub nonopaque_pixels: u64,
}

impl ImageAlphaV1 {
    pub(crate) fn validate(&self, width: u32, height: u32) -> Result<()> {
        let pixels = u64::from(width)
            .checked_mul(u64::from(height))
            .filter(|pixels| *pixels != 0)
            .ok_or_else(|| {
                StudioError::new(
                    "invalid_image_alpha",
                    "Alpha measurement requires a positive checked image extent",
                )
            })?;
        let count_coherent = self.nonzero_pixels <= pixels
            && self.nonopaque_pixels > 0
            && self.nonopaque_pixels <= pixels
            && self
                .nonzero_pixels
                .checked_add(self.nonopaque_pixels)
                .is_some_and(|sum| sum >= pixels);
        let zero_coherent = if self.nonzero_pixels == 0 {
            self.minimum == 0 && self.maximum == 0 && self.nonopaque_pixels == pixels
        } else if self.nonzero_pixels == pixels {
            self.minimum > 0
        } else {
            self.minimum == 0
        };
        let opaque_coherent = if self.nonopaque_pixels == pixels {
            self.maximum < 255
        } else {
            self.maximum == 255
        };
        if self.schema != 1
            || self.minimum > self.maximum
            || !count_coherent
            || !zero_coherent
            || !opaque_coherent
        {
            return Err(StudioError::new(
                "invalid_image_alpha",
                "Image alpha counts and extrema are not a canonical schema1 measurement",
            ));
        }
        Ok(())
    }
}
impl MediaDescriptor {
    pub(crate) fn range_limit(&self, kind: &MediaKind) -> Result<u64> {
        match (self, kind) {
            (Self::Movie { samples, .. }, MediaKind::Movie) => Ok(samples.len() as u64),
            (Self::Audio { sample_frames, .. }, MediaKind::Audio) => Ok(*sample_frames),
            (Self::Image { .. }, MediaKind::Image) => Ok(1),
            _ => Err(StudioError::new(
                "wrong_stream",
                "Selected stream has the wrong media kind",
            )),
        }
    }
    pub(crate) fn picture_extent(&self) -> Result<(u32, u32)> {
        match self {
            Self::Movie { width, height, .. } | Self::Image { width, height, .. } => {
                Ok((*width, *height))
            }
            Self::Audio { .. } => Err(StudioError::new("wrong_stream", "Picture source is audio")),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredAsset {
    pub hash: ContentHash,
    pub bytes: u64,
    pub origin: Origin,
    pub descriptor: MediaDescriptor,
    pub backend: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub measurement: Option<NativeProbeIdentity>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeProbeIdentity {
    pub schema: u32,
    pub producer: crate::BuildIdentity,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AudioBinding {
    pub asset: ContentHash,
    pub source_samples: Span,
    pub source_rate: u32,
    pub channel_order: Vec<String>,
    pub channel_order_basis: String,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoClip {
    pub id: EntityId,
    pub timeline_frames: Span,
    pub asset: ContentHash,
    pub source_samples: Span,
    pub cadence: Cadence,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub framing: Option<crate::Framing>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<crate::PicturePlacement>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<crate::PictureMotion>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<crate::PictureMask>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum Cadence {
    SourcePresentationTime,
    Hold { ordinal: u64 },
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoTrack {
    pub id: EntityId,
    pub clips: Vec<VideoClip>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AudioClip {
    pub id: EntityId,
    pub timeline_samples: Span,
    pub asset: ContentHash,
    pub source_samples: Span,
    pub source_rate: u32,
    pub gain: f32,
    pub pan: f32,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AudioTrack {
    pub id: EntityId,
    pub clips: Vec<AudioClip>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Timeline {
    pub id: EntityId,
    pub frame_count: u64,
    pub video_tracks: Vec<VideoTrack>,
    pub audio_tracks: Vec<AudioTrack>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Snapshot {
    pub schema: u32,
    pub project: EntityId,
    pub name: String,
    pub parent: Option<ContentHash>,
    pub settings: Settings,
    pub assets: BTreeMap<ContentHash, StoredAsset>,
    pub canonical_audio: Option<AudioBinding>,
    pub timelines: BTreeMap<EntityId, Timeline>,
}

impl Snapshot {
    pub(crate) fn validate(&self) -> Result<()> {
        self.validate_cancellable(|| Ok(()))
    }

    pub(crate) fn validate_cancellable(&self, mut check: impl FnMut() -> Result<()>) -> Result<()> {
        check()?;
        self.settings.validate()?;
        if self.schema != 1 || self.name.is_empty() || self.assets.len() > 10000 {
            return Err(StudioError::new(
                "invalid_project",
                "Unsupported schema or project limits",
            ));
        }
        for (id, asset) in &self.assets {
            check()?;
            if id != &asset.hash {
                return Err(StudioError::new(
                    "asset_identity",
                    "Asset key does not match measured hash",
                ));
            }
            if let MediaDescriptor::Image {
                width,
                height,
                alpha: Some(alpha),
                ..
            } = &asset.descriptor
            {
                alpha.validate(*width, *height)?;
            }
            for source in asset.origin.sources() {
                if &source.asset == id {
                    return Err(StudioError::new(
                        "lineage_cycle",
                        "Asset cannot derive from itself",
                    ));
                }
                self.validate_source(source)?;
            }
        }
        fn walk(
            id: &ContentHash,
            assets: &BTreeMap<ContentHash, StoredAsset>,
            seen: &mut BTreeSet<ContentHash>,
            active: &mut BTreeSet<ContentHash>,
        ) -> Result<()> {
            if active.contains(id) {
                return Err(StudioError::new(
                    "lineage_cycle",
                    "Asset lineage contains a cycle",
                ));
            }
            if !seen.insert(id.clone()) {
                return Ok(());
            }
            active.insert(id.clone());
            for source in assets[id].origin.sources() {
                walk(&source.asset, assets, seen, active)?;
            }
            active.remove(id);
            Ok(())
        }
        let mut seen = BTreeSet::new();
        for id in self.assets.keys() {
            check()?;
            walk(id, &self.assets, &mut seen, &mut BTreeSet::new())?;
        }
        if let Some(audio) = &self.canonical_audio {
            self.validate_source(&SourceRange {
                asset: audio.asset.clone(),
                range: audio.source_samples.clone(),
                stream: MediaKind::Audio,
            })?;
            let MediaDescriptor::Audio { rate, channels, .. } =
                &self.assets[&audio.asset].descriptor
            else {
                unreachable!()
            };
            if audio.source_rate != *rate
                || audio.channel_order.len() != *channels as usize
                || audio.channel_order_basis.is_empty()
            {
                return Err(StudioError::new(
                    "audio_binding",
                    "Canonical audio clock or channel decision does not match its source",
                ));
            }
        }
        for (id, timeline) in &self.timelines {
            check()?;
            if id != &timeline.id
                || timeline.frame_count == 0
                || timeline.frame_count > MAX_TIMELINE_FRAMES
            {
                return Err(StudioError::new(
                    "timeline_extent",
                    "Invalid timeline identity or extent",
                ));
            }
            let sample_count = self
                .settings
                .frame_rate
                .samples_at_frame(timeline.frame_count, self.settings.audio_rate)?;
            let mut ids = BTreeSet::new();
            for track in &timeline.video_tracks {
                if !ids.insert(track.id.clone()) {
                    return Err(StudioError::new(
                        "duplicate_id",
                        "Duplicate track or clip ID",
                    ));
                }
                let mut ranges = Vec::new();
                for clip in &track.clips {
                    check()?;
                    if !ids.insert(clip.id.clone()) {
                        return Err(StudioError::new(
                            "duplicate_id",
                            "Duplicate track or clip ID",
                        ));
                    }
                    clip.timeline_frames.within(timeline.frame_count)?;
                    if let Some(framing) = &clip.framing {
                        framing.validate()?;
                    }
                    if let Some(placement) = &clip.placement {
                        placement.validate()?;
                    }
                    if let Some(motion) = &clip.motion {
                        let base = clip.placement.clone().unwrap_or_else(|| {
                            crate::PicturePlacement::canvas(
                                self.settings.width,
                                self.settings.height,
                            )
                        });
                        crate::motion::normalize_motion_cancellable(
                            motion,
                            &base,
                            clip.timeline_frames.length,
                            &mut check,
                        )?;
                    }
                    if let Some(mask) = &clip.mask {
                        crate::mask::normalize_mask_cancellable(
                            mask,
                            clip.timeline_frames.length,
                            &mut check,
                        )?;
                    }
                    let asset = self.assets.get(&clip.asset).ok_or_else(|| {
                        StudioError::new(
                            "missing_asset",
                            "Picture source is absent from this revision",
                        )
                    })?;
                    let stream = match asset.descriptor {
                        MediaDescriptor::Movie { .. } => MediaKind::Movie,
                        MediaDescriptor::Image { .. } => {
                            if clip.cadence != (Cadence::Hold { ordinal: 0 }) {
                                return Err(StudioError::new(
                                    "unsupported_image_cadence",
                                    "Static images require an explicit hold at ordinal zero",
                                ));
                            }
                            MediaKind::Image
                        }
                        MediaDescriptor::Audio { .. } => {
                            return Err(StudioError::new(
                                "wrong_stream",
                                "Picture clip selects audio",
                            ));
                        }
                    };
                    self.validate_source(&SourceRange {
                        asset: clip.asset.clone(),
                        range: clip.source_samples.clone(),
                        stream,
                    })?;
                    if let Some(framing) = &clip.framing {
                        let (width, height) = asset.descriptor.picture_extent()?;
                        framing.validate_source_extent(width, height)?;
                    }
                    if let Cadence::Hold { ordinal } = clip.cadence
                        && (ordinal < clip.source_samples.start
                            || ordinal >= clip.source_samples.end()?)
                    {
                        return Err(StudioError::new(
                            "source_bounds",
                            "Held ordinal is outside allowed source samples",
                        ));
                    }
                    ranges.push(&clip.timeline_frames);
                }
                reject_overlap(ranges)?;
            }
            for track in &timeline.audio_tracks {
                if !ids.insert(track.id.clone()) {
                    return Err(StudioError::new(
                        "duplicate_id",
                        "Duplicate track or clip ID",
                    ));
                }
                let mut ranges = Vec::new();
                for clip in &track.clips {
                    if !ids.insert(clip.id.clone()) {
                        return Err(StudioError::new(
                            "duplicate_id",
                            "Duplicate track or clip ID",
                        ));
                    }
                    clip.timeline_samples.within(sample_count)?;
                    self.validate_source(&SourceRange {
                        asset: clip.asset.clone(),
                        range: clip.source_samples.clone(),
                        stream: MediaKind::Audio,
                    })?;
                    let MediaDescriptor::Audio { rate, .. } = &self.assets[&clip.asset].descriptor
                    else {
                        unreachable!()
                    };
                    if clip.source_rate != *rate
                        || !clip.gain.is_finite()
                        || clip.gain < 0.0
                        || !clip.pan.is_finite()
                        || !(-1.0..=1.0).contains(&clip.pan)
                    {
                        return Err(StudioError::new(
                            "audio_clip",
                            "Invalid source clock, gain or pan",
                        ));
                    }
                    ranges.push(&clip.timeline_samples);
                }
                reject_overlap(ranges)?;
            }
        }
        Ok(())
    }
    fn validate_source(&self, source: &SourceRange) -> Result<()> {
        let asset = self.assets.get(&source.asset).ok_or_else(|| {
            StudioError::new("missing_asset", "Source is absent from this revision")
        })?;
        source
            .range
            .within(asset.descriptor.range_limit(&source.stream)?)
    }
}

fn reject_overlap(mut spans: Vec<&Span>) -> Result<()> {
    spans.sort_by_key(|span| span.start);
    for pair in spans.windows(2) {
        if pair[0].end()? > pair[1].start {
            return Err(StudioError::new(
                "track_overlap",
                "Items on one track must not overlap",
            ));
        }
    }
    Ok(())
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CreateProject {
    pub project: EntityId,
    pub intent: EntityId,
    pub name: String,
    pub settings: Settings,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CommitProject {
    pub intent: EntityId,
    pub base_revision: ContentHash,
    pub imports: Vec<AssetImport>,
    pub canonical_audio: Option<AudioBinding>,
    pub timelines: Vec<Timeline>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RevisionReceipt {
    pub project: EntityId,
    pub revision: ContentHash,
    pub parent: Option<ContentHash>,
    pub sequence: u64,
    pub replayed: bool,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Inspection {
    pub receipt: RevisionReceipt,
    pub snapshot: Snapshot,
    pub asset_measurements: BTreeMap<ContentHash, ContentHash>,
}
