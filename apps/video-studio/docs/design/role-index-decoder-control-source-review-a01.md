# Independent RoleIndexV2 decoder control A01 source review

## Disposition

This is a static source review of the decoder control package.
The control, decoder, helper, vector, compiler, native, media, and control process did not run.
No vector package, decoded model, control attempt, or result report exists.
This review creates no loader, acceptance, gate, trust, or native authority.

The source review is same-family and nonblind. It checks the control's declared
independence and evidence boundaries. It does not replace a future run with a
complete independently readable logical fixture.

## Frozen source identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `independent-role-index-decoder-a01/control_role_index_v2_a01.py` | 1841 | 71914 | `1e463123be1a4da01a1d1e918c9c9a289d355149a23c49b2f29c772e8892f244` |
| `independent-role-index-decoder-a01/control-contract-a01.md` | 166 | 6021 | `2e815e47cf7c3cf79d66b0265076a33dc9f273f2db708b812f1d94499aa1004e` |
| `independent-role-index-decoder-a01/control-rationale-a01.md` | 70 | 2495 | `3843a0f94abd81dc45d9b2515e9f0e0cc8ac8e3e21266de26657617b057454cb` |
| `independent-role-index-decoder-a01/result-schedule-a01.json` | 84 | 10088 | `1780c869130fe1f2d9b223929bc558bfb7cf5be4ae56582951fd4b18608d135b` |
| `independent-role-index-decoder-a01/decode_role_index_v2_a01.py` | 781 | 23381 | `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b` |
| `native-role-index-v2-a01/fixture-contract.md` | 111 | 3331 | `017cc3efc3b41d511f0d378a4e19b98f25bc61ca35b7e3bf589c1e2ab15ef83a` |
| `native-role-index-v2-a01/source-manifest-a01.json` | 97 | 3088 | `f16c1382e436f6eb81ce3f2f590017bd5ed9ce2876432651c485d04211bd7021` |

The frozen decoder, fixture contract, and source manifest are the exact inputs
named by the control. The vector directory and control-attempt directory are
currently absent.

## Source properties that passed review

The actual decode path is `decode_role_index_v2(vector)` at control source
line 1635. The decoder source defines that function at lines 681–757. It
requires an immutable `bytes` input, checks the 4 MiB bound before parsing,
checks the magic, schema, row count, strict raw role order, every nested tag,
field bound, reference, trailing-byte condition, and complete graph acyclicity.

The decoder uses only `hashlib`, `re`, `stat`, and `dataclasses`. The control
uses standard-library file, JSON, and module-loading facilities. Neither source
imports the Rust encoder, shared encoder tags, or shared model types. The
control contains no subprocess or child-process API. Its scanner is separately
authored and records wire spans without calling decoder helpers.

The frozen schedule contains 74 ordered entries. Static inspection gives 14
baseline results, 59 rejection results, and one `different` alias-mapping result.
Ordinals run from 1 through 74. The control checks the mutation and baseline ID
sets against the schedule before appending result rows.

The positive schedule covers all seven observation tags, all seven scalar tags,
directory option variants, Mach-O present and absent cases, empty and nonempty
lists, the 79-row role set, the reference graph, and 65 derived dependencies.
The negative schedule covers unknown tags, option invariants, zero and over-limit
lengths, malformed roles, missing and wrong-kind references, cycles, truncation,
trailing bytes, the 4 MiB boundary, UTF-8, paths, modes, sizes, Boolean values,
and NUL bytes. The 65-dependency fixture is the intended greater-than-64 case;
the 4097 dependency mutation checks the decoder limit.

The alias-mapping result swaps relation names 1 and 3 on a copied model and
requires a different canonical digest. This is a useful semantic sensitivity
check. It does not mutate decoder input bytes. A decoder mapping error can only
be caught by the model comparison when the expected model is independently
authoritative.

Expected decoder rejections preserve the actual error code, byte offset, mutated
byte count, and mutated SHA-256 in each result row. `ControlFailure` and
`require` provide explicit checks. The input reader uses one no-follow
descriptor, fixed chunk reads, before/after descriptor metadata, and a final
pathname identity check. The report writer uses create-new semantics, fsync,
and byte-for-byte readback.

## Findings

### P1 — measured decoder bytes are not the executed decoder bytes

`read_bound_inputs` reads and hashes `DECODER_PATH` through
`read_stable_regular` at lines 1558–1561. `load_frozen_decoder` verifies those
bytes at line 506, but then creates a file-location specification from
`DECODER_PATH` at lines 508–511 and executes that pathname at line 519.
The `source` argument is never supplied to the loader.

A replacement after the measured descriptor closes can therefore make the
executed module differ from the hashed module. This breaks the control's source
identity claim and blocks any source-bound qualification.

The successor must compile and execute the already measured source bytes in a
fresh module namespace, or retain one descriptor and prove that the executed
bytes are the same descriptor bytes. A second pathname read is insufficient.

### P2 — the scheduled decoded-model result is tautological

The preflight comparison at lines 1637–1641 does compare the actual decoder
model with the frozen `decoded-model-a01.json`, which is useful. However,
`ControlContext.model_bytes` is assigned `actual_model_source` at lines
1661–1667. The scheduled `decoded-model-exact` check at lines 1498–1503 then
compares the actual model with itself.

The successor should retain the frozen `model_source` in the context and use it
for the scheduled result. It should keep the actual canonical model as a
separate value. The report must distinguish the preflight equality from the
scheduled evidence.

### Qualification blocker — the 79-row expected model is not yet independent

The A01 fixture contract explicitly says that it omits several concrete
identity values. The rationale repeats that the controls remain pending a
complete A02 fixture. `assert_baseline_facts` covers selected paths, tags,
scalar values, aliases, list values, and the 65 dependency names, but it does
not author every value returned for all 79 rows.

The future vector and decoded model must come with a complete, independently
readable logical fixture. Expected fields must not be generated from the Rust
implementation, from the decoder's `complete_model`, or from observed output.
Until that fixture exists, the 79-row and 65-dependency results remain planned
coverage, not completed cross-implementation evidence.

### P2 — source closure and control provenance are incomplete

The control hashes `source-manifest-a01.json` and checks that it is nonempty at
lines 1578–1586. It does not parse the manifest, verify its eleven file rows,
or recompute its declared aggregate. The fixed manifest hash binds the current
manifest bytes, but it does not provide semantic source-row evidence.

The future report records the decoder, fixture, schedule, source manifest,
vector manifest, vector, and decoded model observations. It does not record the
control source, control contract, or control rationale identities. A successor
should bind those three files and state whether the eleven Rust source rows
were independently opened and checked.

### P2 — schedule and manifest JSON types are not uniformly strict

`require_int` rejects Boolean values, but `validate_vector_manifest` compares
`schema` and `rowCount` with `==` at lines 799 and 845. `validate_schedule`
compares `schema`, `resultCount`, and `ordinal` with `==` at lines 891–915.
Python Boolean values can equal integer values in these checks. The schedule
loop also calls `result.get` before proving that each result is a dictionary.
Malformed input can therefore produce an unstructured attribute error instead
of `ControlFailure`.

The frozen schedule hash prevents ordinary mutation of this A01 file, but the
control contract claims closed strict inputs. A successor should require exact
integer, string, and expectation types before equality checks and reject all
schema errors through the bounded control-failure path.

### P2 — unexpected control failures have no retained causal report

The expected rejection branch at lines 1704–1728 records decoder code and
offset. Other `ControlFailure` paths, unexpected decoder exceptions, baseline
failures, schedule mismatches, and report-write failures escape
`run_scheduled_results` or `main` without a failure report. The attempt
directory is created only inside `write_report_exclusive` at lines 1782–1800.

The successor should preserve a bounded failure record with completed result
rows, the failing result or control code, and partial-report identity when
serialization or publication fails. A successful report must not be inferred
from an interrupted run.

### P2 — process isolation is declared, not enforced

The source has no encoder import, shared tags, subprocess, or child process.
However, the control does not enforce a fresh `-I -B` interpreter, verify the
interpreter argument vector, or inspect the preloaded module environment. The
`importlib` loader inserts the decoder into `sys.modules` but does not establish
whole-process isolation.

The report's `processesLaunched: false` is a scope declaration, not proof of a
clean process. A future gate must either add an externally bound isolated
launcher and record its identity, or narrow the claim to same-process static
control execution with no child process.

## Required successor boundary

Before any vector or control execution, freeze a complete logical fixture for
all 79 rows and all decoded fields. Bind the actual decoder bytes that execute,
the control package identities, and the complete source closure. Keep the 74
result schedule closed and preserve the current tag, mapping, greater-than-64,
partial, trailing, and 4 MiB boundary expectations. Do not convert the current
source-only package into an acceptance or native-media claim.

