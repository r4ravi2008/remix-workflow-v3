# Native preparation A04 parent build readback

The corrected A04 library compiled once with exit code zero.
The A02 libtest harness then failed compilation with fourteen panic-strategy diagnostics.
No pure test ran. The failed combined attempt remains preserved.

The actual attempt is `native-preparation-pure-attempt-a05` under the fixed unit.
Its report is 8,435 bytes with SHA-256
`c53bc7e4c5038772391940a1150d3332c06c935f8ae003585a7b69bb55274ba6`.
The generated A04 rlib is 4,262,496 bytes with SHA-256
`42723d0bc95379d69986bf621accbf62c27d51fff6ca69e4610be8c94b6605bb`.
The library compiler produced no stdout or stderr.

Root read the complete harness diagnostics.
The fixed existing release archives require `panic=abort`.
The standard Rust test harness requires unwinding and rejects those archives.
A small standalone successor will retain all five assertion bodies.
Its explicit main will invoke each body using the fixed archives and abort strategy.

All 112 measured input files and nine identity fields matched after the attempt.
They total 75,527,591 bytes. No Cargo resolver ran.
The earlier `native-preparation-pure-attempt-a04` contains only a root setup failure.
That setup read a nonexistent predecessor JSON key before launching any compiler.
Root corrected the key and used a fresh A05 attempt directory.

Successful library compilation qualifies compilation only.
Pure tests, accepted authority, loaded code, native producer, media, GPU,
Resolve, watched review, heard review, and creative acceptance remain unverified.
