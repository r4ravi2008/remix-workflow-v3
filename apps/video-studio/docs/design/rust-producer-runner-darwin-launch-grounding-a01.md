# Darwin launch grounding

The suspended-launch API route passed a bounded operating-system probe. Runner A06 is still source-only. This record does not accept a native producer or its outputs.

macOS rejected execution through `/dev/fd/<held executable fd>` with EACCES 13. The live SDK has no `fexecve` declaration. The replacement uses direct `posix_spawn`, START_SUSPENDED, SETSID, CLOEXEC_DEFAULT, descriptor-based cwd setup, and libproc vnode observations.

The first suspended probe established API availability and descriptor cwd setup. The second confirmed WIFSTOPPED, but rejected its own offset-zero predicate. `/usr/bin/true` is a universal Mach-O. Its ARM64 slice begins at file offset 49,152. That process was killed and reaped without resume.

The refined third probe selected that measured slice. It observed exactly one executable region with the selected pathname and offset. All six vnode identity fields matched the held executable: device, inode, mode, size, modification time, and change time. The loaded cwd matched its held directory descriptor. The held executable content and full file identity remained unchanged. Only then did root send SIGCONT. The process exited 0 and was reaped. All three probe PIDs are currently absent.

The actual Rust producer is a thin ARM64 Mach-O: magic `0xfeedfacf`, CPU type `16777228`, subtype `0`, file type `2`, and 25 load commands. Its production launch seam can require an offset-zero executable mapping after validating that exact header shape. General FAT support is unnecessary for this unit.

The current SDK defines START_SUSPENDED and both process vnode queries. Apple's [process-info implementation](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/proc_info.c) fills region observations from the mapped vnode. Apple's [VM implementation](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/vm/bsd_vm.c) reports the region's file offset. These sources ground the API interpretation. The live probe establishes current behavior only for the harmless system executable.

## Saved evidence

| Receipt | Bytes | SHA-256 |
| --- | ---: | --- |
| descriptor-exec negative A01 | 1,468 | `3d98793d18851258a3a67ca660a226ae3980be45b17c4533825ab85d70b2d5a2` |
| suspended API probe A01 | 6,290 | `758f0e5ffe80263d03cd3449e1c522645adc23ece3f0e817b6811356e218ba94` |
| stopped-state / offset negative A02 | 6,464 | `7acbd092a35fd28600e5c0f4e45ba6b7b4afaca2eb0f65ee44ff4e1debcd871e` |
| refined positive A03 | 6,801 | `3a2c60ead6c31d66bdb3f82861deffb22a1ef57d873e81b55ba3830e8c14c9f9` |

The receipts are under `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/`. `darwin-launch-grounding-a01/` preserves all three probe sources, the measurement helper, and independent current readback. SDK and libc source receipts are retained there. No project module was imported and no native producer, media, GPU, or Resolve process ran.

## Bounded decision

Root and the separate judge conditionally accept this design for the first diagnostic attempt. The implementation must verify the stopped child, main-image vnode, held exe content/identity, cwd, retained parent/run anchors, authorization, review references, and cancellation before resume. A mismatch must kill and reap without SIGCONT. The changed private runner controls must establish those behaviors before production invocation.

This route does not attest dyld or dependencies. It does not establish protection against general concurrent in-place host mutation. It does not bind output or cancellation path opens after resume. All outputs therefore remain externally pending. An inherited run-directory descriptor and producer `openat` protocol are required before production output qualification or acceptance.

Native result, product integration, WATCHED, HEARD, and creative acceptance remain false. The remaining music-film proof and correction loop are independent outstanding work.
