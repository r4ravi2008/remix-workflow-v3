# Swift native text probe source review A15

## Result

Swift A15 closes the remaining A14 P2. I found no P1 or P2 in the reviewed source closure.

The package is source-ready for the separately reviewed build-helper and compiler gate.

This was a source-only, same-model-family review. I did not invoke Python, `swiftc`, any control, or the native producer.

## A14 P2 closure

The timeout branch still sets `ControlLifetime.mayDeallocate` to false. It returns a failed schema-3 `ControlCase` without later cleanup.

The revised source comment now states that exact behavior. It no longer claims a later quiescence cleanup.

The three revised contract passages match the control:

- the pure control has no allocation ledger;
- the pure control has no producer failure emitter;
- timeout disables storage and scratch cleanup for the remaining control process;
- successful JSON encoding writes the schema-3 report to stdout;
- the failed case then causes a nonzero exit;
- encoding failure writes only `control_encoding_failed` to stderr.

The timeout branch remains ownership-safe. It does not free storage while a queued callback may hold the unretained pointer.

## Preserved producer behavior

`probe.swift` is byte-identical to A14. Its SHA-256 remains `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01`.

The manifest package is `feasibility-swift-a15`. Its producer remains `independent-swift-coretext-a14`, matching the unchanged report literal.

The bounded producer emitter, terminal policy construction, report schema 5, and runtime logic are unchanged.

## Build-helper manifest contract

All 21 manifest rows match their current byte counts and SHA-256 values. The directory has no unlisted source or contract file.

The strict joins remain complete:

- `sourceSha256` names `probe.swift`;
- `sharedSourceSha256` names `png-consumer-shared.swift` in both required compile units;
- exactly four semantic `*ControlSource` keys bind their canonical filenames;
- `sourceControls` uses the canonical four-control order;
- both PNG compile-unit lists are identical;
- `pngConsumerControlSource` names the PNG primary;
- both PNG schema declarations equal 3;
- the producer schema equals 5;
- the other source-control schemas equal 1, 2, and 1.

This establishes source compatibility only. The final build helper still requires its separate review.

## Remaining gates

1. Preserve A15 and this review unchanged.
2. Accept the final build-helper successor independently.
3. Typecheck every declared compile unit.
4. Run all four bounded controls before the native producer.
5. Bind any producer run to the frozen source, compiler closure, inputs, and executable.

CoreText geometry, CoreGraphics pixels, ImageIO output, cancellation, and producer identity remain unverified.

This review establishes no native feasibility, product integration, playback, hearing, creative acceptance, or full-film result.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `source-manifest-a15.json` | 250 | 11,656 | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| `probe.swift` | 4,566 | 259,982 | `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01` |
| `png-consumer-control.swift` | 282 | 12,649 | `0be8296ca50746f1a4828453568c9bed2646010e46e42e322ac9aa355b408727` |
| `png-consumer-control-schema.md` | 61 | 3,446 | `4382a3b5f28964911d022ffea375191f0db8b42cb69f149ef4a80b1bc9d941b7` |
| `output-schema.md` | 416 | 24,612 | `caeed5423d2f33645a99363aed99285b1835adb24d21961fd41e4e23f31b0139` |
| `source-rationale.md` | 468 | 26,679 | `8a2108aed6ca59acab4d2e6c87e5cbd43336b2a7eacf9295de7b46a040a2d567` |
| `protocol-bound-correction-a15.md` | 16 | 889 | `69e9f495a28638d9a55fb7d2c6b8d4eeb60d912f204a21aa74037d7ea54107b0` |

The preserved protocol authority remains SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.
