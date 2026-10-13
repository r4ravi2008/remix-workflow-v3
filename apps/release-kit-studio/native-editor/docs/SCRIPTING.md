# Editor programmability

The editor needs programmable operations.
Its foundation does not need Lua.
Rust owns editing semantics and output.
Callers use the same typed command authority.
This document defines ownership.
It does not implement an embedded language.

## Three capabilities

| Capability | Owner | State |
| --- | --- | --- |
| Agent workflow automation | Direct Rust CLI and typed library API | Bounded P0 commands implemented |
| Animation expressions | Future Rust parameter evaluator | Planned FUSION-04 |
| Embedded workflow scripts | Optional separate Lua host | Architecture target. Not implemented or included in the 81-family runtime registry |

A workflow decides which edits to request.
An expression computes a value at a frame.
An effect processes pixels or samples.
These operations have different validation and performance requirements.

## Shared editing authority

The current CLI converts validated messages into `editor_core::Command` values.
The library validates semantics, applies transactions, and returns typed results.
Future UI and Lua adapters submit commands through the same authority.
Adapters never write the database, redefine intent identity, invent artifact receipts, or render through another backend.
The native discovery registry controls which operations exist.
A script cannot enable a planned operation.

The optional Lua host can embed the Rust library or call the CLI.
Both choices need compatibility tests before adoption.
The design does not select a binding library or Lua version.
The native library must remain usable without Lua, Effect, a UI, or a network account.

## Planned animation expressions

FUSION-04 owns a bounded expression grammar and evaluator in Rust.
Expressions read declared frame time, parameters, and measured response data.
Expressions cannot access files, make network calls, mutate projects, or execute processes.
Expressions must produce finite values with bounded evaluation cost.

A future music-video expression can calculate background brightness from a measured bass envelope.
The frame index and declared source binding define the result.
A different frame-preview order must not change accepted values.
The design does not select the grammar or functions.
Example formulas describe the design.
They are not executable CLI syntax.

## Optional Lua workflow host

A future script invocation needs the script content hash, API version, project identity, and expected revision.
The invocation also needs declared inputs and resource limits.
The host maps script calls to available Rust commands.
Each mutation keeps a stable intent.
Before a retry submits another edit, the script must inspect completed operations.

A script is not one implicit database transaction.
Multi-command atomicity needs an explicit native transaction contract.

CPU-intensive and GPU-intensive media operations remain in Rust operators.
Lua can assemble commands, parameters, or graphs.
Lua cannot become an alternative pixel renderer.

Filesystem and network permissions belong to the script host.
Those permissions need a separate execution policy.
Measurements must prove that the host enforces instruction and memory limits before the host accepts tenant-supplied scripts.
This architecture does not declare a sandbox or permit untrusted hosted scripting.

## Resolve compatibility

Lua support does not reproduce the Resolve API.
Resolve scripts depend on object names, methods, node types, behavior, and project formats.
Compatibility needs a supported API map and a real script corpus.
Unsupported calls must fail with named reasons.
The editor does not claim Resolve script compatibility.

## Future acceptance

1. Compare equivalent CLI, Rust-library, and Lua-host requests for identical typed results and revisions.
2. Reject unavailable commands without a change to project state.
3. Retry a partially completed workflow. Stable intents must prevent duplicate edits.
4. Reject direct database access, substituted receipts, and fallback rendering.
5. Enforce instruction and memory limits on a script that loops or exceeds its size limit.
   The limits must protect accepted revisions.
6. Measure expression values in forward, reverse, and repeated frame order against independent expected values.

The [development verifier](VERIFICATION.md) checks current repository and P0 behavior.
It cannot verify future scripting until the runtime and its acceptance corpus exist.
