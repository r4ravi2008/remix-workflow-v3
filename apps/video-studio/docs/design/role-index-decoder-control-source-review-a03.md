# Independent RoleIndexV2 decoder control A03 source review

## Disposition

This is an independent, read-only source review. I did not import or execute
the A03 control, the A01 decoder, the Rust encoder, a helper, a compiler, a
vector process, a native process, or a media process.

I found no new P1 or P2 in the frozen A03 source package. A03 is a narrow
format repair of the reviewed A02 control. It removes the two incorrect
compact-serialization checks while preserving the raw input identities,
semantic projection, decoder checks, 74-result schedule, and bounded
publication path. A future isolated run still requires the reviewed external
launcher and its source, interpreter, process, and filesystem evidence.

This review is same-family and nonblind. It qualifies source suitability only;
it does not qualify a control run, decoder equality, encoder behavior, native
execution, or media output.

## Frozen identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `independent-role-index-decoder-a03/control_role_index_v2_a03.py` | 2364 | 92907 | `0281d006ed97da61738ff41e3355e450c1ffabcdfd12fef3f1687637e79665b1` |
| `independent-role-index-decoder-a03/source-delta-a02-to-a03.patch` | 77 | 3818 | `b2ff169079e1c7272fb48558b7b1cc13b0bd0a8b3df84c2b9d2d1aa100491c4b` |
| `independent-role-index-decoder-a03/format-repair-note-a03.md` | 81 | 3227 | `fdad82fdbde48f1aea53bc5910cfbc78d39624109624e5e96289da4f8969a823` |
| `independent-role-index-decoder-a03/control-package-manifest-a03.json` | 1 | 1403 | `dbb0ad99abdd7d276e5b9c441972dae6443ebb42c75b15826f255edf1af0b161` |

The manifest records the A02 predecessor as 93,013 bytes with SHA-256
`469b5d5cec6dd85551951db2e243ec5fd943402bd9c9ec905002b870e1c2f744`.
The predecessor source, A02 contract, rationale, schedule, A01 decoder, and
all declared input hashes matched their reviewed identities during inspection.

The A03 manifest is schema 1, state
`source_only_frozen_unexecuted`, and declares three package files. Its three
historical authorities are the A02 contract, rationale, and result schedule.
The manifest deliberately excludes itself, as the A02 package did.

## Exact A02-to-A03 delta

The complete frozen source diff has only these semantic changes:

1. A03 reads its control source from the A03 directory and writes only under
   `control-attempt-a03`, with `control-report-a03.json` and
   `publication-failure-a03.json`.
2. A03 reads the unchanged A02 contract, rationale, and schedule through an
   explicit `A02_CONTROL_ROOT`.
3. After strict parsing and the fixed raw SHA check, A03 no longer requires
   the parsed logical fixture to reserialize to its original bytes.
4. After strict parsing and the fixed raw SHA check, A03 requires the encoder
   source manifest to be a JSON object, but no longer requires its parsed value
   to reserialize to its original bytes.

The docstring and path rebinding explain the repair and compatibility boundary.
No validator, mutation, model, schedule, report, or publication logic changed.

## Preserved input and semantic checks

`read_stable_regular` reads each input through one no-follow descriptor, checks
the regular-file cap, reads the exact initial size, checks EOF, compares the
before and after descriptor identity, and confirms the pathname still names the
same object. It retains the raw bytes, byte count, and SHA-256 observation.

`parse_json` still rejects invalid UTF-8, duplicate object keys, and non-finite
JSON constants. The logical fixture keeps exact top-level keys, schema, state,
operation, fixture name, execution flags, and the explicit false semantic-
recomputation flag. Its projection still requires 79 rows, unique sorted ASCII
roles, every observation variant and nested tag, typed scalar encodings, exact
file/link/directory facts, aliases, and 65 ordered `derived.wide`
dependencies. It independently reconstructs the expected model from the
logical fixture and vector identity.

The source manifest keeps its fixed raw SHA-256 and size observation. The vector
manifest still requires its exact schema, state, fixture name, source aggregate,
relative paths, declared sizes, hashes, row count, and denied authority scope.
The later joins still compare the manifest's fixture, logical-fixture, and
source-manifest byte counts with the observed raw files. The manifest itself
must remain canonical JSON. Thus the repair removes representation checks on
the two intentional pretty-JSON inputs without removing raw identity joins or
strict duplicate-key parsing.

The A01 decoder remains bound to its retained bytes and exact SHA-256
`57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b`.
`load_frozen_decoder` compiles those retained bytes with `dont_inherit=True`,
`optimize=0`, and no import loader reread. It checks the decoder magic and
4-MiB cap before the decoded model is used. Actual and expected models remain
separate, with complete field-shape checks and a canonical byte comparison.

## Schedule and rejection coverage

The explicit A02 schedule remains schema 2, state
`planned_independent_role_index_decoder_control_schedule_a02_unexecuted`, and
SHA-256 `dab5e7edb0c8fd3373a83b0287834212aa94baebf132367a8266a56b21eb255a`.
It contains 74 ordered unique results: 14 `pass`, 59 `reject`, and one
`different`, with ordinals 1 through 74. A03 still validates every schedule
object, exact key set, ordinal, unique identifier, category, expectation, and
rejection code.

The baseline map still covers the vector manifest and identity, complete model,
79-row and role checks, all observation and nested tags, directory/file/link,
alias, scalar, list, 65-dependency, and reference-graph facts. The mutation
map still covers the 59 scheduled rejection IDs and their exact decoder error
codes, including duplicate roles, malformed references, cycles, truncation,
trailing bytes, invalid UTF-8, path and mode rules, scalar boundaries, and the
over-4-MiB index. The alias mapping result still compares separately retained
normal and swapped model bytes.

## Report and attempt boundary

The A03 source requires an absent
`independent-role-index-decoder-a03/control-attempt-a03` directory and creates
it before bound-input reads. No A03 attempt directory, report, or publication
failure file exists in the frozen package. The preserved A02 report is the
expected 4,007-byte, SHA-256
`689ebc74cfb9bbd7b31729e08453637497de73b3c8f55c236b0401e67b39d480`
`logical_fixture_canonical` failure with zero completed results.

A03 intentionally retains report schema 2 and the A02 state names. The repair
note identifies those names as historical wire compatibility, while the A03
filesystem paths identify the fresh attempt and report. Success and failure
reports still include the bounded result state, input observations, scope
denials, and A02 schedule hash. Primary publication still uses exclusive create,
chunked writes, `fsync`, no-follow readback, exact byte comparison, and a
bounded emergency publication record. Storage failure can still prevent both
records; no filesystem transaction is claimed.

The A03 package and source remain source-only. The control still cannot bind its
own executed image, interpreter, environment, process isolation, or loaded
standard library. Those facts remain the responsibility of a separately
reviewed launcher.

## Findings and limits

No P1 or P2 remains in the A03 delta. The historical A02 module name used when
loading the decoder and the A02 report state strings are deliberate compatibility
details, documented by the repair note, rather than evidence of a stale output
path. The package does not self-authorize its own manifest; external closure is
still required before execution.

No control, decoder, compiler, vector, native, media, GPU, Resolve, playback,
or creative acceptance claim is made by this review.
