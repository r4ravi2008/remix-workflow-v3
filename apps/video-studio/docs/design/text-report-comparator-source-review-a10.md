# Comparator A10 independent source review

## Status

Comparator A10 is not ready for control execution or native qualification.

This source-only review found four P1 blockers. The A10 package remains frozen,
unexecuted, and unqualified.

The review read the preserved A09 parent findings and independent review. It
also read the complete A09-to-A10 comparator and control changes, all A10
contracts, and the frozen Swift A15 source contract.

The reviewers use the same model family. This review is not blind or
cross-family evidence.

## Frozen identities

| Artifact | SHA-256 |
| --- | --- |
| `package-manifest-a10.json` | `347d5047d91aa34041bc112d234071466583c15aaf9267ae42c459c4c4df7666` |
| `compare_text_reports_a10.py` | `f3d34fc015891cce0a0bfed5945de59f56410730e74d0db61ab7c4004acd32ab` |
| `actual-comparator-control-a10.py` | `1cce87390afa509fac3310bf008fb351a637b4c12a2fa9a37249ffc567b9ccb6` |
| `required-evidence-control-a10.py` | `0144720e2afca407bd8b4e1dad32452348daa02659ceba5883473a5f727d28c7` |
| `README-a10.md` | `ed1028e555d76623f473e9f4aabe296bc25428effec77a877bbb3af136b9dfa0` |
| `output-schema-a10.md` | `7f6dd3d5ea44be3e7bc2736a3095b53af02d6c804aa12142d4f8f8ee0282f01f` |
| `source-rationale-a10.md` | `165ac08591fa6245fd08bb576044413de4783645f2fc360f5ddb5f799b3d039f` |
| Swift A15 `source-manifest-a15.json` | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| Swift A15 `probe.swift` | `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01` |
| Swift A15 `persisted-output-budget-shared.swift` | `8c678f77f0aabf2b7072be39d72c9fd9bae7926461c98d211e103bc305428838` |

Every A10 package row matches the frozen package manifest.

## P1: the historical projection still rejects an honest A15 allocation

`_validate_a10_current_swift_policy` correctly validates the current 512 MiB
written-file cap. `_project_swift_historical` then replaces only the historical
policy cap with 256 MiB. It leaves `allocation.writtenFilesBytes` unchanged.

The preserved validator compares that current allocation value against the
projected 256 MiB cap. An honest full A15 result therefore fails
`allocation_file_cap` before qualification.

The failure is not hypothetical. The source-bound A15 schedule requires these
mask files before observation-only masks or other files:

- 10 accepted cases, three repeats, raw and canonical main plus guard:
  263,700,480 bytes;
- `te-basic` clipped plus reference files: 199,680 bytes;
- fractional controls: 50,331,648 bytes.

Those required files total 314,231,808 bytes. This already exceeds the
historical 268,435,456-byte limit.

Move the current written-file bound into the current A15 validator. The
historical structural adapter must not reapply its obsolete allocation cap to
the current allocation value.

## P1: the evidence reader cannot admit the required A15 mask graph

`MAX_STORED_EVIDENCE_PER_RUN` remains 256 MiB. `collect_swift_masks` includes
every successful repeat and fractional control. `scan_mask` opens both raw and
canonical files and charges their stored sizes to one report budget.

The required 314,231,808-byte subset above exceeds this comparator limit.
Observation-only success masks add another 52,740,096 bytes. The A15 complete
persisted-output bound is 396,071,265 bytes.

A valid A15 report cannot reach raster comparison under the current limit.
Use a source-bound Swift evidence limit that admits the exact A15 schedule.
Keep Rust and Swift limits explicit if their evidence domains differ. Add a
positive exact-bound control and a one-byte-over rejection.

## P1: the state parser rejects truthful A15 failure evidence

The A10 state rules do not match `probe.swift::processCase`.

The producer stores `retainedShape` before raster completion. It stores case
main, guard, comparison, and fractional controls as each operation completes.
A later operation can fail before a `successfulRaster` record is appended.
Those case-level records are causal failure evidence.

A10 rejects several truthful producer states:

- A repeat-zero failure can retain shape, main, guard, comparison, toggles, or
  failure raster. A10 forbids these case-level records.
- An outer failure can retain `error.shape`. A10 forbids `shape` when the
  repeat array is empty.
- A fractional failure after a successful prefix has only the controls emitted
  before the failure. Both `_validate_a06_extras` and
  `_a10_validate_case_level_success` require all 12 controls.
- The producer maps any `ProbeFailure` in an observation-only case to
  `observation_only_rejected`. That result can occur after repeat zero and can
  use error codes other than the two font errors. A10 requires one repeat,
  rejects retained prefix evidence, and permits only the two font errors.

The parser must preserve these records without qualifying a failed case.
Model a completed prefix separately from terminal causal evidence. Validate
fractional controls as the exact emitted prefix. Keep the active gate false for
unexpected failures. Keep observation-only results explicitly unqualified.

## P1: the actual-function control cannot reach its declared schedule

`allocation_controls()` creates a positive policy cap map without
`reservationTableObservedPeakSlots`. `_validate_a10_allocation_shape` indexes
that required key. The first allocation positive therefore raises `KeyError`
instead of completing the control.

The slot-peak mutation changes only the allocation value. The policy value
would remain different. After adding the missing key, the mutation would fail
with `swift_reservation_binding`, before the expected
`swift_reservation_peak_slots` result.

The control schedule also omits these decisive cases:

- a positive exactly-zero coverage case;
- an observation-only rejection with a producer-valid non-font error;
- source-faithful partial repeat-zero and fractional-prefix failures;
- a current allocation above 256 MiB but below the 512 MiB cap;
- an evidence graph above the inherited 256 MiB reader cap.

Repair the positive policy object first. Mutate policy and allocation together
when testing slot range, or expect the binding failure. Exercise the complete
parser and active gate with producer-shaped records.

## A09 finding disposition

A10 makes useful source-level progress:

- the undefined active Swift state-validator call is repaired;
- current optional Swift fields remain omitted instead of becoming JSON null;
- the 16 MiB logical cap and 512 MiB persisted-output policy are explicit;
- reservation-table peak, owner, key, scratch, and baseline fields are bound;
- allocation replay rejects a release below the permanent baseline;
- Rust control stability removes repetition-specific locations while retaining
  decoded hashes and other semantic fields;
- the complete 21-row Swift A15 source manifest is joined and rehashed.

The historical allocation check, evidence cap, failure-state grammar, and
broken actual control prevent those repairs from qualifying A10.

## Verdict and limits

Preserve Comparator A10 as a rejected source package. Prepare a new successor
before running comparator controls or admitting native reports.

No comparator or control source was imported or executed during this review.
No compiler, native producer, CoreText, CoreGraphics, ImageIO, PNG decoder,
media operation, GPU, or Resolve operation ran.

This review does not establish native text feasibility, product integration,
orientation, playback, hearing, or creative acceptance.
