# Native text preparation A07 peer review

## Disposition

I found no P1 or P2 in the A07 design. A07 closes both A06 design findings
without changing the bound observer source, adapter cardinalities, trust-root
boundary, or execution stage boundaries.

The canonical role-index loader remains unaccepted. A canonical byte vector and
independent encoder/decoder control are still required before any loader or
native qualification can exist.

No helper, compiler, observer, control, producer, comparator, native, GPU, or
Resolve process ran during this review.

## Reviewed identities

| Artifact | SHA-256 | Size |
| --- | --- | ---: |
| `native-preparation-next-design-a07.md` | `d5fce8f6f0b4111de6ed4b3c28ba9701dcacf12af80474a55bf86b62b0fb3b46` | 313 lines, 10,181 bytes |
| `native-preparation-next-design-a06.md` | `260e83d2b5fb8474b3ef04801b5f28f764ee08e4e94ea648352679cedc2b6eb5` | 686 lines, 23,147 bytes |
| `native-preparation-parent-review-a06.md` | `40f4cc5163fa17b62555fb0f139454218eed8b07a5af0cc5e9014a380e6e808b` | 48 lines, 2,290 bytes |
| `native-preparation-next-design-review-a06.md` | `e59a580fd030bbb3f5b40a51a70051df183532ecedc39aa5a2b9886b2b60cbbd` | 186 lines, 8,405 bytes |
| `verify_orientation_a06.py` | `a9e71c86b36217cb15ed154768ecfdbb614dd7a97cabd023d60cc77b1dd8c9d7` | 485 lines, 23,477 bytes |

## Canonical wire tags

A07 assigns literal nonzero tags to all four nested enums that A06 left
undefined:

- `ScalarKindV2`: `Boolean=1`, `Unsigned64=2`, `Signed64=3`, `Utf8=4`,
  `PathBytes=5`, `RelativePathBytes=6`, `Sha256=7`;
- `DirectoryAuthorityModeV2`: `PathnameOnly=1`,
  `HeldDescriptorAndPathname=2`;
- `DirectoryIdentityV2`: `Endpoint=1`, `FullStat=2`;
- `AliasRelationV2`: `DescriptorMatchesPathname=1`,
  `LocatedUnderDirectory=2`, `SameObservedObject=3`.

The mappings agree with the A06 declaration order and its existing V2
serialization rules. A07 also preserves `Option={0,1}`, fixed-width scalar
payload lengths, big-endian integers, valid UTF-8/path constraints, and the
unknown-tag rejection boundary. `FullStat` uses the six fields of the A06
`StableIdentityV2`, including size and both nanosecond timestamps.

The complete accepted tag sets are explicit. The design does not rely on Rust
declaration order as a wire assignment. Its negative matrix covers zero,
first-out-of-range, and one-sided mapping swaps.

The vector is still planned rather than measured. A07 correctly refuses to
create an accepted loader until an independent encoder and decoder produce the
same complete bytes, byte count, and SHA-256.

## Observer stdout compatibility

The unchanged source has two terminal stdout shapes, and A07 describes both.

For a normal return, `verify_orientation_a06.py` writes the report file first,
then `main` prints `result["report"]`. The printed object has exactly
`path`, `bytes`, and `sha256`. It is not the full report and is not nested
under `report`. The source's on-disk report is serialized before the returned
publication binding is added, so it has no top-level `report` member.

For a caught `ValidationFailure` or bounded unexpected exception, the source
prints exactly `state`, `error`, and `report`. The nested publication result
has one of the three source-defined shapes: a written three-field binding, a
four-field `written: false` safe-path failure, or the five-field unsafe actual-
proof rejection. A missing or incomplete terminal publication remains a
contract or publication failure.

A07 also preserves the source's child-owned exclusive report path,
`orientation-report-a06.json` name, one-megabyte report cap, status pairing,
and distinction between a parsed pixel failure and observer acceptance.
Only the passed normal state can move to later technical review.

## Unchanged boundaries

The A06 heterogeneous observation model remains closed over regular files,
invocation symlinks, directory authorities, scalars, ordered lists, aliases,
and derived booleans. The 76, 169, and 89 adapter cardinalities remain fixed.
The compiled trust pin still has a separate noncyclic bootstrap boundary.
Caller-selected paths, dispositions, role lists, and pending values cannot
construct authority.

The A06 stage split remains Rust first, Swift separately, observer separately,
and comparator authority uninhabited. A07 changes no source, helper, gate,
trust record, permission record, authorization, run directory, product file,
media, or saved evidence.

## Review limits

This is a same-model-family, nonblind source/design review. The review checked
the frozen A06 observer source and design contracts by file inspection. It did
not execute the observer, imports, compiler, native framework, producer,
comparator, GPU, Resolve, media, playback, or creative review.

The A06 observer source is an orientation verifier with runtime imports and
artifact checks. Its source does not establish producer source lifetime,
native text support, loaded-image identity, or product acceptance.
