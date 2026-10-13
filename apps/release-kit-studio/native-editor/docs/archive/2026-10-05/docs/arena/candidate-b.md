# Candidate B: Effect-authoritative project service

Status: architecture candidate only. It makes no Resolve-parity, codec, cloud, or production claim.

## Problem

The current project schema fixes 24 fps and six release outputs. Those rules belong to the release-kit profile.
The old local CLI also reaches the Python and FFmpeg renderer. The new path must stay independent.

This candidate recommends Effect ownership of projects, edits, revisions, agent commands, and evidence states.
It recommends Rust ownership of bounded native processing.
Rust receives a compiled frame recipe, so it does not interpret clips, timebases, or revision semantics.

Unit 1 renders one deterministic PPM frame from procedural solid clips. This proves native bytes. It does not imply video support.

## Usage first

```sh
cd apps/release-kit-studio
bun run native:build
export NATIVE_EDITOR_HOME="$(mktemp -d)/native-editor"
bun run native-editor -- tools
bun run native-editor -- schema project.create
bun run native-editor -- call project.create /tmp/create.json
bun run native-editor -- call project.commit /tmp/commit.json
bun run native-editor -- call project.commit /tmp/commit.json
bun run native-editor -- call artifact.render-frame /tmp/render.json
bun run native-editor -- call artifact.verify /tmp/verify.json
```

The create request defines a two-frame, 2-by-2 project with a blue background and one empty layer.

```json
{"intentId":"create-v1","projectId":"demo","document":{"schemaVersion":1,"name":"canary","timeline":{"timebase":{"numerator":24,"denominator":1},"durationFrames":2,"canvas":{"width":2,"height":2,"colorSpace":"srgb","background":{"r":0,"g":0,"b":255}},"layers":[{"id":"accent","clips":[]}]}}}
```

The commit adds a red right-column clip at expected revision zero.

```json
{"intentId":"red-v1","projectId":"demo","expectedRevision":0,"edits":[{"kind":"put-solid-rect","layerId":"accent","clip":{"kind":"solid-rect","id":"right","startFrame":0,"durationFrames":2,"rect":{"x":1,"y":0,"width":1,"height":2},"color":{"r":255,"g":0,"b":0}}}]}
```

The first commit returns revision one. A replay of the same intent returns revision one with `replayed: true`.
A changed request with `red-v1` returns `IntentConflict`. A new stale edit returns `RevisionConflict`.

```json
{"intentId":"frame-0-v1","projectId":"demo","revision":1,"frame":0,"format":"ppm-rgb8-v1"}
```

The artifact is exactly 23 bytes. Its SHA-256 is `b7331c36e3460b744fd063e6774dcaa608f225942b10218038a57c3901d2a579`.

```text
P6\n2 2\n255\n + 00 00 ff ff 00 00 00 00 ff ff 00 00
```

Programmatic callers use one Effect service. The service coordinates project load, locks, native processing, and storage for callers.

```ts
const editor = yield* EditorProjectService
const snapshot = yield* editor.execute(commit)
const artifact = yield* editor.execute({ _tag: "RenderFrame", projectId: snapshot.projectId,
  revision: snapshot.revision, intentId: IntentId.make("frame-0-v1"), frame: Frame.make(0), format: "ppm-rgb8-v1" })
```

## Core shape

```ts
type ProjectId = string & Brand.Brand<"ProjectId">
type IntentId = string & Brand.Brand<"IntentId">
type Revision = number & Brand.Brand<"Revision">
type Frame = number & Brand.Brand<"Frame">
type Sha256 = string & Brand.Brand<"Sha256">

interface SolidRectClip { readonly kind: "solid-rect"; readonly id: string; readonly startFrame: Frame;
  readonly durationFrames: number; readonly rect: { x: number; y: number; width: number; height: number };
  readonly color: { r: number; g: number; b: number } }
interface ProjectDocumentV1 { readonly schemaVersion: 1; readonly name: string; readonly timeline: {
  readonly timebase: { numerator: number; denominator: number }; readonly durationFrames: number;
  readonly canvas: { width: number; height: number; colorSpace: "srgb"; background: SolidRectClip["color"] };
  readonly layers: ReadonlyArray<{ id: string; clips: ReadonlyArray<SolidRectClip> }> } }
type Edit = { kind: "put-solid-rect"; layerId: string; clip: SolidRectClip }
  | { kind: "remove-clip"; layerId: string; clipId: string }
type EditorCommand = ProjectCreate | ProjectCommit | ProjectInspect | RenderFrame | VerifyArtifact

interface EditorProjectServiceShape {
  readonly catalog: Effect.Effect<ToolCatalog, CatalogError>
  readonly execute: <C extends EditorCommand>(command: C) => Effect.Effect<ResultOf<C>, EditorError>
}
```

Effect `Schema` values decode CLI inputs once. Pure reducers then trust branded domain values.
The core accepts rational frame rates. It has no release-output count or fixed-rate invariant.

Layers compose bottom-to-top. Clip IDs are unique per layer. Clips in one layer cannot overlap.
Clip intervals and rectangles must fit the project. Unit 1 accepts no unimplemented clip variant.

`catalog` reports implementation and verification separately. Planned tools stay discoverable with an unavailable reason.
The public service hides SQLite rows, local paths, process arguments, native wire types, and retry machinery.

## Rust processing boundary

Rust owns `RasterizeFrameV1`, its limits, raster pixels, PPM serialization, and native receipt schema.
It publishes Draft 2020-12 schemas through `schemars`. Effect imports them with `SchemaRepresentation.fromJsonSchemaDocument`.
An integration test rejects unsupported schema constructs and excess properties. The Rust wire schema stays private.

```rust
enum NativeOperation { RasterizeFrameV1 { protocol_version: u16, recipe: RasterFrameRecipeV1, output_path: PathBuf } }
struct RasterFrameRecipeV1 { project_sha256: Sha256, frame: u64, width: u32, height: u32,
  background: Rgb8, fills: Vec<FillRect> }
```

Effect selects active clips and emits ordered fills. Rust knows no timeline, project revision, intent, or product profile.
The adapter selects `output_path` in its staging directory. Agent input cannot provide a path or executable argument.

`native-editor-core describe` emits schemas and capabilities. `execute` accepts one JSON request without a shell.
Rust writes a temporary file in the output directory. It flushes the file. Rust renames the file.
Rust then reopens the file and returns measured bytes and SHA-256.

The crate forbids unsafe code. Its locked dependency graph contains no FFmpeg or libav binding.

## Ownership and modules

| Owner | Knowledge hidden |
|---|---|
| `domain.ts` | Project schemas, edits, timeline invariants, frame compilation |
| `commands.ts` | Agent schemas, tool catalog, tagged errors |
| `project-store.ts` | Per-project SQLite, revisions, compare-and-swap, command replay |
| `artifact-store.ts` | Render intents, staging, promotion, crash reconciliation |
| `native-processor.ts` | Rust schema import, exact spawn, timeout, cancellation |
| `artifact-verifier.ts` | Independent hash, PPM header, dimensions, payload checks |
| Rust `contract.rs` | Processing wire contract and native capability limits |
| Rust `ppm.rs` | Pixel generation and deterministic PPM bytes |
| `project-service.ts` | Catalog intersection and complete command orchestration |
| `cli.ts` | JSON envelopes, exit codes, configured-root path presentation |

Each project owns `projects/<id>/project.sqlite`, `artifacts/`, and `staging/`.
SQLite `BEGIN IMMEDIATE` serializes the one genuine shared writer. Different projects share no mutable file.

Create, commit, and render use `(intentId, canonical request SHA-256)`. The same content replays. Changed content conflicts.
Commit checks the intent before the head. A successful old intent can replay after later revisions exist.

Render records a pending intent before Rust starts. A replay verifies promoted or staged bytes before another compute attempt.
Effect independently verifies Rust output before promotion. The service does not silently regenerate a completed corrupt artifact.

## Errors and retries

Errors are tagged data with `retry: never | same-intent | inspect-and-rebase | repair-installation | repair-artifact`.

| Error | Behavior |
|---|---|
| `InvalidInput`, `UnknownTool`, `UnsupportedCapability` | Do not retry automatically |
| `RevisionConflict` | Inspect the project. Rebase the edit. Then use a new intent. |
| `IntentConflict` | Treat the conflict as a caller bug. Do not repurpose the intent. |
| `StoreBusy`, `ProcessorBusy` | Retry the same intent three times with bounded backoff |
| `ProcessorInterrupted` | Reconcile the staging directory. Then retry the same intent once. |
| `ProcessorContractMismatch` | Rebuild the matched Effect and Rust pair |
| `ArtifactIntegrityMismatch` | Keep the evidence. Require explicit repair. |

The frame operation has a 30-second deadline. Cancellation interrupts and awaits Rust before reconciliation.
Validation, revision, intent, native-rejection, and integrity failures do not retry automatically.

## Runnable Unit 1 verification

`bun run native:verify-foundation` builds Rust and runs the actual CLI in an owned temporary root.
It saves the original PPM, altered PPM, command envelopes, and `receipt.json` under `.local/native-editor/verification/`.

The script verifies schema import, catalog discovery, create, commit, identical replay, and changed-intent rejection.
It rejects a stale revision and known `render.video` request. It renders the exact 23-byte PPM through Rust.

It independently compares each byte and SHA-256 with expected values.
It then changes one pixel and requires `ArtifactIntegrityMismatch`.
It audits Cargo dependencies and invocation sites for FFmpeg and libav. Compilation alone cannot mark verification complete.

The receipt records byte measurement and the format parser result.
It records frame inspection, motion review, listening review, and acceptance as false.

Unsupported in Unit 1: media decoding, PNG/JPEG, video codecs, audio, text shaping, transforms, alpha, masks, effects, GPU, UI, cloud, and Resolve interchange.
`render.video` returns `UnsupportedCapability(VIDEO_CODEC_NOT_IMPLEMENTED)`. No request can fall back to the old engine.

## Future Cloudflare boundary

The future Worker can reuse Effect schemas, pure reducers, hash rules, errors, and the Rust processing contract.
It must replace local SQLite with tenant-scoped D1, local bytes with R2, and process spawn with Container RPC.

The Worker derives tenant identity from authentication. The isolate does not start a local Rust process.
Hosted render operations need durable jobs and reconciliation. This local synchronous command does not define those states.
Local evidence cannot satisfy deployment, tenant-isolation, billing, Container, or real-release gates.

## Poteto fit and red-flag screen

Foundational Thinking fixes the types and authority split first. Boundary Discipline confines validation to CLI and Rust IPC.
Idempotent Operations drives stable intents and reconciliation. Separate Before Serializing gives each project isolated state.
Minimize Reader Load keeps one public service. Prove It Works saves a rerunnable, artifact-bound receipt.

The service is deep: two public capabilities hide transactions, native execution, and recovery.
Storage and wire representations do not leak. Commands own complete transitions. Modules do not divide a transition into temporal stages.
Each adapter adds policy or changes abstraction, so no module is a pass-through wrapper.

## Rationale and rejected alternatives

Effect authority gives agents one semantic model and keeps ordinary edits independent from native process availability.
Rust stays authoritative where native limits and byte production matter. PPM exposes the boundary without codec ambiguity.
Per-project SQLite supplies real transactions and keeps task state separate.

- A Rust-authoritative project kernel makes Effect a wrapper and forces simple cloud edits through a Container.
- An Effect-only rasterizer cannot prove the required Rust boundary.
- JSON files plus lock directories expose the operation sequence at a crash and weaken atomic intent replay.
- A daemon or native addon adds lifecycle or ABI ownership before measurements justify it.

The design scores are:

- No-FFmpeg: `5/5`.
- Single-owner invariants: `5/5`.
- Agent interface: `5/5`.
- Local and cloud boundary: `4/5`.
- Artifact proof: `5/5`.
- Poteto fit: `5/5`.

Open risks are Bun SQLite portability, the first canvas bound, and future `schemars` importer compatibility.
None blocks the 2-by-2 PPM unit. This candidate recommends tests that set each bound before capability expansion.

The next procedure is:

1. Implement this single coupled unit.
2. Save its verification receipt.
3. Read the saved verification receipt.
