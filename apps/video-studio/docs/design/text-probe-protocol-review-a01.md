# Native text probe protocol review A01

## Disposition

The protocol is **green for continued isolated Rust and Swift probe authoring**.

I found no P1 protocol defect. The main, guard, clipped-reference, and asymmetric-orientation equations are numerically correct.

Two evidence details remain pre-execution conditions:

1. Freeze the exact independent native-image orientation observation method and its expected record.
2. Freeze the orientation buffer's initial padding value and exact unchanged-padding assertion.

Those details can be completed in the frozen source and JSON schema review. No native call should run before they are explicit.

This review does not establish native feasibility, product support, encoded output, playback, hearing, creative acceptance, or film text.

The reviewed protocol is `text-probe-protocol-a01.md`, SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.

All available reviewers use the same model family. This review is artifact-separated, not cross-family review.

## Numeric verification

### Generous main and guard buffers

The main baseline conversion is correct:

```text
H - baseline_y = 1024 - 768 = 256
native row = H - 1 - y = 1023 - y
```

The guard dimensions and translated baseline are correct:

```text
WG = 2048 + 2 * 32 = 2112
HG = 1024 + 2 * 32 = 1088
guard baseline = (64 + 32, 768 + 32) = (96,800)
native guard baseline y = 1088 - 800 = 288
```

The inner extraction is also correct:

```text
native guard row = 1087 - (y + 32) = 1055 - y
```

The inner interval `[32,2080) x [32,1056)` has the exact main dimensions, 2048 by 1024. Comparing every main byte with this inner region is decisive for the declared translated-box experiment.

The zero outer guard is a fixture observation only. The protocol correctly avoids turning it into a universal antialias-padding claim.

### Deliberate 48-by-48 clipping control

The clipped-box baseline is correct:

```text
48 - 36 = 12
```

The 176-by-176 reference is exactly the clipped box plus a 64-pixel border on every side. Its translated baseline is correct:

```text
(4 + 64, 36 + 64) = (68,100)
176 - 100 = 76
```

The inner reference row equation is correct:

```text
175 - (y + 64) = 111 - y
```

The requirement for nonzero reference coverage outside the inner 48-by-48 region proves that this named case exercises intentional clipping. It does not generalize clipping behavior beyond that bound case.

### Asymmetric orientation and stride control

The 13-by-17 control has a 16-byte stride and 272 raw bytes. A native rectangle at `x=2..5` and `y=3..7` maps to editor rows:

```text
top_y = 17 - (3 + 5) = 9
```

The expected top-left bounds `(2,9,4,5)` and 20 bytes of value 255 are correct when antialiasing is disabled.

This asymmetric shape detects row reversal, stride use, and width-versus-stride mistakes. The report may include the 221 visible pixel samples, but it must separately preserve or hash all 272 raw bytes and the 51 padding bytes.

Before execution, initialize padding to an explicit sentinel and require every padding byte to retain that value. Zero initialization is acceptable only if the protocol records zero as the pre-draw value and separately proves no padding write. A nonzero sentinel is more decisive.

## Classification and source bindings

The protocol binds the correct A02 input identity: 15 cases, 14,706 bytes, SHA-256 `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`.

Its case handling preserves the declared classes:

- accepted cases require their declared positive or exactly-zero coverage outcome;
- `ascii-control`, `missing-emoji`, and `missing-unassigned` must reject the whole item;
- only actual run-font mismatch or glyph zero may satisfy a rejection;
- no rejection case may publish a raster;
- combining-only and ZWJ cases remain observations regardless of their result.

The protocol also binds the exact font manifest, pinned source commit, font bytes, and license. Source text, UTF-8, UTF-16BE, language, direction, and size remain input authority. Native observations cannot rewrite those values.

The Rust and Swift separation is adequate for implementation comparison. Both still share CoreText and CoreGraphics, so agreement is not independent typography-engine proof.

## Setter evidence boundary

The setter evidence claim is accurate.

Several CoreGraphics font switches lack matching public getters. The probes therefore bind the exact source and call trace plus observed pixels. They must not claim inaccessible native-state readback.

The antialias-disabled fractional-size experiment is the decisive effect control. It requires binary coverage and a changed hash.

Smoothing, subpixel-positioning, and subpixel-quantization toggles are observational controls. Equal hashes must remain equal observations. Equal results do not prove that a switch has no effect on other fonts, sizes, contexts, or systems.

No additional getter evidence is required where the public API provides none.

## Caps and admission

The declared dimensions use these payload sizes:

| Buffer | Bytes |
| --- | ---: |
| Main 2048 by 1024 | 2,097,152 |
| Guard 2112 by 1088 | 2,297,856 |
| Clip 48 by 48 | 2,304 |
| Reference 176 by 176 | 30,976 |
| Orientation raw 16 by 17 stride | 272 |

Main and guard coexist at 4,395,008 bytes. The 16 MiB logical cap is plausible only when the implementation avoids full canonical mask duplicates and releases repeat/toggle buffers as declared.

Before execution, the source review must include one checked worst-case ledger. It must cover retained observations, report bytes, both fonts, copied native font bytes, maximum table copy, strings, UTF-16, runs, glyph arrays, masks, and output buffers simultaneously live.

If a native and canonical buffer coexist, both must be charged. Exceeding 16 MiB must reject before allocation rather than silently widening the cap.

Native framework internals and allocator overhead remain explicitly unmeasured. The protocol does not claim process peak memory.

## Remaining pre-execution conditions

The authors may continue writing source now. Before the first native call, freeze and review all of these items:

1. Exact Rust and Swift source hashes, dependency features, locks, compiler, SDK, target, and executable identities.
2. Final JSON schemas and wrapper fields, with exclusive output creation and failure retention.
3. Exact API and file format used for the separate native-image orientation observation.
4. Why that orientation observation does not reuse the same copied row-reversal formula.
5. Orientation buffer initialization, padding sentinel, and unchanged-padding assertions.
6. The complete per-case action table for shaping, rejection, drawing, three in-process repeats, and fresh-process replay.
7. The exact setter-call schedule and toggle isolation for every control.
8. The checked worst-case 16 MiB allocation ledger and release order.
9. Comparator rules that ignore only producer identity, paths, and timing.
10. Preservation rules for partial, failed, and unexpected observations.

Any disagreement in face identity, fallback, ranges, matrices, row orientation, guard extraction, native switches, or alpha bytes must remain a recorded failure. It must stop product integration.

## Verdict

The protocol is sufficiently precise to continue authoring both isolated probes. Its numeric transforms, case classes, caps, and evidence boundaries are sound.

Execution remains blocked until the two orientation details and all listed source, schema, build, and allocation records are frozen. Passing execution would establish bounded feasibility on the bound host only.
