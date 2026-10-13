# Rust producer subject adapter A09 build evidence peer review

## Scope and method

This review covers the saved A09 failed-control attempt. It does not import
the adapter, rebuild it, rerun the control, or start native or media work.

The evidence roots are:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a09`
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a09-attempt-a01`

I reopened the saved regular files and used `lstat` for recorded paths. I
checked recorded content hashes, byte counts, and the nine identity fields in
each input, output, and log row: `bytes`, `mtimeNs`, `ctimeNs`, `device`,
`inode`, `mode`, `links`, `uid`, and `gid`.

## Source package binding

The A09 source package remains a source artifact. Its manifest is 43,023 bytes
with SHA-256
`4a6f37c4e0c6690ef074ca78716a0feafe9f65f5847924975182bfd6aaf1f7c7`.
All 14 manifest rows match their current package files. The declared source
aggregate recomputes to
`adebe1a9a4a426340112c5f86541d7c076a7a72f4233ce878cdf7234b44cc4cd` using
the published domain, one NUL terminator, big-endian row-count and total-byte
prefix, ascending UTF-8 path ordering, and raw SHA-256 row encoding.

## Preflight and command result

`preflight.json` is 99,650 bytes with SHA-256
`a7b5c7a5b51a61d14d4bc1414526c3491963b77c59c396f755afb2dde6cbe9e2`.
It records 161 input rows totaling 77,595,592 bytes, a 60-second command
limit, a 4 MiB captured-stream limit, `sourceControlOnly=true`, and
`nativeProducerAllowed=false`.

The preflight lists library compilation, harness compilation, and one
no-argument control invocation. The saved attempt ran all three commands.

`report.json` is 201,986 bytes with SHA-256
`b592ec7f472f7f30a180374303d33fa5702be9551a6d6f4445180f483c0ce868`.
It truthfully records:

- state `fixed_attempt_failed_preserved`;
- `compiled=true`, `executed=true`, and `controlsPassed=false`;
- library and harness return code `0`;
- control return code `1`;
- all three processes reaped;
- no timeout, captured-stream overflow, or unclosed stream;
- two generated outputs: the library and harness;
- no canonical diagnostic outputs;
- absent FIFO and vector fixture roots;
- false native, acceptance, authorization, product, watched, heard, and
  creative fields.

The saved parent readback records all three PIDs absent at readback. The
attempt `tmp` directory is empty. Both canonical publication paths and both
fixture roots were absent.

## Generated outputs and logs

The generated library is 8,828,648 bytes with SHA-256
`952e135c183d024d8d37795629abd1c4d4ae06e0b1c75ec3b32c857cc470dad1`.

The arm64 harness is 2,590,904 bytes with SHA-256
`1acbe72368b70b805ebc522827e04ce10ba645e7ad529287222da6d930f31ff3`.
The saved Mach-O observation records CPU type `16777228`, file type `2`, and
UUID `254fa6b5eb093f4d9a1c65ab50df30b4`.

`controls.stderr.log` is 101 bytes with SHA-256
`f39be20435e0d124b4db1a274eaf120073657ba8fd7501d48e8a6f5b7d0b3775`.
Its complete message is:

`diagnostic_harness_failed: input_control_state: negative-visible-only-padded-mask:expected-rejection`

`library.stderr.log` is 1,288 bytes with SHA-256
`47a38146a2935e3d07533699ae756db4e027e1f3b0daaae955ea8c9b4ca82e1b`.
It contains three compiler warnings. Library stdout, harness stdout, and
harness stderr are empty, each with the standard empty-file SHA-256.

No canonical control report or diagnostic vector was published. This review
does not infer completed cases, candidate equality, or RoleIndex decoding from
the failed invocation.

## 161-input readback

The preflight input rows equal `report.inputsBefore` exactly. The report
contains 161 rows in both `inputsBefore` and `inputsAfter`, with exact array
equality and total bytes `77,595,592`.

All 322 before and after rows point to current regular files. Every row
matched its current nine-field `lstat` identity, recorded byte count, and
SHA-256. No input changed during the build or failed control invocation.

Both generated output rows and all six log rows matched their current regular
file identities, byte counts, and SHA-256 values.

## Failure scope and parent readback

The saved parent readback is 101,937 bytes with SHA-256
`a651ae773b384ada431dc4ae539298904e2a03dfaf0637c5335d381e09c044f0`.
The parent document is
`apps/video-studio/docs/design/rust-producer-subject-adapter-parent-build-readback-a09.md`,
2,262 bytes with SHA-256
`3edc02c8c2375b084938996c83e574b281b048b5bf188a8ce3510f84e24e0e49`.

The source trace describes a future finite repair for negative charging tests.
That interpretation is separate from the saved process evidence and does not
establish any completed control case.

The evidence establishes diagnostic compilation and one failed source-control
attempt only. It does not qualify a real producer, candidate equality, native
rendering, real acceptance, production pin, attempt authorization, product
integration, watched result, heard result, or creative acceptance.

This review did not import, rebuild, or rerun any target code.
