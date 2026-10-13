# Comparator A13 parent review

Status: source-only review. A13 remains unexecuted and unqualified.
The parent read the complete 209-line A12-to-A13 patch, contracts, manifest,
the preserved A12 peer review, its correction, and the A13 peer review.
The parent independently matched all 38 package, input, Swift, and peer rows.
No comparator import, control, native producer, GPU, or Resolve process ran.

## Reviewed identities

| Artifact | SHA-256 |
| --- | --- |
| A13 actual control | `4ac29f6f708938059f19f00f574a6212828c22873daa80e1d3d915c3ed4c8100` |
| A13 manifest | `239e9f7be13cd63a4058b9b64f245185939840362650d9e1e212281424b2a01e` |
| Complete parent patch | `50009f4162efd9184b6826fa16f4d75a026b5b826ebfb9f1d282c6910f7372da` |
| A13 peer review | `6465c6389e460404cc139de646e6bb93be8868c119562af871ea012202f7b5fad` |
| A12 additive correction | `ffd7af4283612a561ce87ad5a0f9609842274bee9c76bb2fb0ce8e861dad8bf1` |

## P1: current allocation control bypasses the event-log reader

`current_allocation_replay_control` manually updates ownership and calls
`_a06_owner_accounting_step`, `validate_swift_report`, and
`_reconcile_swift_allocation`. It never calls `validate_swift_allocation_log`.
Its eight-event fixture sets `allocationEventBytes` to zero.
It has no encoded event records or write/rollback accounting.

The actual reader enforces exact JSONL keys, sequential indices, byte/count
bindings, newline completion, scratch-inclusive peak, and written-file totals.
It opens bounded evidence, verifies descriptor stability, and closes the handle.
Passing a manually populated replay map does not test these obligations.

A14 must call that reader with a bounded synthetic event-file descriptor.
The resulting replay must feed the actual reconciliation function.
The fixture remains synthetic contract evidence and cannot qualify native execution.

## P1: source and ordered result contract disagree

The parent confirms the peer's missing row:
`a11-complete-parser-outer-failure-no-repeats` is emitted by source but absent
from the 58-row schema. Static source accounting yields 59 rows.
The successor must freeze matching source, schema, manifest, and runner contracts.

## P2: bind the corrected gate review

A13 binds the original A12 review but omits its additive correction.
The correction withdraws the requirement that a valid observation-only rejection
have a false structural case gate. The corrected review must be an explicit row.

The parent confirms A13's source-faithful split: structural validity may be true
while declared qualification and native qualification remain false.
Failed, fractional, and outer cases require the actual case gate to be false.
Integer loader bytes and schema 2 remain the intended successor wire contract.

## Disposition

Preserve A13 and both reviews. Repair the two P1s and the P2 in A14.
No current source package authorizes execution or native acceptance.

The peer is same-model-family and nonblind. Its source origin is not independent.
No playback, hearing, film quality, or creative acceptance was established.
