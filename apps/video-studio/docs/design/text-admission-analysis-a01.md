# Native text admission analysis A01

## Scope and status

This is a read-only arithmetic review of the selected text synthesis and Candidate A admission shape. It does not define a production memory guarantee.

Every representation bound below is **PROVISIONAL**. The current editor has no text, font-resource, Plan8, run-evidence, or text-raster Rust type. A native probe and the first implementation must measure actual Rust layouts, allocation capacities, serializer buffers, and object lifetimes before integration relies on these bounds.

The review uses the selected synthesis at SHA `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` and Candidate A at SHA `6851884d8a76ce5a44181eab1d5c7991f61b323754907b4aaeb4ef69c9c6198e`. The selected input case file remains `synthetic-text-cases-a02.json` at SHA `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`.

The arithmetic uses 1 MiB = 1,048,576 bytes. It uses the synthesis caps: 4,096 text items per timeline, 1 MiB total UTF-8, 524,288 total UTF-16 units, 4,096 total runs, 131,072 total glyphs, 65,536 combined authored and normalized motion/mask keys, 64 direct fonts, 128 tables per font, 64 MiB canonical JSON, 4,194,304 raster pixels, and four nonempty picture tracks.

## Current source anchors

The current Rust sources are media-only at this review point. Their exact files are:

| Source | Bytes | SHA-256 | Relevant fact |
|---|---:|---|---|
| `crates/editor/src/model.rs` | 26,087 | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` | Snapshot, imports, assets, timelines, `ContentHash`, `EntityId`, and current limits |
| `crates/editor/src/curve.rs` | 5,335 | `c5167b70d205ff422ab971fd1ec24b9085499d0f9fa0cfd4d4bb0efd2d2268c3` | `CurveKey`, `PropertyCurve`, `PlannedCurve`, key validation, and normalization |
| `crates/editor/src/identity.rs` | 9,715 | `bf9c70971eb15f58c0c231fcd72722f30cf785178c96abecab0db8cfe02dfab9` | `BuildIdentity` and executable, lock, backend, host, architecture, and UUID identity |
| `crates/editor/src/plan.rs` | 37,502 | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` | Current `VideoUse`, `ExportPlan`, snapshot-to-plan cloning, and JSON identity hashing |
| `crates/editor/src/motion.rs` | 13,477 | `f694d6d7a896a5b138a6389741f09e54643deed8b5717b23e7c1d7bf51461bf5` | Existing x/y/width/height/opacity curves and planned motion |
| `crates/editor/src/mask.rs` | 13,223 | `a1cd2c87e15f806239172a63d398e7d692a5f8ca696818ed9190afc2beb8acaf` | Existing axis-mask curve and Q16 normalization |
| `crates/editor/src/composition.rs` | 51,727 | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` | Four-track and 512 MiB logical budget, permits, and current picture admission |
| `crates/editor/src/pixels.rs` | 7,246 | `9f2c1d86971d28ccbb89bb4678d2ea44cb8358e9d85e46451da4b7c7a2a02216` | 128 MiB per owned BGRA extent and checked pixel sizing |
| `crates/editor/src/project.rs` | 25,370 | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` | `prepare_export` owns snapshot-to-plan and plan serialization lifetimes |

The exact relevant calls are `Project::prepare_export`, `plan::compile`, `ContentHash::document`, and the SQLite plan write.

The current model has `MAX_TIMELINE_FRAMES = 100000`, `Settings` width and height limits of 8192, `Snapshot` asset count limit 10,000, and `EntityId` length limit 128. `ContentHash` is a 64-character lowercase hexadecimal `String`. `BuildIdentity` contains two fixed-format hashes and five string or optional-string fields. The existing `PropertyCurve` validation limits keys only by clip length and ordering. Existing `PictureMotion` has five optional curves, including width and height; selected text must expose only x, y, and opacity. Existing `PictureMask` has one progress curve and an unbounded-by-count key vector subject to clip length.

The current `Budget` uses checked `AtomicU64` reservation against `MAX_ADMITTED_BYTES = 512 MiB`. It does not yet account for text typed data, canonical text JSON, font metadata, shaping evidence, or text rasters. The current `Pixels::extent` limit is 128 MiB per owned BGRA frame.

## Proposed retained Plan8 arithmetic

The following charge uses the requested generous representation envelope. Each term is a policy estimate, not a measured `size_of::<T>()` result.

| Component | Calculation | Bytes | MiB |
|---|---:|---:|---:|
| Item-owned fixed metadata | `4,096 items × 4,096` | 16,777,216 | 16 |
| Authored and planned UTF-8 payloads | `2 × 1 MiB` | 2,097,152 | 2 |
| Authored and planned UTF-16BE payloads | `2 × 524,288 units × 2` | 2,097,152 | 2 |
| Run structs and full matrices | `4,096 runs × 1,024` | 4,194,304 | 4 |
| Glyph, position, advance, and source-index arrays | `131,072 glyphs × 128` | 16,777,216 | 16 |
| Combined authored and planned motion/mask keys | `65,536 keys × 128` | 8,388,608 | 8 |
| Direct font metadata, tables, and measurement identity | `64 × (16,384 + 128 × 256)` | 3,145,728 | 3 |
| Canonical Plan8 JSON buffer | `64 MiB` | 67,108,864 | 64 |
| **Provisional final plan plus one JSON buffer** | **sum above** | **120,586,240** | **115** |

This sum is 13 MiB below the proposed 128 MiB retained Plan8 reservation. The font term includes one 16,384-byte metadata envelope per direct font and 256 bytes per table identity. It treats the 128-byte glyph envelope as covering glyph IDs, six position or matrix components, advances, source indices, and vector overhead. It treats the 1,024-byte run envelope as covering ranges, status, full text and font matrices, names, and vector overhead.

The arithmetic fits only under explicit assumptions. The item envelope must cover the authored and planned fixed fields as one pair. The key envelope must cover both authored and normalized key storage. The UTF-8 and UTF-16 terms must cover all retained copies that the policy permits. `Vec` capacities, `String` capacities, B-tree nodes, enum layout, allocator rounding, and top-level plan fields need measured or separately charged bounds.

## Font metadata and identity

Candidate A stores `StoredFontResource`, `FontFaceDescriptorV1`, sorted `SfntTableIdentity` values, a backend string, and `NativeProbeIdentity`. The selected synthesis caps external source strings at 4,096 UTF-8 bytes, roles at 1,024 bytes, PostScript observations at 128 ASCII bytes, and direct fonts at 64.

The 16,384-byte font metadata envelope must also cover the raw-byte hash, byte count, origin, backend, face descriptor, face hash, measurement schema, `BuildIdentity`, and all framework or producer identity strings. The 256-byte table envelope must cover each tag, length, table hash, vector capacity, and allocation overhead.

The current `BuildIdentity` type has no deserialization length checks for `native_backend`, `host_os`, `architecture`, or `executable_uuid`. Candidate `NativeFrameworkIdentityV1` also has no stated caps for bundle identifiers, bundle versions, or `short_version`. These fields are outside the stated arithmetic until explicit bounds or actual-length charging exist.

At preparation time, the current `plan::compile` shape consumes a `Snapshot` by value, clones timeline data, and builds a plan source closure. A future text compiler may hold authored `font_resources` and the planned `font_closure` at the same time. The 64-font term describes the final direct plan closure. It does not charge a simultaneous snapshot containing the full 256-font snapshot cap.

For reference, an additional full snapshot font table envelope would be `256 × (16,384 + 128 × 256) = 12,582,912 bytes` or 12 MiB. If this copy is live during Plan8 construction, the retained arithmetic changes from 115 MiB to 127 MiB before allocator and top-level overhead. A simultaneous second authored text-item envelope adds 16 MiB under the literal per-item interpretation and exceeds 128 MiB. The implementation must choose and document whether the 4,096-byte item and font terms already include both authored and planned copies.

## Curves, motion, masks, and current Rust behavior

The selected text motion has x, y, and opacity only. Each authored `CurveKey` contains a `u64` frame, a value, and an optional interpolation enum. Normalization clones key vectors into `PlannedCurve`; mask normalization separately clones and quantizes its progress keys. The existing `validate_keys` function allows up to `clip_frames` keys for each curve. The current timeline cap is 100,000 frames.

The synthesis cap of 65,536 combined authored and normalized text motion/mask keys must be checked before any clone or normalization. A plan-level total alone is insufficient if one property can first allocate up to the current 100,000-frame limit. The guard must count x, y, opacity, mask, authored, and planned keys together, with checked addition and cancellation checks.

The 8 MiB key term above uses `65,536 × 128`. It covers both the current `CurveKey` representation and the planned curve representation under the stated envelope. It does not cover an unbounded error string, JSON staging value, or a second independently owned curve tree.

The selected text raster uses fixed width and height, signed x/y placement, Q16 opacity, and the existing axis mask. Width and height curves must remain rejected. The existing motion type still accepts width and height, so the Plan8 central validator must reject those fields before cloning them into a text plan.

## Persistent raster and native alpha-mask charges

The selected policy charges the persistent premultiplied raster separately from the 128 MiB retained typed Plan8 payload. The planned `PremulBgra16` envelope is eight bytes per pixel.

The explicit raster cap is 4,194,304 pixels. One persistent text raster therefore charges:

```text
8 × 4,194,304 = 33,554,432 bytes = 32 MiB.
```

Up to four active text sources could retain four such rasters, for 134,217,728 bytes or 128 MiB. This is a separate category under the existing 512 MiB picture budget. It must not be silently folded into the 128 MiB shared typed payload.

The native alpha drawing buffer uses `align_up(width, 16) × height`, including padding. Under the declared width limit 8,192, height limit 2,048, and pixel limit 4,194,304, an exhaustive integer bound gives a maximum padded mask of 4,225,008 bytes, or about 4.03 MiB. The simple safe bound `4,194,304 + 15 × 2,048 = 4,225,024` is also valid. The current Candidate A temporary formula names `raster_pixels`; the implementation must charge padded stride, not just width times height, and must enforce the pixel cap before this calculation.

The policy forbids a second whole canonical alpha buffer. If a second buffer is ever needed, it must be reserved explicitly. One extra maximum mask adds about 4.03 MiB to the shaping gate.

## One shaping gate and maximum temporary charge

The selected design serializes CoreText and CoreGraphics work through one shaping gate. The temporary charge therefore applies once, even when four picture workers exist. Persistent text rasters and the shared immutable plan can remain live while the gate is occupied.

Candidate A's temporary formula is:

```text
3 × font_blob_bytes
+ utf8_bytes
+ 2 × utf16_units
+ 64 × glyph_count
+ padded_stride × height
```

At the stated maxima, with the corrected padded-mask bound, this is:

```text
3 × 16,777,216       = 50,331,648
+ 8,192              =      8,192
+ 2 × 4,096          =      8,192
+ 64 × 16,384        =  1,048,576
+ 4,225,008          =  4,225,008
                         ---------
                          55,621,616 bytes = 53.0449 MiB
```

For a more conservative gate envelope, I replace 64 bytes per glyph with the requested 128-byte glyph envelope and add one maximum item's fixed metadata, 256 run envelopes, and one font's metadata and table records:

```text
55,621,616
+ (4,096 + 256 × 1,024 + 16,384 + 128 × 256)
= 56,985,584 bytes = 54.3457 MiB.
```

This is still below 128 MiB. It excludes opaque CoreText and CoreGraphics allocations, allocator bookkeeping, and any second JSON or alpha buffer. The shaping gate must release fresh strings, UTF-16 storage, copied run evidence, font copies, alpha storage, native objects, and temporary table data before releasing its permit.

## Combined picture-budget stress case

The retained Plan8 arithmetic, four maximum persistent text rasters, the conservative shaping gate, and the current maximum RGB canvas charge produce this text-only stress sum:

```text
120,586,240       retained plan plus one JSON buffer
+ 4 × 33,554,432  four persistent text rasters
+ 56,985,584      one conservative shaping gate
+ 201,326,592     8,192 × 8,192 × 3 current canvas estimate
= 526,716,928 bytes = 502.3164 MiB
```

This leaves about 9.68 MiB below the existing 512 MiB logical picture limit. Existing movie or PNG source charges, writer reservations, a second JSON buffer, a second alpha mask, duplicated snapshot structures, or uncharged allocator overhead can exceed that margin. The current `Budget` only sees reservations made by the implementation; it cannot protect uncharged typed or serialized objects.

The calculation is therefore a feasibility envelope, not proof that all maxima can run together. Preflight must reserve shared text data, each active text raster, the maximum shaping gate, canvas, existing media payloads, and writer-side charges in one checked temporal sweep.

## JSON coexistence and ownership hazards

The current `ContentHash::document` serializes any value into a fresh `Vec<u8>` before hashing. `Project::prepare_export` then serializes the prepared plan again for the SQLite body. A future Plan8 path can therefore hold typed data, one hash buffer, and one database body unless it deliberately reuses one owned byte buffer.

The proposed 64 MiB JSON term accounts for one canonical buffer. A second simultaneously live 64 MiB JSON buffer would raise the retained arithmetic from 115 MiB to 179 MiB before rasters or shaping. This exceeds the proposed 128 MiB retained reservation. The implementation needs one-buffer hash-and-store ownership or a separate checked reservation for every coexisting serialization.

The current `compile(snapshot: Snapshot, ...)` path also builds a plan while the moved snapshot's owned maps and strings remain live. The text plan must reserve before cloning authored text, font metadata, and curve keys. A final-plan-only charge is insufficient for the prepare peak.

The `ExportPlan` itself duplicates existing timeline, settings, source closure, video uses, and evidence structures. The text arithmetic above covers text-specific fields and the stated JSON buffer. It does not cover arbitrary existing media plan structures, asset sample arrays, or copied source closures. Those remain under their existing admission rules and must be added to the same peak sweep.

## Missing guards and findings

**P1 — the 128 MiB representation bound cannot yet be relied on during preparation.** The current Rust model has no text representation or text admission permit. Snapshot-to-plan cloning, serializer buffers, `Vec` capacities, `String` capacities, B-tree nodes, and framework identity strings have no measured lifetime bound. The final arithmetic leaves only 13 MiB, and a literal authored-plus-planned item or snapshot font copy exceeds the reservation. Add a preallocation envelope that states which copies the 4,096-byte item and 16,384-byte font terms include, then verify that envelope after the probe and first implementation.

**P1 — JSON duplication is an unsafe uncharged aggregation.** The current identity helper allocates a serializer buffer, and preparation serializes the plan again for storage. One additional 64 MiB buffer alone defeats the 128 MiB retained reservation. Hash and store the same owned bytes, or charge each simultaneous buffer before serialization.

**P2 — the temporary formula must charge padded stride.** `raster_pixels` is not sufficient when the closed policy charges `stride × height`. The corrected maximum is 4,225,008 bytes under the declared pixel cap. A second canonical alpha buffer requires another explicit charge.

**P2 — curve guards must precede cloning.** Current `validate_keys` permits up to the full clip length, and normalization clones each property. Enforce the 65,536 combined authored-plus-planned text motion/mask key cap before normalization and count all properties.

**P2 — several serialized identity strings lack explicit bounds.** Add limits or actual-length charges for `StoredFontResource.backend`, `BuildIdentity.native_backend`, `host_os`, `architecture`, `executable_uuid`, and `NativeFrameworkIdentityV1` bundle and version fields. The existing `EntityId` limit is 128 bytes, but `Snapshot.name`, `Settings.working_color`, and other existing strings are not all bounded by the current model.

**P2 — the existing plan payload is outside this text-only sum.** The current `ExportPlan` retains timeline, source closure, media sample arrays, presentation ordinals, decode evidence, and image evidence. Text admission must compose with that payload rather than assume the 128 MiB text reservation covers it.

## Acceptance boundary

The arithmetic supports a provisional 128 MiB typed Plan8 envelope when one JSON buffer, one plan font closure, and the stated combined per-item envelopes are charged exactly once. The existing 512 MiB logical picture policy can contain the provisional text-only stress case with a narrow margin.

This review does not establish actual Rust allocation sizes, CoreText memory, CoreGraphics memory, allocator behavior, serialization-copy behavior, native object lifetime, or throughput. The probe must measure those values before text integration. No runtime, product, frozen state, native output, GPU, or Resolve claim is made.
