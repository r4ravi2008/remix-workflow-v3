# Swift A10 persisted-evidence budget review A01

## Result

Swift A10 cannot complete its required successful schedule under its 256 MiB written-file cap.

This is a pre-native P1. The mandatory mask files alone require 314,231,808 bytes.

A 512 MiB persisted-evidence cap is numerically sufficient for the bounded qualification schedule. That conclusion requires a separate 16 MiB aggregate event-log cap.

The current Swift producer does not enforce that aggregate event-log cap. Comparator A07 also rejects stored evidence above 256 MiB.

No native call, compiler, comparator, helper, or producer ran during this review.

## Reviewed identities

- `feasibility-swift-a10/probe.swift`: `825e55a74afd696a12261ddff4f3cbe5298cbc4479fe54228aba0f932f486110`
- `text-report-comparator-a07/compare_text_reports_a07.py`: `41b655c2e9fdda7f1d9770201b144e26246d4854fdc9187c24503cfd77f299fb`
- `synthetic-text-cases-a02.json`: `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`
- `text-probe-protocol-a01.md`: `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`

This is a same-model-family source review. It is not an independent model-family review.

## Confirmed source behavior

`probe.swift:1169-1172` fixes the main, guard, clip, and reference dimensions.

`writeMaskEvidence` writes both raw and canonical bytes for every rendered mask (`probe.swift:2234-2241`).

Every non-rejection success renders main and guard masks three times (`probe.swift:3608-3647`).

`te-basic` also renders clip and reference masks on every repetition (`probe.swift:3659-3689`).

`te-fractional-size` renders four main-size controls on every repetition (`probe.swift:3707-3718`).

The frozen input has ten `accepted_shape` cases. Two `observation_only` cases can also succeed and publish all three repetitions.

Every one of the fifteen cases writes a bounded `result.json` (`probe.swift:4080-4088`). The producer also writes two orientation files, two PNGs, one event log, and one final report.

`reserveFileWrite` admits each exact byte count before exclusive creation. A failed write retains its conservative charge (`probe.swift:2181-2231`).

The PNG path temporarily writes a partial file. It removes and rolls back that file before writing the completed PNG.

Therefore one PNG encoded bound is sufficient per PNG. A successful path never retains both versions.

An earlier mask or JSON failure stops the schedule. Its conservative charge cannot exceed the corresponding successful-prefix bound.

## Independent arithmetic

All values below are bytes. Multiplication by two accounts for raw and canonical files.

| Persisted category | Formula | Bound |
|---|---:|---:|
| Ten required main and guard schedules | `10 × 3 × 2 × ((2048×1024) + (2112×1088))` | 263,700,480 |
| `te-basic` clip and reference | `3 × 2 × ((48×48) + (176×176))` | 199,680 |
| Four fractional controls | `4 × 3 × 2 × (2048×1024)` | 50,331,648 |
| Mandatory masks subtotal | sum above | **314,231,808** |
| Two observation-only success branches | `2 × 3 × 2 × ((2048×1024) + (2112×1088))` | 52,740,096 |
| All possible successful masks | mandatory plus observations | **366,971,904** |
| Orientation raw and canonical | `(16×17) + (13×17)` | 493 |
| Two native PNG encoded bounds | `(2048×1024 + 1 MiB) + (13×17×4 + 1 MiB)` | 4,195,188 |
| Fifteen case reports | `15 × 262,144` | 3,932,160 |
| Final report | `4 MiB` | 4,194,304 |
| Allocation event log | proposed aggregate cap | 16,777,216 |
| Qualification-path total | sum above | **396,071,265** |

The total is about 377.723 MiB. A binary 512 MiB cap leaves 140,799,647 bytes, or about 134.277 MiB.

The successful upper-bound tree contains 201 files. That count remains below Comparator A07's 512-file limit.

The 512 MiB value is a persisted-output bound. It is unrelated to the product's 512 MiB logical picture-memory policy.

## Why the current gate fails

Swift A10 declares `maxWrittenFiles = 256 MiB` at `probe.swift:27`.

The protocol repeats the same limit at `text-probe-protocol-a01.md:118`.

Comparator A07 limits stored evidence to 256 MiB at `compare_text_reports_a07.py:29`.

Comparator A07 also requires Swift's reported `writtenFiles` cap to equal 256 MiB at lines 777-795.

The first 314,231,808 mandatory mask bytes already exceed 268,435,456 bytes. PNGs, JSON, and events increase the shortfall.

No native outcome can make a fully qualifying schedule fit. Running the frozen producer would only prove this deterministic cap failure.

## Required successor contract

1. Derive a named successful-output bound from the fixed geometry and schedule constants.
2. Include both observation-only success branches in that derivation.
3. Include orientation bytes, both PNG encoded bounds, fifteen case reports, and the final report.
4. Add a 16 MiB aggregate allocation-event-log cap. Enforce it before every append, including the terminal event.
5. Set Swift's persisted-output cap to 512 MiB only after checking the derived bound against it.
6. Expose both persisted-output and event-log caps in the Swift report policy.
7. Add a startup invariant before output creation and before every native call.
8. Add pure controls for one-byte-under-bound rejection and exact-bound acceptance.

The event-log repair must preserve cleanup records. The derivation must reserve every remaining terminal or cleanup event before ordinary events consume the cap.

Comparator A07 needs a preserved successor. That successor must use a 512 MiB Swift stored-evidence cap and expect Swift `writtenFiles = 512 MiB`.

The successor should retain Rust's 256 MiB report contract. A producer-specific cap avoids weakening the already frozen Rust boundary.

Comparator A07's 512 MiB decoded-evidence and 512-file limits already cover the derived Swift schedule.

The frozen protocol must remain unchanged. A bound successor or correction must state the new Swift persisted-output formula and its disk-only meaning.

Any future Swift runner, gate, inventory, or sidecar must accept the same derived cap. Existing Rust-only 256 MiB controls need no change.

## Review boundary

The arithmetic establishes only source-level feasibility of a repaired persisted-output cap.

It does not establish CoreText behavior, native geometry, PNG output, cancellation, or comparator success.

Native execution remains blocked until the producer and comparator use one repaired, source-bound budget contract.
