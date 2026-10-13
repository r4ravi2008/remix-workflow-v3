# Existing-media admission next design A04

## Status and decision

This is a design-only successor to A03.
It changes no product source, state, fixture, executable, helper, or media.

A03 remains normative except where this document replaces its old-media charge terms and peak equations.
The four A03 repairs remain unchanged:

- the explicit Plan8 caller route is selected before any body read;
- SQLite reads revision text through bounded BLOB byte chunks;
- source validation retains no draft while revision and parser owners live;
- every positive B-tree high-water permit survives until its container drops.

A04 closes the remaining implementation-readiness gap.
It defines every application-owned old-media header, container, nested string, transient, channel, and bounded error owner.

Plan8 remains disabled until the implementation derives these charges and passes the declared controls.

This policy measures logical requested Rust payload.
It does not claim allocator metadata, physical pages, RSS, thread stacks, SQLite page-cache memory, or native-framework memory.

## Bound inputs

| Input | SHA-256 |
| --- | --- |
| A03 design | `ff76cab393b1c92468243622e817523b9c4d7f3fd47eef373e6708892b67509b` |
| A03 independent review | `4cd1333ee1ddea5ad8190187ace626f09cb79dd32cf429c3ca7d659041cafbd5` |
| Text admission contract A03 | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |

The nine current product sources were rehashed for this design:

| Source | SHA-256 | A04 use |
| --- | --- | --- |
| [`model.rs`](../../crates/editor/src/model.rs) | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` | Snapshot, asset, descriptor, origin, audio, timeline, track, and clip owners. |
| [`plan.rs`](../../crates/editor/src/plan.rs) | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` | ExportPlan, use, evidence, compile, and plan-validation owners. |
| [`project.rs`](../../crates/editor/src/project.rs) | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` | Revision reading, preparation, and storage lifetimes. |
| [`composition.rs`](../../crates/editor/src/composition.rs) | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` | Existing temporal picture admission and raster metadata. |
| [`media.rs`](../../crates/editor/src/media.rs) | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` | Probe evidence and callback-confined track operation. |
| [`layers.rs`](../../crates/editor/src/layers.rs) | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` | Four track workers, request-response barriers, and raster ownership. |
| [`movie.rs`](../../crates/editor/src/movie.rs) | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` | Plan clone removal, output channel, writer, and native-profile validation. |
| [`pcm.rs`](../../crates/editor/src/pcm.rs) | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` | Capacity-two PCM channel and 4,096-frame chunks. |
| [`exports.rs`](../../crates/editor/src/exports.rs) | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` | Replay, verification, recovery, fencing, and error lifetimes. |

The current source is grounding only.
No current runtime implements this Plan8 accounting path.

## Closed Plan8 count domain

A03's limits remain in force.
A04 names the old-media subcounts needed by the owner formulas:

```text
A   = Snapshot assets                                      <= 10,000
L   = Snapshot timelines                                   <= 10,000
VT  = video tracks across all timelines
AT  = audio tracks across all timelines
VC  = video clips across all timelines
AC  = audio clips across all timelines
I   = VT + AT + VC + AC                                    <= 400,006
E   = Origin source edges                                  <= 400,000
MS  = persisted movie SampleTiming records                 <= 400,000
W   = image plus movie warning records                     <= 640,000
CL  = measured descriptor channel-label records            <= 80,000
CO  = canonical AudioBinding.channel_order records         <= 8
K   = authored plus prospective normalized curve keys      <= 65,536
U   = source-closure assets                                 <= 10,000
VU  = selected VideoUse records                            <= 400,000
AU  = selected AudioUse records                            = 1
DE  = SourceDecodeEvidence records                         <= U
IE  = ImageDecodeEvidence records                          <= U
```

Every local vector also keeps A03's local cap.
For example, one track has at most 100,000 clips.
The token gate counts every unselected asset and timeline.

Every `MediaDescriptor::Audio.channels` value must be within `1..=8` on the Plan8 route.
The selected canonical source and output settings must each be exactly stereo.

`measured_channel_labels` and `AudioBinding.channel_order` are separate domains.
They never share a count or allocation charge.

When measured labels are present, their count must equal that descriptor's `channels` value.
The canonical `channel_order` count must equal the referenced audio descriptor's `channels` value.
The selected canonical order therefore contains exactly two labels.

One measured label and one canonical-order label each remain limited to 128 UTF-8 bytes.
`channel_order_basis` remains limited to 4,096 UTF-8 bytes.
A04 does not infer that measured-label bytes equal canonical-order bytes.

Individual maxima need not fit together.
The checked 512 MiB aggregate rejects combinations that exceed the full peak.

## Charge primitives

The implementation binds the pinned target and evaluates these expressions with checked arithmetic:

```text
H<T>                     = size_of::<T>()
string_policy(0)         = 0
string_policy(b > 0)     = max(8, 2 * b)
vec_policy<T>(0)         = 0
vec_policy<T>(n > 0)     = max(8, 2 * n) * H<T>
map_policy<K,V>(h > 0)   = 16 * h * H<(K,V)>
set_policy<K>(h > 0)     = 16 * h * H<K>
```

`map_policy` and `set_policy` are A03's pinned Rust 1.94.0 logical node envelopes.
Their positive high-water permits release only after the container drops.
Clearing a container or moving its last element does not release its node permit.

The charge walker follows these rules:

1. The root charge contains `H<Snapshot>` or `H<ExportPlan>`.
2. A vector policy contains every inline element header and its spare capacity.
3. A map policy contains every inline key, value, and node envelope.
4. A containing inline header includes its enum, `Option`, `Vec`, `String`, and map handles.
5. Nested heap storage receives a separate charge.
6. Every `ContentHash` and `EntityId` receives its own nested string charge.
7. A moved nested allocation keeps one charge under its new owner.
8. A clone retains both source and destination charges until one owner drops.

The token gate knows each decoded string byte count and local sequence length.
It computes provisional charges before typed construction.

The bounded visitor uses `try_reserve_exact`.
It immediately verifies actual capacity against the provisional policy.
The pinned-toolchain control must prove each observed capacity fits that policy before Plan8 can ship.

After construction, the ledger records actual `String::capacity` and `Vec::capacity * H<T>`.
The provisional family permit remains large enough to cover that actual charge.

Allocator-internal metadata is outside this policy.
Application-owned permit records, error buffers, channel slots, and control blocks are inside it.

## Exhaustive Snapshot old-media owner

Define `M_source_old` as the recursive sum below.
It excludes only accepted Plan8 text and font fields charged by `T_source`.

| Field family | Bound | Charge and nested ownership |
| --- | --- | --- |
| Snapshot root | one | `H<Snapshot>`; includes scalar and container handles. |
| Snapshot name and settings | one each | `string_policy(name bytes)` and `string_policy(working_color bytes)`. |
| Project and parent identity | one each | Nested `EntityId` or `ContentHash` string capacity. |
| Asset map | high-water `A` | `map_policy<ContentHash, StoredAsset>(A)` plus every key's hash string. |
| StoredAsset identity | `A` | Each value's `hash` string, `backend` string, and fixed inline fields. |
| Imported Origin | at most `A` | `external_source` and `role` string capacities. |
| Extracted Origin | at most `A` | Inline `SourceRange`; nested source-asset and recipe hash strings. |
| Derived or Generated Origin | aggregate `E` | Each local `vec_policy<SourceRange>`; source-asset strings; recipe, receipt, attempt, workflow, model, provider, and transfer identity strings. |
| Descriptor enum | one per asset | Inline enum storage already lies inside each `StoredAsset`. |
| Image descriptor | at most `A` | Format string, RGBA hash string, fixed dimensions and alpha record, optional alpha-hash string. |
| Movie descriptor | aggregate `MS` | Codec string; each local `vec_policy<SampleTiming>`; fixed timing, DTS, sync, and encoded-time fields. |
| Descriptor warnings | aggregate `W` | Each local `vec_policy<String>` plus each warning's string capacity. |
| Movie decode error | at most one per movie | Optional String header is inline; present detail receives its string capacity. |
| Audio descriptor | at most `A` | Codec string and fixed scalar fields. `channels` must be `1..=8`. |
| Measured channel labels | aggregate `CL` | Each local `vec_policy<String>` plus each label string. This is not `CO`. |
| Measurement identity | at most `A` | Inline `NativeProbeIdentity`; producer executable and lock hash strings; backend, host, architecture, and optional UUID strings. |
| Canonical AudioBinding | zero or one | Asset hash string, `vec_policy<String>(CO)`, every order-label string, and basis string. |
| Timeline map | high-water `L` | `map_policy<EntityId, Timeline>(L)` plus every map-key ID string. |
| Timeline identity | `L` | Each value's `Timeline.id` string and fixed frame count. |
| Video-track vectors | aggregate `VT` | Each timeline's `vec_policy<VideoTrack>` plus every track ID string. |
| Audio-track vectors | aggregate `AT` | Each timeline's `vec_policy<AudioTrack>` plus every track ID string. |
| Video-clip vectors | aggregate `VC` | Each track's `vec_policy<VideoClip>` plus every clip ID and asset-hash string. |
| Audio-clip vectors | aggregate `AC` | Each track's `vec_policy<AudioClip>` plus every clip ID and asset-hash string. |
| Fixed clip fields | `VC + AC` | Spans, cadence, rates, gain, pan, framing, placement, and option headers are inline in clip elements. |
| Authored motion curves | under `K` | One `vec_policy<CurveKey<T>>` for every present property curve. |
| Authored mask curves | under `K` | One `vec_policy<CurveKey<MaskProgress>>` for every present mask curve. |

The charge walker must visit every enum variant.
An added field or variant fails the Plan8 source gate until this inventory and its field tag are updated.

`Origin::sources()` is forbidden on this path because it allocates an uncharged vector.
The Plan8 validator uses borrowed slices and one inline extracted-source case.

## Exhaustive draft and ExportPlan old-media owner

Define `M_draft_old` and `M_plan_old` from the following families.
`T_draft` and `T_plan` remain the accepted text terms.

| Field family | Bound | Ownership rule |
| --- | --- | --- |
| Draft or plan root | one | Charge its concrete root `H<T>` once. |
| Project and revision | one each | Charge each nested ID or hash string. |
| Selected timeline | one | Move the complete recursively charged timeline from source to draft, then plan. |
| Settings | one | Move the working-color string and fixed fields. |
| Canonical AudioBinding | one | Move its hash, order vector, labels, and basis string. |
| Profile and alpha policy | one each | Fixed inline fields; no nested heap owner. |
| Renderer BuildIdentity | one | Charge two hash strings, backend, host, architecture, and optional UUID. |
| Source-closure map | high-water `U` | Charge destination map nodes before partitioning. Move map keys and `StoredAsset` values with `remove_entry`; do not clone nested asset owners. |
| Video vector | `VU` | `vec_policy<VideoUse>(VU)` plus all nested fields below. |
| Video-use identities | `VU` | Clip, track, and asset strings are clones while the retained timeline contains its originals. Charge both. |
| Presentation ordinals | aggregate `<=400,000` | One local `vec_policy<u64>` per VideoUse. |
| Video-use static picture fields | `VU` | Framing and placement are inline clones and are covered by the VideoUse buffer. |
| Planned motion | under `K` | Charge every keyed `PlannedCurve` vector. Constant variants have no heap allocation. |
| Planned mask | under `K` | Charge every keyed mask curve vector. Constant variants have no heap allocation. |
| Audio vector | `AU = 1` | `vec_policy<AudioUse>(1)`. |
| Audio-use identity | one | Track, clip ID, and asset strings clone timeline values. Charge source and destination. |
| Decode evidence | `DE <= U` | `vec_policy<SourceDecodeEvidence>` plus asset and decoder-hash strings. |
| Image evidence | `IE <= U` | `vec_policy<ImageDecodeEvidence>` plus asset, RGBA, decoder, and optional alpha hash strings. |
| Text payload | accepted A03 domain | Charged only by `T_draft` or `T_plan`; never by this old-media table. |

The selected timeline remains present inside the final plan.
`VideoUse` and `AudioUse` therefore duplicate their stated identity fields.
Those copies are not treated as moves.

The Plan8 compiler consumes the Snapshot owner.
It moves settings, canonical audio, the selected timeline, and used asset entries exactly once.

Source and destination B-tree node permits overlap during partitioning.
The source-map high-water permit cannot shrink while its emptied root remains allocated.
The destination permit is acquired before the first insertion.

If `remove_entry` cannot move a key and value in the chosen representation, the implementation must charge the clone concurrently.
It cannot relabel a clone as a move.

## Finite old-media preparation transients

`C_old_prepare(phase)` is no longer an unnamed remainder.
It selects one of these closed components:

| Component | Maximum domain | Required representation and charge |
| --- | --- | --- |
| `C_old_validate` lineage seen set | `A` | `set_policy<&ContentHash>(A)`; borrowed keys, no hash-string clones. |
| `C_old_validate` lineage active set | `A` | `set_policy<&ContentHash>(A)`; borrowed keys. |
| `C_old_validate` lineage stack | `A` | `vec_policy<&ContentHash>(A)`. |
| Timeline ID set | one timeline, `<=400,006` | `set_policy<&EntityId>(local IDs)`; borrowed IDs. |
| Overlap ranges | one track, `<=100,000` | `vec_policy<&Span>(local clips)`. |
| Unselected normalization scratch | one clip, under `K` | Concrete keyed-vector policies for that clip; drop before the next clip. |
| Selected prospective-key scratch | one clip | Fixed counters only; no retained normalized vector. |
| Frame coverage | selected frame count `<=100,000` | A declared `vec_policy<u8>`; no implicit `Vec<bool>` layout assumption. |
| Used-assets set | `U` | `set_policy<&ContentHash>(U)`; borrowed source keys. |
| Closure queue | `U` | `vec_policy<&ContentHash>(U)`. |
| Source and destination map nodes | `A` and `U` high-waters | Both tree permits remain live through partitioning. Nested values remain singly owned when moved. |
| Draft collection buffers | `VU`, `AU`, `DE`, `IE` | Part of `M_draft_old`, not transient scratch. |
| Plan-validation asset set | `U` | `set_policy<&ContentHash>(U)`; borrowed plan keys. |
| Mapping/order counters | selected plan | Fixed counters and iterators only. No collected tuple vector. |

Only one timeline ID set, one track range vector, and one clip normalization scratch may be live together.
Their owners drop before the next local item.

No Plan8 validator clones a `ContentHash`, `EntityId`, timeline, source closure, or audio-use tuple.
Any implementation that needs a clone adds it to the applicable peak before allocation.

## Finite preparation and replay overhead

Define a closed `OldMediaChargeKind` enum.
It has one variant for every row in the source, plan, transient, string, vector, and tree tables.

The ledger stores one fixed charge record per enum variant.
It does not allocate one permit object per clip, sample, warning, or key.
Local sequence charges draw from their already reserved family total.

`O_prepare(phase)` contains only these application-owned owners:

- the fixed `OldMediaCharges` record array and ledger handle;
- one bounded `StudioError` owner with at most 4,096 detail bytes;
- fixed cancellation and route-control records;
- fixed iterators, counters, and hash state not already inside `W_parse`;
- application-owned allocation-control records measured by their concrete `size_of` values.

Preparation creates no worker channel.
`O_prepare` therefore has no channel term.

Its finite form is:

```text
O_prepare(phase)
  = H<OldMediaCharges>
  + H<AdmissionLedger>
  + H<RouteAndCancellationControl>
  + H<PhaseCountersAndHashState>
  + H<StudioError>
  + string_policy(4,096)
  + sum(H<application-owned fixed control record live in phase>)
```

`OldMediaChargeKind::COUNT` fixes the record-array length at compile time.
The implementation inventory names every item in the final sum.
An unnamed heap owner or variable-capacity control record fails the inventory gate.

An error formatter uses a capped writer.
If detail would exceed 4,096 bytes, it returns a fixed `error_detail_overflow` record.
It never allocates the unbounded detail and then checks its length.

`O_replay` uses the same fixed ledger and one bounded error owner.
It adds no source-validation owner because a replay has no Snapshot.

These overheads exclude allocator-internal metadata.
They include every application-owned allocation wrapper and retained error buffer.

## Replaced preparation peaks

Use these owner names:

```text
M_source_old          exhaustive Snapshot old-media owner
M_source_remnant_old  source fields not moved into the draft
M_draft_old           old-media fields owned by the private draft
M_plan_old            old-media fields owned by the final plan
C_old_validate        validation transients from the closed table
C_old_compile         compile and partition transients from the closed table
C_old_plan_validate   borrowed final-plan validation transients
```

The A03 text terms remain unchanged.

The checked preparation peaks are now:

```text
read_peak = J_revision + W_parse + O_prepare(read)

source_peak = J_revision + W_parse
            + M_source_old + T_source
            + C_old_validate + O_prepare(validate)

shape_peak = M_source_remnant_old + T_source_remnant
           + M_draft_old + T_draft
           + C_old_compile + G + O_prepare(compile)

plan_validate_peak = M_plan_old + T_plan
                   + C_old_plan_validate + O_prepare(plan_validate)

store_peak = M_plan_old + T_plan + J_plan + O_prepare(store)
```

Every peak must be at most `536,870,912` logical bytes.
`T_plan + J_plan` must also satisfy A03's 128 MiB text envelope.

`M_source_old` contains every unselected asset and timeline during source validation.
`M_source_remnant_old` retains their charges during consuming compilation until they drop.

Every recursive charge record carries an owner tag.
A move transfers that same record from `Source` to `Draft`; it does not copy or subtract bytes.
`M_source_remnant_old` is the exact sum of records still tagged `Source` after those transfers.
The full source-map node permit remains source-tagged until the map itself drops.

The selected timeline changes owner from source to draft at the move boundary.
It never appears in both terms.

Source-map and destination-map node permits do appear together.
Moved asset keys and values appear once.

Timeline-to-use identity clones appear twice.
The ledger records each clone before allocation.

`C_old_prepare` is phase-selected:

```text
C_old_prepare(validate)      = C_old_validate
C_old_prepare(compile)       = C_old_compile
C_old_prepare(plan_validate) = C_old_plan_validate
C_old_prepare(read/store)    = 0
```

This definition closes the contract term without hiding a residual byte count.

## Replaced replay peaks

A stored Plan8 replay uses the raw stored body as its only JSON owner:

```text
replay_read_peak = J_plan_read + W_parse + O_replay(read)

replay_validate_peak = J_plan_read
                     + M_plan_old + T_plan
                     + C_old_plan_validate
                     + O_replay(validate)
```

The token facts compute `M_plan_old` and `T_plan` before typed deserialization.
The same exhaustive plan walker verifies the constructed owner.

`J_plan_read`, `W_parse`, and replay validation scratch drop before worker creation.
Replay then transfers the single admitted plan owner into execution.

Plan8 verification, completed replay, recovery, and reconciliation must select the Plan8 table before this read.
They do not load a legacy plan String and then inspect its schema.

## Finite execution overhead

Plan8 uses one `Arc<AdmittedPlan8>` allocation.
`M_plan_old + T_plan` contains the plan root and all nested payload.
`O_execute` contains the Arc counters, padding, handles, channels, bounded errors, paths, and worker-control records.

The main writer, layer orchestrator, four track workers, and callback closures may hold Arc handles.
They never clone `ExportPlan` or a nested plan field.

The following Rust channels are the maximum Plan8 set:

| Channel | Count | Capacity | Bulk payload owner |
| --- | ---: | ---: | --- |
| Picture request | `<=4` | `1` | Fixed request value in `O_execute`. |
| Picture response | `<=4` | `1` | Fixed enum and box metadata in `O_execute`; raster bytes in `P_media`. |
| Compositor output | `1` | `1` | Fixed result/frame metadata in `O_execute`; canvas bytes in `P_media`. |
| PCM event | `1` | `2` | Fixed enum/vector headers in `O_execute`; sample capacity in `P_media`. |

For each channel type and capacity, a pinned-runtime control records the maximum application-requested control-block and slot storage.
The exact observed maximum becomes `channel_policy<T>(capacity)`.
The execution ledger reserves it before `sync_channel` construction.

The control is required because `size_of::<SyncSender<T>>()` does not describe channel storage.
The control does not claim allocator metadata or OS scheduler memory.

At most 32 bounded Rust error-detail slots may coexist across channel slots, workers, join paths, callbacks, and the caller.
Each slot reserves 4,096 bytes before formatting.
An added worker, channel, or terminal holder requires rederivation before Plan8 can run.

One shared immutable execution-path owner holds the blob root and staged output path.
Its actual `PathBuf` capacities are charged before worker creation.
Workers clone only its Arc handle.

`O_execute` also charges:

- one Arc control block and every live Arc handle;
- fixed worker, join-handle, signal, permit-handle, and deadline records;
- response boxes and fixed raster metadata;
- PCM vector headers and evidence records;
- Rust closure captures and application-owned callback state;
- bounded path buffers and bounded error buffers.

Its finite form is:

```text
O_execute
  = arc_control_overhead<AdmittedPlan8>
  + live_arc_handles * H<Arc<AdmittedPlan8>>
  + sum(channel_policy<T>(declared_capacity))
  + 32 * (H<StudioError> + string_policy(4,096))
  + charged ExecutionPaths capacities
  + sum(H<fixed worker, join, signal, permit, deadline, box, evidence, and closure record>)
```

The implementation inventory fixes each multiplicity before worker creation.
An unlisted callback capture or channel makes Plan8 admission unavailable.

Pixel, canvas, source-raster, cached PNG, encoded-writer, and PCM sample bytes remain in `P_media`.
Their headers remain in `O_execute`.
No byte may appear in both terms.

Native objects, framework queues, thread stacks, and codec-internal buffers remain outside this logical Rust policy.
The capability report must state that boundary.

The execution peak is:

```text
execute_peak = M_plan_old + T_plan
             + R_active + G + P_media
             + O_execute + J_live

J_live = 0
execute_peak <= 536,870,912
```

`R_active` retains A03's accepted text raster and active-source cache charge.
It does not contain old-media raster bytes already charged by `P_media`.

The plan permit releases only after every worker, callback, response, writer, and Arc handle releases ownership.
Cancellation and fencing follow the same lifetime.

## Required move and clone ledger

The implementation must emit a bounded owner transition record for these cases:

| Transition | Required multiplicity |
| --- | --- |
| Settings, canonical audio, selected timeline | Move once from source to draft, then plan. |
| Used source-closure key and StoredAsset | Move once into the destination map. |
| Source and destination map nodes | Two concurrent high-water permits during partition. |
| Timeline clip identity into VideoUse | Clone; both copies charged. |
| Timeline audio identity into AudioUse | Clone; both copies charged. |
| Authored curve to normalized planned curve | Source and destination charged while both live; source drops at the declared boundary. |
| Draft to final plan | Move once unless the implementation proves a field-specific clone charge. |
| Final plan to canonical JSON | Plan and `J_plan` coexist; both charged. |
| Final plan into execution | One Arc-owned plan; handles only. |

The ledger rejects an unlabeled copy.
It also rejects a move whose source remains usable after the declared boundary.

## Admission algorithm

The Plan8 implementation performs these steps:

1. Select the explicit Plan8 route and complete A03's row preflight.
2. Read and hash the bounded BLOB bytes through A03's exact chunk query.
3. Run the token gate without constructing `serde_json::Value`.
4. Count every source or plan field family in this document.
5. Reject every local or aggregate cap violation.
6. Compute all provisional root, string, vector, tree, transient, and overhead charges.
7. Compute every applicable phase peak with checked arithmetic.
8. Reject before typed allocation when any peak exceeds 512 MiB.
9. Reserve the source or plan family permits.
10. Deserialize through bounded visitors and verify actual capacities immediately.
11. Run source validation with no retained draft.
12. Drop revision, parser, and validation owners.
13. Consume the source into the draft with recorded moves and clones.
14. Validate the final plan through borrowed views.
15. Serialize once into the one canonical Plan8 buffer.
16. Store those exact bytes and retain no second serialized plan.
17. Drop preparation owners before creating any worker.
18. Reserve execution channels, paths, errors, plan control block, and `P_media` before worker start.

Failure at any step drops every acquired permit.
No worker or native object exists before step 18.

## Required controls

### 1. Exhaustive field-family control

Bind the nine source hashes and the concrete target layout.
Require one inventory row for every Snapshot and ExportPlan field and enum variant.

Add, remove, or rename one field in an isolated source copy.
The owner-inventory gate must fail until the charge mapper changes.

### 2. Old-audio controls

Exercise audio descriptors with channels zero, one, eight, and nine.
Exercise measured-label and canonical-order counts zero through nine.

Require independent `CL` and `CO` totals.
Mutating one total must not change the other.

Require exact stereo only for the selected canonical source and output.

### 3. Nested owner controls

Exercise maximum local movie samples, warnings, decode error, Origin inputs, timelines, tracks, clips, IDs, and BuildIdentity strings.
Exercise one-over and aggregate-over cases.

Require rejection before the affected typed allocation.

### 4. Move, clone, and tree controls

Record the declared transitions above.
Inject one extra asset clone, timeline clone, plan clone, or serializer.
Each mutation must exceed its expected multiplicity or peak.

Run A03's full insertion and deletion domains.
Require positive node permits through retained empty roots and release only after container drop.

### 5. Validation and compile controls

Measure each borrowed set, stack, range vector, coverage buffer, queue, and normalization scratch independently.
Require their actual capacities to fit the declared policies.

Retain two local timeline sets or two clip scratch owners in a mutation.
The peak must reflect both owners.

### 6. Replay controls

Load one bounded Plan8 body through the Plan8 table.
Bind raw bytes, plan ID, route, token facts, recursive plan charge, and final constructed capacities.

Retain `J_plan_read` into execution in a mutation.
The execution gate must reject nonzero `J_live`.

### 7. Channel and error controls

Bind the pinned runtime and every channel type/capacity.
Record requested control-block, slot, box, path, Arc, and error-buffer charges.

Exercise full queues, disconnect, cancellation, callback failure, worker panic classification, and fencing.
Require zero ledger ownership only after all joins and drops complete.

### 8. Compatibility and product proof

Read back the preserved Plan2 through Plan7 fixtures byte-for-byte.
Their requests, plans, receipts, serializers, and worker behavior remain unchanged.

Then run A03's bounded Plan8 synthetic-offset and canonical 24-bit audio fixtures.
Those output proofs remain separate from this design.

## Compatibility

This design does not modify `ExportRequest` or any public legacy Rust struct literal.
It does not modify Snapshot schema1, Plan2 through Plan7, or historical receipt bytes.

The additive `prepare_plan8_export` and `export_plan8` methods remain the only Plan8 entry points.
The private Plan8 table and route marker remain A03's persistence choice.

The accepted text limits, font-map policies, text gate, Plan8 schema, and one canonical plan buffer remain unchanged.

## Scope and remaining gates

A04 is an implementation-ready logical ownership contract.
It is not an implementation or a passing measurement.

Root review and independent peer review remain required before product work.
The implementation must then derive the concrete target sizes and channel charges.
It must pass every source, capacity, route, lifetime, compatibility, cancellation, and bounded-output control.

This design does not establish physical-memory admission, native text feasibility, throughput, playback, hearing, creative approval, full-editor acceptance, or full-film completion.
