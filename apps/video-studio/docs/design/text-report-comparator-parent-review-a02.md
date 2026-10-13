# Comparator A02 parent source review

A02 remains unexecuted. It is rejected before gate creation.

The parent read the complete A01 baseline, all 1,382 lines of the A01-to-A02 source delta,
the complete A02 control source, and both A02 contracts. All four frozen identities matched.

## P1: fresh-process alpha evidence compares absolute locations

`_bind_rust_alpha_raw` retains each run's absolute `path` in the returned binding.
The fresh-process comparison at compare_text_reports_a02.py:4245 compares that binding directly.
The required distinct run roots therefore create a location difference even when every byte agrees.

Preserve the exact paths in provenance. Exclude only those paths from the fresh-process comparison.
Keep the remaining raw-byte observations unchanged.

## Control scope

The A02 control file tests independent miniature implementations.
It does not import or call the comparator functions.
Those controls cannot qualify the actual repaired source.
A separate bounded control must exercise the actual comparator validators and raster relationship functions.
Its synthetic inputs must remain clearly separate from native producer evidence.

## Producer compatibility

A02 supports Swift A06 schema 4. A06 remains rejected before compilation.
The final comparator must bind the actual accepted Swift successor's schema and producer name.
Successful later Swift repeats also need their actual mask context and setter records.
Copying repetition-zero native observations into later repetitions cannot close that gap.

## Confirmed improvements

A02 admits complete mask sets and recomputes guard, clipping, and setter-control predicates.
It adds mandatory draw obligations, alpha raw identity checks, bounded dimensions,
retained report-root descriptors, structured failures, and separate ledger reconciliation.
These are source observations. No comparator, control, native producer, or observer was executed.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| compare_text_reports_a02.py | c7e20428de70184fce6afd7bd17b163ca1130c10afb5fafac88acebb82d8c50b |
| output-schema-a02.md | 039c9dec230ace77232b8560a72ab5ace18227c5a27eb832b9a9d5dd6d198b0f |
| source-rationale-a02.md | 13656a357ff0aa229c3b3e56dbe73607e21e0898f75736aaf177b92f94802813 |
| required-evidence-control-a02.py | fa93770c4694b272c2cd456583ba7766a7a5d0cbce1ecc3c195350331f9b3def |
| Complete source delta | e63a16d2d4e8b605f4ed62bc8a035fe2e3d780f67716ae8f9a4de77d8e3cdbcc |
