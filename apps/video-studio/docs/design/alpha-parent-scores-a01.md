# Transparent PNG parent assessment A01

Root read Candidate A, original Candidate B, and corrected Candidate B A02 end to end.
Runtime and existing proof files remain unchanged. Scores assess designs, not implemented behavior.

| Criterion, 0–5 | A | B A02 |
| --- | ---: | ---: |
| Caller depth | 4 | 4 |
| Pixel contract | 5 | 4 |
| Bounded ownership | 4 | 5 |
| Compatibility | 5 | 3 |
| Verifiable outcome | 4 | 4 |
| Total | 22 | 20 |

Candidate A matches the existing sampled-raster worker boundary. Its UNORM16 color and coverage stay together until composition. It preserves the exact opaque sampler, blender, native callback, and permit lifetime. A source cache can retire after producing its last owned raster: the response owns copied pixels and its own permit. The eight-byte alpha raster costs more admitted memory, but avoids changing reader handoff ownership. Its external usage example incorrectly calls the crate-private StudioError::new. Synthesis must remove that caller-side branch and let Project validate the asset kind. The worker pseudocode must explicitly charge alpha raster bytes before allocation and release the straight cache only after the last raster is complete.

Candidate B A02 gives precise ownership for source responses and acknowledgements. Its direct composition reduces retained raster memory. However, it replaces the current worker handoff and needs a new direct opaque sampler without changing historical rounding. Its new H.264-only Plan7 codec registry restricts measured AV1 and VP9 sources beyond this alpha unit. SourceDecodeEvidence currently has no codec field. The registry also adds persisted native-representation policy unrelated to PNG alpha. Those additions require separate codec work and should not enter this unit. Its metadata class, bounds, counts, and policy provide more redundant facts than the unit needs.

Both candidates hide alpha arithmetic from callers and reject false coverage before writer admission. Both keep output opaque and disclose unmanaged sample values. Neither design establishes independent native pixels, whole-process memory, watching, hearing, or creative acceptance.

Provisional base: A. Graft B's single per-plan math policy and per-asset evidence binding to avoid duplicating an alpha identity on every VideoUse. Preserve A's measured extrema, counts, alpha hash, straight RGBA hash, premultiplied UNORM16 raster, legacy path, and copied-raster ownership. Require independent judgment before final synthesis.

The runners use the same available model family. Candidate A disclosed one accidental broad-search result from B after settling its architecture. This comparison is neither blind nor cross-family.
