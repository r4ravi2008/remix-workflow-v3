# Native text admission contract A02

## Scope and status

This document is the implementable admission successor to `text-admission-analysis-a01.md`.
It preserves A01's arithmetic and makes ownership, lifetime, and rejection points explicit.

This is design work only. It changes no Rust source, fixture, probe, build, native state, GPU,
Resolve project, or frozen evidence. It makes no claim about CoreText, CoreGraphics, allocator,
or process memory peaks. Every Rust representation envelope below is **PROVISIONAL** until the
native feasibility probe and the first Rust implementation measure actual layouts, capacities,
serializer copies, and drop order.

The selected inputs remain:

- `apps/video-studio/docs/design/text-synthesis-a01.md`, SHA-256
  `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323`;
- `apps/video-studio/docs/design/text-candidate-a01.md`, SHA-256
  `6851884d8a76ce5a44181eab1d5c7991f61b323754907b4aaeb4ef69c9c6198e`;
- A01 arithmetic review,
  `apps/video-studio/docs/design/text-admission-analysis-a01.md`, SHA-256
  `4c6667cf376549d3292936eaf2b7535f765384ef44371b0abe66db2cd29e53dd`.

Plan8 is selected only when the requested timeline directly uses text. Text-free requests retain
the existing schema selector and admission behavior. A Plan8 admission failure is a rejection;
it must not silently fall back to an older schema or an unbounded representation.

## Ownership vocabulary

The contract counts pipeline-owned bytes by simultaneous lifetime. It does not count caller-owned
arguments before the pipeline clones them. It does count every pipeline-owned clone and every
capacity that remains live.

| Owner | Contents | Required lifetime rule |
| --- | --- | --- |
| `SourceOwner` | Snapshot text, source font resources, authoring curves, and existing media snapshot fields | May coexist with a draft during preparation. Its charge is separate from the final shared plan. |
| `DraftOwner` | Private normalized text and media draft | Cannot serialize, enter SQLite, or cross a worker channel. Drop or move it at finalization. |
| `SharedOwner` | One immutable finalized Plan8 typed payload | Workers share one owner. They do not deep-clone text evidence, fonts, runs, or rasters. |
| `JsonOwner` | One canonical Plan8 JSON `Vec<u8>` | The same bytes are hashed and passed to storage. A second application-owned JSON buffer is rejected or charged separately. |
| `GateOwner` | One text shaping operation and its temporary Rust-owned copies | At most one gate permit exists. It releases only after native objects, copied evidence, and the alpha buffer drop. |
| `RasterOwner` | One `Arc<AdmittedTextRaster>` and its permit | A response and worker may share the same raster. No per-frame full-raster clone is allowed. |
| `MediaOwner` | Existing snapshot, plan, decode, canvas, writer, and response payloads | Existing media charges remain part of the same 512 MiB aggregate sweep. |

The source snapshot is not a hidden part of the shared plan. The final plan stores only the
directly used font closure and normalized text evidence. If source and plan own equal bytes at the
same time, both charges apply. If an implementation moves ownership without cloning, one charge
remains. The accounting record must state which operation occurred.

## Admission limits

These are application-owned v1 limits. A validator checks them before any pipeline-owned clone,
normalization, native call, or serialization allocation.

| Quantity | Exact limit |
| --- | ---: |
| Font resources in one snapshot | `256` |
| Font imports in one commit | `64` |
| One exact font blob | `1..=16 MiB` |
| SFNT tables in one font | `1..=128` |
| Text clips in one timeline | `4,096` |
| Text UTF-8 bytes per item | `1..=8,192` |
| Text UTF-16 units per item | `1..=4,096` |
| Total authored UTF-8 bytes per plan | `1 MiB` |
| Total planned UTF-8 bytes per plan | `1 MiB` |
| Total authored UTF-16 units per plan | `524,288` |
| Total planned UTF-16 units per plan | `524,288` |
| CoreText runs per item | `256` |
| Total planned runs per plan | `4,096` |
| Glyphs per item | `16,384` |
| Total planned glyphs per plan | `131,072` |
| Combined authored and normalized motion/mask keys | `65,536` |
| Direct font resources in one Plan8 closure | `64` |
| Lines per text item | exactly `1` |
| Distinct run-font objects per item | `4` |
| Canonical Plan8 JSON | `64 MiB` |
| Text raster width | `1..=8,192` |
| Text raster height | `1..=2,048` |
| Text raster pixels | `1..=4,194,304` |
| Font size | Q16 `1..=512` pixels |
| Nonempty picture tracks | existing `1..=4` |
| Aggregate logical picture payload | existing `512 MiB` |

The authored and planned UTF-8 and UTF-16 counts are separate because source and final plan strings
can coexist during preparation. The key count includes authored and normalized copies together.
The glyph and run totals count every text item. Per-property curve counts are included in the
combined motion/mask total.

## Exact new string and identity limits

The following bounds close the new serialized strings. A value exceeding a bound fails before it
is copied. Hashes are fixed-format `ContentHash` values and do not use a general string budget.

| Field | Encoding and maximum |
| --- | --- |
| `FontResourceImport.path` | OS-string bytes `<=4,096`; reject an unmeasurable path |
| `FontResourceOrigin::Imported.external_source` | UTF-8 bytes `<=4,096` |
| `FontResourceOrigin::Imported.role` | UTF-8 bytes `<=1,024` |
| `StoredFontResource.backend` | UTF-8 bytes `<=128` |
| `FontFaceDescriptorV1.postscript_name` | nonempty ASCII bytes `<=128` |
| `TextSourceObservationV1.text` | UTF-8 bytes `<=8,192`; UTF-16 units `<=4,096` |
| `TextLanguage` | canonical lowercase ASCII grammar, maximum `12` bytes |
| `TextRunEvidenceV1.postscript_name` | nonempty ASCII bytes `<=128` |
| `SfntTableIdentity.tag_hex` | exactly `8` lowercase ASCII bytes |
| `TextBackendIdentityV1.*.bundle_identifier` | ASCII bytes `<=128` |
| `TextBackendIdentityV1.*.bundle_version` | ASCII bytes `<=64` |
| `TextBackendIdentityV1.*.short_version` | ASCII bytes `<=64` when present |
| `BuildIdentity.native_backend` | UTF-8 bytes `<=128` |
| `BuildIdentity.host_os` | ASCII bytes `<=64` |
| `BuildIdentity.architecture` | ASCII bytes `<=32` |
| `BuildIdentity.executable_uuid` | ASCII bytes `<=64` when present |
| `ContentHash` values | exactly `64` lowercase ASCII bytes |
| `EntityId` values | existing maximum `128` bytes |

`TextAlgorithm`, `TextDirection`, `TextNormalization`, and `FontContainer` are closed enums and
add no caller-controlled strings. The language grammar remains the selected bounded UTS #35
subset. The backend tuple is a value, not a path or a family lookup.

The existing media model still has strings without these new bounds, including `Snapshot.name`,
`Settings.working_color`, `StoredAsset.backend`, media descriptor format and codec fields,
decode errors, warnings, audio channel labels, and `AudioBinding.channel_order_basis`. A Plan8
admission must receive an existing checked media charge for these fields, or fail closed until
the old media validator supplies bounds. Text admission must not treat their serialized length as
zero.

## Provisional component envelope

The proposed 128 MiB retained text envelope has two separately named permits. `TypedPlanPermit`
covers the owned Rust Plan8 fields. `JsonPermit` covers one canonical JSON buffer while it
coexists with the typed fields. Their sum is the `SharedTextPermit`. This keeps JSON duplication
visible while preserving the A01 128 MiB calculation.

The following bytes are policy envelopes, not `size_of::<T>()` measurements:

| Component | Maximum calculation | Bytes |
| --- | ---: | ---: |
| Fixed metadata for text items | `4,096 × 4,096` | `16,777,216` |
| Authored UTF-8 strings | `1 MiB` | `1,048,576` |
| Planned UTF-8 strings | `1 MiB` | `1,048,576` |
| Authored UTF-16BE units | `524,288 × 2` | `1,048,576` |
| Planned UTF-16BE units | `524,288 × 2` | `1,048,576` |
| Run records and full matrices | `4,096 × 1,024` | `4,194,304` |
| Glyph, position, advance, and index arrays | `131,072 × 128` | `16,777,216` |
| Authored and normalized motion/mask keys | `65,536 × 128` | `8,388,608` |
| Direct font metadata and measurement identity | `64 × 16,384` | `1,048,576` |
| Direct font table identities | `64 × 128 × 256` | `2,097,152` |
| **TypedPlanPermit subtotal** | **sum above** | **`53,477,376` = 51 MiB** |
| One canonical JSON buffer | `64 MiB` | `67,108,864` |
| **SharedTextPermit subtotal** | **typed + JSON** | **`120,586,240` = 115 MiB** |
| **Unused 128 MiB margin** | **`128 MiB - subtotal`** | **`13,631,488` = 13 MiB** |

The authored and planned rows intentionally show separate copies. The font term in A01 is
equivalent to `64 × (16,384 + 128 × 256)`. The split rows make the table auditable.
In the lifetime equations below, `T_source` owns the authored rows and `T_plan` owns the
planned rows. The table's combined total must not be added a second time to either variable.

The 4,096-byte item envelope covers authored and planned fixed fields as one item pair. The
1,024-byte run envelope includes ranges, status, two full six-component matrices, names, and
vector overhead. The 128-byte glyph envelope includes glyph IDs, positions, advances, source
indices, and vector overhead. These meanings are provisional and must be measured after the
Rust types exist. A type with larger capacity or unaccounted allocator metadata fails the permit;
it does not silently redefine the envelope.

The full 256-font source map has a separate provisional metadata estimate:

```text
256 × (16,384 + 128 × 256) = 12,582,912 bytes = 12 MiB.
```

It is not part of the final 64-font Plan8 closure. If all 256 source descriptors coexist with
the 115 MiB shared text envelope, the arithmetic reaches 127 MiB before old media fields and
allocator overhead. Preparation therefore records that overlap explicitly and uses the larger
prepare sweep below. It must stage or release source metadata before relying on the 128 MiB
shared permit if the measured implementation does not fit its margin.

## Padded alpha-mask maximum

The alpha buffer charges `align_up(width, 16) × height` bytes. The dimensions must satisfy:

```text
1 <= width <= 8,192
1 <= height <= 2,048
width × height <= 4,194,304
```

For every allowed integer width, set `height = min(2,048, floor(4,194,304 / width))`.
An exhaustive integer sweep gives the unique maximum at:

```text
width  = 2,049
height = 2,047
stride = align_up(2,049, 16) = 2,064
bytes  = 2,064 × 2,047 = 4,225,008 bytes = 4.029281616 MiB
```

The dimensions use 4,194,303 visible pixels, leaving one pixel below the area cap. A simple
closed bound is `4,194,304 + 15 × 2,048 = 4,225,024` bytes. The contract uses the exact
4,225,008-byte maximum when the implementation proves the same dimensions and alignment rule.
The first `width` bytes of each row are canonical samples. Padding still receives a charge.

No second whole canonical alpha buffer is permitted. If implementation needs one, it reserves
another `4,225,008` bytes before allocation and keeps both permits until the first buffer drops.

## One shaping gate and temporary charge

One cancellable gate serializes CoreText and CoreGraphics text work. The gate is a logical
Rust-owned permit. It does not cap opaque framework allocations.

The corrected conservative gate addends are:

| Gate component | Maximum calculation | Bytes |
| --- | ---: | ---: |
| Rust font, copied `CFData`, one copied table | `3 × 16,777,216` | `50,331,648` |
| One UTF-8 source buffer | `8,192` | `8,192` |
| One UTF-16 buffer | `2 × 4,096` | `8,192` |
| Glyph arrays at the 128-byte envelope | `128 × 16,384` | `2,097,152` |
| One padded alpha buffer | exact maximum above | `4,225,008` |
| One item fixed envelope | `4,096` | `4,096` |
| 256 run envelopes | `256 × 1,024` | `262,144` |
| One font metadata envelope | `16,384` | `16,384` |
| One font's 128 table records | `128 × 256` | `32,768` |
| **Maximum temporary gate** | **sum above** | **`56,985,584` = 54.345687866 MiB** |

The 64-to-128 glyph adjustment is `64 × 16,384 = 1,048,576` bytes. The added metadata is
`4,096 + 262,144 + 16,384 + 32,768 = 315,392` bytes. Therefore:

```text
55,621,616                         baseline gate
+ 1,048,576                        glyph adjustment
+   315,392                        item/run/font metadata
= 56,985,584 bytes
```

The gate includes the alpha buffer and temporary font copies. It excludes the persistent
premultiplied raster, the shared plan, JSON, native framework internals, allocator bookkeeping,
and any complete second fresh-evidence tree. A complete retained fresh-evidence tree must use
the same gate permit's measured component ledger, not an uncharged exception.

## Persistent text rasters

The selected private raster is `PremulBgra16`, provisionally eight bytes per pixel:

```text
8 × 4,194,304 = 33,554,432 bytes = 32 MiB per active text source.
```

The current one-cache-per-nonempty-track design permits at most four simultaneous caches:

```text
4 × 33,554,432 = 134,217,728 bytes = 128 MiB.
```

The compositor borrows a clipped view. A frame-local copy is rejected unless its exact bytes are
added to the execute sweep. The response and worker hold `Arc` references to the same permit.

## Prepare lifetime sweep

Preparation has three distinct peaks. The implementation records actual ownership at each peak;
it does not add bytes from phases that cannot overlap.

Define these checked quantities:

- `M_source`: current Snapshot-owned media fields and source maps, including all old timeline,
  asset, audio, descriptor, and bounded-string payloads;
- `T_source`: authored text strings, source curves, font-resource descriptors, and the full
  256-resource source metadata estimate when that map is live;
- `M_plan`: current ExportPlan-owned media fields, including timeline, settings, canonical audio,
  renderer, source closure, `VideoUse.presentation_ordinals`, audio uses, decode evidence, image
  evidence, and alpha policy;
- `T_plan`: the typed Plan8 text payload under `TypedPlanPermit`;
- `G`: the maximum temporary gate charge `56,985,584`;
- `J`: one `JsonPermit` of at most `67,108,864` bytes;
- `O_prepare`: measured Rust container, capacity, allocator, channel, and error-storage overhead;
- `C_old_prepare`: any existing media source or preparation charge not already included in
  `M_source` or `M_plan`.

The three checked peaks are:

```text
shape_peak = M_source + T_source + M_plan_draft + T_plan + G
             + C_old_prepare + O_prepare

finalize_peak = M_source + T_source + M_plan_final + T_plan + J
                + C_old_prepare + O_prepare

store_peak = M_plan_final + T_plan + J + C_old_prepare + O_prepare
```

`M_plan_draft` or `M_plan_final` includes only owned bytes that coexist with the source. Moved
fields are charged once; cloned fields are charged twice. The prepare admission requires every
peak to fit the existing 512 MiB logical budget. It separately requires the text-specific
`T_plan + J` envelope to fit `128 MiB`, subject to measured overhead and source overlap.

The source map may be released before `store_peak`. If it remains live for recovery or replay,
its charge remains in that peak. The current `Project::prepare_export` and `plan::compile` shape
can keep snapshot and plan structures alive together, so a final-plan-only estimate is invalid.

Preparation order is therefore:

1. Validate scalar types, exact string caps, source hashes, per-item limits, and aggregate counts.
2. Compute checked source, old-media, typed-plan, gate, JSON, and overhead charges.
3. Reserve before cloning text, fonts, curves, or normalized arrays.
4. Build a private draft and normalize only after the combined key cap passes.
5. Enter the text gate one item at a time in stable order. Drop temporary native and copied data
   before releasing the gate.
6. Finalize the immutable typed plan and serialize exactly once into one checked JSON buffer.
7. Hash those exact bytes and give the same owned bytes to storage. Do not call a second serializer
   for the plan ID or SQLite body.
8. Release `SourceOwner`, draft-only buffers, and `JsonOwner` before execution unless a separately
   charged recovery operation requires them.

If storage internally requires a second application-owned JSON copy, this contract is not met.
The implementation must either make storage consume the canonical buffer or reserve the second
copy and re-evaluate the 128 MiB and 512 MiB peaks.

## Execute lifetime sweep

Execution starts from one validated typed Plan8 owner. The canonical JSON buffer is released
after deserialization and plan validation. `SourceOwner` and `DraftOwner` are absent.

Define:

- `M_plan`: the complete existing media portion of the immutable ExportPlan;
- `T_plan`: the typed Plan8 text portion;
- `R_active`: the exact sum of active text raster permits at the maximum overlap, capped at four
  only when the one-cache-per-track invariant is enforced;
- `G`: one maximum text gate permit;
- `A`: one padded alpha buffer already included in `G`; a second buffer is added explicitly;
- `P_media`: existing movie/PNG source, decoded raster, response, canvas, and writer reservations;
- `O_execute`: measured Rust-owned channels, containers, capacities, and error storage;
- `J_live`: zero by contract, or one separately reserved JSON buffer if execution retains it.

The execute check is:

```text
execute_peak = M_plan + T_plan + R_active + G + P_media + O_execute + J_live
```

This value must be checked before workers, media decode, or native text calls start. It must be
less than or equal to the existing 512 MiB logical picture budget. The four 32 MiB raster terms,
the 54.345703125 MiB gate, the canvas estimate, all old media plan payloads, and writer-side
charges are simultaneous categories when their lifetimes overlap.

The text gate checks cancellation before waiting, while waiting, after acquisition, around each
native call, before each copied run or row, before worker response, and before writer append.
Every cancellation, disconnected channel, failed comparison, and writer abort drops its raster
and gate permits before the worker joins.

## Existing media plan aggregation

The text budget is not a replacement for current media admission. The aggregate ledger must
include the complete old fields in both source and plan ownership where they coexist:

```text
Snapshot:
  name, settings, assets, canonical_audio, timelines

ExportPlan:
  timeline, settings, canonical_audio, profile, renderer,
  source_closure, video, audio, timeline_sample_frames,
  decode_evidence, image_decode_evidence, alpha_policy

Per-use payload:
  presentation_ordinals, source ranges, cadence, framing,
  placement, motion, masks, audio mappings, evidence vectors

Execution payload:
  movie and image sources, canvas, response buffers, writer,
  persistent media rasters, and all existing permits
```

`M_source`, `M_plan`, and `P_media` must be computed by a checked old-media accounting path.
The current source has unbounded vectors and several unbounded strings in this area. Until that
path reports a finite bound or actual length charge, Plan8 admission must fail closed. Adding text
must not assume that `ExportPlan` metadata, source closure, sample arrays, or `VideoUse` ordinals
are free.

## Smallest post-probe admission proof

After native feasibility, one standalone Rust-owned proof record is sufficient to review this
contract. It must contain these sections:

1. **Representation table.** For every new struct and owned array, record Rust type name,
   `size_of`, alignment, maximum capacity, element count, capacity bytes, string bytes, owner,
   and lifetime phase. Record `Vec` capacity, not only `len`.
2. **String table.** Recompute every field in the exact string table above. Reject missing,
   non-ASCII, invalid-UTF-8, or over-cap values before cloning.
3. **Prepare sweep.** Record `M_source`, `T_source`, `M_plan`, `T_plan`, `G`, `J`, old-media
   charges, and measured overhead for `shape_peak`, `finalize_peak`, and `store_peak`.
4. **Execute sweep.** Record the maximum active raster overlap, one gate permit, all old media
   and writer charges, and the absence of a live JSON buffer.
5. **Serialization identity.** Record one canonical JSON buffer ID, its byte count, SHA-256,
   plan ID, and storage handoff. The hash input and stored bytes must be the same bytes.
6. **Negative controls.** Exercise a second JSON buffer, one extra font copy, a second alpha
   buffer, an over-cap curve aggregate, a 2,049×2,047 padded mask, an oversized identity string,
   and an unbounded old-media field. Each control must fail before its unchecked allocation.

The proof must include the 256-source-font overlap and the four-raster overlap. It must distinguish
`len` from capacity and moved ownership from cloned ownership. If an implementation uses a new
representation, it adds a new row and recomputes the sweep. It cannot silently reuse the
provisional bytes-per-item terms as measured layout facts.

The proof covers Rust-owned logical admission only. It does not measure or authorize CoreText or
CoreGraphics opaque allocations, system allocator internals, process RSS, throughput, playback,
hearing, or creative acceptance.

## Current integration seams and open guards

The future implementation must route the contract through the existing central paths:

- `Project::prepare_export` owns source-to-plan preparation and must use the prepare sweep;
- `plan::compile` must keep a private draft and avoid uncharged snapshot-to-plan duplication;
- `ContentHash::document` must not allocate a second canonical JSON buffer;
- `curve::PropertyCurve` validation and motion/mask normalization must enforce the aggregate key
  cap before cloning;
- the central plan validator must reject text width/height motion and unsupported legacy fields;
- `composition::Budget` must receive the full execute sweep before workers or decode;
- `pixels::extent` and text raster admission must charge exact checked capacity;
- worker responses must share one `Arc<AdmittedTextRaster>` and release permits on all teardown
  paths.

The current Rust sources do not yet contain the Plan8 text types or this admission permit. The
contract is ready for a post-probe review, not for runtime reliance. The first implementation
must either meet these limits with measured ownership or return a bounded admission error and
revise the design. It must not claim the provisional envelope as a native memory guarantee.
