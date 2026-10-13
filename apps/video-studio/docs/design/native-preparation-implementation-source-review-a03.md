# Native preparation implementation A03 — independent source review

## Result

I found no P1 or P2 in the requested A03 repair scope.

A03 remains source-only and uncompiled. The additive test harness also remains
source-only and unexecuted. Root still owns compilation and the five test runs.

This is a same-family, nonblind review. I knew the A02 findings and the requested
A03 repairs. B authored the additive test harness independently.

## Reviewed material

I read both complete A02 source reviews and the A03 parent source review. I read
the full A02-to-A03 repair surfaces and the current production seams they call.
Those surfaces include:

- `src/artifact_observation.rs`
- `src/saved_report_adapters_v1.rs`
- `src/pure_controls.rs`
- `src/observer_stdout.rs`
- `src/acceptance_v2.rs`
- `src/lib.rs`
- all A03 contracts, fixtures, and the source manifest

I also read every byte of the additive `pure-test-harness-a01` package.

The A03 source manifest is 6,535 bytes. Its SHA-256 is
`d1129e1064f1ecb82eea88e8d98706181c32ebbb5ac6a16b191b7d1615c01106`.
All 27 manifest rows match the current files. The rows total 580,479 bytes.

The harness identities are:

| file | bytes | SHA-256 |
| --- | ---: | --- |
| `pure-test-harness-a01.rs` | 5,097 | `5bb6d8072b2fec03bcd059b201a555885dd43b3b02275f31ca1092b4e9a7b84d` |
| `pure-test-harness-contract-a01.md` | 4,081 | `fea5ee7f770d6cc5187abdc0804eac5b88dc0b3968c806d12983179ed0204760` |
| `source-manifest-a01.json` | 1,531 | `beca58998b0983e70246fa42a11786808ef0fc467e3d8c20ad5703046c565f3a` |

Both self-excluding harness manifest rows match. They total 9,178 bytes. The
manifest also binds the exact A03 source-manifest identity.

## A02 findings closed

### Closed role map

The production `role_token` map now contains the exact lowercase `schema`
token. `ROLE_TOKEN_FIELDS` contains `schema` and uses that production mapper.
The toolchain adapter can therefore reach its complete 89-row expansion.

### Exact baseline semantics

The pure adapter requires the separately measured Swift build report. It joins
the fixed build attempt, report name, and requested report hash to that receipt.

The adapter derives the original semantics from these baselines:

- both build-closure phases;
- all six build binary observations;
- all seven build log observations;
- all seven parent file projections;
- the parent build-report projection joined to the measured build receipt.

The seven parent file baselines remain embedded in the measured pure report.
Their derived facts depend on the pure-report authority row. Build-derived facts
depend on the measured build-report authority row.

Coherent mutations of a file pair, closure, log, or binary reach the production
comparison functions. Each mutation must return `derived_boolean_mismatch`.
The controls no longer substitute cardinality or endpoint equality for the
original before-observation semantics.

### Held report directories

On Unix, the reader opens each fixed intermediate directory with `openat`,
`O_NOFOLLOW`, `O_DIRECTORY`, and `O_CLOEXEC`. It retains that descriptor while
opening `report.json` relative to it.

The reader compares the unit root, intermediate directory, report descriptor,
and report pathname before returning bytes. Rust ownership closes every acquired
descriptor on setup failure and normal return.

The non-Unix path cannot establish the same inode identity. The current macOS
target uses the reviewed Unix path.

## Authority rows and encoded counts

The public expansion vectors remain 153, 339, and 89 rows. The encoded
RoleIndex inputs also contain measured report-authority rows:

| report | expansion | authority rows | encoded rows |
| --- | ---: | ---: | ---: |
| Swift build | 153 | 1 | 154 |
| Swift pure controls | 339 | 2 | 341 |
| Rust toolchain | 89 | 1 | 90 |

Derived dependencies name the corresponding authority roles. The adapter sends
the combined rows through the reviewed RoleIndex V2 validator and encoder.

## Additive executable harness

The harness links A03 through one explicit external rlib. It does not copy the
adapter, reader, validator, or encoder.

Its five tests call the production seams directly:

1. The first test asserts all expansion, authority, and encoded row counts.
2. The second test runs the baseline, schema-map, fresh-role, and fresh-path controls.
3. The third test covers all observer branches, including normal pixel failure.
4. The fourth test calls the combined production control entry point.
5. The fifth test requires the exact unavailable-trust errors.

The encoded count assertions read
`encoded.structural_accounting.row_count`. They do not duplicate encoder
arithmetic. The fixed reports are selected through `SavedReportKind` and the
held `SavedReportRoot` reader.

The positive toolchain observer is explicitly report-backed. It is suitable for
adapter controls only. It does not claim a current filesystem observation.

## Acceptance boundary

`Accepted<T>` retains private fields and an `Infallible` member.
`AcceptanceTrustRootV1::open_pinned` returns `PinnedManifestAbsent`.
`AcceptanceV2::qualify` returns `NoPinnedTrustRoot`.

The harness cannot supply a trust manifest or construct `Accepted<T>`. A passing
future run will prove only the fixed parser, adapter, fixture, and RoleIndex
control behavior for the measured inputs.

## Disposition

A03 and the additive harness are source-ready for root's fixed-archive build and
five-test run. This review does not establish compilation, loaded code, process
launch, native-framework behavior, media output, GPU work, Resolve work, or
creative acceptance.
