# Runner A14 staged-authorization reader peer source review A01

## Disposition

**No P1 or P2 source finding.** The frozen A14 reader is an exact narrow
adaptation of the accepted A12 reader. Its eight literal changes select the
A14 package, first attempt, bootstrap, manifest, binary, and bootstrap state.
The inherited reader behavior remains unchanged.

This review is same-family, nonblind, and source-only. I read the complete A14
source, the complete A12 source, the A12 parent and peer reviews, and the ROOT
A14 parent review. I did not import or execute either reader. I created no
stage, authorization, bootstrap, sidecar, proof, or state record. I launched no
helper, compiler, control, child, native framework, media, GPU, or Resolve
process.

## Frozen receipts

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `rust-producer-runner-a14-staged-authorization-readonly-root-a01.py` | 19,313 | `0d4ce0d5e1091b1a76a86438f76746b2ab33a67cc5534c29df8c66669c71c697` |
| A12 predecessor reader | 19,313 | `a9b41e6ddc61db2cbaa8bd894c154bb063214f0f5056d6452ddcf5f781f4448d` |
| A12 parent source review | 1,399 | `40f42ec895732f9ac1f30f969f3ac8ff24ca2e014978dc5ba12542a342b0683d` |
| A12 peer source review | 3,333 | `e1fe66a7e813a12619c6e95f4ca96d379ca795bcb16e1b47bfb1f8c0fe28c24b` |
| A14 ROOT parent source review | 1,805 | `cbf32e37a4a1f009a24cacdff10feb0ea53214e09c8149fedbdb6e557cc49710` |
| preserved A10 A03 reader | 19,313 | `a1727f68d7d441abfaf898c52cd7204fcf28f9e145a3ca0439a4285073101617` |

Both A12 and A14 readers contain 359 lines. A direct byte comparison confirms
that replacing every `a12` literal with `a14` produces the complete A14 file.
The A14 file contains eight `a14` literals and no remaining `a12` literal.
AST comparison confirms that every function and class except `main` is
identical. The other changed top-level assignments are the package and attempt
roots derived from those literals.

## Exact A14 adaptation

The module package root changes to `rust-producer-runner-a14`.
The first-attempt root changes to
`rust-producer-runner-a14-first-native-attempt-a01`.
The bootstrap root changes to `rust-producer-runner-a14-bootstrap-a01`.

Within `main`, the reader measures `source-manifest-a14.json` and
`rust-producer-runner-a14`. The bootstrap state must equal
`externally_reviewed_runner_a14_bootstrap`. The proof remains
`staged-authorization-parent-readback-a01.json` inside the A14 attempt.

The adaptation leaves the fixed producer path, producer bytes and SHA,
operation, implementation, repetition, seventeen authorization fields,
qualification references, aggregate order, command, environment, policies,
and false acceptance fields unchanged. It does not change the A12 output
schema or the A12 readback checks.

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
process-launch call. It writes only its own A14 readback proof when executed;
this review performed no such execution.

## Applicability limits

The A14 source review does not qualify the A14 manifest, binary, bootstrap,
authorization, producer, or native result. Those artifacts require separate
source, build, control, bootstrap, staged-authorization, and execution
reviews.

This report establishes no native, product, media, playback, watched, heard,
or creative acceptance. Sidecar publication remains outside this reader's
authority.
