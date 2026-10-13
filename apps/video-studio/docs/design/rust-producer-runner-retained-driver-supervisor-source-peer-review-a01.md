# Retained nested-driver supervisor A01 source peer review

## Disposition

**Rejected for execution pending repair.** The supervisor has the intended
retained-owner shape, but three P1 lifecycle findings and four P2 evidence or
boundary findings remain. Nested closure remains externally unaccepted.

This is a same-family, nonblind, source-only review. I read the complete A01
supervisor, contract, rationale, source manifest, and the pinned A04 utility.
I did not import, compile, execute, test, launch a child, run a process probe,
or use native, media, GPU, Resolve, playback, listening, or creative flows.

## Frozen identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `retained_driver_supervisor_a01.py` | 20,037 | `084484e3f443dde25e5a9dd561b86840efd47496f965ec43e3c9a595cfc2a7f3` |
| `supervisor-contract-a01.md` | 3,843 | `3d88d2f9ef3a6a15c985fa1d0289a40e1d476b948072fde0ff98d97700f3dd44` |
| `source-rationale-a01.md` | 1,174 | `2ae98ea9aed4f2d70469cd7fd14f4d41981a1b9722492547992201597e3073ae` |
| `source-manifest-a01.json` | 2,305 | `a5f530b71de4eb8989b9b2959a968fd0551f247b37c633b96af0544dae2e936d` |
| pinned `native_runner_process_a09.py` | 46,572 | `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d` |

The manifest declares three source rows, 25,054 source bytes, and source
aggregate `e93680b389f47f4a4bdaac65deb10e49b49491263b8786f4d29c56802dc655af`.
It declares one external row, 46,572 bytes, and external aggregate
`3df92cffb68b4c4fda791da9e3b3880df756a305af50e85306c8bff4d4d38b9a`.
The manifest state is `source_frozen_unreviewed_unexecuted`; all execution,
authorization, native, product, watched, heard, and creative flags are false.

## P1 findings

### P1.1: Pre-resume cleanup can signal a reaped PID

The A04 `attest_and_resume` path records `terminal_wait_status` and
`returncode`, then raises `child_terminal_before_stop` when the child exits
before the suspended stop is observed. The retained supervisor catches that
error and calls `_terminate_stopped_child` because `sigcontAttempted` is false.

`_terminate_stopped_child` does not first inspect `process.returncode` or
`process.terminal_wait_status`. It calls `os.kill(process.pid, SIGKILL)` using
the stale PID. A reaped PID can be reused before this call, so the cleanup can
signal an unrelated process. `ProcessLookupError` does not remove this risk.

Require a terminal-status check before every cleanup signal. If A04 already
recorded a wait status, publish `signalAttempted=false` and the existing
terminal facts, then skip `SIGKILL` and polling for a new reap.

### P1.2: Failed SIGCONT is treated as an already-resumed driver

The A04 method sets `launch['sigcontAttempted']=True` before calling
`os.kill(..., SIGCONT)`. If that call fails, `sigcontDelivered` and `resumed`
remain false. The retained setup handler tests only `sigcontAttempted`, skips
`_terminate_stopped_child`, publishes a post-resume failure, and enters the
retained polling loop.

The child can remain stopped forever. The supervisor then cannot observe EOF or
terminal absence and cannot close its descriptors. Use delivered or resumed
state for the pre-resume cleanup branch. Record attempted, delivered, and
resumed as separate strict booleans.

### P1.3: A nonzero outer exit can be reported as a successful phase

The returned `phaseFailed` value checks setup errors, recorded failures,
deadline state, and stream overflow. It does not check `process.returncode`.
`outerClosureComplete` also requires only a terminal status and cleanup facts.
Therefore a driver that exits nonzero with clean streams and no observation
error can produce `phaseFailed=false` and `outerClosureComplete=true`.

Require a strict integer return code and an explicit zero-exit condition for
phase success. Preserve outer closure as a separate fact, because closure can
be complete while the driver operation failed.

## P2 findings

### P2.1: Pre-resume spawned failures have no structured failure publication

When setup fails before `sigcontAttempted`, the handler kills or waits for the
stopped child, closes streams and authorities, closes the attempt descriptor,
and raises. It does not call `publish_failure_once`. A caller then receives an
exception without the retained failure-observation file and without a typed
summary of the spawned child, cleanup signal, wait status, or closure facts.

Publish one bounded pre-resume observation before descriptor closure, or define
the caller's exception adapter as the required durable publication boundary.
The record must distinguish a not-started child, a stopped child, and a child
already terminal before resume.

### P2.2: Failure observations can report an unobserved process group

`publish_failure_once` sets `driverProcessGroup` to `process.pid`. The value is
written before the setup code has necessarily read `os.getpgid(process.pid)`.
If group observation fails, the saved record still claims a group equal to the
PID. Store the observed group only after a successful private-group check;
otherwise store `null` with a typed observation error.

### P2.3: Stopped-child cleanup has no finite post-signal outcome

`_terminate_stopped_child` loops until `process.poll()` returns a terminal
status after `SIGKILL`. It has no deadline, bounded retry count, or explicit
unresolved-cleanup result. The main retained loop is intentionally persistent
after resumed observation failures, but this helper handles a child that has
not resumed and cannot own nested work.

Give pre-resume cleanup its own bounded reap policy. If the policy cannot
prove terminal status, keep the owner and publish an unresolved cleanup fact;
do not claim that the child was reaped or silently close its authorities.

### P2.4: The module executes the pinned utility during import

The module calls `_load_a04()` at top level. Importing the module therefore
opens, reads, hashes, compiles, and executes the measured A04 source before a
future caller can perform its own operation-gate transition. The held read and
identity checks are useful, but they do not replace a caller-side pre-import
source and operation authorization check.

Require the future caller to bind the manifest, utility receipt, exact command,
and operation scope before loading this module. Keep the loaded-runtime and
native ownership claims outside this source component.

## Verified positive properties

The A01 source uses a no-follow, nonblocking descriptor for the A04 utility.
It checks regular-file type, exact bytes, full identity, SHA-256, and held
descriptor stability before executing the measured bytes. Input argv,
environment, phase, path, stream, and aggregate byte caps are explicit.

After a successful resume, the source sends no termination signal. It keeps
polling the direct driver, drains both nonblocking streams, retains at most
4 MiB per stream, records overflow, waits for terminal status, waits for outer
PID and private-group absence, then checks executable and working-directory
authority identity before closing descriptors.

The returned result keeps `nestedReportsInspected`,
`nestedProcessAbsenceInspected`, and `nestedClosureAccepted` false. It requires
external nested report and PID or process-group readback. The source does not
create a cancellation marker or claim native ownership.

These properties remain source observations. They do not establish a compiled
package, a running driver, nested report validity, native output, product
integration, or creative acceptance.

## Scope limit

The A04 utility remains a pinned source dependency. Its own exceptional cleanup
supervision and arbitrary host termination remain outside this component's
guarantee. No new ownership matrix or native protocol is introduced here.
