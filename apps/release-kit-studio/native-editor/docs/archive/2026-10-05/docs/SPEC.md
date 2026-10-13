# Native editor specification

Status is an implementation contract. The user authorized the Rust-first local implementation on 2026-10-04.
PROGRESS.md and acceptance evidence record runtime completion separately.
Version 3 specifies an independently usable Rust library and direct Rust agent CLI.

Effect and UI adapters are separate future applications. They are not native editor dependencies.
This version replaces the previous renderer choice. Historical receipts remain evidence only for their original implementation.

## Product contract

The release-kit product accepts a song, native-script lyrics, and an artist profile.
The director combines cinematic scenes, lyric-led passages, and music-reactive environments in one film.
The release profile produces a landscape film, three vertical excerpts, a thumbnail, and square artwork.
The profile defines those output counts and dimensions. The editing kernel supports independent projects and timelines.

The initial release profile retains these targets.

| Output | Target | Required source binding |
| --- | --- | --- |
| Film | 1920 by 1080, 24 fps, full canonical song, stereo MP4 | Exact master hash and measured song duration |
| Three vertical promos | 1080 by 1920, at most 30 seconds each | Declared source intervals and exact song hash |
| Thumbnail | 1920 by 1080 JPEG | Accepted visual direction and source references |
| Artwork | 1920 by 1920 JPEG | Accepted artist identity and visual direction |

The intended movie profile uses H.264 video and AAC audio.
Its platform-specific native encoder remains unresolved. Unsupported encoding fails the release profile before the scheduler starts work.
The kernel's general frame rate and timeline model do not inherit the profile's 24 fps constraint.

Agents discover capabilities, inspect schemas, submit typed commands, inspect results, and verify actual artifacts.
Local execution requires neither a browser nor Cloudflare credentials.
An optional UI uses the same editor commands and evidence.
React, Tauri, and Foldkit remain application choices. No UI framework is selected for the native editor.

## Technology ownership

Rust owns timeline semantics, media buffers, native codecs, composition, color calculations, audio DSP, and artifact measurements.
Rust also owns the direct CLI, native command protocol, local process limits, and local acceptance checks.
The Rust library is usable without its CLI and without JavaScript or a UI.
Effect can own future application orchestration, remote service adapters, and workflows for the UI outside this directory.
A desktop app or native host can embed the library or invoke the CLI.

A browser UI calls a separate adapter connected to a native host. It cannot directly launch a native process.
No Effect, Node, Bun, browser, or Cloudflare dependency enters the native editor. Alchemy remains a future infrastructure choice.

Cloudflare Workers own hosted authorization and coordination. Native Rust execution requires a separate native process host.
Small portable calculations can use Rust WebAssembly in Workers after memory and execution-limit checks.
Cloudflare Containers are one possible CPU process host. GPU hosting remains a separate capability decision.

FFmpeg executables, libav dependencies, FFmpeg bindings, and hidden fallback paths are prohibited in the new implementation.
The codec registry reports platform, codec, pixel format, bit depth, and decode or encode support separately.
Unsupported requests return a structured error before execution.

The architecture uses [Cloudflare's WebAssembly runtime documentation](https://developers.cloudflare.com/workers/runtime-apis/webassembly/)
and [Containers documentation](https://developers.cloudflare.com/containers/).
These sources describe hosting options. They do not establish a deployed editor or GPU availability.

## Data and command invariants

The project model uses rational frame rates and integer frame or sample positions.
An interval stores a start and a positive duration. Floating-point seconds do not identify edit boundaries.
Project revisions are immutable. A mutation includes an expected revision and a stable intent identifier.

An identical intent replay returns its original result. The same intent with different content returns a conflict.
Intent identity is the pair `(projectId, intentId)`. Identical intent strings in different projects cannot collide.
Concurrent mutations compare the expected revision inside one storage transaction.

Rust types define the native protocol. Generated JSON schemas expose transport shapes.
The Rust CLI uses the same authoritative types. Optional application adapters import generated schemas later.
A future Effect adapter cannot maintain a second timeline reducer.

Before publication, static TypeScript library types need a build-time generator with separate verification.
Semantic validation belongs to the Rust domain boundary. Syntax validation also occurs at the untrusted process boundary.

An asset reference binds content hash, byte count, media type, and measured properties.
A rendered artifact binds project revision, command intent, renderer version, output hash, and measured dimensions or duration.
Verification reads stored bytes. Render completion does not imply motion review, listening, or creative acceptance.

The first local revision store is not a multi-tenant authorization service.
The hosted adapter must bind tenant identity from authentication and never trust a caller-supplied tenant identity.
Hosted tests must cover isolation, revocation, cancellation, stale attempts, and receipt substitution before production use.

## Capability coverage

[capabilities.json](../capabilities.json) maps Resolve capability families to intended owned modules and acceptance criteria.
The mapping covers Media, Cut, Edit, Fusion, Color, Fairlight, Photo, Deliver, collaboration, AI, and extension interfaces.
Hardware integration and desktop interaction parity remain explicit future work.
The reference baseline is [DaVinci Resolve 21](https://www.blackmagicdesign.com/products/davinciresolve), checked on 2026-10-04.

This is a public capability mapping. It does not reproduce proprietary algorithms or prove identical output.
The ledger does not claim a complete inventory of all individual menu items or effect parameters.
Each family requires a detailed behavior contract and reference corpus before implementation.

Feature state is one of `planned`, `implemented`, or `verified`.
A `verified` entry requires a saved acceptance receipt from the current implementation.
Receipts identify the implementation version, exercised command, input hash, output hash, and verifier.
No old Python renderer receipt can promote a Rust capability.

`capabilities.json` is authored planning metadata. It defines feature IDs, primary owners, dependencies, and acceptance criteria.
Its `state` and `evidence` fields are a generated progress snapshot once runtime implementation begins.
The Rust binary publishes native implemented feature IDs and its build identity from the compiled registry.

A future application adapter publishes its own feature IDs and build identity. It cannot declare native tools executable.
The progress checker joins each owner's registry with planning metadata and current acceptance receipts that passed.
An absent registry implementation means `planned`. A compiled implementation without acceptance that matches means `implemented`.

Only acceptance-case receipts that pass and match the build, protocol, schema, and feature permit `verified`.
The checker rejects a stored snapshot that differs from this derived state.
Neither an edited ledger nor a forged receipt can enable a compiled tool.
Evidence promotion reruns the trusted acceptance checker. It does not trust caller-supplied flags with a pass result.

Before the checker writes its progress snapshot, it compares current output bytes and build identities.

## Detailed feature guide

[FEATURES.md](FEATURES.md) provides scenario-first navigation for all 81 mapped capability families.
Each family has a proposed behavior contract, implementation pieces, and named verification criteria.
These documents do not establish implemented support, full Resolve control parity, or a tested corpus for future capabilities.
Only the compiled registry and current runtime evidence establish native availability.

## Development guardrails

The separate Rust `editor-devcheck` binary verifies repository ownership and current-build P0 behavior.
It is outside the runtime process protocol. Editing tools and registered-artifact verification remain in `editor-cli`.
Architecture mode proves document and source structure. Full mode adds actual native execution and independent artifact checks.

Each run isolates default and test-hook targets, state, logs, and report paths.
Missing tools, failed commands, and incomplete required checks cannot produce a result that passes.
Development reports do not promote a family to `verified` or replace trusted acceptance-case authority.
Feature acceptance starts with creator purpose, a concrete scenario, and declared observable outcomes.
Named cases bind those outcomes to actual CLI requests, results, state, and artifacts.

The development report compares independent expectations with measured observations for implemented CORE cases.
Planned feature cases remain unobserved. Successful compilation or document coverage cannot satisfy those cases.
Contract adequacy, playback, listening, and creative review remain separate judgments.
[INTENT-VERIFICATION.md](INTENT-VERIFICATION.md) defines that acceptance chain and its limits.

[GUARDRAILS.md](GUARDRAILS.md) defines the ownership choice. [VERIFICATION.md](VERIFICATION.md) documents measured CLI behavior.

## Scripting architecture

CLI automation, animation expressions, and embedded workflow scripts are separate capabilities.
The direct CLI supplies the current bounded automation interface. FUSION-04 plans a Rust expression evaluator.
An optional future Lua host calls the same typed API outside `editor-core`.
No Lua dependency, embedded script execution, or Resolve Lua compatibility is currently supported.
[SCRIPTING.md](SCRIPTING.md) defines the planned boundary and acceptance conditions.

## Layered composition target

[LAYERS.md](LAYERS.md) defines the planned multi-track stack, timed visibility, masks, alpha, graphs, and reference-frame checks.
P2 owns timeline tracks and time mapping. P3 owns masks, blend modes, and composition graphs.

The current P0 format remains a single non-overlapping visual track. It cannot be presented as layered-video support.
A later UI edits the Rust model. The UI cannot duplicate composition semantics.

## First local acceptance unit

The first unit proves command discovery, schema discovery, project creation, typed timeline mutation, revision conflicts, and stable-intent replay.
It also proves a CPU-rendered still frame with independent byte verification.
Procedural solid clips are a deliberately bounded input format.
Native movie ingest, video encoding, sound, Indic text shaping, color management, GPU composition, and the six-output kit remain unimplemented.

The acceptance check exercises the CLI through real child processes.
The check must reject malformed requests, stale revisions, changed intent content, unsupported tools, and altered output bytes.
The check must inspect a known pixel, not only an output filename or process exit code.
The finalized acceptance matrix requires every expected pixel and alpha value in the small reference frame.

## Execution limits

Local requests and project state have explicit byte limits.
Output resolution and frame counts have explicit resource bounds.
The native process writes protocol responses to stdout and diagnostics to stderr.
The Rust CLI watchdog limits execution and terminal-result selection. A timeout selects one process-timeout response and exits.

After the CLI selects a result, it completes that response without a second writer or an arbitrary flush cutoff.
The agent that invokes the CLI owns the total process timeout. This timeout includes blocked stdout. An interrupted or partial response is a process failure.
The reusable library cannot terminate its host. An agent can also terminate the direct process.

Process termination leaves SQLite transactions recoverable under the original intent. A later adapter owns only its child-process lifetime.
Paths are local operator input in the development CLI. They are not accepted from hosted tenants.

## Agent command contract

The direct executable is `native-editor`. The build and verification commands are documented in ../README.md.
The operations below belong to the Rust binary. No package-script wrapper is required.

| CLI operation | Result | Side effect |
| --- | --- | --- |
| `tools` | Implemented tool names, descriptions, limits, and current protocol version | None |
| `schema <tool>` | Rust-generated input and output JSON schemas | None |
| `progress` | Full capability ledger with separate evidence state | None |
| `call <tool> <request.json> --state <directory>` | Build the current envelope around a tool input file, then return one result | Depends on the tool |
| `call --state <directory>` | Read one complete protocol envelope from stdin and return one result | Depends on the tool |
| `demo <new-directory>` | Project, request files, a native PNG preview, and measured receipt | Creates an isolated local example |
| `verify <project-id> <artifact-id> --state <directory>` | Fresh measurement of the registered artifact | Reads output bytes |

The CLI emits one JSON document on stdout. Diagnostics use stderr.
Exit code 0 means success. Exit code 2 means a rejected domain request.
Exit code 1 means process, installation, storage, or protocol failure.
The CLI never retries a mutation with a new intent automatically.

The initial Rust tools are `engine.capabilities`, `project.create`, `project.inspect`, `project.commit`, `frame.render`, and `artifact.verify`.
Planned capabilities remain visible through `progress`. They cannot be invoked successfully.
An unknown tool and a known unimplemented tool return distinct error codes.

The compiled tool registry determines executability. A change to the progress ledger cannot enable a command.
`engine.capabilities` is stateless. It does not create a project database.

`project.inspect` requires a project ID. The revision is optional. Without a revision, the command reads the current snapshot.

This is a proposed create request.

```json
{
	"projectId": "local-example",
	"intentId": "create-v1",
	"name": "Local native example",
	"timeline": {
		"frameRate": { "numerator": 30000, "denominator": 1001 },
		"durationFrames": 60,
		"canvas": { "width": 64, "height": 64 }
	}
}
```

The initial edit command accepts a transaction of typed edits.

```json
{
	"projectId": "local-example",
	"expectedRevision": 0,
	"intentId": "background-v1",
	"edits": [
		{
			"kind": "clip.put",
			"clip": {
				"id": "background",
				"startFrame": 0,
				"durationFrames": 60,
				"source": { "kind": "solid", "rgba": [12, 25, 48, 255] }
			}
		}
	]
}
```

A successful commit returns revision 1, a project content hash, and `replayed: false`.
An identical replay returns the original revision and hash with `replayed: true`.
The replay check precedes the current-revision check. A completed old intent can replay after later edits.
A transaction either applies every edit or applies none.

A commit contains at least one edit. An empty edit transaction fails `invalid_input`. The revision stays unchanged.

The initial frame request has no caller-supplied output path.

```json
{
	"projectId": "local-example",
	"revision": 1,
	"intentId": "frame-zero-v1",
	"frame": 0,
	"format": "png-rgba8"
}
```

The renderer generates a private relative artifact path inside the selected state directory.
The receipt contains a project ID, artifact ID, project content hash, revision, intent ID, and renderer version.
It also contains byte count, SHA-256, width, height, pixel format, and frame position.
`artifact.verify` accepts the project ID and artifact ID. The verifier resolves the authoritative receipt from that project's local store.
An agent cannot supply a different expected hash or arbitrary file path to authorize altered bytes.

## Content identity

Structured hashes use UTF-8 bytes from RFC 8785 JSON Canonicalization Scheme. This document calls the scheme JCS.
Raw artifact and source-media hashes use exact file bytes without canonicalization.
Structured input rejects duplicate keys, nonfinite numbers, and integers outside the exact JavaScript range.
The kernel preserves Unicode text without implicit normalization or transliteration.

Canonicalization does not sort arrays. Timeline order remains part of the typed document.

| Fingerprint | Exact SHA-256 input |
| --- | --- |
| Command request | JCS of `{ identityVersion: 1, protocolVersion: 1, tool, input }`, including project, intent, and expected revision fields |
| Project snapshot | JCS of the complete versioned snapshot, including project ID, revision, name, frame rate, canvas, and clips |
| Schema contract | JCS of `{ protocolVersion: 1, tools }`, with tools sorted by name and each tool's complete input and output schemas |
| Future application adapter build | JCS of its sorted source-file path and SHA-256 manifest, dependency-lock SHA-256, and runtime version |
| Structured receipt | JCS of the complete versioned receipt before adding its own `receiptSha256` field |
| Artifact or source media | Exact stored bytes |

Rust computes authoritative request, project, and schema hashes. Future adapters use those values. Adapters do not reconstruct edit identity.
The independent acceptance checker uses a second JCS implementation and reference vectors.
The test corpus includes reordered object keys, escaped characters, native-script text, maximum allowed integers, and changed payloads.

A change to canonicalization or identity fields requires a new `identityVersion` and explicit migration behavior.
JCS follows [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785).

## Native domain shape

These Rust types describe the required ownership. They are sketches, not implementation files.

```rust
struct ProjectId(String);
struct IntentId(String);
struct ClipId(String);
struct Revision(u64);
struct FrameIndex(u64);
struct FrameCount(std::num::NonZeroU64);

struct FrameRate {
	numerator: std::num::NonZeroU32,
	denominator: std::num::NonZeroU32,
}

struct Interval {
	start: FrameIndex,
	duration: FrameCount,
}

enum VisualSource {
	Solid { rgba: [u8; 4] },
}

struct Clip {
	id: ClipId,
	interval: Interval,
	source: VisualSource,
}

enum Edit {
	PutClip { clip: Clip },
	RemoveClip { clip_id: ClipId },
}

enum Command {
	CreateProject(CreateProject),
	InspectProject(InspectProject),
	CommitProject(CommitProject),
	RenderFrame(RenderFrame),
	VerifyArtifact(VerifyArtifact),
}

enum StoredIntent {
	Pending { request_hash: Sha256 },
	Completed { request_hash: Sha256, result: StoredResult },
}
```

The first model has one non-overlapping visual track and procedural solid sources.
Empty timeline ranges render transparent black. Out-of-range frames fail.
Nonopaque solid pixels preserve alpha. No implicit color-management claim accompanies those raw RGBA values.

`clip.put` replaces a clip by its stored ID. `clip.remove` rejects an unknown ID.
Intervals use half-open semantics. A clip at frame 10 for five frames covers frames 10 through 14.

Two clips can touch at a boundary. Two clips cannot overlap in the initial single-track model.

Frame rates normalize by their greatest common divisor.
Before conversion to seconds or audio samples, the kernel uses checked integer arithmetic on frame positions.
The first kernel does not implement sample conversion. P2 requires a declared rounding rule and an independent sync corpus.

The public native operation is `Editor::execute(Command) -> Result<Execution, EditorError>`.
`Editor::open(stateRoot, config)` binds local storage, limits, and measured renderer build identity.
`Execution` carries a typed result and its replay flag. The library does not query process arguments or terminate the caller.

Storage protects revision and intent transitions. The frame renderer accepts a validated immutable snapshot.
The protocol adapter parses external JSON into domain commands. The domain does not depend on the transport envelope.

## Local storage and recovery

Each local project owns a separate SQLite database and artifact directory under its state root.
Rust owns snapshots, revisions, and intent records. Application adapters do not query or modify that database directly.
One transaction checks intent identity, compares the expected revision, and writes the new immutable revision.
Native artifact production uses a pending intent, a generated temporary path, atomic promotion, and a stored completed result.

Before a restart repeats computation, it inspects the unfinished intent and its source-bound artifact.
After remeasurement, an identical retry can adopt a completed output that matches the request.
A changed or corrupt completed output returns an integrity error. Recovery does not silently replace evidence.
Cancellation or process death never promotes a partial temporary file as a completed artifact.

SQLite transaction behavior agrees with the [SQLite transaction reference](https://www.sqlite.org/lang_transaction.html).
Power-loss recovery, interrupted writes, duplicate calls, and concurrent processes require acceptance tests.
The specification does not treat atomic rename alone as a complete crash-recovery proof.

Tools that mutate a project share that project's intent namespace.
`project.create`, `project.commit`, and `frame.render` bind the tool name as part of the request fingerprint.
The same intent across different tools causes a conflict. Read-only tools do not create intent records.

| Mutation | Duplicate and recovery contract |
| --- | --- |
| `project.create` | Identical intent returns the original revision-zero result. A different create intent for an existing project returns `project_exists`. Concurrent creates produce one durable project. |
| `project.commit` | Identical intent returns its original result, even after later revisions. An invalid transaction writes neither a revision nor a successful intent. |
| `frame.render` | Identical intent remeasures its completed artifact and returns the original result. A matching pending output can be adopted after verification. A missing pending output can be recomputed under the same intent. |

A render's pending record stores the immutable snapshot hash, revision, frame, format, and generated staging identity.
The renderer writes the staged file and synchronizes its file contents before atomic promotion.
After promotion, the renderer synchronizes the parent directory with the supported platform equivalent.
Completion records the measured receipt only after those durability operations succeed.
A power-loss recovery claim requires the platform to pass its acceptance experiment for durability behavior.

Before restart reconciliation adopts staged or promoted bytes, it checks this stored binding.
Two processes that claim the same pending intent cannot compute or promote results that conflict.
P0 first commits the pending record, then holds a SQLite `BEGIN IMMEDIATE` transaction during bounded frame production and completion.
The SQLite write lock is the process-safe ownership mechanism for that project.

Another writer returns `store_busy`. Process death releases the database lock and leaves the committed pending record available for reconciliation.
P0 deliberately blocks other mutations in that project during its bounded frame render.
Movie jobs with long runtimes require a separate leased-job state machine in P6.
Before the kernel adopts pending output, it regenerates deterministic frame bytes from the stored immutable request and snapshot.

The actual file must match those bytes, dimensions, pixel format, and renderer version before receipt completion.
Artifact encoding must be deterministic within one renderer build. A changed renderer build cannot adopt an older pending artifact implicitly.

Required interruption points cover these stages:

- Before the database transaction.
- During revision commit.
- After commit, before response.
- After pending render creation.
- While the renderer writes the file.
- After flush, before promotion.
- After promotion, before receipt commit.

The same original intent must converge at every point. A corrupt completed artifact remains a failure.

## Process protocol and errors

The initial process protocol has one bounded JSON request and response per invocation.
Rust receives input on stdin. After the process writes the response, it exits.
No daemon, HTTP listener, token, or shared GPU reservation is required for the first local unit.
Protocol negotiation includes version 1 and the generated schema hash.

The Rust CLI rejects malformed requests, mismatched protocol versions, excess fields, and oversized input.
Any future process adapter must reject extra responses, malformed messages, oversized output, and contradictory exit codes.

The exact request envelope has this shape.

```json
{
	"protocolVersion": 1,
	"requestId": "request-1",
	"expectedSchemaSha256": "<64 lowercase hexadecimal characters>",
	"tool": "project.commit",
	"input": {
		"projectId": "local-example", "expectedRevision": 0, "intentId": "edit-v1",
		"edits": [{ "kind": "clip.put", "clip": {
			"id": "background", "startFrame": 0, "durationFrames": 60,
			"source": { "kind": "solid", "rgba": [12, 25, 48, 255] }
		} }]
	}
}
```

`engine.capabilities` requires `expectedSchemaSha256: null` for initial discovery. Other tools require the discovered hash.
The displayed hexadecimal placeholder is explanatory. It is not a valid executable request.

The envelope and tool inputs reject undeclared fields. `requestId` follows the identifier rule and only correlates the reply.
The request fingerprint excludes `requestId` and handshake fields. It hashes the canonical command identity defined above.

The exact response is one discriminated envelope.

```json
{
	"protocolVersion": 1,
	"requestId": "request-1",
	"schemaSha256": "<actual schema hash>",
	"status": "success",
	"replayed": false,
	"result": { "projectId": "local-example", "revision": 1, "projectSha256": "<actual snapshot hash>" }
}
```

```json
{
	"protocolVersion": 1,
	"requestId": "request-1",
	"schemaSha256": "<actual schema hash>",
	"status": "error",
	"error": {
		"code": "revision_conflict",
		"message": "The expected revision differs from the current revision.",
		"retry": "inspect_then_rebase",
		"details": { "currentRevision": 1 }
	}
}
```

Success and error variants have disjoint fields. The response rejects undeclared fields.
`result` uses the generated schema for the invoked tool. `error.details` has a declared per-code schema.

An unreadable request returns `invalid_input` with `requestId: null`. The parser never invents a correlation ID.
Discovery returns kernel version, binary SHA-256, protocol and identity versions, schema hash, compiled tool descriptors, and limits.
The implementation measures the actual native executable for its build identity.

Rust exits with code 0 for a success envelope and code 2 for a structured domain-error envelope.
Rust uses code 1 for storage, installation, or internal failures, with a structured error when possible.
Expected contention such as `store_busy` is a domain error with exit code 2. Failed storage I/O is `storage_failure` with exit code 1.

A future process adapter must decode stdout even after exit code 2. It must not discard the typed domain error.
Missing, malformed, or contradictory stdout and exit-code combinations become a process or protocol failure.
The direct Rust CLI uses these exit-code classes itself.

| Error code | Required caller behavior |
| --- | --- |
| `invalid_input` | Correct the request. Do not retry unchanged input. |
| `unknown_tool` | Before you retry, discover tool names. |
| `unsupported_capability` | Inspect feature state. Do not select a fallback renderer. |
| `project_not_found` | Inspect the state directory or create the intended project. |
| `project_exists` | Inspect the existing project. Do not retry a different creation intent. |
| `revision_not_found` | Inspect available revisions. Do not substitute the current revision silently. |
| `artifact_not_found` | Inspect the requested project's artifacts. Do not verify an arbitrary filesystem path. |
| `revision_conflict` | Inspect the current revision. Submit a deliberate new edit intent. |
| `intent_conflict` | Preserve the intent's original content. Use a new ID for different work. |
| `store_busy` | Retry the identical intent with bounded backoff. |
| `storage_failure` | Preserve the original intent. Before you retry, diagnose local storage. |
| `artifact_integrity_mismatch` | Preserve evidence. Report the failure. |
| `protocol_mismatch` | Discover the current native protocol and schema before you submit the request again. |
| `process_timeout` | Inspect the original intent outcome before replay. |
| `process_interrupted` | Inspect the original intent before replay. |

Initial request size is at most 1 MiB. Initial response size is at most 4 MiB.
The initial canvas is at most 2048 pixels on either axis and 4,194,304 total pixels.
The initial project has at most 10,000 clips and 10,000,000 frames.
JSON integer values stay in the exact JavaScript integer range.

The native execution and result-selection deadline is 30 seconds by default. The CLI accepts a bounded operator deadline for local tests.
Response delivery is separate. A caller must drain stdout and enforce its own total process deadline.
Project, clip, and intent identifiers contain at most 80 ASCII letters, digits, underscores, or hyphens.

The first identifier character must be a letter or digit. Empty identifiers and path separators fail validation.
Limits are discovery metadata. An increase to a limit requires a resource measurement and a revised acceptance receipt.

## Acceptance matrix

Before the checker marks P0 verified, every case below must pass.

| Case ID | Case | Required observation |
| --- | --- | --- |
| P0-DISCOVERY | Tool discovery | Callers can invoke only implemented tools. Planned capabilities show the reason for their unavailable state. |
| P0-SCHEMA | Schema agreement | Rust emits Draft 2020-12 schemas from its types. The direct CLI rejects excess request fields. |
| P0-RATIONAL-RATE | Rational rate | A 30000/1001 project preserves exact numerator and denominator through restart. |
| P0-TRANSACTION | Transaction | Valid edits commit together. A later invalid edit leaves no partial revision. |
| P0-REPLAY | Intent replay | An identical request returns its original revision and hash without a second write. |
| P0-INTENT-CONFLICT | Intent reuse | The same intent with different content fails without mutation. |
| P0-STALE-REVISION | Stale edit | A stale revision fails and preserves the current project. |
| P0-CONCURRENT-EDIT | Concurrent edits | Two processes that target one revision produce one winner and one explicit conflict. |
| P0-CRASH-RECOVERY | Crash recovery | Termination before and after commit returns one durable result when the caller retries the original intent. |
| P0-NATIVE-PIXELS | Native pixels | An independent PNG decoder reads all expected RGBA pixels, dimensions, and alpha. |
| P0-RECEIPT-BINDING | Receipt binding | Output references the exact project hash, revision, frame, intent, and renderer version. |
| P0-TAMPER | Tampered output | A one-byte change fails artifact verification. |
| P0-FORGED-RECEIPT | Forged receipt | A new expected hash cannot authorize changed output bytes. |
| P0-RESOURCE-LIMIT | Resource limit | Oversized canvas and request fail before allocation or filesystem mutation. |
| P0-CANCELLATION | Cancellation | Termination of the direct Rust process during work releases its storage lock. Reconciliation of the original intent prevents duplicate completion. |
| P0-RUNTIME-POLICY | Runtime policy | Cargo dependencies and child-process invocation sites contain no prohibited renderer or libav path. |
| P0-CREATE | Project creation | Identical create replays revision zero. Different and concurrent create intents cannot create duplicate projects. |
| P0-RENDER-REPLAY | Render replay | Identical render remeasures the original artifact. Incomplete output uses the specified same-intent recovery. |
| P0-CLIP-BOUNDS | Clip semantics | Reject overlap and invalid intervals. Accept adjacent clips and preserve exact boundary pixels. |
| P0-PROTOCOL | Process boundary | Reject mismatched schema, excess fields, duplicate keys, malformed output, and contradictory exit codes. Decode domain errors from exit code 2. |
| P0-PROGRESS-AUTHORITY | Progress authority | Ledger edits and forged flags for a pass cannot enable tools or promote unmatched evidence. |

The repeatable check saves request hashes, process versions, project hashes, artifact hashes, and every case result.
The checker promotes only the capability IDs that cases with a pass result cover.
The first native still proof cannot promote a movie codec, audio feature, typography feature, or release-kit profile.

Acceptance evidence uses a distinct `acceptance-case` receipt. An artifact receipt cannot substitute for this receipt.

```json
{
	"receiptVersion": 1,
	"kind": "acceptance-case",
	"caseId": "P0-REPLAY",
	"featureIds": ["CORE-03"],
	"checkedAt": "<UTC timestamp>",
	"outcome": "VERIFIED",
	"engine": {
		"binarySha256": "<native executable hash>",
		"protocolVersion": 1,
		"identityVersion": 1,
		"schemaSha256": "<contract hash>"
	},
	"verifier": { "name": "native-acceptance", "version": 1, "sourceSha256": "<checker source hash>" },
	"inputs": [{ "role": "request", "path": "requests/replay.json", "sha256": "<exact request-file hash>", "bytes": 200 }],
	"outputs": [{ "role": "project-snapshot", "path": "outputs/snapshot.json", "sha256": "<exact evidence-file hash>", "bytes": 400 }],
	"assertions": [{ "id": "same-revision-on-replay", "passed": true }],
	"receiptSha256": "<JCS receipt hash>"
}
```

Placeholder hashes, timestamps, and byte counts illustrate the shape. The checker replaces them with actual measurements.
An outcome is `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`. Only `VERIFIED` can contribute to promotion.

Each feature declares its required case IDs. Each required case must pass for the current build and schema.
P0 case IDs are listed in the acceptance matrix and capability ledger.
Before the checker promotes verification, later families need a behavior contract, nonempty case IDs, and an acceptance corpus.

Future application-adapter cases also bind their own interface build hash. UI and hosted cases require the identity of their deployment or build.
Missing cases, changed verifier source, substituted evidence, and hash mismatches prevent promotion.
The checker hashes referenced evidence from disk. The checker never trusts only a receipt's byte count or pass flag.

Evidence paths are relative to the owned acceptance-run directory. Traversal, absolute paths, and symlink escapes fail verification.

## Rust-first implementation boundary

The completed specification run remains documented in TASKS.md.
The user subsequently authorized the independent Rust implementation and separated Effect and UI adapters.
The current implementation unit is CORE-01 through CORE-08. Runtime evidence remains separate from this contract.
Native codec SDK choice, GPU execution host, AI inference provider, and expanded collaboration semantics remain unresolved.

The implementation sequence includes dedicated experiments for these decisions. They do not require a placeholder production claim.

## Production acceptance

The product needs a full-song render from actual assets with all six outputs and source-bound receipts.
Technical verification, frame inspection, complete playback, listening, and creative approval remain separate states.
Before Pal Pal production resumes, its canonical source binding and review holds remain required.
