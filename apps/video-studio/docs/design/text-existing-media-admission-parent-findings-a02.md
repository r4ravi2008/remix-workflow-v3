# Existing-media admission A02 parent findings

A02 remains a preserved design-only proposal.
The parent read all 613 lines and does not accept the design for product implementation.
Its SHA-256 is `d95582f634c4f22e374cd02c029e823295a8a0d36ba2e36c0edac9094648d9a4`.

The dedicated Plan8 methods preserve the existing `ExportRequest` Rust literals.
Route metadata precedes stored-body reads.
The design now gives every Snapshot timeline and asset a bounded count domain.
It specifies bounded SQLite chunks and one canonical serialized Plan8 owner.

Two ownership findings remain.

1. Tree deletion compares live node requests against the current element count, including a zero-byte policy at zero elements.
   The installed Rust 1.94.0 source retains the empty leaf root after the final removal.
   `map/entry.rs` lines 606–617 only remove the pair, decrement length, and pop an emptied internal root.
   `remove.rs` lines 31–74 leave the leaf root in place when it has no parent.
   A reservation must cover the container's retained storage until actual deallocation.
   Removal controls must check the real retained owner and require zero after deallocation.

2. Selected normalized results enter a private draft during source validation.
   The `source_peak` formula omits that retained draft while revision bytes, parse state, and Snapshot owners remain live.
   A03 must define a schedule without overlapping draft ownership or charge that overlap explicitly.
   The selected normalization result must still be constructed once.

The installed source evidence is under:
`/Users/aira/.rustup/toolchains/stable-aarch64-apple-darwin/share/doc/rust/html/src/alloc/collections/btree/`.
The source HTML identifies version `1.94.0 (4a4ef493e 2026-03-02)`.
This is source inspection, not an executed allocation measurement.

The route prose also needs one clarification.
Both routes require the new common cross-table intent check.
The unchanged-query statement should refer to legacy body queries and serializers after that check.

A03 design authoring and independent A02 review are underway.
No product source, helper, test, compiler, native process, or media operation executed during this review.
