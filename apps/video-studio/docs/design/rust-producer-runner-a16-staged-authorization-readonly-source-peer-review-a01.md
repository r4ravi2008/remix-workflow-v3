# A16 staged authorization reader source peer review

This review covers the frozen A16 staged authorization reader only. It is a
source review. I did not import, compile, execute, create a stage, publish a
sidecar, launch a child, or run native, media, GPU, or Resolve code.

## Reviewed identities

The reader is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a16-staged-authorization-readonly-root-a01.py`

It is 19,313 bytes with SHA-256
`7f496910001bf2d8c95e297e424dfe499a13d1c45ddd144ac455e5c9c3d113d5`.

Its A15 predecessor is 19,313 bytes with SHA-256
`be1972c55d732303b17d9edb7ead1dc9493acc464d42ef69d6192ab1a88b209e`.
The ROOT A16 source review is 1,530 bytes with SHA-256
`f8a12921465b76c56b3671c057b0797c6e5c67592c5d2e0a6ddfda4df4f300b6`.

Reversing the eight A15-to-A16 path and label substitutions reproduces the
complete A15 predecessor byte-for-byte. Both versions contain seven complete
64-character digest literals, and their digest sequences are identical.

The eight changes select the A16 runner package, first-native-attempt root,
bootstrap root, source manifest, bootstrap state, and bootstrap binary. The
producer authority remains the measured Rust A05 executable. No algorithm or
authorization field changed in this adaptation.

## Read-only source behavior

The reader imports only Python standard-library modules. It has no subprocess,
process, fork, spawn, signal, native-framework, or media API.

Its bounded file reader rejects symlink paths, requires regular files, uses
`O_NOFOLLOW | O_NONBLOCK`, holds the opened descriptor, and compares the full
identity before and after reading. Its JSON reader rejects duplicate keys and
nonfinite constants. Its JSON writer bounds shape, depth, nodes, strings,
integers, floats, and encoded bytes before exclusive publication.

The fixed invocation accepts one absolute staged `authorization.json` path,
its 64-character digest, and the 64-character bootstrap digest. It requires
the A16 first-attempt directory shape and requires these files to be absent:
the review sidecar, producer output, cancellation marker, and terminal reports.

The reader validates all 17 authorization fields through exact recursive JSON
comparison. The comparison checks keys, list lengths, scalar types, and values.
It binds the A16 bootstrap state, source manifest path and receipt, binary path
and receipt, measured Rust A05 producer, fixed qualification references and
aggregate, command, working directory, four-variable environment, process
policy, output policy, cancellation policy, and false acceptance flags.

It retains descriptors for the output parent, staged run directory, and fixed
unit root. It checks canonical paths, directory type, device, inode, and mode.
It checks the run mode, `0700` permissions, exact directory entries, and final
directory anchors. It rereads the authorization, bootstrap, manifest, runner
binary, producer, and reader through held measurements before publication.

The proof state is
`primary_authorization_content_reviewed_peer_and_sidecar_pending`. The reader
does not create a sidecar. It publishes a separate bounded proof file with an
exclusive descriptor-relative create, fsync, readback, and parent identity
checks. It closes retained descriptors before printing success.

## Boundaries and disposition

The reader validates staged authorization content and file identity. It does
not independently qualify the Rust producer, execute the binary, inspect a
loaded image, or prove native or media output. Its fixed references and
qualification aggregate are content checks for the staged authorization.

The source review found no P1, P2, or P3 issue. The reader is suitable for its
declared read-only staged-authorization scope. Its execution, proof receipt,
sidecar publication, and later producer lifecycle remain unperformed and
require separate evidence.

Native, product, media, watched, heard, and creative acceptance remain false.
