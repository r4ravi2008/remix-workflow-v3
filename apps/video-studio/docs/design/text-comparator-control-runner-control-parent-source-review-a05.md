# Comparator corrected-loader controls A05 — parent source review

Root found no P1 or P2 within the corrected-loader and overlay regression scope.
The source remains unexecuted. Root read all 386 source lines and the complete
contract, fixture, and manifest. All 24 manifest rows match, totaling 617,689
bytes. Root reconstructed aggregate
`2b4d9dd5666e456c21d4f1994351f2e85e22774115ae2f9a7de2a130e6193f1d`.

The 17,382-byte source SHA-256 is
`22a5d89f19a252d365f8b5a2703e6cc9308aa884a2e18f8981974889b18a720e`.
The contract SHA-256 is
`0d08449a8fca1dee8fa9d21bb0aa14aa4734e2439a87fe4aa85106e5c1d3e8e3`.
The fixture SHA-256 is
`080d6b32b518c3dfcc06336826ff472700386a881c1a0e7809858bfe846c698a`.
The manifest SHA-256 is
`21c8eb8e3be4d53828ecc9a6223ed7d68043523225d358bdb9ffac082a669447`.

A05 measures the frozen A03 suite, A04 supplement, and corrected A04 runner.
The one-load hook checks the exact historical runner tuple before assigning
the new measured tuple. It then invokes the unchanged A04 entry point. That
entry point executes the complete A03 suite against the corrected runner and
both A04 report-owner and fixed-command supplements. The hook restores the
loader after the call.

The final result retains the complete A03 report, its canonical digest, the
exact measured two-domain seal row, and the complete A04 result. It verifies
the rebound runner receipt and full report digest joins. Historical fixtures
retain their version labels. The result explicitly names the actual corrected
runner bytes used by the suite.

The direct regression controls call A04's actual overlay validator. The saved
Pillow-then-NumPy overlay is the positive case. Package reversal, within-package
reversal, duplicate rows, and unknown packages must return exact rejection codes.
The saved failed attempt remains a bound predecessor and is never rewritten.

The 4 MiB final control-output cap permits retaining the complete result. It is
separate from the unchanged production publication owner caps. Root must retain
external invocation, interpreter, stdout, stderr, and current-file readback.

No control import, child, runner attempt, compiler, native producer, media
operation, GPU generation, Resolve operation, hearing, viewing, or creative
acceptance occurred during this review.
