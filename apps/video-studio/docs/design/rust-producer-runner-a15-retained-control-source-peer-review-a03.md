# Rust producer runner A15 retained-control source peer review A03

## Disposition

**This source review rejects A03 before execution for two P2 evidence-integrity
findings.** The A02 full-receipt comparison is repaired. The A06 compile
preparation binding is current. The Supervisor A02 ownership boundary and the
declared control schedules remain unchanged.

This is a same-model-family, nonblind, source-only review. I read the complete
A03 caller, contract, rationale, manifest, the preserved A02 caller source
and reviews, the Supervisor A02 source and contract, the pinned A04 utility,
and the A06 compile preparation sources. I did not import, compile, execute,
test, launch a child, run a process probe, or use native, media, GPU, Resolve,
playback, listening, or creative workflows.

## Frozen subject identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `native_runner_retained_controls_a15.py` | 60,827 | `30f6b14757ffd3428aaae6bbab4ae4078cea66d3672632428d745e63f73b09d3` |
| `retained-control-contract-a03.md` | 3,653 | `7f090725205584eeb94e1bd093d4ad17140b102fa1089439c2bf904c4fd8eb54` |
| `source-package-manifest-a03.json` | 17,147 | `33fb21d4a4c55b9c8869164422e596c036282569dbaa9a0958d4ef5700894dd3` |
| `source-rationale-a03.md` | 1,787 | `0493ea2fcc17772627e517fcf309a16c9567fa2eb968f1d881c205f6a742709f` |

The manifest declares three package rows totaling 66,267 bytes. I rehashed
all three rows. The source aggregate recomputed as
`f9deab0e31fd63b64e1e3bdf49c8dc28dce863103ae77da15644cdd143ecb795`.

The manifest declares 32 external rows totaling 19,153,323 bytes. I rehashed
all 32 rows. The external aggregate recomputed as
`88e9f8a601b88cf8084be84aaec323f762f033008e5f249ae90a366c2b7f4eef`.
The declared row order and both aggregate encoding recipes match the measured
bytes. No manifest row changed or was missing.

The eight current Supervisor A02 authorities match the manifest, including
the 33,116-byte source, the 5,147-byte contract, the 1,421-byte rationale, the
two accepted source reviews, the 13,120-byte post-drift rejoin, and the
1,969-byte post-drift ROOT disposition. The manifest correctly preserves
`continuousImmutabilityEstablished: false` and binds the current reviewed
bytes through the rejoin and disposition.

## A03 repairs that are correct

The A02 compiler-terminal defect is fixed at
`native_runner_retained_controls_a15.py:176`. The caller now compares
`terminal['compileMeasurements']` with the complete `build_record`, including
the `identity` field returned by A04 `save_at`. The external build readback at
lines 169–170 keeps its deliberate three-field `path`, `bytes`, and `sha256`
projection. This matches the A06 compiler caller, which writes the complete
four-field measurement receipt into `compile-terminal-closure-a01.json`.

The compile binding advances from A05 to A06 at lines 131, 188, and 189. The
caller requires the A06 operation `runner_a15_fixed_four_compiles_gate_a06`,
the four-command schedule, zero native-producer allowance, and the preserved
compile-only disposition. No A05 compile gate is used by the A03 source.

The new invocation record is set before the synchronous Supervisor call at
lines 315–319 and 626–637. The caller checks the three fixed observation names
are absent before invocation at lines 547–551. The fallback accepts only the
declared state names, phase, positive-or-null PID, false acceptance flags, and
typed launch booleans. The success path separately requires a positive PID,
started and resumed launch facts, a zero driver exit, and complete outer
closure.

The five schedules remain 21 pure cases, 10 lifecycle cases, 15 focused cases,
11 suspended-launch cases, and five review-reference variants. The process
schema still requires 47 fields, including `reap_wait_errno` and
`reap_failure_observed`. The three deliberate malformed collision fixtures
remain exact. The caller still checks nested reports and process or group
absence after Supervisor return, closes its descriptors before terminal
publication, and leaves candidate acceptance false.

## P2.1: the new execution-fact reader reuses `phase` for build commands

The retained phase starts as `phase = None` at line 314. The new
`retained_control_execution_facts` function reads that variable at lines
337–420. The build-input loop at lines 595–596 then rebinds the same variable:

```python
for phase in build['commands']:
    for row in phase['streams'].values():
        add(row)
```

That loop runs before the retained Supervisor call. A preflight failure after
the loop therefore leaves `phase` holding a compiler command dictionary.
Examples include failure opening the attempt directory at line 604, failure
opening the source directory at line 607, and failure publishing preflight at
line 623. The failure hook then reports that unrelated command as
`retainedDriverPhase` and sets `returnedPhaseAvailable` through the
`type(phase) is dict` branch.

The attempted-call branch is also wrong. If the Supervisor raises before
returning a phase, `supervisor_invocation['attempted']` is true but the stale
compiler dictionary still makes the function choose `savedObservationKind:
returned_phase`. The result becomes `raised_with_saved_observation`, even when
none of the three fixed Supervisor observation files exists. The contract
requires `raised_without_returned_or_saved_observation` with null execution in
that case. The returned PID and resume fields become null, but the evidence
state and retained phase remain false provenance.

This does not authorize a control result, but it makes the A03 repair fail on
the exact raised and preflight branches it was added to describe. Rename the
build-loop variable, or hold the retained phase in a separate variable and
make `returnedPhaseAvailable` require a returned call with a dictionary. Use
the same retained-phase variable in the failure hook.

## P2.2: observation fallback validation is not the exact Supervisor schema

At lines 348–371, the pre-resume branches validate only selected top-level
fields and the five launch booleans. They do not require the exact
pre-resume key set, including `streamDescriptorsClosed`,
`launchAuthoritiesClosed`, and `attemptDescriptorHeldAtPublication` on the
failure record. They also do not validate the nested `processGroup`, `cleanup`,
failure-prefix, terminal-status, and descriptor fields that the Supervisor
source writes.

The post-resume branch is weaker. It accepts a dictionary containing the
schema, expected state, phase, optional PID, three false scope flags, and a
boolean `driverResumed`. It does not require the Supervisor's
`driverProcessGroup`, `processGroup`, stage, code, signal, retention, or
cancellation fields. More seriously, `driverResumed: true` with
`driverPid: null` passes the current checks. Lines 382–405 then construct
`started: false`, `resumed: true`, and
`controlCodeExecutionObserved: true`. A malformed saved observation can
therefore claim control execution without a positive driver PID or a started
driver fact.

Validate a separate exact key set for each of the three Supervisor observation
records. Validate every nested scalar with `type(value) is ...`, reject extra
keys, and require a positive PID and started fact whenever resumed is true.
Keep the fixed-path collision check and the null unknown state for a raised
call without a valid observation. The accepted source boundary does not
remove this caller obligation because the caller publishes the observation as
its own execution evidence.

## Ownership and execution limits

The package correctly keeps the retained Supervisor call outside A04
`run_phase`. Its 900-second value is an observation deadline, not a
post-resume destructive timeout. The caller waits for outer PID and private
group absence, stream EOF, authority closure, attempt-anchor stability, and
attempt-descriptor closure before reading nested output.

The manifest state remains
`frozen_source_only_root_and_peer_review_pending`. The A03 gate and current
decision files referenced by the source are not present in the package at this
review point. The two new A03 review paths are also future gate inputs. This is
consistent with the contract's statement that ROOT must create the exact gate;
it blocks execution and is not treated as a source-row mismatch. Compile
outputs and retained-control outputs are likewise not present.

The caller does not accept compiler output, control output, native output,
media output, product integration, WATCHED, HEARD, playback, listening, or
creative approval. The A06 continuity break remains disclosed. No source was
imported or executed, and no compiler, control, child, process probe, native
framework, media, GPU, Resolve, or film operation occurred during this review.
