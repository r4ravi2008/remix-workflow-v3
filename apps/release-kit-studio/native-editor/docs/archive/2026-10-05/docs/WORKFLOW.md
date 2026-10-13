# Develop a native editor capability

1. Read `AGENTS.md` and the applicable installed `poteto-mode` playbook.
2. Select feature IDs from `capabilities.json`.
3. Open the linked contract through [FEATURES.md](FEATURES.md).
4. Use the contract's scenario and implementation-piece IDs to set the task boundary.
5. Record the feature's requested purpose in creator terms.
6. Name the concrete scenario, preconditions, action, expected observable outcomes, and non-goals.
7. Write named acceptance cases in the task plan.
8. Write exact file ownership in the task plan.
9. State how each outcome is independently observed.
10. Include a plausible failure that still compiles.
11. State any required playback, listening, creative, or contract-adequacy review separately.
12. If a runtime check exists, run the check to record the baseline.
13. If no runtime check exists, record that the runtime remains unimplemented.
14. Use the separate [verification CLI](VERIFICATION.md) for repository checks.
15. Trace the affected command through `how`.
16. For a new boundary, compare designs through `architect` and `arena`.
17. Write the necessary first steps, independent tasks, shared state, and smallest safe task division.
18. Before you change ownership or dependencies, run architecture mode.
19. Implement one bounded unit in an isolated worktree or owned directory.
20. Run the feature's acceptance check through the actual CLI.
21. Compare expected and observed outcomes.
22. Save mismatches and raw evidence from all runs.
23. Keep evidence from failed runs.
24. Before a native code handoff, run full development verification.
25. Save the measured receipt.
26. Update only the state that the evidence supports.
27. Append the decision and evidence to `docs/decisions.tsv`.
28. Review the contract and actual runtime evidence independently.
29. Judge whether the expectations represent the requested outcome.

Feature purpose differs from the runtime `intentId` for commands that permit retries.
Each verification run keeps separate evidence.
Complete documents, successful compilation, and artifact integrity cannot establish acceptance of the feature purpose.
An automated comparison cannot judge whether the expectations represent the requested outcome.
[Feature intent verification](INTENT-VERIFICATION.md) explains the acceptance sequence and its limits.

1. Use the skill catalog to find installed skills.
2. Record the actual model and role used for review.
3. Do not claim an unavailable model or cross-family review.
4. If a specialized CLI-control skill is absent, run the saved integration script directly.

Codex and Cursor expose different collaboration tools.

These principles define concrete choices in the specification and current P0 implementation.
[PROGRESS.md](PROGRESS.md) gives measured results.
Future capability gates remain planned.

| Principle | Encoded choice |
| --- | --- |
| Experience First | FEATURES.md starts with creator tasks. Each feature starts with a plain explanation and concrete scenario. |
| Model the Domain | Typed command variants and project intervals replace loose optional fields and scattered switches. |
| Boundary Discipline | Rust validates semantic requests. The Rust CLI validates process messages. Future application adapters keep workflow policy outside the kernel. |
| Foundational Thinking | Protocol and acceptance checks precede codecs, UI, and production orchestration. |
| Type System Discipline | Native protocol schemas derive from Rust types. Future application adapters do not copy timeline shapes. |
| Make Operations Idempotent | Stable intents return original results and reject changed content. |
| Separate Before Serializing Shared State | Candidate artifacts and agent tasks have separate owned paths. Real project mutations serialize transactionally. |
| Sequence Work into Verifiable Units | Each bounded implementation ends with a check before the next phase. |
| Prove It Works | Separate checks examine document coverage and actual CLI behavior. Artifact checks read real bytes and exercise failure paths. |
| Encode Lessons in Structure | The document check distinguishes authored state from runtime evidence. Native dependency and executable checks enforce the no-FFmpeg path. |
| Verification ownership | editor-devcheck controls development processes. Runtime crates remain independent of Cargo, Node, and verifier code. |
| Redesign from First Principles | The native command path has no compatibility fallback into the previous Python renderer. |
| Build the Lever | `docs/check-spec.mjs` reproduces the current document check. Rust integration tests exercise the standalone CLI. PROGRESS.md gives actual results. |
| Never Block on the Human | Reversible specification work proceeds without another architecture approval. |
| Exhaust the Design Space | Reviewers compared two alternative ownership sketches before they selected Rust authority. |
| Laziness Protocol | One compact command interface replaces duplicated typed wrappers in the candidate design. |
| Minimize Reader Load | One index starts with scenarios and links all 81 families. Each feature uses the same seven sections. |

These conventions support the Poteto workflows.
They do not need Cursor-specific tools to run the application.
