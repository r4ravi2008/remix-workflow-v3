# Native RoleIndexV2 Rust A01 source review

## Verdict

The frozen Rust A01 source needs a successor before vector or control execution.

I found no P1 issue in the fixed 79-row fixture path.
I found three P2 issues in generic protocol ownership, admission, and fixture authority.

The encoder's byte order, numeric widths, field order, and literal tags match A06 and A07.
This is a source review only.
No compiler, encoder, decoder, control, helper, or native process ran.

## Review independence

I authored the independent Python decoder and its A01 control sources.
This review is therefore same-family and nonblind.
It is not independent-source-origin evidence.

The decoder controls froze before I read any Rust implementation source.

| Frozen decoder artifact | SHA-256 |
| --- | --- |
| `decode_role_index_v2_a01.py` | `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b` |
| `control_role_index_v2_a01.py` | `1e463123be1a4da01a1d1e918c9c9a289d355149a23c49b2f29c772e8892f244` |
| `control-contract-a01.md` | `2e815e47cf7c3cf79d66b0265076a33dc9f273f2db708b812f1d94499aa1004e` |
| `control-rationale-a01.md` | `3843a0f94abd81dc45d9b2515e9f0e0cc8ac8e3e21266de26657617b057454cb` |
| `result-schedule-a01.json` | `1780c869130fe1f2d9b223929bc558bfb7cf5be4ae56582951fd4b18608d135b` |

No vector or decoder-control attempt existed at review time.

## Reviewed Rust authority

The reviewed source manifest is:

```text
artifacts/scratch-video-goal-20261005/native-project-a01/
native-text-unit-a01/native-role-index-v2-a01/source-manifest-a01.json
```

Its SHA-256 is
`f16c1382e436f6eb81ce3f2f590017bd5ed9ce2876432651c485d04211bd7021`.

Its declared source aggregate is
`ffb15798029a9d38367307f4d0a0b71cd66bb479c4fb77321d912f7fb2634b86`.

I reread every listed file.
All 11 current file byte counts and SHA-256 values match the source manifest.
The listed files total 67,317 bytes.
I did not execute the aggregate encoder to recompute the aggregate digest.

## Findings

### P2 — The generic validator mixes wire structure with adapter policy

`validate_role_index` is presented as the generic RoleIndexV2 validator.
It accepts a narrower language than A06 and A07 define.

The differences are:

- it rejects zero rows;
- it rejects duplicate ordered-list members;
- it rejects duplicate derived dependencies;
- it requires distinct alias endpoints;
- it evaluates all three alias relations;
- it limits scalar `PathBytes` and `RelativePathBytes` to 4,096 bytes;
- it rejects empty relative-path components.

The generic structural contract permits zero through 4,096 rows.
It bounds every scalar payload at 65,536 bytes.
It forbids only `.` and `..` relative components.

A06 assigns adapter code responsibility for derived and domain-specific facts.
The independent decoder correctly preserves that boundary.

The current restrictions do not harm the fixed fixture.
They prevent the Rust validator from defining the same generic language as the decoder.
They also make future cross-implementation rejection controls ambiguous.

Create two explicit validation layers in A02:

1. `validate_role_index_structure` must implement only A06/A07 wire rules.
2. `validate_fixture_adapter` must implement the fixed fixture's stronger semantic rules.

The generic encoder should call structural validation.
The fixture command should call both layers before encoding.
Future exact report adapters must own their own semantic and derived-fact checks.

Relevant source:

- `src/validate.rs:14-40`
- `src/validate.rs:126-142`
- `src/validate.rs:147-190`
- `src/validate.rs:238-310`
- `src/validate.rs:312-390`
- `source-contract.md:23-47`

### P2 — The 4 MiB check occurs after allocation-heavy validation

`encode_role_index` calls `validate_role_index` before it counts encoded bytes.

Validation allocates a `BTreeMap`, duplicate-detection sets, reference vectors, adjacency vectors, and a queue.
`ObservationV2::references` allocates a fresh vector for each call.
Validation calls that method during reference checks and cycle checks.

Per-row reference counts are capped at 4,096.
The aggregate reference count is not admitted before these allocations.
The model can therefore request many secondary allocations before the 4 MiB encoded limit rejects it.

The fixed 79-row fixture is statically small.
This issue blocks reuse by a future loader or caller-supplied adapter.

A02 should perform a checked, nonallocating encoded-size and aggregate-count pass first.
That pass must reject values above 4 MiB before maps, sets, or adjacency storage.

A02 should then charge every secondary allocation to a stated logical budget.
Reference iteration should use borrowed visitors or slices instead of fresh vectors.

The caller-owned input model remains a separate ownership obligation.
The source must not claim a process RSS or physical-allocation cap.

Relevant source:

- `src/encode.rs:7-27`
- `src/model.rs` method `ObservationV2::references`
- `src/validate.rs:19-39`
- `src/validate.rs:126-142`
- `src/validate.rs:147-235`
- `source-contract.md:49-57`

### P2 — The logical fixture contract cannot support an every-field comparison

`fixture-contract.md` describes the role groups and selected facts.
It omits several values encoded by `src/fixture.rs`.

The omitted values include:

- complete regular-file identities;
- several regular-file paths, lengths, and digests;
- Mach-O CPU type, file type, command count, and command bytes;
- the pathname-only full-stat values;
- the invocation path and complete link identity.

An independent decoder cannot derive those values from the frozen contract.
Reading `src/fixture.rs` to obtain them would destroy fixture independence.

A02 must publish a complete logical fixture contract before encoding.
The contract must list every typed value for all 79 rows.
It must also define the lossless canonical decoded-model shape.

The reviewed encoder may then emit bytes from that contract.
The independent decoder can compare every field without reading Rust source.

Relevant source:

- `fixture-contract.md:27-104`
- `src/fixture.rs:13-210`

## Protocol checks that passed source review

The following source properties match A06 and A07:

- the magic is `native-text-role-index-v2\0`;
- schema and row count are unsigned 32-bit big-endian values;
- roles use unsigned 16-bit big-endian lengths;
- variable byte fields use unsigned 32-bit big-endian lengths;
- stable identities preserve all six fields in declaration order;
- signed 128-bit timestamps use big-endian two's-complement bytes;
- all seven observation tags match A07;
- all seven scalar tags match A07;
- both directory mode and identity tag maps match A07;
- all three alias tags match A07;
- option tags use `0` and `1` with correct payload order;
- the counter rejects output above 4 MiB;
- the writer checks every append against the counted limit;
- the second pass uses the same immutable row slice;
- output creation uses `create_new`;
- partial output retention and missing durability guarantees are disclosed.

The graph algorithm uses reversed dependency edges.
That orientation still detects every directed cycle.

## Control coverage assessment

The Rust A01 source controls cover the fixed positive fixture and 16 negative cases.
They cover tags, ordering, overflow, references, cycles, sizes, directories, scalars, aliases, and duplicates.

They do not establish cross-implementation equality.
They do not produce a complete expected decoded model.
They do not close the three P2 findings above.

The independent Python schedule contains 74 planned outcomes.
It remains unexecuted because no vector or complete fixture authority exists.

## Required A02 controls

A02 should add these source-defined controls before any vector execution:

1. Accept an empty structural index and reject it only in the fixture adapter.
2. Accept duplicate list members structurally and reject them only when an adapter requires uniqueness.
3. Accept duplicate derived dependencies structurally under the same rule.
4. Accept same-role alias endpoints structurally and reject invalid fixture semantics in the adapter.
5. Accept scalar path payloads from 4,097 through 65,536 bytes structurally.
6. Accept empty relative components while still rejecting `.` and `..` components.
7. Reject an over-4-MiB model before allocation-backed graph validation.
8. Charge and report secondary logical allocations for a near-limit valid index.
9. Bind a complete 79-row logical model without reading Rust source.
10. Compare every encoded and decoded field with the independent decoder.

## Source-readiness boundary

The source has not been parsed, formatted, compiled, linked, or executed.
Actual Rust API and compiler readiness remain unverified.

The fixed fixture appears internally coherent by source inspection.
That observation is not a vector, control result, or execution proof.

