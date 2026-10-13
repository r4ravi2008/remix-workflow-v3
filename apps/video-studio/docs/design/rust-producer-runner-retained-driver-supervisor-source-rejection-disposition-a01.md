# Retained-driver supervisor A01 combined source disposition

State: **source rejected; preserved and unexecuted**.

ROOT fully read the separate 7,743-byte peer report, SHA-256
`49e80cf9df4e0bdc44a8bac7da4c905e42bb17c858f091f3d58c388a96887cfa`.
The ROOT report remains independent: one P1 and one P2. The peer report records
three P1 and four P2. This disposition maps the findings into four repair groups.
It does not replace either review or create execution authority.

## Required narrow repairs

1. Preserve known terminal facts before any numeric-PID signal. Record actual
   SIGCONT attempt, delivery, and resume facts separately. A proven failed
   signal call can use stopped-child cleanup. An ambiguous resume attempt must
   retain the driver without destructive signals. A finite pre-resume reap
   guard may publish unresolved cleanup, but the owner remains retained until
   actual terminal facts exist.
2. Define strict zero-exit success. A nonzero driver exit remains failed while
   outer closure can independently be complete.
3. Publish typed pre-resume failure evidence before closing the attempt
   descriptor. Preserve not-started, stopped, already-terminal, and unresolved
   facts. Report a process group only after its actual observation and private
   ownership check. Otherwise report null and the observation failure.
4. State the future caller's pre-import manifest, held-source, and operation
   gate requirements. Loading this module does execute the pinned A04 source.
   The module cannot grant its own operation authority.

## Scope interpretation

The current failure publisher runs only after a resume attempt. The private
group check precedes that attempt. Thus the peer's unobserved-group concern is
not reachable in the current post-resume publication path. Adding pre-resume
publication makes explicit unknown-group representation necessary.

The retained-owner policy deliberately has no early return after an unresolved
wait. A bounded pre-resume guard must record failure and retain ownership. It
must not close authorities or declare a fabricated reap when the guard expires.

`sigcontDelivered=false` alone does not prove user code never ran. The accepted
A04 method sets the attempted flag before the signal call and the delivered
flag afterward. An ambiguous exception between these operations must retain
the owner. Only the actual signal-call failure can establish failed delivery.

The dependency import is an authorized-load boundary for a future caller.
Clarifying that boundary does not require a new native ownership protocol,
control matrix, or change to the accepted A04 utility.

## Remaining gates

Prepare a separate A02 successor. ROOT and peer must review its actual frozen
source before a controls or native caller can use it. The independent A13
compiler-only wrapper may continue preparation. All import, control, producer,
native, product, playback, hearing, and creative acceptance remain false.
