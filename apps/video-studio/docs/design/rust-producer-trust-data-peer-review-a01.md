# Rust producer trust data A01 peer review

Disposition: `accepted_no_p1_or_p2` within the final trust-data scope.

This is a same-model-family, nonblind review. I independently decoded both expected final vectors and remeasured every file-backed observation. I did not compile code, construct a pin, create an `Accepted` value, authorize execution, or launch a native producer.

## Manifest and evidence records

`trust-manifest-a01.json` has 2,664 bytes and SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707`.

The manifest has exactly three top-level fields. Its entries are exactly these two keys, in this order:

1. `RustProducerSourceV1`
2. `RustProducerRunnerV1`

Each entry has the required six fields. Each entry joins its exact acceptance record, subject receipt, peer review, and parent review. The manifest has no self-reference.

I parsed all five acceptance records with duplicate-key rejection. Each record has the exact twelve-field schema. The class, version, role schema, scope, disposition, limitations, and false execution field match the declared class.

The five subject receipts are:

| Class | Rows | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| Source | 2,077 | 539,734 | `16333c79eb18f41a8c2ed95777866be293ebd1ceec06865584ff14e853705bbf` |
| Build | 18 | 5,408 | `9068e916a9748038093fe7a904a55d26c233fb2eb7dcbb98c4ceb8cd911c767c` |
| Input | 25 | 7,429 | `2fff4571b0905130d4ecbe8db68d4b1428b26c677786882606a6718b8d000e1e` |
| PNG control | 8 | 2,570 | `c2b65f10c11e7169c53209caa505b88c5686db7dc448bce67ba507529e8c2d46` |
| Runner | 63 | 15,579 | `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2` |

The five records and ten reviews resolve to fifteen distinct paths, file identities, and content hashes. Every record-to-review reference matches the current path, byte count, and SHA-256.

## Final Source vector

I decoded `source-final-expected.role-index` with the frozen standalone decoder. The decoder has 23,381 bytes and SHA-256 `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b`.

The final Source vector has:

- 2,080 rows;
- 540,669 bytes;
- SHA-256 `c60e7e88aafff3d63bb7110ccf887974c732104a58d23f755000d31d7f3c902f`.

Every original 2,068-row Source body remains byte-identical. The 2,077-row Source subject adds exactly nine Build, Input, and PNG-control evidence rows. Every Source-subject row remains byte-identical in the final vector.

The final Source vector adds exactly these three top-level rows:

- `rust.acceptance:source`
- `rust.review:source_peer`
- `rust.review:source_parent`

This ordering preserves the intended noncyclic boundary. The Source acceptance record remains outside the subject that it accepts.

## Final Runner vector

The decoded final Runner vector has:

- 66 rows;
- 16,514 bytes;
- SHA-256 `1f98263dd736b5f30d1906fe15b3a91ef8db6032a0e9f5fc1a02c5732536f77b`.

All 63 Runner-subject row bodies remain byte-identical. The final vector adds exactly these three rows:

- `rust.acceptance:runner`
- `rust.review:runner_peer`
- `rust.review:runner_parent`

The standalone decoder accepted both complete reference graphs. Together, the vectors contain 2,041 regular-file rows, 17 ordered lists, 76 scalar rows, and 12 derived booleans. They contain no alias rows and no reference cycle.

## Current-file observations

I reopened every regular file with no-follow semantics. I hashed each retained file descriptor and compared its metadata before and after reading.

All 2,041 regular-role observations match current content length, SHA-256, and six encoded identity fields. They cover 2,017 unique files and 431,367,482 unique bytes. Duplicate paths have identical non-role observations.

The fifteen acceptance and review rows map to the exact fifteen evidence files. Their paths, observation kinds, hashes, sizes, and identities match current files.

The supporting records also match current bytes:

- `data-receipts-a01.json`: 6,769 bytes, SHA-256 `2c984c5696fa244b9cbfa1a3455ad686056c432fd878db0db2adabfa2e80ffcc`;
- `parent-data-readback-a01.json`: 1,026,423 bytes, SHA-256 `2ce86831d9e6655c236bb8f0cace428245588113704dec8699e7815bd9166dd8`;
- parent review: 3,189 bytes, SHA-256 `6ac24e2d7f604eec8b670893c0878317f15e1750d4e1aad7326a0f175b3118fd`.

## Evidence boundary

These files are expected data vectors. They are not values independently reconstructed and accepted by the pinned Rust loader.

A later compiled pin must bind the exact 2,664-byte manifest. The reviewed Rust implementation must independently reproduce both final vectors before constructing an opaque accepted value.

This review establishes no compiled pin, opaque `Accepted` value, execution authorization, native producer result, product integration, or media acceptance. It establishes no `WATCHED`, `HEARD`, or creative acceptance. Disk identity checks do not attest loaded runtime images.

No P1 or P2 remains within this final trust-data scope. No cross-family reviewer was available.
