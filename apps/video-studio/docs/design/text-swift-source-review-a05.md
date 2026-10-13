# Swift native text probe source review A05

## Disposition

The A05 Swift package is **not green for build, typecheck, or native execution**.

I found two P1 blockers and three P2 evidence defects. The package remains source-only, unbuilt, and unexecuted.

Preserve A05 unchanged. Repair a separate successor, then repeat the complete source, control, schema, and rationale review.

## P1 — consumer aliases can outlive the backing storage

`finalizeNativePNG` passes an unretained `CappedPNGConsumer` pointer to CoreGraphics at `probe.swift:2307`.

The defer sets `destination` and `consumer` to `nil` at lines 2284–2285. It then deallocates both buffers at lines 2286–2294.

Strong `createdConsumer` and `createdDestination` aliases remain in the surrounding function scope at lines 2308 and 2313.
The nil assignments therefore do not prove that either native object was destroyed before the buffers.

The release callback is a no-op at lines 2247–2250. It neither owns the state nor records that CoreGraphics released it.

Cleanup is also installed after both reservations and allocations. A failure before line 2280 leaves earlier ledger ownership without its paired release.

This violates the required destruction order. It also contradicts both documents' claim that destination and consumer release precedes backing release.

Create one enforceable native-owner scope. Destroy every destination and consumer reference before freeing the state or buffers.

Tie the info pointer lifetime to the consumer. Record and require the release callback before inspecting or freeing callback-owned state.

Keep the source raster and `CGImage` snapshot alive through destination finalization and destruction. Their current outer scopes otherwise have the correct direction.

## P1 — the direct control tests a different sink

The production path uses `CappedPNGConsumer.putBytes` and `pngConsumerPutBytes` at `probe.swift:2214–2245`.

The control defines a separate `DirectSink.putBytes` and `directPutBytes` at `png-consumer-control.swift:8–53`.

The control omits production scratch chunking, integer failure codes, cancellation-marker access, release state, and production owner lifetime.

Its boundary and overflow cases can pass while the actual CoreGraphics callback remains defective.

Move the callback state and byte-copy routine into one shared source file compiled into both executables. The control must call that exact callback.

An exact generated-source identity check is also acceptable. Similar-looking duplicate logic is not equivalent evidence.

## P2 — native PNG failures discard causal partial bytes

Capacity, cancellation, and finalize failures throw at `probe.swift:2319–2338`.

The only hash and exclusive write occur after complete success at lines 2344–2346. The defer then destroys any partial encoded bytes.

This violates `text-probe-protocol-a01.md:17` and line 130. Both lines require preserved failures and partial output.

On every post-callback failure, capture the bounded byte count and SHA-256 before teardown. Publish the bytes to a distinct exclusive partial path.

Attach that exact path, count, digest, callback status, and finalize result to the causal error. Preserve a zero-byte observation when applicable.

## P2 — callback cancellation and initialization exceed their stated boundary

`requestedWithoutThrowing` evaluates `marker.path.withCString` at `probe.swift:704–706` from inside the C callback.

That Foundation path access and C-string conversion can materialize temporary Swift storage. No callback reservation or failure status covers that storage.

The callback therefore does more than update preallocated bytes and an integer status, contrary to the rationale's stated boundary.

The source initializes up to `rawBytes + 1 MiB` at `probe.swift:2270–2272`. It initializes another 64 KiB at lines 2273–2275.

The next cancellation check is line 2306. The initialization work has no row or chunk checkpoints.

The orientation image also groups five native setter calls between one check pair at lines 2378–2389.

Initial and run face metrics group multiple native getters at lines 1525–1532 and 1588–1591.

This conflicts with `text-probe-protocol-a01.md:125`, which requires cancellation checks during bounded copies.

Precompute and admit a stable NUL-terminated cancellation path before consumer creation. The callback should use only that stable owner and Darwin status.

Initialize both buffers in fixed chunks with checks between chunks. Keep the truthful limitation that one native or memory operation cannot be interrupted.

The callback itself uses 64 KiB chunks and a nonthrowing integer status. I found no authored Swift `throw` crossing that C callback.

## P2 — repeat and conversion failures lose causal geometry

Run matrix and size conversion failures retain only the run index and range at `probe.swift:1848–1861`.

Glyph position and advance conversion failures retain only indexes and glyph ID at lines 1889–1895.

The native scalar or matrix that failed finite Q16 conversion is absent from both causal records.

Each successful repetition records one shape digest and canonical mask digests at `probe.swift:2804–2816`.

The later full `ShapeRecord`, raw mask hash, mask bounds, count, and paths are discarded after the repetition.

`repeatEvidenceIsStable` detects a digest mismatch only after all repeats at lines 2893–2910. The differing shape is no longer available then.

The catch computes `failedShape = error.shape ?? shape` at line 2822. It then serializes only `error.shape` at lines 2830–2841.

A later error with a valid fallback shape can therefore retain a digest but publish no `failureShape`.

The report can therefore say repeat stability failed without retaining the native field or raw raster observation that changed.

Use tagged raw scalar observations before every fallible conversion. Store `failedShape`, rather than only `error.shape`, in the repeat.

Compare each repeat with the retained first observation before releasing its charge. On mismatch, transfer the existing repeat charge into causal evidence.

Retain the differing full shape and affected raw/canonical mask records. Identical repeats may continue to retain only checked digests.

## Confirmed A05 repairs

The A04 hard-cap defect is repaired in source structure.

- Encoded backing and callback scratch are reserved before allocation.
- The callback checks the complete requested count before copying any byte.
- Writes after the first callback failure return zero.
- The output file receives bytes only after bounded hashing and exclusive creation.

The CoreText call now uses the SDK's four-argument `CTLineGetTypographicBounds` declaration at `probe.swift:1772`.

Cases and the font manifest now receive exact byte-count and SHA-256 checks before JSON decoding at lines 2943–2967.

The authority retains its earlier exact pre-decode check. Later authority cross-checks remain present.

The A04 native-string, face-table, raster, event-log, and final-report ownership repairs remain present.
This review does not convert their source claims into measured runtime facts.

## Standards axis

The new sink duplicates its central boundary logic in the control. This is a material duplicated-code smell because the duplicate is the proof target.

The sink also has divergent ownership responsibilities. One function allocates, creates native objects, translates callback failures, writes files, and releases ledger state.

The required repair should extract one bounded consumer owner. That owner should make its destruction order and failure evidence explicit.

## Local SDK grounding

This review read the installed macOS SDK headers without compiling or calling them.

`CGDataConsumer.h:24–40` defines the byte callback, copied-byte return, zero stop signal, and release callback.

`CGDataConsumer.h:52–54` creates a consumer from the info pointer and callback table.

`CGImageDestination.h:78` creates an ImageIO destination from that consumer.

`CTLine.h:352–356` declares the four-argument typographic-bounds function used by A05.

These declarations support the source review. They do not establish Swift importer compatibility or native behavior.

## Reviewed identities

| File | SHA-256 |
| --- | --- |
| `feasibility-swift-a05/probe.swift` | `ba53f3e8c5c05d88b325c19092557293323ad9f29176fdb0f5b1d27053f64304` |
| `feasibility-swift-a05/output-schema.md` | `7bae045ef234ac3429caee908c917aec8be01b5631bca17d96b7547c312b9975` |
| `feasibility-swift-a05/source-rationale.md` | `524d041184131fe7b961f39f96fd0c78d5dbe58a355c88103986acdbbc97e403` |
| `feasibility-swift-a05/png-consumer-control.swift` | `29b37530c7b5374582e1e7be76992058b1ff054734a36319817902921cbe3860` |
| `feasibility-swift-a05/png-consumer-control-schema.md` | `f0a0b100099b04e851cc42ca335813aa580758f7b82eac2486374124c8fd7524` |
| `text-swift-parent-source-review-a04.md` | `3e2ae3f297b8c151966554ecb791f45600844d9ab5ecbb8b59cce5eb80d84c27` |
| `text-swift-parent-source-review-a04-addendum-a01.md` | `83220875264af9982465899f6f50dace6c2908a695f2b3e8eb2a72dfdc574faf` |
| `text-probe-protocol-a01.md` | `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89` |

## Proof-build verdict

Do not build or typecheck A05 as the Swift proof producer. Preserve it as reviewed source evidence.

Close both P1 blockers and three P2 defects in a new version. Re-review all source and contract bytes before build authorization.

Even a green successor would establish source readiness only. It would not establish native feasibility or product text support.

This is a same-model-family, artifact-separated review. No cross-family review was available.
