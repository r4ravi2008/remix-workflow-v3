# Rust producer runner A02 parent source review

Disposition: preserve A02 and reject source qualification before compilation. One P1 and three P2 findings remain. Independent source review is pending.

Root read the final A01-to-A02 changes, complete A02 lifecycle and inventory paths, pure helpers, CLI, and all package documents. All eight manifest-bound rows match current bytes: 84,924 bytes. Manifest SHA-256: `dc4cb1e93fac4198ec8a994b605fb9114259629ac443868d02bb22fa72c9f856`. Source aggregate: `3b01bf68b103588e73e02bc99fd8117a5e451029546d71d6edf4638de62fd99a`.

A02 closes the A01 duplicate equality implementation, macOS mode conversion, retained parent pipe writers, shared directory-stream offset, mutable run-root metadata comparison, terminal fallback disposition, and caller-mutable closed result. The reaper observation is bounded; its disclosed detached-thread limitation remains.

## Findings

1. **P1 — file opens can block before type validation.** `src/lib.rs:1567` and `:1587` use blocking `O_RDONLY`. Authority reads open the path before checking regular type. Inventory can observe a regular name, then open a replacement FIFO. Neither call has a deadline. A FIFO can therefore block before the bounded read or child wall-time policy applies. Open with nonblocking semantics and reject nonregular descriptors before reading.

2. **P2 — post-read regular-file identity is weakened to an anchor.** `src/lib.rs:755` and `:901` compare the pathname only by device and inode after `observe_fd` has returned. A same-inode mutation between the final descriptor stat and pathname stat is admitted. Authority postflight can retain an old observation even when the later pathname stat shows changed metadata. Require complete stable identity equality for regular files. Keep expected run-directory creation metadata separate.

3. **P2 — TERM delivery facts record an attempt as delivery.** `src/lib.rs:1193`, `:1212`, and `:1304` discard `send_group_signal` returning `Ok(false)` for `ESRCH`, then set `term_sent = true`. The report can therefore claim TERM delivery when the syscall reports no target. Keep an attempted/requested state for escalation and record the actual delivery boolean independently.

4. **P2 — saved log observation is not joined to the capture writer.** `src/lib.rs:546` reopens `producer.log` by name. The runner does not compare that file with the original held write descriptor. A producer that renames and replaces the log can yield a pending result whose reported log is unrelated to the captured stream. Compare the held capture descriptor with the read descriptor and final pathname, or read through an appropriately opened held descriptor.

## Scope

This is static source review. No compiler, import, pure control, runner, native producer, media, GPU, or Resolve process ran. JSON fixture declarations are unexecuted schedules. The qualification loader remains unavailable. No accepted authority, native result, product integration, WATCHED, HEARD, or creative acceptance was created. These observations remain same-family review evidence.

A narrow additive A03 repair is authorized. A01 and A02 remain frozen.
