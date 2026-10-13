# Native preparation implementation A04 — independent source review

## Result

I found no P1 or P2 in the narrow A03-to-A04 repair.

A04 remains source-only and uncompiled. The A02 harness also remains unbuilt
and unexecuted. Root still owns the fixed-archive compile and five-test run.

This is a same-family, nonblind review. I reviewed A03 before its actual failed
compile. B authored this minimal A04 successor and the A02 harness binding.

## Frozen identities

The A04 source manifest is 2,494 bytes with SHA-256
`25e65b31679d6bb05d02249bed14595971367449f0b7a795480803abb41b9b5d`.
All four manifest rows match. They total 78,901 bytes.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `src/lib.rs` | 2,530 | `5f8f9da85ede019fdff461d759741bdf1eac368b8e0abe23bad98b88ea33043b` |
| `src/artifact_observation.rs` | 13,455 | `70598415d8a5ab866bbe406f65ccb87aeefea8e38df8f0ff0ccfd47020d793e6` |
| `src/saved_report_adapters_v1.rs` | 59,120 | `5b84c16e5d67db049d40954c4e09a23a889563e75e0a4cd5d4d45510283fde9e` |
| `implementation-contract-a04.md` | 3,796 | `1c0063ce2ecaa47de2df5b11d18486a1925fa173406defe56aecc1954fe68b3b` |

The A02 harness source remains 5,097 bytes. Its SHA-256 is
`87e461193a3799562bc2f235fcfdfba155abfdbc92de5e0e4d044f3466c02b3d`.

## Preserved failed attempt

The A03 compile failed before harness construction or test execution. Its six
compiler diagnostics are preserved in:

- `library-build.stderr.bin`, 4,954 bytes, SHA-256
  `c68d3ee95bdf07bed9228fe7d0412d6182b22a9da534c48e9a48b1ff78b0fcba`;
- `report.json`, 3,986 bytes, SHA-256
  `af2b502e36710e5aa7206df93a49b5bcbbdcc8c41d84c754926066ff9ecf8261`.

The A04 manifest binds both preserved files and records all six diagnostics.

## MetadataExt repair

`artifact_observation.rs` differs from A03 in four method names only:

- `st_dev()` becomes `dev()`;
- `st_ino()` becomes `ino()`;
- `st_mode()` becomes `mode()`;
- `st_size()` becomes `size()`.

Those methods belong to the imported `std::os::unix::fs::MetadataExt` trait.
The existing nanosecond timestamp calculation remains unchanged.

This repair addresses the four observed E0599 diagnostics. It does not alter
descriptor ownership, no-follow opens, stable-identity fields, report caps, or
the held intermediate-directory checks.

## AdaptedReport repair

`saved_report_adapters_v1.rs` removes only `#[derive(Clone, Debug)]` from
`AdaptedReport`. No reviewed caller clones or debug-formats that type.

This repair addresses the two observed E0277 diagnostics without changing
`EncodedRoleIndex` or the frozen RoleIndex implementation.

All adapter fields, report-authority dependencies, expansion counts, encoded
counts, schema-map controls, baseline joins, and fresh role/path joins remain
byte-preserved from A03.

## Crate assembly

The small A04 crate root selects the two corrected local modules. It selects
the following reviewed A03 modules by their fixed absolute paths:

- `error`;
- `strict_json`;
- `acceptance_v2`;
- `observer_stdout`;
- `pure_controls`.

It also selects the unchanged RoleIndex V2 A02 model, validator, and encoder.
Their manifest remains SHA-256
`ebe268388896fb97ac46277aea71c43d1dfdb13af22ed10cbdc8c9f8c8241c98`.

The A03 predecessor manifest remains SHA-256
`d1129e1064f1ecb82eea88e8d98706181c32ebbb5ac6a16b191b7d1615c01106`.
No predecessor or RoleIndex file changed.

## Harness binding

The A02 harness changes one executable line. It links
`native_preparation_implementation_a04` under the existing local alias `a03`.
The alias deliberately preserves the reviewed A01 test body.

All five tests remain byte-preserved. They still cover:

- expansion counts 153, 339, and 89;
- encoded counts 154, 341, and 90;
- baseline and fresh role/path rejection controls;
- all observer branches, including normal pixel failure;
- the combined production control entry point; and
- unavailable pinned acceptance.

## Disposition

A04 and the A02 harness are source-ready for root's direct fixed-archive compile
and test attempt. This review does not establish successful compilation, test
execution, loaded code, process launch, native-framework behavior, media output,
GPU work, Resolve work, or creative acceptance.
