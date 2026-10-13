# Swift A06 parent source review

A06 is rejected before compilation. No Swift compiler, control, producer, or native framework was invoked.

The parent read the complete 1,005-line A05-to-A06 probe delta, the complete shared callback and direct control, and every changed contract. Truncated source ranges were reread in full. A05 and A06 remain preserved.

The failure RepeatRecord initializer at probe.swift:3023 omits referenceMaskSha256 and orders existing arguments incorrectly. This is an additional compile blocker.

The retained result leases end while the final ProbeReport still owns and encodes those results. The admitted ledger therefore fails to cover the final report lifetime. The nested result envelope must explicitly cover retained heap owners or describe its narrower conservative observation scope.

The callback state needs synchronization for concurrent or reentrant callbacks. The release-unobserved path must avoid reading borrowed storage after teardown. Cancellation before repeat cleanup must release or retain reservations honestly.

writeExclusiveBuffer must preserve disk charges after an exclusive partial file exists. A write or fsync error does not delete those bytes.

The independent A06 review is 0f23a19792f16b570faa1d1a74396ac0fa81bc1a67cd97cf5b3c1ec17d23b8ab. The A06 source manifest is 6e46eb9fbd6bfc3992c36ec2af63be43ab4a9e24a0136c462b554d0f655d58da. A07 repairs are source-only and must preserve A06.

This finding set does not establish imported Swift API compatibility, native behavior, physical memory, product integration, playback, hearing, or creative acceptance.
