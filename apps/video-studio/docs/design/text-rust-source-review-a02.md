# Rust native text probe source review A02

## Disposition

The frozen A02 package is **not yet green for lock generation or a proof build**.

Both A01 P1 findings are closed in source. Three P2 defects remain in the exact admission and cancellation contract.

This was a source-only review of all 14 files. I did not format, build, typecheck, execute, or inspect a process.

## P2 — native strings can allocate beyond their reservation

`native.rs:1498-1577` checks the native UTF-16 length, then reserves `maximum_utf8_bytes`.
Both helpers call `to_string()` before checking the resulting byte length, ASCII policy, or `String` capacity.

The reservation is not a valid conversion bound. A 128-unit non-ASCII string can require more than 128 UTF-8 bytes.
The 256-unit operating-system string can also exceed its 768-byte reservation before the later audit rejects it.

This path matters for foreign fallback metadata and framework metadata. Exact selected-font inputs do not bound those returned native strings.

Before conversion, derive a checked worst-case allocation bound or query the exact UTF-8 extent. Reserve that bound before creating the `String`.
Keep the separate policy limits on accepted UTF-8 bytes and ASCII content. Audit the actual `String::capacity()` before releasing conversion scratch.

`source-rationale.md:36` and `allocation-ledger.md:117` currently overstate this behavior. Update both with the implemented bound.

## P2 — cancellation coverage is narrower than the shared protocol

`text-probe-protocol-a01.md:125` requires checks around native calls and during bounded copies.
The A02 source checks many major phase boundaries, draws, snapshots, table payload copies, and RLE writes.

Several bounded operations remain unchecked:

- `read_admitted` performs the complete `read_exact` without a cancellation check.
- `sha256_open_file` and source traversal do not accept `CancelCheck`.
- `producer_identity` and framework observation run without checks inside the operation.
- native line, run, table-tag, string, and framework getter sequences lack before-and-after checks.
- the first RLE counting pass, mask scan, main/guard comparison, clip comparison, and canonical comparisons lack row or chunk checks.

These gaps do not imply an unbounded native call. They do violate the predeclared cancellation boundary.
`source-rationale.md:267` also claims row-visit coverage that the comparison and scan paths do not implement.

Pass `CancelCheck` through the bounded readers, hashers, traversals, comparisons, scans, and native observation helpers.
Check per bounded chunk or row. Check immediately before and after each relevant native call or indivisible native sequence.
Retain the truthful statement that cancellation cannot interrupt a native call already in progress.

## P2 — retained `PathBuf` capacity is not measured

`sfnt.rs:666-674` accounts each retained canonical font path as twice its byte length.
`PathBuf` capacity is not generally bounded by `2 * len`.

The 128 KiB fixture reservation is likely ample for these two frozen paths. Its commit can still release bytes using an understated measurement.
That can make the final retained count and `all_accounted_bytes_within_preallocation` inaccurate.

Use the retained `PathBuf::capacity()` in `measure_font_fixture_owners`. Convert and add it with checked arithmetic.
Keep the existing preallocation bound, unless the corrected measurement requires a larger proved bound.

## Closed A01 P1 findings

### Checked representation authority

`RepresentationLedger` now enforces a nested 4 MiB envelope through retained and temporary reservations.
The source starts reservations before the major parsed trees, source evidence, native arrays, shape trees, raster evidence, and report records.

The 16 MiB `Budget` separately covers font bytes, native-copy payloads, raster owners, ImageIO bounds, hash scratch, events, and report serialization.
Owner field order and explicit drops keep the principal native and Rust backing owners inside their permits.

The new component derivation closes the A01 blanket-permit P1. The two accounting P2 findings above still require repair.

### Running executable authority

`darwin_identity.rs` keeps one opened executable file description through hashing and Mach-O parsing.
It brackets the read with stable descriptor metadata.

The source obtains the loaded main-image region through `proc_pidinfo`. It compares device, inode, file offset, header origin, and `LC_UUID`.
It also compares the opened SHA-256 and UUID with the future frozen build manifest.

This closes the A01 pathname-only P1 for the declared evidence boundary.
The report correctly states that the UUID is not a whole-image hash and that mapped pages are not hashed.

## Other closed A01 findings

- `read_admitted` uses one opened descriptor, a pre-sized boxed slice, EOF checking, and stable before/after metadata.
- Reported input identities come from the exact bytes used by parsers and font construction.
- Completion pathname reads are additional unchanged-input checks.
- File hashing uses one 64 KiB buffer under one retained hash-scratch permit.
- Event JSON uses one fixed 64 KiB writer, and event write errors propagate.
- Fatal `failure.json` uses a bounded streaming writer.
- Completed shaping survives later structure, disposition, raster, and comparison failures.
- Native face failures preserve tag inventory and partial selected-table identities when those observations exist.
- Main, guard, clip, complete clip-reference, and every control mask join the three-repeat gate.
- The 221-byte canonical orientation owner drops before its permit.
- Native contexts drop before their stable Rust backing buffers.
- Font-copy native objects drop before the copied-byte permit.
- The TrueType scalar is labeled as source-bound rather than native header readback.
- Source traversal has file, entry, depth, and relative-path bounds.
- Report serialization streams once under one 4 MiB permit.

The raw-array scratch release at `native.rs:1011` is valid.
The source positions and advances were consumed by `into_iter().collect()`.
The source indices were consumed by the preceding loop.
The destination vectors remain covered by the shape reservation.

## Required next gate

1. Preserve A02 unchanged.
2. Repair the three P2 findings in a successor package.
3. Re-review the successor source, schema, rationale, and allocation ledger.
4. Only then generate and review `Cargo.lock`, build, and typecheck evidence.

A green source successor would authorize only the isolated build and typecheck freeze.
Native execution would still require a separate authorization and evidence review.

No result here establishes CoreText feasibility, product integration, encoded output, playback, hearing, lyrics, film completion, or creative acceptance.
No process peak, allocator overhead, native-framework heap, or power behavior was measured.

## Exact reviewed identities

The package contains 14 files, 9,973 lines, and 337,283 bytes.
`Cargo.lock` and `target/` are absent.

| File | SHA-256 |
| --- | --- |
| `Cargo.toml` | `451f7f01d38ab3d23523f95c22df6fb098836ff8928caa5c306a89b8babe0f32` |
| `allocation-ledger.md` | `10d5bb42594d63311d6a20ddf809fd0d686355267a1adf753240e08e2260c1f0` |
| `output-schema.md` | `79d4a70745473ead38e4cb19526bd5a9cb7c600d882c7c24c77a7deafe74c9a4` |
| `source-rationale.md` | `904734d73f7a6b850eb94df6d6636a9c123d979ecfea976889ec94320536ee01` |
| `src/budget.rs` | `fcf4eb51af795c6d26f3b2716afa391d8fdd3822ef0266a05242fa96bcd338c6` |
| `src/darwin_identity.rs` | `13b40fd772f6a3081181dfb694e7a69667f06e1abacaeb8aeca0ea2731902e48` |
| `src/error.rs` | `5a9f68446c2ad39d4e03e8dd3edc20a5d7af928a209176e7908259e0b6d3beae` |
| `src/main.rs` | `378231e2a005b6a6b8429fdcd6d43d4202dc91382aece7689f5661bdd3232cd1` |
| `src/model.rs` | `09e795f4ff573f3ffe5f3cb89f41566b323eacb7b3749d9f3a9266fe69d4106f` |
| `src/native.rs` | `39a742c74be434f38f897d1e21e4f947f84858f32abd26e573b38253a44484b8` |
| `src/probe.rs` | `b33fcbb50d9ef368b9313142905d1267d56dcb7aed0a248fa46811cc6b5ecdea` |
| `src/representation.rs` | `75c30a313b798fa7d3b98076f9f9b2d796eeda8fca84bf76998637813763f36e` |
| `src/sfnt.rs` | `8b8fbad1b4b3dcdbfefefa303a61cdecb8c4f8814941d7ac7a4fe140f555d5e7` |
| `src/util.rs` | `690e783b5a68eaa713f0d06f9b482b30e97292a3cda82ac4930637701178dec2` |

Reviewed control documents:

| File | SHA-256 |
| --- | --- |
| `text-synthesis-a01.md` | `d497f472b0d5162e61fab482e2f720a89192645b88b1430b1b61577f0330c323` |
| `text-probe-protocol-a01.md` | `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89` |
| `text-admission-contract-a05.md` | `901c9bd06e4d10d9019bf2f7e8b3785f479b144f998b2dc635a330e8a17f0d7a` |
| `text-rust-source-review-a01.md` | `cf55cc3b301668c6e353d20d162007985e527f8f7fdc51b42a160cd130aae01b` |
| `text-rust-parent-source-review-a01.md` | `5e035ca1fdb9bb0cea75c47816efcf505633b83e183204ad2daec38182e16dfe` |
| `text-swift-source-review-a02.md` | `15155b8414111c4715471e91d5391ce07b3bd4ffea464a9d9185c6e70a5d974e` |

This review is within the same model family. No cross-family reviewer was available.

