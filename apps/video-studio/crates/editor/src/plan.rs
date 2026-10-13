use std::collections::{BTreeMap, BTreeSet};

use serde::{Deserialize, Serialize};

use crate::{
    AudioClip, BuildIdentity, Cadence, ContentHash, EntityId, MediaDescriptor, MediaTime, Result,
    Snapshot, Span, StoredAsset, StudioError, Timeline,
};

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExportRequest {
    pub intent: EntityId,
    pub revision: ContentHash,
    pub timeline: EntityId,
    pub profile: MovieProfile,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MovieProfile {
    H264AacMp4 {
        video_bitrate: u32,
        audio_bitrate: u32,
    },
    NativeColorMasterV1,
    NativeColorMasterV2,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AlphaPolicy {
    StraightRgbaPremulUnorm16Q16V1,
}

impl<'de> Deserialize<'de> for MovieProfile {
    fn deserialize<D: serde::Deserializer<'de>>(
        deserializer: D,
    ) -> std::result::Result<Self, D::Error> {
        #[derive(Deserialize)]
        #[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
        enum WireProfile {
            H264AacMp4 {
                video_bitrate: u32,
                audio_bitrate: u32,
            },
            NativeColorMasterV1 {},
            NativeColorMasterV2 {},
        }
        Ok(match WireProfile::deserialize(deserializer)? {
            WireProfile::H264AacMp4 {
                video_bitrate,
                audio_bitrate,
            } => Self::H264AacMp4 {
                video_bitrate,
                audio_bitrate,
            },
            WireProfile::NativeColorMasterV1 {} => Self::NativeColorMasterV1,
            WireProfile::NativeColorMasterV2 {} => Self::NativeColorMasterV2,
        })
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoUse {
    pub clip: EntityId,
    pub track: EntityId,
    pub timeline_frames: Span,
    pub asset: ContentHash,
    pub allowed_source_samples: Span,
    pub presentation_ordinals: Vec<u64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub framing: Option<crate::Framing>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<crate::PicturePlacement>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<crate::PlannedPictureMotion>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<crate::PlannedPictureMask>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AudioUse {
    pub track: EntityId,
    pub clip: AudioClip,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExportPlan {
    pub schema: u32,
    pub project: EntityId,
    pub revision: ContentHash,
    pub timeline: Timeline,
    pub settings: crate::Settings,
    pub canonical_audio: Option<crate::AudioBinding>,
    pub profile: MovieProfile,
    pub renderer: BuildIdentity,
    pub source_closure: BTreeMap<ContentHash, StoredAsset>,
    pub video: Vec<VideoUse>,
    pub audio: Vec<AudioUse>,
    pub timeline_sample_frames: u64,
    #[serde(default)]
    pub decode_evidence: Vec<SourceDecodeEvidence>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub image_decode_evidence: Vec<ImageDecodeEvidence>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub alpha_policy: Option<AlphaPolicy>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SourceDecodeEvidence {
    pub asset: ContentHash,
    pub source_samples: Span,
    pub decoded_samples: u64,
    pub pts_verified: bool,
    pub decoder_executable_sha256: ContentHash,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ImageDecodeEvidence {
    pub asset: ContentHash,
    pub width: u32,
    pub height: u32,
    pub rgba_sha256: ContentHash,
    pub decoder_executable_sha256: ContentHash,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_alpha_id: Option<ContentHash>,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PreparedExport {
    pub plan_id: ContentHash,
    pub plan: ExportPlan,
    pub replayed: bool,
}

pub(crate) fn compile(snapshot: Snapshot, request: &ExportRequest) -> Result<PreparedExport> {
    snapshot.validate()?;
    if ContentHash::document(&snapshot)? != request.revision {
        return Err(StudioError::new(
            "revision_tampered",
            "Compiler input does not match requested revision",
        ));
    }
    let timeline = snapshot
        .timelines
        .get(&request.timeline)
        .ok_or_else(|| {
            StudioError::new(
                "timeline_missing",
                "Timeline is absent from requested revision",
            )
        })?
        .clone();
    crate::native_format::NativeFormatContract::for_profile(&request.profile)?;
    let count = snapshot
        .settings
        .frame_rate
        .samples_at_frame(timeline.frame_count, snapshot.settings.audio_rate)?;
    let mut video = Vec::new();
    let mut audio = Vec::new();
    let mut used = BTreeSet::new();
    let mut frame_coverage = vec![false; timeline.frame_count as usize];
    let mut audio_coverage = Vec::new();
    let alpha = timeline
        .video_tracks
        .iter()
        .flat_map(|track| &track.clips)
        .any(|clip| {
            matches!(
                &snapshot.assets[&clip.asset].descriptor,
                MediaDescriptor::Image { alpha: Some(_), .. }
            )
        });
    let animated = timeline
        .video_tracks
        .iter()
        .flat_map(|track| &track.clips)
        .any(|clip| clip.motion.is_some());
    let masked = timeline
        .video_tracks
        .iter()
        .flat_map(|track| &track.clips)
        .any(|clip| clip.mask.is_some());
    let layered = alpha
        || masked
        || animated
        || timeline
            .video_tracks
            .iter()
            .filter(|track| !track.clips.is_empty())
            .count()
            > 1
        || timeline
            .video_tracks
            .iter()
            .flat_map(|track| &track.clips)
            .any(|clip| clip.placement.is_some());
    for track in &timeline.video_tracks {
        for clip in &track.clips {
            let asset = &snapshot.assets[&clip.asset];
            let ordinals = match &asset.descriptor {
                MediaDescriptor::Image { .. } => vec![0; clip.timeline_frames.length as usize],
                MediaDescriptor::Audio { .. } => unreachable!(),
                MediaDescriptor::Movie {
                    samples,
                    native_decode,
                    ..
                } => {
                    if !native_decode {
                        return Err(StudioError::new(
                            "unsupported_decode",
                            format!(
                                "Asset {} failed its native decode probe",
                                clip.asset.as_str()
                            ),
                        ));
                    }
                    let start = clip.source_samples.start as usize;
                    let end = clip.source_samples.end()? as usize;
                    let selected = &samples[start..end];
                    let mut ordinals = Vec::with_capacity(clip.timeline_frames.length as usize);
                    for local in 0..clip.timeline_frames.length {
                        let ordinal = match clip.cadence {
                            Cadence::Hold { ordinal } => ordinal,
                            Cadence::SourcePresentationTime => {
                                let origin = &selected[0].pts;
                                let target = offset(origin, local, &snapshot.settings.frame_rate)?;
                                let i = selected.partition_point(|sample| {
                                    sample.pts.compare(&target) == std::cmp::Ordering::Less
                                });
                                if i == selected.len()
                                    || selected[i].pts.compare(&target) != std::cmp::Ordering::Equal
                                {
                                    return Err(StudioError::new(
                                        "unsupported_cadence",
                                        "Source presentation timestamps do not match every output frame; select an explicit retiming operation",
                                    ));
                                }
                                selected[i].ordinal
                            }
                        };
                        ordinals.push(ordinal);
                    }
                    if matches!(clip.cadence, Cadence::SourcePresentationTime) {
                        let required_end = offset(
                            &selected[0].pts,
                            clip.timeline_frames.length,
                            &snapshot.settings.frame_rate,
                        )?;
                        let last = &samples[*ordinals.last().expect("positive clip span") as usize];
                        let measured_end = add_time(&last.pts, &last.duration)?;
                        if measured_end.compare(&required_end) == std::cmp::Ordering::Less {
                            return Err(StudioError::new(
                                "source_coverage",
                                "Last selected source sample ends before output coverage",
                            ));
                        }
                    }
                    ordinals
                }
            };
            let destination_end = clip.timeline_frames.end()?;
            frame_coverage[clip.timeline_frames.start as usize..destination_end as usize]
                .fill(true);
            used.insert(clip.asset.clone());
            let base = clip.placement.clone().unwrap_or_else(|| {
                crate::PicturePlacement::canvas(snapshot.settings.width, snapshot.settings.height)
            });
            let motion = clip
                .motion
                .as_ref()
                .map(|motion| {
                    crate::motion::normalize_motion(motion, &base, clip.timeline_frames.length)
                })
                .transpose()?;
            video.push(VideoUse {
                clip: clip.id.clone(),
                track: track.id.clone(),
                timeline_frames: clip.timeline_frames.clone(),
                asset: clip.asset.clone(),
                allowed_source_samples: clip.source_samples.clone(),
                presentation_ordinals: ordinals,
                framing: clip.framing.clone(),
                placement: if layered && motion.is_none() {
                    Some(base)
                } else {
                    None
                },
                motion,
                mask: clip
                    .mask
                    .as_ref()
                    .map(|mask| {
                        crate::mask::normalize_mask_cancellable(
                            mask,
                            clip.timeline_frames.length,
                            || Ok(()),
                        )
                    })
                    .transpose()?,
            });
        }
    }
    if frame_coverage.contains(&false) {
        return Err(StudioError::new(
            "video_coverage",
            "Export contains uncovered picture frames",
        ));
    }
    for track in &timeline.audio_tracks {
        for clip in &track.clips {
            if clip.source_rate != snapshot.settings.audio_rate
                || clip.source_samples.length != clip.timeline_samples.length
            {
                return Err(StudioError::new(
                    "unsupported_audio_retime",
                    "Audio resampling or stretching is not implemented yet",
                ));
            }
            used.insert(clip.asset.clone());
            audio_coverage.push(clip.timeline_samples.clone());
            audio.push(AudioUse {
                track: track.id.clone(),
                clip: clip.clone(),
            });
        }
    }
    audio_coverage.sort_by_key(|span| span.start);
    let mut covered = 0;
    for span in audio_coverage {
        if span.start > covered {
            return Err(StudioError::new(
                "audio_coverage",
                "Export contains uncovered audio samples",
            ));
        }
        covered = covered.max(span.end()?);
    }
    if covered != count {
        return Err(StudioError::new(
            "audio_coverage",
            "Audio tracks do not cover the complete output clock",
        ));
    }
    if let Some(binding) = &snapshot.canonical_audio {
        let mut canonical_coverage = Vec::new();
        for use_ in &audio {
            let clip = &use_.clip;
            if clip.asset != binding.asset {
                return Err(StudioError::new(
                    "canonical_audio_mismatch",
                    "This behavior unit does not allow audio that replaces the bound canonical master",
                ));
            }
            if clip.source_rate != binding.source_rate
                || clip.source_samples.start
                    != binding
                        .source_samples
                        .start
                        .checked_add(clip.timeline_samples.start)
                        .ok_or_else(|| {
                            StudioError::new(
                                "time_overflow",
                                "Canonical audio source offset overflow",
                            )
                        })?
                || clip.source_samples.end()? > binding.source_samples.end()?
            {
                return Err(StudioError::new(
                    "canonical_audio_mismatch",
                    "Consumed master interval differs from its canonical timeline binding",
                ));
            }
            canonical_coverage.push(clip.timeline_samples.clone());
        }
        if canonical_coverage.is_empty() {
            return Err(StudioError::new(
                "canonical_audio_mismatch",
                "Bound master is absent from audible timeline",
            ));
        }
        used.insert(binding.asset.clone());
    }
    fn collect(
        id: &ContentHash,
        assets: &BTreeMap<ContentHash, StoredAsset>,
        used: &mut BTreeSet<ContentHash>,
    ) {
        for source in assets[id].origin.sources() {
            if used.insert(source.asset.clone()) {
                collect(&source.asset, assets, used);
            }
        }
    }
    for id in used.clone() {
        collect(&id, &snapshot.assets, &mut used);
    }
    let source_closure: BTreeMap<_, _> = used
        .into_iter()
        .map(|hash| {
            let asset = snapshot.assets[&hash].clone();
            (hash, asset)
        })
        .collect();
    let plan = ExportPlan {
        schema: if alpha {
            7
        } else if masked {
            6
        } else if animated {
            5
        } else if layered {
            4
        } else if source_closure
            .values()
            .any(|asset| matches!(asset.descriptor, MediaDescriptor::Image { .. }))
        {
            3
        } else {
            2
        },
        project: snapshot.project,
        revision: request.revision.clone(),
        timeline,
        settings: snapshot.settings,
        canonical_audio: snapshot.canonical_audio,
        profile: request.profile.clone(),
        renderer: BuildIdentity::current()?,
        source_closure,
        video,
        audio,
        timeline_sample_frames: count,
        decode_evidence: Vec::new(),
        image_decode_evidence: Vec::new(),
        alpha_policy: alpha.then_some(AlphaPolicy::StraightRgbaPremulUnorm16Q16V1),
    };
    Ok(PreparedExport {
        plan_id: ContentHash::document(&plan)?,
        plan,
        replayed: false,
    })
}

fn add_time(a: &MediaTime, b: &MediaTime) -> Result<MediaTime> {
    let ticks = i128::from(a.ticks) * i128::from(b.timescale)
        + i128::from(b.ticks) * i128::from(a.timescale);
    let scale = u64::from(a.timescale) * u64::from(b.timescale);
    reduced(ticks, scale)
}

fn directly_used_image_assets(plan: &ExportPlan) -> Result<BTreeSet<ContentHash>> {
    plan.video
        .iter()
        .filter_map(|use_| {
            plan.source_closure
                .get(&use_.asset)
                .map(|asset| {
                    matches!(&asset.descriptor, MediaDescriptor::Image { .. })
                        .then_some(use_.asset.clone())
                })
                .ok_or_else(|| {
                    StudioError::new("invalid_layer_plan", "Picture source missing from closure")
                })
                .transpose()
        })
        .collect()
}

fn directly_used_alpha_assets(plan: &ExportPlan) -> Result<BTreeSet<ContentHash>> {
    plan.video
        .iter()
        .filter_map(|use_| {
            plan.source_closure
                .get(&use_.asset)
                .map(|asset| {
                    matches!(
                        &asset.descriptor,
                        MediaDescriptor::Image { alpha: Some(_), .. }
                    )
                    .then_some(use_.asset.clone())
                })
                .ok_or_else(|| {
                    StudioError::new("invalid_layer_plan", "Picture source missing from closure")
                })
                .transpose()
        })
        .collect()
}

pub(crate) fn validate_decode_evidence(plan: &ExportPlan) -> Result<()> {
    validate_picture_mapping_cancellable(plan, || Ok(()))?;
    if plan.schema != 7 {
        if plan.alpha_policy.is_some()
            || plan
                .image_decode_evidence
                .iter()
                .any(|evidence| evidence.source_alpha_id.is_some())
        {
            return Err(StudioError::new(
                "invalid_decode_evidence",
                "Legacy plans cannot carry alpha policy or alpha decode evidence",
            ));
        }
        return Ok(());
    }
    let expected = directly_used_image_assets(plan)?;
    if expected.len() != plan.image_decode_evidence.len() {
        return Err(StudioError::new(
            "invalid_decode_evidence",
            "Plan7 requires one decode record per unique directly used image",
        ));
    }
    for (expected_asset, evidence) in expected.iter().zip(&plan.image_decode_evidence) {
        if &evidence.asset != expected_asset
            || evidence.decoder_executable_sha256 != plan.renderer.executable_sha256
        {
            return Err(StudioError::new(
                "invalid_decode_evidence",
                "Plan7 image evidence order, identity or decoder differs from the plan",
            ));
        }
        let stored = plan.source_closure.get(expected_asset).ok_or_else(|| {
            StudioError::new(
                "invalid_decode_evidence",
                "Plan7 image evidence source is absent from the closure",
            )
        })?;
        let MediaDescriptor::Image {
            width,
            height,
            rgba_sha256,
            alpha,
            ..
        } = &stored.descriptor
        else {
            return Err(StudioError::new(
                "invalid_decode_evidence",
                "Plan7 image evidence references a non-image source",
            ));
        };
        let expected_alpha = alpha
            .as_ref()
            .map(|alpha| crate::alpha_picture::source_alpha_id(expected_asset, rgba_sha256, alpha))
            .transpose()?;
        if evidence.width != *width
            || evidence.height != *height
            || evidence.rgba_sha256 != *rgba_sha256
            || evidence.source_alpha_id != expected_alpha
        {
            return Err(StudioError::new(
                "invalid_decode_evidence",
                "Plan7 image evidence differs from immutable measured pixels",
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
pub(crate) fn validate_picture_mapping(plan: &ExportPlan) -> Result<()> {
    validate_picture_mapping_cancellable(plan, || Ok(()))
}

pub(crate) fn validate_picture_mapping_cancellable(
    plan: &ExportPlan,
    mut check: impl FnMut() -> Result<()>,
) -> Result<()> {
    check()?;
    if !(2..=7).contains(&plan.schema) {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Unsupported native picture plan schema",
        ));
    }
    let snapshot = Snapshot {
        schema: 1,
        project: plan.project.clone(),
        name: "Native plan validation".into(),
        parent: None,
        settings: plan.settings.clone(),
        assets: plan.source_closure.clone(),
        canonical_audio: plan.canonical_audio.clone(),
        timelines: [(plan.timeline.id.clone(), plan.timeline.clone())]
            .into_iter()
            .collect(),
    };
    snapshot.validate_cancellable(&mut check)?;
    let alpha_assets = directly_used_alpha_assets(plan)?;
    match (
        plan.schema,
        alpha_assets.is_empty(),
        plan.alpha_policy.as_ref(),
    ) {
        (7, false, Some(AlphaPolicy::StraightRgbaPremulUnorm16Q16V1)) => {}
        (2..=6, true, None) => {}
        _ => {
            return Err(StudioError::new(
                "invalid_layer_plan",
                "Picture schema, alpha policy and directly used alpha assets disagree",
            ));
        }
    }
    let has_mask = plan
        .timeline
        .video_tracks
        .iter()
        .flat_map(|track| &track.clips)
        .any(|clip| clip.mask.is_some());
    if plan.schema != 7 && (plan.schema == 6) != has_mask {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Only schema6 plans contain declared picture masks",
        ));
    }
    if plan.schema == 5
        && !plan
            .timeline
            .video_tracks
            .iter()
            .flat_map(|track| &track.clips)
            .any(|clip| clip.motion.is_some())
    {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Schema5 requires declared picture motion",
        ));
    }
    if plan.timeline_sample_frames
        != plan
            .settings
            .frame_rate
            .samples_at_frame(plan.timeline.frame_count, plan.settings.audio_rate)?
    {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Plan audio clock differs from timeline extent",
        ));
    }
    let audio: Vec<_> = plan
        .timeline
        .audio_tracks
        .iter()
        .flat_map(|track| track.clips.iter().map(move |clip| (track, clip)))
        .collect();
    if audio.len() != plan.audio.len()
        || audio
            .into_iter()
            .zip(&plan.audio)
            .any(|((track, clip), use_)| use_.track != track.id || use_.clip != *clip)
    {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Audio uses do not match timeline clips one-to-one",
        ));
    }
    let expected: Vec<_> = plan
        .timeline
        .video_tracks
        .iter()
        .flat_map(|track| track.clips.iter().map(move |clip| (track, clip)))
        .collect();
    if expected.len() != plan.video.len() {
        return Err(StudioError::new(
            "invalid_layer_plan",
            "Picture uses do not match timeline clips one-to-one",
        ));
    }
    for ((track, clip), use_) in expected.into_iter().zip(&plan.video) {
        check()?;
        let base = clip.placement.clone().unwrap_or_else(|| {
            crate::PicturePlacement::canvas(plan.settings.width, plan.settings.height)
        });
        let motion = if matches!(plan.schema, 5..=7) {
            clip.motion
                .as_ref()
                .map(|motion| {
                    crate::motion::normalize_motion_cancellable(
                        motion,
                        &base,
                        clip.timeline_frames.length,
                        &mut check,
                    )
                })
                .transpose()?
        } else {
            if clip.motion.is_some() {
                return Err(StudioError::new(
                    "invalid_layer_plan",
                    "Legacy plans cannot contain picture motion",
                ));
            }
            None
        };
        let placement = if matches!(plan.schema, 4..=7) && motion.is_none() {
            Some(base)
        } else {
            if plan.schema < 4 && clip.placement.is_some() {
                return Err(StudioError::new(
                    "invalid_layer_plan",
                    "Legacy plans cannot contain clip placement",
                ));
            }
            None
        };
        let mask = clip
            .mask
            .as_ref()
            .map(|mask| {
                crate::mask::normalize_mask_cancellable(
                    mask,
                    clip.timeline_frames.length,
                    &mut check,
                )
            })
            .transpose()?;
        if use_.track != track.id
            || use_.clip != clip.id
            || use_.asset != clip.asset
            || use_.timeline_frames != clip.timeline_frames
            || use_.allowed_source_samples != clip.source_samples
            || use_.framing != clip.framing
            || use_.placement != placement
            || use_.motion != motion
            || use_.mask != mask
            || use_.presentation_ordinals.len() as u64 != clip.timeline_frames.length
        {
            return Err(StudioError::new(
                "invalid_layer_plan",
                "Picture use differs from its timeline clip, order or normalized placement",
            ));
        }
        let descriptor = &plan
            .source_closure
            .get(&use_.asset)
            .ok_or_else(|| {
                StudioError::new("invalid_layer_plan", "Picture source missing from closure")
            })?
            .descriptor;
        let end = clip.source_samples.end()?;
        for (local, ordinal) in use_.presentation_ordinals.iter().copied().enumerate() {
            check()?;
            if ordinal < clip.source_samples.start || ordinal >= end {
                return Err(StudioError::new(
                    "invalid_layer_plan",
                    "Picture ordinal outside selected source range",
                ));
            }
            match descriptor {
                MediaDescriptor::Image { .. }
                    if ordinal == 0 && clip.cadence == (Cadence::Hold { ordinal: 0 }) => {}
                MediaDescriptor::Movie {
                    samples,
                    native_decode,
                    ..
                } if *native_decode => {
                    let sample = samples.get(ordinal as usize).ok_or_else(|| {
                        StudioError::new(
                            "invalid_layer_plan",
                            "Picture ordinal outside source sample index",
                        )
                    })?;
                    if sample.ordinal != ordinal
                        || sample.pts.timescale == 0
                        || sample.duration.timescale == 0
                        || sample.duration.ticks <= 0
                    {
                        return Err(StudioError::new(
                            "invalid_layer_plan",
                            "Source sample ordinal or clock invalid",
                        ));
                    }
                    match clip.cadence {
                        Cadence::Hold { ordinal: held } if held == ordinal => {}
                        Cadence::SourcePresentationTime => {
                            let origin = samples
                                .get(clip.source_samples.start as usize)
                                .ok_or_else(|| {
                                    StudioError::new(
                                        "invalid_layer_plan",
                                        "Source origin outside index",
                                    )
                                })?;
                            if origin.pts.timescale == 0
                                || sample.pts.compare(&offset(
                                    &origin.pts,
                                    local as u64,
                                    &plan.settings.frame_rate,
                                )?) != std::cmp::Ordering::Equal
                            {
                                return Err(StudioError::new(
                                    "invalid_layer_plan",
                                    "Source ordinal PTS differs from timeline cadence",
                                ));
                            }
                        }
                        _ => {
                            return Err(StudioError::new(
                                "invalid_layer_plan",
                                "Held source ordinal differs from clip cadence",
                            ));
                        }
                    }
                }
                _ => {
                    return Err(StudioError::new(
                        "invalid_layer_plan",
                        "Picture use has unsupported source or cadence",
                    ));
                }
            }
        }
        if let MediaDescriptor::Movie { samples, .. } = descriptor
            && clip.cadence == Cadence::SourcePresentationTime
        {
            let first = &samples[clip.source_samples.start as usize];
            let last =
                &samples[*use_.presentation_ordinals.last().ok_or_else(|| {
                    StudioError::new("invalid_layer_plan", "Empty picture source map")
                })? as usize];
            if add_time(&last.pts, &last.duration)?.compare(&offset(
                &first.pts,
                clip.timeline_frames.length,
                &plan.settings.frame_rate,
            )?) == std::cmp::Ordering::Less
            {
                return Err(StudioError::new(
                    "invalid_layer_plan",
                    "Last selected source sample ends before timeline coverage",
                ));
            }
        }
    }
    Ok(())
}
fn offset(origin: &MediaTime, frames: u64, rate: &crate::Rate) -> Result<MediaTime> {
    let ticks = i128::from(origin.ticks) * i128::from(rate.numerator)
        + i128::from(frames) * i128::from(rate.denominator) * i128::from(origin.timescale);
    reduced(
        ticks,
        u64::from(origin.timescale) * u64::from(rate.numerator),
    )
}
fn reduced(ticks: i128, scale: u64) -> Result<MediaTime> {
    if scale == 0 {
        return Err(StudioError::new("invalid_clock", "Zero media time scale"));
    }
    let (mut a, mut b) = (ticks.unsigned_abs(), u128::from(scale));
    while b != 0 {
        (a, b) = (b, a % b);
    }
    let gcd = i128::try_from(a)
        .map_err(|_| StudioError::new("time_overflow", "Time reduction overflow"))?;
    Ok(MediaTime {
        ticks: i64::try_from(ticks / gcd)
            .map_err(|_| StudioError::new("time_overflow", "Media ticks overflow"))?,
        timescale: u32::try_from(i128::from(scale) / gcd)
            .map_err(|_| StudioError::new("time_overflow", "Media time scale overflow"))?,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn alpha_plan() -> ExportPlan {
        let mut plan: ExportPlan =
            serde_json::from_slice(include_bytes!("../tests/fixtures/legacy/plan-schema3.json"))
                .unwrap();
        let asset = plan.video[0].asset.clone();
        let stored = plan.source_closure.get_mut(&asset).unwrap();
        let MediaDescriptor::Image {
            width,
            height,
            rgba_sha256,
            alpha,
            ..
        } = &mut stored.descriptor
        else {
            panic!("image expected")
        };
        let pixels = u64::from(*width) * u64::from(*height);
        let measured = crate::ImageAlphaV1 {
            schema: 1,
            alpha_sha256: ContentHash::parse("a".repeat(64)).unwrap(),
            minimum: 128,
            maximum: 128,
            nonzero_pixels: pixels,
            nonopaque_pixels: pixels,
        };
        *alpha = Some(measured.clone());
        let rgba_sha256 = rgba_sha256.clone();
        let width = *width;
        let height = *height;
        plan.schema = 7;
        plan.alpha_policy = Some(AlphaPolicy::StraightRgbaPremulUnorm16Q16V1);
        plan.video[0].placement = Some(crate::PicturePlacement::canvas(
            plan.settings.width,
            plan.settings.height,
        ));
        plan.image_decode_evidence[0].width = width;
        plan.image_decode_evidence[0].height = height;
        plan.image_decode_evidence[0].rgba_sha256 = rgba_sha256.clone();
        plan.image_decode_evidence[0].source_alpha_id =
            Some(crate::alpha_picture::source_alpha_id(&asset, &rgba_sha256, &measured).unwrap());
        plan
    }

    #[test]
    fn v2_profile_keeps_picture_plan_schemas_two_through_seven() {
        let fixtures: [&[u8]; 5] = [
            include_bytes!("../tests/fixtures/legacy/plan-schema2.json"),
            include_bytes!("../tests/fixtures/legacy/plan-schema3.json"),
            include_bytes!("../tests/fixtures/legacy/plan-schema4.json"),
            include_bytes!("../tests/fixtures/legacy/plan-schema5.json"),
            include_bytes!("../tests/fixtures/legacy/plan-schema6-masks-synthetic.json"),
        ];
        for (index, bytes) in fixtures.into_iter().enumerate() {
            let mut plan: ExportPlan = serde_json::from_slice(bytes).unwrap();
            let schema = u32::try_from(index).unwrap() + 2;
            assert_eq!(plan.schema, schema);
            plan.profile = MovieProfile::NativeColorMasterV2;
            validate_decode_evidence(&plan).unwrap();
            assert_eq!(plan.schema, schema);
        }

        let mut plan = alpha_plan();
        plan.profile = MovieProfile::NativeColorMasterV2;
        validate_decode_evidence(&plan).unwrap();
        assert_eq!(plan.schema, 7);
    }

    #[test]
    fn plan7_rejects_forged_alpha_facts_policy_and_evidence_centrally() {
        let valid = alpha_plan();
        validate_decode_evidence(&valid).unwrap();

        let mut changed = valid.clone();
        changed.alpha_policy = None;
        assert_eq!(
            validate_decode_evidence(&changed).unwrap_err().code,
            "invalid_layer_plan"
        );

        let mut changed = valid.clone();
        changed.image_decode_evidence[0].source_alpha_id = None;
        assert_eq!(
            validate_decode_evidence(&changed).unwrap_err().code,
            "invalid_decode_evidence"
        );

        let mut changed = valid.clone();
        let MediaDescriptor::Image {
            alpha: Some(alpha), ..
        } = &mut changed
            .source_closure
            .get_mut(&changed.video[0].asset)
            .unwrap()
            .descriptor
        else {
            panic!("alpha expected")
        };
        alpha.alpha_sha256 = ContentHash::parse("b".repeat(64)).unwrap();
        assert_eq!(
            validate_decode_evidence(&changed).unwrap_err().code,
            "invalid_decode_evidence"
        );

        let mut changed = valid.clone();
        changed
            .image_decode_evidence
            .push(changed.image_decode_evidence[0].clone());
        assert_eq!(
            validate_decode_evidence(&changed).unwrap_err().code,
            "invalid_decode_evidence"
        );

        let mut changed = valid;
        let MediaDescriptor::Image {
            alpha: Some(alpha), ..
        } = &mut changed
            .source_closure
            .get_mut(&changed.video[0].asset)
            .unwrap()
            .descriptor
        else {
            panic!("alpha expected")
        };
        alpha.minimum = 200;
        alpha.maximum = 100;
        assert_eq!(
            validate_decode_evidence(&changed).unwrap_err().code,
            "invalid_image_alpha"
        );
    }

    #[test]
    fn offsets_use_actual_source_clock_and_preserve_nonzero_start() {
        let origin = MediaTime {
            ticks: 512,
            timescale: 12288,
        };
        let rate = crate::Rate {
            numerator: 24,
            denominator: 1,
        };
        assert_eq!(
            offset(&origin, 23, &rate).unwrap(),
            MediaTime {
                ticks: 1,
                timescale: 1
            }
        );
        assert_eq!(
            offset(&origin, 48, &rate).unwrap(),
            MediaTime {
                ticks: 49,
                timescale: 24
            }
        );
        assert_eq!(
            add_time(
                &MediaTime {
                    ticks: 47,
                    timescale: 24
                },
                &MediaTime {
                    ticks: 1,
                    timescale: 24
                }
            )
            .unwrap(),
            MediaTime {
                ticks: 2,
                timescale: 1
            }
        );
    }
}
