# Feature intent verification work

- [x] Read the complete poteto-mode Principles section.

## Matched playbook

### Feature

> **You own the design. Plan, review, verify.** Delegate implementation; stay in the lead.
>
> 1. `how` over the affected subsystem.
> 2. `architect` for parallel design exploration. Skipping stays as `architect skipped: <reason>`; do not fold the design decision silently into implementation.
> 3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
>    - **Blocking first steps.** Gates run before fan-out.
>    - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
>    - **Shared mutable state.** Default to splitting the target (the **separate-before-serializing-shared-state** principle skill). Serialize only for real invariants.
>    - **Smallest safe decomposition.** If one worker is best, name why.
> 4. Delegate code-writing to a subagent using your configured feature model (default `grok-4.6-fast-xhigh`) with a specific scope (file paths, named data shape and its organizing structure per **principle-model-the-domain** — a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic — and success criteria); review its diff yourself. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate via the **arena** skill instead so the runners surface the alternatives and the cross-judge guards the pick. Mandatory: no skip-with-reason escape, and Laziness Protocol does not override it (the gain is review separation, not lines saved). You can spawn a subagent even though you are one; "the app is small" and "a subagent cannot spawn one" are both wrong. A subagent forbidden to spawn satisfies this by owning the diff directly with the same review separation; no "standing by" reply that waits on a nested agent. Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit liberally.
> 5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass; flag it.
> 6. Rebase into small, ordered commits; stack follow-ups.
>    Use the **sequence-verifiable-units** principle skill, building, verifying, and committing each small unit before the next.
> 7. If the design is contested, `interrogate` before shipping.
> 8. Run **Opening a PR**.
>
> Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline; that owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries; spawn a fresh owner rather than chaining interrupts.
>
> **Reply:** what you built, what you chose and why, open decisions. Tables for design alternatives.

## Phase status

- [x] Ground. Examine scenarios, assertions, evidence, and status.
- [x] Sketch. Compare two complete designs.
- [x] Agree. Select the smaller complete design after an independent judge reviews the designs.
- [x] Implement. One owner writes code for the selected design.
- [x] Scrap. Skip this phase. Review repairs agree with the selected design. Repeated design problems do not make replacement necessary.
- [x] Verify. Run the actual CLI. Run a negative probe that breaks the intent contract.
- [x] Review. Examine the diff, comments, reports, and remaining limits.
- [x] Delivery. Skip commits and PR publication. This local directory is untracked, and the repository contains unrelated changes.

## Arena phases

- [x] Frame
- [x] Fan out
- [x] Cross-judge
- [x] Pick
- [x] Graft
- [x] Verify

## Throughput checkpoint

- [x] Blocking first steps. Examine current scenario contracts, assertions, and report evidence before design.
- [x] Independent workstreams. Design candidates write separate notes. One code owner writes the selected contract implementation.
- [x] Shared mutable state. The parent owns workflow prose and this task record. The code owner owns the verifier and contract files.
- [x] Smallest safe decomposition. Reuse current feature IDs, CLI, tests, and reports. Do not add an editor runtime. Do not add a compiler duplicate. Do not add a generic evaluation service.

## Required result

Each feature must connect its stated purpose to named, observable acceptance cases and evidence from the current build.
Document coverage must not count as proof of behavior.
Planned features must keep their untested status visible.
The first executable scope is the eight current P0 core features.
Verification must find a plausible implementation that compiles but breaks a stated outcome.
Technical output checks and human creative acceptance remain separate.

## Measured completion

- The authoritative full run passed 22 checks and all 16 CORE cases.
- Default acceptance passed 29 tests. Hook acceptance passed 32 tests. Development regression passed 26 tests.
- The isolated wrong-frame build compiled. Its clean full run failed only the intent scenarios. The other 21 checks passed.
- The parent calculated hashes again for 2,132 positive and 2,136 negative referenced files. The parent independently decoded the emitted boundary PNGs.
- All nine current runtime and acceptance source files match the earlier runtime baseline.
- Human contract adequacy remains required and unreviewed. The 73 planned families have no observations.
- The independent decision-trail review found no automated-scope completion blocker. The revised index corrects its summary-extraction defect.

Read [the intent guide](INTENT-VERIFICATION.md) for direct evidence links.

## Environment adaptation

This session uses Codex collaboration agents and actual CLI subprocesses.
Cursor-specific agent types and control-cli are unavailable.
The design comparison uses available GPT models. The comparison does not claim independence across model families.
