# Rust producer runner A09 root process utility source peer review A02

## Disposition

**Rejected before caller preparation or execution.** Two P1 findings and one P2 finding remain.

A02 closes the A01 pathname, publication, input-bound, and causal-code findings. The grounded suspended-stop predicate is incorrect, and unresolved cleanup can still lose its final owner.

This review is source-only. I did not import or execute the module. I did not compile, test, spawn, probe, or start any child, native, media, GPU, or Resolve process.

## Frozen receipt

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_process_a09.py` | 41,133 | `323a378d656319b0fa8020fcb395d7b2cbb4b257bdcf7f2c20fe2440eaa74575` |

I read all 861 source lines and the complete A01-to-A02 change. The receipt matches the immutable provisional source.

## P1 findings

### P1.1: The grounded suspended child is rejected by the stop-signal predicate

`attest_and_resume` requires `os.WSTOPSIG(status) == signal.SIGSTOP`. See lines 503-520.

The preserved Darwin `POSIX_SPAWN_START_SUSPENDED` grounding observed `WIFSTOPPED=true` with stop signal `0`. The accepted Rust predicate also requires `0`.

The A02 utility would reject every valid grounded suspended child before main-image and cwd admission. It would then kill the child without `SIGCONT`.

Require the grounded zero stop signal. Keep terminal status and ordinary signal-stop rejection separate.

### P1.2: Unresolved cleanup releases the last process owner

The finalizer stops after the fixed TERM and KILL windows. It records unresolved direct-child or process-group cleanup. See lines 755-793.

It then closes every launch-authority descriptor and returns a serializable result. See lines 794-827 and 829-861.

`closureComplete=false` is truthful. The utility nevertheless retains no reaper or owned process handle after return. A live, stopped, uninterruptible, or zombie child can remain owned by the orchestration process.

Do not return the attempt as terminal while ownership remains unresolved. Retain an explicit cleanup owner until terminal wait status and group absence are observed. Keep this failure distinct from ordinary command failure.

## P2 finding

### P2.1: Executable and cwd authority are not rejoined at process closure

The utility rehashes the executable and rejoins the cwd anchor immediately before `SIGCONT`. See lines 568-573.

It retains both descriptors during the child lifecycle. It closes them without a final executable read or cwd path-and-anchor join. See lines 804-814.

The final result therefore proves pre-resume authority and descriptor retention. It does not prove that the executable bytes and cwd pathname remained unchanged through execution.

Perform a final held executable read and cwd anchor join after reap and before descriptor close. Record both observations. Require them for `closureComplete`.

## Verified A01 repairs

The utility admits aggregate argv and environment bytes before allocation. It requires one exact executable receipt.

The launcher holds executable and cwd descriptors. It uses `addfchdir`, `CLOEXEC_DEFAULT`, `SETSID`, and `START_SUSPENDED` before fallible post-spawn work.

The loaded main image must match one executable mapping by path, zero offset, execute protection, and six vnode fields. The loaded cwd must match the held directory anchor.

The region loop checks its elapsed limit before and after each `proc_pidinfo` call. One synchronous system call still has no user-space interruption bound.

The utility does not attest dyld or runtime dependencies. `runtimeDependenciesAttested` remains false.

The attempt directory stays open through both log publications. Each log uses descriptor-relative exclusive creation, same-created-FD readback, exact bytes, inode identity, fsync, and final attempt-anchor join.

The JSON encoder admits a conservative logical bound before encoding. The saved bytes remain capped during incremental encoding and descriptor-relative publication.

Private `BoundFailure` codes survive into bounded causal records. External exceptions remain classified by stage, fixed class, and errno without arbitrary exception text.

PID and PGID are observed separately. `closureComplete` requires terminal status, PID absence, group absence, both closed streams, both saved logs, and the final attempt join.

## Scope limit

This review covers only the immutable A02 process utility. It does not review any future source helper, compile wrapper, controls wrapper, authorization helper, or A09 runner candidate.

No utility or caller has executed through this review. The future callers remain separate and unreviewed. This report cannot authorize their execution.

This is a same-model-family, nonblind review. The grounded stop-signal evidence and prior A01 findings were known before completion. No cross-family reviewer was available.
