# Swift native text probe source review A12

## Result

Swift A12 is rejected before typecheck or execution.

One P1 manifest defect prevents the declared terminal control from entering an exact build gate. Three P2 issues leave ownership or failure evidence incomplete.

This was a source-only, same-model-family review. I did not typecheck, build, run a control, start the producer, or call a native framework.

## P1 — the manifest omits the terminal control from its authoritative control set

`source-manifest-a12.json:8-36` declares the terminal report schema and its two-file compile unit. The manifest also binds both terminal sources and hashes their file rows.

However, `source-manifest-a12.json:208-211` lists only these two source controls:

- `failed-publication-control.swift`
- `persisted-output-budget-control.swift`

It omits `terminal-publication-control.swift`.

The manifest therefore has two conflicting control inventories. An exact schema/compile-unit/source-control join must reject this package before compilation.

Create a preserved successor. Add the terminal control to the authoritative set and rebind the complete manifest.

## P2 — the new reservation-table baseline cannot be independently replayed

`probe.swift:40-49` derives a 1,056,000-byte reservation-table owner. `probe.swift:1205-1208` adds it to the 25,600-byte event scratch baseline.

The first event therefore starts from 1,081,600 logical bytes. No event records the added baseline.

`AllocationSummary` exposes only `eventScratchBytes` at `probe.swift:615-630`. The policy caps at `probe.swift:4473` omit all reservation-table values.

The current independent replay starts from `eventScratchBytes` alone. A successor cannot verify A12's event transitions without duplicating a hidden Swift constant.

The 256-slot limit also has no declared schedule derivation, observed peak, or direct boundary control. The table fails safely when full, but source evidence does not prove that the required schedule fits.

Expose at least these facts in the next report contract:

- table owner bytes;
- slot count and key-byte limit;
- observed maximum live slots;
- exact initial replay baseline.

Bind a shared boundary control or a checked schedule derivation. Update the independent comparator to seed replay from the reported baseline.

## P2 — `TerminalPublicationOwner` adds an uncharged heap object

`probe.swift:1176-1190` allocates a class instance and a 65,536-byte raw scratch buffer.

The reservation at `probe.swift:4479` charges exactly 65,536 bytes. The scratch consumes that complete charge.

The class object, stored pointer, and capacity remain outside the logical owner formula. The separate 1,024-byte reservation-table allowance belongs to `BoundedReservationTracker`; it cannot cover this owner.

Add a conservative fixed header allowance to the terminal owner charge. Another valid repair is a non-heap owner whose complete retained representation is already covered.

## P2 — terminal-write prefix evidence is not observable after failure

`writeTerminalReport` reads the retained file prefix before descriptor close. It then stores the prefix facts in `ProbeFailure.evidence` at `probe.swift:2553-2574`.

`Main` emits only the error code and detail at `probe.swift:4540-4548`. It discards the evidence map.

The report cannot contain those facts because its own write failed. No bounded sidecar or stderr record carries them.

The manifest says the terminal writer preserves prefix evidence. The implementation preserves it only inside a transient thrown value.

Either publish the bounded failure facts through an admitted channel, or narrow the contract to transient in-process evidence. A retained-file observer can remain separate.

## Confirmed repairs

The A11 digest defect is closed. The eight-byte callback fixture now expects:

```text
66840dda154e8a113c31dd0ad32f7f3a366a80e8136979d8f5a101d3d29d6f72
```

The dynamic cleanup and rollback dictionaries are gone. The fixed table stores bounded byte keys, lengths, and tags.

The successful terminal path pre-admits prefix scratch and rollback state before fixed-point encoding. It appends one terminal event and performs no later ordinary ledger operation.

`TerminalPublicationSequence` checks both aggregate caps. Its source control covers exact limits, one-byte-under limits, missing preparation, and a second terminal event.

The persisted-output arithmetic remains exact:

- mandatory mask evidence: 314,231,808 bytes;
- possible observation-only masks: 52,740,096 bytes;
- complete qualification bound: 396,071,265 bytes;
- qualification file count: 201;
- configured persisted cap: 536,870,912 bytes.

The terminal failure path keeps the conservative report-file charge and rollback reservation. It does not create a post-terminal release event.

The absence of a global ordinary-event guard after terminal append is not a separate defect. The current success path has no such call.

## Required successor gate

1. Preserve A12 and both A11 reviews unchanged.
2. Repair the manifest's exact terminal-control inventory.
3. Expose and verify the reservation-table baseline, capacity, and peak use.
4. Charge the complete terminal scratch owner representation.
5. Make terminal-write failure evidence observable, or correct the preservation claim.
6. Freeze and re-review the successor before typecheck or control execution.

Compiler compatibility, callback behavior, CoreText geometry, CoreGraphics pixels, ImageIO output, and producer identity remain unverified.

This review establishes no product integration, playback, hearing, creative acceptance, or full-film result.

## Reviewed identities

All eighteen manifest file rows match their current byte counts and SHA-256 values. The package directory also contains the manifest itself, as expected.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a12.json` | 9,293 | `5567ed131eaddabfb7d3d2b22c962e26b3913efb8ce715b8e3c9db9239f051d1` |
| `probe.swift` | 258,297 | `52c6b87ccbf406202485afa3799f9d8ab1a9fed75f51640558351b9a566a1bbc` |
| `persisted-output-budget-shared.swift` | 10,288 | `5d0e5a8244697ecf95bcab4c397957effb951a04bb1ec8f5bbe11e865184a4ab` |
| `terminal-publication-control.swift` | 5,418 | `0057c35c0a9149c8bd336da118ea6fc53137705e1a84d77e93158496a268e4e4` |
| `png-consumer-control.swift` | 12,513 | `bb48a12806387cfd4e17bdb9c40befd96ee7fdebdb1a499b7a4f7959b9975a45` |
| `protocol-bound-correction-a12.md` | 1,365 | `500e2aae219efe8351c8e77d8055ecb147d128c80e6d800efaee0c7960859363` |

The preserved protocol authority remains SHA-256 `4e4e399072372f6dbc02bb16f55d80fd1ca7cf1690ac8643d34055a1cae31d89`.
