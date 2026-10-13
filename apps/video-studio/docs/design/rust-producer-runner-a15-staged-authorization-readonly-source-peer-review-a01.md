# Runner A15 staged-authorization reader peer source review A01

## Disposition

**No P1 or P2 source finding.** The frozen A15 reader is an exact narrow
adaptation of the accepted A14 reader. Its eight literal changes select the
A15 package, first attempt, bootstrap, manifest, binary, and bootstrap state.
The inherited reader behavior remains unchanged.

This review is same-family, nonblind, and source-only. I read the complete A15
source, the complete A14 source, the A14 peer review, and the ROOT A15 parent
review. I did not import or execute either reader. I created no stage,
authorization, bootstrap, sidecar, proof, or state record. I launched no
helper, compiler, control, child, native framework, media, GPU, or Resolve
process.

## Frozen receipts

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `rust-producer-runner-a15-staged-authorization-readonly-root-a01.py` | 19,313 | `be1972c55d732303b17d9edb7ead1dc9493acc464d42ef69d6192ab1a88b209e` |
| A14 predecessor reader | 19,313 | `0d4ce0d5e1091b1a76a86438f76746b2ab33a67cc5534c29df8c66669c71c697` |
| A14 peer source review | 4,386 | `8682e30f2368d502bd77fe5b3eb32018071fd554a4e9b591fa0c7d40391b95cb` |
| A15 ROOT parent source review | 1,877 | `2a9f8750ae0e6afe3d8b8ee25a327c9fb6427dc53e066d3bdff39f2f8bc9e13f` |

Both A14 and A15 readers contain 359 lines. A direct byte comparison confirms
that replacing every `a14` literal with `a15` produces the complete A15 file.
The A15 file contains eight `a15` literals and no remaining `a14` literal.
All seven 64-character hexadecimal literals are byte-identical between the
readers. AST comparison confirms that every function and class except `main`
is identical. The other changed top-level assignments are the package and
attempt roots derived from those literals.

## Exact A15 adaptation

The module package root changes to `rust-producer-runner-a15`.
The first-attempt root changes to
`rust-producer-runner-a15-first-native-attempt-a01`.
The bootstrap root changes to `rust-producer-runner-a15-bootstrap-a01`.

Within `main`, the reader measures `source-manifest-a15.json` and
`rust-producer-runner-a15`. The bootstrap state must equal
`externally_reviewed_runner_a15_bootstrap`. The proof remains
`staged-authorization-parent-readback-a01.json` inside the A15 attempt.

The adaptation leaves the fixed producer path, producer bytes and SHA,
operation, implementation, repetition, seventeen authorization fields,
qualification references, aggregate order, command, environment, policies,
and false acceptance fields unchanged. It does not change the A14 output
schema or the A14 readback checks.

## Preserved reader behavior

The reader requires an unoptimized interpreter, a bounded absolute
authorization path, and two 64-character hexadecimal receipt arguments. It
rejects review, probe, cancel, report, and failure sidecars before reading the
authorization.

All file reads use canonical paths, no-follow regular-file checks, nonblocking
no-follow opens, bounded 64 KiB reads, complete identity checks, and held-file
descriptor readback. JSON parsing rejects duplicate keys and nonfinite values.
JSON publication has node, depth, string, integer, encoded-byte, and 16 MiB
limits.

The reader retains descriptors for the output parent, staged run, and unit
root. It checks directory anchors and exact directory inventories before and
after the exclusive proof write. The proof write uses `O_EXCL`, bounded writes,
file `fsync`, same-descriptor byte readback, identity checks, and parent
directory durability. The final success print occurs after retained directory
descriptors close successfully.

The source only reads the fixed producer and staged evidence. It contains no
process-launch call. It writes only its own A15 readback proof when executed;
this review performed no such execution.

## Applicability limits

The A15 source review does not qualify the A15 manifest, binary, bootstrap,
authorization, producer, or native result. Those artifacts require separate
source, build, control, bootstrap, staged-authorization, and execution
reviews.

This report establishes no native, product, media, playback, watched, heard,
or creative acceptance. Sidecar publication remains outside this reader's
authority.
