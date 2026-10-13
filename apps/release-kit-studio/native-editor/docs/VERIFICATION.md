# Verify the native editor locally

The Rust development verifier checks repository rules and documented P0 outcomes.
The verifier is separate from `native-editor verify`, which checks one project artifact.
Release Kit remains an optional workflow and does not change this scope.

## Run the verifier

Run these commands from the `native-editor` directory.
Rust, Cargo, rustfmt, clippy, Node, and Python 3 are development prerequisites.
Node runs document checks.
The editor runtime does not need Node.

1. Build the development executable.

    cargo build --locked -p editor-devcheck --bin native-editor-check

2. Run architecture checks.

    target/debug/native-editor-check architecture

3. Run full checks before a native code handoff.

    target/debug/native-editor-check full

The verifier checks the checkout used for the build.
Build again after you change checkouts.
The command returns one JSON summary.
Read the report path from that summary.

| Exit | Meaning |
| --- | --- |
| `0` | Every required check passed |
| `1` | At least one check failed |
| `2` | Required work is incomplete without a failed check |
| `64` | The command does not match a supported mode |

Each invocation creates a separate directory under `.runs/verification`.
The verifier has no flag that skips checks or promotes features.

The whole run has a 15-minute deadline.
Cargo stages have 3-minute deadlines.
Document and runtime probes have 30-second deadlines.
Tool-version probes have 15-second deadlines.
Each stdout and stderr log has an 8 MiB limit.
A truncated log cannot produce a pass result.

## Read the report

Architecture mode checks ownership, source inventory, dependencies, capability state, documents, and failure fixtures.
Architecture mode does not execute editor operations.
Full mode adds format checks, clippy, default acceptance, test-hook acceptance, fresh builds, and artifact checks.

The verifier compares 16 CORE A/B cases with explicit expected results.
The full mode records current observations for the eight implemented CORE families.
The 73 planned families remain unobserved.

Read each case's expected result, actual observation, mismatch, and evidence path.
Expected values and case bindings come from `docs/features/intent-contracts.json`.
Contract adequacy remains a separate human review.
Technical comparison cannot grant contract adequacy.

The report preserves command arguments, environment overrides, exits, logs, and file hashes.
Default and test-hook builds use separate targets and evidence directories.
Runtime discovery must match the measured binary and schema identities.

PNG checks read actual bytes and pixels.
Altered outputs must fail artifact integrity checks.
Missing tools cannot count as passes.
Rejected-path symlink fixtures remain separate from evidence.
An inventory error produces an incomplete result and a saved report.

## Last passing snapshot

The last successful full runtime snapshot is report.json in `../.runs/verification/1791190183401588000-54565/report.json`.
It passed 22 of 22 required checks.
Its intent report records 16 CORE pass observations.
It records 73 planned families as unobserved.
It did not promote a capability.

The wrong-pixels negative report in `../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/report.json` compiled successfully.
The negative run passed 21 other checks.
It failed CORE-04-A and CORE-05-A.
Each case reported 4,096 wrong pixels.

The slow-reader failure in `../.runs/verification/1791185642606452000-304/report.json` and CORE-07-B failure in `../.runs/verification/1791185835787000000-4022/report.json` remain saved.
The old design and task records are indexed in [HISTORY.md](HISTORY.md).
The cleanup result and any later current full receipt are recorded in the cleanup summary in `../.runs/product-contract-1791264756707/SUMMARY.md`.
This page does not claim a post-cleanup full pass.

## Guardrails

- Runtime crates cannot import `editor-devcheck` or an application adapter.
- `editor-core` cannot spawn processes or terminate its host.
- Source and dependency checks reject FFmpeg, libav, and fallback renderers.
- Recursive inventory covers nested and disabled source files.
- The ledger cannot promote a feature to trusted `verified`.
- Reports and document receipts use separate run directories.
- Process groups and output limits bound an unresponsive child.

The Rust compiler catches type and privacy errors.
The verifier covers source rules and actual feature outcomes.
Neither check proves movie, audio, text, multilayer, GPU, hosted, playback, listening, or creative behavior.
A later source change needs a new run.
Historical pass receipts describe their original snapshots.

Use [GUARDRAILS.md](GUARDRAILS.md) for ownership and enforcement limits.
Use [INTENT-VERIFICATION.md](INTENT-VERIFICATION.md) for purpose and case evidence.
