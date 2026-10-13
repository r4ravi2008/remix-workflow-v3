# Retained nested-driver supervisor A02 source peer review

## Disposition

**Source review accepted for the supplied bounded contract after final identity
recheck.** A02 closes the four A01 repair groups. No P1 or P2 finding remains
within this source boundary. A transient workspace drift occurred during the
review, so the final hash recheck below is part of this disposition. The
package is not an execution gate and does not accept nested, native, media,
product, playback, hearing, or creative results.

This is a same-family, nonblind, source-only review. I read the complete A02
supervisor, contract, rationale, manifest, the A01 combined disposition and
predecessor reviews, and the pinned A04 utility. I did not import, compile,
execute, test, launch a child, run a process probe, or use native, media, GPU,
Resolve, playback, listening, or creative workflows.

## Supplied frozen identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `retained_driver_supervisor_a02.py` | 33,116 | `50600911ab331f2c2a03ea814f3783a83007e9b647318a8fe74d7ef3b477a863` |
| `supervisor-contract-a02.md` | 5,147 | `fd92fe380a99c3b5fb84caf2fc5b58c28fe9468cf32ec2df388fb85d0c14188c` |
| `source-rationale-a02.md` | 1,421 | `66661a800724f5db357560cbfa40b91d98ea1ec44d2a250a3ead01badbb01df9` |
| `source-manifest-a02.json` | 3,672 | `e55383c79f58ac3651795b34aee2431f223088f7800a67ca6edf4fa79c9acb11` |
| pinned `native_runner_process_a09.py` | 46,572 | `b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d` |

The A02 manifest declares three source rows, 39,684 source bytes, and source
aggregate `7eb84204ce205019218398c4ab41cdced99bfca59d961f53bceaca80122f0f98`.
It declares five external rows, 62,478 bytes, and external aggregate
`38bf98df446605a0daea9160db0ca344b3d696dd9b27ad32e34fc7753b091209`.
Those external rows bind the A04 utility, A01 manifest, A01 peer review, A01
rejection disposition, and A01 root review.

The manifest state remains `source_frozen_unreviewed_unexecuted` because this
review does not mutate the frozen package. Its scope keeps import, execution,
controls, authorization, native, product, watched, heard, and creative flags
false. The A01 source remains preserved and rejected as historical evidence.

## Identity recheck and transient workspace drift

The package was temporarily observed with different source and manifest bytes
while this review was in progress. A final recheck now matches every supplied
identity above. The transient observations were:

| Artifact | Bytes | Current SHA-256 |
| --- | ---: | --- |
| `retained_driver_supervisor_a02.py` | 33,173 | `c907506ee4fdeca3d992f70b3e90d8d1d051f9ac71def6e6b5f39c882e57cc84` |
| `supervisor-contract-a02.md` | 5,147 | `fd92fe380a99c3b5fb84caf2fc5b58c28fe9468cf32ec2df388fb85d0c14188c` |
| `source-rationale-a02.md` | 1,421 | `66661a800724f5db357560cbfa40b91d98ea1ec44d2a250a3ead01badbb01df9` |
| `source-manifest-a02.json` | 3,672 | `1385bc318351b0048976c5c5e130308548c0ef1842e4944f0111b2b70f80aed0` |

During that interval, the manifest declared source rows for source SHA
`e40418c55ea5a132eec5cd302d165e60fa965567b9ac958a59a48635a7bfec47` and
contract SHA `f253245aa76aca610db664c780f958d701810cfd097616565fbad225020aa941`.
Its transient source aggregate was 40,405 bytes with SHA
`12ecb6c0f8f1fd2127cb9f79d90f632e6f85a1d46c6437e7a81ace4574cff4d9`.
That transient state is not the final subject. The final recheck restored the
supplied source, contract, rationale, and manifest hashes, including the
supplied source aggregate.

The pinned A04 utility remained unchanged at 46,572 bytes with SHA
`b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.
No package file was changed by this review.

## Repair group 1: pre-resume ownership and signal authority

`_finish_pre_resume_child` checks `process.returncode` and
`process.terminal_wait_status` before any numeric-PID signal. It calls the A04
nonblocking `poll()` once
before cleanup. A child known terminal is recorded without a `SIGKILL`, which
closes the A01 stale-PID risk.

The source records process-group observation separately. It sets the group
only after `getpgid` succeeds, the group equals the child PID, and the group
differs from the caller group. Mismatch or observation failure produces a
null group with a typed observation code.

The cleanup authority distinguishes resume never attempted, SIGCONT delivery
failure, and uncertain resume delivery. Only the first two authorized cases
can send the pre-resume `SIGKILL`. An ambiguous attempted delivery retains the
owner and sends no destructive signal.

## Repair group 2: strict exit and outer closure

The returned `driverReturnCodeAccepted` requires `type(returnCode) is int` and
value zero. Nonzero or invalid codes add a typed failure and set `phaseFailed`.
`outerClosureComplete` remains a separate fact. A failed driver can close its
outer resources without becoming an accepted operation.

After confirmed resume, the source sends no TERM or KILL. It keeps polling and
draining both streams after deadline, read, wait, and overflow failures. Each
stream retains at most 4 MiB while observed bytes continue counting.

The loop returns only after terminal wait status, outer PID absence, verified
private-group absence, and EOF on both streams. It then reads held executable
and working-directory authorities, saves bounded stream receipts, closes
streams and authorities, joins the attempt directory, and closes the attempt
descriptor.

## Repair group 3: typed pre-resume publication

Pre-resume failures now publish a typed record while the attempt descriptor is
held. The record distinguishes no child, terminal-before-cleanup, stopped
cleanup, uncertain resume delivery, and unresolved observation.

The three-second pre-resume observation deadline publishes an unresolved
record but does not release ownership or claim a reap. The source continues
polling until an actual terminal wait status exists. Stream and launch-authority
close results are recorded before the final pre-resume record is saved.

Failure records use schema 2, strict launch booleans, typed process-group
facts, terminal status, return code, failure counts, bounded failure prefixes,
and explicit false nested/native/product flags. The source keeps nested report
and nested process-absence inspection false.

## Repair group 4: external import and operation gate

The module still executes the measured A04 source during `_load_a04()`. The
A02 contract correctly makes this an external pre-import requirement. A future
caller must first bind the A02 manifest, held source receipts, accepted reviews,
exact operation, command, executable, anchors, environment, caps, and nested
report policy.

The module does not self-create that gate. Importing it without the external
boundary cannot qualify a control or native attempt. This is a caller contract
and remains outside the A02 source's authority.

## Bounded source conclusion

The final rechecked A02 source closes the A01 stale-terminal-PID, strict-exit,
pre-resume-publication, process-group-fact, and import-boundary findings. Its
finite deadline applies to observation evidence, while unresolved ownership is
retained until real terminal facts exist. That behavior is consistent with the
contract's owner-retention rule. This conclusion applies to the current
observed source bytes. The final recheck certifies the supplied frozen
identity for this source-only review.

Nested reports, nested PID or group absence, native output, framework loading,
media output, product integration, playback, hearing, and creative acceptance
remain externally unverified and false.
