# Rust producer subject adapter A09 source peer review

## Disposition

**Source-level result: accepted with no P1 or P2 finding.**

A09 repairs the A08 fixture accessor without changing the diagnostic candidate,
control schedule, compile recipe, or authority model. The package remains
source-only. I did not compile, import, or execute its code or controls.

This review is same-model-family and nonblind. I reviewed A08 and its rejection
before reviewing this successor.

## Bound package

| Item | Observed value |
|---|---:|
| Package | `rust-producer-subject-adapter-a09` |
| Manifest | `source-manifest-a09.json` |
| Manifest bytes | 43,023 |
| Manifest SHA-256 | `4a6f37c4e0c6690ef074ca78716a0feafe9f65f5847924975182bfd6aaf1f7c7` |
| Source rows | 14 |
| Source bytes | 252,609 |
| Source aggregate | `adebe1a9a4a426340112c5f86541d7c076a7a72f4233ce878cdf7234b44cc4cd` |
| External rows | 51 |
| External bytes | 1,485,642 |
| External aggregate | `4d931409faa3881b462c9dd4ae4118fc24e23bdafbb9d41a4b3dfd24d561a141` |

I independently re-read and rehashed every source and external row. All byte
counts and digests match. I recomputed both framed aggregates from UTF-8 path
order, the declared ASCII domains, one NUL terminator, row count, total bytes,
and the declared row framing. Both aggregates match.

The package contains exactly the 14 source rows plus the self-excluding
manifest. No unlisted regular file exists in the package. The declared A09
attempt and disposable control roots are absent.

## A08 repair

`MeasuredDocument.json` remains `Option<StrictJson>`. The repaired
`fixture_controls::document_root` now performs these steps:

1. It obtains the requested `MeasuredDocument` with `get_mut`.
2. It preserves `fixture_mutation_document` for a missing descriptor.
3. It calls `document.json.as_mut()`.
4. It returns `subject_document_not_json` for a present non-JSON helper.

`Option::as_mut` yields the required `Option<&mut StrictJson>`. The final
`ok_or_else` therefore yields the declared `Result<&mut StrictJson>` without
an unchecked unwrap or a fabricated JSON value. This closes the A08 source
type mismatch. Compilation remains a later gate.

The fixture mutation schedule addresses JSON descriptors only. The two helper
descriptors cannot enter a JSON mutation unnoticed because the same accessor
fails with `subject_document_not_json`.

## Semantic-delta check

The two non-JSON helper keys remain exactly `buildManifestHelper` and
`inputRawBridgeHelper`. `measure_fixed_documents` still measures both as
bounded regular bytes and assigns `json: None`. The other 18 descriptors still
use strict JSON parsing and assign `Some(parsed)`.

I compared every A08 and A09 source file. After normalizing the A08/A09 package
labels and renamed filenames, the harness and two unchanged carried contracts
are byte-equivalent. The fixture-controls contract adds an explanatory paragraph
about rejecting a missing optional JSON payload. The only executable changes
are the repaired accessor and the A09 disposable-root labels. The remaining
Rust changes are comments or package labels.

The following frozen properties are unchanged from A08:

- 28 diagnostic control cases;
- 2,068 ordered role/tag rows;
- schedule digest `a5ff306ed57b7e4ef44818674efeb03a7950f855d1d30a5e05be1e46f4c05bcf`;
- 20 fixed descriptors, split into 18 JSON documents and two helpers;
- the exact compiler, target, dependency roots, and four direct archives;
- `panic=abort` for the library and `panic=abort` plus thin LTO for the harness;
- the bounded source, stream, JSON, RoleIndex, and retained-byte limits; and
- the failed A07 control lineage and the A08 rejection record.

All 48 A08 external bindings remain unchanged. A09 adds only the A08 manifest,
the A08 parent review, and the A08 peer review. Their current bytes and hashes
match the A09 manifest.

## Evidence boundary

This review establishes source consistency and closes the A08 accessor defect.
It does not establish compiler success, control success, candidate equality,
producer execution, native-framework behavior, acceptance authority, or
permission to run the producer.
