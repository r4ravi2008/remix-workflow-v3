# Native preparation A03 — failed direct build readback

One fixed direct library build exited with status 1. It produced no accepted
rlib. The harness build and all five tests remain unexecuted. The failed attempt
and complete compiler stderr are preserved.

The compiler reported six errors with two causes. `stable_identity` imports
Unix `MetadataExt` but calls four Darwin `st_*` methods. The narrow repair uses
the imported trait's `dev`, `ino`, `mode`, and `size` methods. `AdaptedReport`
derives Clone and Debug while the frozen `EncodedRoleIndex` implements neither.
The unused derives must be removed. The reviewed RoleIndex source remains fixed.

The external preflight binds the exact source manifests, report fixtures,
compiler, selected library commands, fixed existing dependency lookup files,
and root and peer reviews. All 100 current input rows and nine identity fields
matched after the failed build. No Cargo resolution occurred.

The saved report is `native-preparation-pure-attempt-a03/report.json`: 3,986
bytes, SHA-256
`af2b502e36710e5aa7206df93a49b5bcbbdcc8c41d84c754926066ff9ecf8261`.
The complete 4,954-byte compiler stderr is
`native-preparation-pure-attempt-a03/library-build.stderr.bin`.
Root read both files after the attempt.

A small A04 package will contain the two corrected modules and a crate root
that names the unchanged A03 sources. A narrow harness successor will link that
crate. A03 and its source reviews remain preserved. The corrected source must
pass review and actual compilation before the five tests can establish a result.

No acceptance authority, native producer, media operation, GPU generation,
Resolve operation, hearing, viewing, or creative acceptance occurred.
