# A17 actual four-build ROOT readback

ROOT accepts the exact A17 four-build candidate. All four direct Rust compiler commands returned exit code zero. This accepts compilation only. Neither generated executable ran.

The reviewed A09 capsule launched canonical Python through the saved 24-key gate. Its external authentication has 14402 bytes and SHA-256 `226cfdb2183ad681e6b8b37f00e689ce11c3fc80d25885bf97521d773827cb73`. Caller closure has 2358 bytes and SHA-256 `3045bbdad8a941d33019e56facbc128acdd56a8c9be663da3f1e64bbbe377f27`. Caller PID/PGID 58237 returned zero, was reaped, and remains absent. Both external streams closed. Stdout contains the exact measurements and terminal receipts; stderr is empty.

Compile measurements have 815208 bytes and SHA-256 `01d3ab63e876e4d962d93698c1ba38073d365e56a2f3a216c1bec333c7cf5623`. Terminal closure has 1247 bytes and SHA-256 `706dc140d311195ed47b88862ba30c27e806990bb58cdf4c1142a08a5e0059d2`. The terminal proves both caller descriptors closed after measurement publication. The historical pending candidate fields remain immutable.

ROOT used a separate trusted standard-library reader. It reopened all 671 input rows twice. All byte/hash receipts and nine identity fields matched. The before/after arrays are equal and cover 183931265 bytes. Current gate, source decision, source closure, runtime receipt, and all 18 authentication references match. Every actual compiler argv, cwd, and environment matches the fixed recipe and preflight.

Compiler PIDs 58238, 58241, 58259, and 58263 each returned zero. Their process groups match their PIDs. Every process and group is absent. Stopped-image and cwd joins, returned phase evidence, final launch-authority joins, log reads, and descriptor closure all pass. No timeout, stream overflow, cleanup signal, unknown execution state, or causal failure occurred. The compile temporary directory is empty.

All eight compiler logs match complete receipts and identities. Library stderr contains unused-code warnings. Neither library stderr contains a Rust error. Both CLI stderr logs and all four stdout logs are empty. The warnings are expected from the bounded experimental crate's imported modules and do not establish maintained product quality.

Current generated outputs:

| Role | Bytes | SHA-256 |
| --- | ---: | --- |
| Production library | 20590048 | `1dad1693e21c9be42bbbf635ae02666b83b851b590cc477a0de25b6a6735e394` |
| Production CLI | 3792152 | `e3139cb7b6f6f1c7078eccaa94d348fc76367b51642f0c58ebbd52abde7fe84a` |
| Controls library | 25056000 | `72f599d0b370763eac8c167b7c10287df74f0fc2ba85f07b6d7916df16dd67c8` |
| Controls CLI | 5017344 | `008fa6936c107095d0d1b3d05d7f5cdda79490860598f571ec0021ac415e03d7` |

ROOT independently parsed both binaries from held bytes as thin arm64 Mach-O executables. Each contains 19 bounded load commands and one LC_UUID. Production UUID is `477b65fff39b335db1c7339e58a9cfc4`; controls UUID is `27757560cb6b3166af9ee9ac6afd6af0`. Both library outputs have regular archive headers. The four output inode pairs are distinct.

Detailed ROOT observations have 392678 bytes and SHA-256 `7a1460b02a1caf494d3492f70039b4046b4df89a1d437508a11117c23b08bd82`. The separately saved 13-key accepted compilation readback has 1598 bytes and SHA-256 `2df2cca8579f0062eccec23169f23bd08e83aa0218b30606c64b74a4c1621b40`. Its only next operation is `separate_retained_control_gate_required`.

The prior A15 failed attempt and A16 ineligible recipe remain preserved. Actual A17 controls, native producer output, loaded dependencies, general editor integration, tenant adapters, complete film playback, listening, and creative acceptance remain pending.
