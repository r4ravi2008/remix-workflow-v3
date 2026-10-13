# Native text Candidate A: explicit layout boxes over untimed font resources

## Usage: caller view

The caller keeps the existing `Project` workflow. A commit may import media and fonts atomically into one revision.

The first unit treats text as a picture item on an existing video track. Each item has an integer box and integer baseline.

The examples below are technical fixtures. They do not add lyrics or change the user film.

### 1. Import a font and add a Telugu title

The font import is separate from timed media imports. Both enter the same `Project::commit` request and revision transaction.

```rust,ignore
let receipt = project.commit(CommitProject {
    intent: EntityId::parse("text-te-commit-a01")?,
    base_revision,
    imports: vec![],
    font_imports: vec![FontResourceImport {
        path: "/owned/NotoSansTelugu-Regular.ttf".into(),
        expected_hash: ContentHash::parse(
            "2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f",
        )?,
        expected_bytes: 197_228,
        origin: FontResourceOrigin::Imported {
            external_source: "notofonts/noto-fonts@ffebf8c1: NotoSansTelugu-Regular.ttf".into(),
            role: "licensed_typeface".into(),
        },
        previous_measurement: None,
    }],
    canonical_audio: None,
    timelines: vec![Timeline {
        id: EntityId::parse("main")?,
        frame_count: 72,
        video_tracks: vec![
            existing_movie_track,
            VideoTrack {
                id: EntityId::parse("title")?,
                clips: vec![],
                text_clips: vec![TextClip {
                    id: EntityId::parse("telugu-test")?,
                    timeline_frames: Span { start: 8, length: 40 },
                    text: "తెలుగు పరీక్ష".into(),
                    language: TextLanguage::parse("te")?,
                    direction: TextDirection::Ltr,
                    style: TextStyle {
                        font: ContentHash::parse(
                            "2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f",
                        )?,
                        font_size_q16: FontSizeQ16::new(64 * 65_536)?,
                        color: Rgba8 { r: 255, g: 230, b: 64, a: 255 },
                    },
                    layout: TextLayoutBox {
                        destination: PixelRect { x: 40, y: 28, width: 240, height: 72 },
                        baseline: PixelPoint { x: 12, y: 50 },
                    },
                    opacity: Opacity::new(1.0)?,
                    motion: None,
                    mask: None,
                }],
            },
        ],
        audio_tracks: vec![existing_unity_audio_track],
    }],
})?;
```

The layout box is a transparent local raster. Its destination uses signed canvas coordinates.
The baseline is measured from the box's top-left edge. The box clips glyph coverage at its edges.

Old callers omit `font_imports` and `text_clips`. Their snapshot bytes remain unchanged.

### 2. Reuse imported fonts with motion and an axis mask

The second commit imports one Devanagari font. It reuses the Telugu font already in the project.

```rust,ignore
let head = project.head()?;
let receipt = project.commit(CommitProject {
    intent: EntityId::parse("text-two-scripts-a01")?,
    base_revision: head.receipt.revision,
    imports: vec![],
    font_imports: vec![FontResourceImport {
        path: "/owned/NotoSansDevanagari-Regular.ttf".into(),
        expected_hash: ContentHash::parse(
            "385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d",
        )?,
        expected_bytes: 219_212,
        origin: FontResourceOrigin::Imported {
            external_source: "notofonts/noto-fonts@ffebf8c1: NotoSansDevanagari-Regular.ttf".into(),
            role: "licensed_typeface".into(),
        },
        previous_measurement: None,
    }],
    canonical_audio: None,
    timelines: vec![timeline_with_text_clip(TextClip {
        id: EntityId::parse("devanagari-test")?,
        timeline_frames: Span { start: 20, length: 32 },
        text: "देवनागरी परीक्षण".into(),
        language: TextLanguage::parse("hi")?,
        direction: TextDirection::Ltr,
        style: TextStyle {
            font: ContentHash::parse(
                "385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d",
            )?,
            font_size_q16: FontSizeQ16::new(52 * 65_536)?,
            color: Rgba8 { r: 255, g: 255, b: 255, a: 224 },
        },
        layout: TextLayoutBox {
            destination: PixelRect { x: -24, y: 96, width: 300, height: 64 },
            baseline: PixelPoint { x: 16, y: 46 },
        },
        opacity: Opacity::new(0.9)?,
        motion: Some(TextMotion {
            x: Some(PropertyCurve {
                keys: vec![
                    CurveKey { frame: 0, value: -24, to_next: Some(CurveInterpolation::Linear) },
                    CurveKey { frame: 31, value: 20, to_next: None },
                ],
            }),
            y: None,
            opacity: None,
        }),
        mask: Some(PictureMask::AxisReveal {
            axis: MaskAxis::Horizontal,
            progress: PropertyCurve {
                keys: vec![
                    CurveKey {
                        frame: 0,
                        value: MaskProgress::new(0.0)?,
                        to_next: Some(CurveInterpolation::Linear),
                    },
                    CurveKey {
                        frame: 12,
                        value: MaskProgress::new(1.0)?,
                        to_next: Some(CurveInterpolation::Step),
                    },
                    CurveKey {
                        frame: 31,
                        value: MaskProgress::new(1.0)?,
                        to_next: None,
                    },
                ],
            },
            inverted: false,
        }),
    })],
})?;
```

Text motion exposes only `x`, `y`, and `opacity`. Width and height remain fixed for the complete clip.

Media clips and text clips cannot overlap within one video track. Track order remains bottom-to-top.

### 3. Prepare, export, cancel, and verify

No public export operation changes. `Project::export` remains synchronous.

```rust,ignore
let request = ExportRequest {
    intent: EntityId::parse("text-export-a01")?,
    revision: receipt.revision.clone(),
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::NativeColorMasterV2,
};

let prepared = project.prepare_export(request.clone())?;
assert_eq!(prepared.plan.schema, 8);

let result = project.export(request.clone())?;
assert_eq!(result.receipt.artifact.plan_id, prepared.plan_id);
let verified = project.verify_export(request.intent.clone())?;
assert_eq!(verified.receipt.receipt_id, result.receipt.receipt_id);
```

A caller can use a scoped thread when it must request cancellation during the synchronous export.

```rust,ignore
std::thread::scope(|scope| -> video_studio::Result<()> {
    let worker = scope.spawn(|| project.export(request.clone()));
    wait_until_export_is_live(&project, &request.intent)?;
    let cancellation = project.cancel_export(request.intent.clone())?;
    assert_eq!(cancellation.state, "cancellation_requested");
    let error = worker.join().expect("export worker panicked").unwrap_err();
    assert_eq!(error.code, "export_cancelled");
    Ok(())
})?;
```

Cancellation requests remain fences. One bounded CoreText or CoreGraphics call may finish before the worker exits.
After an interrupted process, `project.reconcile_export_staging()?` remains the only public finalizing-recovery operation.

## Problem

The editor needs native Indic text without turning fonts into timed media or exposing CoreText stages to callers.
The design must preserve every text-free snapshot, Plan2 through Plan7, and Receipt2 through Receipt4 byte.
It must also bind the native shaping result strongly enough to reject fallback and changed raster behavior.

The current model has only timed `StoredAsset` values and `VideoClip` items. The current layered renderer already provides the desired track order, sparse spans, masks, motion, alpha arithmetic, cancellation, and backpressure.

Candidate A adds two append-only concepts:

1. untimed, content-addressed font resources owned by the project;
2. text clips appended to existing ordered video tracks.

One `text` subsystem owns font probing, shaping, observation, rasterization, and execution comparison.
Its private `text/font.rs` child owns the single face-fingerprint algorithm.

## Shape

### Authoring and storage types

These types are sketches. Every body is deliberately not implemented.

```rust,ignore
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CommitProject {
    pub intent: EntityId,
    pub base_revision: ContentHash,
    pub imports: Vec<AssetImport>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub font_imports: Vec<FontResourceImport>,
    pub canonical_audio: Option<AudioBinding>,
    pub timelines: Vec<Timeline>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FontResourceImport {
    pub path: PathBuf,
    pub expected_hash: ContentHash,
    pub expected_bytes: u64,
    pub origin: FontResourceOrigin,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub previous_measurement: Option<ContentHash>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum FontResourceOrigin {
    Imported { external_source: String, role: String },
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StoredFontResource {
    pub hash: ContentHash,
    pub bytes: u64,
    pub origin: FontResourceOrigin,
    pub descriptor: FontFaceDescriptorV1,
    pub backend: String,
    pub measurement: NativeProbeIdentity,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct FontFaceDescriptorV1 {
    pub schema: u32,                         // exactly 1
    pub container: FontContainer,            // TrueTypeSfntV1 only
    pub face_count: u32,                     // exactly 1
    pub face_index: u32,                     // exactly 0
    pub postscript_name: String,             // observation, not lookup authority
    pub units_per_em: u16,
    pub glyph_count: u16,
    pub tables: Vec<SfntTableIdentity>,      // strictly tag-sorted
    pub face_id: ContentHash,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FontContainer { TrueTypeSfntV1 }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SfntTableIdentity {
    pub tag_hex: String,                     // eight lowercase hex digits
    pub bytes: u32,
    pub sha256: ContentHash,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Snapshot {
    // Existing fields stay in their existing order.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub font_resources: BTreeMap<ContentHash, StoredFontResource>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct VideoTrack {
    pub id: EntityId,
    pub clips: Vec<VideoClip>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub text_clips: Vec<TextClip>,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextClip {
    pub id: EntityId,
    pub timeline_frames: Span,
    pub text: String,
    pub language: TextLanguage,
    pub direction: TextDirection,
    pub style: TextStyle,
    pub layout: TextLayoutBox,
    pub opacity: Opacity,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<TextMotion>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<PictureMask>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "String", into = "String")]
pub struct TextLanguage(String);

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextDirection { Ltr }

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Rgba8 { pub r: u8, pub g: u8, pub b: u8, pub a: u8 }

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(try_from = "u32", into = "u32")]
pub struct FontSizeQ16(u32);

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextStyle {
    pub font: ContentHash,
    pub font_size_q16: FontSizeQ16,
    pub color: Rgba8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PixelPoint { pub x: u32, pub y: u32 }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextLayoutBox {
    pub destination: PixelRect,
    pub baseline: PixelPoint,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextMotion {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub x: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub y: Option<PropertyCurve<i32>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub opacity: Option<PropertyCurve<Opacity>>,
}

impl TextLanguage {
    pub fn parse(value: impl Into<String>) -> Result<Self> {
        unimplemented!("design only")
    }
}

impl FontSizeQ16 {
    pub fn new(value: u32) -> Result<Self> {
        unimplemented!("design only")
    }

    pub fn value(self) -> u32 {
        unimplemented!("design only")
    }
}
```

`FontResourceOrigin` contains no `SourceRange`. A font has no duration, stream, or sample clock.

The project blob directory remains the only byte authority. Media and font metadata are separate maps over that shared CAS.

The first unit accepts only imported fonts. Derived resource lineage can be added later without inventing a timed range now.

Media and font staging happens before the existing SQLite revision transaction. One immediate transaction publishes both maps and the timeline together.
Failure may leave an unreferenced content-addressed blob, as media import already can. It cannot publish a partial revision.

### Snapshot invariants

`Snapshot::validate_cancellable` gains these rules:

- at most 256 font resources exist in one snapshot;
- every font map key equals the stored raw-byte hash;
- a font is between 1 and 16 MiB;
- its descriptor passes the closed schema1 font policy;
- every text clip selects a present font resource;
- exact UTF-8 is nonempty and within the text caps;
- forbidden line and bidi controls are rejected;
- the language identifier is canonical within the accepted subset;
- direction is `ltr`;
- the layout and style pass their bounds;
- text motion contains at least one property and has no size curves;
- all IDs are unique across media clips and text clips;
- media and text spans on one video track form one nonoverlapping set;
- at most 4,096 text clips exist in the selected timeline.

Plan preparation also enforces aggregate text limits before storing Plan8.
The limits include all text uses, runs, glyph observations, and canonical JSON bytes.

The accepted language grammar is a bounded UTS #35 subset:

```text
language = 2..3 lowercase ASCII letters
script   = optional "-" + uppercase ASCII letter + 3 lowercase ASCII letters
region   = optional "-" + 2 uppercase ASCII letters or 3 ASCII digits
```

Variants, extensions, private-use tags, underscores, and noncanonical case are rejected in v1.

The text is not normalized or transliterated. `\t`, `\r`, `\n`, U+0085, U+2028, U+2029, and Unicode bidi controls are rejected.

The unit explicitly rejects TTC/OTC, variable fonts, color fonts, bidi paragraphs, wrapping, per-range styles, rotation, effects, and animated strings.
Those capabilities require later typed contracts. They are not accepted through ignored fields or native defaults.

### Font acceptance and face identity

The font probe parses the table directory before CoreText sees the bytes.

The accepted font is one TrueType-outline SFNT face with scaler type `0x00010000`.
The probe rejects TTC/OTC, WOFF/WOFF2, CFF/CFF2, collections, and multiple faces.

The probe also rejects:

- malformed, duplicate, overlapping, unsorted, or out-of-range table records;
- more than 128 tables;
- absent `cmap`, `head`, `hhea`, `hmtx`, `maxp`, `name`, `glyf`, or `loca` tables;
- absent `GDEF`, `GPOS`, or `GSUB` tables for this Indic-focused unit;
- `fvar`, `gvar`, `avar`, `HVAR`, `VVAR`, `MVAR`, or `CFF2` variation tables;
- `COLR`, `CPAL`, `CBDT`, `CBLC`, `EBDT`, `EBLC`, `sbix`, or `SVG ` color/bitmap tables;
- invalid units per em, zero glyph count, invalid `loca` shape, or an empty PostScript name.

The parser collects every decodable name-ID-6 record and requires one distinct nonempty ASCII PostScript value.
It does not choose a localized family name. `head.unitsPerEm` and `maxp.numGlyphs` supply the stored integer observations.

The face fingerprint is independent of table offsets and directory order:

```text
SHA-256(
  "video-studio-font-face-v1\0" ||
  0x00010000_u32_be ||
  table_count_u16_be ||
  for each table sorted by four raw tag bytes:
      tag_4_bytes || table_length_u32_be || SHA-256(exact_table_bytes)
)
```

The raw font blob hash remains authoritative for bytes. The face fingerprint identifies the selected table set.

Both import probing and run-font fallback checks call this same private fingerprint function.
No second table-identity implementation exists in the native shaping code.

The selected face is always index zero. There is no public face selector because every accepted resource has one face.

### Normalized Plan8 types

Text selects Plan8. Plan8 subsumes layering, motion, masks, and transparent PNG behavior.

No text means the current schema selector runs unchanged and emits Plan2 through Plan7 exactly.

```rust,ignore
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ExportPlan {
    // Existing fields remain in their current order and retain their current rules.
    #[serde(default, skip_serializing_if = "BTreeMap::is_empty")]
    pub font_resources: BTreeMap<ContentHash, StoredFontResource>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub text: Vec<TextUse>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub text_policy: Option<TextPlanPolicyV1>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextUse {
    pub clip: EntityId,
    pub track: EntityId,
    pub timeline_frames: Span,
    pub source: TextSourceObservationV1,
    pub font: ContentHash,
    pub face_id: ContentHash,
    pub style: PlannedTextStyleV1,
    pub layout: PlannedTextLayoutV1,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub placement: Option<PlannedTextPlacementV1>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub motion: Option<PlannedTextMotionV1>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub mask: Option<PlannedPictureMask>,
    pub shaping: TextShapingEvidenceV1,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextSourceObservationV1 {
    pub text: String,
    pub utf8_sha256: ContentHash,
    pub utf8_bytes: u32,
    pub utf16be_sha256: ContentHash,
    pub utf16_units: u32,
    pub language: TextLanguage,
    pub direction: TextDirection,
    pub normalization: TextNormalization,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextNormalization { None }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedTextStyleV1 {
    pub font_size_q16: FontSizeQ16,
    pub color: Rgba8,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedTextLayoutV1 {
    pub width: u32,
    pub height: u32,
    pub baseline: PixelPoint,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedTextPlacementV1 {
    pub x: i32,
    pub y: i32,
    pub opacity_q16: OpacityQ16,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PlannedTextMotionV1 {
    pub x: PlannedCurve<i32>,
    pub y: PlannedCurve<i32>,
    pub opacity_q16: PlannedCurve<OpacityQ16>,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextPlanPolicyV1 {
    pub schema: u32,                       // exactly 1
    pub algorithm: TextAlgorithm,
    pub backend: TextBackendIdentityV1,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TextAlgorithm { CoreTextSingleLineGrayAlpha8V1 }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextBackendIdentityV1 {
    pub schema: u32,                       // exactly 1
    pub core_text: NativeFrameworkIdentityV1,
    pub core_graphics: NativeFrameworkIdentityV1,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct NativeFrameworkIdentityV1 {
    pub bundle_identifier: String,
    pub bundle_version: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub short_version: Option<String>,
}
```

Plan8 stores exactly the directly used fonts. An unused project font does not enter the plan.

`font_resources`, `text`, and `text_policy` append after the current `alpha_policy` field.
Their absence therefore preserves the existing field order as well as the existing values.

The source observation duplicates only facts needed for independent validation and execution.
The embedded timeline remains the authoring authority. The central validator requires exact agreement.

### Shaping evidence

Preparation shapes every text use and stores deterministic observations in track order.
Execution reshapes and compares the complete observation before drawing a frame.

```rust,ignore
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextShapingEvidenceV1 {
    pub schema: u32,                       // exactly 1
    pub line_utf16_range: UnitRange,
    pub glyph_count: u32,
    pub typographic: TextMetricsQ16,
    pub image_bounds: RectQ16,
    pub runs: Vec<TextRunEvidenceV1>,      // CoreText visual order
    pub alpha8_sha256: ContentHash,
    pub alpha8_nonzero_pixels: u64,
    pub alpha8_bounds: Option<LocalPixelRect>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct UnitRange { pub start: u32, pub length: u32 }

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SignedQ16(i64);

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextMetricsQ16 {
    pub width: SignedQ16,
    pub ascent: SignedQ16,
    pub descent: SignedQ16,
    pub leading: SignedQ16,
}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RectQ16 {
    pub x: SignedQ16,
    pub y: SignedQ16,
    pub width: SignedQ16,
    pub height: SignedQ16,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct LocalPixelRect { pub x: u32, pub y: u32, pub width: u32, pub height: u32 }

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TextRunEvidenceV1 {
    pub utf16_range: UnitRange,
    pub status_bits: u32,
    pub text_matrix_q16: AffineQ16,
    pub face_id: ContentHash,
    pub postscript_name: String,
    pub font_size_q16: FontSizeQ16,
    pub font_matrix_q16: AffineQ16,
    pub glyphs: Vec<u16>,
    pub positions_q16: Vec<PointQ16>,
    pub advances_q16: Vec<PointQ16>,
    pub string_indices_utf16: Vec<u32>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PointQ16 { pub x: SignedQ16, pub y: SignedQ16 }

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AffineQ16 {
    pub a: SignedQ16,
    pub b: SignedQ16,
    pub c: SignedQ16,
    pub d: SignedQ16,
    pub tx: SignedQ16,
    pub ty: SignedQ16,
}
```

`SignedQ16` is `round_half_away_from_zero(binary64 * 65_536)`. Nonfinite values and overflow fail.

`utf16be_sha256` hashes Rust `encode_utf16()` units written in order as two-byte big-endian values.

The font size is authored directly as unsigned Q16. It must represent 1 through 1,024 pixels inclusive.
The binary64 value passed to CoreText is `font_size_q16 / 65_536`, which is exact on this platform.

Run ranges must form a gapless, nonoverlapping partition of `[0, utf16_units)` when sorted by start.
Glyph string indices may repeat or move backward inside a run. Each index must still lie within its run range.
`kCFNotFound`, negative ranges, gaps, overlaps, and out-of-range indices fail.

The validator permits CoreText's nonmonotonic status bit. It rejects right-to-left, nonidentity-matrix, and unknown status bits.
Every stored text matrix must quantize to identity.

Glyph ID zero is missing-glyph evidence for the accepted TrueType class and is rejected.
Every distinct run font is table-fingerprinted. Every result must equal the selected `face_id`.
Each run font must also report the planned size, identity font matrix, and no variation dictionary.
Its PostScript name must equal the stored observation, but that name never substitutes for the face fingerprint.

The unit permits at most 256 runs, 16,384 glyphs, and four distinct run-font objects per text item.
All copied glyph, position, advance, and source-index arrays must have the same glyph count.

### Native construction and fallback rejection

The text module uses an exact byte-owned construction path:

```text
verified blob Vec<u8>
  -> copied CFData
  -> CGDataProviderCreateWithCFData
  -> CGFontCreateWithDataProvider
  -> CTFontCreateWithGraphicsFont(size, identity matrix, no attributes)
  -> exact attributed CFString
  -> CTLineCreateWithAttributedString
```

The path never calls a font-registration API and never queries a system family name.

The attributed string sets these values over its complete UTF-16 range:

- `kCTFontAttributeName` to the exact byte-derived `CTFont`;
- `kCTLanguageAttributeName` to the exact accepted language string;
- `kCTWritingDirectionAttributeName` to left-to-right embedding;
- `kCTForegroundColorFromContextAttributeName` to true.

It sets no family name, fallback list, tracking, kerning, paragraph style, or normalization option.

The module round-trips the `CFString` back to UTF-8 before shaping. The bytes must equal the snapshot string.

After shaping, every run font is fingerprinted from its actual tables. A different face fails with `text_font_fallback`.
PostScript-name equality alone never authorizes a run.

### Layout and raster policy

The layout raster uses `[0,width) x [0,height)` with a top-left editor origin.
The baseline is an integer point within the closed box edges.

The baseline x coordinate is the line origin. CoreText shapes and draws the complete line without wrapping, truncation, or alignment adjustment.
Coverage outside the box is intentionally clipped.
The implementation never creates `CTTypesetter` and never enables unbounded layout.

The initial destination supplies canvas `x` and `y`. Width and height equal the raster extent and never animate.

The native alpha context uses:

- eight bits per component and one byte per pixel;
- `kCGImageAlphaOnly` with no color space;
- identity CTM and identity text matrix;
- text position `(baseline.x, height - baseline.y)` in y-up coordinates;
- fill text mode and context gray `(1.0, 1.0)`;
- antialiasing allowed and requested;
- font smoothing disallowed and not requested;
- subpixel positioning disallowed and not requested;
- subpixel quantization disallowed and not requested.

The closed switch tuple calls `CGContextSetAllowsAntialiasing(true)` and `CGContextSetShouldAntialias(true)`.
It calls both `Allows` and `Should` font-smoothing, subpixel-positioning, and subpixel-quantization setters with `false`.

The module reserves and allocates a fixed `Box<[u8]>` before context creation.
`CGBitmapContextCreate` borrows that stable pointer. The context is dropped before the box moves into Rust processing.
The module draws once with `CTLineDraw`; it does not redraw individual runs with a second layout policy.

The canonical top-left mask reverses native rows exactly:

```text
alpha8[top_y * width + x] = native[(height - 1 - top_y) * stride + x]
```

`alpha8_bounds` is the minimal local integer rectangle containing every nonzero byte.
It is `None` exactly when `alpha8_nonzero_pixels` is zero.

The isolated probe must confirm this row contract. A mismatch invalidates Candidate A before runtime integration.

There is zero implicit padding. The explicit box is the clip boundary, including antialiased coverage.
CoreText image bounds are observations only. They do not allocate or enlarge the raster.

The box constraints are:

- width `1..=8192`;
- height `1..=2048`;
- area `1..=4_194_304` pixels;
- baseline x `0..=width`;
- baseline y `0..=height`.

Signed canvas clipping applies after local rasterization. Text has no framing, crop, fit, or contain bars.

### Alpha arithmetic

CoreGraphics supplies glyph coverage only. Rust supplies color and compositing.

Style RGB values are exact editor sample values in the existing unmanaged working-color contract.
The unit performs no ICC, gamma, source-gamut, or font-color conversion.

For coverage `g`, style alpha `a`, and style channel `c`, all in `0..=255`:

```text
g16         = g * 257
a16         = a * 257
c16         = c * 257
intrinsic16 = round_half_up(g16 * a16 / 65535)
premul16    = round_half_up(c16 * intrinsic16 / 65535)
```

For nonnegative integers, `round_half_up(n / 65535)` is `(n + 32767) / 65535`.

The result becomes the existing premultiplied BGRA UNORM16 contribution.
Existing Q16 clip opacity and mask coverage apply afterward in their current order.

No glyph-mask resampling occurs. Movement changes only the integer destination x and y.

Style alpha zero produces zero coverage and zero premultiplied channels. Hidden style RGB cannot affect output.

### Sparse coverage and ordering

The plan's declared span proves only temporal scheduling. It does not claim visible pixels.

Preparation records the full alpha-mask hash and positive count. Execution redraws and compares both.
Per-frame composition still counts actual positive contributions after clipping, opacity, and masks.

Preflight marks no potential coverage when the prepared mask is empty, style alpha is zero, resolved opacity is zero, or geometry is empty.
Any remaining preflight potential is only an admission hint. The actual per-pixel runtime count is authoritative.

A whitespace-only string, style alpha zero, zero mask, or fully clipped box contributes zero.
Such text cannot make an otherwise uncovered frame pass `video_coverage`.

Text and media uses on each track are merged by `timeline_frames.start`.
The no-overlap invariant makes the active item unique. Tracks still compose in vector order from bottom to top.

### Caps and admission

The complete v1 limits are:

| Quantity | Limit |
| --- | ---: |
| Font resources per snapshot | 256 |
| Font imports per commit | 64 |
| Exact font bytes | 1..=16 MiB |
| SFNT tables | 1..=128 |
| Text UTF-8 bytes | 1..=8,192 |
| Text UTF-16 units | 1..=4,096 |
| Text clips per timeline | 4,096 |
| Direct font resources per plan | 64 |
| Lines per item | exactly 1 |
| CoreText runs per item | 256 |
| Glyphs per item | 16,384 |
| Distinct run-font objects | 4 |
| Total UTF-8 bytes per plan | 1 MiB |
| Total UTF-16 units per plan | 524,288 |
| Total runs per plan | 4,096 |
| Total glyphs per plan | 131,072 |
| Final canonical Plan8 JSON | 64 MiB |
| Raster width | 1..=8,192 |
| Raster height | 1..=2,048 |
| Raster pixels | 1..=4,194,304 |
| Font size | Q16 1..=1,024 pixels |
| Nonempty picture tracks | existing 1..=4 |
| Aggregate logical picture estimate | existing 512 MiB |

Admission happens before track workers or media decode start.

Each active text item charges its cached eight-byte premultiplied raster over its full temporal span.
The sweep combines these charges with current movie, PNG, canvas, and writer-side estimates.

Because native text work is serialized, preflight adds one maximum temporary text charge:

```text
3 * font_blob_bytes
+ utf8_bytes
+ 2 * utf16_units
+ 64 * glyph_count
+ raster_pixels               // alpha8 drawing buffer
```

The factor three covers the Rust font buffer, copied `CFData`, and one copied table during run-font fingerprinting.
The persistent premultiplied raster is charged separately.

Every product, sum, byte conversion, and event-sweep update uses checked `u64`, `u128`, or `i128` arithmetic.
Overflow fails before reservation or allocation. No saturating result becomes an admission value.

After each native line reports its counts, preparation checks remaining aggregate run and glyph capacity before allocating Rust observation vectors.
Finalization serializes once into a checked 64 MiB buffer, hashes those exact bytes, and stores the same bytes.

The runtime reserves the persistent permit before allocating the raster. It reserves the temporary permit before reading font bytes.
The temporary permit is released after evidence comparison and premultiplication.

Preparation handles one text item at a time behind the same gate. Its checked logical temporary charge must also remain within 128 MiB.
Preparation retains only serialized evidence after each item; it does not cache native objects or raster bytes across items.

These values are conservative application-owned estimates. CoreText and CoreGraphics internal allocations remain outside the guarantee.

### Ownership, workers, and cancellation

Plan8 keeps one worker per nonempty picture track, capped at four.
Each worker keeps one active media or text cache because items cannot overlap within a track.

The text cache is `Arc<AdmittedTextRaster>`. It contains only Rust-owned premultiplied samples and its budget permit.
No Core Foundation, CoreText, or CoreGraphics object crosses a channel.

Within the gate, retained objects drop in reverse dependency order: line and runs, attributed string, CTFont, CGFont, provider, then CFData.
The bitmap context drops before its boxed alpha buffer. The shaping gate releases only after these drops complete.

Capacity-one request and response channels remain unchanged. The compositor requests one result from each track and blends in order.

A separate cancellable mutex serializes all CoreText and CoreGraphics shaping and drawing.
The design does not depend on a future concurrency probe for correctness.

Cancellation checks occur:

- before waiting for the native-text gate;
- while polling the gate;
- after acquiring the gate;
- before and after each native call;
- before each run copy and table fingerprint;
- before each row conversion and premultiplication;
- before the worker response;
- before writer append.

CoreText and CoreGraphics calls have no cancellation callback. Cancellation may wait for one bounded call to return.
The existing lease, epoch, writer abort, worker join, and publication fences remain authoritative.

### Private execution types

```rust,ignore
pub(crate) struct AdmittedTextRaster {
    pub width: u32,
    pub height: u32,
    pub pixels: Vec<PremulBgra16>,
    pub positive_samples: u64,
    pub permit: composition::Permit,
}

pub(crate) enum TrackUseRef {
    Media(usize),
    Text(usize),
}

pub(crate) enum LayerSourceObservation {
    Media { asset: ContentHash, ordinal: u64, pts: Option<MediaTime> },
    Text { font: ContentHash, text_utf8_sha256: ContentHash },
}

pub(crate) enum SampledLayer {
    NoGeometry,
    ZeroAlpha { bounds: Bounds },
    LegacyOpaque { raster: Raster, permit: Permit },
    AlphaV1 { raster: AlphaRaster16, permit: Permit },
    TextV1 { raster: Arc<AdmittedTextRaster> },
}
```

`TextV1` blends a borrowed rectangular portion of the cached raster. It never clones the canvas or full text raster.

The worker retires the cache after the final frame response is consumed. No acknowledgement channel is added.

## Signatures and policy ownership

The `text` module owns authoring validation, font measurement, preparation shaping, execution comparison, and raster policy.

```rust,ignore
// text/font.rs
pub(crate) fn probe_font_resource(
    path: &Path,
    expected_hash: &ContentHash,
    expected_bytes: u64,
    check: impl FnMut() -> Result<()>,
) -> Result<FontFaceDescriptorV1> {
    unimplemented!("design only")
}

// text.rs
pub(crate) fn normalize_use(
    track: &VideoTrack,
    clip: &TextClip,
    font: &StoredFontResource,
    backend: &TextBackendIdentityV1,
    check: impl FnMut() -> Result<()>,
) -> Result<TextUseDraft> {
    unimplemented!("design only")
}

pub(crate) fn prepare_evidence(
    draft: TextUseDraft,
    blob: &VerifiedSource,
    gate: &NativeTextGate,
    check: impl FnMut() -> Result<()>,
) -> Result<TextUse> {
    unimplemented!("design only")
}

pub(crate) fn reshape_and_rasterize(
    use_: &TextUse,
    resource: &StoredFontResource,
    blob: &VerifiedSource,
    gate: &NativeTextGate,
    budget: &Arc<Budget>,
    check: impl FnMut() -> Result<()>,
) -> Result<Arc<AdmittedTextRaster>> {
    unimplemented!("design only")
}

pub(crate) fn resolve_layer(
    use_: &TextUse,
    local_frame: u64,
    canvas_width: u32,
    canvas_height: u32,
) -> Result<LayerObservation> {
    unimplemented!("design only")
}

pub(crate) fn blend_cancellable(
    canvas: &mut Pixels,
    raster: &AdmittedTextRaster,
    observation: &LayerObservation,
    check: impl FnMut() -> Result<()>,
) -> Result<u64> {
    unimplemented!("design only")
}

pub(crate) fn validate_plan_text_cancellable(
    plan: &ExportPlan,
    features: &PlanFeatures,
    check: impl FnMut() -> Result<()>,
) -> Result<()> {
    unimplemented!("design only")
}

pub(crate) fn require_current_backend(plan: &ExportPlan) -> Result<()> {
    unimplemented!("design only")
}
```

The plan module remains the central plan authority:

```rust,ignore
// plan.rs
pub(crate) fn compile_draft(
    snapshot: Snapshot,
    request: &ExportRequest,
) -> Result<ExportPlanDraft> {
    unimplemented!("design only")
}

pub(crate) fn finalize(
    draft: ExportPlanDraft,
    media: InputEvidence,
    text: Vec<TextUse>,
) -> Result<PreparedExport> {
    unimplemented!("design only")
}

pub(crate) fn validate_prepared_plan_cancellable(
    plan: &ExportPlan,
    check: impl FnMut() -> Result<()>,
) -> Result<()> {
    unimplemented!("design only")
}
```

`ExportPlanDraft` is private and cannot be serialized or stored. Only `finalize` returns a hashable plan.

This prevents the current temporary-empty evidence pattern from becoming a public Plan8 state.
Existing movie and image evidence can enter the same finalization boundary without changing their serialized form.

## Preparation pseudocode

```text
Project::prepare_export(request)
  replay stored plan if request hash matches
    -> validate_prepared_plan_cancellable
    -> verify media blobs and font blobs
    -> require_current_backend only before a new render
    -> return exact stored plan

  verify requested snapshot and every referenced blob
  compile_draft(snapshot, request)
    -> select requested timeline
    -> merge media/text intervals per track
    -> select Plan8 iff selected timeline directly uses text
    -> retain old schema selector byte-for-byte otherwise
    -> normalize x/y/opacity and masks
    -> collect exactly directly used font resources
    -> measure CoreText/CoreGraphics bundle versions once

  acquire serialized native-text gate for each text use in stable track/start order
    -> read and rehash font blob under temporary admission
    -> reconstruct exact face
    -> round-trip exact UTF-8 through CFString
    -> shape one CTLine
    -> copy and validate every run observation
    -> reject fallback, glyph zero, RTL, or nonidentity matrices
    -> draw alpha8 into explicit layout box
    -> reverse rows and hash alpha8
    -> scan positive count and local bounds
    -> drop all native objects and temporary pixels

  obtain current movie/image decode evidence
  finalize draft exactly once
    -> attach text and media evidence
    -> validate_prepared_plan_cancellable
    -> compute plan_id from final JSON bytes
  CAS-store the final plan under the existing export intent
```

Preparation and execution call the same private shaping function with different result modes.
The policy is not reimplemented in `plan.rs` or `layers.rs`.

## Execution pseudocode

```text
movie::render Plan8
  validate_prepared_plan_cancellable
  require_current_backend
  composition::preflight_cancellable before spawning workers or decoding media
  spawn at most four existing picture-track workers

each track worker
  merge TrackUseRef values by start frame
  on first frame of a text clip:
    reserve persistent raster and maximum temporary payload
    wait cancellably for native-text gate
    read and rehash exact font blob
    shape and copy observations
    compare every observation with prepared TextShapingEvidenceV1
    draw canonical alpha8 and compare hash/count/bounds
    convert alpha8 + style RGBA8 to cached PremulBgra16
    release temporary payload and all native objects
  return Arc<AdmittedTextRaster> through capacity-one response channel
  retire cache after final clip frame

ordered compositor
  resolve x/y/opacity and mask for the local frame
  clip box against canvas
  blend positive cached samples through existing Q16 weight policy
  count actual positive contributions
  fail video_coverage when the total is zero
  append only after cancellation and observer checks
```

## Central schema and tamper validation

`PlanFeatures::derive` reconstructs features only from the embedded selected timeline and closures.
It is the sole schema-selection authority.

```text
if directly_used_text              -> schema 8
else if directly_used_alpha_image  -> schema 7
else if mask                       -> schema 6
else if motion                     -> schema 5
else if layered_or_placement       -> schema 4
else if image                      -> schema 3
else                               -> schema 2
```

For Plan8, alpha policy remains conditional on directly used transparent PNGs.
Text does not impersonate PNG alpha evidence.

`validate_prepared_plan_cancellable` performs all structural checks:

- schema exactly matches derived features;
- media uses match media clips one-to-one;
- text uses match text clips one-to-one in stable order;
- media and text spans share the track no-overlap invariant;
- direct font closure equals the used-font set exactly;
- font descriptors and face IDs agree with snapshot resources;
- text source observations recompute from exact snapshot strings;
- normalized placement, motion, mask, style, and layout match authoring;
- shaping evidence is complete, bounded, and internally coherent;
- Plan8 alpha policy and image evidence follow existing alpha rules;
- legacy schemas contain no font, text, or text-policy fields;
- Plan8 has one closed text policy and one backend identity.

Every plan admission site calls this function directly or through `validate_decode_evidence`:

- stored-plan replay in `project.rs`;
- pixel extent and renderer admission in `movie.rs`;
- dynamic allocation preflight in `composition.rs`;
- track worker startup in `layers.rs`;
- completed verification in `exports.rs`;
- finalizing recovery in `exports.rs`.

Range checks such as `2..=7`, `4..=7`, and `5..=7` must not become independent Plan8 authorities.

Execution additionally calls `reshape_and_rasterize`, which compares actual framework output with immutable evidence.
Historical output verification validates stored structure and reopens media. It does not reshape text on a newer host.

## Compatibility contract

### Snapshot schema1

Snapshot schema remains 1. These absent fields use both `default` and `skip_serializing_if`:

- `CommitProject::font_imports`;
- `Snapshot::font_resources`;
- `VideoTrack::text_clips`.

Existing serialized snapshots and commit request hashes therefore retain their bytes when text is absent.

`Studio::create_project` initializes an empty font map. Serialization omits it.

### Plan2 through Plan7

The three new plan fields are also defaulted and skipped when empty.
The old schema selector and validation behavior remain unchanged for text-free timelines.

A real Plan7 serialization fixture is now frozen before text runtime integration.
Existing Plan2 through Plan6 fixtures and every known legacy hash remain exact.

| Frozen legacy document | SHA-256 |
| --- | --- |
| Plan7 alpha plus NativeColorMasterV2 | `a771942c48dc0e9b1832bb81bccb56fe21e074fe58546f9c49a3bc95a1ec91a2` |
| Snapshot1 with transparent PNG | `22619ba0bae6681d1da67cb65b3c850ecacef31a05c2d8ab13d082eae1af9e73` |
| Receipt4 alpha plus NativeColorMasterV2 | `ba96d0b9d262bd424b4785324c38d3609ed3d5a563fe784382e3a988a6cfd259` |

### Receipt2 through Receipt4

Text does not select a receipt schema. Receipt schema still depends only on `MovieProfile`.

No text field is added to `ArtifactReceipt`, `NativeMeasurements`, or `NativeFormatContract`.
The receipt already binds `plan_id`, renderer identity, exact output bytes, and technical measurements.

Historical V1, V2, and H.264 artifacts retain unchanged readback behavior.

### Backend identity

`BuildIdentity` keeps its existing serialized shape and `native_backend` string.
Plan8 alone carries `TextBackendIdentityV1` with CoreText and CoreGraphics bundle identifiers and version strings.

As with every new executable, future measurements receive that executable and lock hash.
This does not rewrite stored identities or add text backend fields to a text-free plan.

Preparing or rendering Plan8 requires the current bundle tuple to equal its plan.
Reopening a historical artifact does not claim that a newer host can reproduce its text pixels.

The Cargo lock hash already binds the exact Rust framework crate versions.
The initial compatibility claim is limited to 64-bit macOS and the exact plan-bound framework tuple.
The SDK and Command Line Tools versions belong in probe manifests because they do not determine historical runtime readback.

## Module map

| Module | Ownership after this unit | Concrete edit pressure |
| --- | --- | --- |
| `model.rs` | Snapshot font resources and text authoring | Add skipped fields and types; validate cross-kind overlap and caps |
| `project.rs` | One commit transaction and blob CAS | Factor byte staging; stage font imports; verify font blobs; preserve replay |
| `media.rs` | Timed movie/audio and PNG dispatch | No font or text shaping logic |
| new `text/font.rs` | Bounded SFNT structure and face fingerprint | Parse exact tables; reject unsupported fonts; no native layout |
| new `text.rs` | Complete native text contract | Shape, observe, fallback-check, draw alpha8, compare, premultiply |
| `plan.rs` | Schema selection and central plan validation | Add private draft/finalize boundary, Plan8 fields, feature derivation |
| `motion.rs` or `text.rs` | Text x/y/opacity normalization | Reuse curve evaluator without exposing width/height |
| `mask.rs` | Existing analytic axis coverage | Reuse normalized mask against the text box window |
| `alpha_picture.rs` | Premultiplied UNORM16 arithmetic | Add private solid-color coverage constructor; retain existing blend math |
| `composition.rs` | Ordered geometry and aggregate admission | Resolve fixed text rectangles; account cached and temporary payloads |
| `layers.rs` | Bounded per-track actors | Merge media/text uses; cache one Rust text raster; keep capacity one |
| `movie.rs` | Native writer and reader | Admit Plan8 through central validator; no text policy duplication |
| `exports.rs` | Export replay, verification, recovery | Replace local schema gates with central admission |
| `identity.rs` | Existing renderer identity | No serialized change |
| `native_format.rs` | Container, codec, audio, output color | No change |
| `crates/editor/Cargo.toml` | Direct native dependency closure | Pin CoreText, CoreGraphics, and required CoreFoundation features explicitly |
| `crates/cli/src/main.rs` | JSON operations and capability truth | Export new model types; update text status only after proof |

Effect adapters remain outside this module map. No subprocess or FFmpeg/libav path is introduced.

## Resolution of the twenty grounding decisions

| # | Decision | Candidate A resolution |
| ---: | --- | --- |
| 1 | Font storage | Separate `font_resources` map and `font_imports`; shared blob CAS |
| 2 | Untimed lineage | `FontResourceOrigin::Imported` has no `SourceRange`; first unit rejects derived fonts |
| 3 | TTC/OTC | Reject collections; accepted face index is always zero |
| 4 | Variable fonts | Reject every variable-font table and nonempty native variation observation |
| 5 | Line model | Exactly one line; reject line separators and wrapping controls |
| 6 | Direction | Explicit LTR only; reject bidi controls and RTL shaped runs |
| 7 | Geometry | Caller supplies integer destination box and local top-left integer baseline |
| 8 | Precision | Font size is unsigned Q16; native observations are signed Q16 with half-away rounding |
| 9 | Raster bounds | Raster is exactly integer width by height; no bounds-derived allocation |
| 10 | Padding | Zero implicit padding; the caller's explicit box is the intentional clip |
| 11 | Raster switches | Gray alpha8, AA on, smoothing/subpixel positioning/subpixel quantization off |
| 12 | Face fingerprint | Domain-separated SHA-256 over tag-sorted exact table digests and lengths |
| 13 | Missing glyphs | Reject glyph zero, plus require every run font fingerprint to equal the selected face |
| 14 | Run ranges | Require a full range partition; permit repeated or nonmonotonic per-glyph indices |
| 15 | Size motion | Reject width/height motion; allow only x/y/opacity and existing axis masks |
| 16 | Limits | Use the exact caps in the admission table above |
| 17 | Concurrency | Serialize shaping and drawing behind one cancellable gate |
| 18 | Backend identity | Store CoreText/CoreGraphics bundle tuple only in Plan8 `text_policy` |
| 19 | Plan schema | Plan8 subsumes earlier picture features and keeps conditional PNG alpha policy |
| 20 | Fixture authority | Commit-pinned Noto Telugu and Devanagari fonts plus an independent Swift/CoreText producer |

## Proof plan

### 1. Isolated native feasibility probe first

Before product integration, build a standalone Rust probe with explicit pinned objc2 features.
It must not link to the editor crate.

The probe uses these acquired static fixtures:

| Font | Bytes | SHA-256 |
| --- | ---: | --- |
| Noto Sans Telugu Regular | 197,228 | `2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f` |
| Noto Sans Devanagari Regular | 219,212 | `385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d` |

Their acquisition manifest binds `notofonts/noto-fonts` commit `ffebf8c1ee449e544955a7e813c54f9b73848eac`.
The preserved OFL accompanies the fixtures.

The current manifest proves only raw container structure. It does not prove shaping or pixels.

The probe must prove:

- the exact byte-owned CGFont and CTFont construction path;
- Telugu and Devanagari shaping with combining marks and conjuncts;
- full UTF-16 ranges without one-character-to-one-glyph assumptions;
- actual run-font table fingerprints and empty variation state;
- missing-glyph fallback rejection;
- alpha-only context creation and every raster switch;
- y-up drawing and exact top-left row reversal;
- deterministic alpha-mask hashes across repeated calls in one process;
- bounded cancellation before and after native calls;
- actual CoreText and CoreGraphics bundle versions.

The frozen synthetic input set includes Telugu and Devanagari conjuncts, marks, whitespace, large 512-pixel marks, and a 48.25-pixel size.
It also includes whitespace-only, emoji, and unassigned-code-point negatives.
Combining-only and ZWJ cluster cases remain observations until the probe establishes an accepted invariant.

If row orientation, fallback observation, or alpha pixels disagree with this contract, implementation stops and the design is revised.

### 2. Independent shaping and raster fixtures

A separate Swift executable uses direct CoreText/CoreGraphics APIs. It shares no Rust text module.

It writes a canonical manifest containing:

- exact input UTF-8 and UTF-16BE hashes;
- font byte and face-table identities;
- language, direction, size, box, and baseline;
- every run range, status, glyph, position, advance, and source index;
- quantized line geometry;
- exact alpha8 hash, positive count, and bounds;
- framework versions and producer hash.

Fixtures cover Telugu, Devanagari, ASCII, leading/trailing whitespace, zero-width sequences, combining marks, conjuncts, and missing glyphs.

The Swift producer is an independent implementation comparison. CoreText remains the selected shaping authority.

### 3. Exact pure arithmetic vectors

Independent vectors compare every output channel for:

- alpha8 coverage times style alpha;
- straight style RGB to premultiplied UNORM16;
- Q16 clip opacity;
- horizontal and vertical axis masks;
- signed canvas clipping;
- bottom-to-top order with movie, PNG, and text;
- style alpha zero and mask zero;
- half-value rounding boundaries.

These vectors use no CoreText call.

### 4. Product compatibility and tamper tests

Tests freeze and compare:

- the real current Plan7 fixture before integration;
- all current snapshot, Plan2 through Plan6, and Receipt2 fixture hashes;
- existing Plan7 behavioral baselines;
- text-free Plan2 through Plan7 serialization after the new skipped fields exist.

Plan8 tests prove:

- only text in the requested timeline selects schema8;
- unused font resources and text on an unselected timeline do not select schema8;
- mixed text, transparent PNG, masks, motion, and NativeColorMasterV2 retain all policies;
- font bytes, table identity, text, UTF-16 counts, language, direction, style, box, baseline, motion, mask, backend, runs, or alpha hash cannot be forged;
- missing, duplicated, reordered, or substituted text uses fail centrally;
- replay, export, verify, cancellation, and staging recovery admit one valid Plan8;
- legacy recovery behavior is unchanged;
- a fully invisible sole text item fails actual frame coverage;
- sparse invisible text over a visible lower movie preserves truthful source observations;
- permits are released after the final text sample and every cancellation path.

### 5. Ordinary native output proof

The public CLI prepares and exports one exact Plan8 through `NativeColorMasterV2`.

The timeline includes:

- a real movie lower track;
- a transparent PNG overlay;
- Telugu and Devanagari text on separate tracks and overlapping spans;
- signed clipping, x/y and opacity motion, and an axis mask;
- invisible whitespace or alpha-zero negative controls;
- the canonical 24-bit, 48 kHz, stereo unity-audio interval.

A private test-only borrowed-frame observer binds the exact prepared plan ID.
It compares every prehandoff BGRA frame against independent expected hashes.

The ordinary verifier reopens the final movie and checks all frame clocks, source observations, exact PCM, opaque decoded alpha, and V2 color tuples.
Independent ROIs use the fixed master policy. H.264 remains a technical smoke output, not a fidelity reference.

The proof establishes bounded technical behavior only. It does not establish lyric wording, timing, readability, hearing, pilot approval, or film acceptance.

## Rationale

The public interface remains deep: callers state text, font identity, style, time, box, and baseline through one commit.
They do not coordinate font loading, shaping, fallback checks, raster buffers, worker caches, or native framework objects.

Keeping font resources outside `StoredAsset` preserves the meaning of timed source ranges.
Keeping text clips inside `VideoTrack` preserves one z-order authority without rewriting legacy `VideoClip` bytes.

The explicit box makes clipping, allocation, placement, and motion deterministic.
It also moves intentional clipping into caller-visible data instead of hidden glyph-bound padding.

One text module owns both preparation and execution. This prevents shaping policy from leaking across model, plan, and worker modules.
The central plan validator remains the only schema authority.

This follows boundary discipline: external JSON and native observations become validated domain types at their boundaries.
It follows type-system discipline: unsupported size motion, direction, face selection, and font classes are absent from accepted types.

## Tradeoffs accepted

- We accept explicit layout-box clipping in exchange for stable geometry and bounded allocation.
- We accept TrueType-only static fonts in exchange for a small, auditable first contract.
- We accept duplicated shaping during preparation and execution in exchange for immutable tamper evidence.
- We accept serialized native text calls in exchange for simple ownership and bounded concurrency.
- We accept Plan8 host-version specificity in exchange for honest pixel reproducibility claims.
- We accept separate media and font metadata maps in exchange for correct untimed resource semantics.
- We accept per-track raster duplication in exchange for no shared mutable cache between workers.

## Alternatives considered

### Font as `MediaKind::Font`

This reuses `StoredAsset` but forces `SourceRange`, stream kind, and positive spans onto untimed bytes.
The shallow reuse leaks media semantics into every font caller, so it loses.

### Pre-render text into PNG assets

This fits the existing alpha path but removes source text, language, face, shaping, and baseline authority.
Callers would have to coordinate an external renderer, so the interface becomes shallower and unverifiable.

### Separate text tracks

Separate tracks make text storage simple but require a second cross-kind z-order protocol.
Adding skipped text clips to existing tracks preserves the one ordering truth.

### Replace every media clip with a tagged `PictureItem`

This is clean for a new system, but it changes every existing snapshot's serialized clip structure.
Append-only `text_clips` gives the same runtime merge without changing legacy bytes.

### Tight glyph surfaces with derived anchors

Tight surfaces use less memory, but CoreText image bounds exclude raster coverage.
Padding and anchor rules would become hidden caller semantics and unstable clipping boundaries.

### Store glyph outlines and skip execution reshaping

Outline storage could avoid runtime layout changes, but it makes the plan large and creates a second renderer contract.
It also stops verifying that the authorized native shaper still produces the planned result.

## Red-flag screen

| Red flag | Candidate A response |
| --- | --- |
| Shallow module | Existing Project operations hide the complete native text pipeline |
| Native type leakage | No CoreText/CoreGraphics object or wire type is public or crosses a channel |
| Mutable system lookup | Fonts come only from exact project blob bytes |
| Silent fallback | Every actual run font is table-fingerprinted and compared |
| Temporal decomposition | `text.rs` owns font-to-observation-to-raster policy at prepare and execute time |
| Duplicate schema authority | One central validator derives and admits Plan2 through Plan8 |
| Implicit geometry | Integer box, baseline, quantization, row transform, and clipping are explicit |
| Unbounded native work | Input, glyph, run, table, and raster caps bound each uncancellable call |
| False memory guarantee | The 512 MiB value is labeled an application-owned estimate |
| Legacy byte drift | Every new field is defaulted and skipped; text-free schema selection is unchanged |
| Creative overclaim | Proof claims stop at bounded technical output behavior |

## Synthesis decision

No synthesis decision is made in Candidate A. The parent comparison selects or grafts the final design.

## Open risks before implementation

- Will the isolated probe confirm the assumed alpha-only bitmap row order on the installed SDK?
- Will CoreText expose every fallback run through a fingerprintable `CTFont` attribute for the negative fixture?
- Will the chosen antialias switches produce stable repeated alpha8 hashes on the bound host and architecture?
- Does the explicit 4,194,304-pixel text cap leave enough aggregate headroom for the largest supported canvas fixture?
- Will direct SFNT table parsing need a vetted crate after the probe exposes malformed-font edge cases?

These are probe outcomes, not unresolved authoring decisions.

## Next implementation step

Build the isolated Rust CoreText/CoreGraphics probe against the two frozen Noto fixtures, then compare it with the independent Swift manifest.
