# Native run preparation A02 parent review

A02 remains unexecuted and is rejected before gate creation.

The parent read the complete gate builder, runner, sealer, contract, and independent review.
Their identities match the completed independent review. No helper or native child was started.

## P1: release build and PNG control steps are mixed

`run_rust_native_probe_a03.py:764` assigns release build steps to `steps`.
Line 910 replaces `steps` with the two PNG control steps.
Lines 1023 and 1030 then compare the PNG test build with the release build command and environment.
These commands differ by construction. An otherwise valid gate therefore fails before launch.

Use distinct release build and PNG control variables throughout the reconstruction.
Preserve this helper and its original review. Save the repair as a successor.

## Comparator prerequisite

The gate builder and runner bind Comparator A01.
Its independent source review rejected three P1 and five P2 findings.
The successor must bind an accepted comparator, its changed contracts, and its bounded control evidence.
Comparator agreement cannot qualify probes until that source and control review completes.

## Scope

The corrected source substantially improves gate closure, log bounds, exclusive directory ownership,
terminal report bounds, and orientation sidecar authority. Those improvements remain source observations.

The A02 execution gate and A03/A04 attempt directories remain absent.
The Rust main producer, ImageIO output, font shaping, orientation observer, product integration,
normal-speed playback, hearing, and creative acceptance remain unverified.

## Reviewed identities

| Source | SHA-256 |
| --- | --- |
| prepare_rust_native_gate_a02.py | d95cfaa45ee59d36e7ab1b73e06cef1c2f1fdce70b90f5e3be3407360c2000b2 |
| run_rust_native_probe_a03.py | 1dcda8040b85c30786456a499c9ffba5a3de4720b47e8eb0fd53fe43fffe6f4d |
| seal_native_orientation_sidecar_a02.py | ad4a3a835d32195713599483bc3627d1f5d85cefa3e0787203ba5c854b00e22b |
| text-native-run-preparation-a02.md | cccd90432ba562e0e15a4cc816fd9d6fd7eb9507e77bc1f1fcaa3540ec9ca647 |
| text-native-run-preparation-review-a02.md | 65127168dc0efbe1f8e9e7f67fec361ac9fe1c8aea0f3b130a43719f50837055 |
