# Independent RoleIndexV2 decoder control A02 source review

## Disposition

This is a read-only source review. I did not import or execute the control,
decoder, Rust source, helper, compiler, vector, native, media, or control
process. The A02 attempt directory and vector package are absent.

I found no P1 or P2 in the frozen A02 control source or its source-only
package. A02 closes the actionable findings in the A01 control review. It is
ready for a separately reviewed isolated launcher and one bounded control run.
That run remains unperformed and cannot create loader, gate, trust, acceptance,
native, or media authority by itself.

This review is same-family and nonblind. It checks the stated independence,
ordering, source bindings, schedule, error publication, and scope boundary.

## Reviewed identities

| File | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `independent-role-index-decoder-a02/control_role_index_v2_a02.py` | 2368 | 93013 | `469b5d5cec6dd85551951db2e243ec5fd943402bd9c9ec905002b870e1c2f744` |
| `independent-role-index-decoder-a02/control-package-manifest-a02.json` | 1 | 1672 | `02546c2c341c13c28b8532827595bf084146f108ffc7f13c726cebe0fcd73a10` |
| `independent-role-index-decoder-a02/control-contract-a02.md` | 158 | 6727 | `3c18bc4766fb82791f11dfdf59da24949c92c34f266d3c2c4107193bfcc8f7d3` |
| `independent-role-index-decoder-a02/control-rationale-a02.md` | 93 | 3761 | `961883dfe3f3c57f7cd539b7a8742c3a07dfc43ce23dc4bb1a588b32ab1ee0e5` |
| `independent-role-index-decoder-a02/result-schedule-a02.json` | 85 | 10186 | `dab5e7edb0c8fd3373a83b0287834212aa94baebf132367a8266a56b21eb255a` |
| `independent-role-index-decoder-a01/decode_role_index_v2_a01.py` | 781 | 23381 | `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b` |
| `independent-role-index-decoder-a01/wire-contract-a01.md` | 268 | 7192 | `679df5d0e6dcd3997c7b4a582ca8b6fa7a4ca9504baf217d8e5f98c182650b31` |
| `independent-role-index-decoder-a01/source-rationale-a01.md` | 111 | 4131 | `091c8528a88d6d1728aa04b16a6d695fb4cf31781de33eee09ae8b11ac2cbf28` |
| `native-role-index-v2-a02/logical-fixture-a02.json` | 720 | 17565 | `fb45c24ecee8a80a3787c7f9a211c0758d058b64949c89bbd535023ce507efaf` |
| `native-role-index-v2-a02/fixture-contract.md` | 60 | 2204 | `16fc743d42797e833213dc2cc00dfa6fb3af9d8295f5c8963e86a41035eafb4b` |
| `native-role-index-v2-a02/source-manifest-a02.json` | 155 | 5369 | `ebe268388896fb97ac46277aea71c43d1dfdb13af22ed10cbdc8c9f8c8241c98` |

The A01 control review used for the comparison is
`apps/video-studio/docs/design/role-index-decoder-control-source-review-a01.md`,
SHA-256 `3ac62f4e38c96efaa563829ab3144a9c566ddd9cdf1a842cc65dbf7dc8556f99`.

The A02 package manifest declares eight source-package files. The encoder
source manifest declares thirteen Rust-package files totaling 181,791 bytes
and aggregate SHA-256
`1ddbbaf55adb2e183363d3b88062697c66c533e735be03e905674d525e18215a`.
The control binds that manifest and aggregate claim but intentionally does not
open Rust source rows.

## A01 findings closed by A02

### Measured decoder bytes are the executed decoder bytes

`read_bound_inputs` reads the decoder once through `read_stable_regular`,
checks the exact A01 decoder SHA, and passes those retained bytes to
`load_frozen_decoder`. The loader hashes the received bytes again, calls
`compile` with `dont_inherit=True` and `optimize=0`, and executes that code
object in a fresh `ModuleType` namespace. It does not ask an import loader to
reread the decoder pathname. The module is removed from `sys.modules` if its
execution raises.

The loader also checks the frozen decoder's size cap and magic after execution.
The module name is rejected if it is already present. This closes the A01 P1
where measured bytes and pathname-loaded bytes could differ.

### The expected model is retained separately

`project_logical_fixture` creates `expected_model` and its canonical bytes
from the frozen logical fixture plus only the vector envelope byte count and
SHA. `complete_model` creates a separate `actual_model` from the decoder.
`decoded-model-exact` compares `actual_model_bytes` with
`expected_model_bytes`; it does not compare the actual model with itself.
The expected and actual model hashes remain separate in the success report.

The logical fixture is read and SHA-bound before projection. Its canonical
UTF-8 bytes are checked. The projection validates all 79 descriptive rows,
all nested fields, all seven observation and scalar variants, directory
identity variants, aliases, lists, exact scalar bytes, and the ordered
65-dependency row. It never reads Rust source or decoder output to construct
expected fields. No Rust source row is opened before or after this projection;
the source-manifest JSON is only a fixed descriptive input.

### Complete expected coverage replaces the A01 partial fixture

The A02 fixture contract and logical fixture state all fields for all 79 rows.
The projection validates exact row keys and values, sorted unique roles,
strict scalar representations, identity fields, options, alias endpoints,
list members, and dependency order. The model-shape checks preserve every
decoded field in the canonical actual model.

This closes the A01 qualification blocker for a complete independent expected
model. It does not claim that a vector exists or that the future Rust encoder
agrees with the fixture.

### Source and control provenance is explicit

The control reads and SHA-binds its contract, rationale, schedule, A01
decoder, fixture contract, logical fixture, and source-manifest JSON. It reads
the control source through the same stable no-follow descriptor and records its
observation in the report. The package manifest independently binds the A02
control source, A02 documents, schedule, A01 decoder, and descriptive inputs.

The control does not self-authorize its package manifest or claim that its own
control-source hash is internally authoritative. `scope_model` explicitly
sets `controlSourceIdentityBoundInternally` and all authority fields to false.
The contract correctly requires a later launcher to bind the package/control
closure. This is an execution prerequisite, not an unacknowledged source
claim. The launcher must verify the package manifest and all fixed file rows
before invoking the control.

### Strict JSON validation is present

`parse_json` rejects invalid UTF-8, duplicate keys, and non-finite constants.
The validators require exact object key sets, exact Python integer types,
strict Boolean types, exact lowercase SHA-256 strings, fixed paths, and
closed schedule expectations. The schedule loop proves each result is an
object before calling `.get`. Canonical JSON is required for the logical
fixture, source manifest, and vector manifest. A malformed schedule or
manifest enters the bounded failure path rather than an unstructured result.

### Causal failure and publication state is retained

The control creates its fresh attempt directory before bound-input reads. The
scheduled loop stores completed result rows and the active result identity.
Unexpected decoder exceptions, baseline failures, schedule mismatches, and
input failures become bounded failure reports with stage, code, detail, active
result, completed results, and observed inputs. Error detail is capped at
1024 characters.

Primary report publication uses exclusive create, bounded chunked writes,
`fsync`, no-follow readback, and exact byte comparison. If primary publication
fails, the emergency record retains intended report bytes and SHA, the readable
partial primary observation, and the publication failure. A storage failure
can still prevent both records. The source does not infer success from a
missing report and does not claim transactional filesystem durability.

## Closed 74-result schedule

The schedule is SHA-bound and validated as schema 2 with 74 ordered unique
ordinals. Static inspection confirms 14 `pass`, 59 `reject`, and one
`different` result. `run_scheduled_results` requires the exact mutation ID set
for all 59 rejection rows, the exact baseline ID set for all 14 pass rows, and
the sole mapping result `one-sided-alias-tag-swap`.

The baseline results cover vector identity, all 79 rows and roles, all seven
observation tags, all seven scalar tags, both directory modes and identity
variants, all alias relations, Mach-O present and absent cases, empty and
nonempty lists, exact file/link/directory/scalar facts, the ordered 65
dependencies, and reference acyclicity.

The rejection rows cover unknown tags and options, option presence rules,
length and count limits, role grammar and ordering, invalid and missing
references, wrong symlink target kind, cycles, truncation, trailing bytes,
the over-4-MiB boundary, invalid UTF-8 and NULs, absolute and relative path
rules, modes, sizes, and Boolean payloads. Each rejection requires the fixed
scheduled error code and records the actual decoder offset, mutated byte count,
and mutated SHA. The mapping result changes only copied comparison-side alias
names and requires a different canonical model digest.

## Interpreter and process boundary

The A02 control imports no subprocess or child-process API and contains no
process spawning path. Its report states `sameProcessControl: true`,
`childProcessesLaunchedBySource: false`, and
`processIsolationEnforcedHere: false`. The contract requires a future external
launcher with a fixed interpreter, `-I -B`, closed environment, and its own
source/runtime closure. The source itself does not and cannot prove the
launcher argv, Python version, preloaded modules, or process-group isolation.

Those facts remain required external evidence. They are intentionally excluded
from this source-only control's authority scope. No execution result exists to
qualify them.

## Review limits

No vector, vector manifest, encoder command, Rust source execution, decoder
execution, compiler, isolated launcher, control attempt, report, filesystem
observer, native framework, media, GPU, Resolve, playback, or creative review
ran. The A02 source is therefore suitable for a reviewed isolated run, but this
review does not qualify encoder/decoder equality or any product behavior.

The 4-MiB input, 1-MiB source, 4-MiB JSON, and 1024-character failure-detail
limits bound the retained values declared by the control. They do not prove
Python allocator, process-RSS, or whole-process physical memory bounds.
