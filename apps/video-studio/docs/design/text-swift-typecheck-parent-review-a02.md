# Swift A10 compiler-only parent review

The A10 producer and direct PNG callback control passed typechecking. No Swift executable was built or run.

Root read the complete A09-to-A10 source and contract changes. Root also read the new failed-publication control and additive contract correction. All ten manifest rows matched. The eight preserved A09 rows also matched.

Root reviewed the complete compiler wrapper A03 and its independent source review before invoking it. The wrapper used Apple Swift 6.2.1, SDK 26.1, target `arm64-apple-macosx26.0`, and a fresh module cache. The producer invocation included the exact imported C header.

The producer typecheck returned zero in 23.83 seconds. Its only warning concerns the unchanged `canonicalReleased` variable. The callback control typecheck returned zero with an empty log. Root independently rechecked all fifteen source, wrapper, Python, compiler, and SDK-settings identities. Before, after, and current observations match.

The evidence root is `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/`:

- `swift-typecheck-attempt-a02/report.json`: 21,884 bytes; SHA-256 `eb6c73f57a38f7410f2cee32654edb4819d01b9146711732fca5639500af0e92`.
- `swift-typecheck-attempt-a02/producer.log`: 535 bytes; SHA-256 `e6f2f777c82ae7fcaf73f8c3f5ec98c67cded1d07673de8d4904ea360bdc1df7`.
- `swift-typecheck-parent-readback-a02.json`: 3,046 bytes; SHA-256 `79fa4e57c0a95e2e8c729e44c69ef0d29fd94dcb0af6a348ce35a71756f1d6f5`.

This confirms compiler acceptance of the producer and callback-control source groups. The separate failed-publication source control remains untypechecked and unexecuted. Loaded compiler attestation, linking, native ownership, raster output, and publication behavior remain unverified.

Root subsequently found a separate storage-admission defect before native execution. Mandatory raw and canonical raster files require at least 314,231,808 bytes. Swift A10 and Comparator A07 each cap stored evidence at 268,435,456 bytes. The source arithmetic is saved separately. The native gate remains absent while a bounded successor policy is reviewed.
