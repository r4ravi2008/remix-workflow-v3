# Verification architecture decision

The selected design adds a Rust development verifier outside both runtime crates.
A local agent uses the editor CLI to edit projects and verify stored artifacts.
A repository developer uses the verifier for checks of ownership, source rules, current-build P0 behavior, and evidence.

## Design comparison

The arena compared an integrated development command with a separate verifier.
The parent read both complete artifacts. An independent `gpt-6-sol` judge scored the designs.

| Criterion | Integrated command | Separate verifier |
| --- | ---: | ---: |
| Preserve runtime ownership | 3 | 5 |
| Enforce current guard gaps | 5 | 4 |
| Current-build evidence and isolation | 4 | 4 |
| Bounded processes and incomplete outcomes | 5 | 4 |
| Maintainer burden | 2 | 4 |
| Shared API and optional Lua | 4 | 5 |
| Total | 23 | 26 |

The separate verifier is the base.
It keeps Cargo, Node, subprocess groups, and report publication outside the editing runtime.
"Preserve runtime ownership" in the comparison means component responsibilities and dependency packages.
Rust already enforces types and visibility.
Those compiler guarantees do not need a separate verifier.

The additional runner checks project rules and observable feature outcomes that the compiler cannot establish.
The integrated candidate contributes a fixed whole-run deadline and broader negative fixtures.
The design rejects full historical workspace snapshots and generic checker plugins because they add unnecessary complexity.

The saved designs are [candidate A](arena/guardrail-a.md), [candidate B](arena/guardrail-b.md), and [the judge](arena/guardrail-judge.md).
Only GPT models are available.
This is independent-agent review.
It does not establish cross-family model independence.

## Chosen ownership

`editor-core` owns typed editing semantics, revisions, intents, native pixels, and artifact integrity.
`editor-cli` owns runtime JSON, schemas, discovery, deadlines, and exits.
`editor-devcheck` owns development policy, bounded check processes, independent observations, and isolated reports.
No runtime crate imports the verifier.
The verifier observes the public CLI.
It does not share the CLI editing implementation.

## Verification states

Each required check produces passed, failed, or incomplete.
The aggregate verdict derives from those observations.
A missing tool cannot count as a pass.
Architecture mode proves repository structure only.
Full mode adds current-build P0 execution.

The intent correction adds expected and observed results for documented CORE creator cases.
Its report derives creator purpose and scenarios from the current feature contracts.
Planned features remain unobserved.
Human contract review remains separate from technical comparisons.

Both modes preserve prior runs and produce reports that identify the actual sources and evidence.
No report promotes a capability.
No report establishes movie, audio, typography, layers, GPU, cloud, playback, listening, or creative approval.

The verifier enforces development rules.
It does not sandbox arbitrary hostile Rust.
It does not authenticate a compromised compiler or sign trusted promotion receipts.
The [task record](GUARDRAIL-TASKS.md) records implementation and measured completion.
The [source review](GUARDRAIL-REVIEW.md) records found gaps, repairs, and current acceptance limits.
The [intent design](arena/intent-synthesis.md) records the correction's selected scope and proof requirements.
