# Runner A18 source repair design

## Result

Runner A18 is a source-only successor to the preserved Runner A17 package.
It does not authorize compilation, controls, a producer child, native output,
or product integration.

The frozen A17 retained A04 attempt passed 21/21 pure controls, 9/10 lifecycle
controls, 4/15 focused controls, and 6/11 launch controls. A18 addresses only
the six groups established by the corrected A17 failure diagnosis.

## Complete authorization publication

`authorization.json` and `authorization-review.json` use a dedicated complete
publisher. The publisher creates a hidden stage with `openat(O_EXCL|O_NOFOLLOW)`,
writes all bytes, and fsyncs the held file. It then calls descriptor-relative
`linkat` with flags zero, so an existing final name fails without replacement.
The publisher unlinks the stage, fsyncs the directory, and joins held and final
full identities.

The local macOS SDK declares `linkat` in
`MacOSX.sdk/usr/include/sys/unistd.h`. The A18 call uses no platform-specific
flag. The terminal-prefix writer remains unchanged because partial terminal
evidence has a different contract.

The source-control build exposes separate authorization and sidecar
identity-complete rendezvous bits. Production builds contain neither bit. A
control waits before reading or mutating authorization. The producer waits
before reading the sidecar.

A failure before successful stage unlink retains the stage. Every failure after
final-name publication retains the final prefix. The publisher never unlinks a
final name because a concurrent actor could have replaced that name. This
private protocol does not claim universal concurrent identity stability.

## Review and mutation ordering

A control captures the original complete authorization after the rendezvous.
The review sidecar always binds that original snapshot. A declared mutation then
changes only its intended private fixture.

Every negative authorization mutation saves an exclusive delivery record. The
record names the mutation, stage, bounded details, and false native and product
scope. Typed field mutations also bind before and after hashes and exact changed
JSON paths. Same-byte review-reference replacement retains before and after full
identities.

The review sidecar uses the complete publisher. Runner A17's existing
`serde(deny_unknown_fields)` contract remains unchanged. A18 adds no unknown-field
variant.

## Launch controls

Same-byte executable replacement, different-executable replacement, and cwd
replacement use the existing production `PRESPAWN` rendezvous. Paused
cancellation stays at `STOPPED`.

Each nonempty launch action saves `mutation-delivery-a18.json`. Executable
replacement records the live object and retained original. Cwd replacement
records the original, replacement, and retained directory identities. A control
cannot pass without matching delivery evidence.

Normal launch requires start, stop, resume, SIGCONT delivery, reap, resolved
cleanup, and the user-code marker. Suspended failures require no resume, no
SIGCONT, reap, resolved cleanup, and no marker. Cwd path replacement rejects
before spawn and therefore requires no PID or reap.

## Lifecycle and focused controls

The FIFO lifecycle case accepts the saved `authority_missing` terminal on the
exact `AuthorizationNotReviewed` return. It still requires bounded elapsed time,
no child, no probe output, and false scope.

Focused prelaunch failures require no PID, no start, no resume, no reap, and
resolved cleanup. Same-byte root, peer, and sidecar identity replacements require
a started and stopped child, no resume, completed reap, and resolved cleanup.
Postflight drift requires start, stop, resume, SIGCONT delivery, reap, and
resolved cleanup.

The path-anchor case waits for the fake producer's saved invocation. It then
renames the run path, requests cancellation, and requires the exact
`run_root_parent_drift` postflight code. The saved process must have started,
resumed, reaped, and reached resolved cleanup. The
21 pure, 10 lifecycle, 15 focused, 11 launch, and 5 review-reference schedules
remain unchanged.

## Preserved evidence and pending work

The A17 source, A09 compiler preparation, A04 retained caller, failed reports,
and ROOT forensic readback remain unchanged. The direct A17 identities and the
corrected diagnosis are manifest inputs for A18.

The frozen retained caller still omits the fourth intentional malformed JSON
sentinel. Its exact relative path is
`focused/cases/authorization_path_collision/output-parent/collision-run/authorization.json`.
Its body is `authorization-collision-sentinel\n`, 33 bytes, with SHA-256
`a3b8e30e1f8de716401feff51dc0589442e7f4012d17905883bd24eb1a776916`.
ROOT owns any future caller successor.

A18 remains uncompiled and unexecuted. ROOT and an independent peer must review
this source before any separate compiler preparation or control attempt.
