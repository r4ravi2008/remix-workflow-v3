# Candidate A. Rust authoritative kernel with an Effect agent bridge

## Problem

The new editor needs a local executable path that proves native processing. The current editor schema and CLI belong to the release kit. They fix 24 fps, limit projects to six outputs, and select a Python and FFmpeg renderer. Their receipts cannot establish a Rust implementation.

The new foundation must keep Rust as the only owner of edit semantics. Effect supplies typed orchestration and an agent interface.

The first unit must run on a developer machine without Cloudflare, codecs, GPU access, or Resolve. It must produce a real native artifact, replay an intent safely, and reject stale, unknown, and altered work. It must also leave a clear boundary for a future Cloudflare control plane.

## Usage (caller's view)

The consumer uses one scoped Effect service. The service starts a Rust kernel process. It discovers the kernel capabilities and validates agent input. When the Effect scope closes, the service closes the process. The consumer does not know the wire framing, journal layout, or renderer implementation.

```ts
import { Effect } from "effect"
import { NativeEditor } from "@release-kit/native-editor"

const program = Effect.gen(function* () {
  const editor = yield* NativeEditor

  const capabilities = yield* editor.discover()
  const created = yield* editor.createProject({
    projectId: "poteto-demo",
    intentId: "create-poteto-demo",
    frameRate: { numerator: 24, denominator: 1 },
    duration: { frames: 24 },
  })

  const committed = yield* editor.commit({
    projectId: created.project.id,
    expectedRevision: created.project.revision,
    intentId: "put-solid-clip",
    edit: {
      kind: "clip.put",
      clip: {
        id: "solid-background",
        start: 0,
        length: 24,
        source: { kind: "solid", rgba: [12, 25, 48, 255] },
      },
    },
  })

  const receipt = yield* editor.renderPreview({
    projectId: committed.project.id,
    revision: committed.project.revision,
    intentId: "preview-solid-clip",
    frame: 0,
    format: "ppm-p6",
    width: 8,
    height: 8,
  })
  const verification = yield* editor.verifyArtifact(receipt)

  return { capabilities, committed, receipt, verification }
}).pipe(
  Effect.scoped,
  Effect.provide(
    NativeEditor.layer({
      taskId: "poteto-demo",
      stateRoot: ".local/native-editor/tasks/poteto-demo",
      evidenceRoot: ".local/native-editor/evidence",
      kernelBinary: "native-editor/kernel/target/debug/native-editor-kernel",
    }),
  ),
)
```

The command line wrapper supplies the same operations for an agent that cannot import TypeScript. It starts one private state root per task.

```sh
bun run native-editor:cli -- --state-root .local/native-editor/tasks/poteto-demo discover
bun run native-editor:cli -- --state-root .local/native-editor/tasks/poteto-demo invoke project.create --input create.json
bun run native-editor:cli -- --state-root .local/native-editor/tasks/poteto-demo invoke project.commit --input solid-clip.json
bun run native-editor:cli -- --state-root .local/native-editor/tasks/poteto-demo invoke artifact.render-preview --input preview.json
bun run native-editor:cli -- --state-root .local/native-editor/tasks/poteto-demo invoke artifact.verify --input receipt.json
```

The wrapper prints JSON results and writes a verification receipt under the requested evidence root. It never prints the kernel token because local execution uses a private process pipe rather than a network bearer token.

An agent first discovers the contract. The contract supplies the command names and request shapes.

```ts
const tools = yield* editor.discover()
const commitTool = tools.find(tool => tool.name === "project.commit")
if (!commitTool) return yield* Effect.fail(new UnsupportedCapability("project.commit"))

const result = yield* editor.invoke(commitTool.name, agentJson, {
  taskId: "poteto-demo",
})
```

`discover` returns a capability ledger and Draft 2020-12 input and output schemas. `invoke` validates `agentJson` against the discovered input schema. It sends a domain request to Rust, then validates the response. It returns a result that is safe for an agent. The caller does not construct an NDJSON envelope.

An ordinary program uses typed methods when it knows the operation. The typed method crosses the same boundary. The typed method receives the same Rust validation and evidence.

```ts
const result = yield* editor.commit({
  projectId: "poteto-demo",
  expectedRevision: 0,
  intentId: "put-solid-clip",
  edit: {
    kind: "clip.put",
    clip: {
      id: "solid-background",
      start: 0,
      length: 24,
      source: { kind: "solid", rgba: [12, 25, 48, 255] },
    },
  },
})
```

The same call with the same `intentId` and content returns the original revision with `replayed: true`. If you reuse that `intentId` for different content, the call fails with `intent_conflict`. After the first commit reaches revision 1, a new intent with `expectedRevision: 0` fails with `revision_conflict`.

## Shape

### Ownership decision

Rust owns the edit domain. Rust parses and validates the project. Rust applies edits, assigns revisions, and stores intent records. Rust renders the first native artifact and calculates artifact receipts. Effect owns process lifetime, schema discovery, agent input decode, retry classification, cancellation, and evidence-file writes.

Neither side keeps a second timeline model.

The Rust kernel is a deep module. Five domain methods hide the journal, revision checks, idempotency, artifact names, and native pixel generation. The Effect service is a second deep module at a different boundary. It hides process startup, protocol framing, schema import, resource cleanup, and retry recovery. The protocol adapter is private and does not appear in the public package.

Both the Effect boundary and the Rust boundary decode raw JSON. This obeys boundary discipline. The revisioned intent log directly represents the edit state. This obeys model-the-domain.

The first unit has one timeline track, one native still format, and one storage mechanism. This obeys the laziness protocol. The first unit adds no abstraction for future codecs before a codec exists.

### Core Rust domain types

These are the domain types that the kernel owns. Constructors validate their ranges. The sketches show the public structure. The bodies stay `not implemented` until Unit 2.

```rust
pub struct ProjectId(String);
pub struct IntentId(String);
pub struct ClipId(String);
pub struct AssetId(String);
pub struct Revision(u64);
pub struct FrameIndex(u64);
pub struct FrameCount(std::num::NonZeroU64);

pub struct FrameRate {
    pub numerator: std::num::NonZeroU32,
    pub denominator: std::num::NonZeroU32,
}

pub struct Rgba8(pub [u8; 4]);

pub struct FrameRange {
    pub start: FrameIndex,
    pub length: FrameCount,
}

pub enum VisualSource {
    Solid { rgba: Rgba8 },
}

pub struct Clip {
    pub id: ClipId,
    pub range: FrameRange,
    pub source: VisualSource,
}

pub struct Timeline {
    pub duration: FrameCount,
    pub clips: Vec<Clip>,
}

pub struct Project {
    pub schema_version: u16,
    pub id: ProjectId,
    pub revision: Revision,
    pub frame_rate: FrameRate,
    pub timeline: Timeline,
}

pub enum Edit {
    PutClip { clip: Clip },
    RemoveClip { clip_id: ClipId },
}

pub struct CreateProject {
    pub project_id: ProjectId,
    pub intent_id: IntentId,
    pub frame_rate: FrameRate,
    pub duration: FrameCount,
}

pub struct CommitIntent {
    pub project_id: ProjectId,
    pub expected_revision: Revision,
    pub intent_id: IntentId,
    pub edit: Edit,
}

pub struct ProjectSnapshot {
    pub project: Project,
    pub fingerprint: Sha256,
}

pub struct CommitResult {
    pub project: Project,
    pub fingerprint: Sha256,
    pub replayed: bool,
}

pub enum StillFormat {
    PpmP6,
}

pub struct PreviewIntent {
    pub project_id: ProjectId,
    pub revision: Revision,
    pub intent_id: IntentId,
    pub frame: FrameIndex,
    pub format: StillFormat,
    pub width: std::num::NonZeroU32,
    pub height: std::num::NonZeroU32,
}

pub struct ArtifactReceipt {
    pub artifact_id: String,
    pub project_id: ProjectId,
    pub revision: Revision,
    pub intent_id: IntentId,
    pub format: StillFormat,
    pub relative_path: String,
    pub bytes: u64,
    pub sha256: Sha256,
    pub width: u32,
    pub height: u32,
}

pub struct VerificationReceipt {
    pub artifact: ArtifactReceipt,
    pub measured_bytes: u64,
    pub measured_sha256: Sha256,
    pub passed: bool,
}
```

`VisualSource::Solid` is deliberate. It permits a real pixel artifact without a claim of video decode, audio decode, typography, or codec support. Add more source variants only when their capability and verification path exist.

The domain service owns the invariants. The public kernel trait is intentionally small.

```rust
pub trait Kernel {
    fn describe(&self) -> Result<CapabilityManifest, KernelError>;
    fn create_project(&mut self, input: CreateProject) -> Result<ProjectSnapshot, KernelError>;
    fn inspect_project(
        &self,
        project_id: ProjectId,
        revision: Option<Revision>,
    ) -> Result<ProjectSnapshot, KernelError>;
    fn commit(&mut self, input: CommitIntent) -> Result<CommitResult, KernelError>;
    fn render_preview(&mut self, input: PreviewIntent) -> Result<ArtifactReceipt, KernelError>;
    fn verify_artifact(
        &self,
        receipt: ArtifactReceipt,
    ) -> Result<VerificationReceipt, KernelError>;
    fn reconcile_intent(
        &self,
        intent_id: IntentId,
    ) -> Result<Option<StoredIntentResult>, KernelError>;
}
```

The trait is a domain interface. It does not accept paths to executables, SQL statements, HTTP requests, or raw JSON. `KernelService` implements it with a `ProjectJournal` and an `ArtifactStore`.

### Effect public service

The Effect package supplies domain values and a discovery API for agents. It does not export Rust serde structs or protocol envelopes.

```ts
export type AbsolutePath = string & { readonly AbsolutePath: unique symbol }
export type TaskId = string & { readonly TaskId: unique symbol }

export interface NativeEditorOptions {
  readonly taskId: TaskId | string
  readonly stateRoot: AbsolutePath | string
  readonly evidenceRoot: AbsolutePath | string
  readonly kernelBinary: AbsolutePath | string
  readonly startupTimeoutMs?: number
}

export interface CapabilityManifest {
  readonly protocolVersion: 1
  readonly kernelVersion: string
  readonly capabilities: ReadonlyArray<Capability>
  readonly schemaDigest: string
}

export interface Capability {
  readonly name: string
  readonly support: "implemented" | "planned" | "unsupported"
  readonly description: string
  readonly inputSchema: JsonSchemaDocument
  readonly outputSchema: JsonSchemaDocument
  readonly evidence: EvidenceRef | null
}

export interface NativeEditorApi {
  readonly discover: () => Effect.Effect<CapabilityManifest, DiscoveryError>
  readonly invoke: (
    name: string,
    input: unknown,
    context?: AgentContext,
  ) => Effect.Effect<unknown, AgentError>
  readonly createProject: (
    input: CreateProjectInput,
  ) => Effect.Effect<ProjectSnapshot, CommandError>
  readonly inspectProject: (
    input: InspectProjectInput,
  ) => Effect.Effect<ProjectSnapshot, CommandError>
  readonly commit: (
    input: CommitIntentInput,
  ) => Effect.Effect<CommitResult, CommandError>
  readonly renderPreview: (
    input: PreviewIntentInput,
  ) => Effect.Effect<ArtifactReceipt, CommandError>
  readonly verifyArtifact: (
    input: ArtifactReceipt,
  ) => Effect.Effect<VerificationReceipt, CommandError>
}

export class NativeEditor extends Context.Tag("NativeEditor")<
  NativeEditor,
  NativeEditorApi
>() {
  static layer(options: NativeEditorOptions): Layer.Layer<NativeEditor> {
    // not implemented
    return Layer.die("NativeEditor.layer is a design sketch")
  }
}
```

`CreateProjectInput`, `InspectProjectInput`, `CommitIntentInput`, and `PreviewIntentInput` are Effect domain values. The service derives their definitions from the Rust schemas at runtime. The service does not use manually copied definitions. `JsonSchemaDocument` appears only inside the agent discovery result because an agent needs a contract. The editor does not use that document type as its internal timeline representation.

The service imports Rust's generated Draft 2020-12 documents with Effect 4.

```ts
const inputSchema = SchemaRepresentation.fromJsonSchemaDocument(
  capability.inputSchema,
  {
    patterns: "apply",
    onExcessProperty: "error",
  },
)

const input = yield* Schema.decodeUnknown(inputSchema)(rawAgentInput)
```

This removes a second hand-maintained timeline schema. Rust `schemars` remains the schema authority. The imported schema is a boundary decoder. Rust still validates every command after the decode step.

### Module map

Each module owns a specific kind of knowledge. The modules do not separate the load, validate, transform, and save phases.

| Module | Owner | Responsibility | Private details |
| --- | --- | --- | --- |
| `kernel/domain.rs` | Rust | Project, timeline, frame, edit, intent, and artifact types | Constructors and domain invariants |
| `kernel/kernel.rs` | Rust | Apply commands, fold revisions, render preview, reconcile intents | No JSON or process APIs |
| `kernel/journal.rs` | Rust | Per-project immutable event files and atomic recovery | File names, fsync, locking |
| `kernel/artifacts.rs` | Rust | Deterministic PPM output and SHA-256 receipts | Temp paths and byte reads |
| `kernel/capabilities.rs` | Rust | Capability ledger and generated JSON schemas | `schemars` derive details |
| `kernel/protocol.rs` | Rust | NDJSON request and response adapter | Envelope and serde types |
| `kernel/main.rs` | Rust | Stdio loop and process exit behavior | Framing limits and stderr diagnostics |
| `agent/kernel-client.ts` | Effect | Start the binary and translate protocol replies into domain results | Child process and protocol frames |
| `agent/schemas.ts` | Effect | Import discovered JSON Schema documents | Schema cache keyed by digest |
| `agent/native-editor.ts` | Effect | Scope, typed methods, agent invocation, retry policy | No timeline rules |
| `agent/cli.ts` | Effect | `discover`, `invoke`, and evidence receipt commands | CLI argument validation |
| `agent/verification.ts` | Effect | Save local acceptance evidence | Receipt serialization only |

`kernel-client.ts` is an adaptation boundary, not a pass-through public API. It translates process failures, response envelopes, and dynamic JSON into typed `CommandError` values. `native-editor.ts` owns the retry and reconciliation policy for the user. The caller does not coordinate both modules.

### Private protocol

The first protocol is one request and one response per newline-delimited JSON record. Stderr is for diagnostics. Stdout contains protocol records only.

```json
{"protocol":1,"requestId":"r-17","operation":"project.commit","input":{}}
{"protocol":1,"requestId":"r-17","ok":true,"output":{}}
```

An error response has a stable code, a human message, and optional current state.

```json
{
  "protocol": 1,
  "requestId": "r-17",
  "ok": false,
  "error": {
    "code": "revision_conflict",
    "message": "Expected revision 0 but current revision is 1.",
    "retry": "inspect_then_rebase",
    "currentRevision": 1
  }
}
```

The protocol adapter enforces a maximum request and response frame size. It rejects duplicate request IDs during one process lifetime. The Effect client ties a response to its request ID and fails on malformed, missing, or extra records. The wire types stay private. Later transport changes do not enter the agent API.

### Persistent state and ownership

Each Poteto task receives its own state root. The first implementation uses immutable event files instead of a mutable database.

```text
<stateRoot>/
  task.json
  projects/<project-id>/events/0000000000000000.json
  projects/<project-id>/events/0000000000000001.json
  artifacts/<artifact-id>.ppm
  receipts/<intent-id>.json
  evidence/<run-id>.json
```

The kernel folds the ordered event files to derive the current revision. It keeps no second `HEAD` revision that can disagree with the project. Every event contains the intent ID, content fingerprint, expected revision, result revision, and domain command. The kernel writes and synchronizes a temp file. The kernel atomically renames the temp file before the event becomes visible.

The kernel takes one process lock for a state root. A second process receives `state_owned` and does not write. Concurrent Poteto tasks use separate roots and publish evidence at the read boundary. A later merge command can compare project fingerprints and revisions. The kernel does not use instructions to take turns as concurrency control.

The event log is intentionally small and auditable for Unit 1. A future compaction operation can write a snapshot only after proof that replay and recovery produce the same project fingerprint. Compaction is outside this first unit.

### Invariants

Rust enforces these rules in constructors and the kernel service. Effect uses the result types after the boundary decode step.

| Invariant | Enforcement | Observable failure |
| --- | --- | --- |
| IDs are non-empty and path-safe | `ProjectId`, `IntentId`, `ClipId`, and `TaskId` constructors | `invalid_identifier` |
| Frame rate is positive and canonical | `FrameRate::new` rejects zero and reduces the ratio | `invalid_frame_rate` |
| Frame ranges have positive length | `FrameCount` and `FrameRange` constructors | `invalid_frame_range` |
| Clips stay inside the timeline | `Timeline::put_clip` | `clip_out_of_bounds` |
| Unit 1 has one visual track without overlaps | `Timeline` checks ranges before commit | `timeline_overlap` |
| The project revision is contiguous | Journal fold and atomic event creation | `corrupt_journal` |
| A commit requires the current revision | Compare and swap under the state lock | `revision_conflict` |
| An intent has one content fingerprint | Journal lookup by `IntentId` | `intent_conflict` |
| An intent replay returns the stored result | Intent record in the event | `replayed: true` |
| Preview is tied to project revision and intent | Receipt fields and deterministic artifact ID | `artifact_binding_mismatch` |
| Artifact bytes are measured from disk | `verify_artifact` reads and hashes the file | `artifact_changed` |
| Output stays inside the state root | Kernel generates relative paths and rejects traversal | `invalid_artifact_path` |
| No external media tool runs | Kernel has no external renderer adapter or shell escape | `unsupported_capability` for video work |

The old release profile's six output limit and fixed 24 fps do not appear in this model. A release-kit adapter can add that policy at a higher boundary later. It cannot change the kernel's frame or revision rules.

### Error and retry policy

Errors are tagged values. Message text is explanatory. Agent policy branches on codes.

```ts
export type CommandError =
  | InvalidInput
  | UnsupportedCapability
  | StateOwned
  | ProjectNotFound
  | RevisionConflict
  | IntentConflict
  | CorruptJournal
  | ArtifactBindingMismatch
  | ArtifactChanged
  | KernelExited
  | ProtocolViolation

export type RetryClass =
  | "none"
  | "bounded_startup"
  | "reconcile_then_replay"
  | "inspect_then_rebase"
```

| Failure | Effect behavior |
| --- | --- |
| Invalid input, unsupported capability, state ownership, intent conflict, corrupt journal, artifact mismatch, or altered artifact | Fail immediately. Do not retry. |
| Kernel startup failure | Restart at most twice. Use bounded delays of 100 ms and 500 ms. Preserve the original error if all attempts fail. |
| EOF or timeout after a mutating request | Call `reconcile_intent` with the same intent ID. Replay only when the stored fingerprint matches. Never issue a new intent automatically. |
| Revision conflict | Return the current revision. The agent must inspect the revision. After the agent selects a merge or rebase, the agent must create a new intent. |
| Read-only `discover` or `inspect` failure caused by a clean process exit | Restart once, then retry the same read. |
| Preview request after uncertain completion | Reconcile by intent and artifact binding. Do not render a second artifact with a new ID. |

`Effect.Schedule` implements only these bounded policies. It does not retry every error. The kernel's content fingerprint includes the protocol version, operation, project ID, expected revision, intent ID, and canonical command JSON. The same input therefore converges to one result even after a crash.

### Capability ledger and unsupported work

`discover` returns every named capability with a support state and evidence pointer. The first ledger contains at least these entries.

| Capability | State in Unit 1 | Behavior |
| --- | --- | --- |
| `project.create` | Implemented | Creates revision 0 in the journal |
| `project.inspect` | Implemented | Folds a revision and returns its fingerprint |
| `project.commit` | Implemented | Applies a solid clip edit with revision and intent checks |
| `artifact.render-preview` | Implemented | Writes a native PPM P6 still |
| `artifact.verify` | Implemented | Rehashes the actual artifact and returns a receipt |
| `audio.decode` | Unsupported | Returns `unsupported_capability` |
| `video.decode` | Unsupported | Returns `unsupported_capability` |
| `video.encode` | Unsupported | Returns `unsupported_capability`. Attempts no fallback |
| `caption.render` | Planned | Returns `unsupported_capability` until shaping evidence exists |
| `resolve.import` | Unsupported | No Resolve project parser is present |
| `gpu.render` | Planned | No GPU path is claimed |
| `cloudflare.execute-native` | Unsupported locally | Requires a future native runner outside a Worker isolate |

An unsupported operation does not create a placeholder artifact. It does not silently select the old Python engine or report a future feature as complete. The capability ledger records the missing evidence.

### First implementation unit

Unit 1 is one end-to-end local canary. It is intentionally narrower than a release kit.

1. `discover` starts the Rust kernel and reads its capability manifest.
2. `project.create` creates a 24 frame project with a general `FrameRate` value and revision 0.
3. `project.commit` adds one 8 by 8 solid clip over the 24 frame timeline at expected revision 0.
4. The same commit with the same intent returns revision 1 and `replayed: true`.
5. A new commit with expected revision 0 returns `revision_conflict` and leaves the journal unchanged.
6. `artifact.render-preview` renders frame 0 as a PPM P6 still. It does not encode a film.
7. `artifact.verify` reads the generated file, measures bytes and SHA-256, and writes an evidence receipt.
8. A change to one artifact byte makes `artifact.verify` return `artifact_changed`.
9. An unknown operation and every unimplemented media operation return `unsupported_capability`.

The kernel process has no dependency on FFmpeg, libav, Python, a browser, Resolve, or a network service. The Effect CLI can spawn only the configured Rust binary. The Rust binary does not spawn another renderer.

### Local verification

The recommendation is to include one saved integration check in the first implementation. The check starts a fresh temporary state root and exercises the actual process boundary.

```sh
bun install --frozen-lockfile
cargo test --manifest-path apps/release-kit-studio/native-editor/kernel/Cargo.toml
bun run native-editor:integration
bun run native-editor:check-no-ffmpeg
```

The integration check must assert all these results:

- `discover` returns the Rust kernel version and the five implemented Unit 1 capabilities.
- The imported Rust schemas reject an unknown field with `onExcessProperty: "error"`.
- The first commit reaches revision 1 and writes one event file.
- The exact commit replay returns the original fingerprint and does not write a second event.
- The kernel rejects a stale edit. The current project still has revision 1.
- The PPM file starts with the expected `P6` header. The file has the requested dimensions and contains the solid RGB bytes.
- The receipt SHA-256 equals a fresh hash of the file on disk.
- A byte mutation fails verification.
- `cargo tree` contains no FFmpeg or libav dependency, and the integration trace contains no external media command.
- The evidence file names the exact kernel binary, protocol version, project fingerprint, and artifact path.
- It also names the artifact bytes, artifact SHA-256, and check command.

This is a native artifact check. It does not establish render quality, video playback, listening review, typography review, or Resolve parity.

### Poteto-mode workflow fit

The CLI gives installed Poteto workflows a small, repeatable control interface.

- Before a task opens the editor, the task selects a unique `taskId` and state root.
- `discover` supplies the current schema and capability ledger before an agent plans a command.
- `invoke` records the task ID and intent ID in every result.
- Each mutation call uses an explicit intent and expected revision.
- Each task writes acceptance evidence under its own evidence directory.
- The integration check is the throughput checkpoint for the first feature unit.
- After a crash, a task can reconcile its intent to resume. The task does not guess the result from process state.
- Separate tasks never write one shared project root. A later read-side merge compares fingerprints and revisions.

The CLI does not encode Poteto prose or pretend that a checklist is concurrency control. It supplies the state and evidence that those workflows need.

### Future Cloudflare boundary

Cloudflare remains a control plane. Cloudflare authenticates the tenant and assigns a release scope. Cloudflare stores opaque project and intent metadata. Cloudflare sends work to a native runner. A Worker isolate does not execute the Rust process. The Worker isolate does not claim native render output.

The future adapter has a separate contract.

```ts
export interface NativeRunnerTicket {
  readonly tenantId: TenantId
  readonly projectId: ProjectId
  readonly expectedRevision: Revision
  readonly intentId: IntentId
  readonly projectFingerprint: Sha256
  readonly operation: "project.commit" | "artifact.render-preview"
}

export interface NativeRunner {
  readonly submit: (
    ticket: NativeRunnerTicket,
  ) => Effect.Effect<NativeJob, WorkerDispatchError>
  readonly reconcile: (
    intentId: IntentId,
  ) => Effect.Effect<NativeJob | null, WorkerDispatchError>
}
```

The runner executes the same Rust kernel outside the Worker isolate. The Worker records the last observed kernel revision. It does not increment a second timeline revision or reapply edits in D1. D1 can store tenant and intent ownership. R2 can store immutable source objects and receipts.

The Rust journal stays authoritative for timeline semantics. The Worker must report `remote-native-runner` only after it reads a runner receipt bound to the project fingerprint and artifact hash.

The local adapter and future Cloudflare adapter share the agent tool vocabulary, but their runtime capabilities are explicit. Local `discover` reports `execution: "local-rust-process"`. The Worker reports `execution: "cloud-control-plane"` until a native runner produces evidence. A missing runner is a typed error, not a fallback to the old renderer.

## Synthesis decision

This file is candidate A. It awaits the parent arena synthesis. It recommends the Rust-authoritative structure because all timeline and artifact invariants have one owner. It uses Effect as a boundary and orchestration layer rather than as a second editor implementation.

## Tradeoffs accepted

- We accept an append-only event directory in Unit 1 in exchange for crash recovery and an inspectable revision history. Compaction waits for a separate verified unit.
- We accept a PPM still artifact in exchange for proof of native bytes without a codec dependency. The first unit does not produce an encoded film.
- We accept one state-root lock in exchange for deterministic single-writer behavior. Parallel Poteto tasks receive separate roots.
- We accept runtime import of Rust JSON Schema in exchange for no duplicate Effect timeline schemas. Rust still validates each decoded command.
- We accept a process boundary. Local execution and the future hosted native runner can then use the same kernel contract.
- We accept a small domain API. Audio, video, typography, GPU, and Resolve work stay explicitly unsupported until each has its own evidence.

## Alternatives considered

### Effect-authoritative project service with Rust operation adapters

In this alternative, Effect owns `Project`, revisions, and edit semantics. Rust supplies render operations. This alternative hides process orchestration, but duplicates timeline rules across TypeScript and Rust. Stale revisions, intent replay, and artifact bindings then need two implementations. The public service appears simpler but gives maintainers more coordination work. It loses on single ownership and native proof.

### Reuse the current local Python and FFmpeg engine behind a new CLI

This shape has the shortest implementation path. It violates the no-FFmpeg requirement and cannot prove that a Rust kernel processed the artifact. It also imports release-kit limits into the general editor. It is rejected before implementation.

### Cloudflare-first control and render service

The Worker can own tenant state and render intents. It cannot run a native Rust process inside the current isolate boundary. A synthetic Worker receipt cannot prove local native output. This structure also makes local tests depend on provider credentials and cloud state. This proposal keeps the structure only as a future control-plane adapter.

### SQLite-backed shared editor service

In this alternative, SQLite supplies transactions and a familiar query interface. It adds a storage schema before proof of the domain contract. It encourages the Effect and Worker layers to inspect database rows. The immutable event files expose less storage policy and keep revision recovery inside the Rust owner. SQLite remains a possible later storage adapter if replay and compaction evidence justify it.

### Rust compiled to WASM for the Worker

In this alternative, WASM can reduce the process boundary. It does not solve the current codec, filesystem, GPU, or execution-duration constraints. It also makes local and hosted capability sets appear identical too early. A native runner boundary keeps the unsupported behavior explicit.

## Open questions and risks

- Which Unit 2 option is preferable before audio and video? A source image asset, or only the solid visual fixture until artifact review tools exist?
- After the local kernel receipt contract becomes stable, which option is preferable for the first hosted native runner? A long-lived service or one isolated container per intent?
- What signing or authenticated transport will bind a future runner receipt to a tenant? How will it keep timeline ownership outside D1?
- How large can the event directory grow before a measured compaction unit becomes necessary?
- Which Poteto evidence directory convention is preferable before more than one native-editor task runs in parallel?
- Which native text-shaping library and font packaging policy can pass Telugu, Hindi, and Tamil frame review? Which choice preserves the kernel's timeline model?

## Grounding rubric score

| Criterion | Score | Reason |
| --- | ---: | --- |
| No FFmpeg and honest future codec boundary | 5 | The first renderer emits PPM and the kernel has no external media process. |
| One owner per invariant | 5 | Rust owns project, revision, intent, and artifact semantics. |
| Agent discovery and recovery | 5 | Effect imports Rust schemas, exposes discovery, classifies errors, and reconciles intents. |
| Local execution and Cloudflare boundary | 5 | The local process is independent. Cloudflare dispatches only to a future native runner. |
| Reproducible first artifact proof | 5 | The PPM bytes, receipt, replay, stale edit, and mutation checks are explicit. |
| Poteto workflow fit | 4 | Per-task roots and evidence are defined. Repository-specific task conventions remain open. |

## Next implementation step

1. Build the Rust domain, journal, PPM renderer, and private NDJSON loop.
2. Add one scoped Effect client.
3. Add the integration check described above.
