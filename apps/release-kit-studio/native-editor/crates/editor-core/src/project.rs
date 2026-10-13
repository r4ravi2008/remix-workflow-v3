use crate::{EditorError, Limits};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

pub const MAX_SAFE_INTEGER: u64 = 9_007_199_254_740_991;

macro_rules! identifier {
    ($name:ident) => {
        #[derive(Clone, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, JsonSchema)]
        #[serde(transparent)]
        pub struct $name(
            #[schemars(
                length(min = 1, max = 80),
                regex(pattern = "^[A-Za-z0-9][A-Za-z0-9_-]*$")
            )]
            String,
        );
        impl $name {
            pub fn new(value: impl Into<String>) -> Result<Self, EditorError> {
                let value = value.into();
                if value.is_empty()
                    || value.len() > 80
                    || !value.as_bytes()[0].is_ascii_alphanumeric()
                    || !value
                        .bytes()
                        .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
                {
                    return Err(EditorError::invalid(
                        "Identifiers require 1..80 ASCII letters, digits, underscores or hyphens.",
                    ));
                }
                Ok(Self(value))
            }
            pub fn as_str(&self) -> &str {
                &self.0
            }
        }
        impl<'de> Deserialize<'de> for $name {
            fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
                Self::new(String::deserialize(d)?).map_err(serde::de::Error::custom)
            }
        }
    };
}
identifier!(ProjectId);
identifier!(IntentId);
identifier!(ClipId);
identifier!(ArtifactId);
identifier!(RequestId);

macro_rules! position {
    ($name:ident, $min:literal) => {
        #[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, JsonSchema)]
        #[serde(transparent)]
        pub struct $name(#[schemars(range(min = $min, max = 9_007_199_254_740_991_u64))] u64);
        impl $name {
            pub fn new(value: u64) -> Result<Self, EditorError> {
                if !($min..=MAX_SAFE_INTEGER).contains(&value) {
                    return Err(EditorError::invalid(
                        "Integer is outside the exact supported range.",
                    ));
                }
                Ok(Self(value))
            }
            pub fn get(self) -> u64 {
                self.0
            }
        }
        impl<'de> Deserialize<'de> for $name {
            fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
                Self::new(u64::deserialize(d)?).map_err(serde::de::Error::custom)
            }
        }
    };
}
position!(Revision, 0);
position!(FrameIndex, 0);
position!(FrameCount, 1);

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct FrameRate {
    #[schemars(range(min = 1))]
    numerator: u32,
    #[schemars(range(min = 1))]
    denominator: u32,
}
impl FrameRate {
    pub fn new(numerator: u32, denominator: u32) -> Result<Self, EditorError> {
        if numerator == 0 || denominator == 0 {
            return Err(EditorError::invalid(
                "Frame-rate numerator and denominator must be positive.",
            ));
        }
        let (mut a, mut b) = (numerator, denominator);
        while b != 0 {
            (a, b) = (b, a % b);
        }
        Ok(Self {
            numerator: numerator / a,
            denominator: denominator / a,
        })
    }
    pub fn numerator(self) -> u32 {
        self.numerator
    }
    pub fn denominator(self) -> u32 {
        self.denominator
    }
}
impl<'de> Deserialize<'de> for FrameRate {
    fn deserialize<D: serde::Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        #[derive(Deserialize)]
        #[serde(deny_unknown_fields)]
        struct Rate {
            numerator: u32,
            denominator: u32,
        }
        let rate = Rate::deserialize(d)?;
        Self::new(rate.numerator, rate.denominator).map_err(serde::de::Error::custom)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Interval {
    pub start: FrameIndex,
    pub duration: FrameCount,
}
impl Interval {
    pub fn end(self) -> Result<u64, EditorError> {
        self.start
            .get()
            .checked_add(self.duration.get())
            .filter(|v| *v <= MAX_SAFE_INTEGER)
            .ok_or_else(|| EditorError::invalid("Clip interval overflows the exact integer range."))
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Canvas {
    #[schemars(range(min = 1, max = 2048))]
    pub width: u32,
    #[schemars(range(min = 1, max = 2048))]
    pub height: u32,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Timeline {
    pub frame_rate: FrameRate,
    #[schemars(range(min = 1, max = 10000000))]
    pub duration_frames: FrameCount,
    pub canvas: Canvas,
}
impl Timeline {
    pub(crate) fn validate(&self, limits: &Limits) -> Result<(), EditorError> {
        let c = self.canvas;
        if c.width == 0
            || c.height == 0
            || c.width > limits.canvas_axis
            || c.height > limits.canvas_axis
            || u64::from(c.width) * u64::from(c.height) > limits.canvas_pixels
            || self.duration_frames.get() > limits.frames
        {
            return Err(EditorError::invalid(
                "Timeline exceeds the canvas or frame limits.",
            ));
        }
        Ok(())
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "kind", rename_all = "lowercase", deny_unknown_fields)]
pub enum VisualSource {
    Solid { rgba: [u8; 4] },
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Clip {
    pub id: ClipId,
    pub start_frame: FrameIndex,
    pub duration_frames: FrameCount,
    pub source: VisualSource,
}
impl Clip {
    pub fn interval(&self) -> Interval {
        Interval {
            start: self.start_frame,
            duration: self.duration_frames,
        }
    }
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
#[serde(tag = "kind", deny_unknown_fields)]
pub enum Edit {
    #[serde(rename = "clip.put")]
    PutClip { clip: Clip },
    #[serde(rename = "clip.remove")]
    RemoveClip {
        #[serde(rename = "clipId")]
        clip_id: ClipId,
    },
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CreateProject {
    pub project_id: ProjectId,
    pub intent_id: IntentId,
    pub name: String,
    pub timeline: Timeline,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct InspectProject {
    pub project_id: ProjectId,
    pub revision: Option<Revision>,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct CommitProject {
    pub project_id: ProjectId,
    pub expected_revision: Revision,
    pub intent_id: IntentId,
    #[schemars(length(min = 1, max = 10000))]
    pub edits: Vec<Edit>,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
pub enum FrameFormat {
    #[serde(rename = "png-rgba8")]
    PngRgba8,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct RenderFrame {
    pub project_id: ProjectId,
    pub revision: Revision,
    pub intent_id: IntentId,
    pub frame: FrameIndex,
    pub format: FrameFormat,
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct VerifyArtifact {
    pub project_id: ProjectId,
    pub artifact_id: ArtifactId,
}
#[derive(Clone, Debug)]
pub enum Command {
    CreateProject(CreateProject),
    InspectProject(InspectProject),
    CommitProject(CommitProject),
    RenderFrame(RenderFrame),
    VerifyArtifact(VerifyArtifact),
}
impl Command {
    pub fn tool(&self) -> &'static str {
        match self {
            Self::CreateProject(_) => "project.create",
            Self::InspectProject(_) => "project.inspect",
            Self::CommitProject(_) => "project.commit",
            Self::RenderFrame(_) => "frame.render",
            Self::VerifyArtifact(_) => "artifact.verify",
        }
    }
    pub(crate) fn identity(&self) -> Result<String, EditorError> {
        #[derive(Serialize)]
        #[serde(rename_all = "camelCase")]
        struct Identity<'a, T> {
            identity_version: u8,
            protocol_version: u8,
            tool: &'a str,
            input: &'a T,
        }
        macro_rules! hash {
            ($input:expr) => {
                crate::structured_hash(&Identity {
                    identity_version: 1,
                    protocol_version: 1,
                    tool: self.tool(),
                    input: $input,
                })
            };
        }
        match self {
            Self::CreateProject(v) => hash!(v),
            Self::InspectProject(v) => hash!(v),
            Self::CommitProject(v) => hash!(v),
            Self::RenderFrame(v) => hash!(v),
            Self::VerifyArtifact(v) => hash!(v),
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
pub struct Snapshot {
    pub snapshot_version: u8,
    pub project_id: ProjectId,
    pub revision: Revision,
    pub name: String,
    pub timeline: Timeline,
    pub clips: Vec<Clip>,
}
impl Snapshot {
    pub(crate) fn apply(&mut self, edits: &[Edit], limits: &Limits) -> Result<(), EditorError> {
        if edits.is_empty() || edits.len() > limits.clips {
            return Err(EditorError::invalid(
                "A transaction requires 1..10000 edits.",
            ));
        }
        for edit in edits {
            match edit {
                Edit::PutClip { clip } => {
                    if clip.interval().end()? > self.timeline.duration_frames.get() {
                        return Err(EditorError::invalid("Clip extends beyond the timeline."));
                    }
                    if let Some(existing) = self.clips.iter_mut().find(|c| c.id == clip.id) {
                        *existing = clip.clone();
                    } else {
                        self.clips.push(clip.clone());
                    }
                }
                Edit::RemoveClip { clip_id } => {
                    let i = self
                        .clips
                        .iter()
                        .position(|c| c.id == *clip_id)
                        .ok_or_else(|| EditorError::invalid("The removed clip does not exist."))?;
                    self.clips.remove(i);
                }
            }
        }
        if self.clips.len() > limits.clips {
            return Err(EditorError::invalid("Project exceeds the clip limit."));
        }
        self.clips
            .sort_by(|a, b| (a.start_frame, &a.id).cmp(&(b.start_frame, &b.id)));
        for pair in self.clips.windows(2) {
            if pair[0].interval().end()? > pair[1].start_frame.get() {
                return Err(EditorError::invalid(
                    "Clips overlap on the single visual track.",
                ));
            }
        }
        self.revision = Revision::new(
            self.revision
                .get()
                .checked_add(1)
                .ok_or_else(|| EditorError::invalid("Revision overflow."))?,
        )?;
        Ok(())
    }
}
