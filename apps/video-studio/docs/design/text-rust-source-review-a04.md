# Rust native text probe source review A04

## Disposition

The final A04 package is **green for a new source freeze, lock review, typecheck, and isolated proof build**.

I found no P1 or P2 source defect. This verdict does not authorize native probe execution.

I reviewed the complete semantic patch, format patch, final contract documents, and final on-disk identities. I did not run Cargo, Rust, the probe, or native frameworks.

## Compiler repair

The A03 compiler error is repaired through the pinned public API.

`attributes` owns a `CFRetained<CFDictionary<CFType, CFType>>`. `CFRetained<T>` dereferences to `T` for the method call.

The pinned `CFDictionary<K, V>::as_opaque` returns a shared opaque dictionary reference. Its implementation erases only the generic view.

`CFAttributedString::new` accepts that exact opaque reference type. The typed retained dictionary remains live through the copying native call.

The dictionary contains Core Foundation keys and values. Therefore, the unsafe call's dictionary-type requirement remains satisfied.

The local source hashes cited by `source-rationale.md` match the inspected `objc2-core-foundation 0.3.2` files.

## Other semantic changes

The two unused `AffineQ16` imports are removed. `LimitedHashWriter::finish` no longer marks its consumed receiver mutable.

The package name, probe name, invocation, and source-hash domain consistently use A04. No stale A03 producer or hash-domain string remains.

The evidence schema, cases, font authority, source text, native policy, limits, and qualification gates remain unchanged from reviewed A03.

## Patch integrity

The semantic patch has SHA-256 `4dd556d0741385449ec4db958ddbb42d62a79549a01ed4561cde8a25ff3aa51e`.

I reverse-applied the format patch to an isolated copy. The reconstructed preformat tree produced every declared semantic hunk exactly, apart from path and timestamp headers.

The format patch has SHA-256 `63390d945f5fcb904ae98f69d92a0e67160f2523b6bdd4da`. It changes nine Rust files and no contract document.

Its reviewed changes are import ordering, line wrapping, block layout, and trailing commas. I found no changed value, call, branch, bound, error code, or ownership order.

The package contains 14 files, 10,608 lines, and 360,927 bytes. `Cargo.lock` and `target/` are absent.

## Required next gate

1. Freeze these exact A04 files and this review.
2. Generate and review a new A04 `Cargo.lock` and dependency closure.
3. Bind the compiler, Cargo, target, SDK, deployment target, features, and build command.
4. Typecheck and build the isolated package.
5. Preserve any further compiler, linker, SDK, or API failure.
6. Create a new source version if any source or contract byte changes.

The repaired call remains compiler-unverified in A04. A successful build would still require a separate native-execution gate.

## Scope boundary

This review establishes source build readiness only.

It does not establish CoreText feasibility, pixel orientation, memory use, product integration, Plan8 behavior, playback, hearing, lyrics, or creative acceptance.

This was a same-model-family review. No cross-family reviewer was available.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `Cargo.toml` | `942e1fbe27912217f6c86fcd2bb3bf4e530c3a4fbc22c590a8db20602dd4ff24` |
| `allocation-ledger.md` | `e2a9e577351b2404fbd02007568c6255a7024a9230fcc802967f76fa30f244f3` |
| `output-schema.md` | `29985f47174df4ee9155d5f394addf2434af224cd47190842767961bcfa54d19` |
| `source-rationale.md` | `6ae2daebcfdb3f1ad961f977090047b67b5f423c7130304164c9a39a3c0c8144` |
| `src/budget.rs` | `2a7858b0b0ba339eda6709bbcce977686b40bab598a4c39d5e6176422874e75f` |
| `src/darwin_identity.rs` | `0de7477421cbb8bc505e837762805e5e358b2a30a2f1d45e7e8e9974f51ee0be` |
| `src/error.rs` | `5a9f68446c2ad39d4e03e8dd3edc20a5d7af928a209176e7908259e0b6d3beae` |
| `src/main.rs` | `3abee97d5f81bd1b2513d28ea2c48e61677063fd6ca398b4a09a6ea4d6a8e641` |
| `src/model.rs` | `0af5ec5e375a4d3ace3498e97f1cf6d01d3921bcdaed52eac2dd731947fb4` |
| `src/native.rs` | `d58b1bcbcc8202f54d9b14a4cf23f972b4f718eca9ae507718ec70e085beb7a2` |
| `src/probe.rs` | `616e68aed58bac4e11e1d472ccbcda8d41ec3678bd360adb1cc9ef637180ca31` |
| `src/representation.rs` | `0b9ae914ea6370723952d90627cd4b557b22c3a5552e76c7109ab7a62acd3b77` |
| `src/sfnt.rs` | `ccbd6b8cb96b1edc4d4023a155d1653643006f4c8421bda9deef577913333d15` |
| `src/util.rs` | `d2247fe1038169ee728294eee6808780f1a8c6e2c4eb3b7c4454d922b00f3629` |
