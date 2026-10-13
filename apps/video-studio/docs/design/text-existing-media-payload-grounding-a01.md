# Existing media payload grounding for future Plan8 text

## Scope and disposition

This is a source-only grounding report for the current accepted editor schemas 2 through 7.
It derives the existing media owner graph before text is added. It does not change Rust, fixtures,
plans, state, native output, GPU state, Resolve state, or frozen evidence. No build, test, native
call, or memory measurement was run.

The current source package is bound to
`artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01/build-a03.json`.
That manifest is 104,751 bytes with SHA-256
`0e59a36134e93e947c6263f57f94f0d50edcacd54c069f0adb37192f9b552932`.
It binds 30 Rust source paths and 18 fixture paths, including the current binary
`ff89563d736a985380c09ff64b7bccac67c7751545aa8a28425b2b2630bba57a` and lock hash
`e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.
The manifest records the authoritative byte count and SHA-256 for every listed path.
Its `watched`, `heard`, and `creativeAccepted` fields are all false.

The admission references read for this report are:

- `apps/video-studio/docs/design/text-admission-analysis-a01.md`, SHA-256
  `4c6667cf376549d3292936eaf2b7535f765384ef44371b0abe66db2cd29e53dd`.
- `apps/video-studio/docs/design/text-admission-contract-a03.md`, SHA-256
  `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f`.

The A03 text caps and owners remain provisional. This report does not convert a policy envelope
into a measured Rust or process-memory guarantee.

## Current source closure

The build manifest's 30 Rust paths are the current closure for this derivation:

```text
crates/cli/src/main.rs
crates/editor/src/alpha_picture.rs
crates/editor/src/composition.rs
crates/editor/src/curve.rs
crates/editor/src/export_stage.rs
crates/editor/src/exports.rs
crates/editor/src/frame.rs
crates/editor/src/frame_verification.rs
crates/editor/src/framing.rs
crates/editor/src/identity.rs
crates/editor/src/image.rs
crates/editor/src/layers.rs
crates/editor/src/lib.rs
crates/editor/src/mask.rs
crates/editor/src/media.rs
crates/editor/src/model.rs
crates/editor/src/motion.rs
crates/editor/src/movie.rs
crates/editor/src/native_format.rs
crates/editor/src/owned_directory.rs
crates/editor/src/pcm.rs
crates/editor/src/pixels.rs
crates/editor/src/plan.rs
crates/editor/src/project.rs
crates/editor/src/publication.rs
crates/editor/src/verified_source.rs
crates/editor/tests/frame_directory_verification.rs
crates/editor/tests/legacy_hashes.rs
crates/editor/tests/project_invariants.rs
crates/editor/tests/replay_and_cleanup.rs
```

The 18 bound fixture paths are:

```text
crates/editor/tests/fixtures/legacy/plan-schema2.json
crates/editor/tests/fixtures/legacy/plan-schema3.json
crates/editor/tests/fixtures/legacy/plan-schema4.json
crates/editor/tests/fixtures/legacy/plan-schema5.json
crates/editor/tests/fixtures/legacy/plan-schema6-masks-canonical.json
crates/editor/tests/fixtures/legacy/plan-schema6-masks-synthetic.json
crates/editor/tests/fixtures/legacy/provenance.json
crates/editor/tests/fixtures/legacy/receipt-schema2.json
crates/editor/tests/fixtures/legacy/snapshot-schema1-masks.json
crates/editor/tests/fixtures/legacy/snapshot-schema1-motion.json
crates/editor/tests/fixtures/legacy/snapshot-schema1-placement.json
crates/editor/tests/fixtures/legacy/snapshot-schema1.json
crates/editor/tests/fixtures/masks/evaluation-vectors-a01.json
crates/editor/tests/fixtures/masks/pixel-vectors-a01.json
crates/editor/tests/fixtures/motion/evaluation-vectors-a01.json
crates/editor/tests/fixtures/motion/pixel-vectors-a01.json
crates/editor/tests/fixtures/native/h264-source-a14.json
crates/editor/tests/fixtures/native/h264-source-a14.mp4
```

Relevant source hashes from that closure are:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `crates/editor/src/model.rs` | 26087 | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `crates/editor/src/project.rs` | 25370 | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `crates/editor/src/plan.rs` | 37502 | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `crates/editor/src/composition.rs` | 51727 | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` |
| `crates/editor/src/layers.rs` | 57725 | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `crates/editor/src/movie.rs` | 46119 | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `crates/editor/src/pcm.rs` | 18524 | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` |
| `crates/editor/src/pixels.rs` | 7246 | `9f2c1d86971d28ccbb89bb4678d2ea44cb8358e9d85e46451da4b7c7a2a02216` |
| `crates/editor/src/image.rs` | 21255 | `6acb1310003874d2233a885113649f34aef69c4af14694b5357d53884269eca2` |
| `crates/editor/src/alpha_picture.rs` | 27575 | `c1d755ebb0dea89db971560a3a0897d4c4c88a7f136bfe0e0f2273e6c38ce132` |
| `crates/editor/src/native_format.rs` | 39875 | `e33d9f9ff7de3e0b8793b5301a465bebcccbe3f4ab496c8454929d498cb19f23` |
| `crates/editor/src/exports.rs` | 56266 | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` |

The fixture identities include schema 2 through 6 plans, preserved schema 1 snapshots, motion and
mask vectors, and the H.264 source JSON/MP4. The H.264 MP4 is 1,319,960 bytes with SHA-256
`097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`. The manifest, rather than
this abbreviated table, is the complete source closure binding.

## Existing source to snapshot ownership

`Project::commit` starts by hashing the request and inspecting the base revision. The inspection
loads a SQLite `body` into a Rust `String`, deserializes an owned `Snapshot`, validates it, and
computes a separate asset-measurement map (`project.rs:400-406`, `project.rs:364-398`). Each import
then passes through `Studio::stage` (`project.rs:159-243`). The staging loop owns a 64 KiB stack
copy buffer, a staging file, a digest, and the imported `AssetImport` fields while it copies and
hashes the source. It probes the immutable blob and returns one owned `StoredAsset`; the source
`PathBuf`, staging file, and copy buffer then leave this scope.

`Snapshot` owns `BTreeMap<ContentHash, StoredAsset>` assets and
`BTreeMap<EntityId, Timeline>` timelines (`model.rs:482-493`). Each `StoredAsset` owns its hash,
byte count, origin lineage, media descriptor, backend string, and optional native measurement
(`model.rs:395-410`). Movie descriptors retain every measured `SampleTiming`; image descriptors
retain dimensions, format, warnings, and optional alpha facts; audio descriptors retain rate,
channels, sample count, flags, and labels (`model.rs:284-390`). The blob bytes remain on disk.

The current snapshot validator limits assets to 10,000 and each timeline to 100,000 frames
(`model.rs:500-590`). It recursively walks every origin lineage and allocates temporary `seen` and
`active` hash sets (`model.rs:536-562`). It does not cap the number of timelines, video tracks,
audio tracks, clips, descriptor samples, warning strings, or many existing strings. Track overlap,
source ranges, frame motion, mask normalization, and audio coverage are checked, but their temporary
vectors are not a memory proof (`model.rs:584-740`). These uncapped dimensions require a separate
checked charge or an explicit fail-closed rule before Plan8 preparation.

The committed snapshot is serialized into the revision record by the append path. Its identity is
`ContentHash::document`, which creates a fresh `serde_json::to_vec` buffer before SHA-256
(`model.rs:33-39`). A source revision therefore has at least the loaded SQLite `String`, the typed
snapshot, and a transient identity buffer during inspection or commit. A future text admission must
charge the loaded input before deserialization. It cannot treat a snapshot loaded from SQLite as
caller-owned.

## Snapshot to current Plan2–7 ownership

`Project::prepare_export` hashes the request, loads and verifies the selected snapshot, and passes
that owned snapshot by value to `plan::compile` (`project.rs:248-264`). The compiler validates the
snapshot and revision, then clones the requested timeline (`plan.rs:138-160`). Other snapshot
 timelines remain live in the moved snapshot until compilation returns. The compiler builds these
additional owners:

- `frame_coverage: Vec<bool>` has one entry per selected timeline frame.
- `audio_coverage: Vec<Span>` retains one span per audio clip until its sweep completes.
- `video: Vec<VideoUse>` retains one entry per picture clip.
- Each `VideoUse.presentation_ordinals: Vec<u64>` has one value per local picture frame.
- `audio: Vec<AudioUse>` retains cloned audio clips.
- `used: BTreeSet<ContentHash>` retains selected hashes and is cloned for lineage collection.
- `source_closure: BTreeMap<ContentHash, StoredAsset>` clones every used asset and ancestor.
- Normalized motion and mask values clone authored key vectors into planned values.

These allocations are visible in `plan.rs:161-406`. `ExportPlan` then owns the selected timeline,
settings, canonical audio binding, profile, `BuildIdentity`, source closure, video/audio uses,
audio frame count, and evidence vectors (`plan.rs:407-438`). Plan schemas 2 through 7 are selected
by existing media features. `Project::prepare_export` validates pixel extents and native input
evidence, updates evidence vectors, hashes the typed plan, and serializes another plan body into
SQLite (`project.rs:257-282`). The body is a `String` created by `serde_json::to_string`; it is a
second serialization lifetime after the plan identity buffer.

Replay loads the stored body into another `String`, deserializes a fresh typed plan, rejects schemas
outside 2 through 7, recomputes its identity, and returns the owned plan (`project.rs:285-325`).
`verify_plan_sources` rechecks every source-closure blob and decode evidence
(`project.rs:327-335`). The current replay branch therefore has no Plan8 path. A Plan8 implementation
must add a bounded input gate and schema branch without changing the accepted byte and identity
behavior of text-free schemas 2 through 7.

`validate_picture_mapping_cancellable` reconstructs a temporary snapshot from cloned plan fields,
validates it, and compares every `VideoUse` against the embedded timeline and source closure
(`plan.rs:566-835`). Source PTS checks use `source_closure[asset].descriptor.samples`; they do not
read a nonexistent plan sample field. This validator is a useful future ownership seam, but its
reconstructed snapshot is another simultaneous typed graph during validation.

## Checked ledger for existing media

A future source-only harness should record exact lengths and capacities at each boundary. It should
not assign one blanket byte estimate to an entire Rust struct. Define the following logical terms:

```text
H(x)       = String or PathBuf payload capacity, including its actual measured allocation.
V(T, x)    = checked capacity(x) × size_of::<T>(), plus the measured vector header.
M(K, V)    = measured BTreeMap/BTreeSet node bytes for K entries and owned key/value payloads.
J(x)       = JSON Vec or String length and capacity for one serialization lifetime.
N(x)       = native-framework ownership, reported separately and never folded into Rust bytes.
```

The harness must report `len`, `capacity`, and `size_of::<T>()` for every `Vec` and `String` it can
reach. It must report map entry count and a measured node/layout value from a crate-local probe.
`BTreeMap` and `Vec<bool>` have representation details that a `size_of` multiplication cannot infer.
An unmeasured node or allocator term is a missing guard, not zero bytes. All additions must use
checked `u128` intermediates and reject on conversion to the selected permit type.

| Owner and term | Exact source of the term | Existing bound or required guard |
|---|---|---|
| `S_assets` | `Snapshot.assets` map, hashes, `StoredAsset`, origin lineage, descriptors, warnings, labels, and backend strings | Assets `<=10,000`; all other lengths need actual-length charging or bounds |
| `S_timelines` | All snapshot timeline map nodes and all track, clip, span, framing, motion, and mask vectors | One requested timeline is selected, but snapshot timeline count is currently uncapped |
| `S_samples` | Movie `MediaDescriptor.samples` and each `SampleTiming` | No current sample-count cap; bind to measured probe bytes and count |
| `S_validate` | Temporary lineage `seen`/`active`, overlap vectors, and normalization outputs | Cancellation exists; count and capacity need measurement before normalization |
| `S_selected_timeline` | `snapshot.timelines[request.timeline].clone()` | `frame_count <=100,000`; clip and track counts need guards |
| `S_video` | `Vec<VideoUse>` and per-use `presentation_ordinals` | Accepted layered execution has at most four nonempty picture tracks; `O = sum(ordinals)` is at most `4 × 100,000` after that check |
| `S_audio` | `Vec<AudioUse>`, cloned `AudioClip`s, and `audio_coverage` spans | Audio track and clip counts are not capped by current snapshot validation |
| `S_used` | `BTreeSet` selected hashes, its clone, and recursive closure sets | Closure entry count is bounded only by the 10,000 asset map today |
| `S_closure` | Cloned `StoredAsset` values in `ExportPlan.source_closure` | At most the used lineage closure; each value is charged separately from `S_assets` while both live |
| `S_plan` | `ExportPlan` timeline, settings, closure, video/audio uses, evidence, profile, and renderer | No fixed byte guarantee; every nested capacity must be measured |
| `J_request` | `ContentHash::document(&request)` in `prepare_export` | No current request JSON cap |
| `J_revision` | Snapshot identity serialization during inspection/commit | No current revision JSON cap |
| `J_plan_id` | `ContentHash::document(&prepared.plan)` after evidence | No current plan identity JSON cap |
| `J_plan_body` | `serde_json::to_string(&prepared.plan)` for SQLite | Coexists with typed plan until SQL execution; no current cap |
| `J_replay` | SQLite body `String` plus typed plan from `serde_json::from_str` | Current replay has no bounded pre-parser |

For an accepted current picture plan, use these derived quantities rather than guessed constants:
`T = timeline.frame_count <= 100,000`, `W <= 4` nonempty picture tracks after preflight,
`K_v = video-use count`, `K_a = audio-use count`, `O = sum of presentation-ordinal lengths`,
`D = source-closure entries`, and `F = total retained movie sample timings`. The accepted-track
check implies `O <= W × T` only after plan validation succeeds. It does not bound `K_v` before
validation, and it does not bound `K_a` at all. A Plan8 preflight must reject those cases before
cloning vectors.

The current model also leaves `Snapshot.name`, `Settings.working_color`, descriptor format and
codec strings, backend strings, warning and decode-error strings, channel labels, and
`AudioBinding.channel_order_basis` without explicit length caps. A text-only permit cannot charge
these as zero. The old-media admission must either cap each field or add its measured `H(x)` term to
the same preparation ledger.

## Execution ownership and worker payloads

For schemas 4 through 7, `movie::write_inner` clones the entire `ExportPlan` into a decoder worker
(`movie.rs:163-209`). `layers::decode` then clones that plan again into an `Arc` before it starts
one worker per nonempty picture track (`layers.rs:618-680`). The `Arc` clone is cheap after the
second deep clone, but the two plan clones are real typed payloads. Each worker also owns a vector of
video-use indices, a `PathBuf`, signal and budget `Arc`s, and one request and response
`sync_channel(1)`. The environment and channels are private, so an external measurement harness
cannot inspect them without a crate-local test seam.

`run_track` clones the current `VideoUse` at each clip boundary (`layers.rs:266-335`). An image
worker caches one decoded picture and its source permit across held frames. A movie worker captures
a plan `Arc`, a `VideoUse`, response sender, and control state in the native media completion
callback (`layers.rs:336-431`). Native reader objects live inside that callback. The callback copies
one native BGRA frame into a Rust-owned `Pixels`, rasterizes it, sends a boxed `LayerFrame`, and
drops the copied frame and source permit before the next source sample. The Rust worker waits while
that callback and its native objects remain live; this does not prove a separate worker thread has
stopped.

`Decision::Source(Box<LayerFrame>)` moves a raster and its logical `Permit` through the response
channel. The parent checks identity, PTS, observation, and bounds before blending
(`layers.rs:440-510`). `Workers::finish` drops request and response senders and joins workers;
`Drop` sets the stop flag (`layers.rs:76-113`). `send` and `receive` poll bounded channels with
cancellation checks (`layers.rs:116-145`). A future text payload must use the same cancellation
aware ownership rule. It must not send a non-droppable retained raster or shaping permit across a
channel that can outlive its cancellation owner.

The parent allocates one opaque canvas per timeline frame and sends one `EvaluatedFrame` through a
bounded output channel (`layers.rs:689-765`). `EvaluatedFrame` owns a `Pixels` and optional picture
permit. The writer keeps one `pending` frame while it appends video (`movie.rs:357-434`). With the
current capacity-one output channel, the source-level frame ledger must allow a current canvas, one
queued `EvaluatedFrame`, and one writer `pending` frame. Those are three possible Rust `Pixels`
owners at different pipeline points. The exact overlap must be measured around channel scheduling;
`MAX_ADMITTED_BYTES` is only a logical permit ceiling.

## Raster and audio/video temporary charges

`pixels::extent` checks width times height times four against
`MAX_OWNED_FRAME_BYTES = 128 MiB` (`pixels.rs:13-33`). `Pixels::copy` locks a native pixel buffer,
allocates packed BGRA bytes, copies each native row, and releases the lock (`pixels.rs:45-120`).
`Pixels::into_native` allocates a new native pixel buffer and copies the packed rows
(`pixels.rs:121-165`). The native pixel buffer is a framework-owned `N` term, not a Rust vector.

PNG input uses one opened file and a bounded `Vec<u8>` of at most
`MAX_FILE_BYTES = 129 MiB` (`image.rs:10-31`). Decode then owns expanded samples and either a
packed opaque `Pixels` or `StraightRgba8`; alpha sampling owns `PremulBgra16` values at eight bytes
per raster pixel (`alpha_picture.rs:27-135`). `raster_bytes` checks the 128 MiB owned-frame limit.
The current picture preflight charges `source_bytes + raster_bytes` per dynamic source frame and
tracks the largest `source_bytes + asset.bytes + 128 MiB` PNG temporary
(`composition.rs:641-733`). It then adds three canvas extents and that PNG temporary to the 512 MiB
logical estimate (`composition.rs:741-778`). This is an admission formula, not a process peak: it
does not measure allocator overhead, native CVPixelBuffers, AVAssetReader buffers, or all clone
lifetimes.

For audio, `pcm::Stream` owns a worker, a bounded `sync_channel(2)`, and `PcmStreamEvidence`
(`pcm.rs:21-133`). Each `PcmChunk` owns at most 4,096 interleaved stereo `f32` frames
(`pcm.rs:36-45`). The converted sample vector is at most `4096 × 2 × 4 = 32,768` bytes. The
native block-copy byte buffer can reach the same 32,768 bytes before conversion; the source-level
copy ledger must allow both when their scopes overlap. Two queued chunks add at most
`2 × 32,768` bytes of Rust-owned sample payload. Native CMSampleBuffer and CMBlockBuffer ownership
remains an `N` term.

`native_format::NativeWriterSession` owns AVAssetWriter inputs, the adaptor, and native retained
objects (`native_format.rs:552-771`). `append_audio` builds a native PCM sample buffer from the
chunk, and `append_picture` consumes a native pixel buffer. `finish` waits for the writer, while
`Drop` cancels an incomplete session. `movie::encode_frames` owns counters, the output receiver,
one pending frame, and the audio stream (`movie.rs:357-434`). The output stage file is disk
ownership. `exports::export` owns the staged artifact, lease/control state, verification, immutable
receipt CAS, and publication transition (`exports.rs:1143-1292`). None of these native or OS file
allocations is included in the Rust typed text envelope.

A source-only ledger should therefore report these formulas:

```text
B_snapshot       = S_assets + S_timelines + S_revision_input + S_validate
B_compile        = B_snapshot + S_selected_timeline + S_used + S_video + S_audio
                   + S_closure + S_plan + J_request + J_revision + J_plan_id
B_prepare_peak   = max(B_compile, B_compile + J_plan_body, replay-specific lifetimes)
B_picture_peak   = B_plan_worker_clones + B_canvas_slots + B_layer_rasters
                   + B_png_temporary + B_pcm_chunks + B_channel_payloads
B_native         = N(reader buffers, CVPixelBuffers, CMSampleBuffers, writer/adaptor)
```

`B_native` must remain a separate observed category. The existing 512 MiB budget covers only the
logical reservations made by `composition::Budget`; it is not a process-memory guarantee and does
not cover uncharged plan graphs or arbitrary native framework allocations.

## Future Plan8 owner seams

The selected A03 names are `Snapshot::font_resources`, `ExportPlan::font_closure`, `ExportPlan::text`,
and `ExportPlan::text_policy`. These fields do not exist in the current source. The future source
path should preserve the following ownership transitions:

1. A bounded source input owns the Plan8 JSON bytes before parsing. A token gate and bounded visitor
   reject counts, strings, nesting, and unknown fields before `serde` grows typed vectors.
2. `SourceOwner` owns source text, font resources, authoring curves, and all current media fields.
   Its text string is `S_snapshot`.
3. A private `DraftOwner` normalizes text, font closure, curves, and evidence. It cannot enter
   SQLite or a worker channel. It is dropped or moved once.
4. One immutable `SharedOwner` becomes the final Plan8 typed payload. The embedded plan timeline is
   the authoring authority. `TextUse::source` is a bounded duplicate and must compare byte-for-byte
   with that timeline value.
5. One `JsonOwner` owns the canonical JSON bytes used for hashing and storage. The implementation
   must reuse that buffer or charge every simultaneously live serialization buffer.
6. One `GateOwner` owns UTF-8, UTF-16, copied runs, native text objects, and alpha storage through
   one shaping operation. It releases only after native objects and copied evidence drop.
7. One `RasterOwner` shares an admitted text raster and permit across frames. It must follow the
   current `Decision` and cancellation teardown rules.
8. `MediaOwner` remains the current snapshot, plan clones, source closure, movie/image/audio
   workers, canvases, writer, response, receipt, and reopen verification. Text admission composes
   with these owners; it does not replace them.

The A03 fixed-item rows cover the embedded timeline and `TextUse.source` pair. They do not cover
`S_snapshot`. The current source-to-plan graph proves that the snapshot and plan copies coexist
while `plan::compile` runs. A future implementation must record whether it moves a value or clones
it, then charge exactly the live owners. It must not claim that an immutable `Arc` removes the deep
`plan.clone()` calls already present in `movie.rs` and `layers.rs`.

Text-free schemas 2 through 7 must preserve their existing schema selector, JSON bytes, plan hash,
source closure, and replay behavior. A Plan8 request must not fall back to a text-free schema after a
text admission failure. The old parser may remain for text-free historical bodies, but Plan8 input
must pass the bounded pre-parser described by A03 before typed deserialization.

## Required source-only proof before text integration

The first measurement harness should live inside the editor crate under an explicitly test-only
seam. Current `Pixels`, `Mapping`, `Budget`, `LayerFrame`, worker environment, `PcmChunk`, and
native writer types are private or `pub(crate)`; `lib.rs` exports only selected public model,
project, plan, and export types (`lib.rs:1-52`). An external standalone crate cannot measure these
owners without copying source, adding a temporary crate-local test seam, or changing visibility.
No such seam or harness was created in this task.

The future harness must capture, without native calls first:

- exact byte length and capacity for request, revision, plan identity, and SQLite plan JSON;
- snapshot map counts and owned capacities before and after `plan::compile`;
- timeline, clip, curve, mask, ordinal, audio, evidence, closure, and lineage capacities;
- deep clone counts for `write_inner` and `layers::decode`;
- channel capacities, queued payload counts, canvas slots, and raster permits;
- image input and decoded-picture overlap for opaque and alpha PNGs;
- PCM chunk, conversion buffer, and output-frame overlap;
- cancellation at parse, validation, worker send, reader callback, audio pull, writer finish,
  and receipt verification;
- current schemas 2, 3, 4, 5, 6, and 7 using the preserved fixture identities; and
- a text-free Plan8-adjacent run that proves old media charges remain when text is absent.

After native feasibility and the first implementation, a second pass must add `N` observations for
AVAssetReader, CVPixelBuffer, CMSampleBuffer, CoreText, CoreGraphics, writer/adaptor, and
autorelease-pool lifetimes. That pass can establish a measured run for a particular producer. It
cannot turn the source-only ledger into a universal macOS process-memory bound.

The immediate unresolved P1 items are the uncapped old-media strings and timeline/track/audio
counts, descriptor sample cardinality, serializer duplication, plan deep clones, and native
memory. The existing 512 MiB logical picture gate is useful evidence, but it cannot close those
items. The next implementation review should reject a Plan8 payload until every missing term has a
checked cap or a measured actual-length charge.
