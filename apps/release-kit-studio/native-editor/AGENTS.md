# Native editor agent entry point

This directory contains the standalone Rust editor library, direct Rust agent CLI, and development verifier.
The product targets one-to-one DaVinci Resolve feature behavior for general media projects.
Release Kit is one optional workflow that uses the editor.

## Read the contract first

1. Read [README.md](README.md) for the local entry path and commands.
2. Read [docs/PROGRESS.md](docs/PROGRESS.md) for measured implementation state.
3. Read [docs/SPEC.md](docs/SPEC.md) before a runtime change.
4. Read [docs/FEATURES.md](docs/FEATURES.md) and the assigned feature document before a feature change.
5. Read [docs/WORKFLOW.md](docs/WORKFLOW.md) for the implementation and acceptance procedure.

Use [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for crate ownership.
Use [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for phase boundaries.
Use [docs/TASKS.md](docs/TASKS.md) for the current implementation backlog.
Use [docs/VERIFICATION.md](docs/VERIFICATION.md) for development checks and evidence.
Use [docs/INTENT-VERIFICATION.md](docs/INTENT-VERIFICATION.md) for creator scenarios and acceptance limits.

## Keep ownership clear

| Owner | Scope |
| --- | --- |
| `editor-core` | Typed edit semantics, SQLite state, revisions, native frame output, receipts, and artifact verification |
| `editor-cli` | Direct process arguments, JSON framing, schemas, deadlines, discovery, demo, progress, and exit codes |
| `editor-devcheck` | Development checks, bounded subprocesses, source policy, and evidence reports |
| Future applications | Effect orchestration, UI, remote adapters, authentication, and hosted deployment |

Keep the Rust library process-free.
Keep the runtime crates independent from `editor-devcheck`.
Keep Effect and UI adapters outside this directory.
Do not add FFmpeg executables, libav dependencies, bindings, or fallback renderers.

## Change and verify

1. Choose the feature ID and read its behavior contract.
2. Record the creator scenario, preconditions, expected result, acceptance cases, and non-goals.
3. Change the owner Rust crate and its acceptance tests.
4. Run the workspace checks from [README.md](README.md).
5. Run `target/debug/native-editor-check architecture` for ownership or document changes.
6. Run `target/debug/native-editor-check full` before a native implementation handoff.
7. Keep `planned`, `implemented`, and `verified` separate.

Measured output, frame inspection, playback, listening, and creative approval are separate evidence states.
Do not claim a feature or workflow complete from a queue, a build, or a document check alone.

## Optional workflow and history

The Release Kit profile has its own source bindings, output dimensions, review gates, and acceptance record.
It does not define the editor API or the native P0 completion gate.

Use [docs/HISTORY.md](docs/HISTORY.md) to find archived design, review, task, and baseline records.
