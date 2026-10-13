# Rust native text probe source review A03

## Disposition

The frozen Rust A03 package is **green for lock generation, formatting, typecheck, and a proof build**.

No P1 or P2 source finding remains from the A02 review. This verdict authorizes only the isolated build gate.

I reviewed all changed source and all three A03 contract documents. I did not format, build, typecheck, execute, or inspect a process.

## Closed A02 findings

### Native string admission and ownership

`bounded_cf_string` reads the native UTF-16 length before Rust string growth. It derives Core Foundation's maximum UTF-8 size for that length.

The helper reserves the rounded growth bound and the 32-byte display buffer. It then creates and audits the Rust `String` under that reservation.

`bounded_ns_string` queries UTF-16 length, UTF-8 length, ASCII extent, and ASCII convertibility before copying. It reserves the accepted policy capacity before `to_owned` creates the Rust string.

The helper-local scratch reservation can drop when each helper returns. Every returned string remains covered by an already-live outer reservation:

- `CaseSourceEvidence` covers source and attributed-string round trips;
- `ShapeEvidence` covers run-font names;
- `RawFontFaceEvidence` covers bound-face names;
- `ProducerIdentity` covers operating-system and framework strings.

The attributed-string round trip remains live through `observe_line`. The case reservation remains live for that complete call.

I inspected the locally cached pinned crate sources. The authored Core Foundation and Foundation methods, constants, and signatures exist in version `0.3.2`.

The Core Foundation `Display` implementation uses the documented 32-byte stack buffer. The source does not claim ownership of Foundation's autoreleased conversion buffer.

### Cancellation coverage

A03 closes the named A02 gaps.

- Admitted reads, file hashes, table hashes, and direct output writes check each bounded chunk.
- Source traversal checks each bounded entry and recursive step.
- Opened and loaded Mach-O parsing checks each bounded load command.
- Native construction, getter, table, drawing, snapshot, and framework sequences have checks before and after.
- Mask scans, padding scans, comparisons, and both RLE passes check each row.
- Output synchronization has checks before and after the indivisible filesystem call.

The remaining boundary is stated correctly. Cancellation cannot interrupt a native call already in progress.

### Retained path capacity

`measure_font_fixture_owners` now adds each retained `PathBuf::capacity()` with checked conversion and addition.

The existing 128 KiB preallocation remains conservative for the two frozen fixture owners. The retained audit no longer substitutes `2 * path length` for capacity.

## Preserved A02 authority

The checked representation ledger remains unchanged. Its source hash is `75c30a313b798fa7d3b98076f9f9b2d796eeda8fca84bf76998637813763f36e`.

The loaded-executable binding remains structurally unchanged. A03 only threads cancellation through its reads and bounded command traversal.

The executable operation still binds one opened vnode, stable metadata, opened SHA-256, opened `LC_UUID`, loaded region device and inode, and loaded `LC_UUID`.

The report still excludes mapped-page hashing, allocator overhead, native framework memory, process peak memory, and file-description execution.

The preserved A02 package rehashes to every identity recorded in `text-rust-source-review-a02.md`.

## Required next gate

1. Preserve A03 source and this review unchanged.
2. Generate and review `Cargo.lock`.
3. Record compiler, Cargo, target, SDK, deployment target, dependency features, and build command.
4. Format, typecheck, and build the isolated package.
5. Preserve any compiler, linker, SDK, or API failure.
6. Create a new reviewed source version if a build fix changes source.

The local crate inspection reduces signature uncertainty. It does not replace compiler, linker, SDK, or runtime evidence.

A successful build would not authorize native execution by itself. Native execution remains a separate gate.

## Scope boundary

This review establishes source build readiness only.

It does not establish CoreText feasibility, pixel orientation, product integration, Plan8 behavior, encoded output, playback, hearing, lyrics, or creative acceptance.

No native framework, allocator, process-memory, GPU, Resolve, or power behavior was measured.

This review is within the same model family. No cross-family reviewer was available.

## Exact reviewed identities

The package contains 14 files, 10,488 lines, and 355,828 bytes. `Cargo.lock` and `target/` are absent.

| File | SHA-256 |
| --- | --- |
| `Cargo.toml` | `b20be0833ecba9fdeec3720ed37be0b4e6b06a10077f539617558beb71bccf61` |
| `allocation-ledger.md` | `c6557215a5fea296fc5f97e0a3198c38afd8aea0d7316da6e3f636509f1136e0` |
| `output-schema.md` | `41c83bebc4db467ba01ef072e44c3fe3c73e2a68b8659b1334b44c6a2cd6aea3` |
| `source-rationale.md` | `fba558fa431efd4892f5b9c2077c532da5ff82763fe8a6c2cb3f2ca53454407f` |
| `src/budget.rs` | `fcf4eb51af795c6d26f3b2716afa391d8fdd3822ef0266a05242fa96bcd338c6` |
| `src/darwin_identity.rs` | `d2af74fed3bd35fff72ccfb83e90da496e8b9d0a8881f173393f99b6d44376c8` |
| `src/error.rs` | `5a9f68446c2ad39d4e03e8dd3edc20a5d7af928a209176e7908259e0b6d3beae` |
| `src/main.rs` | `230721a182c52a320a567e2f57688e59cd1d8a9c9b1aa87da6080474027275bc` |
| `src/model.rs` | `09e795f4ff573f3ffe5f3cb89f41566b323eacb7b3749d9f3a9266fe69d4106f` |
| `src/native.rs` | `31d70015bc17aa30bfbebe05d5bf00f71d378e62def7b2a78c6e73bc889dc92a` |
| `src/probe.rs` | `4a000dd90244a3d751f0f126b0cb04d6ef5040ebcc2b8d2db7c143e97aa16080` |
| `src/representation.rs` | `75c30a313b798fa7d3b98076f9f9b2d796eeda8fca84bf76998637813763f36e` |
| `src/sfnt.rs` | `eb9385ab0f32ea62d1cd729fa375bd999ae8c7222239d9eef46dc3f2cc6f8a73` |
| `src/util.rs` | `07aad274aafbd6d495233e77860c52b7aa78734e8a6e6e54323672b6502dc9a6` |

The complete preserved diffs used during review have these identities:

| File | SHA-256 |
| --- | --- |
| `rust-a03-native-diff.patch` | `767e0e16ab69ba01a9071d4f2714bac9f8afc60c54520f7023f9d7fcde4bc02a` |
| `rust-a03-probe-diff.patch` | `5b97626e02645ab6fc4205921d4369e7623d4b392055c1d620080c547d35fde8` |

The inspected pinned local API sources have these identities:

| Source | SHA-256 |
| --- | --- |
| `objc2-core-foundation-0.3.2/src/generated/CFString.rs` | `47afaf4bdc4d0775bef71100bb858bd378190dcda50505deaa1e8f46c34800b4` |
| `objc2-core-foundation-0.3.2/src/string.rs` | `013a6a8e4d3e1752c4a5ae3bdc84b95cc059d9faa9228397baf5d74de8483cf3` |
| `objc2-foundation-0.3.2/src/generated/NSString.rs` | `69566889177a40450501f5a3b12768e0e34be30c0e99f260b31c848e9e216338` |
| `objc2-foundation-0.3.2/src/string.rs` | `a296817db800fa77c8bacd9775f61f2e87dc957089225a98c366491643dd4dbb` |
