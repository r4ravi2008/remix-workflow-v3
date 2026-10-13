# Comparator A11 source review

Status: source-only independent review. The A11 package is frozen. No Python
module was imported, and no comparator, control, compiler, native framework,
GPU, or Resolve process was run.

## Reviewed identities

| Item | SHA-256 |
| --- | --- |
| `text-report-comparator-a11/package-manifest-a11.json` | `d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872` |
| `text-report-comparator-a11/compare_text_reports_a11.py` | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| `text-report-comparator-a11/actual-comparator-control-a11.py` | `3e1d293a57e1b617f39702d4d599f8520f6828860daba3fe59cd781f0b7c49a2` |
| `text-report-comparator-a11/required-evidence-control-a11.py` | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| `feasibility-swift-a15/source-manifest-a15.json` | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| A10 source review | `c3766d3c6d2969ed70c37010391c565c68fe64e483b897e83fae9cb3091188f7` |

## Findings

### P1-1: three actual-control negatives assert the wrong first error

`actual-comparator-control-a11.py:374-377` mutates an accepted allocation and
calls `_validate_a10_allocation_shape` directly.

* The baseline mutation changes only `allocation.initialReplayBaselineBytes`.
  The accepted policy still binds that field to the original value. The
  validator visits the binding map first and returns `swift_reservation_binding`.
  The control expects `swift_reservation_baseline`.
* The peak mutation changes only `reservationTableObservedPeakSlots` to 257.
  The same binding check returns `swift_reservation_binding` before the range
  check. The control expects `swift_reservation_peak_slots`.
* The missing fractional toggle removes one toggle and calls
  `_a10_validate_swift_case` at line 431. `_a11_validate_swift_state` reports
  `toggle_count` before the schedule comparison. The control expects
  `swift_toggle_schedule`.

These controls therefore fail for the intended reason even when the validator
is correct. They cannot qualify the claimed baseline, peak, or schedule
checks. The control must either mutate the paired policy binding too, or
expect the binding error and add separate inputs that reach each later check.
The fractional case must retain the required count while changing a schedule
entry if it is intended to test schedule equality.

### P1-2: the actual control does not use the full current validation path

The control claims to cover the current A15 allocation and causal parser/gate
paths, but several rows call private validators directly.

* The `314231808` row at line 373 calls only
  `_validate_a10_allocation_shape`. It does not call
  `_reconcile_swift_allocation`, `validate_swift_report`, or the active
  `producer_internal_passed` gate. It therefore does not demonstrate that a
  complete current allocation under the Swift 512 MiB bound survives replay.
* Fractional partial prefixes at lines 462, observation-only non-font prefixes
  at lines 470, and the outer causal failure at line 475 call only
  `_a10_validate_swift_case`. They bypass `validate_swift_report` and the
  active gate. The source paths are valid A15 `processCase` shapes, but the
  control does not prove their full report and qualification behavior.

The control needs a complete report wrapper for each positive prefix case.
The wrapper must call `validate_swift_report`, then call the same active-gate
entry used for accepted or observation-only reports. The allocation row needs
the current replay log and closure or must be labeled as shape-only.

## Verified A11 repairs

The comparator source itself closes the first three A10 validator findings.

1. `_validate_a10_allocation_shape` checks current
   `allocation.writtenFilesBytes` against the current policy cap. The
   historical projection in `_project_swift_historical` sets adapted written
   bytes to zero, so the preserved 256 MiB historical validator is structural
   and does not reject the A15 396,071,265-byte persisted bound.
2. `EvidenceBudget` uses separate Rust and Swift stored limits. It calculates
   the next file, stored-byte, and decoded-byte totals before mutating its
   counters or inode set. The A11 schedule includes exact-boundary and
   one-byte-over rows for both producers.
3. `_a11_validate_swift_state` and `_a11_terminal_has_no_success` preserve
   causal `processCase` state: repeat-zero failure may retain shape and case
   fields, a terminal failure cannot retain successful raster fields, and
   completed prefixes remain ordered. Accepted cases still require all three
   repeats. Observation-only cases may retain a non-font `ProbeFailure` while
   remaining unqualified.
4. `validate_swift_report` binds schema 5, producer, A15 source and shared
   source hashes, exact current caps, allocation fields, orientation, and
   current-plus-historical validation. `producer_internal_passed` remains the
   separate active qualification gate.

These repairs are source observations. They do not compensate for the two
actual-control blockers above.

## Source-faithful coverage and limits

The A11 control constructs the relevant A15 shapes, including successful
repeats, failed prefixes, exact-zero coverage, observation-only non-font
failures, and an outer failure with causal shape. The comparator's source
validators now accept those shapes without treating retained failure facts as
successful native evidence. The A15 source and manifest join remain bound to
the frozen 21-row source manifest.

`actual-comparator-control-a11.py:115` reads the font manifest with
`Path.read_text` and does not independently record its expected byte identity.
The future A04 runner must bind the manifest through bounded descriptor reads,
the frozen six input rows, and before/after identity checks. The control source
alone does not prove that its child read observed unchanged fixture bytes.

The package declares Swift stored evidence at 396,071,265 bytes, Swift decoded
evidence at 512 MiB, Rust stored evidence at 256 MiB, and Rust decoded evidence
at 512 MiB. The historical 256 MiB projection remains separate from the
current A15 allocation. These are validator and source-contract observations;
they are not native execution, pixel, codec, playback, or creative evidence.

## Disposition

The A11 comparator validator is suitable for another source review after the
actual control repairs. The A11 control package is not ready for execution.
Repair P1-1 and P1-2 first, then rehash the package manifest and update the
runner's frozen package binding. A same-family review cannot establish
CoreText, CoreGraphics, ImageIO, native PNG, media, GPU, Resolve, or visual
acceptance.
