# Rust producer subject adapter A07 build evidence peer review

## Scope and method

This review covers the saved A07 failed-control attempt. It does not import
the adapter, rebuild it, rerun the control, or start native or media work.

The evidence roots are:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a07`
- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-subject-adapter-a07-attempt-a01`

I reopened the saved regular files and used `lstat` for recorded paths. I
checked recorded content hashes, byte counts, and the nine identity fields in
each input, output, and log row: `bytes`, `mtimeNs`, `ctimeNs`, `device`,
`inode`, `mode`, `links`, `uid`, and `gid`.

## Source package binding

The A07 source package remains a source artifact. Its manifest is 38,040 bytes
with SHA-256
`47c01337bc4703deddf7a948ba88f39146a1eaca02d7b65ca2b81f067463ed68`.
All 14 manifest rows match their current package files. The declared source
aggregate recomputes to
`3d2dc8c4d5c073ce54cf50f0cd430fc3e83c1a7b1d53c68e533609395dedde76` using
the published domain, one NUL terminator, big-endian row-count and total-byte
prefix, ascending UTF-8 path ordering, and raw SHA-256 row encoding.

## Preflight and command result

`preflight.json` is 89,978 bytes with SHA-256
`85a29fee353f0461ff291026fc95d874dec61de95b7465ccdd9a5e7b8c530abb`.
It records 144 input rows totaling 77,119,369 bytes, a 60-second command
limit, a 4 MiB captured-stream limit, `sourceControlOnly=true`, and
`nativeProducerAllowed=false`.

The preflight lists library compilation, harness compilation, and one
no-argument control invocation. The saved attempt ran all three commands.

`report.json` is 182,619 bytes with SHA-256
`2cc010148351ec053b1d732409ae6a7b90623fb8367ca26ad89192994f790331`.
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

The saved parent readback records all three PIDs absent at readback. It also
records an empty attempt `tmp` directory. No canonical output or fixture-root
path was created.

## Generated outputs and logs

The generated library is 8,810,496 bytes with SHA-256
`033889442efb1cf1d588d12ba18b5e54793db7ec0b131c900082fea7db76e642`.

The arm64 harness is 2,588,248 bytes with SHA-256
`eef4946ad846fa5b18109ecb55e244cc605bdf83204dc0d2d306f11e247cdcd8`.
The saved Mach-O observation records CPU type `16777228`, file type `2`, and
UUID `76037802b21633f1bf48e839756a4cb8`.

`controls.stderr.log` is 78 bytes with SHA-256
`a1345fa898a03516459cee5c6b1cfbf8852b05ae0a138b1d04b1875cfe532c96`.
Its complete message is:

`diagnostic_harness_failed: json_parse: trailing characters at line 1 column 3`

`library.stderr.log` is 1,288 bytes with SHA-256
`9911b57dec924b5500c5cf9e4a6d71adfa2a86e5dd5b73a257a42a37961f0213`.
It contains three compiler warnings. Library stdout, harness stdout and
harness stderr are empty, each with the standard empty-file SHA-256.

The saved report does not identify a completed control case or publish a
canonical control report. A source-level hypothesis about particular Python
helper files entering the JSON parser is not treated as measured case
evidence in this review.

## 144-input readback

The preflight input rows equal `report.inputsBefore` exactly. The report
contains 144 rows in both `inputsBefore` and `inputsAfter`, with exact array
equality and total bytes `77,119,369`.

All 288 before and after rows point to current regular files. Every row
matched its current nine-field `lstat` identity, recorded byte count, and
SHA-256. No input changed during the build or failed control invocation.

Both generated output rows and all six log rows matched their current regular
file identities, byte counts, and SHA-256 values.

## Parent readback and disposition

The saved parent readback is 92,263 bytes with SHA-256
`de6e1befeef0fb21240de8b240f447c7b67dfe6736edfad54102c2892eff08d8`.
The parent document is
`apps/video-studio/docs/design/rust-producer-subject-adapter-parent-build-readback-a07.md`,
2,023 bytes with SHA-256
`4c4cc31fa3833a3402341d46007ec6d8afa9cb4412d897cec53680e379b57292`.

The saved evidence supports successful diagnostic compilation and one failed
source-control attempt. It does not establish completed controls, candidate
equality, RoleIndex decoding, native rendering, real acceptance, a
production pin, attempt authorization, product integration, watched result,
heard result, or creative acceptance.

This review did not import, rebuild, or rerun any target code.
