# Candidate A: one Rust package, one deep editor boundary

## Problem

P0 must prove an editor that uses an owned Rust implementation. P0 must not imply movie support. It must preserve rational timelines, immutable revisions, stable intents, per-project SQLite, protocol v1, and source-bound receipts. It must render only bounded solid RGBA clips to PNG. FFmpeg, libav, Effect, React, Tauri, video, audio, and hosted tenancy stay outside this package and outside P0 claims.

## Usage (caller's view)

An agent discovers the binary before mutation:

```sh
native-editor tools
native-editor schema project.commit
native-editor call --state "$STATE" < commit-request.json > commit-response.json
native-editor verify local-example frame-zero-v1 --state "$STATE"
```

`call` accepts exactly one protocol-v1 JSON envelope on stdin. It writes one success or error envelope to stdout. Diagnostics use stderr. Discovery returns the schema hash, build identity, limits, and implemented tool registry. Every non-discovery request supplies that schema hash.

An embedded Rust caller uses the same domain operation:

```rust
let editor = Editor::open(StateRoot::trusted_local(state_dir))?;
let result = editor.execute(Command::CommitProject(commit))?;
let verified = editor.execute(Command::VerifyArtifact(verify))?;
```

The acceptance runner never links the library. It spawns the compiled binary and evaluates process output, restart and concurrency behavior, and artifact bytes.

## Shape

The package is `native-editor`, with a library and `native-editor` binary. Its public API is small:

```rust
pub struct Editor { /* store, renderer, registry */ }
pub enum Command {
    CreateProject(CreateProject), InspectProject(InspectProject),
    CommitProject(CommitProject), RenderFrame(RenderFrame),
    VerifyArtifact(VerifyArtifact), Capabilities,
}
pub enum CommandResult { Created(CreateResult), Snapshot(ProjectSnapshot),
    Committed(CommitResult), Rendered(ArtifactReceipt),
    Verified(ArtifactMeasurement), Capabilities(Capabilities) }
pub enum RetryDirective { Never, SameIntentBackoff, InspectThenRebase,
    InspectOriginalIntent, DiagnoseStorage }
pub struct EditorError { pub code: ErrorCode, pub retry: RetryDirective,
    pub details: ErrorDetails, /* stable message */ }
impl Editor { pub fn open(root: StateRoot) -> Result<Self, EditorError>;
    pub fn execute(&self, command: Command) -> Result<CommandResult, EditorError>; }
```

Newtypes represent identifiers, revisions, frame positions, nonzero durations, frame-rate terms, hashes, and dimensions that pass validation. `Interval` remains half-open. `VisualSource::Solid { rgba }` is the only source. One ordered track rejects overlap but permits adjacency. Edit transactions apply all changes or none.

Transport envelopes and SQLite rows are private. Both convert into domain types once, at their respective boundaries.

### Module map

| Path | Knowledge owned |
| --- | --- |
| `src/lib.rs` | `Editor`, public commands, results, and errors |
| `src/project.rs` | Timeline invariants, edits, snapshots, and project hashes |
| `src/identity.rs` | JCS fingerprints, SHA-256 types, identity versioning |
| `src/store.rs` | Per-project SQLite revisions, intents, locking, and recovery |
| `src/frame.rs` | Deterministic RGBA evaluation, PNG writing, measurement |
| `src/receipt.rs` | Artifact and acceptance receipt bindings |
| `src/protocol.rs` | Strict envelopes, schemas, tool registry, exit mapping |
| `src/bin/native-editor.rs` | Arguments, bounded stdin/stdout, diagnostics |
| `tests/acceptance.rs` | Black-box P0 matrix through child processes |
| `tests/support/` | Independent JCS vectors, PNG decoder, fault controller |

`store.rs` does the replay lookup before the revision comparison. Intent identity remains `(projectId, intentId)`. Fingerprints bind identity version, protocol version, tool, and canonical input. One `BEGIN IMMEDIATE` transaction owns each mutation. Render commits a pending intent. Render holds the project write lock during bounded production.

Render synchronizes the bytes, then promotes the artifact atomically. Render then records the measured receipt. Recovery regenerates the deterministic expected bytes before it adopts output. Recovery never replaces corrupt evidence.

Domain rejections use exit 2. Process, storage, or internal failures use exit 1. Success uses exit 0. Current error codes and P0 resource limits remain unchanged.

The binary never retries a mutation with a new intent. Only for `store_busy`, callers can retry after a delay. The retry uses the identical request.

For revision conflicts, callers must inspect the revision and deliberately select a new intent. After interruption, callers must inspect or replay the original intent. Callers must not retry an integrity mismatch automatically.

## Acceptance and implementation sequence

1. Define newtypes, commands, errors, JCS vectors, and generated Draft 2020-12 schemas.
2. Implement project rules and pure hash calculation for snapshots.
3. Implement SQLite creation, immutable revisions, intent replay, conflicts, and concurrent writers.
4. Implement solid-frame evaluation, deterministic PNG, promotion, receipts, and fresh verification.
5. Add the thin JSON binary and exit-code contract.
6. Run standalone cases for the complete P0 matrix.
7. Include concurrent processes, tampering, limits, protocol rejection, and compile-time-gated crash failpoints.

Only acceptance receipts that match can promote `CORE-01` through `CORE-06` and applicable `CORE-08` checks. `CORE-07` remains planned and external. Movie, audio, typography, GPU, and release-kit capabilities remain planned.

## Future adapter boundary

Future Effect, React, Tauri, Foldkit, and hosted adapters live outside `native-editor`. They discover and invoke the versioned JSON process contract. A Rust host can depend on the library. UI types cannot enter the library's public API. Hosted identity and authorization remain adapter responsibilities.

## Tradeoffs and red-flag screen

- We accept one larger package in exchange for one version, one schema authority, and short traces.
- We accept per-invocation startup cost until measurements justify a daemon.
- We reject a multi-crate split. The split adds build boundaries to P0 but hides no new policy.
- We reject command-specific service methods. That design makes callers coordinate shallow wrappers.

The design has no modules divided into load, validate, and save phases. Storage rows and wire envelopes stay private. The CLI adds protocol framing and exit policy instead of only argument forwarding. The two public methods hide validation, persistence, render operations, recovery, and evidence production.
