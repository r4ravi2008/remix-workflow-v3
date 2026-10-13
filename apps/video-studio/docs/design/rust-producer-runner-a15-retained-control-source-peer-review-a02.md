# Rust producer runner A15 retained-control source peer review A02

## Disposition

**Source review rejects this preparation before execution for one P2 finding.**
I found zero P1 and zero additional P3 findings. The retained caller keeps the
required Supervisor A02 ownership boundary and the required nested evidence
joins. Its failure publication does not state the execution fact precisely when
the supervisor raises after starting a child.

This is a same-model-family, nonblind, source-only review. I read the complete
caller, contract, rationale, source manifest, the bound Supervisor A02 source
and contract, the Supervisor A02 ROOT and peer reviews, and the pinned A04
utility identity. I did not import, compile, execute, test, launch a child,
run a process probe, or use native, media, GPU, Resolve, playback, listening,
or creative workflows.

## Frozen subject identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_retained_controls_a15.py` | 55,353 | `8c82ab5eafb11f3e0639fd12ca604f5318792cd5d9df697d3962309c632fee4a` |
| `retained-control-contract-a02.md` | 2,768 | `23f1d540026aeed0ec761850db267bfade3e3019f4086d7a5dac5d9626fdf4c2` |
| `source-package-manifest-a02.json` | 12,236 | `4d7d68d6d0cfbf34949f411f5351f614fa5141dae3a3a3bf34f5d2cdc2c50bfb` |
| `source-rationale-a02.md` | 947 | `1b37683f3c67d5168010a5c6f158a04be304cbe83d3b7c51f135493c40a9b703` |

The three source rows total 59,068 bytes. I rehashed all three rows and all 21
external bindings. No row was missing or changed. The manifest-excluded source
aggregate recomputed as
`0ed26c034c04facb24b6957d73e566349645dce2a56146ba4289da975e5967a5`.
The external aggregate recomputed as
`79f15c962d2de202788bf099b4c12cd6e696881bb402a9f401b93ae185275424`.

The bound Supervisor A02 identities are:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `retained_driver_supervisor_a02.py` | 33,116 | `50600911ab331f2c2a03ea814f3783a83007e9b647318a8fe74d7ef3b477a863` |
| `supervisor-contract-a02.md` | 5,147 | `fd92fe380a99c3b5fb84caf2fc5b58c28fe9468cf32ec2df388fb85d0c14188c` |
| `source-rationale-a02.md` | 1,421 | `66661a800724f5db357560cbfa40b91d98ea1ec44d2a250a3ead01badbb01df9` |
| pinned A04 utility | 46,572 | `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d` |

The caller binds Supervisor A02's manifest, source, contract, rationale, ROOT
review, peer review, post-drift rejoin, and post-drift disposition. The
manifest correctly records `continuousImmutabilityEstablished: false` and
`currentReviewedBytesRejoined: true`.

## P2.1: a raised supervisor call is reported as `controlsExecuted: false`

The caller initializes `phase = None` at
`native_runner_retained_controls_a15.py:307`. It assigns `phase` only when
`run_retained_driver_phase(...)` returns at lines 515–521. The failure hook at
lines 368–436 then sets both `retainedDriverPhase` and `controlsExecuted` from
that variable. In particular, line 382 publishes:

```python
'controlsExecuted': phase is not None,
```

Supervisor A02 can start a child before returning a phase. Its
`run_retained_driver_phase` creates the owned process at lines 450–453, checks
the private group and launch streams, and calls `attest_and_resume` at line
471. If the pre-resume branch matches `process is None`, no resume attempt, or
the actual pre-resume `SIGCONT` error, the supervisor publishes its typed
pre-resume failure, closes its own attempt descriptor, and raises at
`retained_driver_supervisor_a02.py:487–553`.

The caller's separate attempt descriptor remains available to its failure hook,
so the caller can publish a failure measurement. However, `phase` remains
`None`. The failure record therefore says `controlsExecuted: false` and
`retainedDriverPhase: null` after a call that may have created a stopped child,
recorded a process group, and published pre-resume observations. The same
boolean also represents a genuine preflight failure before the supervisor call.

This conflates at least four states: the call was never attempted, the call was
attempted but the child was never created, a child was created before a raised
pre-resume failure, and a returned phase was unavailable. A false value cannot
prove that the retained control invocation did not occur. It also does not
preserve the distinction between attempted invocation, confirmed resume, and
unknown execution when the call raises.

A successor should record an invocation state before the call and preserve a
structured raised-call outcome. It should distinguish `not_attempted`,
`started`, `resumed`, `returned`, and `raised_unknown` using the Supervisor
pre-resume receipt and actual PID or launch facts. Keep the existing boolean
false only when the source has explicit evidence that no control invocation
occurred or that no child was started. Use an explicit unknown state when a
raised call lacks usable execution proof. Keep native, product, WATCHED, HEARD,
and creative fields false in every branch.

This is P2 because the caller cannot publish an accepted control result after
the raised call. The error still makes the saved failure evidence materially
misleading and weakens the required execution-fact record.

## Ownership and publication checks

The caller authenticates the eight Supervisor A02 authorities through regular,
canonical, no-follow, nonblocking reads before executing the held supervisor
source. The external gate remains required before this source can be evaluated.
The caller checks isolated, nonoptimized, no-bytecode Python after supervisor
source loading; that runtime precondition remains an external launcher
responsibility as stated by the contract.

The caller invokes `run_retained_driver_phase` synchronously. It does not wrap
the call in ordinary A04 `run_phase`, and it does not send a destructive outer
timeout after resume. The caller requires Supervisor A02's schema-2 outer
closure, terminal PID absence, private-group absence, stream EOF, authority
closure, attempt-anchor join, and attempt-descriptor closure before reading the
private output tree.

After the supervisor returns, the caller inventories the complete bounded tree,
checks the three exact malformed collision files, parses every other JSON file,
and joins every launch report to its saved terminal and process record. It
checks the 21 pure rows, 10 lifecycle rows, 15 focused rows, 11 launch variants,
and five review-reference variants in their declared order. Each process record
must have exactly 47 fields, including `reap_wait_errno` and
`reap_failure_observed`; integer fields reject booleans and all boolean fields
are checked as actual booleans.

The caller recursively collects direct child PIDs and process-group IDs from
the parsed records and PID marker files. It requires every collected PID and
group to be absent before measurement publication. It remeasures all input
rows and output files, then saves the full measurement record through its held
attempt descriptor. It closes its caller descriptors before saving the terminal
closure record. The terminal record remains `candidateAccepted: false` and
requires independent ROOT and peer readback. These ownership and ordering
checks did not produce an additional P1 or P2 finding.

## Scope and limits

The package state remains
`frozen_source_only_root_and_peer_review_pending`. Its retained-control gate,
caller ROOT review, caller peer review, compile readback, and actual controls
remain absent. The report is not an execution or authorization gate.

No source was imported or executed during this review. No compiler, control,
producer, native framework, media, GPU, Resolve, playback, listening, or
creative operation occurred. This review does not establish process execution,
loaded runtime identity, nested report acceptance, native output, product
integration, WATCHED, HEARD, or creative approval.
