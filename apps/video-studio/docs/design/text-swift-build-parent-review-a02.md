# Swift compiler build A02 parent readback

The fresh A02 compiler build passed all seven steps.
All six produced binaries remain unexecuted.
The parent independently read the final report, publication seal, preflight, sources, tools, logs, and binaries.

| Saved record | Bytes | SHA-256 |
| --- | ---: | --- |
| A02 build report | 108,721 | `214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea` |
| A02 publication seal | 2,624 | `23cd14ae2a46f5990831cb34e7de9b2dfa959cd642d3aec81381d804c63a97ae` |
| Independent parent readback | 36,183 | `cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a` |

The audit source is `readback_swift_build_a02.py` with SHA-256
`d4c89a176660127e68d0113c0b0582f702a13cf3380bc9e05ed5de466c44df29`.
The audit imports no build helper and launches no child process.

Every current observation matches the corresponding before and after build record.
The source package has twenty-one matching, distinct inode records.
All six ordered build contracts, compiler arguments, environment fields, and seven log observations match.
The held build directory matches the report and seal directory authority.
Each binary independently has a regular executable mode, thin arm64 Mach-O header, one UUID, matching bytes, and matching SHA-256.

Swift 6.2.1 produced the main executable in 20.261 seconds.
The main executable is 2,570,328 bytes with SHA-256
`73a690570b65fa9ae035646ef9602f03e93b5eabf90cff14361d490a1359e99f`.
Its UUID is `3d73f2c916343502b0c8d4a894d6f21a`.
The producer log contains the previously reviewed unused-variable warning.
The other six logs contain the compiler version or no diagnostics.

These observations establish compilation and saved pathname evidence.
Loaded helper, interpreter, compiler, and produced images remain unattested.
Complete compiler dependencies and SDK contents remain outside this observation.
The compiler log and binary caps are post-run read limits.

Control execution still requires a reviewed runner, exact authorization, and saved control readback.
Native producer execution, native text pixels, film watching, hearing, and creative acceptance remain unverified.
The incomplete A01 directory remains preserved separately.
