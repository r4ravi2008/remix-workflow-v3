# Swift native text probe source review A14

## Result

Swift A14 remains rejected before typecheck or control execution.

The three A13 producer findings are closed. The A14 manifest also satisfies the strict A03 build-helper contract.

One P2 documentation defect remains. No P1 remains in the reviewed source.

This was a source-only, same-model-family review. I did not invoke Python, `swiftc`, any control, or the native producer.

## P2 — PNG control documentation claims producer-only ledger behavior

The timeout branch in `png-consumer-control.swift:225-243` sets `mayDeallocate` to false and returns a failed schema-3 case.

`withState` checks that flag once at lines 121-128. No later control path waits for quiescence or deallocates those buffers.

The control has no allocation ledger. It also has no producer failure-evidence emitter.

Its failure output is the normal schema-3 `ControlCase`, when JSON encoding succeeds. Encoding failure emits only `control_encoding_failed`.

Three documents therefore overstate the control:

- `png-consumer-control-schema.md:34-39` claims a surviving ledger charge and bounded failure record;
- `output-schema.md:409-412` repeats those claims;
- `source-rationale.md:453-456` says the control records ledger charge and failure evidence.

The source comment at `png-consumer-control.swift:227` also says storage remains alive “until quiescence.” The code has no later quiescence cleanup.

Describe the implemented boundary instead. A timeout disables deallocation for the remaining control process because a callback may retain the unretained pointer.

The timeout branch returns a fixed schema-3 failed case. It makes no logical-ledger or physical deallocation observation.

This is a proof-scope defect. The timeout branch does avoid freeing storage beneath a queued callback.

## Closed A13 findings

`probe.swift` now routes both `ProbeFailure` and generic errors through `emitFailureEvidence`.

No second producer stderr write remains. Each record reserves room for the fixed truncation marker under the 131,072-byte aggregate cap.

The producer creates `PolicyRecord` after the terminal owner and report rollback reservations. Its observed slot peak therefore includes both final reservations.

`setTerminalReportFileBytes` updates an existing terminal reservation. It does not add another reservation-table slot after that observation.

Producer lifetime claims now match the code. The documents claim retained logical charges and thrown evidence while `run` unwinds.

They no longer claim that unwound producer owners remain physically live until process exit.

## A03 build-helper contract

All 20 manifest rows match their current byte counts and SHA-256 values. The package has no unlisted source or contract file.

The manifest satisfies the frozen A03 source checks:

- `sourceSha256` names `probe.swift`;
- `sharedSourceSha256` names `png-consumer-shared.swift` in both required compile units;
- the four semantic `*ControlSource` keys exist with their canonical filenames;
- `sourceControls` uses the canonical four-control order;
- the duplicate PNG compile-unit lists are identical;
- the duplicate PNG report schemas both equal 3;
- the producer report schema equals 5;
- the remaining control schemas equal 1, 2, and 1.

This validates A14 manifest compatibility with the A03 contract. It does not accept the A03 helper or validate any helper by execution.

## Required successor gate

1. Preserve A14 and this review unchanged.
2. Correct the PNG control comment and the three documentation passages.
3. Freeze and re-review the documentation-only successor.
4. Use a separately reviewed final build-helper successor before any compiler invocation.
5. Typecheck all declared compile units before running any control.

CoreText geometry, CoreGraphics pixels, ImageIO output, cancellation, and producer identity remain unverified.

This review establishes no native feasibility, product integration, playback, hearing, creative acceptance, or full-film result.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `source-manifest-a14.json` | 241 | 11,177 | `215399fbfa0abdf47f874f64b943cf157b7f235525e1e036bc9b4e165f0aa8bc` |
| `probe.swift` | 4,566 | 259,982 | `83e9693be8d53a4bf2a2135f9b6bd643b7be3329129bddf13288ab85ea9f8a01` |
| `persisted-output-budget-shared.swift` | 415 | 15,113 | `8c678f77f0aabf2b7072be39d72c9fd9bae7926461c98d211e103bc305428838` |
| `png-consumer-control.swift` | 280 | 12,511 | `8fe586ebb32a916b929b4f6ebd66ae2166cc2b2874e216aa2e46fd4b55f7ef6d` |
| `output-schema.md` | 412 | 24,321 | `e4b65d7fd0f4beaef0c6ebd5080cf67ee9d441fd2a389528385301ac09604272` |
| `source-rationale.md` | 465 | 26,462 | `9f4746008ab300bac0f2cc0f4173d2f070ac0003c81c0638c184f811ab9c215a` |
| `allocation-ledger.md` | 177 | 9,405 | `4cdfd2351b7bf49c0f27430e719c3c84a67fbd6d1f6365d73a20c2b83f3f8311` |
| `png-consumer-control-schema.md` | 58 | 3,211 | `786b2c6a62d6b940fc3cc3e4ec0d044bd454946f20e668362eb9f7e4c25ee495` |
| `protocol-bound-correction-a14.md` | 28 | 1,605 | `3dc7acd79f659dd3240d583a1f1f4c6539a55dc43effeeedb31dec421bdae8e0` |

The preserved protocol authority remains SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.
