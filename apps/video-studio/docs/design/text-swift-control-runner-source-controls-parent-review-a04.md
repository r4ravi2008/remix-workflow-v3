# Swift runner source controls A04: parent review

The parent read the complete A03-to-A04 diff and the complete rationale. The parent had already read all 926 A03 lines. The parent also read the complete independent A04 review.

| Artifact | SHA-256 |
| --- | --- |
| Source controls A04 | `9f6c3391c6bb2717a92049749959c77525627308bd80a9343bedd161d4f02028` |
| Rationale A04 | `7c3b898522627472361e6657e28ee9c5360430c216c8f848226fff503c8ebce3` |
| Unchanged runner A03 | `d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c` |
| Independent review A04 | `c1c5be61b5d27f994eead56ad63c29221f39a7ccf5bd7fd7837f749a1e195c40` |

No P1 or P2 finding remains. A04 corrects the disposable replacement test's assumption. It verifies unchanged retained bytes, hash, UUID, device, inode, mode, and size. It verifies the full-record equality flag against the actual metadata comparison. It separately requires replacement pathname identity, hash, and UUID differences and a false pathname match.

The production runner retains full metadata drift rejection. Runner A03 and its wire schema remain unchanged. A03's failed source-control result remains preserved.

Proceed with one fresh A04 no-child source-control run. Its actual result must pass and receive parent readback before the four compiled controls are authorized. The independent reviewer used the same model family and inherited context. No control, compiler, native framework, GPU, or Resolve process ran during this source review.
