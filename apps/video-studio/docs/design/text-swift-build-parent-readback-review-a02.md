# Swift build parent readback A02: independent review

## Scope and method

This is a source and evidence review of the A02 build parent readback. It used file reads and digest comparisons only. It did not launch the readback driver, a compiler, a produced binary, a native framework call, a control, or a helper.

Reviewed artifacts:

| Artifact | SHA-256 |
| --- | --- |
| `readback_swift_build_a02.py` | `d4c89a176660127e68d0113c0b0582f702a13cf3380bc9e05ed5de466c44df29` |
| `swift-build-attempt-a02/report.json` | `214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea` |
| `swift-build-attempt-a02/publication-seal.json` | `23cd14ae2a46f5990831cb34e7de9b2dfa959cd642d3aec81381d804c63a97ae` |
| `swift-build-attempt-a02/preflight.json` | `5f4f3c0a1e1ea417e969e4aeff8770a96e8616ce46c4961cbff440e8294f9d92` |
| `swift-build-parent-readback-a02.json` | `cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a` |
| `source-manifest-a15.json` | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |

The review also checked the bound helper digest `ba632ed73005d8c3f870d4b7886c3057ae80405071c4f2154469fe090c195886`, operation `manifest_authorized_swift_build_preparation_a04`, and target `arm64-apple-macosx26.0`.

## Verdict

No P1 or P2 finding remains for the bounded claim represented by this readback. The readback is suitable as evidence that the six authorized Swift compiler steps were attempted and produced the recorded unexecuted Mach-O files, subject to the explicit boundaries below.

## Verified consistency

The parent readback and the saved report agree on the request, manifest digest, helper digest, operation, target, attempt root, source closure, binary contracts, log observations, and final path identities. The report and readback both contain six binary observations and seven log observations.

The six binary records are `producer`, `png-control`, and `source-control-00` through `source-control-03`. Each record has a Mach-O identity, byte count, UUID, and SHA-256. The readback compares each current descriptor observation with the report record. The seven logs include the compiler-version log and one log for each compiler step. The readback compares their bytes, hashes, descriptor identities, and descriptor-relative directory authorities.

The readback reopens the held build root with no-follow and close-on-exec flags. It checks root mode, device, inode, and size authority against the path. It repeats this check after reading the report, seal, preflight, source closure, logs, and binaries. It rejects a changed root, changed descriptor identity, unexpected extra bytes, or a path identity mismatch.

The report, publication seal, and preflight form a consistent join. The seal binds the report observation and the preflight observation. The readback checks both file observations again. The report states that every authorized compiler step completed with return code zero, no timeout, a stable attempt root, and an exact environment, working directory, argument vector, and log binding.

The source manifest has 21 file rows. The readback checks each row's path, size, digest, and direct-child placement, and requires 21 unique file identities. It then requires the current source closure to equal both report closure snapshots. The manifest digest is fixed before parsing and rechecked after the closure walk.

The readback reconstructs the four source-control binary contracts from the manifest and report schemas. It compares those contracts with both the authorized and observed report contracts. This covers the producer, PNG control, and all four source-control compile units without executing any of them.

## Qualification boundaries

This evidence does not show that any produced binary ran. It does not show a loaded helper image, a CoreText or ImageIO call, native output, a source-control result, or a completed text feature. The report and readback correctly keep those boundaries false.

The build preparation does not establish a complete dependency or SDK closure. It also does not establish a live compiler memory or process-size limit. The report records post-process log and binary caps, while the readback checks the resulting bounded files. Those limits must remain separate from runtime or native acceptance.

The persisted seal records the attempt root before and after report creation. It does not persist a separate `attemptRootAfterSeal` observation. The helper checks root authority after creating the seal, and the readback checks the held root and seal identity again. Therefore the current evidence supports final path and descriptor authority. A future qualification rule that requires a persisted, timestamp-specific post-seal root snapshot would need one additional seal field.

The readback does not repeat every semantic manifest field assertion, such as the manifest state, package name, producer report schema, and full caller-binding object. This is not a qualification gap here: the exact manifest digest and all 21 current rows are bound, the reviewed A04 helper parses the manifest contract, and the readback reconstructs the source-control contracts. Adding duplicate field assertions would strengthen defense in depth but is not needed to qualify this bounded readback.

The parent readback itself is written after the checks and is not sealed by the build publication seal. A later runner must bind its path, byte count, and digest, as the parent evidence record does for the current review. That is an evidence-consumption requirement, not a defect in the A02 readback.

## Review result

The A02 readback evidence is internally consistent for pure compiler preparation. It is ready for the next explicitly separate review or control-preparation stage. It does not authorize binaries, native calls, controls, or product acceptance.
