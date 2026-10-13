# Runner A06 parent source review

## Disposition

Reject A06 before compilation. Preserve the frozen package unchanged.
A separate source-only A07 may repair the finite findings below.
Independent full-source peer review remains pending at this document's publication.

## Evidence and scope

Root measured the frozen manifest and every local and external row.
The source readback contains 394 inputs totaling 127,595,435 bytes.
All nine identity fields, contents, and before/after observations match.
Root resolved 26 explicit import/include edges across 22 Rust files.

| Evidence | Bytes or rows | SHA-256 |
| --- | ---: | --- |
| source-manifest-a06.json | 37,785 bytes | `98d225bed7f2dde75d0bd882292a30b3f26cf421da61bd2938d917a2f2976fe1` |
| local source aggregate | 14 rows / 293,236 bytes | `2c3e3ed40c2a19bb04c3e02f078ac23e122f465a721fc09807f6f274ce403293` |
| external aggregate | 84 rows / 10,317,267 bytes | `d4a9f9aad65b7f4c2acdebac0a6e50c2ef90fbe4418d6a5699b595f92af4f773` |
| parent source readback A01 | 468,508 bytes | `41a6b683d96b0ebe7f94323e1667ff8b090dce5c4c6cf96b2e863e8901600a28` |

Root read the complete changed library delta, complete focused-control source,
complete lifecycle-extension delta, pure source, fixture delta, entry points,
recipe, package configuration, rationale, README, contract, and output schema.
Unchanged source remains bound to the prior A05 full review and stable closure.
This review does not claim compilation or runtime behavior.

## Findings

### F1 — P1: the production library command has no Rust input

`direct-build-recipe-a06.json` declares four compiler commands.
The first command contains no source argument.
The other commands name `src/main.rs`, `src/lib.rs`, and `src/control_main.rs`.
The first command cannot build the library needed by the production CLI.
Add the exact `src/lib.rs` input to the successor recipe.

### F2 — launch readiness: the region-end rule needs correction

`lib.rs:2184` accepts only a zero result with clear errno as the region walk end.
Apple's kernel source returns `EINVAL` when `fill_procregioninfo` finds no region.
See [Apple proc_info.c](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/bsd/kern/proc_info.c),
`proc_pidregionpathinfo`, lines 1077–1080 in the reviewed source.

The saved OS canary did not record its terminal errno.
Root therefore does not infer a verified clear-errno end from that canary.
A separate read-only primary-source check is verifying the user-space wrapper.
Keep the successor fail-closed until a bounded normal-end predicate is grounded.
Do not convert every zero result or every `EINVAL` into success.
The walk must also retain a monotonic-address check, cap, and deadline.

### F3 — P2: required finite authorization and launch variants are absent

The mutation enum and `focused_run_all_a05` retain six authorization-file variants.
They omit separate mutations for schema, operation, implementation, repetition,
run directory, four qualification references, aggregate, cwd, process policy,
cancellation policy, and the product false flag.
The existing false-flag case mutates both flags together.

The package contains no stopped-launch control seam or finite launch variants.
Required variants include normal main-image admission, executable replacement,
cwd replacement, paused cancellation, proc failure, deadline, and scan truncation.
A rejected stopped child needs kill/reap evidence and an absent user-code marker.

Keep the existing fifteen focused group IDs and ten lifecycle IDs.
Declare only the finite variants required by this boundary.
Each authorization variant must join the saved causal code and no-child result.
Launch variants must use disposable copies of the private fake executable.
Never mutate or hardlink the frozen controls binary.

### F4 — P2: three pure results do not exercise production decisions

`a05_focused_controls.rs:758` computes a fixture mode/read boolean directly.
The ESRCH case echoes three fixture inputs into an object.
The pipe-drain case ignores its pipe and deadline inputs and forces `ReapFailure`.
These bodies can pass when the corresponding production decisions are broken.

Use shared production decision functions for these three cases.
Preserve the twenty-one IDs and their observed per-case results.
The FIFO integration control remains separate evidence.

### F5 — P2: launch ownership and closure facts have gaps

The first executable-open and observation error returns leak the supplied pipe FDs.
The observation error also leaves the opened executable FD alive.
Use owned cleanup on every return after resource acquisition.

On a process-group mismatch, cleanup sends a group signal to the observed foreign group.
Only the verified private group may receive group signals.
Otherwise kill and reap the owned direct PID.
The current branch returns an error without recording that a child existed.

An early exited child is reaped by the stop waiter, then its status is discarded.
Retain that actual exit/reap result in the failure report.

### F6 — P2: the report and pre-resume checks do not establish the launch contract

`ProcessObservation` records no stopped-state, loaded-main-image, cwd, held-hash,
scan-end, or resume observations.
A terminal report therefore cannot distinguish an admitted resume from a paused rejection.
Record bounded launch facts and the `SIGCONT` outcome.

The paused path revalidates opaque A02 evidence and the executable.
It does not remeasure all nine current runner authority rows before resume.
Those rows include the current runner bootstrap, source manifest, and binary.
Join those observations to the retained preflight rows before `SIGCONT`.

Executable and cwd descriptors close immediately after `SIGCONT`.
The conditional launch design requires those descriptors through child closure.
Keep the measured executable hash and full regular-file identity.
Use device/inode for cwd identity; mutable directory metadata is not its anchor.
The current full cwd comparison can reject valid directory updates.

### F7 — P2: output documentation and invocation ordering are inconsistent

The output schema names snake-case aggregate fields that the report does not emit.
The code emits nested camel-case results and counts.
Describe the actual exact report shape.

The recipe requires a reviewed A06 bootstrap before invocation.
Its unavailable-loader controls require that bootstrap to be absent.
Specify private controls before bootstrap publication.
Require the reviewed bootstrap before the production CLI invocation.

## Repairs already observed in source

Both CLI recipes now include both measured dependency search paths.
The stale qualification field and moved-layout expression are removed.
Review observations retain full identities and are reread before and after the child.
The authorization-file negatives expect the retained-file drift code.
Saved terminal checks require exact causal codes and process state.
The collision case calls the production writer and preserves sentinel bytes and identity.
The cancellation inventory checks the five permitted preterminal entries.
The positive two-entry field is derived from an observed result.
The marker fixture now contains an actual authorization entry.

## Remaining boundary

No compiler, control, bootstrap, authorization, or producer run occurred in this review.
Darwin source inspection is not loaded-runtime or producer attestation.
Successful direct execution must still be `completed_external_qualification_pending`.
Output/cancellation paths after resume need a future inherited-FD producer protocol
before output qualification or acceptance.
Native, product, WATCHED, HEARD, and creative acceptance remain false.
The independent review is same-model-family and nonblind; no cross-family claim applies.
