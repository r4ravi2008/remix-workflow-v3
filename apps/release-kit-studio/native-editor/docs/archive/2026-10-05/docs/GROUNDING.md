# Current execution boundary

The earlier application uses Effect schemas in `editor/project.ts` and an agent CLI in `agent/editor-cli.ts`.
The project schema fixes the frame rate at 24 and limits a project to six release outputs.
Those limits belong to the release-kit product profile.
They do not apply to the new general editing kernel.

The old CLI discovers schemas locally.
Its remote calls pass through `agent/editor-request.ts` into `editor/api.ts`.
The Cloudflare service owns tenant-scoped revisions and render intents.
`editor/render-coordinator.ts` coordinates execution.

The old `editor/engine` renderer is Python and FFmpeg.
Its receipts do not verify any Rust implementation.
The newer `agent/editor-local.mjs` standalone path also selects that old renderer.
The new CLI must have an independent executable path.

The read-only trace confirmed `editor-local.mjs:197` creates a `local-python-ffmpeg` renderer map.
`editor/local/adapters.ts:333` starts `editor/engine/server.py`, which calls `editor/engine/engine.py`.
The setup path also needs FFmpeg.
`agent/editor-cli.ts:445` has a Python archive verifier.
The native command path cannot reuse those execution adapters.

The current human requirements replace that kernel choice.
Rust owns editing and systems-level processing.
The user separated all Effect and UI adapters from the native editor.
Rust owns the direct agent CLI.
CLI discovery and execution come before UI work.

The new implementation must not call FFmpeg.
It must not link libav or silently use the old engine as a fallback.

Local tests come first.
The eventual hosted control service remains a separate Cloudflare Worker.

At the initial trace, the Git checkout contained the application as untracked files.
Git history cannot establish the old application's rationale.
The supplied conversation and the earlier architecture document explain the earlier hosted service boundary.
External issue, chat, analytics, and infrastructure searches cannot resolve the explicit current technology choice.
No production media, active Resolve project, cloud resources, or GPU work are needed for this foundation.

## Earlier ownership experiment

1. Produce an architecture and bounded first implementation contract.
2. Compare two designs with different ownership decisions.

Candidate A evaluates a Rust-authoritative command kernel with an Effect CLI over a process protocol.
Candidate B evaluates an Effect-authoritative project service with Rust processing operations.

Each candidate includes these details:

- Caller usage, core types, and module ownership.
- Error and retry behavior, and verification commands.
- Unsupported capability behavior and rejected alternatives.

Score each criterion from zero to five.

1. The design enforces no FFmpeg and distinguishes actual native processing from future codec work.
2. One module owns each invariant. Rust and Effect do not keep different timeline semantics.
3. An agent discovers schemas, executes commands, recovers from errors, and receives structured evidence.
4. Local execution works independently of Cloudflare. The future Worker does not claim to execute native Rust processes in an isolate.
5. The first unit has a reproducible byte-level artifact check and honest feature progress.
6. Poteto workflows have small owned modules, isolated tasks, and saved acceptance evidence.

## Rust-first grounding

The user later requested a standalone Rust implementation.
Effect belongs only in a separate future application.
The previous documents made the Effect CLI mandatory.
The Rust process already owned all editing behavior.

The updated architecture compares a single Rust library/binary package with separate core and CLI crates.
The two-crate design keeps the core reusable by a future desktop app without process framing or UI dependencies.

Local merge semantics depend on native revision rules.
Hosted tenant authorization remains an application dependency.

The optional UI capability records React, Tauri, and Foldkit as candidates.
It does not select one.
The direct Rust CLI owns a bounded watchdog.
The library does not exit its host process.
Agents can terminate the CLI directly and reconcile the original project-scoped intent.
