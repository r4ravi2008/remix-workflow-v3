# Runner A15 retained controls A02: ROOT source review

ROOT rejects this source preparation before execution for one P2 finding.
Zero P1 was found. Peer source review remains pending. Preserve frozen A02;
repair the execution-fact field in a separate successor.

## Exact reviewed subject

ROOT read all 55,353 caller bytes, the 2,768-byte contract, 947-byte rationale,
and 12,236-byte source manifest. Caller SHA:
`8c82ab5eafb11f3e0639fd12ca604f5318792cd5d9df697d3962309c632fee4a`.
Manifest SHA:
`4d7d68d6d0cfbf34949f411f5351f614fa5141dae3a3a3bf34f5d2cdc2c50bfb`.
ROOT independently reopened all 25 source and external inputs through held,
canonical, regular, nonblocking, no-follow descriptors. All nine identity
fields and both framed aggregates matched, including a second fresh reopen.
Readback `rust-producer-runner-a15-retained-control-root-held-source-readback-a02.json`
is 24,203 bytes, SHA
`e95611fe8a24f66679dcf2346839a8f9da43ac5858fc46bc502874b4eb2da9bc`.
Candidate source was AST-parsed only. No candidate or dependency was imported.

## P2: absent returned phase is not proof of absent process execution

The failure hook reports `controlsExecuted: phase is not None`. The caller
assigns `phase` only after `run_retained_driver_phase` returns. Supervisor A02
can create a stopped driver and then raise after its pre-resume cleanup.
Its source lines 447-553 preserve that actual child history in separate
observations. The caller would publish `controlsExecuted: false` despite
having attempted the invocation and possibly having created the driver.
A raised call can also lack returned execution proof. A missing return cannot
justify a negative execution fact.

Record invocation attempt before entering the supervisor. Distinguish actual
positive-PID process evidence, actual resumed-user-code evidence, and unknown
execution on a raised invocation. Preserve uncertainty when no usable returned
proof is available. Keep all native and product claims false. This correction
must not alter ownership, fixed schedules, native schema, or failure codes.

## Source observations and scope

The caller authenticates exact held supervisor bytes and all eight authorities.
It binds current-byte rejoin and disclosed post-freeze drift. It correctly
keeps continuous immutability false. A future independently reviewed launcher
must validate the exact caller gate before evaluation; this package includes
no launcher and grants no import authority.

The caller invokes Supervisor A02 synchronously. No ordinary A04 `run_phase`
wraps the nested driver. It joins outer closure, complete nested report bytes,
strict 47-field process records, exact schedules, three malformed fixtures,
actual PID and group absence, stable inputs, and descriptor closure before
terminal publication. The terminal remains externally nonaccepting.

The compile-only A05 wrapper has an independent source review. This P2 does
not reject its separate four-compiler scope. No build, controls, supervisor,
bootstrap, authorization, native, media, GPU, playback, listening, or creative
action occurred during this review. All execution gates remain absent.
