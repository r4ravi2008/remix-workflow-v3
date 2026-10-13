# Intent design verdict

Select Candidate B as the base. Use a smaller contract and one decisive probe from A.

This is a design judgment. I did not run Cargo or observe either proposal in operation.

| Criterion (1–5) | A | B | Judgment |
| --- | ---: | ---: | --- |
| Independent expected/observed public CLI proof | 5 | 5 | Both compare saved CLI results, pixels, state, and hashes against independent expectations. |
| Purpose, scenario, named cases, and remaining human judgment | 4 | 4 | Both bind these concepts, but duplicate the current feature prose across 81 entries. |
| Smallest maintainable change using the current runner | 2 | 3 | A adds capture instrumentation throughout acceptance tests and a comparison vocabulary. B reuses `ProcessRunner`, but duplicates some scenario execution. |
| Wrong, missing, or stale evidence fails. Compiler-successful negative probe | 5 | 4 | Both reject bad evidence. A alone specifies a successful compile with deliberately wrong pixels. |
| Honest planned/unobserved status and no runtime promotion | 5 | 5 | Both separate eight implemented CORE families from 73 planned families and leave human review pending. |

## Recommended synthesis

1. Keep B's direct, case-specific Rust evaluator inside `editor-devcheck`.
2. Invoke the current `ProcessRunner` through `Verifier`.
3. Keep `architecture` and `full` as the only modes.
4. Do not add runtime behavior or a generic assertion language.
5. Use the current strict feature headings as the source for purpose, scenario, and named verification cases.
6. Derive those fields for all 81 report rows from the Markdown.
7. Do not duplicate prose, headings, paths, section hashes, commands, and case lists in 81 sidecar records.
8. Limit the sidecar to the eight implemented CORE families.
9. Store independent expected constants, explicit case-to-check bindings, non-goals, and remaining review requirements in the sidecar.
10. Bind the sidecar to the current source inventory and exact CORE document bytes.
11. For 73 planned families, report their Markdown purpose and cases as `planned-unobserved` without executable bindings.
12. Execute all 16 CORE document cases through fresh public CLI binaries.
13. Save request, response, process, file, state, and decoded pixel observations under the current run.
14. Compare the observations with independent expectations.
15. Do not derive expectations from the response or receipt under examination.
16. Use before/after inspection for rejection and rollback cases.
17. Add A's compiler-successful wrong-pixels probe.
18. In a scratch checkout, change the solid-pixel calculation.
19. Preserve valid receipts and schemas.
20. Build the scratch checkout successfully.
21. Run `full`.
22. Require the expected-pixel comparison to fail.
23. Require current-run evidence for every implemented named case and expected outcome.
24. Keep oracle adequacy and creative, playback, or listening review explicit and unreviewed where required.
25. Limit the `full` claim to observed CORE outcomes.

`docs/features/check.mjs` already enforces the feature headings' presence and coverage.
The wrong-pixels probe demonstrates the specific gap that the user identified.
Wrong values fail. Missing evidence is incomplete.
Previous-run or mismatched binary, source, contract, or profile evidence is stale.
A Cargo test pass, a valid hash, or a named case alone cannot pass intent coverage.

The `full` report must never promote capability state or imply approval of the complete creator purpose.

B proposes an 81-record sidecar and a per-section hash catalog. These records duplicate information already in seven feature documents. A's observation DSL and test-wide instrumentation add a second maintenance path. A direct evaluator is reasonable at 16 implemented cases. If later implementation makes the direct code repetitive, redesign the code from measured duplication.

The recommended report contract shows one CORE row before implementation. The CORE row contains purpose, scenario, expected and actual values, evidence, and review state.
It also shows one planned row with its documented case names and `planned-unobserved`.
These rows give reviewers a concrete target for the code. These rows distinguish a structurally complete report from runtime proof.
