# Swift native text probe source review A13

## Result

Swift A13 remains rejected before typecheck or execution.

The prior P1 and two ownership P2 findings are closed. The terminal-prefix facts are now externally observable.

Three P2 contract defects remain. No P1 remains in the reviewed source.

This was a source-only, same-model-family review. I did not typecheck, build, run controls, launch the producer, or call native frameworks.

## P2 — the documented aggregate stderr cap has an uncounted second write

`emitFailureEvidence` at `probe.swift:748-792` counts each emitted byte against the 131,072-byte cap.

`Main` then writes another code-and-detail line at `probe.swift:4525`. That line bypasses the counter and field bounds.

The output schema and terminal-control contract call 131,072 bytes an aggregate stderr bound. The source does not enforce that aggregate bound.

This extra write can also repeat a terminal error after the structured line protocol. An oversized argument error can exceed the declared channel cap.

Remove the legacy write, or make the bounded emitter own every failure-channel byte.

The descriptor-derived terminal prefix facts themselves are present. `writeTerminalReport` captures them before descriptor close and places them in the thrown evidence map.

## P2 — one reported peak is sampled before the final reservation slots

`PolicyRecord` is created at `probe.swift:4453`. Its `caps` map snapshots `reservationTableObservedPeakSlots` at that point.

The producer then adds the terminal-owner cleanup slot and terminal-report rollback slot at `probe.swift:4459-4461`.

`AllocationSummary` samples the table after those additions. The two report locations can therefore contain different observed peaks.

The output schema says `policy.caps` records observed peak slots. A runtime observation cannot be final before the final reservations occur.

Construct the policy after both reservations. Another valid repair is to remove this observation from `policy.caps` and keep `allocation` authoritative.

## P2 — failure-path owner lifetime is overstated

The successful path retains `TerminalPublicationOwner`, the ledger, report data, and result graph through the exclusive write and post-write guards.

The failure path differs. A throw from `run` unwinds its local owners before `Main.catch` emits the evidence.

The thrown evidence map survives that unwind. The event log also contains no release event for the conservative logical charge.

However, the terminal owner and retained report graph need not remain physically live until process exit. Several A13 documents claim that lifetime.

Narrow those statements to conservative ledger evidence and surviving thrown facts. Alternatively, emit the facts inside a scoped catch while the owners remain live.

## Closed A12 findings

The manifest now has one exact four-control inventory:

- PNG callback control, schema 3;
- failed-publication control, schema 1;
- persisted-output budget control, schema 2;
- terminal-publication control, schema 1.

Each control has an ordered compile-unit map. The PNG control now appears in the same authoritative source-control map.

`BoundedReservationTable` is shared by the producer and budget control. The shared contract exposes these values:

- 256 slots;
- 4,096 bytes per key;
- 1,056,000 owner bytes;
- 25,600 event-scratch bytes;
- 1,081,600 initial replay bytes.

The control fills every slot, rejects overflow, recycles one slot, and observes a peak of 256 slots.

The producer reports the table owner, capacity, key limit, observed peak, and replay baseline in `AllocationSummary`.

`TerminalPublicationOwner` now reserves 66,560 bytes before allocation. That charge covers 65,536 scratch bytes and a 1,024-byte object allowance.

The terminal path pre-admits the owner and rollback reservation before fixed-point encoding. It appends one terminal event.

Successful publication performs no later ledger event. Post-write checks compare event bytes, event count, written bytes, caps, and final outstanding bytes.

The fixed persisted-output arithmetic remains unchanged:

- complete qualification bound: 396,071,265 bytes;
- configured persisted cap: 536,870,912 bytes;
- allocation-event cap: 16,777,216 bytes;
- fixed successful file count: 201.

The corrected PNG callback digest remains:

```text
66840dda154e8a113c31dd0ad32f7f3a366a80e8136979d8f5a101d3d29d6f72
```

## Required successor gate

1. Preserve A13 and this review unchanged.
2. Enforce one aggregate bound across every stderr failure write.
3. Make the reported table peak authoritative after all reservations.
4. Correct the failure-path lifetime claim or retain the owners during emission.
5. Freeze and re-review the successor before typecheck.

The next gate must still typecheck the exact macOS SDK source. It must then run all four controls before any native producer execution.

CoreText geometry, CoreGraphics pixels, ImageIO output, producer identity, and native cancellation remain unverified.

This review establishes no product integration, playback, hearing, creative acceptance, or full-film result.

## Reviewed identities

All nineteen manifest file rows match their current byte counts and SHA-256 values. The package has no unlisted source or contract file.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a13.json` | 10,294 | `9f3514162514c5109257b1caadbebd5443913534667fea12043e4292fd6e63a6` |
| `probe.swift` | 258,963 | `a4f36c7ccb00f4c1fe1319e647d1fe34ec1a85e86a2242ce10330f5ea83787bf` |
| `persisted-output-budget-shared.swift` | 15,113 | `84bba49cbe05aa0013cb4e43fc5fa1927f23252f97d541e5f78345dd41e3cb92` |
| `persisted-output-budget-control.swift` | 6,401 | `44fc99ebd77dc93cda14046931e1bbe98d2bcaf5c82b0f3c05b9544d2025c454` |
| `terminal-publication-control.swift` | 5,418 | `df6564ba4aa21ad8a3e3b04ba6e4803d1da071f3faf7dff0ad60f93eb09135af` |
| `png-consumer-control.swift` | 12,513 | `5f1eaaacca37bdfd704ca484b9fdae5a3116d56fae2c2ba4478af582e0df80a6` |
| `protocol-bound-correction-a13.md` | 1,379 | `76d918f28b41c420b3c6ab06705b5868b560f4cfb6a092dd22e6093d0727b6ef` |

The preserved protocol authority remains SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.
