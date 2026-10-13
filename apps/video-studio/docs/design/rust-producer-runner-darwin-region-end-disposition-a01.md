# Darwin region-end parent disposition A01

Root fully read the 5,585-byte independent source review.
Its SHA-256 is `68aacdfbfb089878545392ce4d82d588c91c35934e25941413e6b2f3277a4737`.
Root separately read Apple's kernel and user-space wrapper sources.
The normal region-end defect is confirmed as a source-level P1.
A06 remains rejected before compilation.

The frozen primary snapshots are under `darwin-region-end-primary-source-a01`.

| Snapshot | Bytes | SHA-256 |
| --- | ---: | --- |
| apple-proc-info.c | 105,375 | `557092f14fbad3341100f59e0391d2e812c54b79a7404c89b2af97471ad67082` |
| apple-libproc.c | 28,996 | `5c8a771427e04c5e1d55c4cdf5a077f3b52c5be4a091683b970084bfdda76df2` |
| readback.json | 1,251 | `a82ad2cb39d3edc82386ba39b9cbe12e194dd15257e17dd77bee113279a42e8a` |
| parent-readback-a01.json | 4,779 | `a91f6679e7d985f329506cf4c063093e6655f21fde2490e25658c35c883140ef` |

The saved kernel snapshot returns `EINVAL` at lines 1143–1145 when no later region exists.
The saved wrapper returns zero at lines 105–106 when the syscall returns `-1`.
The wrapper preserves the syscall's errno.
Line numbers differ from cached web views; the named function and behavior agree.
See [Apple kernel source](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/proc_info.c)
and [Apple wrapper source](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/libsyscall/wrappers/libproc/libproc.c).

A07 may classify captured `EINVAL` as normal end only after a validated record and nonzero monotonic cursor.
The query uses the fixed reviewed flavor and exact buffer size for the owned stopped child.
Initial zero, process disappearance, permissions, other errors, malformed records, deadline, and cap exhaustion remain failures.
The unique main-image identity and cwd anchor must still pass before resume.
Actual Rust source review and finite controls remain required.

The parent readback matches both source contents and four input rows across two stable nine-field observations.
No compiler, import, probe rerun, authorization, producer, or media process ran.
This source review does not provide loaded-runtime, native, product, or creative acceptance.
The historical parent A06 review's pending F2 text remains unchanged; this disposition closes that research question.
