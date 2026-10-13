# Verification ownership and current gaps

The Rust editor before these changes has two ownership boundaries.
`editor-core::Editor::execute(Command)` accepts typed editing operations and returns typed results.
`editor-cli` validates JSON envelopes and exposes Rust-derived schemas.
It measures its executable.
It owns process deadlines and exits.
The compiled registry exposes six tools and eight bounded CORE families.

`protocol::progress` derives implemented or planned state from that registry.
It clears evidence.
A saved pass report cannot enable a tool or promote a family to verified.
The current native renderer supports one solid RGBA track and PNG output.

## Actual pre-change checks

The baseline ran both document checkers and `cargo test --workspace --locked`.
All three commands exited zero.
The default acceptance suite passed 29 tests.
The commands, stdout, stderr, and hashes are saved under [.runs/guardrail-baseline](../.runs/guardrail-baseline).

The document checkers verify structure and references.
They explicitly exclude runtime verification.
Rust acceptance executes actual CLI processes and checks source-bound PNG bytes, command intents, revisions, failures, and process behavior.
Test hooks add interruption experiments.
They do not prove physical power-loss behavior.

## Observed enforcement gaps

`p0_runtime_policy` changes source to lowercase before a search for mixed-case `Command::new(`.
That search cannot match.
The test also reads only immediate Core source files and only CLI main.rs.

Nested modules, additional targets, and build scripts need a complete inventory.
Package-name checks alone do not establish crate ownership or aliased dependency identity.

The document scripts overwrite fixed receipts.
Thus, concurrent runs share output files.
Separate manual Cargo commands can leave a hook-enabled executable in the shared target directory.
Saved observations lack one reproducible current-build driver with bounded process control and an evidence audit.

## Constraints retained

Development verification must remain outside the editing library.
Production project state is not a verification workspace.

Every run needs separate outputs.
Every run also needs separate default and hook targets.
Missing required tools and failed checks cannot produce a pass verdict.

Current-build identity and measured output take priority over historical pass summaries.
Lua, Effect, UI, hosted orchestration, codecs, and GPU work remain separately owned future capabilities.
