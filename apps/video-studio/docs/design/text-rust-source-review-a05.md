# Rust native text probe source review A05

## Disposition

The A05 source package is conditionally green for lock generation, typecheck, and an isolated
proof build. I found no new P1 or P2 source defect in the CGDataConsumer delta.

This verdict does not authorize callback, ImageIO, native, or product execution. The new
`CGDataConsumer` feature, callback ABI, and `with_data_consumer` call remain compiler-unverified.

I reviewed the complete 1,225-line semantic patch, 176-line formatter patch, Cargo feature diff,
PNG sink source, direct control, allocation ledger, output contract, and pinned local SDK and
objc2 sources. I did not run Cargo, rustc, rustfmt, the callback control, ImageIO, or any native
framework.

## Scope of the A05 delta

The Cargo change adds only `CGDataConsumer` to the existing pinned
`objc2-core-graphics = 0.3.2` feature list. The native semantic change removes the unbounded
`CFMutableData` PNG destination and adds `PngConsumerState`, two C callbacks, a bounded file sink,
release-state observation, and one pure Rust callback control. Font inputs, source cases, drawing
policy, report schema, limits, cancellation points, and qualification gates remain inherited from
reviewed A04.

The semantic patch hash is
`1dcbfa7ce74a41b8eb124624f16e9a5ae2a9552e148ee4ca6c1488e7042cfdd5`.
The formatter patch hash is
`1132034b6f2f16c341755f78a9cbf8367b9924db36b67bd474f29e61a755179b`.
The formatter patch contains layout changes only in the new A05 source state.

## Callback admission and cap behavior

`snapshot_png` computes `raw_bytes + 1 MiB` with checked arithmetic. It reserves that complete
encoded bound before creating the output file, the callback state, or the ImageIO destination.
`OutputTracker::create_bounded_exclusive` reserves the same on-disk maximum and creates the path
with exclusive creation.

`png_consumer_put_bytes` checks the existing byte count plus the complete requested `count` before
copying. A crossing request records `PNG_CONSUMER_CAP_EXCEEDED` and returns zero. It cannot write
a prefix of an over-bound request. After any callback error, later requests return zero. Writes
handle short writes, retry `EINTR`, reject zero writes, and update the atomic byte count only for
bytes actually written.

The callback has no Rust allocation, formatting, or authored panic path. It uses checked arithmetic,
atomics, pointer offsetting within the supplied buffer, and `libc::write`. The reentrancy flag
rejects nested entry. The callback state is heap-stable in a `Box`, and the raw pointer remains
valid while the consumer exists.

The direct control covers exact-boundary writes, a crossing request before copy, unchanged partial
bytes and SHA-256, zero writes after the first error, cancellation before callback entry, and
Rust-unwind capture. The control is source-only and has not run.

## ImageIO and file ownership

The source keeps the `CGImage`, encoded permit, callback-owner permit, `PngConsumerState`, and
`BoundedOutputFile` live across destination creation, `add_image`, and `finalize`. It explicitly
drops the destination before the consumer. The consumer release callback then marks the state
before the caller reads release, error, and byte counters.

`BoundedOutputFile::finish` checks the opened file descriptor's stable metadata against the
callback byte count, calls `sync_all`, commits actual bytes to `OutputTracker`, hashes through the
same opened descriptor, and checks metadata again. The file owner then closes during drop. A
callback, release, or finalize failure retains the exclusive partial file and reports its path,
byte count, and SHA-256 after bounded finalization succeeds. Failures before that finalization
retain the file through the fatal output path but may have only the causal error and filesystem
artifact available.

Cancellation is checked before and after each indivisible native call, before and after bounded
file synchronization, and during file hashing. A marker cannot interrupt a native call already in
progress. Unwinding after cancellation drops ImageIO objects before the consumer state and keeps
the exclusive partial file for diagnosis.

The ownership order is sound in the reviewed source. The remaining behavior is runtime-dependent:
ImageIO must call the consumer synchronously during finalization, and Core Graphics must invoke the
release callback when the retained consumer drops. The source records both conditions instead of
assuming them.

## Allocation ledger and contract

The A05 ledger adds 131,072 bytes for callback state and bounded file ownership. The documented
PNG peak becomes 12,497,668 bytes, below the 16,777,216-byte logical policy ceiling. The encoded
bound remains an application-owned reservation. The ledger excludes native framework internals,
allocator bookkeeping, physical pages, and process RSS.

The report identifies the destination as
`CGDataConsumerCreate + CGImageDestinationCreateWithDataConsumer/AddImage/Finalize + bounded exclusive fd callback`.
It keeps `external_png_decode_required: true` and `row_hypothesis_qualified: false`, so the
native PNG does not establish orientation or creative acceptance.

The source still uses the existing aggregate output limit and bounded event/report writers. A
bounded-output failure conservatively retains the full reservation until its owner drops. This
can leave a partial file and can make a later failure envelope unavailable when the aggregate
output limit is already exhausted; the source reports that limitation through its existing fatal
path rather than claiming durable failure publication.

## Pinned API identity

The inspected local generated bindings and SDK headers match the authored signatures:

| source | SHA-256 | relevant surface |
| --- | --- | --- |
| `objc2-core-graphics-0.3.2/src/generated/CGDataConsumer.rs` | `0cd3ef90653be037eef30f327881f029a56a2f828f770fdd74150bde3f4b8b7c` | `CGDataConsumerCallbacks`, `CGDataConsumer::new` |
| `objc2-image-io-0.3.2/src/generated/CGImageDestination.rs` | `33394b9a5fd13a38987a0957a5425adc49be3fa41afbcf6f950feed906ca7fa9` | `with_data_consumer`, `add_image` |
| macOS SDK `CoreGraphics/CGDataConsumer.h` | `04cce913c9c9e29d2ae719c4af122dfe438a44d9f3d45300019ae7ef86fad83b` | callback return and release contract |
| macOS SDK `ImageIO/CGImageDestination.h` | `840abd3e2ec6b13f288ac36bf9776b413a0bfbd62b6cf98f741a53ed56dd41ed` | data-consumer destination constructor |

The generated callback ABI is `unsafe extern "C-unwind"`. The source uses the generated field
names and passes `None` for the reserved ImageIO options dictionary.

## Required next gate

1. Preserve the A05 source and this review.
2. Generate and review the A05 `Cargo.lock` and dependency closure.
3. Bind compiler, Cargo, target, SDK, deployment target, features, and build command.
4. Typecheck and build the isolated package.
5. Preserve any objc2, libc, linker, or SDK failure in a new source review.
6. Run the pure callback control before any native ImageIO call.
7. Run native capture only after the callback control and independent PNG decode gates pass.

## Scope boundary

This review establishes source-level build readiness for the bounded sink. It does not establish
Rust compilation, ImageIO behavior, callback release behavior, font feasibility, pixel orientation,
memory peak, Plan8 integration, playback, hearing, or creative acceptance.

This is a same-model-family review. No cross-family reviewer was available.

## Exact reviewed package identities

The package has 14 files, 11,265 lines, and 387,655 bytes. `Cargo.lock` and `target/` are absent.

| file | SHA-256 |
| --- | --- |
| `Cargo.toml` | `902082d267d7bd34aafb3c0eef325e695dad55931069f5ca4f3546769cc19b12` |
| `allocation-ledger.md` | `0f8e52baf4f8aaefc6ddf279de0f0dfacb753428c87cf962550b53980716f3eb` |
| `output-schema.md` | `5979a2a9e76176c24adc45e616d6b055e48369f64d784d77ecdb3d8822fa6cad` |
| `source-rationale.md` | `e064a977b4a48523c8270c4d8224ca8d86ee43672efb9ed5d9f34fb6a32cbf90` |
| `src/budget.rs` | `2a7858b0b0ba339eda6709bbcce977686b40bab598a4c39d5e6176422874e75f` |
| `src/darwin_identity.rs` | `0de7477421cbb8bc505e837762805e5e358b2a30a2f1d45e7e8e9974f51ee0be` |
| `src/error.rs` | `5a9f68446c2ad39d4e03e8dd3edc20a5d7af928a209176e7908259e0b6d3beae` |
| `src/main.rs` | `8d16cc36a1c8ace9b56dc4f69a966f000c1467362d092d29322ce88f4bf7f2c8` |
| `src/model.rs` | `0af5ec5e375a4d3ace3498e97f1cf6d01d3921bcdaed52eac2dd731947fb4` |
| `src/native.rs` | `100f7054a067f9697a6b824507248c67d21edab211ace14d91b6ce9c76c3d8f9` |
| `src/probe.rs` | `616e68aed58bac4e11e1d472ccbcda8d41ec3678bd360adb1cc9ef637180ca31` |
| `src/representation.rs` | `0b9ae914ea6370723952d90627cd4b557b22c3a5552e76c7109ab7a62acd3b77` |
| `src/sfnt.rs` | `ccbd6b8cb96b1edc4d4023a155d1653643006f4c8421bda9deef577913333d15` |
| `src/util.rs` | `2438378dfdacdfcc93423a1455f37adceb7c331bb3477deca11c35d75df83995` |
