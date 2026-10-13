# Swift native text probe source review A06

## Scope and disposition

I reviewed the frozen A05 review, its A05 addendum, the complete A05-to-A06 source delta, the A06 source package, the source manifest, the output contracts, and the allocation ledger.

This was a source-only review. I did not build, typecheck, run, or call CoreText, CoreGraphics, ImageIO, or the direct callback control.

A06 closes the two prior P1 ownership defects and the prior repeat, geometry, callback-cancellation, and partial-output findings. A06 is **not ready for native proof** because one retained-result cap defect remains. Two native callback assumptions remain explicit proof limits.

This is an artifact-separated, same-model-family review. It does not establish Swift importer compatibility or native framework behavior.

## P1 — retained `CaseResult` owners are released before the final report

A06 reserves an inline result-array charge and one nested-result lease per case at `probe.swift:3222-3243`. The result values remain in `results` after each case is appended at `probe.swift:3270`.

The aggregate `observationData` encoding ends at `probe.swift:3272-3280`. A06 releases every nested-result lease immediately afterward at `probe.swift:3281-3287`.

The same `results` array is then retained by the `ProbeReport` at `probe.swift:3309` and encoded into the terminal report in the fixed-point loop beginning at `probe.swift:3318`. The result values, their nested strings, arrays, masks, errors, and failure evidence therefore remain live after their leases are released.

This under-reports the application-owned logical charge during final report construction. The A06 `caseResultOwnerBound` addition at `probe.swift:2767-2780` is useful, but releasing that lease before the `ProbeReport` encode defeats its lifetime claim.

Keep the result leases until the terminal report bytes are written and the retained result graph is no longer needed. Alternatively, move ownership into an explicitly bounded report owner and release the result graph only after report publication. Recompute `finalOutstandingBytes` and the fixed-point allocation facts after that lifetime decision.

## P2 — the nested-result formula still needs a concrete heap-capacity proof

`caseResultOwnerBound` counts four top-level mask records, twelve toggle records, three repeat records, array headers, one native image record, one error dictionary header, a fixed `caseObservationEnvelope`, and a few string slots at `probe.swift:2767-2780`.

The actual retained graph also contains setter arrays and their strings inside every mask, `RepeatRasterEvidence` mask records, error dictionaries and strings, optional geometry arrays, native-image paths, and absolute output paths. The fixed envelope is checked against JSON bytes at `probe.swift:3262-3265`, but JSON byte length does not establish Swift heap capacity or array growth.

Before treating the 16 MiB ledger as a complete retained-object bound, add explicit maximums and capacity charges for these nested owners, or state that the envelope is a conservative admitted opaque observation budget rather than a measured heap bound. Bind the output-root path length if it contributes to retained record strings.

## P2 — the release-unobserved branch reads callback storage after teardown begins

The normal failure branches capture partial bytes before calling `nativeOwner.destroy()` at `probe.swift:2438-2447` and `probe.swift:2450-2453`. The success path hashes the complete bytes, calls `destroy()`, and then, when `releaseObserved` is false, calls `partialNativePNG` at `probe.swift:2457-2461`.

`NativePNGOwner.destroy()` drops the destination and consumer at `probe.swift:2273-2279`. The installed SDK header says the release callback is called when the consumer is freed, but it does not specify callback quiescence or thread serialization (`CGDataConsumer.h:24-40`). When `releaseObserved` is false, the source has no proof that native callbacks have stopped before `partialNativePNG` hashes and writes the still-borrowed storage.

Capture the partial bytes before destruction in this branch, or retain the callback owner and backing until the release callback is observed. Do not use post-destroy bytes as causal evidence until callback quiescence is established.

## P2 — callback serialization and reentrancy remain an unverified assumption

`SharedPNGConsumerState` mutates ordinary Swift counters in `png-consumer-shared.swift:28-78`. The callbacks use an unretained lookup for `putBytes` at lines 81-85 and consume one retained reference in `sharedPNGRelease` at lines 87-94.

`CGDataConsumer.h:24-40` specifies the callback arguments, the copied-byte return value, and the release callback. It does not state that callbacks are serialized, non-reentrant, or confined to the thread that created the consumer.

The direct control calls the same callback serially at `png-consumer-control.swift:37-84`. It therefore proves the byte-cap and cancellation state machine for serial calls, but it does not prove safety under concurrent or reentrant callbacks. Establish a documented one-consumer serialization invariant before native acceptance, or protect `bytesWritten`, `failureCode`, and `releaseObserved` with a suitable synchronization strategy. Add a bounded control for the chosen invariant.

## Confirmed A06 repairs

- `NativePNGOwner` is the sole strong owner of the destination and consumer. It drops the destination before the consumer at `probe.swift:2273-2279`.
- The consumer receives one retained `SharedPNGConsumerState` reference at `probe.swift:2247-2254`. The shared release callback consumes that reference.
- Backing and callback scratch are admitted before allocation and initialized in cancellation-checked chunks at `probe.swift:2339-2394`.
- Partial bytes, callback status, release observation, finalize result, digest, and an exclusive `.partial` file are captured before normal failure teardown at `probe.swift:2293-2325` and `probe.swift:2438-2473`.
- The producer and direct control compile the exact shared callback source listed in `source-manifest-a06.json`.
- The direct control covers exact capacity, one-byte overflow after a retained prefix, and cancellation before copy. It does not import CoreGraphics or ImageIO.
- Geometry errors now retain typed raw scalar observations through the `ProbeFailure` chain.
- Each successful repeat compares shape, main, guard, clipped, and reference digests immediately at `probe.swift:2965-2980`.
- A later failed repeat retains `failureShape` and `failureRaster` at `probe.swift:2999-3024`.
- The four fractional-size setter controls run inside every `repeatIndex` at `probe.swift:2942-2961`; `ToggleRecord.repeatIndex` binds each control to its fresh repetition.
- `NativeShapeOwner.endNativeObjects()` releases line, attributed string, font, graphics font, and provider in dependency order at `probe.swift:634-647`.
- Raster and CGImage snapshot owners remain live through ImageIO finalization at `probe.swift:2486-2626`.

## Cancellation and failure limits

Cancellation checks surround descriptor reads, hashes, native calls, fixed-size initialization, callback chunks, and bounded writes. One CoreText, CoreGraphics, or ImageIO call remains non-interruptible.

A cancellation or ledger failure before the inner repeat `defer` can leave a reserved source or shape charge live. `processCase` reserves the source record at `probe.swift:2837-2842` and the retained shape at `probe.swift:2845`, then checks cancellation before installing the repeat cleanup at `probe.swift:2847-2855`. The outer loop converts the error into a result at `probe.swift:3250-3257` and may continue. Add one outer cleanup scope or stop processing after cancellation so failed reservations cannot survive as phantom ledger charge.

The source does not claim total process RSS or undocumented framework allocations. The callback proof remains limited to the application-owned backing and scratch buffers.

## Source identities

| A06 file | Bytes | SHA-256 |
| --- | ---: | --- |
| `feasibility-swift-a06/probe.swift` | 196097 | `88748445e0e4fa0cb7c23dbf3ed9e155b86faf3b58d64514311e86cd4bcc2e61` |
| `feasibility-swift-a06/png-consumer-shared.swift` | 3669 | `ddb37479b71f8373f188259cbff4ac54ffa57ffb5439ae91388588f0c6e46167` |
| `feasibility-swift-a06/png-consumer-control.swift` | 5470 | `07177a99af8bc9d0137bd0a21c19d31bc1e78bf024461a06269db8aab61cee93` |
| `feasibility-swift-a06/source-manifest-a06.json` | 2223 | `6e46eb9fbd6bfc3992c36ec2af63be43ab4a9e24a0136c462b554d0f655d58da` |
| `feasibility-swift-a06/output-schema.md` | 16413 | `1aed6968912fb96e6e61a765f192c0639212345a7b5736c20b7b5fc2beae6dfe` |
| `feasibility-swift-a06/source-rationale.md` | 18953 | `73a22931b0fcc9a9393c949a17e7ea90bd38b1803b1e6948240ef5772ffd775b` |
| `feasibility-swift-a06/allocation-ledger.md` | 3718 | `875b025a446a7a73c64a6a6e3bf1579a707fda11b901133c585587a5388d59f6` |
| `feasibility-swift-a06/png-consumer-control-schema.md` | 2298 | `cfbb684acf15b99ace03b3398096b3f2a30cda2621599319def417b38390d669` |

The source manifest records the producer compile unit as `probe.swift` plus `png-consumer-shared.swift`, and the control compile unit as `png-consumer-control.swift` plus `png-consumer-shared.swift`. Its caller bindings cover the producer source hash, shared source hash, and compiled producer image hash. A future control runner should also bind the control source and control binary identity before giving the direct-control result proof credit.

| Preserved A05 review input | SHA-256 |
| --- | --- |
| `text-swift-source-review-a05.md` | `e3ff8dec0441066d006ce95c8b1823fba9f911bbbb48e4c66df1da71e7ba7ebc` |
| `text-swift-source-review-a05-addendum-a01.md` | `3c08775ab22dca25bc5890bee45a6608490886bb69a1462e6e537c138b64e2ff` |

## SDK grounding

The installed SDK is `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk`.

`System/Library/Frameworks/CoreGraphics.framework/Headers/CGDataConsumer.h:24-40` defines the put-bytes callback, zero-byte stop result, and release callback. `:52-54` creates a consumer from the info pointer and callback table.

`System/Library/Frameworks/ImageIO.framework/Headers/CGImageDestination.h:78` creates a destination from a data consumer. `:109` adds an image, and `:126` finalizes the destination.

These headers support the ownership review. They do not establish Swift importer compatibility, callback serialization, callback quiescence after finalization, or successful native execution.

## Final verdict

A06 is a meaningful source repair. The shared callback is now the same code used by the direct control, partial bytes are preserved before ordinary teardown, all setter controls repeat three times, and repeat failures retain raw geometry and raster records.

Do not freeze A06 as a complete bounded native proof until result-owner leases cover final report construction, nested dynamic owner bounds are made explicit, and the callback serialization/release-quiescence assumption is either established or bounded as a stated limitation.
