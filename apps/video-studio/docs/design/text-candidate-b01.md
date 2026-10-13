# Native text and story graphics, candidate B

## Usage (caller's view)

The caller imports an exact font blob, places text in a picture track, and keeps the existing export workflow. The caller never sees CoreText, CoreGraphics, glyph IDs, or a text worker.

```rust
let revision = project.commit(CommitProject {
    intent: EntityId::parse("add-telugu-title")?,
    base_revision: head.receipt.revision,
    imports: vec![movie_import, master_audio_import],
    font_imports: vec![FontImport {
        path: licensed_noto_telugu.clone(),
        expected_hash: ContentHash::parse(
            "2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f",
        )?,
        expected_bytes: 197_228,
        origin: FontOrigin::Imported {
            external_source: "licensed-noto-ofl".into(),
            role: "telugu-title-face".into(),
        },
    }],
    canonical_audio: Some(master_audio_binding),
    timelines: vec![Timeline {
        id: EntityId::parse("main")?,
        frame_count: 72,
        video_tracks: vec![VideoTrack {
            id: EntityId::parse("title-over-picture")?,
            clips: vec![],
            text_clips: vec![TextClip {
                id: EntityId::parse("title")?,
                timeline_frames: Span { start: 8, length: 48 },
                text: "తెలుగు కథ".into(),
                font: ContentHash::parse(
                    "2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f",
                )?,
                language: LanguageTag::new("te")?,
                direction: TextDirection::Ltr,
                font_size: FontSizeQ16::from_video_pixels(64.0)?,
                color: TextColor::rgba8(255, 255, 255, 255),
                placement: TextPlacement {
                    anchor: BaselineAnchor { x: 120, baseline_y: 420 },
                    opacity: Opacity::new(1.0)?,
                },
                motion: None,
                mask: None,
            }],
        }],
        audio_tracks,
    }],
})?;

let request = ExportRequest {
    intent: EntityId::parse("export-title-a01")?,
    revision: revision.revision,
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::NativeColorMasterV2,
};
let prepared = project.prepare_export(request.clone())?;
let exported = project.export(request.clone())?;
let verified = project.verify_export(request.intent.clone())?;
assert_eq!(verified.receipt.artifact.plan_id, exported.receipt.artifact.plan_id);
```

The text span is sparse. A lower movie or image track must cover the other frames. A text-only frame is accepted by preparation only when its declared span is covered; execution still requires positive visible contribution.

A second direct callsite uses the same public types for a Devanagari overlay and a simple fade. The fade is an opacity curve. Anchor motion remains baseline motion, so the caller does not guess the shaped surface dimensions.

```rust
let devanagari = TextClip {
    id: EntityId::parse("chapter-hi")?,
    timeline_frames: Span { start: 32, length: 24 },
    text: "देवनागरी".into(),
    font: devanagari_font_hash,
    language: LanguageTag::new("hi")?,
    direction: TextDirection::Ltr,
    font_size: FontSizeQ16::from_video_pixels(48.0)?,
    color: TextColor::rgba8(255, 220, 160, 240),
    placement: TextPlacement {
        anchor: BaselineAnchor { x: -20, baseline_y: 160 },
        opacity: Opacity::new(0.0)?,
    },
    motion: Some(TextMotion {
        x: None,
        baseline_y: None,
        opacity: Some(PropertyCurve {
            keys: vec![
                CurveKey { frame: 0, value: Opacity::new(0.0)?, to_next: Some(CurveInterpolation::Linear) },
                CurveKey { frame: 12, value: Opacity::new(1.0)?, to_next: None },
            ],
        }),
    }),
    mask: Some(axis_reveal_mask),
};
```

Cancellation and reconciliation stay the existing operations. A caller may call `Project::cancel_export(intent)` after `export` starts, then `Project::reconcile_export_staging()`. Neither operation exposes a text-specific handle.

## Problem

The editor currently serializes exact schema-1 snapshots and Plan2 through Plan7 while `VideoClip` only names movie or image assets. Text must become a picture contribution without changing those bytes when text is absent. Candidate B uses a separate non-timed font resource and a shaper-derived tight surface. A baseline anchor keeps caller geometry independent from CoreText bounds, while one private text kernel owns import observation, shaping, rasterization, and execution comparison. Movie and audio processing remain native AVFoundation paths; this unit adds no FFmpeg, libav, subprocess, or Effect adapter.

## Shape

### Authoring types

These are public domain values. They do not expose framework or storage objects.

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FontImport {
    pub path: PathBuf,
    pub expected_hash: ContentHash,
    pub expected_bytes: u64,
    pub origin: FontOrigin,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum FontOrigin {
    Imported {
        external_source: String,
        role: String,
    },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FontResource {
    pub hash: ContentHash,
    pub bytes: u64,
    pub origin: FontOrigin,
    pub face: FontFaceObservation,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FontFaceObservation {
    pub container: FontContainer,       // StandaloneTrueType only in unit 1.
    pub face_index: u16,                // Always zero in unit 1.
    pub table_fingerprint: ContentHash,
    pub postscript_name: String,        // Observation, never an authority.
    pub glyph_count: u32,
    pub units_per_em: u16,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum FontContainer { StandaloneTrueType }

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextClip {
    pub id: EntityId,
    pub timeline_frames: Span,
    pub text: String,                   // Exact UTF-8. No normalization.
    pub font: ContentHash,
    pub language: LanguageTag,
    pub direction: TextDirection,       // Only Ltr is accepted initially.
    pub font_size: FontSizeQ16,
    pub color: TextColor,               // Solid straight RGBA8.
    pub placement: TextPlacement,
    pub motion: Option<TextMotion>,     // Anchor x/y and opacity only.
    pub mask: Option<PictureMask>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextPlacement {
    pub anchor: BaselineAnchor,
    pub opacity: Opacity,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BaselineAnchor {
    pub x: i32,                         // Canvas x, positive right.
    pub baseline_y: i32,                // Canvas y, positive down.
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextMotion {
    pub x: Option<PropertyCurve<i32>>,
    pub baseline_y: Option<PropertyCurve<i32>>,
    pub opacity: Option<PropertyCurve<Opacity>>,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct FontSizeQ16(u32);             // 16 fractional bits, video pixels.

impl FontSizeQ16 {
    pub fn from_video_pixels(value: f64) -> Result<Self>; // finite, 1..=512 px, half-away quantization
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct TextColor { pub r: u8, pub g: u8, pub b: u8, pub a: u8 }

impl TextColor {
    pub const fn rgba8(r: u8, g: u8, b: u8, a: u8) -> Self;
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LanguageTag(String);          // Strict ASCII UTS-35 subtags; each is 2..=8 bytes.

impl LanguageTag {
    pub fn new(value: impl Into<String>) -> Result<Self>; // bounded ASCII language/script/region subtags
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum TextDirection { Ltr }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Utf16Range { pub start: u32, pub length: u32 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Q16Point { pub x: i64, pub y: i64 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Q16Size { pub width: i64, pub height: i64 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Q16Rect { pub min_x: i64, pub min_y: i64, pub max_x: i64, pub max_y: i64 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct SignedPixelPoint { pub x: i32, pub y: i32 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct TextMatrixIdentity { pub a_q16: i64, pub b_q16: i64, pub c_q16: i64, pub d_q16: i64 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct TextRunStatus { pub right_to_left: bool, pub non_identity_matrix: bool, pub raw_bits: u32 }

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct TextRasterPolicy {
    pub schema: u32,
    pub grayscale_antialias: bool,
    pub font_smoothing: bool,
    pub subpixel_positioning: bool,
    pub alpha_only: bool,
    pub padding_px: u8,
    pub outer_guard_px: u8,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextBackendIdentity {
    pub schema: u32,
    pub core_text_bundle: String,
    pub core_graphics_bundle: String,
}
```

`VideoTrack` gains `text_clips: Vec<TextClip>` after `clips`, with `#[serde(default, skip_serializing_if = "Vec::is_empty")]`. `CommitProject` gains `font_imports: Vec<FontImport>` with the same omission rule. `Snapshot` gains `fonts: BTreeMap<ContentHash, FontResource>` with `#[serde(default, skip_serializing_if = "BTreeMap::is_empty")]`. Empty fields therefore leave existing request and snapshot bytes unchanged.

Validation combines media and text spans before calling the existing overlap check. The track vector remains the only bottom-to-top authority. A text font must exist in `Snapshot::fonts`, but it never becomes `MediaKind`, `MediaDescriptor`, or a `SourceRange`. Its only first-unit lineage is `FontOrigin::Imported`.

### Normalized plan types

Text selects Plan8 only when at least one `TextClip` is directly used by the requested timeline. The old compiler continues to emit Plan2 through Plan7 for timelines without text.

```rust
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextUse {
    pub clip: EntityId,
    pub track: EntityId,
    pub timeline_frames: Span,
    pub font: ContentHash,
    pub pose: PlannedTextPose,
    pub shape: TextShapeEvidence,
    pub surface: TextSurface,
    pub mask: Option<PlannedPictureMask>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PlannedTextPose {
    pub x: PlannedCurve<i32>,
    pub baseline_y: PlannedCurve<i32>,
    pub opacity_q16: PlannedCurve<OpacityQ16>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextShapeEvidence {
    pub utf8_sha256: ContentHash,
    pub utf8_bytes: u32,
    pub utf16_units: u32,
    pub utf16_sha256: ContentHash,
    pub language: LanguageTag,
    pub direction: TextDirection,
    pub font_size_q16: u32,
    pub color: TextColor,
    pub line_range: Utf16Range,
    pub line_origin_q16: Q16Point,
    pub text_matrix: TextMatrixIdentity,
    pub runs: Vec<TextRunEvidence>,
    pub ideal_bounds_q16: Q16Rect,
    pub raster_policy: TextRasterPolicy,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextRunEvidence {
    pub string_range: Utf16Range,
    pub status: TextRunStatus,
    pub font_face_fingerprint: ContentHash,
    pub glyphs: Vec<GlyphEvidence>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GlyphEvidence {
    pub glyph_id: u16,
    pub utf16_index: u32,
    pub position_q16: Q16Point,
    pub advance_q16: Q16Size,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TextSurface {
    pub width: u32,
    pub height: u32,
    pub top_left_from_baseline: SignedPixelPoint,
    pub padding_px: u8,                 // Exactly two.
    pub outer_guard_px: u8,              // Exactly one.
    pub coverage_sha256: ContentHash,
    pub nonzero_bounds: Option<PixelRect>,
}

pub(crate) struct TextDecision {
    pub(crate) frame: u64,
    pub(crate) surface: crate::alpha_picture::AlphaRaster16,
    pub(crate) observation: LayerObservation,
}
```

`ExportPlan` adds skipped-empty `font_closure`, `text`, and `text_backend` fields. Plan8 requires all three. The existing `source_closure`, `video`, `audio`, `decode_evidence`, `image_decode_evidence`, and `alpha_policy` remain authoritative for media. Plan8 reuses alpha policy and image evidence when transparent or opaque images are present. It does not duplicate a frame trace or add receipt fields.

`TextShapeEvidence` is the single normalized shaping observation. `TextSurface::coverage_sha256` is the preparation mask hash. The original string remains in `plan.timeline`; the hash and byte count bind it to the observed UTF-16 coverage. `font_closure` carries the non-timed font lineage and face table identity.

### Signatures and ownership

The following are design-only signatures. Their bodies remain `not implemented` until a selected probe and runtime contract exist.

```rust
// project.rs
fn stage_font(&self, import: &FontImport) -> Result<FontResource>;

// text.rs; all framework values remain private to this module.
pub(crate) fn prepare(
    clip: &TextClip,
    font: &FontResource,
    blob: &Path,
    canvas: PixelRect,
    backend: &TextBackendIdentity,
    budget: &Arc<Budget>,
    check: impl FnMut() -> Result<()>,
) -> Result<TextUse>;

pub(crate) fn execute(
    use_: &TextUse,
    frame: u64,
    font: &FontResource,
    blob: &Path,
    plan: &ExportPlan,
    budget: &Arc<Budget>,
    check: impl FnMut() -> Result<()>,
) -> Result<TextDecision>;

// plan.rs
pub(crate) fn validate_text_plan(plan: &ExportPlan) -> Result<()>;
pub(crate) fn normalize_text_pose(
    clip: &TextClip,
    frames: u64,
) -> Result<PlannedTextPose>;

// composition.rs
pub(crate) fn resolve_text_layer(
    use_: &TextUse,
    local_frame: u64,
    canvas: PixelRect,
) -> Result<LayerObservation>;

// layers.rs
fn run_track(/* existing bounded request/response port */) -> Result<()>;
fn execute_text_source(/* private text use and one-frame request */) -> Result<Decision>;
```

`TextDecision` contains only Rust-owned coverage and a resolved observation. It contains no `CTFont`, `CTLine`, `CTRun`, `CGContext`, `CFData`, or raw framework pointer. The text module drops every native object before returning. The existing capacity-one port applies backpressure. A track worker retains at most one active text source and retires it after its last frame.

The `prepare` and `execute` functions share one private `TextKernel`. `TextKernel::observe` and `TextKernel::rasterize` are policy-owned methods, not independent public stages. Preparation stores their normalized evidence. Execution repeats both methods and compares every observed field before publishing a raster.

## Pseudocode

```text
Project::commit
  stage each FontImport through the same CAS transaction as media imports
  parse the blob as one standalone static TrueType face
  record FontFaceObservation and store FontResource in Snapshot::fonts
  validate every text font reference and merged track span

Project::prepare_export
  compile media uses exactly as today
  for each directly used TextClip:
    reserve logical font, string, glyph, guard-buffer, and raster budget
    create CFString from exact UTF-8 and require a byte-for-byte UTF-8 round trip
    TextKernel::shape with explicit CTFont, language, and LTR
    reject fallback, glyph zero, bad ranges, and non-finite geometry
    quantize observations and derive the padded tight surface
    draw into a guarded alpha-only bitmap
    copy rows to top-left Rust order, then drop CGContext and native objects
    require coverage to stay inside the outer guard
    normalize baseline pose and existing axis mask
  select schema 8 and hash one plan containing all text evidence

layers worker for a requested frame
  select the one text or media item whose span covers this track frame
  for text, check cancellation and enter the serialized native text gate
  reshape and rerasterize the bounded text source
  compare shape, policy, face, UTF-16 coverage, surface, and mask hash
  leave the gate, resolve anchor to fixed surface rectangle, and compose
  send one Rust-owned decision through the capacity-one response channel

ordered compositor
  receive one decision per bottom-to-top track
  apply existing clip opacity and axis-mask coverage
  blend text premultiplied contribution with existing alpha arithmetic
  reject a frame with no positive contribution
```

### Tight surface and coordinate proof

The native line uses a y-up baseline at `(0, 0)`. Quantized ideal bounds are signed Q16.16 values. Lower bounds use fixed-point floor. Upper bounds use fixed-point ceil. The integer surface is:

```text
x0 = floor(min_x_q16) - 2
x1 = ceil (max_x_q16) + 2
y0 = floor(min_y_q16) - 2
y1 = ceil (max_y_q16) + 2
width  = x1 - x0
height = y1 - y0
top_left_from_baseline = (x0, -y1)
```

The renderer allocates a one-pixel outer guard around that surface. It draws the line translated by `(-(x0 - 1), -(y0 - 1))` in native y-up coordinates. Native row `h - 1 - top_y` becomes editor row `top_y`. The outer guard must remain zero. Any touched guard pixel rejects the source with `text_bounds_insufficient_padding`; no clipped coverage is silently accepted. The returned `TextSurface` excludes the guard and includes the declared two-pixel anti-alias padding.

The caller anchor is the baseline origin. The compositor computes:

```text
destination.x = resolved_anchor.x + surface.top_left_from_baseline.x
destination.y = resolved_anchor.baseline_y + surface.top_left_from_baseline.y
destination.width  = surface.width
destination.height = surface.height
```

This formula is integer and signed. Off-screen rectangles clip through the existing mapping. Text never enters `Framing`; it is not scaled or resampled. Width and height stay fixed for the entire text span.

### Alpha and raster policy

The alpha-only CoreGraphics buffer contains coverage only. `TextKernel` converts each coverage byte with the existing UNORM16 policy before composition:

```text
coverage16 = coverage8 * 257
style_alpha16 = color.a * 257
intrinsic16 = round_half_up(coverage16 * style_alpha16 / 65535)
channel16 = round_half_up((color.channel * 257) * intrinsic16 / 65535)
```

The returned channels are premultiplied BGR16 and the returned coverage is `intrinsic16`. Existing compositor code applies clip opacity and mask Q16 weights. It performs no text-specific blend or floating-point color conversion. Zero style alpha produces zero coverage, so hidden RGB cannot fabricate a visible contribution.

`TextRasterPolicyV1` is closed and stored in every Plan8 text use: grayscale antialiasing enabled, font smoothing disabled, subpixel positioning disabled, subpixel quantization represented by Q16 geometry, alpha-only `CGBitmapContext`, native y-up draw, top-left row copy, padding 2, and guard 1. The feasibility probe must fail if the selected CoreGraphics calls cannot enforce these settings.

### Shape and fallback proof

The kernel accepts only a standalone SFNT with scalar `0x00010000`, `glyf`, `loca`, `head`, `maxp`, `hhea`, `hmtx`, `cmap`, `name`, `OS/2`, and `post` tables. It rejects `ttcf`, `OTTO`, `typ1`, `CFF `, `CFF2`, `fvar`, `gvar`, `HVAR`, `VVAR`, `MVAR`, `COLR`, `CPAL`, `CBDT`, `CBLC`, `sbix`, and `SVG ` tables. Malformed directories, duplicate tags, zero units-per-em, zero glyph count, and multiple CoreText descriptors also reject.

The face fingerprint is:

```text
SHA256("video-studio-text-face-v1\0"
       || sfnt_scalar_be
       || face_index_be_u16
       || for table tags sorted ascending:
            tag[4] || byte_length_be_u64 || raw_table_bytes)
```

Only face index zero is legal. The table fingerprint, not PostScript name, is the identity. The font blob hash remains a separate identity. There are no variation axes in this unit.

The kernel creates `CFData` from the verified blob, then creates `CGFont` and `CTFont` from that byte-owned data. It never calls registration or family lookup. Every run font fingerprint must equal the selected face fingerprint. A glyph ID of zero is missing-glyph evidence for the accepted TrueType class and rejects the text.

The concrete native path is `CTFontManagerCreateFontDescriptorsFromData` for one-face discovery, `CGDataProviderCreateWithCFData` plus `CGFontCreateWithDataProvider` and `CTFontCreateWithGraphicsFont` for byte-owned construction, `CTLineCreateWithAttributedString` and `CTLineGetGlyphRuns` for one-line shaping, `CTRunGetGlyphs`/`CTRunGetPositions`/`CTRunGetAdvances`/`CTRunGetStringIndices`/`CTRunGetStringRange`/`CTRunGetStatus` for copied evidence, and `CGBitmapContextCreate` with a null color space and alpha-only bitmap for coverage. The raster policy uses the available CGContext antialias, font-smoothing, and subpixel-position setters. No native object from this sequence leaves `text.rs`.

The line range must equal the entire UTF-16 string. Run ranges must be sorted, non-overlapping, and cover that line range exactly. Glyph string indices must remain within their run range. Indices may repeat or decrease inside a run because Indic clusters and reordering are legitimate. The validator never assumes one glyph per Unicode scalar. Run status, direction, text matrix, glyph IDs, positions, advances, and source indices are all copied into `TextShapeEvidence`.

### Limits, cancellation, and lifetime

The first-unit limits are explicit:

| Resource | Limit |
| --- | ---: |
| font blob | 16 MiB |
| UTF-8 text | 16 KiB |
| UTF-16 units | 32 KiB |
| CoreText runs | 64 |
| shaped glyphs | 8,192 |
| text lines | 1 |
| surface width or height | 4,096 pixels |
| surface plus guard pixels | 8,388,608 |
| coverage bytes | 8 MiB |
| premultiplied text raster | 64 MiB |
| one logical text contribution estimate | 96 MiB |

The existing 128 MiB per-owned-frame and 512 MiB aggregate logical picture limits remain authoritative. The 96 MiB estimate includes two font byte copies, UTF-8 and UTF-16 storage, copied observations, guarded coverage, and the eight-byte raster. It is a logical application permit. It does not claim total native or process memory.

Admission checks the checked sum before every owned allocation. The active text source is retained only for its span. The last response retires its font copy and raster. A one-item capacity-one channel bounds producer retention.

The kernel checks cancellation before and after every native call, while acquiring the text gate, between copied runs and rows, before returning a decision, and before writer append. CoreText or CoreGraphics may ignore cancellation during one bounded call. Export fencing, worker join, writer abort, and publication remain responsible for final cancellation state.

`CFData` owns its byte copy. `CGFont`, `CTFont`, `CTLine`, and `CTRun` stay inside the kernel scope. The alpha buffer is a boxed Rust allocation that outlives its CGContext. The context is dropped before that buffer becomes a `TextDecision`. No framework object, pointer, or borrowed image buffer crosses a worker channel.

### Module map

| Module | Candidate B ownership |
| --- | --- |
| `model.rs` | `FontResource`, `FontImport`, `TextClip`, merged-span validation, optional fields that preserve old bytes |
| `project.rs` | Font CAS staging, standalone-face probe, font measurement and origin checks |
| `text.rs` | One deep text kernel: face parsing, CoreText shaping, fallback checks, bounds, alpha-only raster, evidence comparison |
| `plan.rs` | Plan8 selection, `font_closure`, `TextUse`, central text and picture validation |
| `composition.rs` | Baseline-to-surface integer geometry, admission, existing mask and blend policy |
| `layers.rs` | Sparse text source selection, one active cache, capacity-one backpressure, Rust-only decisions |
| `alpha_picture.rs` | Shared premultiplied UNORM16 conversion and blend arithmetic |
| `movie.rs` | Plan8 pixel/profile admission and unchanged native writer |
| `exports.rs` | Plan8 replay, verify, cancellation, and staging recovery through the same validator |
| `identity.rs` | Unchanged historical `BuildIdentity`; no global text-framework mutation |
| `native_format.rs` | Unchanged H.264/AAC and NativeColorMaster profiles |
| `crates/cli/src/main.rs` | Existing commit, prepare, export, verify, cancel, and reconcile JSON operations |

The flow is intentionally knowledge-centered. The text module owns both preparation and execution policy. It is not split into load, shape, raster, and save stages that would duplicate evidence decisions.

## Twenty grounding decisions

1. **Font storage:** a separate content-addressed `Snapshot::fonts` map and `FontImport`, staged in the same `Project::commit` transaction as media.
2. **Lineage:** `FontOrigin` has imported external source and role only. Font hashes never enter timed `SourceRange` values.
3. **Collections:** reject TTC and OTC. Accept one standalone TrueType face with face index zero.
4. **Variables:** reject variable tables. No implicit default axis values become identity.
5. **Layout:** one CoreText line only. Reject wrapping, truncation, and multiline input.
6. **Direction:** explicit language plus `TextDirection::Ltr`. Reject bidi and RTL.
7. **Geometry:** caller supplies a signed baseline anchor. Preparation derives a tight padded glyph surface.
8. **Precision:** Q16.16 for font size, positions, advances, and bounds. Integer canvas placement remains signed `i32`.
9. **Rounding:** finite CGFloat values use nearest-away Q16 for positions and advances; bounds use Q16 floor for minima and ceil for maxima, then integer floor/ceil.
10. **Padding:** two pixels around ideal bounds plus a one-pixel draw guard. A touched guard rejects the source.
11. **Raster switches:** grayscale AA on, smoothing off, subpixel positioning off, fixed alpha-only context, native y-up drawing, deterministic row inversion.
12. **Face fingerprint:** SHA-256 over a domain tag, SFNT scalar, face index, and sorted raw table tags, lengths, and bytes.
13. **Glyph zero:** reject glyph ID zero for the accepted standalone TrueType class.
14. **Run ranges:** require contiguous full UTF-16 line coverage and in-range indices, while allowing repeated or reordered cluster indices within a run.
15. **Motion:** dimensions are fixed. Existing curve machinery is reused for baseline x, baseline y, and opacity only. Width and height curves reject.
16. **Caps:** 16 MiB font, 16 KiB UTF-8, 32 KiB UTF-16, 64 runs, 8,192 glyphs, one line, 4,096-pixel dimension, 8,388,608 guarded pixels, 64 MiB premultiplied raster, and 96 MiB logical text estimate.
17. **Concurrency:** serialize CoreText and CoreGraphics calls behind one cancellable process-local gate until an isolated probe proves safe parallelism.
18. **Backend identity:** `TextBackendIdentity` is a Plan8-only field containing CoreText and CoreGraphics bundle versions. Historical `BuildIdentity` bytes stay unchanged.
19. **Plan composition:** Plan8 subsumes text with existing media, alpha evidence, masks, motion, ordering, and `NativeColorMasterV2`; Receipt2 through Receipt4 stay unchanged.
20. **Fixtures:** use the committed OFL Noto TrueType blobs from `/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/font-fixtures-a01/manifest.json`: Telugu SHA `2c05072e8018a9be1cb0582953d9edf9a0cf129cdfb74e611de763b09c411f7f` and Devanagari SHA `385e78e6359a9d88a0f243d53b1209d7548361ba2194e2b9ec779bcaa7e8949d`. An independent Swift/CoreText producer owns expected shaping and raster files.

## Compatibility, tamper checks, and proof

When text is absent, empty optional fields are omitted. Snapshot schema 1, Plan2 through Plan7, Receipt2 through Receipt4, existing profiles, and `BuildIdentity` remain byte-for-byte and behaviorally unchanged. A real Plan7 serialized fixture must be frozen before adding Plan8 dispatch. Every replay, render, verify, and recovery path calls the same central `validate_plan` dispatcher. Plan8 validation reconstructs the timeline, checks merged text/media spans, verifies exact font closure, recomputes the text shape and surface evidence, and rejects unused font ancestors or duplicate text uses.

Tamper controls change one fact at a time: font blob bytes, face table fingerprint, exact UTF-8, UTF-16 hash, language, direction, size, color, anchor, run ranges, glyph IDs, positions, bounds, raster policy, backend identity, coverage hash, or plan schema. Each control recomputes incidental document hashes so the intended central validator reports the rejection. A zero-coverage text clip cannot satisfy sole-frame positive coverage. A transparent text overlay retains its source identity while a visible lower layer supplies the frame contribution.

The first implementation step is an isolated native feasibility probe. It uses the two committed Noto blobs, proves no registration, shapes Telugu and Devanagari, records run observations, draws the guarded alpha-only mask, verifies row orientation, checks fallback rejection, and records framework versions. The probe must pass before product integration.

The independent producer then writes exact UTF-8/UTF-16, face fingerprints, run observations, quantized geometry, guard results, coverage hashes, and visible bounds. Fixtures include Telugu clusters, Devanagari conjuncts, ASCII, leading/trailing spaces, combining-only input, and a missing-glyph negative case. Pure vectors cover Q16 bound rounding, signed anchor clipping, coverage/style alpha, premultiplication, opacity, mask, track order, and zero contribution.

The ordinary native proof combines a measured movie lower track, a transparent PNG, Telugu and Devanagari text on separate sparse spans, overlap ordering, signed clipping, opacity motion, an axis mask, exact source ordinals and PTS, the one 48 kHz stereo unity PCM interval, and the selected native output profile. An independent verifier checks every prehandoff BGRA frame, every text surface hash, every movie clock, exact PCM, output reopen, decoded opaque alpha, and profile evidence. The proof establishes bounded technical behavior. It does not establish lyric wording, readability, listening, or creative acceptance.

## Synthesis decision

This is an independent Candidate B package. No arena synthesis or sibling-candidate comparison is claimed here. Its distinguishing boundary is a byte-owned, non-timed font resource plus a shaper-derived surface and baseline anchor. It concentrates native policy in one text kernel while preserving the existing track worker and compositor contracts.

## Tradeoffs accepted

- We accept a new Plan8 schema in exchange for leaving every text-free plan byte unchanged.
- We accept one serialized native text gate in exchange for a clear callback and framework-lifetime boundary.
- We accept a two-pixel transparent pad in exchange for a measurable guard against ideal-bounds clipping.
- We accept no automatic fallback in exchange for truthful face and glyph identity.
- We accept fixed text dimensions in exchange for exact antialiased edge pixels and simple motion semantics.
- We accept a separate font closure in exchange for avoiding timed media lineage fiction.
- We accept logical admission rather than a total native-memory claim because CoreText owns opaque internal allocations.

## Alternatives considered

**Treat fonts as `MediaKind::Font`.** This reuses the CAS map but exposes `SourceRange` semantics to a timeless blob. It also leaks media probing rules into font identity. The separate font closure has a deeper boundary and keeps the caller API small.

**Use an explicit caller layout box.** This simplifies allocation but forces callers to choose dimensions and baseline offsets before shaping. It also makes width and height motion appear harmless. The tight surface hides those decisions and exposes only a baseline anchor.

**Use one tagged picture-item enum.** This gives one runtime list but rewrites every existing `VideoClip` serialization. Optional `text_clips` and Plan8 preserve old bytes while the merged private track program still gives one z-order authority.

**Pre-shape all text before workers start.** This shortens worker logic but retains every text raster for the export. The one active source cache and capacity-one port bound lifetime and backpressure more directly.

**Draw colored text directly in CoreGraphics.** This hides alpha and color arithmetic inside an OS context. Alpha-only coverage and the existing Rust premultiplication policy provide stronger exact vectors.

## Red-flag screen

- No public type contains a CoreText, CoreGraphics, CF, pointer, or transport object.
- Family-name lookup, registration, fallback, and mutable system font state are forbidden.
- `TextKernel` owns both preparation and execution observation, so shaping rules do not diverge.
- The guarded draw proves ideal bounds were not treated as raster coverage.
- Native objects die before a Rust decision crosses a channel.
- No unbounded typesetter or renderer subprocess is used.
- Empty optional fields preserve historical serialization.
- `BuildIdentity` is not changed to smuggle text framework versions into old documents.
- Admission is explicitly logical and never described as total process memory.
- Text is not called lyric or creative acceptance.

## Open questions and risks

- Does the isolated probe confirm that the selected CoreGraphics switches remain stable on every supported macOS host?
- Does the two-pixel pad pass the independent Telugu and Devanagari fonts at the maximum allowed size without repeated guard failures?
- Should a future font container extension add an explicit face-index contract, or remain a separate unit?
- Can a future parallelism probe justify more than one native text call without weakening the single ownership scope?

## Next implementation step

Build only the standalone native feasibility probe against the committed Noto blobs, and do not touch product integration until its lifetime, shaping, fallback, row-order, and guard results are archived.
