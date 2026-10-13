# Standalone Rust native editor

The editor is a general media editor with one-to-one DaVinci Resolve feature behavior as its reference.
Agents use the Rust library or the direct Rust CLI.
Release Kit is one optional workflow built on the editor.

The current Rust implementation is a bounded P0 foundation.
It supports local project revisions, stable intents, one visual track of solid RGBA clips, CPU PNG frames, and artifact verification.
Eight CORE families are implemented, and 73 of the 81 catalog families remain planned.
No capability has a trusted `verified` state in the current ledger.

## Start here

- [AGENTS.md](AGENTS.md) gives the agent entry path and ownership rules.
- [docs/PROGRESS.md](docs/PROGRESS.md) gives measured implementation state.
- [docs/SPEC.md](docs/SPEC.md) gives the normative protocol, storage, identity, and acceptance contract.
- [docs/FEATURES.md](docs/FEATURES.md) gives scenario-first navigation for all 81 feature families.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) gives crate boundaries and current source facts.
- [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) gives the P0 through P7 sequence.
- [docs/TASKS.md](docs/TASKS.md) gives the short implementation backlog.
- [docs/WORKFLOW.md](docs/WORKFLOW.md) gives the feature implementation procedure.
- [docs/VERIFICATION.md](docs/VERIFICATION.md) gives the development verifier commands and evidence rules.
- [docs/CLI-EXAMPLES.md](docs/CLI-EXAMPLES.md) gives direct CLI examples.
- [docs/HISTORY.md](docs/HISTORY.md) indexes archived native-editor records.

## Build and test

Historical `.runs/` paths in these documents refer to Mac-local evidence retained
outside Git. A fresh clone should run its own verifier and use that new receipt.

Run these commands from `apps/release-kit-studio/native-editor`.

```sh
cargo build --workspace --locked
cargo test --workspace --locked
cargo test --workspace --locked --features test-hooks
cargo clippy --workspace --all-targets --locked -- -D warnings
```

Build the development verifier separately.

```sh
cargo build --locked -p editor-devcheck --bin native-editor-check
target/debug/native-editor-check architecture
target/debug/native-editor-check full
```

The `architecture` mode checks ownership and source policy.
The `full` mode also exercises the current P0 path.
The latest measured implementation state is in [docs/PROGRESS.md](docs/PROGRESS.md).
The 2026-10-05 documentation cleanup result is in .runs/product-contract-1791264756707/reports/product-writer.md in `.runs/product-contract-1791264756707/reports/product-writer.md`.

## Use the direct CLI

The binary is `target/debug/native-editor`.
It does not need Bun, Node, Effect, a browser, Cloudflare credentials, Resolve, or a GPU.
Use [docs/CLI-EXAMPLES.md](docs/CLI-EXAMPLES.md) for the current command sequence.

The six current tools are `engine.capabilities`, `project.create`, `project.inspect`, `project.commit`, `frame.render`, and `artifact.verify`.
Planned features remain visible in the capability ledger and return an unsupported-capability error.

## Keep adapters separate

The Rust library and CLI own native edit semantics, storage, frame output, and artifact integrity.
Effect and UI adapters are separate future applications.
They can call the generated Rust contract or coordinate hosted workflows later.
They do not own native timeline semantics or direct access to the SQLite store.

Do not add FFmpeg executables, libav dependencies, bindings, or hidden fallback renderers.
Do not treat the historical Bun, Python, Cloudflare, or FFmpeg editor as a native implementation.

The optional Release Kit profile has separate source bindings, output targets, and creative review gates.
Its six outputs do not define the general editor API or native P0 acceptance.
