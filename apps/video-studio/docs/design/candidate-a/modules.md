# Module ownership

The native call chain stays short:

```text
library caller or CLI
        |
        v
video-studio-core: persistent Project aggregate
        |
        v
video-studio-macos: AVFoundation and Apple framework adapter
```

The aggregate owns one operation from request to durable result.
Callers do not coordinate probe, decode, composition, audio mix, encode, or artifact promotion.

## Native Cargo workspace

### `video-studio-core`

This is the independently usable Rust library.

It owns:

- `Studio` and `Project`, the complete public Rust surface.
- Exact clocks, intervals, frame rates, sample rates, curves, and timeline values.
- Immutable revisions, branch heads, stable intents, and optimistic conflicts.
- Asset imports, content identity, source representations, and lineage validation.
- Timeline tracks, retiming, composition order, masks, motion, color, audio, and text semantics.
- Render-job claims, fencing epochs, cancellation checkpoints, and artifact promotion.
- Source-bound artifact receipts and fresh byte verification.
- Version-bound review evidence and derived gate evaluation.
- Capability ownership and native build identity.

Internal modules follow knowledge boundaries:

```text
video-studio-core/src/
  lib.rs                 public Studio and Project surface
  project.rs             aggregate transaction and invariant owner
  revision.rs            immutable snapshot identity and branch heads
  asset.rs               content identity, probing claims and representation bindings
  lineage.rs             acyclic derivation graph and exact range ancestry
  timeline.rs            clocks, tracks, items, retiming and nesting invariants
  visual.rs              composition, masks, motion and color semantics
  audio.rs               sample-domain placement, gain, pan and mix semantics
  text.rs                exact Unicode content, font assets and shaping requirements
  export.rs              durable export intent, lease, fencing and final receipt
  review.rs              evidence variants and policy evaluation
  storage.rs             SQLite transactions and aggregate-owned paths
  platform.rs            sealed MediaPlatform interface
```

These are internal reading units.
They do not become separate service interfaces.

`project.rs` can complete a commit or export through internal calls.
No public load, validate, compile, decode, render, encode, or save service exists.

### `video-studio-macos`

This crate implements the sealed native media interface.
It owns every unsafe Apple framework call.

It owns:

- AVFoundation asset probing and sample-level reading.
- Core Media timestamps and sample buffers.
- Core Video pixel buffers and buffer pools.
- Core Image or CPU-backed visual surfaces selected by declared capability.
- Core Text shaping and Core Graphics glyph rasterization.
- AVAssetWriter video and audio inputs, MP4 or QuickTime muxing, and finalization.
- Framework errors translated into stable native domain errors.
- Runtime codec probes for each exact profile.

Its internal modules are grouped by framework knowledge:

```text
video-studio-macos/src/
  lib.rs                 one MacOsMediaPlatform implementation
  asset.rs               AVURLAsset, AVAssetReader and sample indexes
  surface.rs             CVPixelBuffer ownership and image attachments
  graphics.rs            Core Image, Core Text and Core Graphics adaptation
  writer.rs              AVAssetWriter, H.264 or ProRes, AAC or PCM, container mux
  capability.rs          can-read and can-write probes with host identity
  ffi.rs                 retained Objective-C objects and autorelease boundaries
```

The crate does not own edit decisions.
It receives validated internal requests from `video-studio-core`.

AVFoundation classes, `CMTime`, `CMSampleBuffer`, and `CVPixelBuffer` stay private.
An SDK change therefore affects one crate.

### `video-studio-cli`

This executable is a real adapter, not a second editor.

It owns:

- Arguments and one-request JSON framing.
- Protocol and schema version negotiation.
- Conversion from wire DTOs into validated domain values.
- Request and response byte limits.
- Signal handling, process deadlines, and cancellation tokens.
- Progress events on stderr and one terminal JSON result on stdout.
- Stable exit-code classes.
- Generated JSON schema publication.

It does not own:

- Project storage or revision selection.
- Asset hashing or media probing.
- Timeline validation.
- Render scheduling or retries.
- Codec fallback policy.
- Review promotion.

The executable links the library and macOS adapter.
It never launches a media subprocess.

### `video-studio-acceptance`

This development and release verifier is outside the runtime protocol.

It owns:

- Immutable fixture manifests and independent expected values.
- Direct CLI execution and exit-code checks.
- Source and artifact remeasurement.
- Movie reopen, sample timestamp, frame-count, audio-alignment, and decode checks.
- Static Cargo and source audits for FFmpeg, libav, and renderer subprocess paths.
- Capability promotion receipts bound to binary, schema, OS, and verifier hashes.
- Negative tests for stale revisions, changed intents, unsupported codecs, and forged evidence.

The verifier cannot change the compiled capability registry.
Its receipt can only verify a capability that the native binary reports as implemented.

## Persistent project aggregate

Each project has one aggregate root and one owned directory.

```text
state/projects/<project-id>/
  project.sqlite          revisions, heads, intents, jobs, artifacts, reviews
  blobs/sha256/<hash>     immutable imported bytes and media indexes
  artifacts/<artifact-id> aggregate-owned completed outputs
  staging/<intent-id>/    recoverable, untrusted work until promotion
```

The SQLite schema is private.
Other applications cannot query or update it.

The aggregate has four durable journals:

1. The revision journal stores immutable project snapshots and mutable branch heads.
2. The intent journal makes create, commit, export, and review submission idempotent.
3. The export journal binds long work to one revision, request, backend, and fencing epoch.
4. The evidence journal stores observations that bind an exact revision and artifact.

Large media bytes live in the content-addressed store.
The revision stores their hashes and measured descriptors.

### Commit transaction

The aggregate stages imports before the short SQLite transaction.
It reads and hashes bytes through one open file handle.
It copies those same bytes into an intent-scoped staging location.

The transaction then:

1. Checks for an identical completed intent.
2. Rejects changed content under the same intent.
3. Compares the requested base with the branch head.
4. Resolves import keys to measured asset identities.
5. Applies every edit to an in-memory candidate snapshot.
6. Validates timelines, source bounds, lineage, nesting, fonts, and limits.
7. Appends the immutable revision and moves the branch head.
8. Stores the completed intent result.

No invalid edit becomes visible.
An orphaned content-addressed blob is harmless and collectable.

### Export transaction

Export does not hold a database write lock for the movie duration.

The aggregate first creates or reconciles a job in a short transaction.
The job binds:

- Intent and canonical request hash.
- Immutable revision and project hash.
- Complete source-closure manifest hash.
- Native renderer and framework identity.
- Output profile and staging identity.

A worker claims the job with a fencing epoch.
The worker renders into the aggregate's staging directory.

Before promotion, the aggregate reopens and measures the movie.
It then checks the fencing epoch in one final transaction.
A stale worker cannot promote output after another worker takes ownership.

If the process dies, the next identical export request inspects the existing job.
A valid completed output is adopted.
A partial file is discarded and recomputed under the same job.
A changed output becomes an integrity failure.

The first implementation may recompute an interrupted MP4 from frame zero.
This preserves correctness before resumable native encoding exists.

## Source representations

One logical source can have two byte identities:

- `authority` is the preserved original.
- `representation` is the exact file selected for native decode.

The representation equals the authority when the native backend supports the original.
Otherwise, the relation needs an explicit sample-range mapping and verification receipt.

This design addresses Panja's mixed codec reality.
The AV1 source decodes on the current host.
The VP9 source does not decode through AVFoundation on the current host.

The editor never substitutes a representation by filename, extension, or newest timestamp.
The project revision names the selected representation and mapping.

## Review ownership

Review records are part of the aggregate but outside the revision document.
Recording a review does not create a new edit revision.

Every record binds:

- Project ID and immutable revision.
- Project snapshot hash.
- Artifact ID and output byte hash.
- Renderer build hash.
- Evidence kind, coverage, actor, outcome, and policy version.

Policy state is derived on read.
The database does not store a trusted `accepted = true` flag.

Measurement, frame inspection, playback, listening, and creative judgment are distinct variants.
A policy gate names the required variant and coverage.

Full-playback and full-listening evidence never carries to a changed artifact.
A component record can carry only through a new explicit revalidation record.

## Separate Effect and tenant adapters

The application layer sits outside the native Cargo workspace.

```text
Effect application
  tenant authorization
  budget and usage records
  Herdr or provider jobs
  native-worker process supervision
  delivery workflow
        |
        v
versioned video-studio CLI contract
        |
        v
native Project aggregate
```

The Effect adapter owns authenticated tenant mapping.
The native project ID is never accepted as proof of tenant ownership.

The adapter stores each GPU submission intent before network submission.
It uses states such as `prepared`, `submission_uncertain`, `bound`, and `transfer_verified`.

After restart, the adapter checks Herdr, ComfyUI queue, and history before retrying.
Only a definitive absence or failed attempt permits a new attempt ID.

The native editor receives generated bytes only after transfer hash verification.
The import records the external attempt receipt and all source anchors.

Alchemy may provision the application and workers later.
It is not a native editor dependency.

## Dependency rules

Allowed directions are:

```text
video-studio-cli        -> video-studio-core
video-studio-cli        -> video-studio-macos
video-studio-macos      -> video-studio-core sealed platform types
video-studio-acceptance -> video-studio-cli executable and public receipts
Effect adapter          -> versioned CLI schema and executable
```

Forbidden directions are:

- `video-studio-core` to CLI or Effect transport types.
- `video-studio-core` to process arguments or exit codes.
- `video-studio-macos` to SQLite tables.
- Effect adapters to native SQLite tables.
- UI or Effect code to a second timeline reducer.
- Any runtime crate to FFmpeg, libav, or a renderer subprocess.

