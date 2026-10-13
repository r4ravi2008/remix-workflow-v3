# Swift native text probe source review A10

## Result

A10 closes the P1 and three P2 findings from the A09 source review.

No source-level P1 or P2 finding remains. The exact producer and direct PNG control are ready for isolated compiler-only checks.

The failed-publication control is source-ready for its own compiler-only check. The current typecheck wrapper does not compile that separate source control.

This was a read-only, same-model-family review. I did not typecheck, build, execute a control, start a producer, or call a native framework.

## Reviewed identities

All ten `source-manifest-a10.json` rows match the current package files.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `probe.swift` | 239,672 | `825e55a74afd696a12261ddff4f3cbe5298cbc4479fe54228aba0f932f486110` |
| `png-consumer-shared.swift` | 6,693 | `22c66166890efc6dfd2e2076d1117139e1b7481f71a4e63df676ab9b2e185866` |
| `png-consumer-control.swift` | 12,513 | `78983b3869c2e651ba66f42bc830afa8e3d42b41a73c2d0817ae45d54855fd99` |
| `output-schema.md` | 20,867 | `1609c628769c7187632a7c360ec934fcb816d28c6e8d4e2238a14543b622e84e` |
| `source-rationale.md` | 23,335 | `9f79e99b18fefc7eb31e31acd610a05b42bb9ad4c862cb79f884751f83c8b4f0` |
| `allocation-ledger.md` | 6,056 | `fafddf2df0cd0225339aa9844a9d34a798aa48233a1208c39b1584e1e36773ca` |
| `png-consumer-control-schema.md` | 3,073 | `95891dadff847014c8fcac89843f49ce97f10b09185442ca9d41c3087bda8925` |
| `alpha-context-shim.h` | 936 | `45bab2f2be3022da7fda10884197d4e98b709bf9ce60dcb983d7f13d6aac4144` |
| `failed-publication-control.swift` | 5,121 | `2a40e9a29eb754b33fb30a1513752522a2cfe0531059632d9c566b12f21400e9` |
| `failed-publication-control.md` | 1,437 | `7d3536dcc0e974fb70e53a6a06def3fc541de4d7ca54c04a97fd9565167242d5` |

The manifest is 5,101 bytes with SHA-256 `82cc90e4a8a6783c033d1e0b2482ccc3d2a69f387010172fc20c3d22425c36e6`.

The external correction is 910 bytes with SHA-256 `fd6b5f01f75211ef05bf1d4e28c9d72368c8d461abe97594f3db7c7ee212e516`.

## Closed A09 findings

All three text-matrix writes now use the SDK-imported `context.textMatrix` property setter.

`maxEvidenceEntries` now derives 23 from the `13 + 6 + 2 + 2` publication formula. The owner bound and runtime validator use that value.

`matrixOwnerBound()` and `imageBoundsOwnerBound()` now charge their separately validated state strings.

`policy.caps` now includes `failedFilePrefixScratch: 65,536`. The manifest now assigns header authority to the future exact build closure.

The previously low-severity diagnostic placeholders now interpolate their actual labels and indices.

## Failed-publication source control

The source control declares exact 23-key maximum shapes for failed partial-file and failed complete-file publication.

Its key sets match the producer's base capture, six prefix facts, two path facts, and two terminal facts.

The control does not call the producer or shared publication functions. Its report cannot prove that an actual failure emits those keys.

The contract states that limit. A later native control must induce both failures and compare the actual retained key sets.

## Contract correction and compiler boundary

`output-schema.md` incorrectly says `policy.caps` records the 23-entry limit. `contract-correction-a10.md` explicitly supersedes that sentence.

The root readiness record binds the correction. Every later build and proof closure must continue binding it.

`run_swift_typechecks_a02.py` compiles the manifest's producer and PNG-control groups. It does not compile `sourceControls`.

A separate reviewed invocation must typecheck `failed-publication-control.swift`. That result remains pending.

The C header import, property setter spelling, and all other SDK calls remain compiler-unverified until the exact A10 typecheck succeeds.

## Scope boundary

This verdict permits compiler-only checks. It does not permit native producer execution or either control's execution.

It does not establish CoreText shaping, CoreGraphics alpha semantics, ImageIO output, publication failure behavior, or loaded producer identity.

Playback, watching, hearing, creative acceptance, product integration, and the full film remain unverified.
