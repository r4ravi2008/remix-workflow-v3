# Feature intent and acceptance evidence

Feature intent describes the result necessary for a creator and why that result matters.
For CORE-04, a background change at an exact chorus boundary is necessary for the creator.
For CORE-03, a retry must keep one edit after an uncertain response.
The term differs from `intentId`. That identifier identifies a project command that permits retries.

The compiler validates types and visibility. Repository guardrails enforce development rules.
Neither result proves that the creator received the requested result.
A comparison that measures the requested result is also necessary for a named test.

## The missing link

The current feature contracts contain purpose, scenarios, behavior rules, and named acceptance cases.
The earlier full verifier examines named P0 test evidence and actual artifact bytes.
That earlier report does not show the expected and observed results for each documented scenario.
Document coverage makes sure that sections exist. Coverage cannot prove that the implementation agrees with the sections.

The implemented correction connects four items in one record that permits review.

1. The feature contract states the creator's purpose and scenario.
2. The acceptance case states inputs, actions, observable expectations, and failure conditions.
3. The current build runs the public CLI and saves responses and artifacts.
4. An independent comparison records expected values, observed values, mismatches, and evidence identity.

The current executable scope is CORE-01 through CORE-08.
Planned features keep their authored scenarios and remain untested.
The correction does not add editor runtime features or promote capabilities.

## Measured result

The [full run](../.runs/verification/1791181299992260000-62429/report.json) passed all 22 required checks.
Its [intent coverage](../.runs/verification/1791181299992260000-62429/intent-coverage.json) records 16 cases with a pass result across eight implemented CORE families.
All 73 planned families keep their authored purpose, scenario, and case IDs without runtime observations.
Contract adequacy remains `required-unreviewed`.

An isolated copy deliberately changed each frame-48 render to blue.
That copy compiled successfully and passed the other 21 development checks.
The [negative intent report](../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/intent-coverage.json) rejected CORE-04-A and CORE-05-A.

Each case reported 4,096 wrong pixels. CORE-04-A expected gold. CORE-05-A expected an uncovered transparent frame.

The [parent audit](../.runs/intent-parent-final-1791181090933543000/summary.json) independently decoded emitted PNGs and matched raw CLI requests, receipts, snapshots, and hashes.

The [source review](../.runs/intent-review/source-review.md) records repaired acceptance gaps and inspected limits.
The [decision trail review](../.runs/intent-review/trail-review.md) found no completion blocker in the audited automated scope.
The [execution index](../.runs/intent-implementation-evidence/final-handoff-revised.json) preserves all seven full-run attempts and their classifications.

The summary correction keeps the original index. The correction gets the human contract-review state from the authoritative coverage reports.

The parent saved completion notes after execution. At that historical completion point, the tested Rust sources, sidecar, and document checker remained unchanged.

## A concrete boundary case

CORE-04-A describes a 96-frame project at 24 fps.
Blue occupies frames 0 through 47. Gold occupies frames 48 through 95.
The acceptance comparison must inspect exact clip intervals and independently decode frames 47 and 48.
An implementation fails this case if it reports a successful render but produces blue at frame 48.

CORE-04-B submits a valid edit with an invalid removal.
The whole transaction must fail. The original snapshot and hash must remain unchanged.

These comparisons examine the promised timeline behavior.
Output existence, receipt hashes that match, or successful compilation cannot replace the comparisons.

## Limits of automated intent verification

An automated comparison measures declared, observable acceptance cases.
The comparison cannot prove that the cases contain each part of the human purpose.
Reviewers must decide if the expectations describe the requested feature. Reviewers must also decide if the expectations cover plausible failure modes.
A hash connects the report to a contract version. The hash does not prove contract adequacy.

Technical acceptance and creative acceptance remain separate.
Checks of exact text, timing, and text shaping are necessary for a future lyric feature.
A viewer must also review readability and creative fit.
Checks of layer order, opacity, mask, timing, and audio preservation are necessary for a future layered scene.
The current single-track PNG renderer cannot satisfy those future cases.

## A planned layer feature

The EDIT-01 creator wants a performer and Telugu lyrics over an environment. The song continues independently.
The current EDIT-01 scenario gives the performer frames 48 through 191 and the lyrics frames 96 through 143.

| Intended result | Required observation |
| --- | --- |
| The performer appears at the correct time | Frame 47 contains only the environment. Frame 48 adds the performer. |
| The lyrics appear only in their interval | Frame 96 adds lyrics. Frame 144 removes them. |
| Transparency reveals the environment | Each independently decoded fixture pixel matches the declared stack and alpha policy. |
| The hidden performer does not change the song | A1 PCM samples remain identical when V2 is hidden. |
| An unsupported mask cannot cause damage to the edit | The command fails and the previous revision hash remains unchanged. |

These are authored expectations for planned behavior. No expectation has evidence from the current renderer.
The intent report must show that gap. The report must not count a complete document as a feature that passed.
The [EDIT-01 contract](features/editing.md#edit-01-track-and-timeline-composition) contains the full cases and prerequisites.

The [development workflow](WORKFLOW.md) defines how a feature moves from requested purpose to acceptance evidence.
The [verification guide](VERIFICATION.md) describes executable commands and their measured scope.
The [task record](INTENT-TASKS.md) records the design and implementation state of this correction.
