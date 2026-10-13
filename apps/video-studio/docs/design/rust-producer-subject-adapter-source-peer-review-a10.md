# Rust producer subject adapter A10 source peer review

## Disposition

**Source-level result: accepted with no P1 or P2 finding.**

A10 closes the preserved A09 control-state failure with one narrow validator
change. The package remains source-only. I did not import, compile, or execute
its source, controls, harness, or predecessor binaries.

This review is same-model-family and nonblind. I reviewed A09 before this
successor and knew the preserved failure classification.

## Bound package

| Item | Observed value |
|---|---:|
| Package | `rust-producer-subject-adapter-a10` |
| Manifest | `source-manifest-a10.json` |
| Manifest bytes | 49,981 |
| Manifest SHA-256 | `f9542ea9eda14c8892dc2cb246ee448fd176a60083fb83d9f5d8b3b1dbaa06fe` |
| Source rows | 14 |
| Source bytes | 255,410 |
| Source aggregate | `9c7baa1763de48c3317436411c78ad0671b4e1561be1060844fa5a822e5b74b0` |
| External rows | 65 |
| External bytes | 13,360,550 |
| External aggregate | `4653961bd303da6e6df22d6945a3fb455bf146625ba1137084e7668ca640c900` |

I independently re-read and rehashed every source and external row. Every byte
count and digest matches. I recomputed both framed aggregates from the declared
ASCII domain, one NUL terminator, row count, total bytes, UTF-8 path order, and
row framing. Both results match the manifest.

The package contains exactly the 14 source rows plus the self-excluding
manifest. No unlisted regular file exists. The A10 attempt directory, both
canonical outputs, and both disposable control roots are absent.

## Closed control-state repair

The saved report and `inputRawBridge.controlIds` contain the same 21 unique IDs
in the same order. The four rejection IDs occupy these exact positions:

| Index | Identifier | State |
|---:|---|---|
| 9 | `negative-visible-only-padded-mask` | `expected-rejection` |
| 10 | `negative-one-byte-padded-mask` | `expected-rejection` |
| 12 | `negative-orientation-visible-only` | `expected-rejection` |
| 13 | `negative-orientation-one-byte` | `expected-rejection` |

For each listed ID, the saved `actualAccepted`, `expectedAccepted`, and nested
`result.accepted` values are false. A10 checks all four values directly. A
different state or any true acceptance value fails with the bounded input
control error.

The remaining 17 IDs retain the A09 state rule. Each must be either
`positive-pass` or `expected-failure`. The final ordered-vector comparison and
the uniqueness check still reject missing, added, reordered, or duplicate IDs.
The bridge supplies only identifier order; the four rejection states remain
source-owned.

## Delta and preserved contract

I compared all A09 and A10 package files. The only new executable behavior is
the closed four-ID branch in `validate_pure_control_report`. The A09 fixture
accessor repair remains unchanged. Other Rust changes are package labels,
comments, or A10 disposable-root names.

The fixed build evidence and four archive paths intentionally remain under
`rust-build-attempt-a09`. They are measured predecessor authorities rather than
an invented A10 build. The future diagnostic outputs use the separate absent
A10 attempt directory.

These properties remain unchanged:

- 28 diagnostic control cases;
- 2,068 ordered role/tag rows;
- schedule SHA-256 `a5ff306ed57b7e4ef44818674efeb03a7950f855d1d30a5e05be1e46f4c05bcf`;
- 20 fixed descriptors, comprising 18 strict JSON documents and two helpers;
- the source, stream, JSON, RoleIndex, and retained-byte limits;
- the exact compiler, target, dependency roots, and four archive receipts;
- `panic=abort` for the library and `panic=abort` plus thin LTO for the harness;
- the fixed fixture, role schema, observation schema, and output limits; and
- the A07 lineage inherited through A09.

All 51 A09 external rows remain unchanged. A10 adds the A09 manifest, the full
preserved A09 failed attempt, its parent readback, and both A09 evidence reviews.
Every added row matches its declared current bytes and hash.

The A09 failure record is internally consistent: library and harness return
codes are zero, controls return code is one, no canonical output was published,
and stderr names the first unadmitted `expected-rejection` ID. A10 records this
as predecessor failure evidence. It does not convert that attempt into success.

## Evidence boundary

This review establishes source consistency and closes the identified A09
state-admission defect. It does not establish A10 compiler success, control
success, candidate equality, producer execution, native behavior, acceptance
authority, or permission to run the producer.
