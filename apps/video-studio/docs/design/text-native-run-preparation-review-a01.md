# Rust native-run preparation review A01

## Disposition

The saved Rust build manifest, source bundle, and observer closures rehash correctly.
I found no factual error in their current recorded values.

The native runner and orientation-sidecar path are **not ready for gate release**.
Three P1 authority defects and three P2 evidence defects remain.

The native execution gate and both run directories are absent. No probe or observer ran during this review.

The separate PNG admission review also found a producer P1.
That finding independently blocks Rust and Swift native execution.

## P1 — the runner records and authorizes different gate reads

`run_rust_native_probe_a01.py:84` observes and hashes the gate through one descriptor.
Line 87 opens the pathname again and parses those later bytes.

The parsed authorization can therefore differ from the recorded `gate` identity.
A replace-and-restore sequence can also make the final pathname observation equal the first one.

Parse the exact bytes read through the observed descriptor.
The runner must derive the recorded identity and authorization object from one bounded read.

The A02 runner has the same defect. Its only intended difference is the fresh run path.

## P1 — the runner does not enforce the required gate closure

The runner requires only its own path somewhere in `gate.bindings`.
It does not require an exact schema, binding set, or cross-field joins.

The separate `gate.binary` descriptor need not equal a binding row.
The runner verifies it only before launch unless the gate author also listed it.

The `gate.buildManifest` descriptor is passed to the child without an independent verification.
It also need not equal a binding row.

The source-bundle manifest, source-root relationship, observer closure, and comparator can be absent.
Unexpected binding rows are accepted.

An incorrectly authored gate can therefore launch native code despite an incomplete proof closure.
The comment at lines 90-91 does not enforce that contract.

Before release, define and validate one exact gate schema and allowlist.
Join `binary`, `buildManifest`, `sourceRoot`, source bundle, runner, observer closure, and comparator to exact binding rows.
Recheck every execution input after the child closes.

## P1 — the child inherits unbound dynamic-loader state

`subprocess.Popen` receives no explicit environment.
The child inherits all variables from the parent process.

Dynamic-loader variables can add or redirect code without changing the main executable SHA-256 or Mach-O UUID.
The producer's loaded-main-image check does not detect that interposition.

Launch with a minimal explicit environment.
Reject unapproved `DYLD_*`, `LD_*`, and framework-path variables.
Record the exact admitted environment in the attempt report.

## P2 — exclusive output ownership is not retained or evidenced

The driver creates `RUN` exclusively and checks that `probe-output` is absent.
The exact child then creates `probe-output` exclusively.

However, the driver retains no descriptor for either directory.
It records no directory device or inode before and after execution.
Inventory later resolves the pathname and can follow a substituted directory.

The sidecar then writes `run.exclusive: true` from this pathname history.
It does not carry evidence that the captured artifacts belong to the originally created directory.

Retain the run-directory descriptor through closure.
Capture the child output-directory identity after creation and before inventory.
Use descriptor-relative, no-follow reads where available.
Recheck both directory identities before saving the attempt and sidecar.

The external A06 observer correctly keeps `exclusiveRunEstablishedHere: false`.
That truthful label does not repair the missing producer-run evidence.

## P2 — output bounds are applied after allocation or writing

`producer.log` can grow for 300 seconds without an active byte limit.
Its first size rejection occurs during post-run observation.

The output inventory applies its total-byte and file-count caps after files already exist.
Directory count and traversal work have no bound.

`write_json` builds the complete string and byte buffer before checking the report cap.
A large accepted gate or inventory can make terminal report creation fail.
That failure leaves the completed attempt without its promised terminal record.

Use a bounded log consumer that stops the child before crossing its allowance.
Bound directory and file creation in the closed inventory.
Precompute or stream the report through a hard-capped writer.
Preserve a small exclusive causal failure record when full reporting cannot complete.

## P2 — the orientation sidecar mislabels the execution gate as the build closure

`seal_native_orientation_sidecar_a01.py:65` assigns `gate_identity` to `rootBuildClosure`.
The execution gate is an authorization document, rather than the recorded schema-2 build manifest.

The observer reports that field as measured build-closure evidence.
That label is unsupported unless the gate schema explicitly defines and validates the full build closure.

Bind the actual reviewed build-closure document in `rootBuildClosure`.
Keep the execution-gate identity in a separate field.
Require both identities in the runner report and sidecar.

## Verified current records

I recomputed the 15-file source-bundle aggregate.
It equals `a8d8d6b56b8af07f25b96200e4fa3f1d09603cc5ecd1a3f3e905655f29069222`.

All 15 file byte counts and hashes match `rust-source-bundle-manifest-a04.json`.
The source bundle includes `Cargo.lock`, the three contract documents, and all ten Rust source files.

The current release binary is 1,168,656 bytes.
Its SHA-256 is `37e5a9be513347eabbf0f313158340e5a8211220354ab619b492e08a1dbe95b5`.

I independently parsed the same bytes as a little-endian, 64-bit arm64 Mach-O executable.
It contains one LC_UUID value: `1266dd20cc3036b9926934c2ae5677e4`.

The schema-2 manifest agrees with the reviewed build, dependency, toolchain, SDK, and framework records.
Its command, target, host, dependency policies, and framework metadata match those saved records.

The observer closure contains 141 Pillow files and 901 NumPy files.
All 1,042 package paths rehash correctly.
The three helper hashes, runtime binding, prior closure, and freeze helper also rehash correctly.

Both observer records retain `nativeTextExecution: false` and `observerProofExecuted: false`.

## Correctly implemented behavior

- A02 differs from A01 only by `rust-native-run-a02`.
- Both drivers kill and reap a live child on timeout and exceptional terminal paths.
- Both drivers keep native and product acceptance false.
- The sidecar requires a completed attempt with no recorded after-check or inventory error.
- The sidecar records a nonzero producer return code instead of upgrading it to native success.
- The sidecar rechecks each selected artifact against the closed inventory.
- The sidecar uses exclusive file creation and keeps orientation qualification false.
- The A06 observer independently requires exact 272-byte raw and 221-byte canonical buffers.

These correct behaviors do not close the P1 and P2 findings above.

## Manifest-helper limit

The saved manifest is factually correct because this review independently reparsed the current binary.

`prepare_rust_native_manifest_a01.py` parses LC_UUID through a separate binary open between two hashes.
A transient pathname replacement could make a future run combine one file's hash with another file's UUID.
Any successor should parse and hash one retained descriptor.

This helper-reuse limit does not invalidate the current independently checked manifest.

## Required next gate

1. Preserve both unexecuted runner versions and the sidecar source.
2. Create corrected successor sources for every finding above.
3. Repair the separate Rust and Swift PNG admission P1s.
4. Freeze and review the comparator source.
5. Author one exact native gate from the corrected sources and closures.
6. Keep the gate absent until a final pre-execution review passes.

## Scope

This review establishes current manifest accuracy and observer path identities only.
It does not establish native API feasibility, producer output, source lifetime, run exclusivity, or memory compliance.

It does not accept text rendering, Plan8, product integration, playback, hearing, lyrics, or creative quality.

No Cargo command, native framework, probe, observer, product, GPU, or Resolve operation ran during this review.

This review is within the same model family. No cross-family reviewer was available.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `prepare_rust_native_manifest_a01.py` | `5ab2cc5e5eb45ed5c4eec042202aea074103567bee4f7d9bfd480ebf4b076461` |
| `rust-native-build-manifest-a04.json` | `4442ee679b6f869a2b0ae47c5d0e880472e6f3788e484dcb38877e5b2cbdd3e8` |
| `rust-source-bundle-manifest-a04.json` | `2313dc8eb13f80b2dfa0354cd63bf3d059f1e7e47fcfb32a8d1b83bba49ca0f1` |
| `run_rust_native_probe_a01.py` | `be43acf7f56d4ab155030cb24298b5684b7108062fae6b72d5f4c4c25077cdd6` |
| `run_rust_native_probe_a02.py` | `6a02235442244b4d775020581cc2f3755b8555f80f7d2ded484f9d45c5c2285f` |
| `seal_native_orientation_sidecar_a01.py` | `cf9663bc215b55d934991a38a47ff5f7d8a143934b60a0e15a19f74bc05cced8` |
| `freeze_observer_runtime_a03.py` | `23017ac4d9d0b40b487e8882397c968871f651052d6961e20481fbea0e0f4b67` |
| `observer-runtime-binding-a03.json` | `7917d0890987f83568817a56bada908bfd6ca0eec0ae49ffb3fd28957dc067da` |
| `observer-runtime-closure-a03.json` | `8ca43d6b5f7340de7fcdbc22642239719f32e0201a957849d4a1d26474540c6e` |
| `native-observer-source-closure-a03.json` | `ad901ed8ce516d9778cb26dbad17af195c133b048a2c035db0012f4b904b9e70` |
