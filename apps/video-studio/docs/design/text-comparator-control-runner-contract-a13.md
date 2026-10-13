# Comparator control runner A13 additive contract

## Status and boundary

This is an additive source contract for the A12 runner design. It closes the
inherited wire, package-key, cap-ledger, and source-closure gaps.

This contract is preimplementation. It has not launched a runner, comparator,
control, compiler, child, native process, decoder, media process, GPU process,
or Resolve operation. It does not create external authorization.

The A09 and repaired A03 records remain unqualified filesystem evidence. They
do not prove loaded code, package import, native support, provider origin,
playback, listening, or creative acceptance.

## Immutable authorities

| Authority | Bytes | SHA-256 |
| --- | ---: | --- |
| A10 capture/publication design | 27,406 | `08443a784b95a46b7de7602c4f1e2cac94974026d0b5990c446f03cb5bdd30da` |
| A11 complete digest wire | 22,398 | `a4d388ce66f9d47d9d160ac3e8c60399dc61cacf21a34eff43dbd21bc91946f6` |
| A12 runner design | 35,574 | `a5a91fee3e23f8b64c051eb747bf030ea7422acf8329417e89d9df9091df4ab9` |
| A12 independent review | 17,890 | `fa8cddf5f4600571d6a1d76408d232c6ca977bdd68bdc8d10302b188099401c2` |
| A12 A03-binding erratum | 2,528 | `157598afb8bf88e649811f184a259078d57534429a4765b6dce660faf8c0a14a` |
| A09 report | 2,837,530 | `7a43e5606a49bab8d949444707a132b102326cb86d6236e512e0160ac5dd29e8` |
| A09 overlay | 25,945 | `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a` |
| A09 diagnostic | 1,379,634 | `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2` |
| A03 execution output | 870,446 | `931a6359701c8586341763c6e1128e0360c1367fc54f2e7e4d23504bbb147e8b` |
| A03 root post-check | 858,951 | `cb04626dd19ec505cf5f1bb285e9bab35dc8fb8a9069da59fb65196349d30545` |
| A03 launch receipt | 2,480 | `681dd4515dab592477336d21da9f2a75a791669a41ca302890b8d17f7514c6c0` |
| A14 package manifest | 14,110 | `b8e0422d8c2737009978c7fe2a71c6d5a59430ae116afc399b0bf9c69cad7d31` |
| A14 control source | 50,342 | `b43e3ada668f150a52ce7c77c7028fdf91b0447a7f15fc08cb040d0ea98617c1` |
| A14 output schema | 6,508 | `cb638935ad79e212fd5eaf0a560c32ea49a7b015cbe6c8d386fa72c84bcab04a` |
| A15 source manifest | 11,656 | `0314ddef919e873ce271256f7da8de5206c871a9df883c5874ac39baf7d9fa9e` |
| A13 vector recipe | 15,468 | `ae51933516a2651005e379337c46232848683c6d2a3b06a2b1ac3249d8540dad` |
| A13 vector artifact | 11,427 | `4aaa1cd4d83bd0714f509fb48edb08da2ba52f7887527040a7ee829d6dee73e2` |

The A03 repaired execution and root post-check replace the older A09-named
parent execution binding. The A03 acceptance review records the same scope and
the same corrected identities.

## Distribution and overlay keys

The binary wire preserves exact source values. It does not normalize package
names for display.

```text
DistributionKey = "pillow" | "numpy"
OverlayPackage = "pillow-12.3.0.dist-info" | "numpy-2.3.5.dist-info"
```

The A09 row order is Pillow rows, then NumPy rows, in each source report order.
The overlay order is the exact 45-row overlay order. A display label may be
derived outside the digest, but it cannot replace either wire value.

The validator rejects a swapped key, a swapped row group, a changed package
version, or a display-name substitution.

## Inherited wire and A12 override

A13 inherits the complete binary grammar from A11 SHA
`a4d388ce66f9d47d9d160ac3e8c60399dc61cacf21a34eff43dbd21bc91946f6`.
A11 is the authority for separators, U8/U32/U64/I64/BOOL, string and option
encoding, row field order, overlay field order, domain tags, and domain field
order.

A13 applies one A12 correction to `ObservedSymlink`. The encoded order is:

```text
S(path) S(target) U64(device) U64(inode) U32(mode)
U64(links) U64(uid) U64(gid) U64(bytes)
I64(mtime_ns) I64(ctime_ns)
BOOL(pathname_after_read_matched_before)
BOOL(pathname_final_matched_before)
```

No other inherited field may be reordered, omitted, renamed, or retyped. The
row and overlay encoders must use the exact A11 tags and separators. A12's
summary prose cannot define a replacement wire.

## Frozen vector expectations

The standalone A13 recipe uses Python standard-library functions only. It does
not import a target helper or project module. It implements the written A11
grammar and the A12 symlink correction.

The frozen artifact is:

```text
canonical-vectors-a13.json
bytes = 11,427
sha256 = 4aaa1cd4d83bd0714f509fb48edb08da2ba52f7887527040a7ee829d6dee73e2
```

The generated facet expectations are:

| Facet | Bytes | SHA-256 |
| --- | ---: | --- |
| rows-empty | 33 | `1b47012a24817833a73829cecb438cb29787c2452ba19c87ee4bdf9845b0c8b2` |
| rows-one, A13 grammar | 189 | `7b27483354433c3d22bdaeb23a73481d50f15bc10a4537c4455295fcc1d4d70e` |
| overlay-one | 132 | `6a943b3833cde33e4954211700ac5927f85c3635504d81887c222f399e1d63cc` |
| domain-one, A12 fixture | 1,310 | `109fa9ae6a211c734b19ad5c5ee40335fe58e72f929b3a5a40486696b094f527` |

The artifact also retains the A11 declared `rows-one` value, 188 bytes and
SHA `9db3cefd108afa971649fbe505d495a0a0fd708dd6e83328f223842f0243fcb9`.
The explicit A11 field grammar produces 189 bytes and a different SHA. A13
does not silently use the unreproducible declaration as an implementation
expectation. This discrepancy requires parent review before the digest module
is implemented.

The A11 domain hash
`fc10a17e3b32b00cf0aa217d49efe654ebb31579f3d3de5037b87a6af1cd22fd` remains
retired. A13 publishes all domain fixture fields and the corrected symlink
fields.

The canonical JSON expectations are:

| Vector | Bytes | SHA-256 |
| --- | ---: | --- |
| basic | 34 | `75a5e1754766234964e2cc913129d7dbdc36e806b6e4346fc2412794490e74ca` |
| escapes-and-unicode | 79 | `e28bf60301be509c89f976fb14319791a4c32d436fe837b7b7befe9da8a23950` |

The escape vector covers named controls, uppercase `u00XX` controls, quote,
reverse solidus, slash, and direct UTF-8 `é`. Rejection expectations cover
duplicate keys, floats, NaN, infinity, NUL strings, surrogate scalars, and
invalid UTF-8. The artifact stores exact bytes in hexadecimal.

The recipe and artifact are data expectations. They do not implement the
runner writer. The target writer must reproduce every byte, length, and SHA.

## Complete cap-owner ledger

Every limit has one owner and one retained evidence field. A counter from one
owner cannot silently satisfy another owner's limit.

| Owner | Limits | Required evidence |
| --- | --- | --- |
| authority scan | one file 128 MiB; package 512 MiB; scan reads 1 GiB; opens 65,536; rows/package 4,096; total rows 8,192; path 4,096; paths 32 MiB | phase counters, maximum file, package bytes, row count, path bytes, read bytes, opens |
| report/overlay binding | report 32 MiB; diagnostic 2 MiB; overlay 256 KiB; fixed rows 1,548/45 | bounded descriptor read, bytes, identity, SHA, parsed counts |
| request/preflight | request 256 KiB; preflight 4 MiB | encoded bytes, byte count, SHA, flush/fsync/reopen result |
| child capture | deadline 15 s; TERM 2 s; drain 1 s; reap 1 s; stdout 1 MiB; stderr 128 KiB | launch/process distinction, stream prefixes, total bytes, hashes, timeout, signals, pipe residue, cleanup |
| child result | schema 3, 59 ordered rows, loader bytes integer, control/failure 1 MiB | exact top-level keys, result names/order, typed fields, loader identity, bounded report bytes |
| publication | seal 4 MiB; aggregate attempt 16 MiB; seven allowlisted entries | per-file bytes/SHA/identity, partial prefix, flush/fsync, reopen comparison, allowlist, aggregate total |
| parent readback | fourth authority scan and all attempt files | independent file/directory identities, raw hashes, phase counters, seal/auth joins |

The runtime phase identity excludes phase labels and phase counters. Each phase
still retains its own ledger. Parent readback compares identity fields and
checks each phase ledger against the same caps without requiring equal totals.

## Ordered source closure

The external closure manifest is
`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/comparator-source-closure-a13.json`.
It is an ordered list. The manifest itself and external authorization are
excluded from the closure to avoid a hash cycle. An outer acceptance record
binds the manifest's raw identity.
The order is fixed:

1. A10 design, A11 wire design, A12 design, A12 review, and A12 erratum.
2. A09 helper, contract, rationale, report, diagnostic, and overlay.
3. A03 reader source, launch receipt, preflight, execution output, root
   post-check, and scoped acceptance review.
4. A14 package manifest, then its nine `files` rows in manifest order.
5. A14 six `inputRows` in manifest order.
6. A15 source manifest, then its 21 `files` rows in manifest order.
7. A13 recipe, vector artifact, and this contract.

Each closure row stores the exact repository-relative path, stable descriptor
identity, byte count, and raw SHA-256. The closure rejects duplicate paths,
aliases, changed bytes after hashing, missing rows, and a row whose manifest
role differs from its authority role. Excluded A11/A12 historical packages
remain documentary metadata and cannot become current inputs.

The closure does not include any runner output, attempt directory, external
authorization, loaded-image assertion, provider assertion, native result, or
creative result.

## Authorization and publication order

The root creates external authorization only after the ordered closure is
complete. The root reopens every closure row before writing authorization.
Authorization pins the closure SHA, runner source SHA, three A09 facet digests,
mode map, and finite-limit table. It does not enter the closure.

The runner then validates the mode and fresh attempt name, binds all rows,
validates A09, scans preflight and prelaunch, launches the fixed A14 child,
scans post-child, validates schema 3 and 59 rows, publishes bounded outputs,
and writes the seal. Parent readback reopens authorization, seal, outputs,
all source authorities, and the fourth runtime domain.

No caller supplies a runtime path, digest, report, cap, deadline, environment,
or child argument. No result is accepted from a reduced projection or a count-
only parser.

## Required preimplementation controls

Before writer implementation, controls must reproduce the frozen vector bytes
and reject every listed JSON invalid input. They must mutate one row field,
overlay field, symlink field, endpoint field, policy byte, count, flag, package
key, or digest and observe the intended facet change.

Controls must also prove that a phase label alone leaves domain identity stable,
while a counter mutation stays outside identity but fails its owner cap. Full
path controls must exercise A09 schema, overlay order, A14 schema 3 and 59-row
order, exact package keys, bounded publication at the exact limit and one byte
over, cancellation, child failure, pipe residue, and parent output mutation.

These controls remain source-only until separately reviewed and authorized.
