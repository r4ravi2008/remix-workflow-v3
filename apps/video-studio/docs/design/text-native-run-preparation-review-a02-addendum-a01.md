# Rust native-run preparation review A02 addendum A01

## Corrected disposition

The frozen A02 review missed one P1 source defect.
Its green disposition is withdrawn for `run_rust_native_probe_a03.py`.

The frozen review remains byte-identical at SHA-256
`65127168dc0efbe1f8e9e7f67fec361ac9fe1c8aea0f3b130a43719f50837055`.
This addendum preserves the original record and states the correction separately.

The A02 execution gate and A03/A04 run directories remained absent during discovery.
No helper, producer, observer, compiler, native framework, GPU, or Resolve process ran.

## P1 — release-build validation reads the PNG-control step

`run_rust_native_probe_a03.py:764` stores the release build list in `steps`.
`run_rust_native_probe_a03.py:910` overwrites `steps` with the PNG-control list.

`run_rust_native_probe_a03.py:1023` then compares `steps[0].argv` with the release build command.
Line 1030 compares that same PNG-control step with the release build environment.

The PNG-control step is a Cargo test build.
The release step is the Cargo producer build.

The commands and environments must differ.
An otherwise valid gate therefore always fails before run-directory creation.

This defect is fail-closed.
It cannot launch the native producer or publish a false attempt result.

## Source-only successor

The repair preserves every A02 byte and creates these separate successors:

- `prepare_rust_native_gate_a03.py`;
- `run_rust_native_probe_a04.py`;
- `seal_native_orientation_sidecar_a03.py`;
- `text-native-run-preparation-a03.md`.

The successor keeps `release_build_steps` and `png_control_steps` distinct.
All later release command and environment checks use `release_build_steps`.

The successor accepts one reviewed versioned comparator package at gate creation.
It derives closed source, schema, rationale, and evidence-control roles from that package.
This avoids binding the rejected comparator A02 package into another source successor.

Comparator A02 remains unqualified.
Its fresh `alpha_raw` comparison included absolute run paths.
Its controls exercised replicas instead of the production validators.
An accepted successor must bind the actual accepted Swift producer schema.

The successor sources remain unexecuted.
Their source hashes are recorded in the A03 contract after source freeze.

## Review boundary

This addendum acknowledges the missed defect and the intended narrow repair.
It is not an independent green review of the successor sources.

Root must read the full successor sources and generated gate before execution.
Native API behavior, text output, observer output, and product integration remain unverified.

This correction uses the same model family.
It is not a blind or cross-family review.
