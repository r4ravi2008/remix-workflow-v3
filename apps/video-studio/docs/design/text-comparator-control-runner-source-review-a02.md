# Focused comparator control runner A02 — independent source review

## Review status

I read the complete 3,011-line A02 runner, its 476-line A01-to-A02 source
delta, all four A02 package documents, and the A01 runner source and reviews.
I did not import, compile, execute, or run the runner, codec, helper, controls,
child, compiler, native process, media process, GPU process, or Resolve.

A02 correctly repairs the four A01 findings. It remains source-rejected because
the publication seal cap is smaller than a permitted retained capture record.
The cleanup and source-closure boundaries also need explicit successor policy.

## Frozen A02 package identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `run_comparator_controls_a02.py` | 150821 | `5350e3d15574181087396c31a5869893839bd6685f8b8a9ec22cfda3314c8a57` |
| `runner-contract-a02.md` | 8849 | `9364c1209f44a73716a0f813ef1ebfae620fd14aa19fb8ade51f7c07ae3238b0` |
| `output-schema-a02.md` | 3494 | `a2a365f3c6f6df3ea7c1e51e3469c0fc6664c9fe809c22b0f8e4bc2466269294` |
| `source-rationale-a02.md` | 3391 | `bb02d855aa7b2806d365197117e8d3cdd2ad25ccea443e5fc2cba9dd84727c71` |
| `source-package-manifest-a02.json` | 3757 | `d7d52c08185c2978da6bd71d2bc47fd7018e57e29a891a43abb1fc8e8357f32e` |

The manifest is self-excluding. All four rows match the current files by exact
size and SHA-256. The A01 manifest remains `e47bb19f385ab07bccc4795b2f8eb27fbf18ead3b565a6018593dce914708877`.

The A02 directory also contains these not-yet-manifested control inputs:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-controls-a02/control_comparator_runner_a02.py` | 38336 | `3ef4efbf74309e9c1b1940c1be3d7cb611e6628850730597957fbb7d3b3f0182` |
| `source-controls-a02/control-fixture-a02.json` | 23844 | `755db7475bc22b42564e43541c0cfbbcc497bddf234711b701e4c8e43178cab0` |

The package manifest explicitly marks the A02 control contract, control
manifest, reviews, source closure, and authorization as external rows pending.
This is consistent with the declared source-only state. The runner must not be
authorized until those rows exist and bind the two present control files.

## A01 repairs verified

The ordinary macOS `PosixPath` values now pass both absolute-path guards. The
capture boundary uses `isinstance(temporary, Path)` at line 1983. The held
directory boundary uses the same check at line 2246. The absolute-path checks
remain in place.

Capture timestamps now use `time.monotonic_ns()` and exact integer nanoseconds.
The record declares `monotonicUnit: "nanoseconds"` at lines 1994–2033. Event
timestamps use `atMonotonicNanoseconds` at lines 1860–1867. The nanosecond
deadlines convert back to seconds only for `selector.select` and `sleep`.

The positive started PID becomes `processGroup` before `getpgid` at lines
2077–2084. A `ProcessLookupError` during the live lookup is recorded as
`process-group-absent-before-live-observation` at lines 2085–2094. A different
live group still fails recursive exact equality.

`typed_equal` now recursively compares dictionaries, lists, tuples, and scalar
leaves at lines 438–451. It checks exact types before equality, so nested
Boolean and integer substitutions fail.

## P2 — the seal cap cannot contain the permitted capture record

The runner sets `MAX_SEAL_BYTES` to 4,194,304 and `MAX_CAPTURE_EVENTS` to 4,096
at lines 95–113. `_capture_event` retains up to all 4,096 event objects. Each
object contains an event, two state strings, and an integer nanosecond value at
lines 1860–1867.

`_seal_value` includes both complete runtime phase observations and the complete
capture record at lines 2710–2753. A source-only projection over the frozen A09
phase rows plus 4,096 valid retained events is 4,503,788 bytes. It exceeds the
4,194,304-byte seal cap by 309,484 bytes. The projection omits other domain,
capture, and seal fields, so the complete canonical value is larger.

The projection is preserved in
`comparator-control-runner-a02/root-publication-cap-lower-bound-a02.json`,
1,286 bytes, SHA-256
`536eca6006eed87acb15a9f807910f7e90f27c2aef56f324db38199c731fb1a8`. Its
scope records no runner, codec, helper, runtime scan, control, or native
execution. This review independently confirms the source join that makes the
projection applicable.

This is reachable under the declared event cap. The source does not prove that
the fixed child cannot generate 4,096 retained events. `canonical_publication`
rejects an oversized seal after encoding. The failure path rebuilds the same
seal shape at lines 2958–2962, so a full event history cannot receive a sealed
failure record either.

The successor must connect the retained-event bound to the seal owner. It can
reduce retained events, allocate a larger declared seal owner, or publish the
event history under a separate bounded owner. It must test the exact boundary.
Until this join is fixed, the runner cannot promise a sealed result for every
capture admitted by its own limits. This is a bounded publication-cap defect,
not a native or media acceptance claim.

## Normal publication review

The normal sequence is coherent through `request.json`, `preflight.json`, the
two stream files, the control report, the seal, and the allowlist check.

`AttemptPublisher.write` uses exclusive creation, no-follow flags, bounded
chunked writes, file `fsync`, descriptor reread, directory `fsync`, pathname
reopen, identity comparison, and a second reread at lines 2334–2385. It adds a
file to `entries` only after those checks. `inventory` checks the held root,
the seven-name allowlist, and the published entry set at lines 2396–2405.

The seal remains explicitly pending independent parent readback. The runner
does not claim loaded-image, provider, native, media, or creative evidence.

There is one post-seal failure ambiguity. `execute_request` writes the success
seal before `inventory` at lines 2905–2912. If inventory finds an extra file or
identity drift, the failure path tries to append a failure report. The publisher
rank rejects that report after the seal, because failure rank four precedes seal
rank five. The runner then emits `failure_publication_incomplete` while the
directory already contains a success-shaped seal. Parent readback must reject
that combination. A successor should inventory before sealing or define an
explicit post-seal invalidation record.

## Failure publication review

For errors before a publisher exists, the runner emits an outer failure and no
attempt receipt. This is a valid pre-publication scope, but `AttemptPublisher.create`
can leave an empty attempt directory when its post-`mkdir` setup fails. Its
exception path closes the child descriptor but does not remove or publish that
directory at lines 2278–2309. The successor needs an explicit orphan-directory
disposition or a bounded cleanup record.

For errors after publisher creation, the runner preserves stream files, writes
a failure report, writes a failed seal, and validates the failure allowlist at
lines 2924–2976. A partial file or publication error is retained as an outer
`failure_publication_incomplete` error. The source does not claim a seal after
that error, which is correct.

The final cleanup is not itself recorded. `publisher.close()` and
`unit_root.close()` run unguarded at lines 2984–2987. A close error can replace
an already prepared result, and a publisher close error can prevent the unit
descriptor from being attempted. The successor should record both cleanup
attempts and their errors without changing the already-published evidence.

## Process-group race and cleanup scope

The A02 getpgid repair is correct. The runner retains the positive started PID
before the live lookup. If the leader exits before `getpgid`, the recorded race
does not discard the group target. If pipes remain open, the pipe-residue path
can still signal that retained group. A mismatched live group fails.

The runner correctly keeps direct-child signal and process-group signal results
separate. It records `descendantsReapedAttested: false`, so it makes no false
descendant-reaping claim. Direct child wait and pipe closure remain bounded.

The runner does not perform a post-reap group-quiescence observation on an
ordinary clean exit. This is acceptable only because the contract limits cleanup
proof to the direct child and pipes. Any later report must not call ordinary
completion descendant cleanup evidence.

## P2 — source closure and authorization receipts are not cross-joined

`read_regular` checks final-path type, descriptor identity, bytes, hash, and
before/after stability at lines 517–563. It opens the final file with
`O_NOFOLLOW`, but it does not hold parent directory descriptors while reading.
An ancestor component can therefore be replaced between path operations.

`validate_source_closure` reads the closure rows, then
`validate_external_authorization` rereads the runner, codec, and source manifest
at lines 1721–1784. It compares each authorization receipt with that later read,
but does not compare those receipts with the corresponding closure-row receipt.
The same path can therefore produce two independently valid reads without a
single cross-joined source identity. A root-owned wrapper must hold or otherwise
bind the source roots and join every authorization row to its closure row.

This is a source-path integrity boundary. It does not establish any native,
media, loaded-image, or provider claim.

## Open invocation boundary

`_validate_process_environment` checks the executable, CPython version, three
flags, and six environment values at lines 2596–2630. `parse_run_request` checks
only the two mode arguments at lines 2990–2995. The runner does not inspect
`sys.orig_argv`, the exact runner script path in `sys.argv[0]`, or extra
interpreter options. The contract documents the fixed `-I -B` command and keeps
authorization external, so this remains an outer-launcher requirement rather
than a native or media claim.

## Scope disposition

No new P1 was found in the four A01 repair changes. The seal-cap mismatch is a
new P2 publication defect. Cleanup publication, source identity joins, and
exact invocation provenance remain P2 or external-gate items.

This review is same-family and nonblind. It establishes source inspection only.
It does not prove runner execution, child execution, comparator correctness,
loaded Python images, native text output, media output, provider origin,
watching, hearing, or creative acceptance. A successor must preserve the A01
package and bind all A02 control and external-authority rows before any run.
