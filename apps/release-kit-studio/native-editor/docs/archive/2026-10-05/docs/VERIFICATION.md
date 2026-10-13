# Verify the native editor locally

The Rust development verifier checks repository guardrails and documented P0 creator outcomes.
[PROGRESS.md](PROGRESS.md) gives measured status and the exact observed source snapshot.
The verifier is separate from `native-editor verify`, which checks one registered project artifact.

## Build the verifier

Run these commands from `apps/release-kit-studio/native-editor`.
Rust, Cargo, rustfmt, clippy, Node, and Python 3 are development prerequisites.
Node runs documentation checks.
The editing runtime does not need Node.
Process-control tests currently invoke `/usr/bin/python3` for timeout fixtures, excessive-output fixtures, and descendant fixtures.

The verifier checks the checkout where you built it.
When you change checkouts, rebuild the verifier.

1. Build the development executable.

```sh
cargo build --locked -p editor-devcheck --bin native-editor-check
```

2. Run architecture checks.

```sh
target/debug/native-editor-check architecture
```

3. Before a native code handoff, run full checks.

```sh
target/debug/native-editor-check full
```

The command returns one JSON summary.
Read the generated report path in that summary.

A zero exit means that every required check passed.
Failed and incomplete results exit nonzero.
Each invocation creates a separate directory under `.runs/verification`.

| Exit | Meaning |
| --- | --- |
| `0` | Every required check passed |
| `1` | At least one check failed. The report can also contain incomplete checks |
| `2` | Required work is incomplete without a recorded failed check |
| `64` | The command does not match a supported mode |

The verifier permits no flag to skip checks or promote features.
After the initial build adds dependencies, Cargo checks run locked and offline.

The whole run has a 15-minute deadline.
Cargo stages have 3-minute deadlines.
Documentation and runtime probes have 30-second deadlines.
Tool-version probes have 15-second deadlines.

Each stdout and stderr log retains at most 8 MiB.
A truncated log prevents a pass result for that process.

## Read the evidence

Architecture mode checks ownership, source inventory, dependencies, capability state, documents, and guardrail failure cases.
It does not execute editing operations or establish that the renderer works.
Full mode adds formatting, clippy, actual default and test-hook acceptance, fresh runtime builds, and native artifact checks.

The intent correction also compares all 16 CORE-A/B cases with explicit observable expectations.
Both modes save `intent-coverage.json` beside `report.json`.
Architecture reports the CORE cases as not run.
Full mode needs current-run outcomes for implemented cases.
The 73 planned families remain unobserved in either mode.

Read each case's expected result, actual observation, mismatch details, and evidence references.

Purpose and scenario text come from the current feature contracts.
Independent expected constants and executable case bindings come from `docs/features/intent-contracts.json`.
Contract adequacy remains a required human review.
Technical comparisons cannot grant that approval.

[INTENT-VERIFICATION.md](INTENT-VERIFICATION.md) explains purpose, scenarios, non-goals, and the planned layer example.

The run preserves exact command arguments, selected environment overrides, exits, logs, and file hashes.
Default and test-hook builds have different Cargo targets and evidence directories.
Runtime discovery must agree with measured binary and schema identities.

The native PNG checks examine actual bytes and pixels.
Altered outputs must fail integrity checks.
Missing required tools cannot count as passed checks.

The report records deliberate rejected-path symlink fixtures separately.
The inventory never follows those fixture links.
Unexpected evidence-inventory errors produce a required incomplete check and a preserved report.

## Development guardrails

- Runtime crates cannot import the development verifier or future application adapters.
- Core cannot spawn processes or exit its host.
- Runtime source and dependency checks reject FFmpeg, libav, and historical renderer fallback paths.
- Recursive inventory covers nested and disabled source, additional target paths, and additional build paths.
- The current ledger cannot claim trusted verified promotion or accept caller-authored evidence.
- Reports and document-check receipts belong to separate runs.
- Process groups and bounded output control prevent an unresponsive child from an indefinite delay of a required check.

[GUARDRAILS.md](GUARDRAILS.md) explains the architecture choice and enforcement scope.
[GUARDRAIL-REVIEW.md](GUARDRAIL-REVIEW.md) links actual negative-fixture, subprocess, and full-plan results.

## Measured intent correction

The historical [authoritative full run](../.runs/verification/1791181299992260000-62429/report.json) passed all 22 checks in 86.2 seconds.
It records 29 default acceptance tests, 26 development regressions, and 32 hook acceptance tests.
Its [intent report](../.runs/verification/1791181299992260000-62429/intent-coverage.json) records all 16 CORE cases as passed.
The 73 planned families remain unobserved.
Human contract adequacy remains required and unreviewed.

The [isolated negative run](../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/report.json) compiled a frame-48 color error successfully.
All 21 other checks passed.
Only intent scenarios failed.
The concrete 4,096-pixel discrepancies affected CORE-04-A and CORE-05-A.

The [parent audit](../.runs/intent-parent-final-1791181090933543000/summary.json) matched 2,132 positive and 2,136 negative referenced files and all case bindings.
The audit independently reconstructed exact clips and snapshot identity.
The audit then decoded the emitted PNGs associated with raw CLI receipts.
At that audit, all nine runtime and acceptance source files were unchanged from the earlier baseline.

The [source review](../.runs/intent-review/source-review.md) records acceptance repairs and inspected source hashes.
The [execution index](../.runs/intent-implementation-evidence/final-handoff-revised.json) classifies all seven full-run attempts.
The revised index corrects blank human-review summary values.
The original index remains saved.
Authoritative coverage always retained `required-unreviewed`.

Earlier failed or cancelled runs remain saved and do not count as pass evidence.
The parent saved completion notes after execution.
At that handoff, the tested Rust sources, sidecar, and document checker were unchanged.
Those reports describe their historical snapshots.

## Earlier guardrail baseline

The [frozen full report](../.runs/verification/1791153958803819000-1131/report.json) passed in 51.3 seconds.
It records 29 default P0 tests, 20 development regressions, and 32 test-hook tests.
The [parent audit](../.runs/guardrail-parent-final-1791154080811595000/summary.json) independently matched all 1,708 evidence files and both runtime binaries.
The audit also matched all 73 observed inputs and decoded every one of the demo's 192 RGBA pixels.

Each report describes its observed snapshot.
The parent saved completion notes afterward.
Those notes did not change the tested Rust sources.
This baseline predates the feature-intent correction. It does not establish a pass result for the new scenario checks.

## Limits

The verifier applies repository-development rules.
It is not an arbitrary-Rust sandbox or an authenticated promotion authority.
A full mode pass result covers bounded P0 behavior.
It does not establish movie, audio, typography, layers, GPU, cloud deployment, playback, listening, or creative approval.
A later source change needs another run.
Historical pass receipts are not current-build proof.
