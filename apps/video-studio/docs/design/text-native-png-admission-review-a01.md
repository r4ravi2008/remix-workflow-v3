# Native text PNG admission review A01

## Disposition

Both frozen producers have the same P1 admission defect.

The native execution gate must remain absent. The Rust and Swift packages need new source versions before execution.

The prior source and build reviews remain valid historical records. They do not authorize native execution with this defect.

## P1 — ImageIO can grow the application-owned PNG buffer beyond its charge

Rust A04 reserves `raw_bytes + 1 MiB` at `native.rs:438-447`.
It then creates `CFMutableData::new(None, 0)` at line 449.
ImageIO writes into that mutable owner during `destination.finalize()` at line 473.
The producer reads and rejects an oversized result only at lines 483-490.

`CFMutableData` has no hard maximum in this path. The reservation does not constrain ImageIO's writes.
ImageIO can therefore grow the encoded owner beyond `encoded_bound` before the producer rejects it.

Swift A04 reserves the same derived bound at `probe.swift:2194-2201`.
It creates `NSMutableData(capacity: encodedBound)` at line 2202.
That initializer sets an initial capacity. It does not establish a maximum length.
ImageIO can expand the owner during finalization at line 2216.
The first length check occurs at lines 2220-2223, after that expansion.

Both paths contradict their checked application-owned payload claim.
The excess bytes belong to the mutable encoded owner, rather than an excluded framework-internal allocation.
Rejecting the final length does not undo the earlier cap violation.

## Required repair

Use a consumer whose write callback rejects bytes before the cumulative count exceeds the admitted bound.
A bounded `CGDataConsumer` or equivalent descriptor-backed sink can provide that enforcement.

The successor must meet these conditions:

1. Reserve the exact encoded-output bound before creating the destination.
2. Reject the write that would cross that bound before copying those bytes into application-owned storage.
3. Keep the bounded sink and its permit live through ImageIO finalization.
4. Preserve partial output and a bounded causal failure record.
5. Keep the current bound. Do not widen the cap to hide this defect.
6. Add a direct negative control for a consumer write that crosses the remaining allowance.

A mathematical PNG maximum could also close the issue if the implementation proves and enforces it before encoding.
A post-finalization length check alone is insufficient.

## Scope

This is a source-level admission finding. I did not build or run either producer.

It does not reject the reviewed font, shaping, geometry, or identity designs.
It blocks both producers from supporting the stated 16 MiB logical owned-payload claim during native execution.

No native framework, probe, GPU, Resolve, product, playback, hearing, or creative operation ran during this review.

This review is within the same model family. No cross-family reviewer was available.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `feasibility-rust-a04/src/native.rs` | `d58b1bcbcc8202f54d9b14a4cf23f972b4f718eca9ae507718ec70e085beb7a2` |
| `feasibility-rust-a04/allocation-ledger.md` | `e2a9e577351b2404fbd02007568c6255a7024a9230fcc802967f76fa30f244f3` |
| `feasibility-rust-a04/output-schema.md` | `29985f47174df4ee9155d5f394addf2434af224cd47190842767961bcfa54d19` |
| `feasibility-swift-a04/probe.swift` | `515ff13aac25a73dbaaa1e0b0a06f11e0b001910484e6305de10ce7fad9bf711` |
| `feasibility-swift-a04/output-schema.md` | `ff3b99a02cf20e5ddc31b778966f3908c480b40e600050bc912838e2b8703d43` |
| `feasibility-swift-a04/source-rationale.md` | `035478859d02178278883f54e8b3b6d4f4db900ee13287574f4567c45ead0957` |
