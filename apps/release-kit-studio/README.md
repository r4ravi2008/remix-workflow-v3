# Release Kit Studio

This repository contains a standalone Rust media editor and an optional Release Kit application.
The Rust editor is the current product path for general media projects.
The Release Kit application is a separate workflow profile.

## Start with the native editor

Read these documents before you change native behavior:

- [native editor agent map](native-editor/AGENTS.md)
- [native editor README](native-editor/README.md)
- [native editor specification](native-editor/docs/SPEC.md)
- [native feature catalog](native-editor/docs/FEATURES.md)
- [native implementation phases](native-editor/docs/IMPLEMENTATION.md)
- [native workflow](native-editor/docs/WORKFLOW.md)
- [native CLI examples](native-editor/docs/CLI-EXAMPLES.md)
- [native progress](native-editor/docs/PROGRESS.md)

Run the native checks from `apps/release-kit-studio/native-editor`:

```sh
cargo build --workspace --locked
cargo test --workspace --locked
cargo test --workspace --locked --features test-hooks
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo build --locked -p editor-devcheck --bin native-editor-check
target/debug/native-editor-check architecture
target/debug/native-editor-check full
```

The direct agent binary is `target/debug/native-editor`.
The development verifier is `target/debug/native-editor-check`.
The direct binary does not need Bun, Node, Effect, Foldkit, a browser, Cloudflare credentials, Resolve, or a GPU.

The current native registry exposes six runtime tools:

- `engine.capabilities`
- `project.create`
- `project.inspect`
- `project.commit`
- `frame.render`
- `artifact.verify`

The current P0 path stores local SQLite revisions and stable command intents.
It renders one non-overlapping solid RGBA visual track to CPU PNG frames.
It verifies stored artifact bytes against bound receipts.
It does not ingest movie files or render native video codecs.
It does not process audio, shape Indic text, manage color, compose layers, or use a GPU.

The capability ledger has 81 initial families.
Eight `CORE` families are implemented.
Seventy-three families are planned.
Zero families are promoted to `verified`.
Use [native `SPEC.md`](native-editor/docs/SPEC.md) and [native `FEATURES.md`](native-editor/docs/FEATURES.md) as the contract sources.

The P0 path exposes these limits:

| Limit | Value |
| --- | ---: |
| Input JSON | 1 MiB |
| Output JSON | 4 MiB |
| Canvas axis | 2,048 pixels |
| Canvas pixels | 4,194,304 |
| Timeline frames | 10,000,000 |
| Clips | 10,000 |
| Default CLI deadline | 30 seconds |

The native implementation does not use FFmpeg executables, libav dependencies, Python renderers, or hidden fallback paths.
The earlier Bun, Python, and FFmpeg editor remains historical application material.

## Use the optional Release Kit application

The optional TypeScript application uses Foldkit `0.165.0`, Effect `4.0.0`, and Alchemy `2.0.0-beta.80`.
It contains the Foldkit UI, Release Kit workflow, Cloudflare adapters, GPU transport, and local Resolve pilot code.
Those components do not implement native editor semantics.

Run the optional application from `apps/release-kit-studio`:

```sh
bun install
bun run dev
bun run check
bun run build
```

Read the optional workflow documents:

- [Release Kit product profile](PRODUCT.md)
- [Foldkit application rules](FOLDKIT.md)
- [Release Kit agent runbook](agent/README.md)
- [Tailscale and Resolve pilot runbook](worker/README.md)

The profile accepts a song, exact native-script lyrics, and an artist profile.
It names six required output IDs when the profile runs: `film`, `short-1`, `short-2`, `short-3`, `thumbnail`, and `artwork`.
The profile does not define the native editor API, feature ledger, timeline model, or P0 gate.
No completed native six-output Release Kit is established.

## Read the source tree by role

| Path | Role |
| --- | --- |
| `native-editor/` | Current Rust library, direct agent CLI, and development verifier |
| `src/` | Optional Foldkit and Effect application state, views, and browser entry |
| `editor/` | Optional TypeScript and legacy Cloudflare editor adapters |
| `agent/` | Optional Release Kit production agent and source-bound workflow helpers |
| `worker/` | Optional local Resolve and Tailscale pilot helpers |
| `migrations/` | Optional application database migrations |
| `public/` | Optional application assets and asset provenance files |
| `docs/` | Application receipts, checks, and current evidence indexes |
| `docs/archive/2026-10-05/` | Archived product, operator, and legacy editor documents |

The Python renderer under `editor/engine/` is a legacy path.
Its receipts apply to that renderer and its Cloudflare application.
They do not prove Rust capability, Resolve parity, hosted deployment, playback, listening, or creative acceptance.

Playback, listening, frame inspection, human contract review, and creative approval are separate evidence states.
Read the implementation owner and evidence state before you use any receipt.
