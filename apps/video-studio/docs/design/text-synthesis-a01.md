# Native text synthesis A01

## Usage first

The caller imports exact font bytes through `Project::commit` and places text in an existing ordered video track.
The existing prepare, export, verify, cancel and reconciliation operations remain the complete workflow.
These are synthetic editor examples. They do not author film lyrics.

```rust,ignore
let revision = project.commit(CommitProject {
    intent: EntityId::parse("title-commit-a01")?,
    base_revision: project.head()?.receipt.revision,
    imports: vec![],
    font_imports: vec![FontResourceImport {
        path: exact_noto_telugu_path,
        expected_hash: telugu_hash,
        expected_bytes: 197_228,
        origin: FontResourceOrigin::Imported {
            external_source: exact_pinned_source_url,
            role: "licensed_typeface".into(),
        },
        previous_measurement: None,
    }],
    canonical_audio: Some(existing_canonical_audio),
    timelines: vec![timeline_with_lower_picture_and_text(TextClip {
        id: EntityId::parse("title")?,
        timeline_frames: Span { start: 8, length: 48 },
        text: "తెలుగు కథ".into(),
        language: TextLanguage::parse("te")?,
        direction: TextDirection::Ltr,
        style: TextStyle {
            font: telugu_hash,
            font_size_q16: FontSizeQ16::new(48 * 65_536)?,
            color: Rgba8 { r: 255, g: 240, b: 190, a: 224 },
        },
        layout: TextLayoutBox {
            destination: PixelRect { x: 24, y: 90, width: 280, height: 72 },
            baseline: PixelPoint { x: 12, y: 50 },
        },
        opacity: Opacity::new(1.0)?,
        motion: None,
        mask: None,
    })],
})?;
let request = ExportRequest {
    intent: EntityId::parse("title-export-a01")?,
    revision: revision.revision,
    timeline: EntityId::parse("main")?,
    profile: MovieProfile::NativeColorMasterV2,
};
let prepared = project.prepare_export(request.clone())?;
let output = project.export(request.clone())?;
let checked = project.verify_export(request.intent)?;
assert_eq!(output.receipt.artifact.plan_id, prepared.plan_id);
assert_eq!(checked.receipt.receipt_id, output.receipt.receipt_id);
```

Font construction, shaping, fallback checks, native buffers, cache lifetime and composition stay private.
The caller controls an integer clip box and local baseline. Coverage outside that box is intentionally clipped.
Text never uses a media SourceRange, framing, scaling or contain bars.

## Problem and selected shape

Use Candidate A as the base. Its complete types, signatures, module map, math and twenty decisions are the contract except for the explicit amendments below.
The candidate is frozen at SHA `6851884d8a76ce5a44181eab1d5c7991f61b323754907b4aaeb4ef69c9c6198e`.
Candidate B remains preserved at SHA `5d2bba28c4faea686c03e099977d434376769e20131b07f8b766121158af9da0`.

One private text subsystem owns font parsing, face identity, CoreText shaping, copied observations, alpha-only rasterization and execution comparison.
Project font metadata remains separate from timed media metadata over one blob CAS and one commit transaction.
Text clips append to existing video tracks. Merged media and text spans cannot overlap within one track.
Track vector order remains the only bottom-to-top authority.

Only directly selected text creates Plan8. No text retains the existing Plan2–7 selector and admission behavior.
Receipt2–4 remain output-profile contracts. NativeColorMasterV2 settings and all historical identities remain unchanged.

## Synthesis decision

The parent scored A 22/25 and B 19/25 after reading both end to end.
The independent judge scored A 24/25 and B 17/25 and also selected A.
The ranking agrees. Score differences reflect emphasis on caller geometry and historical validation risks.
There are no missing candidates. All reviewers share one model family.

Grafts from B are limited to the name `font_closure` for Plan8 and an outer-guard experiment for the probe.
Snapshot still uses `font_resources`. The plan closure contains exactly the directly used fonts.
A baseline-anchor convenience remains a future extension. Production tight-surface allocation is deferred.
B's per-frame shaping, by-value raster responses, fixed 96 MiB estimate and incomplete guard transform are rejected.

## Exact first-unit boundaries

- One standalone static TrueType-outline SFNT face at index zero.
- Exact UTF-8 without normalization or transliteration; explicit canonical language subset and LTR embedding.
- One line, one style, one font, one RGBA8 color and one fixed integer clip box per item.
- Font size is authored Q16 in `[65_536, 512 * 65_536]`.
- Native observations use signed Q16 with finite checks and half-away rounding.
- Integer x/y and Q16 opacity motion plus existing axis masks are supported.
- Width/height motion, raster resampling and per-frame string changes are rejected.
- Collections, CFF, variations, color/bitmap fonts, fallback, bidi paragraphs, wrapping, per-range styles, rotation and effects are rejected.
- All Candidate A resource caps remain, with the reduced 512-pixel font-size cap and aggregate curve-key cap below.

Language accepts 2–3 lowercase ASCII letters, optional canonical four-letter script, and optional two-letter or three-digit region.
Line separators, tabs, bidi controls and noncanonical language forms fail explicitly.
LTR embedding must preserve native RTL run detection. It must never become an override that conceals an RTL run.

## Font and shaping identity

Keep Candidate A's exact face fingerprint: domain tag, scalar, sorted tag/count/length and SHA-256 of every exact table.
Imported byte SHA and byte count remain separate from face identity.
Every actual run font must match the face, planned size, full identity font matrix, empty variation state and observed PostScript name.
The PostScript name cannot authorize a face by itself.

Bind exact UTF-8 and UTF-16BE hashes/counts, the complete line range, sorted range partition and CoreText visual run order.
Bind full six-component text/font matrices, status bits, glyph IDs, positions, advances and source indices.
Permit repeated and nonmonotonic cluster indices. Reject glyph zero, fallback, RTL, nonidentity matrices and unknown status bits.

Preparation and execution call the same policy owner.
Execution shapes, compares and draws once when a text source becomes active. Subsequent frames use its cached Rust raster.
Historical output verification checks stored structure and reopens exact media. It does not reshape on a newer host.
A fresh render requires the bound CoreText/CoreGraphics tuple and an exact execution comparison.

## Closed raster policy

`CoreTextSingleLineGrayAlpha8V1` is one named closed policy, not caller-configurable boolean switches.

The bitmap has eight bits per component, alpha-only samples, no color space and a stable application-owned boxed buffer.
Stride is `align_up(width, 16)` with checked arithmetic. The permit charges `stride * height`, including padding.
CTM and text matrix are identity. Text position is `(baseline.x, height - baseline.y)` in native y-up coordinates.
Set fill mode and gray/alpha `(1,1)`. Set foreground-color-from-context on the complete attributed string.
Allow and request antialiasing. Disallow and do not request smoothing, subpixel positioning or subpixel quantization.
Call each `Allows` and `Should` setter explicitly.

The canonical top-left coverage order is:

```text
canonical row y = native row (height - 1 - y), first width bytes only
```

This row rule is a hypothesis until separate native probes establish it.
No implicit padding or ideal-bounds allocation is added to the public clip box.

Production needs one native alpha buffer. Hash canonical rows by streaming them in reverse row order.
Scan count/bounds and convert those same rows directly into the admitted premultiplied raster.
Do not allocate a second whole canonical alpha buffer.
If an implementation needs a second buffer, its reservation must precede allocation and include both buffers until release.
Drop CGContext before moving or reusing its boxed backing memory.

Coverage8 and RGBA8 use Candidate A's exact UNORM16 half-up arithmetic.
Existing Q16 opacity, axis-mask weights and source-over remain the only blend arithmetic.
Style alpha zero and whitespace remain zero contributions. Runtime positive coverage remains authoritative.

## Cache and response ownership repair

The final-response lifetime uses the existing request-response barrier.

```rust,ignore
struct AdmittedTextRaster {
    width: u32,
    height: u32,
    samples: Vec<PremulBgra16>,
    positive_samples: u64,
    permit: Permit,
}
enum SampledLayer {
    // Existing variants retain their historical behavior.
    TextV1 { raster: Arc<AdmittedTextRaster> },
}
```

1. The worker owns one cache Arc; a response owns a second Arc to the same raster and permit.
2. Before sending the final response, the worker drops its cache Arc.
3. The response retains the raster during compositor checks and blending.
4. The compositor drops that response before requesting the next frame from the track.
5. The last Arc releases the single permit; no acknowledgement channel or raster clone is needed.

The worker cannot claim to observe consumer completion. Its next request is the barrier.
Disconnected send, cancellation and worker-drop paths release all retained references.
Metadata observations and the borrowed-frame test observer must not retain a raster Arc after the frame.
Blend a borrowed clipped view of the full cached raster. Do not allocate a per-frame copied text surface.

## Admission repair

The existing 512 MiB policy remains an application-owned logical picture payload limit.
It excludes opaque native framework internals, allocator bookkeeping and caller-owned copies outside the pipeline.
It is not a process-memory or throughput guarantee.

Name every concurrent category before allocation:

| Category | Required charge and lifetime |
| --- | --- |
| Shared retained Plan8 text data | One admitted immutable text payload; source strings, font closure/descriptors, runs, glyph/position/advance/index arrays, layout, motion and mask data |
| Canonical JSON buffer | Separate checked reservation for up to 64 MiB while serialization/read buffer coexists with typed data; release before workers start |
| Cached text contribution | Exact `8 * width * height` for each temporally active source; one permit shared by response Arcs |
| Font read and native byte copy | Rust font read plus copied CFData, each exact font byte count |
| Run-face table inspection | At most one copied table at a time, conservatively one font byte count, plus bounded table-record scratch |
| Fresh execution evidence | Separate string, UTF-16 and copied run/glyph/position/advance/index allocations; retained plan evidence does not replace this charge |
| Native alpha mask | Exact padded stride times height; no uncharged canonical duplicate |
| Other picture payloads | Existing movie/PNG source and raster, canvas, response and writer reservations remain unchanged |

The typed Plan8 text payload receives a conservative 128 MiB logical reservation before internal construction or copying.
Its aggregate limits include 1 MiB source UTF-8, 524,288 UTF-16 units, 4,096 runs and 131,072 glyphs.
Also limit all authored and normalized text motion/mask curve keys to 65,536 combined.
Bound imported external-source strings to 4,096 UTF-8 bytes, roles to 1,024 bytes and PostScript observations to 128 ASCII bytes.
Font closure remains at most 64 resources, each at most 128 table identities.
These limits fit the conservative reservation; the implementation must document the checked component upper bound before relying on it.
Do not replace that derivation with a claim that the reservation covers every heap object.

Caller-supplied authoring values may already exist before Project receives them.
Reserve before any pipeline-owned clone, normalized array or serialization allocation.
For saved Plan8 loading, reserve the bounded encoded buffer and typed text payload before their owned allocations.
Text-free loading keeps its existing behavior and policy.
Move the plan into one shared immutable owner for workers; do not deep-clone its text evidence per worker.

Only one native text call may hold temporary admission at a time.
Use Candidate A's three-font-copy estimate plus exact string/glyph/table scratch and stride-mask bytes.
The temporary charge includes fresh evidence even while the shared prepared evidence remains retained.
Reserve the shared evidence charge, per-source persistent raster charge and maximum temporary charge in the same temporal sweep with existing payloads.
Reject combinations that exceed 512 MiB before workers or media decode start.
Individual maximum dimensions are not a promise that every maximum can run simultaneously.

Compare fresh runs incrementally when practical. If a complete fresh observation is retained, charge that complete copy.
Drop fresh evidence, font copies, alpha mask and native objects before releasing the shaping gate.
No final JSON buffer may remain live during track execution unless its separate permit remains charged.

## Compatibility and schema admission

Append defaulted, skipped-empty font imports, snapshot resources and track text clips.
Append defaulted, skipped-empty `font_closure`, `text` and `text_policy` plan fields.
Keep all current serialized field orders and absent-field byte hashes.

Use one central dispatcher with two explicit contracts:

```text
Plan2–7: existing feature selection, validation and readback behavior unchanged;
          require new text fields absent.
Plan8:   require directly used text, exact media/text scheduling and font closure;
          retain all prior media, image-alpha, motion, mask and output-profile evidence.
```

Do not globally tighten historical schema admission through a new exact feature derivation.
Plan8 conditional PNG alpha policy applies only to directly used transparent PNGs.
Text intrinsic coverage uses its closed text raster policy and does not fabricate PNG decode evidence.
The common validator is called by preparation/replay, renderer/preflight, completed verification and finalizing recovery.
Native execution performs the additional actual reshape/raster comparison; structural validation alone cannot establish glyph pixels.

The preserved real Plan7, Snapshot1-alpha and Receipt4 files become exact legacy tests before integration.
Receipt3 historical readback and existing legacy fixtures remain required.
Discovery must report text as planned until the bounded runtime and ordinary output proofs pass.
The next source version may update alpha proof wording to the accepted A17 scope without relabeling the frozen producer.

## Independent probe gate and proof inputs

The first implementation is a standalone Rust probe that does not link to the editor crate.
A separate Swift executable uses CoreText/CoreGraphics directly and shares no Rust text module.
They bind exact fonts, their source license, raw table identity, original UTF-8/UTF-16, complete runs, metrics, alpha masks and native backend.
Independent implementation comparison still shares the selected native frameworks; it is not an independent typography engine.

Use `synthetic-text-cases-a02.json`, SHA `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`.
A01 qualitative cases and all failed/earlier helpers remain unchanged.
Supported digits replace the ambiguous ASCII positive role; `ABC 123`, emoji and U+0378 must reject the whole item before raster publication.
Only actual run-font mismatch or glyph-zero evidence can satisfy those negatives.
Combining-only and ZWJ remain unqualified observations until their native results are reviewed.

Run generous explicit boxes and deliberately clipped boxes separately.
For a generous box, also draw into a larger guarded context with an exactly specified translated baseline.
Compare the complete inner raster and require no coverage outside the declared generous box.
This is a bounded fixture observation, not a universal antialias-padding guarantee.
Keep y-up matrices unchanged. A separate implementation must establish row orientation with actual text and an asymmetric coordinate control.

The Rust and Swift probes must establish byte-owned font construction, actual fallback visibility, full ranges/matrices, row policy, fixed native switches, repeated alpha hashes and backend tuple.
Record all failures. A coordinate, fallback or raster discrepancy stops product integration and triggers design revision.

After feasibility, retain Candidate A's independent pure vectors, plan tamper controls, exact legacy bytes, ordinary Plan8 V2 movie/PNG/Indic-text output, prehandoff frames, decoded ROIs, PCM/clocks, cancel/fencing/recovery and bounded peer review.
The existing 34 dB native master ROI gate remains unchanged.

## Tradeoffs and remaining limits

Explicit boxes expose intended clipping and allocation to callers. Automatic tight surfaces remain a later extension.
Once-per-active-source reshaping protects immutable evidence while bounding native work.
Native calls cannot be interrupted internally; cancellation may wait for one bounded call to return.
CoreText/CoreGraphics internal memory and complete-editor performance remain unproved.
Font shaping, native text output, full-film playback, hearing and creative acceptance remain unverified.

## Phase status

Grounding, both candidates, parent comparison and independent judgment are complete.
The synthesis repairs the two design P2 findings in the declared ownership and admission contract.
Independent synthesis recheck and isolated feasibility execution are pending.
Product runtime integration has not started.
