# Swift A04 parent source review

A04 is rejected before build. A05 repairs are in progress. A04 remains byte-preserved.

The parent read the complete A04 source changes against the previously read A03 baseline.
The parent read both complete A04 contract documents.
The source diff contains 1,660 source lines, followed by contract-document changes.
The saved combined patch has SHA-256 `e8a0e6bb3810d78bcc76cf525f1fa2403a7448d30dba2e6ad13ee3a416377234`.

## Findings

1. P1: PNG admission remains a capacity hint followed by a post-finalization check.
   `NSMutableData(capacity:)` permits ImageIO to expand the application-owned encoded buffer.
   The shared PNG admission review confirms this defect in both Rust A04 and Swift A04.
   A05 must reject writes that cross the admitted bound before copying them.

2. P1: The new `CTLineGetTypographicBounds` call passes five arguments, including `CFRange`.
   The bound macOS 26.1 SDK declaration accepts only line, ascent, descent, and leading.
   The range argument belongs to a different CoreText API.
   Remove the range argument in A05 and preserve the typographic metric observations.
   The parent checked `CoreText.framework/Headers/CTLine.h`, lines 352 through 356.

## Checked repairs

Shape runs are mutable. Geometry preserves tagged nonfinite scalars.
Native initial metrics come from CTFont getters.
Descriptor reads require regular files, bounded chunks, and an EOF check.
Native tag counts are checked before copying the owned array.
Temporary table owners remain in their scoped block until their charge is released.
Render failures receive the current shape through `withShape`.
The glyph image uses alpha8 backing with an explicitly charged snapshot.
The terminal report predicts its final event and keeps its report reservation through teardown.
Nonmonotonic status remains observational.

This review does not claim that every earlier ownership concern is proven closed.
The successor requires source review, compiler verification, and independent native observation.
No Swift build, typecheck, native framework, probe, GPU, Resolve, or product operation ran.
