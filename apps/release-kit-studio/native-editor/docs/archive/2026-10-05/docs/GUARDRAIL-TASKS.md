# Architecture and verification CLI task

- [x] Read the complete Principles section of poteto-mode.
- [x] Phase A: Frame
- [x] Phase B: Design the workflow
- [x] Phase C: Run the loop
- [x] Phase D: Keep the audit trail
- [x] Phase E: Verify and hand back

## Applicable Feature steps

The quoted steps come from the installed playbook. The execution decisions that follow record adaptations.

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

## Completion predicate

A local Rust verification CLI runs enforceable architecture checks and actual acceptance for the current build.
The CLI writes structured reports and keeps isolated evidence. The CLI exits nonzero on failure or incomplete required checks.
Negative fixtures prove rejection of prohibited dependencies, process access in the library, and unsupported promotion.

The architecture specifies CLI automation, planned expressions, and optional future Lua. Lua does not become an editor dependency.
Rust domain behavior stays unchanged. Effect, UI, Cloudflare, Resolve, GPU access, and FFmpeg remain outside this task.

## Throughput checkpoint

- [x] **Blocking first steps.** Examine the current ownership and checks. Save the baseline before source changes. Compare verification designs before implementation.
- [x] **Independent workstreams.** Read-only trace and isolated design candidates have separate outputs. The parent owns documents and the shared ledger. One code owner owns the coupled verifier implementation.
- [x] **Shared mutable state.** Each verification run gets a new evidence directory and a new Cargo target directory. No checker changes production project state or promotes feature state.
- [x] **Smallest safe decomposition.** Keep one owner for verifier report types, process control, checks, and regression tests. Review the actual source and CLI results independently.

## Bounded workflow

- [x] Ground. Complete a read-only `how` trace. Save baseline command evidence.
- [x] Sketch. Compare two verification packages with different structures through `architect` and `arena`.
- [x] Agree. Select the base after independent judgment. A user checkpoint is not necessary for reversible local work.
- [x] Implement. Add guardrails and a verification command without changes to the ownership of editing semantics.
- [x] Scrap. Skip this phase because separate verifier ownership still applies. Integration repairs kept the selected design.
- [x] Verify. Do tests of actual CLI success, intentional failures, missing tools, isolated reports, and core regressions.
- [x] Review. Complete independent reviews of source, comments, evidence, and the decision trail.

## Publication and tool adaptations

This task skips rebase, commits, and Opening a PR. This request is local, and the repository contains unrelated uncommitted work.
Skip Interrogate unless design judgment remains contested.
Cursor-specific poteto-agent, control-cli, create-skill, and deslop tools are unavailable in this Codex session.
Codex collaboration agents provide separate writers and reviewers. Real subprocess checks provide CLI verification.

Only GPT models are available. The task records model choices without a claim of independence across model families.
This task does not create a skill. This task does not authorize deployment, hook installation, provider action, or production-media mutation.
