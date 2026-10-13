# Rust producer runner A17 compilation readback peer review

This is an independent read-only review of the saved A17/A09 fixed compilation attempt. It reviews compiler evidence only. It does not qualify the native producer, generated media, product integration, or creative output.

## Evidence reviewed

The build attempt is `rust-producer-runner-a17-build-attempt-a01`.

- `compile-measurements-a01.json`: 815,208 bytes, SHA-256 `01d3ab63e876e4d962d93698c1ba38073d365e56a2f3a216c1bec333c7cf5623`.
- `compile-terminal-closure-a01.json`: 1,247 bytes, SHA-256 `706dc140d311195ed47b88862ba30c27e806990bb58cdf4c1142a08a5e0059d2`.
- External launch authentication: 14,402 bytes, SHA-256 `226cfdb2183ad681e6b8b37f00e689ce11c3fc80d25885bf97521d773827cb73`.
- External caller closure: 2,358 bytes, SHA-256 `3045bbdad8a941d33019e56facbc128acdd56a8c9be663da3f1e64bbbe377f27`.
- Pre-gate current-source readback: 416,276 bytes, SHA-256 `9a090f8cb64f662eb691491a0a192bebe9f6aeb106bbe4054c43ddd61f086870`.
- Held-source orchestration readback: 27,712 bytes, SHA-256 `ea9592aa71953a6275d1b0c0d06c6df8804d3eb20c5ef347379ffb040f1de038`.

The saved external records also bind the A17 source manifest, A17 recipe, A09 caller, A09 capsule, A09 reviews, helper authentication, source readback, and fixed gate. Their recorded file identities and hashes were rechecked against current files.

## Input closure

The measurement contains 671 input rows and 183,931,265 input bytes. The before and after arrays are byte-for-byte equal. All 671 paths and `(device, inode)` pairs are unique.

I reopened every input path and recomputed its bytes, SHA-256, and nine identity fields: device, inode, mode, links, uid, gid, bytes, mtime nanoseconds, and ctime nanoseconds. Every row matched. The independent audit found zero mismatches.

The current-source readback separately reports 655 rows, 164,928,922 bytes, 65 selected dependency rows, 116 scalar/path joins, and zero missing companion paths. It selects the A17 recipe key `a17_external_evidence_rows=204`. Its dependency checks report complete current rows, fresh-path agreement, no duplicate paths, and no device/inode aliases.

The source aggregate is 4 rows, 65,144 bytes, SHA-256 `ff7219e07bc7c689d11a5c376b9bae897d06db7d9f2fe3136b0974dec28ae97a`. The external aggregate is 40 rows, 20,221,050 bytes, SHA-256 `2cfaf0ce85a7bbd912707c4619247a7745fb985ecd3246fff5607cdb91ea7fab`. The selected dependency preflight is bound by SHA-256 `2b89dcc5dc5472867c17f27ac1474726ba8230f9faa6b3a1ab405eec7eaf64f5`.

Across the measurements, source readbacks, current-source readback, gate, decision, and external records, I checked 2,096 recorded file-reference occurrences covering 703 unique paths. Every current bytes, SHA-256, and nine-field identity comparison passed. No record conflicts were found for a shared path.

## Four compiler phases

The four recorded commands are `production_library`, `production_cli`, `controls_library`, and `controls_cli`. Each invocation was attempted, returned phase evidence, and returned exit code 0. Each process was reaped, absent after reaping, and absent with its process group.

Each phase reports a verified process group, closed selector and streams, closed launch authorities and attempt descriptor, joined attempt anchor, logs read through the held attempt, no timeout, no stream overflow, no termination signal, and complete closure. The compiler PIDs were 58238, 58241, 58259, and 58263. The saved caller closure reports PID 58237, exit code 0, reaped, absent, group absent, and both outer streams closed.

The four generated outputs were reopened and matched their recorded bytes, SHA-256, and nine identity fields:

| output | bytes | SHA-256 |
| --- | ---: | --- |
| `lib-rust-producer-runner-a17.rlib` | 20,590,048 | `1dad1693e21c9be42bbbf635ae02666b83b851b590cc477a0de25b6a6735e394` |
| `rust-producer-runner-a17` | 3,792,152 | `e3139cb7b6f6f1c7078eccaa94d348fc76367b51642f0c58ebbd52abde7fe84a` |
| `lib-rust-producer-runner-a17-controls.rlib` | 25,056,000 | `72f599d0b370763eac8c167b7c10287df74f0fc2ba85f07b6d7916df16dd67c8` |
| `rust-producer-runner-a17-controls` | 5,017,344 | `008fa6936c107095d0d1b3d05d7f5cdda79490860598f571ec0021ac415e03d7` |

I parsed both thin Mach-O output files independently. Both have magic `0xfeedfacf`, arm64 CPU type `16777228`, file type 2, and 19 load commands. The production UUID is `477b65fff39b335db1c7339e58a9cfc4`. The controls UUID is `27757560cb6b3166af9ee9ac6afd6af0`.

The eight compiler log files also matched their recorded bytes, hashes, and identities. Production-library stderr is 25,913 bytes. Controls-library stderr is 26,136 bytes. The other six streams are empty with the SHA-256 of an empty file.

## Gate and scope

The fixed gate operation is `runner_a17_fixed_four_compiles_gate_a09`, with the single allowed operation `fixed_four_compiles`. Its native-producer, native-result, and product-integration flags are false.

The measurements report `candidateChecksPassed=true`, `fixed_four_compiles_measurements_complete`, and `externalAcceptancePending=true`. The terminal report keeps `candidateAccepted=false` and `externalReadbackRequired=true`. These are build-stage results, not native qualification.

The measurements record compiler processes executed. They record `productionBinaryExecuted=false`, `controlsExecuted=false`, `nativeProducerExecuted=false`, `nativeResultAccepted=false`, `productIntegrationAllowed=false`, `loadedRuntimeAttested=false`, `watched=false`, `heard=false`, and `creativeAccepted=false`. The external authentication record is a pre-launch record and therefore reports `callerLaunched=false` and `compilerExecutionObserved=false`; the later caller-closure record independently records the completed external caller and its closed process state.

The source decision remains `accepted_no_p1_or_p2` for the reviewed source scope and preserves its historical pending state. It records no compiler execution, controls execution, native producer execution, native result acceptance, or product integration. The current build evidence does not convert that source decision into a native or product acceptance decision.

## Disposition

The saved A17/A09 compiler attempt is a closed successful four-command compilation with complete current-file and process-closure evidence. I found no P1 or P2 evidence defect in this readback. The generated production and controls binaries remain unexecuted in this scope. Native producer qualification, media validation, and product integration remain outside this report.

This review performed no binary, controls, helper, capsule, compiler, native-process, media, GPU, Resolve, or project operation. It only parsed saved JSON and reopened the already recorded files for independent hashing and Mach-O inspection.
