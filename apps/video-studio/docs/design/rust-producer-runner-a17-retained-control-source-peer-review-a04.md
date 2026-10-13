# Runner A17 retained-control A04 source peer review

This is a same-family, nonblind, source-only review of the frozen A04 retained-control caller. It does not import or execute the caller, Supervisor, controls, compiler, native producer, or any candidate binary.

## Frozen package and row recheck

The package is `rust-producer-runner-a17-retained-control-preparation-a04`.

- Manifest: 45,050 bytes, SHA-256 `e3401393028553f925b6ab4ac7c40ecc2a5bfa4bc43b1bf1776a6bf31daafbaf`.
- Caller: 87,927 bytes, SHA-256 `198f5e7a6a9213800da70a05aeb9b35c71ebabb4624d7a1224aa7bb9e6da661f`.
- Contract: 4,875 bytes, SHA-256 `dc9c91a4f64980b74e8af8543d0b1a4aae71fcb428084e392d73ae593599ca31`.
- Source rationale: 2,154 bytes, SHA-256 `5359305182242286531599202344ae81b6d546eb472d7de9be6ef81d10a34049`.
- A03-to-A04 patch: 66,358 bytes, SHA-256 `b20e57bfed6fe471aef918782ba4b104618d1b37972a06b36c6d0e6382d9d12a`.

The four package rows contain 161,314 bytes. I recomputed the declared source aggregate with its stated UTF-8, zero terminator, big-endian length, byte-count, and raw SHA-256 encoding. The result is 370 encoded bytes with SHA-256 `1d18e6c36621b7190d98f5f8d383ec1b89e58a4bdbae9d86e859f7dacda8e126`.

The 93 external rows contain 77,121,587 bytes. I recomputed the declared role-then-path aggregate. The result is 24,289 encoded bytes with SHA-256 `3571d894464848163d965fdd9c518400c685d96b0cc81e3ea08769de389541ea`.

All four package files and all 93 external files were reopened. Their current bytes and SHA-256 values matched the manifest. I also measured all nine identity fields for every current row: device, inode, mode, links, uid, gid, bytes, mtime nanoseconds, and ctime nanoseconds. The manifest rows carry bytes and SHA-256 rather than expected identity objects, so these identity measurements are independent current observations.

## A03-to-A04 repairs

A04 advances the caller, build, recipe, gate operation, source decision, and output paths from A15 to A17. It binds compiler preparation A09 and the A17 full identity-bearing build readback. The A03 behavior is otherwise preserved through the declared patch.

The first repair separates the retained Supervisor phase from compiler command rows. The caller owns `retained_phase` and `supervisor_invocation`; compiler rows remain inside the build measurement. The invocation state changes before the synchronous Supervisor call. A returned phase is accepted only when the call returned a dictionary. A raised call cannot reuse a compiler row or an earlier phase value.

The second repair validates complete Supervisor A02 observations. The caller requires these exact schemas:

- returned phase: 49 fields;
- pre-resume failure: 21 fields;
- pre-resume unresolved observation: 18 fields;
- post-resume failure: 16 fields.

The validators reject missing, extra, or malformed fields. They check nested receipts, vnode identities, anchors, process groups, cleanup state, wait statuses, failure prefixes, monotonic ordering, signal delivery, resume state, and false native/product scope flags.

The raised-call paths preserve uncertainty. A raised call without valid saved evidence produces `raised_without_returned_or_saved_observation` and null process-start, resume, and control-execution facts. An attempted SIGCONT without proven delivery produces null control-execution evidence. Valid saved pre-resume and post-resume observations use separate state and causal checks. The three fixed observation paths must be absent before invocation.

## Build and gate joins

The source requires the 13-key A17 external build readback at:
`rust-producer-runner-a17-fixed-compilation-root-readback-a01.json`.

That readback is 1,598 bytes with SHA-256 `2df2cca8579f0062eccec23169f23bd08e83aa0218b30606c64b74a4c1621b40`. Its exact keys include full identity-bearing `measurements` and `terminalClosure` receipts. The caller compares both complete receipts with the live parsed A17 build files. It also requires four named command rows, zero return codes, reaping, process and group absence, complete closure, no causal failures, and no termination reason.

The compile-only A09 gate is joined to the build's `rootGate` record. The required operation is `runner_a17_fixed_four_compiles_gate_a09`, with only `fixed_four_compiles` allowed and native production disallowed. The retained-control gate and retained-control decision are future inputs. The A04 package records both as absent and grants no execution authority.

The A04 source binds eight Supervisor A02 authorities: manifest, source, contract, rationale, ROOT review, peer review, fresh rejoin, and post-drift disposition. Each authority is read through the bounded fixed-input path, which verifies all nine identity fields before the gate receives its reference. The retained gate join itself carries the full path, byte count, and SHA-256 reference. The package correctly records `continuousImmutabilityEstablished=false`, while requiring current reviewed bytes and all eight authorities.

## Schedules and process schema

The fixed schedule remains 21 pure cases, 10 lifecycle cases, 15 focused cases, 11 suspended-launch variants, 5 review-reference variants, and 3 deliberate malformed collision files. The caller checks the pure fixture IDs and exact focused, launch, lifecycle, and review order.

The nested process record is strict and has 47 fields. The source partitions them into 18 optional integer fields, 2 optional string fields, 24 booleans, and 3 nonnegative counters. The required new fields are `reap_wait_errno` and `reap_failure_observed`. The caller checks exact field sets, scalar types, process-group relationships, injected-fault joins, marker rules, terminal wait status, and unresolved-cleanup state.

The caller parses every JSON output except the three explicitly bound malformed collision files. It verifies the three malformed files by exact relative location, run-name shape, byte count, and SHA-256. It requires the combined report, ten lifecycle rows, fifteen focused rows, twenty-one pure rows, eleven launch rows, and five review variants. It joins each saved report to its terminal and process records before publication.

## Ownership and scope

The A04 caller invokes Supervisor A02 synchronously and does not wrap it in the ordinary destructive A04 `run_phase`. The 900-second value is an observation deadline. Forced host or tool termination remains unqualified. The returned phase must report outer PID absence, private group absence, stream EOF, descriptor closure, authority closure, attempt-anchor join, and attempt-descriptor closure before the caller publishes measurements.

The package records four completed A17 compiler builds from prior evidence. It records generated production and controls binaries as unexecuted. It records no retained caller execution, controls execution, native producer execution, native result acceptance, product integration, loaded-runtime attestation, WATCHED, HEARD, or creative acceptance. The package source remains unimported and source-only. The retained-control decision and gate are intentionally pending.

## Disposition

I found no P1 or P2 source defect in the frozen A04 package. The A03 phase-owner and exact-observation repairs are present, the A17 build joins use full identity-bearing receipts, the schedules and Supervisor A02 authority set remain fixed, and the source preserves uncertainty for raised or unproven-resume paths.

This review performed no import, compiler, control, gate, decision, child-process, native, media, GPU, Resolve, or project operation. It only read source, patch, contract, rationale, manifest, and current referenced files, then recomputed hashes and aggregates.
