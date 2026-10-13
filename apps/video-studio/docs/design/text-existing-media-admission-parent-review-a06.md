# Existing-media admission A06: parent design review

Root read the complete 870-line A05-to-A06 patch against the previously reviewed A05 baseline.
Root read the complete A06 peer review and checked the cited ownership seams in the current product sources.
The peer matched all fourteen product-source hashes to the design.
No Plan8 source, helper, build, test, native process, or media execution occurred during this review.

| Artifact | SHA-256 |
| --- | --- |
| A06 design | `c53ea732da16a384c71e1a3f52e65cfda2ca5c9b5bf0ba702ddb20087e858502` |
| A05-to-A06 patch | `42f6ac9e625a4cb4b64359f5529e23368bcf863ca90cc691b7c8db5a5f231e05` |
| A06 peer review | `178e938867d6606bb33bf9eab4da049b0ad8520e219c2c2f0e3e3f869242983e` |

A06 closes the three A05 design findings.
Its canonical bodies, receipt graph, two running claims, and closed error adapters remain useful repair inputs.
Four P2 ownership or schedule gaps prevent implementation approval.
There are no P1 findings in this design-only artifact.

## P2: picture evidence is missing from the terminal execution peak

The peer identifies a missing overlap for `PictureExecutionEvidence.scope`.
Root confirmed its allocation at `layers.rs:769-774` after worker joins.
The outer decode closure, encoder result, writer, audio stream, and fixed result carriers can still be live at that point.
The separate post-write publication charge does not cover the earlier construction event.

Add one explicit terminal execution peak with `M_picture_execution` and every retained owner.
State which payloads and captures have dropped before constructing the scope.
Retain the fixed outer records until their actual drop or move.
Add the peer's 512-byte scope overlap control.

## P2: collision verification can allocate a second hash String

Root confirmed `project.rs:609-627` creates a hexadecimal String from the existing-file digest.
Canonical verification bytes and the expected `verification_id` remain live during this check.
`SerializerScalarScratch` covers serialization, so it does not cover this later owner.

Use a fixed-byte digest comparison on the Plan8 path or charge a separate temporary hash String.
Keep the canonical bytes and expected hash live in the collision-path control.

## P2: failure closure omits retained outer ownership

`failure_close_peak_A06` includes the main claim, error, canonical body, and fixed failure records.
It omits `M_prepared_plan` and the retained request/hash ownership from the outer export frame.

The current `Project::export` binds `prepared`, `request`, and `request_hash` before starting the attempt.
The terminal `match result` calls `close_failed_claim` while those outer bindings remain in scope.
An execution or verification error does not consume the prepared wrapper.
The inner closure drops its local picture evidence on error, but that fact does not drop the outer prepared plan.

Define the exact Plan8 failure transition before constructing `CanonicalFailureBody`.
Either consume and drop the outer owners first, or retain their charges in every failure-closure peak.
Apply the rule to execution, recovery, verification, cancellation, and fenced-attempt failures.
Do not remove variable owners merely because the failure helper does not receive them as arguments.
Add a control with a near-limit prepared plan retained during failure persistence.

## P2: recovery uses a joined-claim charge before the stated join

The recovery receipt-check, complete, and uncertain peaks use `C_claim_quiesced`.
The only general join rule says `ExportLease::quiesce` joins before publication.
Recovery reads and measures the receipt before calling `complete_legacy`.

The current recovery path at `exports.rs:1228-1240` retains the running lease during readback and measurement.
`ExportLease::quiesce` consumes the lease, so an earlier join also needs an explicit completion API transition.
The current source cannot supply the same consumed lease to `complete_legacy` afterward.

Specify one complete Plan8 recovery schedule.
Keep `C_claim_running` and `M_renewal_project` through the actual join, or define a separately reviewed joined-lease completion contract.
Use the joined charge only after the transition proves the renewal worker has finished.
Include the retained canonical stored body and fresh verification graph at their actual overlap points.
Add a control that rejects a premature one-claim charge while the renewal worker remains live.

## Repair boundary

Preserve A06 and its peer review.
Repair these four gaps in a successor without weakening its canonical-body, compatibility, receipt, or closed-error rules.
No implementation or process authority follows from this review.
This same-family, nonblind review establishes no physical-memory bound, native output, playback, hearing, or creative acceptance.
