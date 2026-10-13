# Swift native text probe source review A11

## Result

Swift A11 is rejected before typecheck or execution.

Two P1 defects make the required control or producer success impossible. One P2 defect leaves new admission state outside the logical owner ledger.

This was a source-only, same-model-family review. I did not typecheck, build, run a control, start the producer, or call a native framework.

## P1 — the exact-boundary PNG control has an impossible digest

`png-consumer-control.swift:134-140` copies the eight bytes `1...8`.

Their SHA-256 is:

```text
66840dda154e8a113c31dd0ad32f7f3a366a80e8136979d8f5a101d3d29d6f72
```

A11 expects `...f5a111d3d29d6f72`. The changed nibble makes `exact-boundary` fail deterministically. The control then reports `allPassed: false` and exits nonzero.

Restore the A10 digest in a preserved successor. Bind the repaired control source through a fresh manifest and source review.

## P1 — final report publication adds two events after its fixed point

The fixed-point loop at `probe.swift:4266-4301` predicts one terminal `file:report.json` write event. Line 4303 appends that event.

Line 4305 then calls `writeExclusive(..., recordEvent: false)`. That flag suppresses only the file-write event.

`writeExclusiveBuffer` still reserves and releases `failed-file-prefix-scratch:report.json` at lines 2304-2310. Both operations append allocation events.

The final guard at lines 4306-4307 therefore observes two extra events and extra event-log bytes. It must fail with `report_fixed_point` after the report file was written.

Use a dedicated terminal writer. Its prefix scratch and rollback capacity must be admitted before the fixed point. No ledger event may occur after the final report facts are encoded unless the fixed point includes that event.

The owner must stay charged for its real lifetime. Do not release a live scratch buffer merely to avoid the event mismatch.

## P2 — the new reservation dictionaries are uncharged retained owners

`AllocationLedger` adds these maps at `probe.swift:1074-1075`:

```swift
private var cleanupReservations: [String: Int] = [:]
private var rollbackReservations: [String: Int] = [:]
```

Every owner reserve can retain an interpolated label in `cleanupReservations`. Retained result, shape, font, input, and final-report owners make several entries coexist through terminal publication.

Every admitted file can also create a rollback-map entry until commit or rollback. Neither dictionary header, bucket storage, retained key bytes, nor value storage has a logical permit or fixed capacity bound.

This contradicts the A11 claim that every application-owned representation is charged under the 16 MiB logical payload cap.

Prefer reservation tokens whose fixed storage is already owned by each caller. A bounded preallocated tracker is also acceptable if its complete storage and key representation are charged before allocation.

Do not rely on Swift `Dictionary` allocator behavior as an unmeasured owner bound.

## Confirmed storage-budget repair

The shared source derives these exact values from the frozen case schedule:

- 314,231,808 mandatory mask bytes;
- 52,740,096 possible observation-only mask bytes;
- 396,071,265 complete qualification bytes, including the full 16 MiB event-log allowance;
- 201 persisted files;
- a separate 536,870,912-byte Swift persisted-output cap.

The arithmetic matches the A10 review. The new shared contract checks the 512 MiB cap before output-root creation and before native entry.

The removed per-event combined file-plus-log guard is not a separate P2 for this fixed package. The complete schedule proof is below 512 MiB, file writes remain capped, and event bytes have their own 16 MiB cap. A successor should still assert the final combined `writtenTotal` against the persisted-output cap.

`PersistedEventAdmission` protects cleanup and terminal event capacity from ordinary events. The pure budget control covers exact-bound and one-byte-under transitions using the same shared source.

Those source properties do not close the P1 terminal sequence or the P2 reservation-owner gap.

## Preserved scope

The 512 MiB value bounds persisted Swift evidence. It is separate from the producer's 16 MiB logical owner cap, Rust's 256 MiB persisted bound, and the product's 512 MiB logical picture budget.

None of these values measures process RSS, allocator bookkeeping, undocumented native allocations, or physical memory.

A11 remains source-only. It establishes no compiler compatibility, callback behavior, CoreText geometry, CoreGraphics pixels, ImageIO output, producer identity, playback, hearing, creative acceptance, product integration, or full-film result.

## Required successor gate

1. Preserve A11 and this rejection unchanged.
2. Restore the exact bytes-`1...8` control digest.
3. Make terminal report publication ledger-stable after its fixed point.
4. Remove or fully charge both reservation dictionaries.
5. Keep the shared 396,071,265-byte derivation and pure boundary control.
6. Freeze and review the successor before any typecheck, control, or native execution.

## Reviewed identities

All fifteen manifest rows match their current files.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a11.json` | 7,557 | `2450a08ddf3e1ab3434e4f06ecb41ae6d3c131c5cedfe2f53a61dab1ce6b0e67` |
| `probe.swift` | 247,898 | `754d55702da0b0a069af8dad9d8c59bbc230f64b2d32869f2876c4d67c603207` |
| `persisted-output-budget-shared.swift` | 7,890 | `c1934f68bcf46421c1972726378407620695de9a99b60f2e9ef59b6775cc4255` |
| `persisted-output-budget-control.swift` | 4,453 | `48c424aa2dc75b6cd059037e733ee2addfc8234ca161d5fd655e4a5ecd3582cd` |
| `png-consumer-control.swift` | 12,513 | `e9b7770fba7baef0cd87c9e6586174068d665142bf50e7cd69a4b4a552217378` |
| `protocol-bound-correction-a11.md` | 1,467 | `c0272e6b7c7a234e78833338b8d1a45966a88f2bedecf07c0dfa1adecd02eb51` |

The preserved protocol authority remains SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.
