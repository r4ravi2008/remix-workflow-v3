# Existing-media admission next design A03

## Status and decision

This is a design-only successor to A02. It changes no product source, state, fixture, executable, or media.

It repairs the two A02 ownership findings and the two route/read-boundary findings.

Plan8 must use an explicit caller route before any plan replay or revision-body read.

The selected route adds `prepare_plan8_export(ExportRequest)` and `export_plan8(ExportRequest)`.
Both methods call the existing private lifecycle with `Route::Plan8TextV1`.

The existing `ExportRequest`, `prepare_export`, and `export` APIs remain unchanged for Plan2–7.
All existing Rust struct literals therefore remain valid.

Plan8 remains disabled until every gate in this document passes.

A03 makes four narrow decisions:

- every positive B-tree high-water permit survives until the container drops;
- source validation retains no draft while revision and parser owners remain live;
- the explicit public method remains the only pre-body revision route authority;
- SQLite revision chunks use BLOB byte offsets through one fixed query.

## Bound inputs

| Input | SHA-256 |
| --- | --- |
| A02 proposal | `d95582f634c4f22e374cd02c029e823295a8a0d36ba2e36c0edac9094648d9a4` |
| A02 parent findings | `6ecd4193283bb5635f2880e06b771502dd539b0b7ce1af986674ae78beefe617` |
| A02 independent review | `c2ca5ef489c6f3178b2942e73a2691f1ac59537a3042b79d72b680749d212d07` |
| A01 proposal | `d128ec8cb5114d98ef9a68fb1f5a27d174ff653445cd7819e690697234518a3e` |
| A01 independent review | `92ee1eea467968115b1997baadd9e31881cc6d7e7a4f7ecd5d7eee813f4b00f1` |
| Selected text synthesis | `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` |
| Text admission contract A03 | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |
| Payload A03 root readback | `c7b2c6be9538d703f62ecc0f1cdb29290013906a546050b838c263683e73a2fc` |
| Payload A03 measurement report | `124102dcb3f4c76d97d3f4faa30678c8788df118a8210f64a562f5b63952e3ca` |
| Payload A03 runner report | `83f6196e6e69194d6c69c4509ba50e157226f707ffbd4f00797a5c9ee08f89bf` |
| Payload A03 wrapper report | `c02245a4df8a440094bc8a5c05bcc473586ffea4ac5d555f11f14d45e6080aa6` |

The installed Rust 1.94.0 source HTML is also bound:

| Installed source | SHA-256 |
| --- | --- |
| `alloc/collections/btree/map/entry.rs.html` | `3d898b3ea7a49425706e50f01c8402c75a7459da0e79509f0ce151d456c5a781` |
| `alloc/collections/btree/remove.rs.html` | `3c482866c94fd1c9e0dc1bcd21e14bfb8aca8946d1a8e304b8e6d1e753dd7962` |

These files identify Rust `1.94.0 (4a4ef493e 2026-03-02)`.
They show retained empty leaf-root storage after final removal.
This is source inspection, not an allocation measurement.

The Payload A03 result measured 2,378 capacity rows and 28 B-tree rows.
It measured only through 10,000 tree entries.
It did not establish product admission, physical memory, native execution, or audiovisual acceptance.

The current source groundings are unchanged from A01:

| Source | SHA-256 | Relevant current behavior |
| --- | --- | --- |
| [`model.rs`](../../crates/editor/src/model.rs) | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` | Snapshot validation allocates lineage, ID, range, and normalization scratch. |
| [`plan.rs`](../../crates/editor/src/plan.rs) | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` | Compile clones the timeline and source closure, then creates coverage and ordinal collections. |
| [`project.rs`](../../crates/editor/src/project.rs) | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` | Prepare replays before loading a full revision `String`. It serializes the plan twice. |
| [`composition.rs`](../../crates/editor/src/composition.rs) | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` | Current temporal admission covers picture payloads but not retained plan ownership. |
| [`media.rs`](../../crates/editor/src/media.rs) | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` | Import probing limits newly measured movie samples, but replay needs its own bound. |
| [`layers.rs`](../../crates/editor/src/layers.rs) | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` | Track workers and compositor define the existing request-response payload lifetime. |
| [`movie.rs`](../../crates/editor/src/movie.rs) | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` | Profile validation occurs after preparation. The decoder worker clones the plan. |
| [`pcm.rs`](../../crates/editor/src/pcm.rs) | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` | The selected audio path streams bounded 4,096-frame chunks. |
| [`exports.rs`](../../crates/editor/src/exports.rs) | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` | Verify and stage recovery load legacy plan bodies before routing by schema. |

These product paths are visible at [`plan.rs:12`](../../crates/editor/src/plan.rs#L12),
[`project.rs:248`](../../crates/editor/src/project.rs#L248),
[`project.rs:285`](../../crates/editor/src/project.rs#L285),
[`model.rs:483`](../../crates/editor/src/model.rs#L483),
[`plan.rs:138`](../../crates/editor/src/plan.rs#L138),
[`plan.rs:566`](../../crates/editor/src/plan.rs#L566),
[`movie.rs:66`](../../crates/editor/src/movie.rs#L66),
[`movie.rs:163`](../../crates/editor/src/movie.rs#L163), and
[`exports.rs:928`](../../crates/editor/src/exports.rs#L928).

This design does not treat test-only frame-observer maps as product owners.

## Entry-route comparison

### Rejected: optional field on `ExportRequest`

An optional `mode` with `skip_serializing_if = "Option::is_none"` would preserve old request bytes.
It would still break every existing Rust struct literal that does not name the new field.

It would also make the mode part of a public serialized request type.
Older binaries deny unknown fields and would reject that new document.

### Selected: additive Plan8 methods

Keep the four-field `ExportRequest` exactly as it is.
Add these methods:

```rust,ignore
pub fn prepare_plan8_export(&self, request: ExportRequest) -> Result<PreparedExport>;
pub fn export_plan8(&self, request: ExportRequest) -> Result<ExportResult>;
```

Both public method pairs call one private implementation:

```rust,ignore
enum Route {
    Legacy,
    Plan8TextV1,
}

fn prepare_export_internal(&self, route: Route, request: ExportRequest) -> Result<InternalPrepared>;
fn export_internal(&self, route: Route, request: ExportRequest) -> Result<ExportResult>;
```

The route is selected at the public call boundary.
It is selected before opening either plan table or reading a revision body.

Legacy request hashing remains `ContentHash::document(&request)`.
Plan8 hashes a private, fixed-order identity containing `kind="plan8_text_v1"` and the unchanged request.
The Plan8 identity is domain-separated from every legacy request hash.

Calling a legacy method and a Plan8 method with the same intent produces an intent conflict.
No operation infers a route from `MovieProfile`, Snapshot fields, plan schema, or body bytes.

The first unit adds no revision feature marker.
The public method is the only pre-body route authority.
A legacy call therefore keeps its current parser and error behavior.
It does not promise a pre-body `plan8_route_required` error for a text-bearing revision.

This changes one statement in the selected synthesis.
The Plan8 usage example must call the two additive Plan8 methods.
`verify_export`, `cancel_export`, and reconciliation keep their existing public operations.
The caller still performs the same number of workflow steps.

## Persistent routing

Plan8 bodies must not enter the legacy `plans` table.
Add a private `plan8_plans` table with these fields:

```text
project, intent, request_hash, hash, kind, body BLOB
PRIMARY KEY(project, intent)
CHECK(kind = 'plan8_text_v1')
```

Add a nullable `plan_kind` column to `exports`.
Historical rows remain `NULL`; new Plan8 rows store `plan8_text_v1`.

One new common route precheck checks both plan tables inside one immediate transaction.
An intent present in the other table is a conflict.
The transaction prevents two routes from claiming one intent concurrently.

Plan8 verification reads `exports.plan_kind` before it reads a plan body.
Plan8 recovery and stage reconciliation use the same route-first lookup.
Publication completion checks the route-specific immutable plan row.

Unknown, missing, or conflicting route metadata fails closed.
Stage reconciliation retains an owned stage when its route cannot be proved.

After that common precheck, legacy body queries, body types, and serializers remain unchanged.
There is no cross-route fallback.

## Plan8 count domain

The token gate enforces these counts before typed deserialization.
All additions use checked arithmetic.

Define:

```text
A  = Snapshot assets
L  = Snapshot timelines
I  = all video-track, audio-track, video-clip, and audio-clip IDs
E  = all Origin source edges
MS = all persisted movie SampleTiming records
W  = all descriptor warning records
CL = all measured audio channel-label records
K  = authored keys plus prospective normalized motion, mask, and text keys
```

| Quantity | Plan8 limit |
| --- | ---: |
| Revision or plan JSON bytes | `1..=67,108,864` |
| JSON nesting depth | `<=32` |
| `A` | `<=10,000` |
| `L` | `<=10,000` |
| Origin inputs for one asset | `<=10,000` |
| `E` | `<=400,000` |
| Movie samples for one descriptor | `<=100,000` |
| `MS` | `<=400,000` |
| Warnings for one descriptor | `<=64` |
| `W` | `<=64 * A`, therefore `<=640,000` |
| Channel labels for one audio descriptor | `<=8` |
| `CL` | `<=8 * A`, therefore `<=80,000` |
| Clips in one track | `<=100,000` |
| IDs in one timeline | `<=400,006` |
| `I` across all timelines | `<=400,006` |
| `K` | `<=65,536` |

Every timeline, including every unselected timeline, contributes to `I` and `K`.
Every asset contributes to `E`, `MS`, `W`, and `CL`.
No unselected value receives a free authoring-state exemption.

The selected timeline has tighter rules:

| Selected quantity | Plan8 rule |
| --- | --- |
| Frame count | `1..=100,000` |
| Picture tracks | `1..=4`; every track is nonempty |
| Picture clips | `<=4 * frame_count`, therefore `<=400,000` |
| Presentation ordinals | one per output frame per picture track; `<=400,000` |
| Audio tracks | exactly one |
| Audio clips | exactly one |
| Track and clip IDs | `<=400,006` |
| Source closure assets | `<=10,000` |
| `VideoUse` records | equal selected picture clips; `<=400,000` |
| `AudioUse` records | exactly one |
| Movie plus image evidence records | `<=10,000` and one-to-one with directly used assets |

The `400,006` ID bound is exact for four tracks with 100,000 one-frame clips each.
It also includes one audio track and one audio clip.

Individual maxima need not fit together.
The JSON limit and 512 MiB aggregate reject oversized combinations.

## String and vector bounds

The token gate measures decoded string bytes, not encoded escape bytes.
It enforces these existing-media per-value limits:

| Field | Maximum bytes |
| --- | ---: |
| `Snapshot.name` | `4,096` UTF-8 |
| `Settings.working_color` | `128` UTF-8 |
| Imported `external_source` | `4,096` UTF-8 |
| Imported `role` | `1,024` UTF-8 |
| `StoredAsset.backend` | `128` UTF-8 |
| Image format or movie/audio codec | `128` UTF-8 |
| One decode error or warning | `4,096` UTF-8 |
| One channel label | `128` UTF-8 |
| `channel_order_basis` | `4,096` UTF-8 |
| `BuildIdentity.native_backend` | `128` UTF-8 |
| `BuildIdentity.host_os` | `64` ASCII |
| `BuildIdentity.architecture` | `32` ASCII |
| `BuildIdentity.executable_uuid` | `64` ASCII when present |
| `EntityId` | existing `128` ASCII |
| `ContentHash` | exactly `64` lowercase hexadecimal bytes |

The A03 text-specific string, font, run, glyph, and raster limits remain unchanged.

For every `Vec<T>` with admitted length `n`, reserve this logical policy before construction:

```text
vec_policy<T>(0) = 0
vec_policy<T>(n) = checked(max(8, 2 * n) * size_of::<T>())
```

For every nonempty decoded string of `b` bytes, reserve `checked(max(8, 2 * b))` before its copy.
The bounded visitor uses `try_reserve_exact` and checks the resulting capacity against the policy.

The factor two is a pinned-toolchain logical envelope.
It is not an allocator or RSS guarantee.
An integration control must reject a toolchain whose reported capacities exceed it.

After construction, actual `capacity * element_size` replaces the provisional vector charge.
Actual `String::capacity` replaces the provisional string charge.

## Bounded SQLite read and parse

The Plan8 branch never calls legacy `inspect`, `verify_assets`, or `replay_plan`.

It loads a revision or Plan8 plan in this order:

1. Start one SQLite read transaction.
2. Read only row identity, `typeof(body)`, and `length(CAST(body AS BLOB))`.
3. Require TEXT for a revision and BLOB for a Plan8 plan.
4. Reject a missing, zero-length, wrong-type, or larger-than-64-MiB body.
5. Reserve the exact full-body permit and one 64-KiB chunk permit.
6. Read the same row through the fixed byte queries below.
7. Require the accumulated byte count to equal the first length.
8. Hash the exact bytes and compare their immutable revision or plan identity.
9. Run the bounded token gate without creating `serde_json::Value`.
10. Reserve the complete source or plan envelope from the token facts.
11. Deserialize through bounded seeds and visitors.
12. Repeat local counts while constructing each sequence.
13. Run typed semantic validation before releasing the input bytes.

The first-unit revision query is fixed to this byte form:

```sql
SELECT CAST(substr(CAST(body AS BLOB), ?1, ?2) AS BLOB)
FROM revisions
WHERE project = ?3 AND hash = ?4
```

The first-unit Plan8 plan query is fixed to this byte form:

```sql
SELECT CAST(substr(body, ?1, ?2) AS BLOB)
FROM plan8_plans
WHERE project = ?3 AND intent = ?4 AND hash = ?5 AND kind = 'plan8_text_v1'
```

Parameter `?1` is the checked one-based byte offset `1 + accumulated_bytes`.
Parameter `?2` is exactly `min(65,536, total_bytes - accumulated_bytes)`.
Every result must be a BLOB whose length equals `?2`.
The next offset derives only from the checked accumulated byte count.

Both queries run in the metadata transaction and retain the exact row identity.
The revision cast makes SQLite `substr` use BLOB byte offsets, not TEXT character offsets.
The query text, parameter values, result type, and result length enter the implementation proof.
The charged chunk must not become a second whole-body buffer.

The token gate rejects unknown fields, duplicate fields, invalid enums, oversized strings, and all count excesses.

The token gate retains fixed `WireFacts`, not one record per input sequence.
Each closed field family has three checked counters: total elements, nonempty sequence count, and maximum local length.
The 32-level path stack and fixed counter array do not grow with body size.

For one field family, the provisional vector charge is:

```text
sum(vec_policy<T>(local_length))
```

The token scanner computes that sum directly while it sees each closing sequence.
It never retains all local lengths.

The bounded visitor repeats each local cap before a push.
It draws each vector's policy from the already reserved family total.
No visitor trusts Serde's `size_hint` as allocation authority.

The raw revision bytes must equal the requested revision hash.
The raw Plan8 plan bytes must equal the stored plan ID.
This stronger raw-byte rule applies only to Plan8.
Plan8 does not call `ContentHash::document` on either parsed owner.

## Validation before plan construction

One private Plan8 validator extends the current Snapshot semantics.
It visits every asset and every timeline.

It uses borrowed origin slices instead of `Origin::sources()`, which currently creates a `Vec`.
It uses iterative lineage traversal instead of recursive traversal.

The validator owns these separately charged transients:

| Transient | Maximum live domain |
| --- | ---: |
| lineage `seen` set | `A <=10,000` |
| lineage `active` set | `A <=10,000` |
| lineage stack | `A <=10,000` |
| timeline ID set | `<=400,006` for one timeline |
| overlap range vector | `<=100,000` for one track |
| normalization scratch | checked prospective normalized keys under `K <=65,536` |

Only one timeline ID set is live at a time.
Only one track range vector is live at a time.
The source Snapshot and all authored vectors remain live throughout validation.

The selected timeline's audio cardinality is checked twice.
The token gate checks one track and one clip before typed allocation.
Typed validation then requires all of these facts before any plan collection is built:

- 48-kHz stereo output settings;
- one measured 48-kHz stereo audio asset;
- timeline coverage from zero through the complete output sample count;
- equal source and timeline lengths;
- unity gain and zero pan;
- exact canonical-audio asset and timeline-to-source interval mapping.

The current post-prepare checks at [`movie.rs:72`](../../crates/editor/src/movie.rs#L72) remain defense in depth.

Prospective normalized-key counts are computed without allocating normalized arrays.
`authored_keys + prospective_normalized_keys` must fit `65,536`.

Unselected clips normalize one at a time only for semantic validation.
Their scratch drops before the next clip.

Selected clips receive borrowed authored-form validation in this phase.
This phase retains no selected normalized result and constructs no draft owner.

After typed source validation succeeds, `J_revision`, `W_parse`, and `C_validate` drop.
Consuming compilation then normalizes each selected clip exactly once.
Each admitted normalized result moves directly into the private draft.
Final plan validation checks that result through borrowed views and never normalizes again.

The same normalization routine serves unselected validation and selected compilation.
A selected normalization error aborts before plan storage, worker start, or native work.

## Preparation ownership and construction

Use these nonoverlapping owner names:

- `J_revision`: one bounded revision-body buffer;
- `W_parse`: chunk storage, the 32-level token stack, and fixed `WireFacts` counters;
- `M_source` and `T_source`: admitted existing-media and text Snapshot ownership;
- `C_validate`: lineage, ID, range, and normalization scratch;
- `M_draft` and `T_draft`: private plan construction ownership;
- `C_compile`: coverage, used-assets, lineage queue, ordinals, and evidence scratch;
- `M_plan` and `T_plan`: finalized immutable Plan8 ownership;
- `C_plan_validate`: borrowed mapping, order, evidence, and closure-validation scratch;
- `G`: the A03 text gate;
- `J_plan`: one canonical serialized Plan8 buffer.

The checked preparation peaks are:

```text
read_peak = J_revision + W_parse

source_peak = J_revision + W_parse
            + M_source + T_source + C_validate

shape_peak = M_source + T_source
           + M_draft + T_draft + C_compile + G

plan_validate_peak = M_plan + T_plan + C_plan_validate

store_peak = M_plan + T_plan + J_plan
```

Every peak must be at most `536,870,912` logical bytes.
`T_plan + J_plan` must also satisfy the A03 128-MiB text envelope.

Each symbol means the bytes still live in that phase.
A moved allocation leaves its source term before it enters the destination term.
A cloned allocation appears in both terms while both owners remain live.

The schedule is exact:

1. Read, token-check, deserialize, and borrow-validate the complete source.
2. Retain no draft data while `J_revision` or `W_parse` is live.
3. Drop `J_revision`, `W_parse`, and `C_validate` after source validation.
4. Start consuming compilation and acquire draft permits before the first draft allocation.
5. Move the selected timeline into `M_draft` and `T_draft`.
6. Normalize each selected clip once and append its result to the draft.
7. Finalize the draft, then drop source remnants and compile scratch.

The selected timeline belongs to `M_source` and `T_source` before step 5.
It belongs to `M_draft` and `T_draft` after step 5.
It never belongs to `C_compile`.
`C_compile` owns only auxiliary coverage, queue, set, ordinal, and evidence storage.

Finalization moves the draft into the immutable plan.
It then drops source remnants, compile scratch, and draft-only storage before plan validation and serialization.
If an implementation keeps one of those owners, it must add the owner to the later peak.

`J_revision` and `W_parse` drop before any retained draft allocation.
They never coexist with `J_plan`.

A stored Plan8 replay uses two additional checked peaks:

```text
replay_read_peak = J_plan_read + W_parse

replay_validate_peak = J_plan_read
                     + M_plan + T_plan + C_plan_validate
```

`J_plan_read` drops after raw hash, bounded parse, and typed plan validation.
It is absent before any worker starts.

The Plan8 compiler consumes the admitted source owner.
It removes and moves the selected timeline, settings, canonical binding, used assets, and used font resources.
It does not clone their nested strings, sample vectors, warnings, or authored curves.

Source-map nodes and destination-map nodes can overlap during partitioning.
Each map retains its admitted high-water node permit until that map drops.
The source-map permit does not shrink as entries move or after the map becomes empty.
Moved nested values remain charged once.

Any representation that cannot move a field must charge its source and destination copies concurrently.

`M_draft` and `T_draft` own the selected timeline and its retained normalized values.
`C_compile` includes these auxiliary allocations:

- frame coverage through 100,000 frames;
- one audio coverage record;
- a used-assets set through 10,000 assets;
- an iterative lineage queue through 10,000 assets;
- `VideoUse` records through 400,000 clips;
- presentation ordinals through 400,000 `u64` values;
- source-closure map nodes and every cloned nested owner;
- movie and image evidence through 10,000 records.

The current `used.clone()` traversal must not remain in Plan8.
One used set plus one bounded queue supplies the closure.

The current mapping validator clones the source closure and timeline into a new Snapshot.
Plan8 instead validates the finalized plan through borrowed views.
It counts audio and picture iterators without collecting `Vec` copies.
Any required asset set is capped at 10,000 and charged to `C_plan_validate`.
The Plan2–7 validator remains unchanged.

## One canonical Plan8 buffer

Serialize the finalized Plan8 plan once through a 64-MiB capped writer into `J_plan`.
Hash those exact bytes with `ContentHash::bytes`.
Bind the same byte slice to the `plan8_plans.body` BLOB insertion.

Do not call `ContentHash::document` for a Plan8 plan.
Do not call `serde_json::to_string` after computing its ID.

The Rust owner remains live until the SQLite transaction commits.
SQLite's internal page copies are outside this Rust-owned logical policy and are disclosed as such.

Replay hashes the raw stored bytes before typed parsing.
Successful parse and validation cannot substitute for the raw-byte identity check.

The small domain-separated request-identity serialization drops before revision loading.
It is not a second Plan8 plan buffer.

## One shared immutable execution owner

Plan8 execution uses one private owner:

```rust,ignore
struct AdmittedPlan8 {
    plan: ExportPlan,
    fixed_permit: Permit,
}

type SharedPlan8 = Arc<AdmittedPlan8>;
```

The main writer and each worker clone only the `Arc`.
They do not clone `ExportPlan`, source closure, samples, ordinals, evidence, or text data.

This replaces the Plan8 equivalent of the current clone at [`movie.rs:178`](../../crates/editor/src/movie.rs#L178).
Legacy worker ownership remains unchanged.

The fixed permit remains inside the shared owner.
It releases after all workers, callbacks, responses, and the writer release their `Arc` values.

Public Plan8 preparation may return the sole plan by value after `Arc::try_unwrap`.
The execution path retains the shared owner and never constructs that public copy.

The execution check remains:

```text
execute_peak = M_plan + T_plan + R_active + G
             + P_media + O_execute + J_live
execute_peak <= 536,870,912
```

`J_live` is zero by contract.
`P_media` remains the existing temporal movie, PNG, canvas, response, and writer charge.

Cancellation, channel disconnect, callback failure, native exception, and fencing must join workers before releasing the final fixed permit.

## Tree policy and full-domain control

Keep the A01 positive high-water formulas:

```text
map_policy<K,V>(high_water) = checked(16 * high_water * size_of::<(K,V)>())
set_policy<K>(high_water) = checked(16 * high_water * size_of::<K>())
```

The product charges nested keys and values separately.
The tree policy covers node storage only.

`high_water` is the admitted or precreated maximum for that container.
A never-populated container with `high_water = 0` has no node permit.
A container with positive `high_water` acquires its complete node permit before its first insertion.
That permit never shrinks when entries move, merge, clear, or reach logical length zero.
It releases only after the container drops and its tracked outstanding node request becomes zero.

This lifetime matches the inspected Rust 1.94.0 removal path.
Final removal can retain an empty leaf root.
Logical length zero therefore does not authorize a zero live-node charge.

Controls must cover these actual domains:

| Product shape | Prefix domain |
| --- | ---: |
| `BTreeMap<ContentHash, StoredAsset>` | `0..=10,000` |
| `BTreeMap<EntityId, Timeline>` | `0..=10,000` |
| `BTreeSet<ContentHash>` | `0..=10,000` |
| `BTreeSet<EntityId>` | `0..=400,006` |
| `Snapshot::font_resources: BTreeMap<ContentHash, StoredFontResource>` | `0..=256` |
| `ExportPlan::font_closure: BTreeMap<ContentHash, StoredFontResource>` | `0..=64` |

Run sorted, reverse, and deterministic shuffled insertion orders.
Precreate keys and values before the tracked tree phase.
Charge their nested owners separately.

Each run grows one container once.
Before insertion, acquire the complete policy for the run's precreated high-water count.
After every insertion, require live requested node bytes not to exceed that held permit.
Then remove every entry while retaining the same permit.
After each removal, record logical length and actual outstanding node bytes.

After final removal, require the retained empty-root request to remain covered.
Then drop the container and require tracked outstanding node bytes to become zero.
Only that observed drop permits release of the logical node reservation.

An additional zero-high-water control constructs and drops a never-populated container.
It must request zero node bytes throughout.
`clear` may be observed separately, but it cannot authorize release without proven deallocation.

This is linear in the admitted domain for each order.
It does not rebuild a container for every prefix.

The control evaluates every prefix online and retains no per-prefix result vector.
Its report retains only boundary checkpoints, the worst live request, the retained-empty observation, and the post-drop zero.

The pinned toolchain must pass before integration.
A toolchain change repeats the control before product use.
This remains a logical requested-layout policy, not an allocator or RSS claim.

## Compatibility rules

Plan2–7 retain all current behavior:

- the `ExportRequest` type and field order stay unchanged;
- legacy request bytes and hashes stay unchanged;
- legacy `plans.body` remains text and uses its current serializer;
- legacy replay, validation, verification, recovery, and publication stay on the current path;
- historical Snapshot, plan, receipt, and artifact bytes stay unchanged.

The new route does not globally tighten historical source parsing.
The legacy dispatcher uses an exact Plan2–7 wire view and rejects new text fields.
It does not deserialize Plan8 text ownership through the legacy compiler.

Plan8 requires directly selected text.
A text-free Plan8 request fails instead of falling back.
A text-bearing legacy request follows the existing legacy parser and rejection behavior.
It never selects Plan8 and receives no new route-specific error promise.

Plan8 schema, text fields, font closure, and text policy remain those selected by the synthesis.
This document changes only routing and existing-media admission.

## Required implementation proof

### 1. Exact legacy compatibility

Compile existing public `ExportRequest` struct literals without edits.
Rehash every frozen Plan2–7 request, Snapshot, plan, receipt, and output binding.
Require exact equality.

### 2. Route controls

Prove all four combinations of text presence and public method.
Text-free input plus the legacy method succeeds.
Text-bearing input plus the Plan8 method succeeds.
Text-free input plus the Plan8 method fails with `plan8_text_required`.
Text-bearing input plus the legacy method preserves the exact legacy rejection.

Mutate persisted `plan_kind`, cross-table intent state, and route-specific request hashes.
Verification, recovery, and reconciliation must fail closed before a body fetch.

### 3. Pre-allocation controls

Exercise every count at its limit and one above.
Include `400,006/400,007` all-Snapshot IDs and `400,000/400,001` lineage edges.

Exercise the selected-domain authority for four 100,000-clip tracks plus one audio clip.
Exercise the same aggregate authority across unselected timelines.

Those full-domain controls test the counter, owner, and tree authorities directly.
They do not claim that every independent maximum fits one 64-MiB JSON body.
Body-backed controls use the largest encodable forms and test the body limit separately.
Each direct control precreates its values outside the tracked phase and charges every retained owner.

Reject an oversized SQLite body from the length query.
Prove that no whole body, typed Snapshot, plan clone, worker, or native object exists on that path.

Bind the exact metadata and chunk SQL strings in the proof.
Exercise multibyte UTF-8 boundaries with one-based byte offsets and 65,536-byte chunks.
Reject a short chunk, wrong result type, changed row identity, overflowed offset, and final byte-count mismatch.

### 4. Ownership and lifetime controls

Record every source, draft, validation, compile, plan, JSON, and execution permit transition.
Exercise cancellation and each error exit.
Require the ledger to return to zero.

Inject a second Plan8 serializer, a plan clone, and a retained revision buffer.
Each mutation must exceed or violate its declared owner rule.

### 5. Canonical-byte controls

Bind one Plan8 buffer address, byte count, SHA-256, plan ID, and SQLite readback.
Require exact equality.

Mutate whitespace, plan ID, body type, body length, and one stored byte.
Each mutation must fail before typed trust.

### 6. Full-domain tree controls

Run the incremental controls above through every declared prefix.
Bind the toolchain, source, helper, insertion seed, and compact report.
Require retained-empty coverage and zero tracked node bytes only after container drop.

### 7. Bounded product proof

After the source gates pass, prepare one useful Plan8 fixture.
It must include two movie readers, PNG, Indic text, motion, masks, and synthetic-offset audio.

Run a separate canonical 24-bit audio fixture.
Bind clocks, source mappings, pixels, cancellation, recovery, and exact legacy readback.

These output proofs remain separate from this design.

## Scope limits

This design governs application-owned logical Rust payloads on the Plan8 path.

It does not bound allocator metadata, physical pages, RSS, SQLite page-cache memory, or native framework allocations.
It does not establish throughput, power-loss durability, playback, hearing, creative approval, full-editor acceptance, or full-film completion.

Payload A03 supports the formulas and fixture observations above.
It does not prove that the current product satisfies this design.
