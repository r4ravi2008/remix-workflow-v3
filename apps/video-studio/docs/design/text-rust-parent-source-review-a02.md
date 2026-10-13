# Parent Rust text probe source review A02

The parent read the complete frozen A01 source previously.
For A02, the parent read every complete changed-file diff and every new source file.
The parent also read all four A02 package and contract documents.
This covers the complete resulting A02 source through the preserved baseline and complete changes.
The parent did not format, generate a lock, build, typecheck, or call native APIs.

The parent agrees with `text-rust-source-review-a02.md`.
Both A01 P1 findings are closed in source.
Three P2 findings block the proof build.

1. Native string conversion can allocate beyond the accepted UTF-8 limit before the later audit.
2. Cancellation does not cover all required bounded copies, scans, comparisons, and native observation sequences.
3. Retained font paths use twice their length instead of their actual `PathBuf` capacity.

The pinned Core Foundation string formatter uses a 32-byte stack buffer and writes chunks into a Rust formatter.
The returned Rust `String` can grow before the accepted ASCII and UTF-8 checks run.
The repair must admit the conversion before creating that owner.

`PathBuf::capacity()` exposes the underlying `OsString` capacity.
It has been stable since Rust 1.44.0. [Rust documentation](https://doc.rust-lang.org/std/path/struct.PathBuf.html#method.capacity)
Use that value with checked arithmetic for the retained path audit.

The initial suspicion about raw glyph-array scratch was resolved by the complete current context.
Positions and advances are consumed by their iterators.
Indices are consumed by the conversion loop.
Those source owners end before their temporary permit drops.
Destination arrays remain covered by the shape reservation.

The parent confirmed the opened-file and loaded-region identity structure.
The parent also confirmed streaming reports, exact used-input identities, and all three clip-reference repeat hashes.
These are source findings. Actual Darwin and framework behavior remains unrun.

Preserve A02 as rejected before lock generation and build.
Repair A03 separately under the same caps and selected drawing policy.
Re-review its complete source, schema, rationale, and ledger before building.

The package identities are listed in the independent A02 review.
No result establishes native text support, product integration, film completion, watching, hearing, or creative acceptance.
