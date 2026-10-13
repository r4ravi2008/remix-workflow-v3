# Comparator control runner A12 independent review

## Disposition

This review covers the frozen A12 design and saved A09 and A14 authorities.
It does not run the runner, comparator, control, compiler, or native process.

The A09 evidence is a complete, unqualified current-runtime observation. It
supports the fixed schema, row counts, overlay classification, and saved file
identities. It does not support loaded-image, provider, native, playback,
creative, or comparator acceptance.

The A12 design is internally coherent as a source-only plan. The full-domain
canonical vector is still an implementation gate. No accepted runner result
exists until that vector, the writer, the capture path, and parent readback have
independent source and byte checks.

## Reviewed identities

| Item | Path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| A12 runner design | `apps/video-studio/docs/design/text-comparator-control-runner-design-a12.md` | 35,574 | `a5a91fee3e23f8b64c051eb747bf030ea7422acf8329417e89d9df9091df4ab9` |
| A11 complete wire design | `apps/video-studio/docs/design/text-comparator-control-runner-design-a11.md` | 22,398 | `a4d388ce66f9d47d9d160ac3e8c60399dc61cacf21a34eff43dbd21bc91946f6` |
| A10 cap/capture design | `apps/video-studio/docs/design/text-comparator-control-runner-design-a10.md` | 27,406 | `08443a784b95a46b7de7602c4f1e2cac94974026d0b5990c446f03cb5bdd30da` |
| A09 runtime report | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-attempt-a09/runtime-snapshot-a09.json` | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| A09 observer source | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/freeze_observer_runtime_a09.py` | 55,732 | `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4` |
| A09 contract | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-contract-a09.md` | 14,189 | `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a` |
| A09 rationale | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-rationale-a09.md` | 6,202 | `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603` |
| A09 overlay | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-record-divergence-overlay-a09.json` | 25,945 | `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` |
| A09 diagnostic | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/runtime-record-declaration-diagnostic-a01.json` | 1,379,634 | `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` |
| A03 root launch receipt | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback-launch-receipt-a03.json` | 2,480 | `681dd4515dab592477336d21da9f2a75a791669a41ca302890b8d17f7514c6c0` |
| A03 readback source | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/readback_runtime_snapshot_a03_parent.py` | 28,044 | `857724047478e614389f7d93de3f4d8d7cca906d432eb3aa0845982b99c8f810` |
| A03 parent execution evidence | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/observer-runtime-snapshot-parent-execution-a09.json` | 861,763 | `7fb498f6659d2ba89a746c7234cb3a1664151dc171b36b31e998be39565de01e` |
| A14 package manifest | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/package-manifest-a14.json` | 14,110 | `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31` |
| A14 control source | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/actual-comparator-control-a14.py` | 50,342 | `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` |
| A14 package README | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/README-a14.md` | 2,781 | `9640d7439602e26e7d32a52fcfe2e1c78401967e4ff118d3506cef13fd659e10` |
| A14 output schema | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/output-schema-a14.md` | 6,508 | `cb638935ad79e212fd5eaf0a560c32ea49a7b015cbe6c8d386fa72c84bcab04a` |
| A14 rationale | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/text-report-comparator-a14/source-rationale-a14.md` | 2,216 | `ec9eacbf80364ab18194773a644b8b90da8f6a9c5b7bc3dc59d97bc482cd14bc` |
| A15 Swift source manifest | `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/feasibility-swift-a15/source-manifest-a15.json` | 11,656 | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |

The A14 package manifest declares output schema 3 and exactly 59 ordered
results. Its state is `authored_unbuilt_unexecuted_unqualified_pending_peer_review`.
The A14 source package is therefore a contract and control schedule, not a
captured child result.

## A09 authority comparison

The saved A09 report has exact root schema 4 and state
`current_runtime_filesystem_snapshot_complete_unqualified`. Its fixed facts are:

- 1,548 total rows;
- 1,503 strict non-overlay rows;
- 995 declared matches;
- 508 independently observed undeclared rows;
- 45 fixed measured divergences;
- zero unexpected divergences; and
- 45,567,887 installed file bytes.

The report preserves Pillow rows before NumPy rows. The separate overlay has
schema 1 and 45 rows. The diagnostic has 1,548 rows and describes exactly those
45 fixed divergences. The overlay remains a local measured classification. It
does not grant a general RECORD waiver.

The actual A09 entry symlink has path and target plus nine numeric identity
fields: device, inode, mode, links, uid, gid, bytes, mtime, and ctime. It also
has the two path-after-read and path-final checks. A12's `ObservedSymlink` and
binary encoding include every one of these fields in a fixed order. I found no
field omission in this comparison.

The A09 report was written with a pretty `json.JSONEncoder` and a trailing
newline. A12's compact canonical writer is a separate new wire. The two formats
must remain separate. The A09 report cannot serve as a canonical-writer vector.

## Closed binary encoding

A12 defines unambiguous U8, U32, U64, I64, BOOL, string, digest, and option
encodings. It fixes Pillow-then-NumPy row order and includes row, overlay, policy,
counts, flags, all twelve authority objects, and root endpoint facts. It also
excludes phase labels and phase counters from the phase-independent domain.

The symlink encoding is complete for the actual A09 object:

```text
S(path) S(target) U64(device) U64(inode) U32(mode)
U64(links) U64(uid) U64(gid) U64(bytes)
I64(mtime_ns) I64(ctime_ns)
BOOL(pathname_after_read_matched_before)
BOOL(pathname_final_matched_before)
```

This is a design rule only. No implementation has yet demonstrated that its
integer widths, signed conversion, length checks, separators, and field order
produce the intended bytes.

A11 contains the complete row, overlay, and domain field order. A12 only
summarizes those encodings. It does not explicitly inherit the A11 wire
authority or repeat the row tags, separators, optional-field tags, parent
confinement fields, and all domain tags. The implementation must bind the A11
design hash above, carry its complete byte grammar, and apply only the A12
symlink-field correction. It must not invent a second row encoding from the
A12 summary.

The A09 distribution keys are `pillow` and `numpy`. The A09 overlay package
values are `pillow-12.3.0.dist-info` and `numpy-2.3.5.dist-info`. A12's
`RuntimeRow.package` type uses display values `Pillow` and `NumPy`, and its
`DivergenceRow.package` type does not define the mapping. The mapping must be
explicit and injective, or the binary facet can lose package identity. The
safer rule is to encode the exact A09 key and exact overlay package value.

## Canonical JSON and vector gate

A12 gives one exact compact JSON algorithm. It fixes UTF-8 key ordering, array
order, integer formatting, literal spelling, control escapes, and non-ASCII
handling. It rejects duplicate keys, floats, non-finite values, invalid UTF-8,
NUL strings, and surrogate scalars.

The small vector is declared as 34 UTF-8 bytes with SHA
`75a5e1754766234964e2cc913129d7dbdc36e806b6e4346fc2412794490e74ca`:

```json
{"a":1,"b":true,"n":null,"s":"é"}
```

The vector hash is a design input, not an independently captured implementation
result in this review. The complete twelve-authority domain vector still has no
frozen byte count or SHA. A12 correctly retires the old A11 `domain-one` hash.

This is the primary preimplementation gate. Freeze the complete expanded
fixture, generated bytes, byte count, and SHA in a separate artifact. Test
quotation, reverse-solidus, named controls, uppercase `u00XX` escapes,
non-ASCII scalars, duplicate keys, invalid strings, and integer/bool separation.
Require every one-byte mutation to change only the intended facet and the final
domain digest. Do not accept an implementation-generated expected hash.

## Fixed domains and phase counters

A12 validates the A09 counts, row order, overlay order, report keys, state,
historical path hashes, and all fixed limits before any child launch. Its four
phase observations carry one shared domain identity and separate counters.
Excluding the phase label from the identity is correct. Requiring counters to
stay unequal would be incorrect; A09 and parent readback have different valid
read totals.

One accounting boundary remains under-specified. `PhaseCounters` contains only
`opened_inputs`, `read_bytes`, and `path_bytes`. A10 also limits package bytes,
maximum file bytes, row counts, output entries, captured input, report bytes,
and aggregate attempt bytes. Those limits appear elsewhere in A12, but the
design does not state which phase-owned ledger records each one. The
implementation must assign every cap to an owner and retain its observed value.
It must distinguish runtime-scan counters from capture and publication counters.
Otherwise “checked against caps” can become a check of only three counters.

The A09 report's limits are also phase-specific observations. The report records
its limits at report construction, while final attempt enumeration occurs after
serialization. A12 must retain that distinction. It must not silently treat a
post-publication counter as part of the frozen report identity.

## A10 bounded capture and publication

A12 carries the A10 bounds without reduction: 15 seconds, 2 seconds SIGTERM
grace, 1 second final drain, 1 second direct-child reap, 1 MiB stdout,
128 KiB stderr, 256 KiB request, 4 MiB preflight, 1 MiB control/failure,
4 MiB seal, 16 MiB aggregate attempt output, seven attempt entries, 128 MiB
per runtime file, 1 GiB per runtime scan, 65,536 opens, 4,096 rows per package,
8,192 total rows, 4,096 path bytes, 32 MiB total path bytes, 1,548 expected
rows, 45 overlay rows, and 2 MiB diagnostic bytes.

The capture state machine records launch attempted separately from process
started. It bounds selector drains, TERM/KILL cleanup, direct-child reaping,
pipe residue, cancellation, and post-child observation. The publication design
uses one owned descriptor, exclusive creation, flush, fsync, reopen, exact byte
comparison, and directory fsync where supported. It retains bounded partial
bytes, SHA, flush, fsync, and failure code.

These are source-level obligations. No runner implementation or boundary control
has been executed here. The later implementation must prove that exception
paths cannot skip cleanup, release a descriptor before partial capture, or
reopen a replaced pathname while claiming same-file verification.

## A14 child contract

The A14 schema requires exactly these top-level fields: schema 3, state
`executed`, loader `{path, bytes, sha256}`, and the ordered result array. The
loader byte count is an integer. Every result requires `name`, `status`, and
`code`, with only source-defined optional fields.

The A14 output schema lists 59 exact result names and order. A12's child
validator must enforce that table, reject unknown fields, reject reordered or
missing rows, reject non-integer loader bytes, and validate every optional field
type and bound. The A14 control source has not run, so its 59-row contract
cannot be treated as a successful control result.

The A14 package manifest lists nine A14/A11 package files plus six input rows,
the A15 manifest and its 21 source rows, and review authorities. The source
closure should enumerate the package manifest itself and every one of those
nine file rows. It should also enumerate the A15 manifest itself and all 21
manifest rows. “Every A14 source row” must not remain an informal shorthand.
Excluded A11/A12 histories must stay documentary and must not become current
authority through a copied path or stale hash.

## Source closure and authorization

The A12 closure graph is acyclic and well separated:

```text
fixed sources + A09 evidence + A03 receipt
  -> source closure
  -> external authorization
  -> runner preflight and publication seal
  -> parent readback
```

Excluding the authorization and runner outputs from their own source closure
avoids a hash cycle. Creating authorization outside the attempt directory is
also correct. The runner must verify the authorization before scanning or
launching the child. Parent readback must reopen the authorization, seal, every
closure input, and the fourth runtime domain.

The A03 launch receipt currently binds the fixed interpreter, exact child
invocation, A03 reader source, and the A09 report. Its saved identity is the
2,480-byte file listed above. This receipt does not attest loaded code. The
design correctly keeps loaded-image, provider, native, and creative fields
false.

The saved A03 parent execution evidence has state
`parent_current_files_readback_passed_unqualified`. A12's final risk paragraph
still says that A03 readback remains unexecuted. That sentence is stale and
must be corrected before implementation. The correction changes status only;
it does not add loaded-image, native, provider, playback, or creative proof.

One closure risk remains. The A12 design names the A14 package and A15 rows,
but it does not show the final ordered closure record list or its digest. The
implementation must create that list from measured descriptors, reject aliases
and duplicate paths, and rehash every source after publication. A literal list
of hashes in a design cannot replace these checks.

## Findings

### P1 gate: full-domain vector is not frozen

The A12 design explicitly leaves the complete domain vector hash pending. That
is the correct status, but it blocks implementation and any runner acceptance.
Freeze it before writing the canonical digest module. Keep the small JSON vector
as a separate control. Do not claim that the declared hash proves the complete
domain encoding.

### P2: cap ownership needs a complete ledger

The typed phase counters cover only opens, read bytes, and path bytes. Assign
package bytes, row counts, maximum file size, output entries, captured stream
bytes, report bytes, and aggregate attempt bytes to explicit phase or publication
owners. Record each measured value and enforce the same values in parent
readback. Keep logical cap claims separate from RSS and native framework memory.

### P1: A12 must inherit the complete A11 wire

The A11 design is the reviewed source of the full row, overlay, and domain
encoding. A12 repeats the primitive types and corrected symlink fields, but
condenses the other field order into prose. Without an explicit A11 wire hash
and inheritance rule, two implementations can produce different facet bytes
while both appear to follow A12. Bind A11 design SHA
`a4d388ce66f9d47d9d160ac3e8c60399dc61cacf21a34eff43dbd21bc91946f6`, then
freeze the A12 symlink override and complete vector against that grammar.

### P2: package identity mapping is not defined

The typed model's display package literals do not match the actual A09 keys or
overlay package strings. Define the exact mapping before hashing. Add controls
for swapped package keys, swapped row groups, and a changed distribution
version. Retain Pillow-before-NumPy order as a separate order check.

### P2: source closure needs an explicit ordered row set

The closure prose is acyclic and correctly excludes future authorization and
outputs. Before implementation, publish the ordered row set for the nine A14
package files, A15 manifest plus 21 rows, A09 authorities, A03 receipt and
reader, A12 runner/contract, canonical-vector artifact, and capture policy.
Bind every row's path, bytes, descriptor identity, and raw SHA. Keep excluded
predecessor metadata out of current authority.

### P2: child and publication controls remain unexecuted

The A14 59-row schedule, canonical writer, capture transitions, publication
boundary, and parent-readback mutations are specified but untested. Require
source-controlled positive and one-byte-over controls before any child run.
Preserve structured failures and partial-file identities on every failed branch.

## Required disposition

Keep the A09 report, overlay, diagnostic, A03 receipt, and parent readback as
completed unqualified observations. Keep the A14 package as source-only,
unbuilt, unexecuted, and unqualified contract evidence.

Before implementation, freeze the complete domain vector and its measured hash,
publish the ordered closure rows, assign every cap to a ledger owner, and review
the canonical writer, capture backend, publication writer, child validator, and
parent readback independently. No watched, heard, creative, native, provider,
or loaded-image claim is made by this review.
