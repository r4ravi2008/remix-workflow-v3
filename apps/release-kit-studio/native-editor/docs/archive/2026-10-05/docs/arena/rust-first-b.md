# Candidate B: Rust workspace with a process-free editor core

## Usage (caller's view)

Build the local workspace. Then discover commands without access to storage:

```sh
cargo build --workspace
native-editor tools
native-editor schema project.commit
native-editor call project.create create.json --state ./example
native-editor call project.commit edit.json --state ./example
native-editor call frame.render frame.json --state ./example
native-editor verify local-example artifact-1 --state ./example
```

`call` supplies the negotiated version/schema envelope. `serve-once --state ./example` accepts that exact envelope on stdin. Each command emits one JSON response and exits. Discovery, schema, progress, and demo require no Bun runtime.

The agent procedure is:

1. Discover `engine.capabilities`.
2. Store the schema hash.
3. Invoke `serve-once` with the immutable request.

After timeout, the agent terminates its owned process and inspects/replays the original intent.

An embedded Rust caller uses domain commands directly:

```rust
let editor = Editor::open(state_root, Limits::p0())?;
let created = editor.execute(Command::CreateProject(create))?;
let committed = editor.execute(Command::CommitProject(edit))?;
let frame = editor.execute(Command::RenderFrame(render))?;
```

The same editor serves a future desktop adapter. That adapter supplies typed commands and receives measured results. The adapter does not read SQLite.

## Problem

Deliver P0 solid PNG frames, immutable revisions, and authoritative receipts through Rust alone. The current domain, identity, protocol, and SQLite contracts stay unchanged. Effect, React, Tauri, hosted authorization, and UI dependencies live outside `native-editor`. Movie codecs, audio, typography, GPU execution, and full release kits stay planned. FFmpeg/libav and historical Python renderer delegation are prohibited.

## Shape

Use a Cargo workspace with two production crates and a test-only acceptance crate:

| Crate/module | Knowledge owned |
| --- | --- |
| `editor-core/project.rs` | Validated identifiers, normalized rational rates, intervals, edits, snapshot identity |
| `editor-core/store.rs` | Per-project SQLite, revisions, intent replay, concurrency, recovery |
| `editor-core/frame.rs` | RGBA composition, deterministic PNG, durability, receipt verification |
| `editor-core/lib.rs` | Complete command execution and native capability registry |
| `editor-cli/protocol.rs` | Strict JSON envelopes, duplicate-key rejection, negotiation, output framing |
| `editor-cli/main.rs` | Arguments, executable identity, discovery, schemas, demo, progress presentation |
| `editor-acceptance` | Real-process acceptance and independent decoding/canonicalization |

The library links no process-launch or framework code. SQLite and PNG implementation details stay private. Domain command schemas derive from Rust types. Envelope schemas derive inside the CLI. No handwritten parallel reducer exists.

```rust
pub struct ProjectId(String); // validated, private representation
pub struct IntentId(String);
pub struct FrameRate { numerator: NonZeroU32, denominator: NonZeroU32 }
pub struct Interval { start: FrameIndex, duration: FrameCount }
pub enum VisualSource { Solid { rgba: [u8; 4] } }
pub enum Edit { PutClip { clip: Clip }, RemoveClip { clip_id: ClipId } }
pub enum Command { CreateProject(CreateProject), InspectProject(InspectProject),
    CommitProject(CommitProject), RenderFrame(RenderFrame), VerifyArtifact(VerifyArtifact) }
pub struct Execution { pub result: CommandResult, pub replayed: bool }
impl Editor {
    pub fn open(root: impl AsRef<Path>, limits: Limits) -> Result<Self, EditorError>;
    pub fn execute(&self, command: Command) -> Result<Execution, EditorError>;
}
```

Bodies stay `not implemented` until synthesis. Validated constructors enforce checked arithmetic and positive durations. The public operation hides coordination of transactions, renders, and recovery.
This is one deep interface, as specified by Boundary Discipline.

Commit replay precedes revision checks. Identity uses the specified JCS command document and shared `(projectId,intentId)` namespace. Each project owns SQLite and artifacts.

A render commits its pending record, then holds `BEGIN IMMEDIATE` during bounded production. Recovery regenerates deterministic expected bytes before it adopts staged or promoted output. Completed corrupt evidence fails verification. Receipts do not accept caller hashes or output paths.

## Errors and retries

Preserve all declared error codes and typed details. Exit 0 means success, 2 means domain rejection, 1 means storage/process/internal failure.
Unknown and unavailable tools differ. Strict envelopes preserve request IDs, schema hashes, and disjoint variants. Enforce all specified byte, integer, clip, frame, and canvas limits.

Only `store_busy` permits bounded identical-intent retry.

Conflicts require inspection. Different content requires a deliberate new intent. Interrupted calls retain uncertain outcomes until reconciliation. The direct CLI does not claim an embedded library can forcibly terminate filesystem operations. Deadlines for agent-owned processes provide hard termination.
Bounded operations and cancellation observations require acceptance through real processes.

## Acceptance and sequencing

1. Implement validated domain types, identity vectors, schemas, and compiled discovery.
2. Implement SQLite creation/commit/replay and concurrent/crash cases.
3. Implement solid PNG render, durable recovery, and registered verification.
4. Implement direct CLI, independent acceptance runner, and evidence-derived progress.

Run each current P0 matrix case against Rust processes. Rename Effect ownership to Rust CLI for CORE-07/08. Bind acceptance interface identity to the Rust CLI build manifest. Compare each RGBA pixel with an independent decoder. Verify schema strictness, JCS vectors, interruption points, tamper/forgery rejection, executable hashes, and dependency policy. Only current receipts whose identities match promote features.

## Tradeoffs, alternatives, and screening

We accept two crate manifests for an enforced reusable library boundary. A single lib/bin package hides similar behavior but cannot separately restrict CLI dependencies. A daemon exposes lifecycle complexity before measured need.

The design has no shallow coordination API or transport envelope leakage.
It has no modules for temporal stages or pass-through wrappers. Future adapters are in separate applications beside this application. They use the library or the current JSON protocol. No adapter queries storage. The parent owns the synthesis decision.
