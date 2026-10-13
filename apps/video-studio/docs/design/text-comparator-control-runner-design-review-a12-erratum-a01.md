# Comparator runner A12 review erratum

## Purpose

This erratum corrects one evidence binding in the frozen A12 review. It does
not modify the A12 design or the original review.

Original review:
`apps/video-studio/docs/design/text-comparator-control-runner-design-review-a12.md`

Original review SHA-256:
`fa8cddf5f4600571d6a1d76408d232c6ca977bdd68bdc8d10302b188099401c2`

The original table named the older A09-named parent execution file. The repaired
A03 execution file is the authority for the completed parent readback.

## Corrected evidence binding

| Evidence | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| A03 execution output | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-execution-a03.json` | 870,446 | `931a6359701c8586341763c6e1128e0360c1367fc54f2e7e4d23504bbb147e8b` |
| A03 root post-check | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback-runtime-a03-root-postcheck.json` | 858,951 | `cb04626dd19ec505cf5f1bb285e9bab35dc8fb8a9069da59fb65196349d30545` |
| A03 scoped acceptance review | `apps/video-studio/docs/design/text-runtime-readback-parent-scope-acceptance-a03.md` | 6,364 | `579742a8aa93e353e85ab2d18b214399c885d9e2b54283c8ed5bc17dfd83db12` |

The A03 execution output has schema `3` and state
`parent_current_files_readback_passed_unqualified`. The root post-check has
schema `1` and state
`root_external_launch_and_current_readback_passed_unqualified`.

The post-check records `externalPreflightSealMatched=true`,
`readerArgumentVectorsMatched=true`,
`readerSourceAndInterpreterMatched=true`, seven fresh source rows, 1,562
unique regular files, and 68,299,969 regular-file bytes.

The A03 execution records 1,548 installed rows, 45 fixed divergences, 995
strict declared matches, 508 independently observed undeclared rows, 11,000
input opens, and 69,901,069 read bytes.

Both records keep `authorizesExecution`, `comparatorExecuted`,
`nativeExecution`, `loadedImageAttestation`, and `creativeAcceptance` false.
The A03 evidence is therefore a completed, bounded, unqualified filesystem
readback. It does not prove loaded code, comparator execution, native support,
provider origin, playback, listening, or creative approval.

## Scope correction

Replace the A12 review's older A09-named parent execution binding with the A03
execution and root post-check above. Keep the A09 report, overlay, diagnostic,
and A03 launch receipt bindings unchanged. The A12 design remains unchanged.
