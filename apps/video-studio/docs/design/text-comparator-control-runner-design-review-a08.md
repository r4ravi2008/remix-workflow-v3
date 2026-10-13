# Comparator control runner A08 peer review

## Disposition

I found no P1 because A08 is design-only and creates no execution authority.

Two P2 findings block runner implementation:

1. the design binds the failed A07 runtime snapshot package instead of its A08 successor;
2. the runner reobserves only the saved snapshot report, not the runtime bytes used by the child.

The package cycle repair, A14 schema 3 contract, 59-row schedule, and finite limits are otherwise consistent.
No runner, helper, control, compiler, comparator, native, media, GPU, or Resolve operation ran during this review.

## Reviewed identities

| Artifact | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `text-comparator-control-runner-design-a08.md` | 20,615 | 513 | `dad29517b4a357436714e21e23cdb097ab3a424c5a8ba7fe41c6c83ec9ddeda0` |
| `text-comparator-control-runner-parent-review-a07.md` | 2,049 | 45 | `3e1a62cdf6f8255b63a374291cde422607654c3f40cec2e7879bbe31db2a2d3b` |
| `text-report-comparator-a14/package-manifest-a14.json` | 14,110 | 334 | `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31` |
| `text-report-comparator-a14/actual-comparator-control-a14.py` | 50,342 | 789 | `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` |
| `text-report-comparator-a14/output-schema-a14.md` | 6,508 | 111 | `cb638935ad79e212fd5eaf0a560c32ea49a7b015cbe6c8d386fa72c84bcab04a` |
| `text-report-comparator-a11/required-evidence-control-a11.py` | 10,626 | 216 | `69c8c96d60b7b8842d6e5f55a564ea23e6853d66c8d06b006e9738e203be809c` |
| `freeze_observer_runtime_a07.py` | 39,611 | 1,006 | `eb0cbd3d68de9ff1d41c12170ab127cc5613cc084c73b8d0ee2de54ae65f5b65` |
| `freeze_observer_runtime_a08.py` | 39,611 | 1,006 | `a8b7a2466ad4d46ecbd69e2ad6827142716d00b615fc867bddadfcee671f0d2f` |
| `observer-runtime-snapshot-contract-a08.md` | 11,384 | 312 | `b26b2fdb88ef648fcf4ae1fcc7927dab8b887b9e28bb7ab7d9a60ee628b08a55` |
| `observer-runtime-snapshot-rationale-a08.md` | 4,906 | 86 | `49c3eb26a4dc5266a3150a5da0341b9182d4f441e987c93f78ce71227ea9e1e9` |

## P2: the runtime authority names the failed A07 package

A08 binds these A07 artifacts:

- `freeze_observer_runtime_a07.py`;
- `observer-runtime-snapshot-contract-a07.md`;
- `observer-runtime-snapshot-rationale-a07.md`;
- `observer-runtime-snapshot-attempt-a07/runtime-snapshot-a07.json`.

The preserved A07 attempt is empty.
A07 stopped before report publication because it required `Name: Pillow`.
The current metadata contains exact `Name: pillow`.

The A07 helper also owns one fixed exclusive attempt name.
That empty attempt now prevents an A07 retry at its exact path.
No `runtime-snapshot-a07.json` exists for the proposed source closure.

The frozen A08 successor changes the expected literal to `pillow`.
It also owns the fresh A08 attempt and report names.
Its report schema remains 3, and all other runtime input rules remain unchanged.

A runner successor must bind the accepted A08 helper, contract, rationale, and actual A08 report.
It must not inherit A07 hashes or invent an A07 report identity.
This repair stays within the existing one-report, two-facet architecture.

## P2: report stability does not establish current execution bytes

The runtime facet digests authenticate one past snapshot report.
The external authorization also pins that report and those facet digests.

The execution order reobserves the runtime-report file before and after the child.
It does not reobserve the filesystem objects described by that report.

The report can remain byte-for-byte stable while any of these inputs change:

- the fixed interpreter entry symlink;
- the actual `python3.12` executable;
- the runtime, Python, or site-packages root endpoint;
- any of the 1,548 installed files declared by Pillow and NumPy `RECORD` metadata.

The child launches the current executable and resolves imports from the current roots.
A stable report hash therefore does not prove which runtime bytes the child used.
Parent readback currently repeats the same report-only limitation.

The existing schema already contains every required expected observation.
A narrow repair can use those rows directly:

1. Reobserve the entry symlink, executable, three roots, and all 1,548 installed files before launch.
2. Require each observation to equal the exact corresponding schema-3 report row.
3. Repeat those descriptor-based observations after child cleanup and before publication.
4. Record the complete before/after equality result in preflight, report, seal, and parent readback.
5. Reject an unchanged snapshot report paired with any changed runtime object.

The repair does not need a second runtime report or a new package model.
It must retain bounded reads, `O_NOFOLLOW`, confinement, and the existing file-count domain.

Meaningful source controls should mutate one executable, root endpoint, and installed file while retaining the report.
Each mutation must fail on the applicable before-launch or after-child observation.

## Confirmed A14 wire contract

The A14 manifest has exact SHA-256
`b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31`.
It declares output schema 3 and exactly 59 results.

The A14 source emits these exact top-level fields:

```text
schema
state
loader
results
```

`schema` is integer 3.
`state` is `executed`.
The loader byte count comes from `len(payload)` and is an integer.

The design's 59 names, order, statuses, and codes match `output-schema-a14.md`.
The seven optional result fields also match the source-defined schema.
The design rejects schema 1, schema 2, string byte counts, unknown fields, and count-only matches.

The required-evidence source still emits exactly `obligation` and `relations`.
Its fixed source hash matches the design.

## Confirmed noncyclic authorization shape

The A14 package contains package rows only.
The source closure excludes its own hash and the external authorization.
The external authorization is created last and pins both earlier identities.

The resulting direction is:

```text
package and runtime authorities
  -> source closure
  -> external authorization
  -> runner admission
```

No earlier record contains the external authorization.
I found no remaining hash cycle in this shape.

## Confirmed finite process and output contract

The A08 limits match the reviewed A07 policy:

- 15-second child deadline;
- two-second TERM grace;
- one-second final drain;
- one-second direct-child reap bound;
- 1 MiB stdout and 128 KiB stderr prefixes;
- 256 KiB request;
- 4 MiB preflight;
- 1 MiB control or failure report;
- 4 MiB seal;
- 16 MiB aggregate attempt cap;
- seven attempt entries maximum.

The seven-entry allowlist accounts for the optional failure record.
The capture contract drains both pipes and bounds direct-child cleanup.
It does not claim descendant reaping from group signals.

The external runtime report remains outside the 16 MiB attempt aggregate.
Its own source contract limits it to 32 MiB.

## Required successor

1. Preserve A08 and this review.
2. Replace every A07 runtime source and report binding with the reviewed A08 successor.
3. Add exact live runtime observations before and after the child.
4. Preserve the one-report, two-facet projection.
5. Preserve the noncyclic external authorization shape.
6. Preserve schema 3, all 59 ordered rows, and the finite capture limits.
7. Review runner source and controls before any child execution.

## Review limits

This was a same-model-family, nonblind review.
I did not author the A08 runner design.
I did author the source-only A08 runtime snapshot successor used to identify the stale A07 binding.
The parent supplied the possible live-runtime reobservation finding before this review.

This review is not independent-source-origin or cross-family evidence.
It establishes no runner execution, comparator result, native execution, text feasibility, media result, playback, hearing, film quality, or creative acceptance.
