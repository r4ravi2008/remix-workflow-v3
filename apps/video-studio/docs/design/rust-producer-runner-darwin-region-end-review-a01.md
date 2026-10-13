# Darwin region scan end semantics review A01

Date: 2026-10-11

## Scope and identity

This is a read-only source review. No compiler, import, probe, native process, or media action ran.

The reviewed source is `rust-producer-runner-a06/src/lib.rs`, SHA-256 `46eea07941b34504bad203fd3bce8c901ecafc4da78e18ff5fcdbb1f1b210f9c`.

The frozen A06 manifest is `rust-producer-runner-a06/source-manifest-a06.json`, SHA-256 `98d225bed7f2dde75d0bd882292a30b3f26cf421da61bd2938d917a2f2976fe1`.

## Result

The A06 region-walk end condition is incorrect for the Apple implementation reviewed here.

At `lib.rs:2172-2189`, A06 clears `errno`, calls `libc::proc_pidinfo` with flavor `8`, and treats `received == 0` as a clean end only when `errno` remains zero.

Apple's kernel path returns `EINVAL` when the region lookup has no next region. Apple's user-space wrapper converts the failing `__proc_info` result to `0` and leaves `errno` as the error. Therefore the normal end is observed as `received == 0` with `errno == EINVAL`, and A06 returns `loaded_region_walk_failed` instead of setting `clean_end`.

This is a source-level P1 for the launch identity path. It is not a runtime observation. The saved Darwin probe does not exercise the frozen Rust A06 function.

## Primary source trace

1. The kernel `proc_pidregionpathinfo` implementation calls `fill_procregioninfo`. When that lookup returns zero, it returns `EINVAL` before copying a region record. The same file shows the corresponding `PROC_PIDREGIONPATHINFO` dispatch and returns the helper error unchanged.

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/proc_info.c#L1034-L1065>

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/proc_info.c#L1773-L1964>

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/proc_info.c#L2071-L2094>

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/proc_info.c#L2270-L2276>

2. The same kernel implementation returns `ESRCH` when `proc_find(pid)` cannot find the process. Security-policy failures also return their own error. These errors must remain failures, rather than becoming region-scan termination.

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/bsd/kern/proc_info.c#L1926-L1963>

3. Apple's `proc_pidinfo` wrapper calls `__proc_info`. It returns zero when `__proc_info` returns `-1`; it does not clear or replace `errno` in that branch.

   <https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/libsyscall/wrappers/libproc/libproc.c#L93-L103>

4. Apple's private test source calls `__proc_info` directly and checks it as a POSIX-style operation. This confirms that the low-level call is the error-reporting boundary, while `proc_pidinfo` is the lossy zero-return wrapper.

   <https://raw.githubusercontent.com/apple/darwin-xnu/main/tests/proc_info.c#L100-L126>

   <https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/syscalls.master#L336>

The conclusion that kernel `EINVAL` reaches user space as `__proc_info == -1` with `errno == EINVAL` follows the Darwin syscall ABI. This review did not run that syscall.

## Exact A06 consequence

The A06 source has the following relevant sequence:

- `clear_errno()` writes zero through `libc::__error()` at `lib.rs:2174` and in the helper at `lib.rs:3032-3051`.
- `libc::proc_pidinfo` returns zero for a failed low-level call.
- `errno_is_set()` sees the kernel's `EINVAL` and returns `true`.
- `loaded_region_walk_failed` is emitted at `lib.rs:2185-2186`.
- `clean_end` remains false, so the later cap error is not reached for this normal endpoint.

The 256-region bound is useful, but it does not repair this terminal condition. A successful mapping record has already established the next cursor, so the scan needs an explicit endpoint classification.

## Bounded alternatives

The smallest repair is to capture `errno` immediately after each call and classify the zero result explicitly:

- `received > 0` requires the exact 1,272-byte record, positive size, checked monotonic end, and all existing path/protection/vnode checks.
- `received == 0 && errno == EINVAL` is a candidate normal end only after at least one valid row and a nonzero cursor were accepted.
- `received == 0 && errno == ESRCH` reports process disappearance.
- `received == 0` with `EPERM`, `EACCES`, `ENOMEM`, `EFAULT`, or another error reports a query failure.
- A zero result on the first query remains a failure. It cannot prove that a process has no regions.
- Exhausting 256 rows remains a cap failure.

The prior-row and nonzero-cursor guards prevent an initial invalid query from being accepted as an empty process. The existing monotonic and overflow checks remain required. The error value must be copied before any later libc call changes `errno`.

A raw `__proc_info` declaration could preserve the `-1` result, but it is a private interface and still requires the same `errno` classification. It does not remove the need to distinguish `EINVAL` from `ESRCH` and other errors.

Using Mach VM region enumeration would avoid this particular sentinel, but it introduces a task-port access path and a different permission contract. It is outside the current A06 route and is not needed for this narrow repair.

## Disposition and limits

Disposition: source finding confirmed; no runtime qualification.

The review does not establish loaded-image identity, process lifecycle safety, native producer execution, media output, or product acceptance. It only resolves the end semantics of the frozen A06 `PROC_PIDREGIONPATHINFO` scan.
