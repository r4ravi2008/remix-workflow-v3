# Comparator runner A03 no-child controls — peer source review

## Review result

I found no P1 and two P2 coverage gaps. The package remains source-frozen and
unexecuted. It must not qualify runner A03 until a successor closes both gaps.

I read the complete control source, fixture, contract, and self-excluding
manifest. I compared the controls with the frozen A03 runner and the prior A01,
A02, and A03 reviews. I did not import or execute any runner, control, codec,
helper, child, compiler, native process, media process, GPU process, or Resolve.

This review is separate-author, same-family, and nonblind. I authored runner
A03. The judge authored these controls after the runner interfaces were known.

## Frozen identities

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `control_comparator_runner_a03.py` | 79,578 | `116e8099cdda156fecb9bc4aa6092ef9b852e4fc56e4704d9624608ac1fc53c7` |
| `control-contract-a03.md` | 7,224 | `973d9176a0de30a83c71aed4a9e513ca5ef99128d5926b4518bb6a9e9079f83b` |
| `control-fixture-a03.json` | 24,239 | `80c0bb6cfad1291e713c57ed733e68d0a933755d45ba0a668650bb73f5a6aa2e` |
| `source-package-manifest-a03.json` | 14,704 | `120d3e0c7683cc468e1b599c6d18e0eb224173f6b10e02c4cfd9d58a052a2748` |

All 45 manifest rows match current file sizes and SHA-256 values. Their total is
5,198,613 bytes. I independently recomputed the documented binary aggregate as
`7c2a5244067dfc7d581a535c4bc186b3c6be5e9d1ef47e161c5f99fa92e540d5`.

## P2 — the maximum report-owner control is not production-shaped

`maximum_capture_record` creates each retained event with `state`, `event`, and
`atMonotonicNanoseconds` at control-source lines 693–704. Production
`_capture_event` creates `event`, `before`, `after`, and
`atMonotonicNanoseconds` at runner lines 1952–1960. The synthetic event is
smaller and does not represent the retained production wire shape.

The control then places that record inside only `schema`, `operation`, and
`capture` at control-source lines 867–876. The production success report also
contains request hashes, child identity, validation, phase summaries, closure,
authorization, and scope at runner lines 3299–3329. The production failure
report has its own complete envelope at runner lines 3383–3402.

Therefore, the two 1 MiB encodes do not prove that the maximum production
success and failure reports fit their owners. This is a proof gap. It does not
show that either production report exceeds its cap.

The seal portion is sound at source level. It calls the production
`build_seal_value`, retains two complete measured domains, replaces events with
the bounded summary, joins the report reference, and encodes through the actual
canonical codec. That 4 MiB result remains unverified until a control runs.

A successor should use production-shaped events and complete success and
failure report values. Prefer one shared pure report builder if the runner needs
a source change. Retain the existing owner caps and the complete failure facts.

## P2 — only one fixed child command reaches the Popen gate

The fixture declares both fixed commands at fixture lines 751–778. However,
`PopenRecorder` always compares against `required-evidence` at control-source
lines 1200–1218. `fake_capture_controls` always selects the required-evidence
child at line 1374.

No capture case sends the A14 actual-comparator child through the production
command builder. A wrong actual-comparator source mapping could pass these
controls while the required-evidence mapping remains correct.

A successor should run one no-child fake-backend case for each `ControlMode`.
Each case should check the exact interpreter, `-I -B`, child path, working
directory, six-value environment, streams, descriptor policy, and new session.

## Confirmed production-seam coverage

The A09 positive case reads the fixed report, overlay, and diagnostic through
bounded descriptors. It calls the central raw binder and checks 1,548 rows and
45 overlay rows. Nested mutations exercise the central structure validator.

Recursive type controls reject Boolean and integer substitutions in mappings,
lists, and tuples. A09, phase, child, and scope mutations also exercise nested
production validators.

The child controls validate all 59 ordered actual-comparator results and all 12
required-evidence results. They cover exact loader identity, optional types,
missing and extra rows, order, duplicate keys, floats, and native qualification.

The fake backend enters the production capture loop. Its cases cover
prelaunch cancellation, Popen failure, post-Popen setup failure, clean exit,
deadline, TERM, KILL, final drain, both stream overflows, active cancellation,
direct-child fallback, retained pipes, the early `getpgid` race, and bounded
reap timeout. Applicable records encode through control or failure owners.

The ordinary macOS `PosixPath` case enters `BoundDirectory.open`, reads through
the held descriptor, checks stability, and closes the descriptor.

The source-join controls call the production recursive join validator for all
three roles. They cover content, identity, and later-read drift. The receipts
are structurally complete synthetic values, as the contract states. They do not
create a measured source closure or external authorization.

Both modes cover success, failure, and failure-after-control inventories before
and after seal publication. Negative cases cover order, duplicates, and using a
final inventory at the pre-seal boundary.

The post-seal classifier returns terminal outer failure. The setup classifier
distinguishes an owned empty directory from an unverified orphan. The cleanup
case proves that a failed publisher close does not suppress the unit-root close,
and that any close error invalidates qualification.

The report-reference control checks exact entry equality, role, content, and
aggregate bytes. The summary enforces the 4,096-event cap and event accounting.
The full event array is absent from the seal.

## Scope

The package is reviewable but has not passed. It establishes no real child,
subprocess, stream, signal, process-group, reaping, authorization, attempt,
publication, loaded-image, native, media, provider, playback, watched, heard,
or creative evidence. External launch provenance and parent readback remain
pending.
