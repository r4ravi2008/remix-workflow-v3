# Native text preparation next design review A06

## Disposition

I found no P1 because A06 creates no executable authority.

One P2 blocks implementation of the canonical role-index encoder.
A06 does not assign numeric wire tags to four nested enums.
An independent encoder cannot derive the promised exact bytes from the document.

The three A05 findings otherwise have the following disposition:

1. The saved-report adapters now preserve the heterogeneous field shapes and exact cardinalities.
2. The embedded trust manifest now has an external, noncyclic bootstrap boundary.
3. The observer contract now matches the unchanged A06 source when its normal stdout is read as the publication observation itself.

The first repair remains incomplete only at its binary wire boundary.
No helper, gate, control, compiler, producer, observer, comparator, GPU process, or Resolve process ran during this review.

## Reviewed identities

| Artifact | Bytes | Lines | SHA-256 |
| --- | ---: | ---: | --- |
| `native-preparation-next-design-a06.md` | 23,147 | 686 | `260e83d2b5fb8474b3ef04801b5f28f764ee08e4e94ea648352679cedc2b6eb5` |
| `native-preparation-next-design-a05.md` | 37,998 | 1,051 | `336e19dd491ac04843e31cb4b93b189e5cfb982c0312e55cf123fc182a0ad1d0` |
| `native-preparation-parent-review-a05.md` | 3,966 | 63 | `7aa0fc0a50059b74063486497c95dc07459a2023b68543987e9fc8709061f564` |
| `native-preparation-next-design-review-a05.md` | 9,216 | 200 | `55ad0e2f55a67e41346c5d6c82b3093049e5ba7aaf84b07cbc00ea9eb034146c` |
| `swift-build-attempt-a02/report.json` | 108,721 | 2,617 | `214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea` |
| `swift-pure-controls-attempt-a03/report.json` | 194,652 | 4,943 | `43a58d030bc7d4f2d6ddb799871472517e68bece09f70b675bd8e1f0f07c6632` |
| `toolchain-observation-a01/report.json` | 7,698 | 202 | `c22b5cb70e490131c14456f021cfb11a843a67140d26ec93d759fb5ac29c87c8` |
| `verify_orientation_a06.py` | 23,477 | 485 | `a9e71c86b36217cb15ed154768ecfdbb614dd7a97cabd023d60cc77b1dd8c9d7` |

## P2: nested enum wire tags are asserted but not assigned

A06 assigns the seven top-level `observation_kind` tags.
It also assigns the one-byte `Option` tags.

The document does not assign numeric tags for these nested enums:

- `ScalarKindV2`, with seven variants;
- `DirectoryAuthorityModeV2`, with two variants;
- `DirectoryIdentityV2`, with two variants;
- `AliasRelationV2`, with three variants.

The canonical encoding says enum values use tags declared by the schema.
It also says the schema fixes every nested tag.
No declaration maps these variants to bytes.

Rust declaration order is not a wire-format assignment.
Another implementation could choose different valid tags and produce a different aggregate.
Unknown-tag rejection also lacks a complete accepted-tag set.

A narrow successor should preserve every A06 shape and count.
It should add one numeric tag table for each nested enum.
An independent encoder control should reproduce one fixed aggregate containing every nested variant.
Unknown and duplicate tag assignments must fail before aggregate construction.

## Heterogeneous adapter closure

The adapters now model regular files, symlinks, directories, scalars, lists, aliases, and derived booleans separately.
The current report shapes support the declared counts.

### Swift build closure: 76 rows

The saved closure has twelve direct heterogeneous fields.
It also has one `sourceRows` list and twenty-one source entries.
Each source entry produces a file, relative path, and declared role.

The exact count is:

```text
12 + 1 + 21 * 3 = 76
```

The before and after closures remain separate.
Their equality is one derived boolean.

### Swift pure-control inputs: 169 rows

The saved input set expands as declared:

```text
allBinaries                         7
top-level derived booleans          5
held roots                          3
build closure                      76
seven file groups                  35
seven log groups                   22
four held-binary groups            21
                                  ---
                                  169
```

The alias rows do not replace either observed endpoint.
The log adapter also checks each repeated directory identity against its referenced root.

### Rust toolchain observation: 89 rows

The saved report has eleven top-level scalars and seven fixed file objects.
Its nine argument vectors contain exactly twenty-four tokens.
Its three framework records contain five scalars and one `Info.plist` file each.

The exact count is:

```text
11 + 7 + 1 + 9 + 24 + 9 + 9 + 1 + 18 = 89
```

The adapter correctly keeps SDK and framework path text as scalars.
It does not invent historical directory or symlink authority.

The six-field `StableIdentityV2` matches the saved Swift identity shape.
Its separate `size` field also closes the A05 size-authority omission.

## Noncyclic trust-root closure

`open_pinned` accepts no path, digest, review, or disposition from the caller.
The compiled pin binds exact embedded manifest bytes.
The manifest selects entries through a closed subject-key type.

The prohibited edges prevent the manifest, pin source, loader, acceptance record, and reviews from authenticating themselves.
The trust graph ends at separately reviewed loader source and binary hashes.
That bootstrap cannot come from a record opened by the loader.

This closes the A05 caller-selected acceptance flaw at the design boundary.
No manifest, compiled pin, loader review, or accepted value exists today.
A06 therefore creates no present authorization.

## A06 observer contract closure

The bound observer source accepts the command and filenames declared by A06.
Actual-proof mode requires `a06` in both the sidecar and report basenames.
The exact `orientation-report-a06.json` name satisfies that rule.

The child owns exclusive report creation.
The runner owns only stdout, stderr, and the optional cancellation marker.
The design truthfully states that child publication is pathname-based.

The normal-return stdout shape needs one precise reading:

- success prints the three-field publication observation directly;
- a parsed pixel-check failure prints that same three-field object directly and exits one;
- neither branch prints the complete in-memory run report;
- neither branch nests the object under a `report` key;
- the on-disk report carries the `passed` or `failed` state and has no self-observation.

Those three fields are `path`, `bytes`, and `sha256`.
This is the “printed publication observation” named by the A06 contract.
The runner must compare that direct object with its independent on-disk measurement.

`ValidationFailure` and bounded unexpected-error branches use a different stdout shape.
They print `state`, `error`, and `report`.
The nested `report` is either the publication observation or a `written: false` result.

Read this way, the A06 prose matches lines 402 and 468 through 480 of the bound source.
An implementation that prints or expects the complete run report would violate both the design and source.
I found no remaining observer-contract P2.

## Confirmed boundaries

A06 keeps Rust, Swift, observer, and comparator qualification separate.
Comparator authority remains uninhabited.

The saved Swift records establish compiler and pure-control facts only.
The new adapters do not turn those records into native execution evidence.

The current observer remains unaccepted.
A06 creates no gate, trust manifest, permission record, run directory, or acceptance record.

## Required successor before implementation

1. Preserve A05, A06, and their reviews.
2. Assign fixed numeric tags to all four nested enums.
3. Bind one independent canonical-encoding vector that covers every nested variant.
4. Keep the three accepted adapter cardinalities unchanged.
5. Keep the observer's direct normal-return stdout shape unchanged.
6. Review loader and runner source before creating any authorization.

## Review limits

This was a same-model-family, nonblind review.
I authored the A05 peer review but did not author A06.
I received the parent's two source-level observations during this review.

This review is not independent-source-origin or cross-family evidence.
It establishes no native execution, native text feasibility, output correctness, product integration, playback, hearing, lyrics, film quality, or creative acceptance.
