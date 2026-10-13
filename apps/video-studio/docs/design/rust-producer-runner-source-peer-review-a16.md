# Rust producer runner A16 source peer review

This review covers the frozen A16 package and its read-only source measurement
helper. It is a source review only. I did not import, compile, execute, or run
controls, native code, media code, or a producer child.

## Reviewed identities

The package is:

`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a16`

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a16.json` | 98,788 | `5c22f08360ab78e07933d3fea68b6c986bc331092bea27ddee2a3681fb90b659` |
| `direct-build-recipe-a16.json` | 35,773 | `39b54ddceb0e56635b011cbaaca4f36f5ae094d29f1995648eca2af311eebbc1` |
| `src/lib.rs` | 200,612 | `afc2597909c25121bd6bc1229c076f8da4f7c8ca58dced7c086ecd8c9c5d1d8a` |
| `src/pure.rs` | 7,187 | `cc79345d6a994eeb860814aa84ca220f6a6f471ad6f9c28b864ee44742f47f7a` |
| `src/a16_focused_controls.rs` | 67,915 | `350b062a5715a6144d46a5a13d865d6b4074899a98c544840e7122c544888650` |
| `src/a05_control_extension.rs` | 74,344 | `3fe7d52f6881a51076c88580e238a7d991c640c550fa41b1d88c69c0a25ccd1e` |
| `src/a16_launch_controls.rs` | 21,491 | `43f4bb719fa7e556376f42f45158261e317f1f6a4371d1b0b4a18e2c9d99e7a4` |

The package manifest binds 15 source files and 463,576 source bytes. Its
framed source aggregate is
`b4eef131436e37f8461b9e5350abab572eedffcc4e62d388a62fb2b7c51a2a07`.

The manifest binds 159 external rows and 39,721,126 external bytes. Its
framed external aggregate is
`760b5988448e5ec3e204342bf0216fb2ca56a80e9712bc177e14fbcf8345712c`.

The source aggregate uses the declared domain, NUL, sorted relative path,
big-endian path length, path bytes, big-endian byte count, and raw digest.
The external aggregate adds sorted role bytes and role length before the path.

I rehashed all 15 source rows and all 159 external rows. Every byte count and
digest matched. Source paths and external role/path pairs were unique. The
manifest excludes itself from the source file list as declared.

The inherited A15 source readback is bound as 676,824 bytes with SHA-256
`a92c7c3d0cf41f16ceb4860e6a0902f005f3fc14f54cb59e3e13bcaecd4cc2a5` and 578
input rows. The A16 manifest records that predecessor as evidence, not as a
current A16 execution result.

## A16 source delta

The production `src/lib.rs` delta changes only A16 source paths, bootstrap
paths, bootstrap state text, and the feature-control module path. Its fixed
64-character digest literals remain the same as A15. The ten digest literals
in `lib.rs` are unchanged as a sequence. The four digest literals in
`a05_control_extension.rs` are also unchanged.

`src/pure.rs` is byte-identical to A15. `main.rs` and `control_main.rs` only
rename the crate. The launch-control file changes its package comment.
`Cargo.toml` changes package and binary names for A16.

The A15 compile readback records nine errors: two missing `BoundArtifact`
serialization implementations, one returned borrow, one escaping borrow, four
borrowed-then-moved `String` values, and one immutable mutation row.

A16 addresses those errors in the controls-only files:

1. `focused_bound_artifact_value_a16` at
   `src/a16_focused_controls.rs:321` projects the private `BoundArtifact`
   into owned JSON fields. It avoids adding a public serialization derive.
2. `control_stage_fixture_a03` accepts `&str` at
   `src/a05_control_extension.rs:1240`. The fixture does not retain the ID.
3. Four error branches use `Some(error.as_str())` and `error.clone()`.
   The borrowed display value ends before the owned detail is moved.
4. The focused variant row is mutable before its `passed` field is updated.
5. A16 names the changed authorization-path function, included fixture,
   operation strings, and report filenames consistently.

The `StableIdentity` type derives `Serialize`, so the current JSON projection
has a serializable identity. Its `unwrap_or(Null)` fallback does not hide a
current failure for this type. It is a local observation projection, not a
change to the production artifact type.

The private authorization structure still has 17 serialized fields. The
`ProcessObservation` structure and the manifest process-field list each have
47 fields. The control schedule remains 21 pure cases, 10 lifecycle cases, and
15 focused cases. It retains 11 launch variants, five nested review variants,
and the `PRESPAWN`, `STOPPED`, and `REVIEW` rendezvous phases.

The A16 manifest explicitly keeps native result acceptance, product
integration, compilation, execution, and native-child-start flags false. Its
launch rows expect native execution only when the future private control is
run; the current manifest records that it has not been observed.

## Read-only helper disposition

The helper is:

`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a16-readonly-root-source-measurement-a01.py`

It is 14,766 bytes with SHA-256
`433cae78cdb0b09bcbfb75b90bab28f193ec0bdfd83e717e23caf2f3043e48e2`.

The helper accepts one exact A16 manifest digest. It reads the manifest and
predecessor receipt through descriptor-held, no-follow, nonblocking regular
file opens. It checks the opened descriptor against the pathname before and
after bounded reads. It rehashes every source and external row, recomputes
both framed aggregates, and scans Rust include and path leaves against the
measured closure.

Its JSON parser rejects duplicate keys and nonfinite constants. Its output
encoder applies node, depth, string, integer, and encoded-byte limits before
writing. The output writer uses an exclusive descriptor-relative file create,
bounded writes, fsync, descriptor readback, and parent-directory identity
checks. The helper imports no project module and no process-launch utility.

The helper measures its own source before the closure check and rechecks that
identity after the scan. It binds the A15 parent readback, A16 manifest,
helper, and every current closure row by bytes, digest, and stable identity.
Its output path is the new A16 parent source readback. That output is still
pending because this review does not execute the helper.

The helper is a bounded readback for the frozen current files. This review does
not credit it with generic malformed-manifest fuzz coverage or loaded-code
attestation. Those claims require a separate bounded control or runtime proof.

## Disposition

I found no P1, P2, or P3 source issue in the frozen A16 package or helper.
The A16 source changes are limited to the recorded controls compile repairs
and package-label/path advancement. The source manifest and direct recipe
correctly keep A16 unbuilt and unexecuted.

The root helper must still run and publish its current-source readback before
the A16 closure becomes measured evidence. That later receipt must remain
separate from compiler, control, native, media, product, watched, heard, and
creative acceptance.
