# Existing-media admission next design A01

## Status and decision

This is a source-only design proposal. No editor source, fixture, state, executable, media, GPU, or Resolve resource changed.

The Payload A03 measurement passed its declared logical-measurement scope. It does not establish product admission.

The smallest complete next delta is one private existing-media admission module. Plan8 preparation and execution consume its checked charges.

The module adds no Snapshot, Plan2–7, receipt, or artifact fields. Historical serialized bytes and hashes therefore remain unchanged.

Plan8 must fail closed until this module covers every current old-media owner. A text-only reservation cannot authorize Plan8.

## Bound evidence

The proposal uses these immutable measurement records:

| Record | Bytes | SHA-256 |
| --- | ---: | --- |
| Root readback `payload-build-prep-a10/measurement-parent-readback-a03.json` | 3,683 | `c7b2c6be9538d703f62ecc0f1cdb29290013906a546050b838c263683e73a2fc` |
| Measurement report `measurement-a03/runner-output/measurement-output/report.json` | 365,967 | `124102dcb3f4c76d97d3f4faa30678c8788df118a8210f64a562f5b63952e3ca` |
| Runner report `measurement-a03/runner-output/report.json` | 71,319 | `83f6196e6e69194d6c69c4509ba50e157226f707ffbd4f00797a5c9ee08f89bf` |
| Wrapper report `measurement-a03/measurement-wrapper-report-a03.json` | 310,664 | `c02245a4df8a440094bc8a5c05bcc473586ffea4ac5d555f11f14d45e6080aa6` |

The root readback recomputed 2,378 capacity rows. It also checked 28 B-tree request rows and seven precreation rows.

The readback matched 64 source rows and 4,065 dependency files. It recorded 57,684 generated-key cases.

The largest logical precreation charge was 132,369,399 bytes. The largest observed B-tree request total was 7,548,968 bytes.

The report explicitly records these limits:

- `physicalMemoryAdmissionEstablished=false`;
- `nativeExecution=false`;
- `productIntegrationAllowed=false`;
- `audiovisualAcceptance=false`.

The selected text contracts remain:

| Document | SHA-256 |
| --- | --- |
| `docs/design/text-admission-contract-a03.md` | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |
| `docs/design/text-synthesis-a01.md` | `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` |

The measurement package copied the runtime types and added measurement-only hooks. The current runtime files were inspected at these identities:

| Current file | SHA-256 | Relation to measured copy |
| --- | --- | --- |
| `model.rs` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` | Runtime fields match; copied file adds two feature-gated capacity accessors |
| `plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` | Exact byte match |
| `project.rs` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` | Exact byte match |
| `composition.rs` | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` | Exact byte match |
| `media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` | Exact byte match |
| `layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` | Copied file adds a feature-gated layout hook |
| `movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` | Copied file adds feature-gated layout hooks |
| `pcm.rs` | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` | Copied file adds a feature-gated layout hook |

The copied `lib.rs` only enables the feature-gated measurement module. These differences do not change the measured runtime layouts.

Any later runtime type change invalidates the measured layout rows. The post-implementation proof must remeasure the accepted source version.

## What A03 established

A03 measured these relevant inline layouts:

| Type | Bytes |
| --- | ---: |
| `Snapshot` | 272 |
| `StoredAsset` | 480 |
| `MediaDescriptor` | 128 |
| `SampleTiming` | 128 |
| `Timeline` | 80 |
| `VideoTrack` / `VideoClip` | 48 / 320 |
| `AudioTrack` / `AudioClip` | 48 / 96 |
| `ExportPlan` | 568 |
| `VideoUse` / `AudioUse` | 352 / 120 |
| `SourceDecodeEvidence` | 80 |
| `ImageDecodeEvidence` | 104 |

A03 also walked actual `String` and `Vec` capacities for six plans and five snapshots.

| Fixture | Bytes | SHA-256 | Parsed owned lower bound | Cloned owned lower bound |
| --- | ---: | --- | ---: | ---: |
| Plan2 | 369,279 | `97fdd9f63d48ee3b600ee37a845c302e79815bd1870b20dae376f9c4a957e025` | 298,425 | 295,057 |
| Plan3 | 4,983 | `4e5a89b00e7b5fabaafb4bf1335c1a5c3538c593765b4f5e5c818ff6bcede219` | 11,180 | 6,124 |
| Plan4 | 413,967 | `5cf0320f82bfc19839c5a06ffec15449fcdb80b97be15e2b4fb4105517ef0687` | 323,645 | 318,005 |
| Plan5 | 415,912 | `8ca51e03d048971a86cb598990fabd2f93f839c98b1b6c5fda3eb7aa90c3ee06` | 324,614 | 318,670 |
| Plan6 | 417,888 | `507038af46a4b5c970734a0c3738f034038b8228674c2058f9c1cb41b8ea7eb0` | 325,426 | 319,434 |
| Plan7 | 32,539 | `a771942c48dc0e9b1832bb81bccb56fe21e074fe58546f9c49a3bc95a1ec91a2` | 26,566 | 20,590 |
| Snapshot1 | 3,064 | `a4afc9237cdc477ddc0c62023b7e0ed185a9f39bd3f72fd3f6596964d1c82423` | 3,934 | 2,398 |
| Snapshot1 placement | 409,983 | `00d8a0eb3bbf0cd6290e68fffaa8c4d8b5a654446fb2220f5d084da17944e1ea` | 317,429 | 313,157 |
| Snapshot1 motion | 410,865 | `1947fcb6939dbec40f13ae23b87a156f5d6e1758fa18e058aaa1f810abc313d3` | 318,128 | 313,552 |
| Snapshot1 masks | 411,721 | `a7bc52df330b5a9d7e0ef8e8fe71b47963d308be393eeefa0e00d0cfbbfc24dd` | 318,498 | 313,922 |
| Snapshot1 alpha | 27,938 | `22619ba0bae6681d1da67cb65b3c850ecacef31a05c2d8ab13d082eae1af9e73` | 19,860 | 15,396 |

These lower bounds include one root layout and reachable `String` and `Vec` capacities. They exclude B-tree nodes and native memory.

The fixture values are observations. They are not maximums and cannot substitute for admission limits.

At 10,000 entries, A03 observed these current-thread B-tree requests:

| Owner | Calls | Requested bytes | Largest request |
| --- | ---: | ---: | ---: |
| `BTreeMap<ContentHash, StoredAsset>` | 1,355 | 7,548,968 | 5,656 |
| `BTreeMap<EntityId, Timeline>` | 1,548 | 1,816,320 | 1,256 |
| `BTreeSet<ContentHash>` | 1,331 | 387,560 | 376 |
| `BTreeSet<EntityId>` | 1,548 | 454,080 | 376 |

These are requested `Layout` callbacks for one pinned probe. They do not establish allocator, physical-memory, or RSS bounds.

## Current product boundary

The current product already enforces these limits:

| Quantity | Current limit | Enforcement point |
| --- | ---: | --- |
| Assets in a Snapshot | 10,000 | `Snapshot::validate_cancellable` |
| Timeline frames | 100,000 | `Snapshot::validate_cancellable` |
| Imported movie samples | 100,000 | `media::probe` only |
| Nonempty executed picture tracks | 1..=4 | `composition::preflight_cancellable` |
| One owned BGRA or alpha raster | 128 MiB | `pixels` and `alpha_picture` |
| Dynamic picture admission | 512 MiB | `composition::preflight_cancellable` |
| PCM chunk | 4,096 stereo frames | `pcm` |
| Output channels | 1..=8 | `Settings::validate` |

The current 512 MiB preflight covers canvas, source/raster peaks, and the configured PNG temporary allowance.

It does not include the retained `ExportPlan`, source closure, sample arrays, ordinals, or evidence vectors.

The following old-media owners remain unbounded at the Plan8 boundary:

- Snapshot timeline count;
- track and clip vector counts;
- `Origin.inputs` counts;
- persisted movie sample counts during replay;
- warning and channel-label counts;
- Snapshot, settings, origin, backend, codec, warning, and channel strings;
- plan `video`, `audio`, evidence, and ordinal capacities;
- validation and compile scratch collections;
- SQLite body and canonical serializer buffers.

`Project` currently parses stored bodies with ordinary `serde_json::from_str`. It serializes plans through separate identity and storage calls.

`plan::compile` clones the selected timeline and source assets. It also builds coverage, lineage, audio, use, and ordinal collections.

`movie::validate_profile` rejects anything except one native audio use. That rejection currently occurs after plan construction.

## Selected limits for the Plan8 path

These limits apply only when preparing, loading, replaying, or executing Plan8. They do not reinterpret Plan2–7.

### Structural counts

| Quantity | Plan8 rule | Reason |
| --- | --- | --- |
| Snapshot assets | `<=10,000` | Existing invariant |
| Snapshot timelines | `<=10,000` | Matches the measured map domain |
| Movie samples per descriptor | `<=100,000` | Promotes the existing import limit to Plan8 replay |
| Origin inputs per asset | `<=10,000` | Cannot exceed the admitted asset domain without repetition |
| Warnings per descriptor | `<=64` | Bounds many small diagnostic owners |
| Measured channel labels | `<=8`; when present, equal measured channels | Matches the current channel domain |
| Selected picture tracks | `1..=4`, all nonempty | Matches the existing executor |
| Selected audio tracks and clips | exactly one track containing exactly one clip | Matches the existing native writer contract |
| Video clips per selected track | `<=timeline.frame_count` | Positive nonoverlapping spans establish this bound |
| Aggregate selected video clips | `<=4 * timeline.frame_count` | Follows from four admitted tracks |
| Aggregate presentation ordinals | equal the selected clip-frame sum; `<=400,000` | One ordinal per output frame per track |
| Plan source closure | `<=10,000` | Subset of Snapshot assets |
| Movie decode evidence | one per directly used movie requiring evidence | Existing typed relationship |
| Image decode evidence | one per directly used image | Existing typed relationship |
| Combined motion, mask, and future text curves | `<=65,536` keys | Existing Plan8 text contract |
| Canonical Plan8 JSON | `<=64 MiB` | Existing Plan8 text contract |

Unselected timelines remain authoring state. Their actual tracks and clips receive full source-owner charges.

The 512 MiB aggregate stops large unselected authoring state. No unselected collection receives a zero-cost exemption.

### Existing-media strings

The Plan8 validator applies these byte limits before a pipeline-owned copy:

| Field | Limit |
| --- | ---: |
| `Snapshot.name` | 4,096 UTF-8 bytes |
| `Settings.working_color` | 128 UTF-8 bytes |
| `Origin::Imported.external_source` | 4,096 UTF-8 bytes |
| `Origin::Imported.role` | 1,024 UTF-8 bytes |
| `StoredAsset.backend` | 128 UTF-8 bytes |
| Image format and movie/audio codec | 128 UTF-8 bytes each |
| One decode error or warning | 4,096 UTF-8 bytes |
| One audio channel label | 128 UTF-8 bytes |
| `AudioBinding.channel_order_basis` | 4,096 UTF-8 bytes |
| `BuildIdentity.native_backend` | 128 UTF-8 bytes |
| `BuildIdentity.host_os` | 64 ASCII bytes |
| `BuildIdentity.architecture` | 32 ASCII bytes |
| `BuildIdentity.executable_uuid` | 64 ASCII bytes when present |

`ContentHash` remains exactly 64 lowercase hexadecimal bytes. `EntityId` retains its existing 128-byte ASCII limit.

Every admitted string also contributes its actual retained capacity to the live owner charge.

## One private accounting authority

Add one private module, provisionally `existing_media_admission.rs`.

It owns no media bytes and changes no serialized document. It computes checked policy charges and validates Plan8 limits.

```rust,ignore
pub(crate) struct ExistingMediaCharge {
    pub root_inline_bytes: u64,
    pub string_capacity_bytes: u64,
    pub vector_capacity_bytes: u64,
    pub tree_policy_bytes: u64,
    pub total_bytes: u64,
    pub counts: ExistingMediaCounts,
}

pub(crate) struct Plan8SourceAdmission {
    pub media: ExistingMediaCharge,
    pub selected: SelectedTimelineCounts,
}

pub(crate) fn inspect_plan8_snapshot(
    snapshot: &Snapshot,
    timeline: &EntityId,
    check: impl FnMut() -> Result<()>,
) -> Result<Plan8SourceAdmission>;

pub(crate) fn inspect_plan8_plan(
    plan: &ExportPlan,
    check: impl FnMut() -> Result<()>,
) -> Result<ExistingMediaCharge>;
```

The traversal uses the A03 owner vocabulary. Each owner appears once.

The charge includes:

1. one top-level root layout;
2. every reachable `String::capacity()`;
3. every reachable `Vec::capacity() * size_of::<T>()`;
4. one policy envelope for each B-tree or set;
5. every transient validation, lineage, coverage, range, and compile collection while live.

Nested struct roots already live inside parent vector or tree storage. The traversal must not add those inline bytes twice.

### Tree policy envelope

Use this deterministic logical policy for current B-tree and set owners:

```text
tree_policy<K,V>(0) = 0
tree_policy<K,V>(n) = checked(16 * n * Layout::<(K,V)>.size)
set_policy<K>(0)    = 0
set_policy<K>(n)    = checked(16 * n * Layout::<K>.size)
```

The factor 16 exceeds every A03 requested-layout row, including each one-entry node request.

This is an admission policy envelope. It is not a standard-library allocation guarantee.

A pinned-toolchain control must compare actual requested callbacks against this envelope across the admitted count domain.

If the control exceeds the envelope, product integration stops. The implementation must increase the policy or change the representation.

### Parsed owners and future owners

A loaded source owner is already allocated. Plan8 charges its actual capacities before any plan clone or native work.

Future plan collections use checked target counts. The builder reserves the policy charge before creating each owned collection.

After construction, the exact live capacities replace the provisional bound. Any excess fails before serialization or worker startup.

This sequencing controls application policy. It does not claim that Rust allocator internals obey the permit.

## Preparation integration

Keep the public caller unchanged:

```rust,ignore
Project::prepare_export(request) -> Result<PreparedExport>
```

The Plan8 branch performs these internal steps:

1. Read the stored body through the existing 64 MiB Plan8 input boundary.
2. Let the bounded token gate compute old-media counts and string lengths.
3. Reserve the source and JSON policy charges before typed deserialization.
4. Deserialize with bounded sequence visitors.
5. Inspect actual source capacities and reject any charge above the reserved bound.
6. Validate Snapshot identity, lineage, clocks, geometry, and Plan8 text fields.
7. Compute the selected timeline counts and a conservative plan-construction bound.
8. Reserve that bound before timeline, closure, use, ordinal, or evidence construction.
9. Build the plan with exact target capacities where practical.
10. Inspect the completed plan and replace the construction bound with its exact live charge.
11. Encode one canonical JSON buffer, then hash and store those same bytes.

The current `ContentHash::document` plus `serde_json::to_string` pair cannot serve step 11.

Plan8 needs a private canonical-byte owner. Plan2–7 retain their existing behavior and byte identity.

Move the native audio cardinality check before plan construction. Plan8 requires one track and one complete clip at that boundary.

The compiler can then allocate `audio` for exactly one use. It avoids constructing a plan that `movie` must immediately reject.

The preparation ledger retains the existing text-contract names:

```text
shape_peak = M_source + T_source + M_plan_draft + T_plan + G
             + C_old_prepare

finalize_peak = M_source + T_source + M_plan_final + T_plan + J
                + C_old_prepare

store_peak = M_plan_final + T_plan + J + C_old_prepare
```

`M_source` and `M_plan` come from the new existing-media authority.

`C_old_prepare` consists of individually reserved transient collections. It is not a fixed unexplained allowance.

Each peak must remain at or below 536,870,912 logical bytes.

## Execution integration

The current composition preflight remains the temporal authority for media frame payloads.

For Plan8, extend its result without changing the frame-sweep algorithm:

```rust,ignore
pub(crate) struct Admission {
    pub tracks: usize,
    pub peak_active_sources: usize,
    pub fixed_plan_bytes: u64,
    pub dynamic_picture_bytes: u64,
    pub estimated_bytes: u64,
}
```

`fixed_plan_bytes` contains `M_plan + T_plan`. `dynamic_picture_bytes` contains the existing media frame sweep and text runtime terms.

The Plan8 worker path creates one 512 MiB `Budget`. It first retains a fixed-plan permit.

Dynamic media, text gate, raster, canvas, response, and writer permits then use the remaining budget.

The execution check remains:

```text
execute_peak = M_plan + T_plan + R_active + G + P_media + O_execute + J_live
execute_peak <= 536,870,912
```

`J_live` is zero after Plan8 load and validation. Any retained JSON buffer needs a separate permit.

`P_media` is the existing temporal source/raster/canvas/PNG estimate. The plan charge is added once outside that sweep.

The permit lifetime ends only after workers, callback-owned media, response rasters, and the writer have released their owners.

## Compatibility and authority

The new module is private. Its report is live diagnostic data and never enters `ExportPlan` or `ArtifactReceipt`.

Plan2–7 parsing, validation, hashes, output identities, and receipt schemas remain unchanged.

Snapshot1 serialized fields remain unchanged. Optional Plan8 text fields follow the selected synthesis.

The central plan validator remains the source, clock, order, placement, motion, mask, alpha, and evidence authority.

The admission traversal does not duplicate those semantic checks. It only validates limits and charges owned representations.

The A03 fixture set becomes a compatibility regression set. Its eleven exact input hashes must remain unchanged.

Passing those fixtures will establish byte compatibility. It will not establish the Plan8 aggregate by itself.

## Verification plan

No native or audiovisual operation is needed for the first four gates.

### 1. Traversal equivalence

Port the A03 capacity-row walker into an independent test helper. Do not import the product admission function.

For all eleven frozen fixtures, compare every owner path, length, capacity, element size, and total.

Require exact agreement with the 2,378 A03 capacity rows. Bind the report and root-readback hashes above.

### 2. Limit controls

Use isolated constructed values for these boundaries:

- 10,000 and 10,001 timelines;
- 100,000 and 100,001 movie samples;
- four and five selected picture tracks;
- one and two selected audio clips;
- 400,000 and 400,001 presentation ordinals;
- every string at its limit and one byte above;
- 64 and 65 warnings;
- eight and nine measured channel labels;
- an origin input count at 10,000 and 10,001;
- a combined motion, mask, and text key count at 65,536 and 65,537.

Each negative must fail before plan cloning, serialization, source decode, or worker creation.

### 3. Aggregate and lifetime controls

Construct source and plan owners that remain below every individual limit but exceed the 512 MiB aggregate.

Require rejection at each preparation peak and at the execution peak.

Exercise source-to-plan cloning, one canonical JSON buffer, a forced second JSON buffer, cancellation, and every error return.

The recorded permit total must return to zero after each path.

### 4. Tree-policy controls

Under the pinned Rust toolchain, observe requested B-tree layouts for counts `0..=10,000`.

Use sorted, reverse, and deterministic shuffled insertion orders. Check all four measured key/value shapes.

Require every observed total to remain within the 16-times policy envelope.

This gate validates the policy against the tested toolchain. It does not convert the policy into an RSS claim.

### 5. Compatibility and product proof

Rehash the eleven frozen fixtures before and after all controls. Re-serialize them and preserve their accepted document identities.

Re-run the complete legacy Plan2–7 readback set and unchanged receipt/output identities.

Then prepare one maximum-useful bounded Plan8 fixture. It must combine two movie readers, PNG, text, synthetic-offset audio, and canonical 24-bit audio.

Record preparation peaks, execution permits, actual output clocks, independent pixels, cancellation, and recovery.

The Plan8 output proof remains separate from this source-only admission design.

## Scope limits

This design covers application-owned logical Rust payloads for existing media and the selected Plan8 path.

It excludes allocator metadata, physical pages, RSS, native framework allocations, native process peaks, throughput, and power-loss durability.

It makes no playback, hearing, creative, full-editor, or full-film acceptance claim.

The measured A03 result is sufficient to design the next delta. It is insufficient to claim that the current product passes admission.
