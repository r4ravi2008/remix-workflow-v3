# Existing-media admission next design A01: independent review

## Scope and disposition

This is an independent source and design review of `text-existing-media-admission-next-design-a01.md`.

The reviewed design is source-only and has not changed the editor, fixtures, state, executables, media, GPU, or Resolve resources.

The design correctly limits its claim to application-owned logical Rust payloads. It does not claim RSS, allocator metadata, native framework memory, process memory, or audiovisual acceptance.

Plan8 is not ready for integration. The admission boundary is currently later than several allocations that the design intends to control.

## Bound source identity

The design file is 20,891 bytes with SHA-256 `d128ec8cb5114d98ef9a68fb1f5a27d174ff653445cd7819e690697234518a3e`.

The current source files still match the identities bound by the design:

| File | SHA-256 |
| --- | --- |
| `crates/editor/src/model.rs` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `crates/editor/src/plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `crates/editor/src/project.rs` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `crates/editor/src/composition.rs` | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` |
| `crates/editor/src/media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `crates/editor/src/layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `crates/editor/src/movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `crates/editor/src/pcm.rs` | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` |

The A03 report measured a 10,000-entry B-tree probe. It recorded 2,378 capacity rows, 28 B-tree rows, and seven precreation rows. Those records are observations, not maximums.

## P1: the admitted scratch domain exceeds the measured tree domain

`Snapshot::validate_cancellable` creates one `BTreeSet<EntityId>` for each timeline and inserts every video and audio track ID and clip ID (`crates/editor/src/model.rs:584-729`). The same validation also creates per-track span vectors and normalizes motion and masks.

The current validator caps assets at 10,000 and each timeline at 100,000 frames (`model.rs:500-508`, `model.rs:584-598`). It does not cap timeline count, track count, video clip count, audio clip count, or lineage input count before those collections are built.

The selected Plan8 rules allow four picture tracks and up to 400,000 selected clip-frame ordinals (`text-existing-media-admission-next-design-a01.md:163-167`). A selected timeline can therefore insert roughly 400,000 clip IDs, plus track and audio IDs, into its ID set. That is already greater than the A03 tree control domain of 10,000 entries.

Unselected timelines are a larger gap. The design says they remain authoring state but receive full source-owner charges (`design-a01.md:174-176`). Current Snapshot validation still visits every timeline. Since current validation has no per-timeline track or clip cap, an unselected timeline can exceed 10,000 IDs even when its frame count is valid.

The A03 `BTreeSet<EntityId>` probe observed 1,548 allocation callbacks for its 10,000-entry probe. It does not establish behavior for 400,000 IDs, or for the sum of all unselected timelines. The factor-16 policy envelope is useful as a policy formula, but it does not extend the evidence domain by itself.

This is a P1 admission gap. The next contract must either reject before validation scratch is created, or measure the complete admitted maximum. It must define limits for total track-plus-clip IDs per timeline, total IDs across unselected timelines, and all transient span, lineage, coverage, and normalization collections. The tree controls must run through those actual maxima with every admitted key/value shape and insertion order.

`BTreeSet<ContentHash>` lineage state is a separate owner. The design's 10,000 `Origin.inputs` limit is per asset, so 10,000 assets could still describe 100 million source edges without an aggregate edge limit. That aggregate and the temporary `seen` and `active` sets also need a checked bound.

## P1: the proposed inspection API is too late to bound parsing and validation

`Project::prepare_export` calls `verify_assets` and then `plan::compile` before it persists a plan (`crates/editor/src/project.rs:248-283`). `verify_assets` reaches `inspect_from`, which retrieves the entire SQLite body as a `String`, deserializes it, and only then calls `snapshot.validate()` (`project.rs:364-398`, `518-527`). `plan::compile` validates the same typed snapshot again (`crates/editor/src/plan.rs:138-145`).

The current code has no 64 MiB body check before the SQLite `String` allocation. The proposed `inspect_plan8_snapshot(&Snapshot, ...)` therefore cannot provide the design's step-1 through step-6 ordering. A typed snapshot already owns its maps, vectors, strings, sample arrays, and nested source inputs before that function starts.

The Plan8 path needs a separate bounded read and parse boundary. First check the SQLite body byte length, then fetch at most the admitted bytes as a bounded byte buffer. Run a bounded token or visitor gate before constructing typed sequences. Bound maps, arrays, strings, duplicate keys, unknown keys, movie samples, warnings, channel labels, origin inputs, and nested curve keys during that parse. Only then build the typed source owner and run semantic Snapshot validation.

The gate must also charge or avoid `Origin::sources`, which creates a new `Vec<&SourceRange>` on each call (`model.rs:239-248`), and the motion and mask normalization allocations in `model.rs:623-642`. A post-parse capacity walk cannot prevent those earlier allocations.

## P1: plan construction and worker cloning are not currently charged

The current `composition::Admission` contains only tracks, peak active sources, and estimated bytes (`crates/editor/src/composition.rs:630-634`). Its preflight covers the temporal media sweep, canvas, source/raster peaks, and PNG temporary allowance (`composition.rs:641-785`). It does not include the retained `ExportPlan`, source closure, sample arrays, ordinal arrays, evidence vectors, or JSON buffers.

`plan::compile` allocates frame and audio coverage, presentation ordinals, normalized motion and masks, lineage sets, audio and video uses, and a cloned source closure (`plan.rs:161-165`, `200-305`, `312-406`). `validate_picture_mapping_cancellable` clones the source closure and timeline into a second Snapshot before validating (`plan.rs:566-589`). `movie::write_inner` then clones the entire plan for the decoder worker (`movie.rs:163-180`).

The proposed fixed-plan permit must cover these owners at their real lifetimes. It must cover the validation clone or remove that clone. It must remain live through the worker, callbacks, response, writer, cancellation, and join. A dynamic picture permit alone cannot establish the 512 MiB logical bound.

## P1: sound Plan8 discriminator before bounded body parsing

The current `Snapshot.schema` is always `1` and does not distinguish a future Plan8 authoring body. The current compiler chooses output plan schemas `2..=7` from alpha, mask, motion, layering, and image-source properties (`plan.rs:407-443`). `MovieProfile` is also unsuitable as a discriminator because existing requests already use H264 and NativeColorMaster profiles (`plan.rs:10-28`). Body sniffing or profile inference would therefore reinterpret legacy input.

Use an explicit request-side mode. A compatible shape is an optional field on `ExportRequest`, such as `mode: Option<ExportMode>`, with `serde(default, skip_serializing_if = "Option::is_none")`. A missing field means the existing legacy path. A present `Plan8` value is part of the request hash and selects the new path. The skip rule preserves the old serialized request bytes and request hash when the field is absent.

Branch on that mode before calling the existing `replay_plan` or `verify_assets` path. The legacy branch must retain the current Plan2–7 replay, Snapshot parse, validation, compile, hash, and storage behavior. The Plan8 branch must use its own bounded revision reader, token gate, source admission, plan builder, and replay record.

Do not sniff a JSON `schema` field with `serde_json::Value`. That allocates an unbounded intermediate and the current Snapshot has no useful Plan8 marker. Do not use `MovieProfile` as the mode.

For persistence, use a separate Plan8 metadata/table keyed by intent and request hash, or an explicit mode column that old rows do not populate. Do not place a schema-8 body in the legacy `plans` row and rely on `replay_plan`; that function reads an entire `String`, deserializes without a size gate, and intentionally accepts only schemas `2..=7` (`project.rs:285-326`).

For the revision body, check `length(CAST(body AS BLOB))` before fetching it. Then fetch bounded bytes and bind the raw bytes to the requested revision hash before parsing. The existing `r.get::<String>` path is not a Plan8 boundary.

## P2: audio cardinality is still checked after plan construction

`movie::validate_profile_cancellable` enforces one audio use, 48 kHz stereo, complete coverage, unity gain, and zero pan (`movie.rs:63-109`). `Project::export` calls it only after `prepare_export` returns (`exports.rs:1143-1147`). The current compiler has already built the audio vector and coverage before that rejection (`plan.rs:312-345`).

The Plan8 gate must check the one-track, one-clip source contract before compile allocations. It must also repeat the typed semantic check after bounded parsing. The existing import probe's 100,000 movie-sample guard is not enough for replay: stored descriptors must be checked again before typed sample-vector use.

## P2: the one-buffer JSON promise is not current behavior

`ContentHash::document` hashes a `serde_json::to_vec` buffer, while plan persistence calls a separate `serde_json::to_string` (`model.rs:36-38`, `project.rs:272-280`). The bytes used for identity and storage can therefore be distinct allocations and distinct representations.

The Plan8 path needs one owned canonical byte buffer. It must hash and store that same buffer, with an explicit capacity limit and a failure record that preserves the buffer owner until persistence finishes. The legacy serializer and byte identity must remain unchanged.

## P2: existing old-media owners need explicit Plan8 caps

Current Snapshot validation does not cap timeline count, track vectors, clip vectors, `Origin.inputs`, warning vectors, channel-label vectors, or descriptor string lengths before deserialization. `MediaDescriptor::Movie.samples` and warnings are owned vectors (`model.rs:284-313`). Current `media::probe` limits imported movie samples, but replayed stored descriptors bypass that import call.

The design should also account for `Settings.working_color`, backend and codec strings, decode errors, source lineage strings, span vectors, `reject_overlap` scratch, `Origin::sources` temporary vectors, and normalized motion and mask data. The current source owner and the current compiler scratch must have separate owner paths in the ledger. A single root `Layout` plus container headers would double count some inline fields and still miss tree nodes; the ledger needs one non-overlapping ownership rule.

## Confirmed design boundaries

The design correctly keeps Plan2–7 serialized bytes, hashes, receipts, and validation behavior unchanged in principle (`design-a01.md:359-373`). That compatibility claim still needs a byte-identity regression after implementation.

The design correctly states that A03 rows are observations, not maxima, and that native and physical memory remain outside scope (`design-a01.md:97-110`, `436-444`). Those limits should remain in the next contract.

## Required next proof

1. Define all Plan8 count caps before typed deserialization, including unselected timelines, per-timeline track-plus-clip IDs, aggregate lineage edges, and normalization keys.
2. Measure each B-tree and set shape from zero through the true admitted maximum, with sorted, reverse, and deterministic shuffled insertion.
3. Add a request-mode compatibility fixture. Verify that an old request with no mode keeps its exact bytes and hash, and still uses the unchanged Plan2–7 path.
4. Add a bounded SQLite read fixture. Reject an oversized body before typed allocation, and reject malformed bounded input before plan cloning or worker startup.
5. Prove the fixed-plan charge across source parsing, Snapshot validation, compile, mapping revalidation, plan cloning, worker lifetime, cancellation, and all error exits.
6. Prove that Plan8 identity and storage use one canonical byte buffer. Re-run the frozen legacy plan, receipt, and output identities.

No tests, builds, native calls, media operations, GPU operations, or Resolve operations were run for this review.
