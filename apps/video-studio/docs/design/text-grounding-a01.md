# Native text and graphics grounding A01

## Status and result

This is Phase A grounding only. It does not select a design or authorize implementation.

The installed macOS stack has the APIs needed for a bounded native text unit. CoreText can shape exact UTF-8 text with an explicit font made from bytes. CoreGraphics can draw the shaped line into an application-owned, eight-bit alpha bitmap.

That API availability does not yet prove correct Indic shaping, stable pixels, fallback rejection, memory bounds, or export fidelity. Those require an isolated native probe and independent fixtures after a design is selected.

The useful first unit is narrow:

- static, single-style text within a frame span;
- exact imported font bytes and one explicit face;
- explicit language and writing direction;
- CoreText shaping with no font fallback;
- a solid straight-RGBA8 style color;
- an eight-bit glyph-coverage mask converted to the existing premultiplied contribution representation;
- existing track order, clipping, opacity, motion, mask, export, cancellation, and verification machinery;
- no system-font lookup by family name;
- no FFmpeg, libav, subprocess renderer, or Effect adapter work.

This unit is a general editor capability. It does not add lyrics to the user film. Native Indic lyrics remain optional and require separate authoring and review authorization.

The frozen source baseline is `build-a03.json`. Its binary SHA-256 is `ff89563d736a985380c09ff64b7bccac67c7751545aa8a28425b2b2630bba57a`. The frozen `Cargo.lock` SHA-256 is `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`. This grounding did not build or modify that baseline.

## Current caller-to-output path

The public workflow already has the right outer boundary:

```text
Studio::create_project
  -> Project::commit
  -> Project::prepare_export
  -> Project::export
  -> Project::verify_export

Project::cancel_export may fence a live export.
Project::reconcile_export_staging recovers owned finalizing work.
```

Text should remain behind these operations. A caller should not coordinate shaping, font loading, raster creation, or framework objects.

### Commit and snapshot

`Project::commit` stages every `AssetImport` into the content-addressed blob store. It verifies the caller's expected SHA-256 and byte count before probing the staged blob.

The current import model accepts only `MediaKind::{Movie, Audio, Image}`. `MediaDescriptor` has the same three variants. There is no font asset or font probe.

`Snapshot` remains schema 1. It contains settings, immutable assets, canonical audio, and timelines. A `Timeline` contains ordered video tracks and audio tracks. A `VideoClip` always selects a movie or image asset.

Clips within one video track cannot overlap. Video tracks are later composed bottom-to-top. These two rules provide a natural ordering model for text if text becomes another picture item.

`ContentHash::document` hashes exact `serde_json::to_vec` bytes. A Rust `String` therefore enters revision identity as exact valid UTF-8. A future text contract must also state that no Unicode normalization or transliteration occurs.

### Prepare and immutable plan

`Project::prepare_export` compiles the revision, probes selected input coverage, attaches decode evidence, hashes the final plan, and stores it by intent.

Current plan schemas are feature-selected:

| Plan schema | Current trigger |
| --- | --- |
| 2 | Native movie cuts |
| 3 | Opaque static PNG |
| 4 | Ordered layers or explicit placement |
| 5 | Picture motion |
| 6 | Analytic axis mask |
| 7 | A directly used transparent PNG |

Output profiles do not change this picture schema. `NativeColorMasterV2` can still use Plan2 through Plan7.

`VideoUse` binds each media clip to its track, frame span, asset hash, allowed source range, exact `presentation_ordinals`, framing, normalized placement, motion, and mask. The plan also binds the complete source lineage closure.

Plan7 adds one closed alpha policy and unique evidence for every directly used image. Its source authority remains straight RGBA8. Its execution authority is a copied premultiplied BGRA UNORM16 raster.

No current plan type can bind text, a font face, shaping observations, or a text raster policy.

### Native picture execution

Schemas 4 through 7 use `layers.rs`. The compositor owns one worker per nonempty picture track, with at most four workers. Each worker uses capacity-one request and response channels.

The compositor requests one frame from each track. It blends results bottom-to-top into an opaque BGRA8 canvas. The worker copies native movie buffers into Rust-owned pixels before returning.

Transparent PNG processing preserves straight source pixels. It samples into an eight-byte-per-pixel premultiplied raster. Intrinsic alpha then combines with clip opacity and mask coverage during composition.

Transparent contain bars contribute zero coverage. Signed placement clips at the canvas. The frame succeeds only if at least one picture item makes a positive contribution.

The alpha path is the correct execution seam for text. Text should produce a transparent contribution. It should not create an opaque picture with black contain bars.

### Writer, receipt, verification, and recovery

`movie.rs` sends composed BGRA frames to the existing native writer. It preserves one measured 48 kHz stereo PCM source.

`ArtifactReceipt` binds the project, revision, plan, renderer, output path, output hash, output bytes, and technical measurements. Receipt schemas remain output-profile contracts:

| Receipt schema | Output profile |
| --- | --- |
| 2 | H.264/AAC MP4 |
| 3 | `NativeColorMasterV1` |
| 4 | `NativeColorMasterV2` |

Fresh verification reopens the exact artifact. It checks container, codecs, clocks, complete video decode, opaque output alpha, audio evidence, and profile-specific color evidence.

Text does not inherently require a new receipt schema. The receipt already binds `plan_id` and the renderer. Any text-specific execution evidence belongs in the text plan or a justified producer observation, not a duplicate receipt field.

Replay, verification, and staging recovery currently admit only Plan2 through Plan7. A future text plan must update every central schema gate. Partial admission would make successful text exports unverifiable or unrecoverable.

## Required text identity

A design must bind five distinct identities. A family-name string cannot replace any of them.

### 1. Source text identity

The authoring document must retain the exact UTF-8 string. Preparation must derive and bind at least:

- SHA-256 of the exact UTF-8 bytes;
- UTF-8 byte length;
- UTF-16 code-unit length used by CoreText;
- explicit language identifier;
- explicit writing direction;
- an explicit statement that normalization is `none`.

The plan must retain the original string or a lossless reference to it. A digest alone cannot reproduce shaping.

Core Foundation's `CFString::from_str` uses `CFStringCreateWithBytes` and UTF-8. A probe must round-trip the resulting `CFString` before CoreText uses it.

### 2. Font byte and face identity

The font must be an immutable content-addressed blob. Required observations include:

- blob SHA-256 and byte count;
- imported origin and role;
- container kind;
- face count;
- selected face identity;
- PostScript name as an observation, not the primary identity;
- glyph count and units per em;
- a stable fingerprint of the selected face's table tags and table bytes;
- variation axes and selected values, if variable fonts are accepted.

`CTFontManagerCreateFontDescriptorFromData` uses font bytes without registering the font for descriptor matching. Apple states that it selects only the first face from TTC or OTC input.

`CTFontManagerCreateFontDescriptorsFromData` exposes all faces and can return an empty array for invalid data. This is the safer discovery API when collections might be accepted.

`CGDataProviderCreateWithCFData`, `CGFontCreateWithDataProvider`, and `CTFontCreateWithGraphicsFont` provide a second byte-owned construction path. Neither path requires process-global font registration.

`CTFontManagerRegisterGraphicsFont` is deprecated on this SDK. Process-global registration also creates shared mutable name resolution. The first unit should avoid it.

### 3. Style identity

The first style needs integer or fixed-point source values. At minimum it must bind:

- solid straight RGBA8 color;
- font size in an explicit video-pixel unit;
- one declared antialiasing policy;
- one declared font-smoothing policy;
- one declared subpixel positioning policy;
- one declared subpixel quantization policy.

CoreText accepts `CGFloat` font sizes and positions. Platform floating-point results must not become an implicit portable contract. The plan needs an explicit finite check and quantization policy.

Using an alpha-only raster keeps color arithmetic in Rust. CoreGraphics then supplies coverage only. This avoids an unmanaged RGB conversion in the text rasterizer.

### 4. Layout identity

Layout must bind the decisions that change glyph selection or geometry:

- single-line or multiline policy;
- language and direction;
- source range consumed by each line;
- glyph IDs per run;
- glyph positions and advances;
- original UTF-16 string indices;
- run direction and text matrix;
- line origin, baseline, and bounds;
- alignment and wrapping decisions;
- the float-to-fixed-point quantization policy;
- the raster extent and coordinate transform.

The first unit can avoid multiline wrapping. If wrapping is included, `CTTypesetterSuggestLineBreak` must choose every line break. Width, line spacing, alignment, and line origins then become normalized plan data.

### 5. Native backend identity

Current `BuildIdentity` binds the executable, `Cargo.lock`, architecture, host OS, and AVFoundation bundle version. Changing its serialized shape or `native_backend` string would change old plan and receipt bytes.

A text plan therefore needs separate text-backend identity. It should bind the CoreText and CoreGraphics bundle versions for new text plans only.

The current host observations are:

| Item | Observed value |
| --- | --- |
| macOS | 26.0.1, build 25A362 |
| SDK | macOS 26.1, build 25B74 |
| Command Line Tools | 26.1.0.0.1.1761104275 |
| CoreText bundle | 876.0.0.2 |
| CoreGraphics bundle | 1957 |
| Rust bindings already used | objc2 0.6.4 and framework crates 0.3.2 |

`CTGetCoreTextVersion` is deprecated. Its return value cannot exceed the macOS 11 constant. It is not sufficient as the backend identity.

## Trustworthy Indic shaping

CoreText must remain the shaping authority. Nominal character-to-glyph mapping is insufficient.

Apple states that `CTFontGetGlyphsForCharacters` reads the font's nominal cmap. It does not perform Unicode layout. It cannot shape Telugu, Devanagari, Tamil, combining marks, or conjuncts correctly by itself.

`CTLineCreateWithAttributedString` performs shaping for a single immutable line. `CTTypesetterCreateWithAttributedString` adds contextual line breaking. The typesetter has a bounded default: Apple can reject input that requires unreasonable work unless unbounded layout is explicitly enabled. The editor must never enable unbounded layout.

The attributed string must include the exact `CTFont`, `kCTLanguageAttributeName`, and an explicit writing-direction policy. Default system language is not a stable plan input.

After shaping, preparation and execution must inspect every `CTRun`:

- `CTRunGetGlyphCount` establishes bounded glyph allocation;
- `CTRunGetGlyphs` copies exact glyph IDs;
- `CTRunGetPositions` copies visual positions;
- `CTRunGetAdvances` records advances but does not replace positions;
- `CTRunGetStringIndices` maps glyphs back to UTF-16 indices;
- `CTRunGetStringRange` and `CTLineGetStringRange` bind consumed source coverage;
- `CTRunGetStatus` binds direction and nonidentity-matrix flags;
- `CTRunGetTextMatrix` exposes per-run transform state;
- `CTRunGetAttributes` exposes the font selected by the layout engine.

Apple warns that the run attribute dictionary may be manufactured during font substitution. Every run font must match the bound face fingerprint and variation settings. A different run font is an error, even if its family or PostScript name matches.

For accepted SFNT fonts, glyph ID zero should be treated as missing-glyph evidence. The design still needs to decide whether table parsing independently proves that assumption.

Run string ranges must cover the complete Core Foundation string. The check must permit ligatures, reordered marks, and multiple glyphs for one source cluster. It must not demand one glyph per Unicode scalar or UTF-16 unit.

The initial scope can require left-to-right text. Telugu, Devanagari, and Tamil are all valid complex-script tests within that bound. Bidirectional text and right-to-left paragraph layout can be deferred explicitly.

## Installed native API feasibility

The following APIs exist in the installed macOS 26.1 SDK. Matching objc2 0.3.2 bindings are present in the local Cargo registry.

| Need | Installed primary API | Grounded use | Limitation still requiring proof |
| --- | --- | --- | --- |
| Copy exact font bytes | `CFDataCreate` | Native-owned copy from verified blob bytes | Counts as a second admitted copy |
| Inspect font faces | `CTFontManagerCreateFontDescriptorsFromData` | Reject invalid data or select an explicit face | Face-selection policy remains undecided |
| Create exact face | `CGFontCreateWithDataProvider`, `CTFontCreateWithGraphicsFont` | Avoid family-name lookup | Collection and variation behavior need a probe |
| Recreate descriptor face | `CTFontCreateWithFontDescriptor` | Create a sized font from a byte-derived descriptor | Apple documents best matching; fallback checks remain mandatory |
| Inspect face | `CTFontCopyGraphicsFont`, `CTFontCopyTable`, `CGFontCopyTableForTag` | Build a table fingerprint | Stable fingerprint format remains to be designed |
| Shape one line | `CTLineCreateWithAttributedString` | Correct visual-order glyph runs | It does not perform proper line breaking |
| Break lines | `CTTypesetterCreateWithAttributedString`, `CTTypesetterSuggestLineBreak` | Contextual bounded line layout | Multiline increases plan and proof scope |
| Observe shaping | `CTLineGetGlyphRuns` and `CTRunGet*` | Bind glyphs, positions, ranges, direction, and fonts | Floating geometry needs quantization |
| Draw shaped text | `CTLineDraw` or `CTRunDraw` | Draw the shaped result | Exact alpha depends on host and render settings |
| Own alpha buffer | `CGBitmapContextCreate` or `CGBitmapContextCreateWithData` | Draw into Rust-owned eight-bit alpha memory | Buffer lifetime and stride must be explicit |
| Control grayscale rasterization | `CGContextSetShouldAntialias`, smoothing and subpixel setters | Close render policy | Actual behavior needs exact-pixel probes |
| Position text | text position, text matrix, CTM translation | Explicit baseline and origin | Coordinate conversion must preserve Indic marks |

`CGBitmapContextCreate` permits a null color space only with `kCGImageAlphaOnly`. The editor can therefore allocate one byte per raster pixel and avoid a text RGB color space.

`CTLineDraw` expects a text matrix whose y values increase bottom-to-top. Apple warns that a flipped text matrix may misplace diacritics. The safer first probe keeps the native text matrix y-up, draws into the native row order, then copies rows into the editor's top-left raster order.

The current editor does not depend directly on `objc2-core-text`. Version 0.3.2 is present in the local registry but absent from `Cargo.lock`.

`objc2-core-graphics` 0.3.2 is already locked transitively. The editor does not declare it directly. A future implementation should add explicit, pinned feature sets rather than rely on a transitive dependency.

Likely required features are:

```text
objc2-core-foundation:
  CFArray, CFAttributedString, CFData, CFDictionary, CFNumber, CFString

objc2-core-text:
  CTFont, CTFontDescriptor, CTFontManager, CTLine, CTRun,
  CTStringAttributes, and CTTypesetter only if wrapping is selected

objc2-core-graphics:
  CGBitmapContext, CGColorSpace, CGContext, CGDataProvider,
  CGFont, CGImage, and required geometry types
```

This feature set is an API inventory. It has not been compiled in this grounding.

## Geometry and alpha contract obligations

The native shaper uses Core Graphics coordinates. The editor uses integer canvas coordinates with a top-left origin.

A text plan must define one complete transform between these spaces. It must not derive geometry again in separate modules.

Two raster boundaries remain viable:

1. An explicit layout box uses caller-owned integer width and height. Text draws at a normalized baseline inside that box.
2. A tight glyph surface derives from shaped image bounds plus a declared integer padding rule.

The layout box is easier to clip and admit. The tight surface uses less memory. Apple states that CoreText image bounds are ideal path bounds and exclude raster coverage. A tight surface therefore needs measured padding and a post-draw clipping guard.

The text raster should contain glyph coverage only. Style color remains straight RGBA8. A deterministic Rust conversion can create the existing premultiplied UNORM16 contribution:

```text
glyph coverage8
  x style alpha8
  -> intrinsic coverage16

style RGB8
  x intrinsic coverage16
  -> premultiplied BGRA16
```

The exact rounding order must be selected once and frozen as a named policy. It must not reuse floating-point CoreGraphics color blending.

Existing composition then applies clip-local opacity and analytic mask coverage. It blends the premultiplied contribution over the opaque canvas. Track order remains bottom-to-top.

The glyph raster background is transparent. There are no contain bars for text. Scaling or fitting text through the media `Framing` model would introduce an unrelated crop/fit decision.

Signed x and y placement may put part or all of the raster off-screen. Canvas clipping is authoritative. A fully clipped item retains text and shaping observations but contributes zero visible pixels.

Whitespace, font holes, and transparent style pixels also contribute zero alpha. The existing runtime positive-contribution gate must remain truthful. A frame with only invisible text fails `video_coverage`; a sparse invisible overlay may coexist with a visible lower track.

The design must decide whether text may use existing width and height motion. Resampling an already antialiased glyph mask changes edge pixels. A smaller first unit can allow x, y, opacity, and masks while requiring fixed raster dimensions.

## Ownership, lifetime, allocation, and cancellation

Font and text handling must preserve the current bounded worker shape.

### Ownership boundary

The blob store owns immutable font bytes. A shaping operation temporarily owns `CFData`, `CGFont` or `CTFont`, attributed strings, lines, and runs.

No Core Foundation, CoreText, or CoreGraphics object should cross a track channel. The shaping scope must copy glyph observations and the final alpha coverage into Rust-owned values. It must drop native objects before publishing the raster.

An application-owned bitmap buffer must outlive its `CGContext`. A boxed slice avoids reallocation. The context must be dropped before the buffer is moved into the Rust raster.

### Worker and backpressure seam

The existing picture worker can request and cache one active text source, just as it caches one active PNG or movie source. It can publish the resulting Rust raster through the same capacity-one response channel.

The first implementation should serialize CoreText shaping and drawing behind one cancellable gate unless a native concurrency probe proves independent calls safe. Serialization does not add threads or change track ordering.

One alternative is a dedicated pre-shape stage. That stage risks retaining every text raster for the full export. It is unsuitable without an explicit temporal cache and aggregate admission.

### Logical admission

Admission must occur before every owned allocation. It must include:

- verified font blob bytes held by the operation;
- the copied `CFData` bytes, if `CFDataCreate` is used;
- UTF-8 and UTF-16 text storage;
- copied glyph IDs, positions, advances, and source indices;
- the one-byte-per-pixel alpha mask;
- the eight-byte-per-pixel premultiplied raster;
- the existing source, canvas, and writer-side Rust payloads.

The current limits provide useful ceilings: 128 MiB per owned picture frame or alpha raster, and 512 MiB aggregate logical picture payload. The text design must decide font-byte, text-length, glyph-count, line-count, and raster-specific caps within that aggregate.

CoreText and CoreGraphics can allocate internal native objects outside the Rust permits. Logical admission is an application-owned estimate. It cannot be presented as a total process-memory guarantee.

### Cancellation

CoreText shaping and drawing calls do not expose the current editor's cancellation callback. Bound input sizes are therefore part of the cancellation contract.

The editor can check cancellation:

- during font read and hash verification;
- while waiting for the shaping gate;
- before and after each native call;
- between lines and runs;
- during row conversion and premultiplication;
- before worker response and before writer append.

A cancellation request may wait for one bounded native call to return. The existing export fence, lease checks, worker join, writer abort, and publication transaction remain authoritative.

## Compatibility requirements

### Snapshot compatibility

All existing snapshot schema 1 bytes must round-trip exactly. New optional collections must use defaults and omit empty values. New enum variants do not change old serialization by themselves.

A text design must choose how fonts and text items enter the snapshot:

- a `Font` asset descriptor and text items within picture tracks;
- a separate content-addressed font collection and separate text tracks;
- or another shape that preserves one source of ordering truth.

Treating a rendered PNG as the text source is not sufficient. It discards source text, shaping, face, and layout identity.

### Plan compatibility

Plan2 through Plan7 bytes and validation behavior must remain unchanged. Text probably requires a new feature-selected plan schema. That remains a design decision, not a grounding conclusion.

A new schema must compose with earlier features. A text timeline can also contain transparent PNGs, masks, motion, and `NativeColorMasterV2`. Schema selection must not erase Plan7 alpha policy or earlier normalized facts.

The plan must centrally validate text uses against the reconstructed authoring timeline, exact font assets, normalized shaping, and backend identity. Execution, verification, and recovery must call the same validator.

Current schema gates needing deliberate review are:

- `project.rs`: stored plan replay admits `2..=7`;
- `plan.rs`: picture validation admits `2..=7` and special-cases Plan7 evidence;
- `movie.rs`: layered execution and channel sizing use `4..=7`;
- `composition.rs`: dynamic admission branches use `5..=7`;
- `exports.rs`: completed verification admits `2..=7`;
- `exports.rs`: staging reconciliation admits `2..=7` and special-cases Plan7.

### Receipt compatibility

Receipt2, Receipt3, and Receipt4 remain profile-specific. Text should not renumber them merely because a new picture feature exists.

Historical receipts must reopen with their original plan, renderer, measurements, and byte hashes. A new optional measurement field would need `default` plus `skip_serializing_if`, but no such field is currently justified.

### Exact legacy guards

`crates/editor/tests/legacy_hashes.rs` freezes these current documents:

| Document | SHA-256 |
| --- | --- |
| snapshot schema 1 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` |
| plan schema 2 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` |
| plan schema 3 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` |
| placement snapshot schema 1 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` |
| plan schema 4 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` |
| motion snapshot schema 1 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` |
| plan schema 5 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` |
| receipt schema 2 | `44c0c27ad1a58f22746011673d8e4d4a211c5b5cdeffcb18172d6cc73fc73be2` |
| synthetic plan schema 6 | `5f9556fa7085bcd668d45cbc0564ff905adaf9b7f3d2e23b7fbed21ea65c5b28` |
| canonical plan schema 6 | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` |
| mask snapshot schema 1 | `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd` |

Plan7 is covered by current behavioral tests and frozen Alpha A03 source. It does not yet have a file in `tests/fixtures/legacy`. A text implementation should first preserve a real Plan7 serialization fixture if the root work has not already done so.

## Narrow first-unit boundary

A candidate can stay useful and bounded with these constraints:

- imported, content-addressed SFNT font bytes;
- one explicitly selected face;
- either static fonts only or explicit rejection of unresolved variation axes;
- exact UTF-8 without normalization;
- explicit UTS #35 language identifier;
- left-to-right single-line layout;
- one font, size, and solid RGBA8 style per text item;
- no font fallback;
- a transparent glyph-coverage raster;
- fixed raster dimensions after shaping;
- signed x and y placement, clip opacity, and existing axis mask;
- existing bottom-to-top track order;
- sparse temporal spans over a visible lower source;
- existing one 48 kHz stereo unity-audio contract;
- existing native H.264 and master output profiles.

The first unit should defer:

- system font-family lookup;
- fallback chains;
- TTC or OTC unless face indexing is fully bound;
- variable-font axes unless every axis is explicit;
- right-to-left and mixed-direction paragraphs;
- multiline wrapping, hyphenation, and truncation;
- per-range styles;
- kerning or tracking controls;
- strokes, shadows, glows, backgrounds, and gradients;
- emoji and color-font tables;
- vertical text and text on paths;
- rotation and perspective;
- animated strings or per-frame reshaping;
- ICC, gamma, or source-gamut conversion;
- audio changes;
- Effect adapters and tenant orchestration.

These are scope boundaries. They do not prevent later typed extensions.

## Structural seams for candidate design

The next design phase must resolve four whole-shape choices.

### Font storage

Adding `MediaKind::Font` and `MediaDescriptor::Font` reuses CAS, import replay, origin, and source verification. However, `SourceRange` assumes timed streams and a positive `Span`. Fonts do not have sample ranges.

A separate font asset collection avoids that semantic mismatch. It also creates a second import and lineage path unless it remains behind `Project::commit`.

The chosen shape must preserve one content-addressed blob authority and one commit transaction.

### Text ordering

Adding skipped `text_clips` to each `VideoTrack` preserves track order. Validation must reject overlap across media clips and text clips in the same track.

A separate `text_tracks` collection creates an ambiguous z-order unless all picture and text tracks share one ordered parent list.

Replacing `VideoClip` with a tagged enum creates a clean unified item model, but it changes every existing serialized clip. That conflicts with exact snapshot compatibility.

### Preparation versus execution

Preparation must shape text and store normalized observations in the immutable plan. Otherwise the plan does not describe the pixels it authorizes.

Execution must shape again, compare the observation, rasterize, and compose. Trusting only prepared glyph data would require bypassing CoreText at render time or storing large path data.

The selected module must own both operations so the shaping policy is not duplicated.

### Raster geometry

An explicit layout box gives stable allocation and simple signed clipping. A tight glyph surface reduces memory but depends on a padding rule around ideal CoreText bounds.

This choice controls caller semantics, plan fields, motion compatibility, and exact pixel tests. It cannot remain an implementation detail.

## Likely module touch map

This is a trace of affected ownership. It is not an implementation plan.

| Module | Current authority | Text-specific pressure |
| --- | --- | --- |
| `model.rs` | assets, clips, tracks, snapshot validation | font asset and text authoring shape; cross-item overlap |
| `project.rs` | staged CAS import and immutable revision | font probe and exact blob measurement |
| `media.rs` | movie, audio, and PNG dispatch | must not absorb text shaping; font dispatch only if chosen |
| a new text module | absent | font parsing, CoreText shaping, fallback checks, normalized evidence, alpha raster |
| `plan.rs` | feature schema and central mapping validation | text schema selection, uses, backend and shaping evidence |
| `composition.rs` | geometry, masks, logical budget | text raster placement and admission |
| `alpha_picture.rs` | premultiplied UNORM16 policy | share arithmetic or expose a private contribution constructor |
| `layers.rs` | bounded track workers and ordered blend | request, cache, and release text contributions |
| `movie.rs` | layered dispatch, writer, native verification | admit the new plan schema without changing output profile |
| `exports.rs` | replay, verify, recovery | admit and centrally validate the new schema |
| `identity.rs` | frozen renderer identity | do not change legacy bytes; add new-plan text backend identity elsewhere |
| `native_format.rs` | output container, codecs, color tuple | can remain generic; text does not change the format contract |
| `crates/cli/src/main.rs` | public JSON operations and capability truth | describe implemented text only after independent proof |

Effect adapters remain outside this module map.

## Independent proof required

The proof must separate API feasibility, shaping identity, pre-encode pixels, encoded output, and creative review.

### 1. Isolated native feasibility probe

Before product integration, compile a standalone Rust probe against the selected objc2 features. It must:

- load exact owned font bytes without registration;
- shape synthetic Telugu and one second complex script;
- enumerate runs, glyphs, positions, indices, ranges, and run fonts;
- draw an alpha-only mask into application-owned memory;
- prove the context lifetime and row orientation;
- record framework bundle versions and all settings;
- preserve a failing fallback case.

This probe was not run during grounding.

### 2. Independent shaping fixture

Use owned, licensed font fixtures with exact SHA-256 values. Do not use a mutable system font path as the fixture authority.

An independent producer must write expected source bytes, UTF-16 units, face fingerprint, glyph runs, quantized geometry, alpha-mask hashes, and visible bounds. The producer must not share the product's Rust module.

Test at least:

- Telugu base characters, vowel signs, combining marks, and conjuncts;
- a second complex script such as Devanagari or Tamil;
- ASCII control text for simple geometry;
- leading and trailing whitespace;
- a missing-glyph input that attempts fallback;
- a zero-width or combining sequence without one-code-point-to-one-glyph assumptions.

### 3. Exact pure arithmetic vectors

Independent vectors must cover coverage8 plus style-alpha conversion, UNORM16 premultiplication, clip opacity, mask coverage, track order, signed clipping, and zero coverage.

These vectors should compare every channel exactly. They should include hidden RGB behind zero style alpha only if the selected representation can carry such data.

### 4. Product plan and tamper tests

Tests must prove:

- old snapshots and Plan2 through Plan7 keep exact bytes;
- only directly used text selects the new schema;
- an unused font or unused text ancestor does not select it;
- font bytes, face, source string, language, direction, style, geometry, backend, or glyph observations cannot be forged;
- missing, duplicated, reordered, or substituted runs fail central validation;
- replay, verify, cancellation, and staging recovery admit valid text plans;
- legacy recovery behavior remains unchanged;
- invisible text cannot fabricate sole-frame coverage;
- sparse text overlays retain their source observations.

### 5. Actual native output proof

The ordinary public CLI must export an exact prepared plan. A separate observer must compare every borrowed prehandoff BGRA frame with independent expected hashes.

The fixture should combine:

- an actual movie lower track;
- an actual transparent PNG layer;
- simultaneous Telugu text and second-script text on separate spans;
- overlapping text and image layers to prove order;
- signed clipping, opacity, motion or a declared fixed-motion subset, and an axis mask;
- the canonical 24-bit 48 kHz stereo audio interval.

The independent verifier must reopen the final output and check every frame and source clock, exact PCM, output profile, V2 color tuple when selected, decoded alpha 255, and fixed text ROIs. It must preserve negative controls and failed outputs.

ProRes pixel thresholds remain encoded-output policy. Exact alpha-mask and prehandoff canvas hashes provide the text arithmetic proof. H.264 does not become a fidelity reference.

The proof can establish bounded technical behavior. It cannot establish correct lyric wording, performance timing, readability, hearing, pilot approval, full-film quality, or creative acceptance.

## Concrete remaining decisions

The design phase must answer these before implementation:

1. Is a font a `StoredAsset` variant, or a separate content-addressed project resource?
2. How does font lineage avoid pretending that a font is a timed stream?
3. Are TTC and OTC rejected, or is face index part of the public contract?
4. Are variable fonts rejected, fixed to measured defaults, or given explicit axis values?
5. Is the first layout single-line only, or is wrapping part of the unit?
6. Is direction limited to LTR, or does the unit include Unicode bidi behavior?
7. Does the author specify a layout box, baseline, anchor, or tight glyph surface?
8. Which fixed-point precision represents font size, positions, advances, and bounds?
9. What exact rounding derives raster integer bounds?
10. What padding prevents ideal glyph bounds from clipping antialiasing coverage?
11. Which antialias, smoothing, and subpixel switches form the closed raster policy?
12. How is the selected face fingerprint derived from table tags, table bytes, and variations?
13. Is glyph zero sufficient missing-glyph evidence for the accepted font class?
14. How are run ranges checked without rejecting legitimate Indic clustering or reordering?
15. May existing width and height motion resample text, or are dimensions fixed initially?
16. What are the font-byte, text-byte, UTF-16, glyph, line, and raster limits?
17. Does execution serialize CoreText calls, or will a concurrency probe support parallel shaping?
18. Where does text-backend identity live without changing historical `BuildIdentity` bytes?
19. Does text use a new plan schema that subsumes alpha, mask, motion, and layering?
20. Which independent fixture producer and licensed fonts become long-term proof authority?

## Red-flag screen for the next design

- A public CoreText or CoreGraphics type leaks native representation.
- A font family string delegates identity to mutable host state.
- Automatic fallback hides missing source glyphs.
- A rendered PNG replaces text, font, or shaping identity.
- Separate text tracks and video tracks lack one z-order authority.
- Preparation and execution implement different shaping rules.
- Ideal path bounds are treated as guaranteed raster coverage.
- Native objects cross worker channels or outlive their byte buffers.
- A layout API exposes CoreText stages for callers to coordinate.
- Unbounded typesetting is enabled to handle difficult input.
- New text fields serialize into old snapshots, plans, or receipts when absent.
- `BuildIdentity` changes globally to record text frameworks.
- Application-owned admission is reported as total native memory.
- A successful compile or one screenshot is called Indic shaping proof.
- Technical output checks are called film or lyric acceptance.

## Host font observations

The host contains native Indic fonts, including `KohinoorTelugu.ttc`, `Telugu MN.ttc`, `Devanagari Sangam MN.ttc`, and `Tamil MN.ttc`. Their presence confirms local shaping inputs exist.

These system paths are unsuitable as project authority. OS updates can replace their bytes, and several are collections. A project must import and hash exact licensed font bytes.

For reference, the observed `KohinoorTelugu.ttc` is 675,700 bytes with SHA-256 `6e55a5b0eb8169b634db0d6345078d6c5637b7a9d375cb56a1742a0944892bc7`. This observation is not a selected product fixture.

## Sources inspected

Runtime source:

- `crates/editor/src/model.rs`
- `crates/editor/src/project.rs`
- `crates/editor/src/plan.rs`
- `crates/editor/src/image.rs`
- `crates/editor/src/alpha_picture.rs`
- `crates/editor/src/framing.rs`
- `crates/editor/src/composition.rs`
- `crates/editor/src/layers.rs`
- `crates/editor/src/movie.rs`
- `crates/editor/src/native_format.rs`
- `crates/editor/src/exports.rs`
- `crates/editor/src/identity.rs`
- `crates/editor/src/media.rs`
- `crates/cli/src/main.rs`
- `crates/editor/tests/legacy_hashes.rs`
- `docs/WORK.md`
- `docs/design/judgment.md`
- `docs/design/synthesis.md`

Frozen closure:

- `artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01/build-a03.json`
- `artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01/native-proof-policy-a02.json`

Installed primary headers:

- `CoreText.framework/Headers/CTFont.h`
- `CoreText.framework/Headers/CTFontManager.h`
- `CoreText.framework/Headers/CTLine.h`
- `CoreText.framework/Headers/CTRun.h`
- `CoreText.framework/Headers/CTStringAttributes.h`
- `CoreText.framework/Headers/CTTypesetter.h`
- `CoreGraphics.framework/Headers/CGBitmapContext.h`
- `CoreGraphics.framework/Headers/CGContext.h`
- `CoreGraphics.framework/Headers/CGDataProvider.h`
- `CoreGraphics.framework/Headers/CGFont.h`
- `CoreGraphics.framework/Headers/CGImage.h`

Installed Rust binding sources:

- `objc2-core-text-0.3.2`
- `objc2-core-graphics-0.3.2`
- `objc2-core-foundation-0.3.2`

No runtime, fixture, helper, media, state, GPU, provider, Resolve, or Effect artifact was changed. No build or native behavior probe was run.
