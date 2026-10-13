# Feature intent and acceptance evidence

Feature intent describes the result that a creator needs.
`intentId` identifies a project command that permits retries.
These terms have different meanings.

The Rust compiler checks types and privacy.
Repository guardrails check development rules.
Neither check proves that the creator received the requested result.

## Connect purpose to evidence

Each implemented feature needs one record that connects four items:

1. The feature contract states the creator purpose and scenario.
2. The acceptance case states inputs, actions, expected observations, and failure conditions.
3. The current build runs the public CLI and saves responses and artifacts.
4. An independent comparison records expected values, observed values, mismatches, and evidence identity.

Document coverage proves that required sections exist.
It cannot prove that the implementation agrees with those sections.

The executable scope is CORE-01 through CORE-08.
Planned features keep their authored scenarios and remain unobserved.
The intent check does not add editor features or promote capabilities.

## Observed CORE cases

The last successful full snapshot is report.json in `../.runs/verification/1791190183401588000-54565/report.json`.
The paired intent report in `../.runs/verification/1791190183401588000-54565/intent-coverage.json` records 16 CORE A/B pass observations.
The 16 observations cover eight implemented families.
The report records 73 planned families as unobserved.
Contract adequacy remains `required-unreviewed`.

An isolated copy changed every frame-48 render to blue.
That copy compiled successfully.
The copy passed the other 21 development checks.
The wrong-pixels intent report in `../.runs/intent-negative-1791180824088958000/native-editor/.runs/verification/1791181963547193000-69082/intent-coverage.json` rejected CORE-04-A and CORE-05-A.

Each case reported 4,096 wrong pixels.
CORE-04-A expected gold.
CORE-05-A expected an uncovered transparent frame.

The parent audit in `../.runs/intent-parent-final-1791181090933543000/summary.json` decoded emitted PNGs and matched CLI requests, receipts, snapshots, and hashes.
The source review in `../.runs/intent-review/source-review.md` records repaired acceptance gaps and inspected limits.
The execution index in `../.runs/intent-implementation-evidence/final-handoff-revised.json` preserves the seven full-run attempts.

The cleanup result and any later current full receipt are recorded in the cleanup summary in `../.runs/product-contract-1791264756707/SUMMARY.md`.
This page does not claim a post-cleanup full pass.

## Boundary case

CORE-04-A describes a 96-frame project at 24 fps.
Blue occupies frames 0 through 47.
Gold occupies frames 48 through 95.
The comparison must inspect exact clip intervals.
The comparison must decode frames 47 and 48.
The case fails when the report says render success but frame 48 remains blue.

CORE-04-B submits a valid edit with an invalid removal.
The transaction must fail.
The original snapshot and hash must remain unchanged.

Output existence, receipt hashes that match, and successful compilation cannot replace these comparisons.

## Contract adequacy

An automated comparison measures a declared acceptance case.
It cannot prove that the case covers every part of the human purpose.
An independent reviewer must decide whether the expectations describe the requested feature.
The reviewer must also examine plausible failure modes.

A contract hash binds the report to one contract version.
The hash does not prove contract adequacy.
Technical acceptance and creative acceptance remain separate.

Future lyric checks need exact text, timing, and text shaping.
A viewer must also review readability and creative fit.
Future layer checks need order, opacity, masks, timing, and audio preservation.
The current single-track PNG renderer cannot satisfy those cases.

## Planned layer case

EDIT-01 describes a performer and Telugu lyrics over an environment.
The song continues independently.
The performer occupies frames 48 through 191.
The lyrics occupy frames 96 through 143.

| Intended result | Required observation |
| --- | --- |
| The performer appears at the correct time | Frame 47 contains only the environment. Frame 48 adds the performer. |
| The lyrics appear only in their interval | Frame 96 adds lyrics. Frame 144 removes them. |
| Transparency reveals the environment | Decoded fixture pixels match the declared stack and alpha policy. |
| A hidden performer does not change the song | A1 PCM samples remain identical when V2 is hidden. |
| An unsupported mask cannot damage the edit | The command fails and the previous revision hash remains unchanged. |

These are planned expectations.
The current renderer has no evidence for them.
The intent report must show that gap.
The report must not count a complete document as a passed feature.

See the [EDIT-01 contract](features/editing.md#edit-01-track-and-timeline-composition), the [development workflow](WORKFLOW.md), and the [verification guide](VERIFICATION.md).
