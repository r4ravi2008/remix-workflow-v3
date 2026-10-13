# Comparator A11: parent source findings

Root read all 1,320 lines of the A10-to-A11 patch against the reviewed A10 baseline.
Root matched all six A11 package files to the frozen manifest.
The independent source review remains pending.
No A11 comparator or control was imported or executed.

| Artifact | SHA-256 |
| --- | --- |
| Comparator A11 | `e94b6ea3fb671ba66d413594060959bb5ec86f7e4fcffb8e774ababaeb438520` |
| Actual controls A11 | `3e1d293a57e1b617f39702d4d599f8520f6828860daba3fe59cd781f0b7c49a2` |
| Required controls A11 | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| Manifest A11 | `d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872` |
| Parent-read patch | `e041b2a95941f5be97f52a18946512ab376ee84e4cf727c0683985ea926df831` |

A11 separates current allocation from historical structural validation.
It also adds producer-specific evidence budgets and preserves more causal failure fields.
These changes remain source-only.

## P1: actual controls still predict the wrong errors

Three negative fixtures fail before their declared expected error.

1. The baseline mutation changes only allocation.initialReplayBaselineBytes.
   The unchanged policy baseline causes swift_reservation_binding before swift_reservation_baseline.
2. The peak mutation changes only allocation.reservationTableObservedPeakSlots to 257.
   The unchanged policy peak causes swift_reservation_binding before swift_reservation_peak_slots.
3. The omitted fractional control reaches _a11_validate_toggle_prefix first.
   That function raises toggle_count, while the fixture expects swift_toggle_schedule.

Keep separate binding-mismatch and aligned policy/allocation range controls.
Assert the actual first error without weakening the production validators.

## P1: repaired branches still lack complete-path controls

The above-256-MiB allocation control calls only allocation-shape validation.
The new fractional, observation-only and outer-causal controls call only the case helper.
They do not exercise the complete report parser, historical projection and active gate together.

Use source-faithful complete reports for each repaired branch.
Check the current 314,231,808-byte allocation through the complete parser.
Check causal failed repeat zero, all fractional prefixes and all non-font observation prefixes.
Check the outer failure with retained causal shape.
Preserve truthful diagnostics and keep failed-report qualification false.
Observation-only evidence must remain unqualified as native support.

## P2: prerequisite prose contradicts actual build evidence

README-a11.md calls the A15 source package unbuilt and unexecuted.
The same document records its compiler build and four executed controls.
State that those bounded prerequisites passed while the native producer remains unexecuted.

Preserve A11 and repair A12 separately.
Actual controls and native execution remain pending.

## Completed peer review and subsequent metadata drift

Root read the completed source peer review with SHA-256 `0f8ac005d4fe790dbbc7a39cb602e0d8385cac6b3df1c7e0f2a3ac092fe33bd7`.
The peer confirms both P1 control findings.
The earlier statement that peer review was pending records the state when this parent review began.

After that source freeze, the author corrected the README in place and refreshed its manifest hash row.
The manifest retained the old 6,682-byte count for the corrected 6,802-byte README.
The current A11 manifest is therefore invalid as authority.
The three comparator and control source files remain byte-identical to this review's subject.

The original README and manifest were reconstructed from the preserved A10 files and this review's exact patch.
Root rehashed both reconstructed files and matched their original SHA-256 values.
Root also matched all six original manifest rows using the reconstructed README and five unchanged source or contract files.
The original and changed metadata have separate saved snapshots.

| Preserved metadata | SHA-256 |
| --- | --- |
| Original README, 6,682 bytes | `1eb295208fd4cbc65215e796cedefa32261edb227427951cb7aaf6ad08441555` |
| Original manifest | `d95e76834d427d8b44000cc35995808d975a0be8273fadcd8658de18bd824872` |
| Changed README, 6,802 bytes | `cacf608a6ba6a1880ea20064ed5762be89d864c60a82d2d3027df937355bbb74` |
| Invalid changed manifest | `fde359966503739aa5225cf911e3e75ff61e74b04396343612d5ff323ce064a8` |
| Measured provenance note | `18c40efd350d65494436c45ffe66cd7fdd363117d56dc6c78cfbbb7cae6c0afa` |

A12 controls now have a separately saved source successor.
Its package manifest inherits the invalid changed A11 manifest and cannot authorize execution.
A narrow manifest and contract successor must bind the actual source files directly.
No comparator, control, or native process ran during preservation or reconstruction.
