# Native editor progress

The standalone Rust library and direct agent CLI are implemented for bounded P0 behavior.
The specification describes all 81 mapped families through scenarios, rules, implementation pieces, and named checks.
Effect and optional UI adapters belong in separate future applications.

## Latest correction results

The [current correction result](../.runs/warning-fix-1791188261870798000/SUMMARY.md) records the exact prose and native verification outcomes.
The [project check](../../docs/check-writing.py) retains raw upstream diagnostics and vocabulary results.
The [technical-use records](../../docs/ste-technical-uses.json) bind each reviewed use to its exact sentence and count.
The records do not approve a word globally.

The response checks distinguish execution and terminal selection from response delivery.
Short timeout and recovery cases remain separate.
The correction preserves feature expectations and native crate ownership.
Independent reviews examine the changed prose, contextual records, and source.
The current full native verdict appears in the linked correction result.

## Previous documentation revision

The STE revision changed the maintained application prose and added [WRITING.md](WRITING.md).
The document checker reports no errors. Feature coverage and specification checks pass.
The revision preserves Rust runtime source and acceptance expectations.
Only the CORE source-document digest changes in the intent sidecar.

Full validation remains incomplete.
The [first full run](../.runs/verification/1791185642606452000-304/report.json) failed the slow-reader regression test.
Its CORE intent cases passed.
The [isolated regression rerun](../.runs/ste-docs-1791184225862792000/slow-reader-isolated.log) passed without source changes.

The [second full run](../.runs/verification/1791185835787000000-4022/report.json) failed CORE-07-B.
That case expected a large successful response. The CLI returned a complete timeout response.
The declared deadline does not establish the cause of either failure.
The revision preserves both failed reports and their original contract snapshots.

The documentation revision does not claim a successful current full verification.
It does not change capability states or grant human contract adequacy.
The earlier measurements below describe their recorded historical snapshots.


## Historical measurements

The measurements below describe the linked historical snapshots.
They do not verify later document changes.

| Deliverable | State | Evidence |
| --- | --- | --- |
| Existing-path grounding | Read-only trace complete | [GROUNDING.md](GROUNDING.md) |
| Rust package comparison | Two candidates saved and independently judged | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Rust command and storage contract | Saved | [SPEC.md](SPEC.md) |
| Complete feature-detail guide | 81 families in seven documents. Scenarios and implementation pieces saved | [FEATURES.md](FEATURES.md) |
| Feature-detail review | Independent review complete. Concrete findings corrected | [FEATURE-REVIEW.md](FEATURE-REVIEW.md) |
| Feature document coverage | 81/81 sections passed structural checks | [coverage-check.json](features/coverage-check.json) |
| Document links and ownership | Structural check passed. No runtime claim | [spec-check.json](spec-check.json) |
| Rust library and direct Rust CLI | Eight CORE families implemented in bounded P0 | [Full report](../.runs/verification/1791181299992260000-62429/report.json) |
| Default Rust acceptance suite | 29/29 P0 tests passed | [Full report](../.runs/verification/1791181299992260000-62429/report.json) |
| Development regression suite | 26/26 tests passed | [Full report](../.runs/verification/1791181299992260000-62429/report.json) |
| Test-hook acceptance suite | 32/32 tests passed. Separate default and hook targets | [Full report](../.runs/verification/1791181299992260000-62429/report.json) |
| Rust formatting and clippy | Passed. Both clippy configurations deny warnings | [Full report](../.runs/verification/1791181299992260000-62429/report.json) |
| Parent artifact and evidence audit at the recorded snapshot | Passed. 2,132 positive and 2,136 negative referenced files and all case bindings matched. The audit independently decoded boundary PNGs. | [Parent audit](../.runs/intent-parent-final-1791181090933543000/summary.json) |
| Independent runtime source review | No remaining serious findings in inspected scope | [RUNTIME-REVIEW.md](RUNTIME-REVIEW.md) |
| Separate development verifier | Implemented. All 22 full checks passed in 86.2 seconds | [VERIFICATION.md](VERIFICATION.md) |
| Feature intent coverage | 16 cases passed across eight implemented families. 73 planned families remain unobserved | [Intent coverage](../.runs/verification/1791181299992260000-62429/intent-coverage.json) |
| Intent-breaking output probe | Compiles. 21 other checks passed. Wrong frame pixels failed CORE-04-A and CORE-05-A | [Negative full](../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/report.json) |
| Intent source review | Repaired findings reread. No actionable priority issue remains in inspected source | [Source review](../.runs/intent-review/source-review.md) |
| Human contract adequacy | Required and unreviewed. Automated comparisons cannot grant it | [Intent guide](INTENT-VERIFICATION.md) |
| Intent decision-trail audit | No completion blocker in audited automated scope. The revised summary corrects the defect. The original remains saved. | [Trail review](../.runs/intent-review/trail-review.md) |
| Guardrail source review | Independent findings repaired. No priority issue remains in inspected source | [GUARDRAIL-REVIEW.md](GUARDRAIL-REVIEW.md) |
| Guardrail architecture | Separate Rust development ownership selected | [GUARDRAILS.md](GUARDRAILS.md) |
| Lua and expression boundaries | Saved architecture target. No embedded runtime | [SCRIPTING.md](SCRIPTING.md) |
| Trusted capability promotion | Not implemented. No feature is marked verified | [capabilities.json](../capabilities.json) |
| Layer stacks, masks, and composition | Specified. Not implemented | [LAYERS.md](LAYERS.md) |
| Remaining mapped capabilities | 73 families planned. Phases identify their first bounded unit | [IMPLEMENTATION.md](IMPLEMENTATION.md) |
| Effect and optional UI adapter | Planned outside native editor | No adapter runtime |
| Native movie codecs and GPU path | Not implemented | No codec corpus or device evidence |
| Hosted native editor | Not deployed | No provider readback |
| Pal Pal native release kit | Not produced | No six-output native receipt |

## What works locally

P0 exposes six tools: discovery, project creation, project inspection, atomic timeline commits, frame renders, and artifact verification.
Projects have immutable SQLite revisions and stable command intents.
The renderer supports one track of solid RGBA clips without overlap and CPU PNG output.
It preserves alpha and rejects altered completed artifacts.
It cannot render footage, sound, typography, or multiple visual layers.

Use [CLI-EXAMPLES.md](CLI-EXAMPLES.md) for tests of this bounded implementation.
The earlier foundation binary and schema identities are saved in [RUST-FIRST-CHECK.json](RUST-FIRST-CHECK.json).
The separate verifier records measured run identities in its [full report](../.runs/verification/1791181299992260000-62429/report.json).

The parent saved completion notes afterward.
At that handoff, the tested Rust sources, sidecar, and document checker were unchanged.
The reports describe their historical snapshots.

Test-hook interruptions do not establish physical power-loss behavior.
The CLI bounds execution and terminal-result selection.
The agent that invokes the CLI must drain stdout.
The agent that invokes the CLI must enforce the total process timeout.

## Evidence boundaries

Saved source, tests with pass results, artifact inspection, playback, listening, and creative approval remain separate states.
A document checker cannot verify runtime behavior.
An artifact integrity result cannot promote a capability.
The ledger therefore retains implemented and planned states despite P0 test pass results.
No historical Python or FFmpeg renderer evidence promotes a Rust capability.

The [decision trail](decisions.tsv) records scope, package, layout, and verification choices.
The reviewers use GPT models.
The review does not establish cross-family model independence.
[The earlier audit](AUDIT.md) concerns the earlier specification, not this runtime.
