# Swift pure-control parent readback A03: peer review

## Scope and method

This is a read-only source and evidence review of the four saved pure Swift control results.
I used bounded file reads, digest checks, and static JSON inspection only.
I did not run the audit, runner, controls, compiler, producer, helper, or any native framework.

I authored Runner A03 and the A03/A04 source-control package.
This review is therefore same-family and nonblind.
It is an independent readback of saved evidence, not independent source-origin evidence.

Reviewed artifacts:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `readback_swift_pure_controls_a03.py` | 15,089 | `4a4775efa0274198e3483416a31e358860826bac3f49d44533970850c97ed40d` |
| `swift-pure-controls-authorization-a03.json` | 860 | `4d271cab075562b761653b3497311cd74defc3fbe515cd79253d1d4b4bd11125` |
| `swift-pure-controls-attempt-a03/preflight.json` | 3,216 | `1a1be83109b2caf9be8fff24ee9b6b2a0d06be5f1025095852e5026555f87786` |
| `swift-pure-controls-attempt-a03/report.json` | 194,652 | `43a58d030bc7d4f2d6ddb799871472517e68bece09f70b675bd8e1f0f07c6632` |
| `swift-pure-controls-attempt-a03/publication-seal.json` | 2,679 | `b6e7ab47467e1dca3243e0ac096176e93f6230025a7778663daf62d91b10dcad` |
| `swift-pure-controls-parent-readback-a03.json` | 41,372 | `7f7312a84190033b7e76743b28dee9c550b04bff9b1f20622613d23ff568a10d` |

The accepted no-child prerequisite is
`swift-control-runner-source-control-parent-readback-a04.json`, SHA-256
`f6e7f8abfb0c1b7bd5d2144a3cf9165e34478ab0f3d736e7df1f59c57f595711`.

## Verdict

No P1 or P2 finding remains for this bounded pure-control result.
The readback supports four successful path-bound control executions.
It supports 16 cases and 146 runner assertions across those controls.

This evidence does not qualify the native text producer.
It does not qualify ImageIO, CoreText, CoreGraphics, text rasterization, or loaded-image identity.

## Authorization and publication joins

The authorization permits only the four pure controls.
It explicitly keeps native producer execution false.
It binds Runner A03, build helper A04, manifest A15, build report A02, build seal A02, and build readback A02.

The control report repeats the authorization digest and all accepted build digests.
The report binds Runner A03 at
`d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c`.
It binds manifest A15 at
`0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e`.

The publication seal contains the exact report and preflight observations.
Its `reportState` equals `four_pure_controls_passed`.
The seal records the held attempt-root authority before and after report publication.

The parent readback fixes the report and seal digests before parsing.
It reopens both through the held attempt directory.
It then verifies the seal, report, and preflight join.

## Build and current closure

The report's complete input snapshots are byte-for-byte equal before and after execution.
The closure contains all six produced Mach-O files and all seven build logs.
It contains all 21 A15 source rows.

The six binaries are the producer, duplicate PNG control, and four source controls.
Only `source-control-00` through `source-control-03` appear in process argument vectors.
Each selected binary has equal descriptor and pathname observations before execution.
Each selected binary has equal descriptor observations after execution.

Each control retains equal attempt-root and build-root observations before and after execution.
Each source-control binding matches its manifest compile units and source observations.
Each binding's build binary matches the held descriptor used for execution.

The parent readback records 52 unique current file observations.
These include all six binaries, seven logs, 21 sources, authority files, and eight captured streams.
The readback source checks current bytes, SHA-256, metadata, and directory authority.

The bundled Python executable is 18,058,560 bytes.
Its current SHA-256 is
`4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc`.
The saved build report and control report both bind this value.

## Process evidence

All four argument vectors contain one exact selected executable.
Each process uses an isolated work directory and temporary directory.
Each environment has only `HOME`, `PATH`, `LANG`, `LC_ALL`, `TZ`, and `TMPDIR`.

Every direct child returned integer zero.
Every direct child was reaped through the recorded bounded wait.
The timeout is 15 seconds, and the direct-child reap bound is one second.

No result records timeout, cancellation, capture overflow, forced closure, or reap timeout.
No result records launch, capture, reap, cleanup, or termination errors.
Every result keeps descendant-reaping attestation false.

Captured stream identities are:

| Control | Stdout bytes | Stdout SHA-256 | Stderr |
| --- | ---: | --- | --- |
| `source-control-00` | 3,016 | `7b61b70a43a960a538bdb8aa47df378dce3120a299ddebe07ed1d4c53e3cb5e8` | empty |
| `source-control-01` | 2,022 | `02c02b020fb10d99eb9ef90a5ede50e801c9881939f405047f798a4545393e37` | empty |
| `source-control-02` | 1,772 | `b9d1e0aac2bc30620fce5b7e32ab3cd34be47147abb60e7bc81048d848eac210` | empty |
| `source-control-03` | 1,433 | `7d8c86443de1344c7ca59f62ec1f00e57b3ab9d884bf46d19dcd33a6d2bbcb56` | empty |

All four stderr files have the empty-file SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Parsed control semantics

The parent readback reparses each captured stdout.
It requires exact equality with the report's parsed object.
It also checks each closed case schedule and critical numeric result independently.

The PNG callback control passes five cases.
They cover exact capacity, overflow, cancellation, reentrancy, and serialized concurrency.
The readback recomputes every expected payload digest.
The report states `imageIOUsed: false` and `callbackThrows: false`.

The failed-publication control passes two cases.
Each case contains exactly 23 unique required evidence keys.
The report states `nativeCalls: false` and `fileIO: false`.

The persisted-budget control passes five cases.
It reports the 512 MiB persisted-output cap and 16 MiB event-log cap.
It reports the 396,071,265-byte qualification bound and the fixed 256-slot reservation table.

The terminal-publication control passes four cases.
It covers exact terminal admission, two one-byte-under failures, and missing preparation.
The report states `nativeCalls: false` and `fileIO: false`.

The 146 assertion records have unique names.
Every record has equal actual and expected values and a true pass flag.
The readback also checks typed parsed fields, so stringified assertion values are not the sole authority.

## Qualification boundaries

The producer binary did not run.
The separately compiled duplicate PNG binary did not run.
Only the four listed source-control binaries ran.

The report and seal keep loaded-control-image attestation false.
They keep native-framework call-trace attestation false.
They also keep GPU, Resolve, and creative-acceptance claims false.

The pure reports' `imageIOUsed` and `nativeCalls` fields are source-defined observations.
They do not establish loaded-image or framework-call evidence.

The parent readback is not itself covered by the control publication seal.
A later gate must bind its exact path, byte count, and SHA-256.

The audit relies on the fixed report digest for some redundant field relationships.
The saved per-control roots and binary records were inspected and are equal.
A generic audit without a fixed report digest should check those relationships directly.

## Review result

The saved A03 pure-control evidence is internally consistent and bounded.
It is suitable as a prerequisite for a separately reviewed native-producer gate.
It does not establish native text feasibility or output acceptance.
