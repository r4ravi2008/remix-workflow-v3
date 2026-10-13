# Rust producer runner build A01 parent readback

The fixed A03 library build exited 1. No library, CLI binary, or source control was produced. CLI compilation and invocation did not run. The failed attempt remains preserved.

The compiler reported four E0609 diagnostics from two Darwin timestamp expressions at A03 lib.rs:1615-1616. Rust libc 0.2.190 has flattened st_mtime/st_mtime_nsec and st_ctime/st_ctime_nsec fields. Root resolved its primary source through the fixed libc archive dependency file and read the stat declaration at lines 329-352. A04 will repair only those expressions and package metadata.

Root read the complete compiler stderr and saved report. The attempt has one phase, return code 1, no timeout, no TERM/KILL request, and completed direct-child reap. Standard output is empty. The temporary directory is empty. All 78 current input files and nine identity fields match before and after: 74,940,709 bytes.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| preflight.json | 52,549 | 067a42019829b4f655ef443580d92ab26e5c862966322a19f1149764caf6fc62 |
| report.json | 100,187 | f2d9ff34dddca8db84fe604c730f03a1513d557185ba92b273e5c953d8421d3b |
| 0-stderr.log | 3,226 | 9f0d4a3654d9b4709cfa43d9b80125d1bad01303cbdbffca8338dfc20f9e02be |

This is retained failed compiler evidence. A03 source reviews established static scope only; the compiler exposed a remaining target dependency mismatch. No Rust A05 native producer, control body, media, GPU, Resolve, accepted authority, product integration, WATCHED, HEARD, or creative acceptance occurred.
