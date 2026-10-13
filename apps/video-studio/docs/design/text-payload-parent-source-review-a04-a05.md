# Payload A04 and A05 parent source review

A04 and A05 remain rejected before build. The parent read all 558 lines of the A03-to-A04 Rust source patch and all 299 lines of its runner patch. The parent read all three A04 contracts. The full previously reviewed A03 source remains the baseline.

A04 had a definite compile blocker. Err(error) shadowed the module error constructor in the buffer-extraction branch. Its runner could lose remaining reconciliation on OSError, report launched state before launch, and discard partial report identity after JSON failure. The parent fully read B's independent A04 review, which confirmed these and the incomplete final sync evidence.

The parent read the entire A04-to-A05 module and runner changes and all three contract deltas. A05 removes shadowing, captures expected filesystem errors per after-check, separates attempted and observed launch, and retains partial report identity on JSON/schema failure.

Three P2 findings remain. Invalid UTF-8 raises an uncaught UnicodeDecodeError. Final sync_all failure omits written_bytes and flush:ok. Partial hashing reopens the pathname instead of observing the still-owned writer descriptor. The parent fully read B's independent A05 review, which confirmed all three. A separate A06 repair is requested.

No payload build, typecheck, formatter, measurement executable, native call, product mutation, media, GPU, or Resolve operation ran. Copied-package capacities and application-owned logical charges remain unmeasured.
