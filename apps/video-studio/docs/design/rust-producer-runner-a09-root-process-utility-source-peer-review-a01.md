# Rust producer runner A09 root process utility source peer review A01

## Disposition

**Rejected as a future wrapper execution authority.** Two P1 and two P2 findings remain.

The read, JSON, inventory, and process-cleanup improvements are material. The utility still lacks one retained ownership chain for command, cwd, attempt, and saved logs.

This review is source-only. I did not import or execute the module. I did not compile, test, spawn, probe, or start any child, native, media, GPU, or Resolve process.

## Frozen receipt

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_process_a09.py` | 20,344 | `8a5312dead50e5976d1873953a01396221cbc385112bf5d4f4b0b6bf7626d159` |

I read all 450 source lines. The file identity above matches the immutable provisional snapshot.

## P1 findings

### P1.1: Spawn does not retain or join executable and cwd authority

`run_phase` validates the cwd pathname, then discards the returned canonical path. It passes the original cwd value to `Popen`. See lines 250-252 and 306-312.

The function does not open or measure `argv[0]`. It accepts any non-NUL string and sends it directly to `Popen`. See lines 239-249 and 306-312.

A caller can measure the compiler or controls binary before this call. A transient pathname substitution can still change the executed image or cwd and restore the original before later measurements.

This utility therefore does not close the A08 wrapper's command-path race. A future wrapper needs a retained executable receipt and cwd directory anchor across spawn. The execution evidence must bind what the child actually used.

### P1.2: Attempt and log ownership are reopened by pathname

`run_phase` validates `attempt`, but it retains no directory descriptor. See lines 248-251.

The finalizer later calls `save(attempt / name, ...)`. `save` reopens the attempt directory through its pathname. See lines 415-419 and 112-143.

`save` closes the newly created file before readback. It does not compare the created file's inode with the reread file's inode. A leaf replacement can therefore return a receipt for another file with equal bytes.

A directory substitution can redirect both logs. A leaf substitution can replace either exclusive file before verification. The process result then attributes those files to the original attempt.

Hold the attempt directory descriptor for the entire phase. Create, fsync, and reread each log relative to that descriptor. Compare the created descriptor identity with the final readback identity.

## P2 findings

### P2.1: Input and JSON-output allocations are not fully bounded before allocation

The utility caps the argv item count, but it does not cap each item or aggregate argv bytes. It does not cap environment count, key bytes, value bytes, or aggregate bytes. See lines 239-247.

The returned process record retains both complete values. `Popen` also receives them before any aggregate admission check.

`save` calls `json.dumps` before checking the encoded byte cap. See lines 112-118. An arbitrarily large object can allocate past the stated file cap before rejection.

Add fixed aggregate argv and environment limits before `Popen`. Require valid environment keys and NUL-free values. Accept measured bytes for publication, or encode through a writer that enforces the cap during encoding.

### P2.2: Causal failures lose the specific bounded error code

`failure` retains only stage, exception class, and errno. See lines 270-276.

Internal `require` failures use stable strings such as `spawned_group_not_private`. Those strings are discarded. The saved result reports only `process_group_readback`, `ValueError`, and null errno.

The same loss affects path, selector, stream, save, and final-absence failures. A later review cannot distinguish different failures within one stage.

Use a private error type with a fixed bounded code. Preserve that code in `causalFailures`. Do not serialize arbitrary exception text.

## Verified improvements

`_read_at` opens regular files with `O_NOFOLLOW | O_NONBLOCK`. It compares pathname, held descriptor, size, bytes, hash, and full identity before returning.

The JSON reader caps input bytes. It rejects duplicate keys and nonfinite constants. Exact application schemas remain a caller responsibility.

`inventory` retains directory descriptors during recursion. It bounds depth, entries, paths, and regular-file bytes. It rejects symlinks and unexpected special files without reading FIFOs.

`run_phase` reads the actual PGID and accepts only a private group equal to the child PID. It records PID and group absence separately.

The process finalizer runs after spawn and setup exceptions. It bounds TERM, KILL, pipe-hold, stream-retention, and reap windows. It records unresolved cleanup and refuses `closureComplete` when any required condition remains open.

Stream buffers stay within their fixed retained caps. Both output files must save successfully before `closureComplete` can become true.

## Scope limit

This review covers only `native_runner_process_a09.py`. It does not review any caller, compile wrapper, controls wrapper, authorization helper, or future A09 runner.

The utility has never been imported or executed through this review. The four future wrappers remain separate and unreviewed. This source review cannot authorize their execution.

This is a same-model-family, nonblind review. The A08 wrapper findings were known before this utility review. No cross-family reviewer was available.
