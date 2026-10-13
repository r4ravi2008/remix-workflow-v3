# Transparent PNG alpha implementation notes A01

Status: runtime implementation and code checks complete; independent ordinary-CLI native proof pending.

## Bound contract

The implementation follows `alpha-synthesis-a01.md`, SHA-256
`b86adde3537a2fcf285a97ba35ed52a374db69859052ae40b36864f5ce3d8db8`.
It also follows `alpha-judgment-a01.md`, SHA-256
`cf99b0a0cc0fc2f714d558ba873ea96cd2bf5746b47305fb7472a06a19f9d359`.

The implementation adds transparent eight-bit static PNG inputs to the existing
Project commit, prepare, export, cancel and verify operations. It adds no public
pixel executor or caller-selected alpha arithmetic.

## Implemented shape

- `ImageAlphaV1` binds the row-major alpha hash, extrema and pixel counts.
  Opaque images omit this field and retain their serialized descriptor bytes.
- `AlphaPolicy::StraightRgbaPremulUnorm16Q16V1` selects Plan7 only for a
  directly used transparent image.
- Each unique directly used image has one sorted decode-evidence record.
  Transparent records bind `source_alpha_id`; opaque records omit it.
- The decoder keeps transparent source pixels as straight RGBA8. The worker
  copies transformed samples into an eight-byte premultiplied BGRA16 raster.
- Mapping retains the established binary64 crop, fit and placement geometry.
  The alpha branch alone quantizes bilinear fractions to Q16 and uses Q32 taps.
- The compositor applies intrinsic coverage, clip opacity and mask coverage.
  It writes only opaque BGRA8 canvas pixels.
- A frame must have at least one positive effective picture contribution before
  handoff. A cropped transparent hole can pass conservative preparation and
  fail this exact runtime check.
- Logical admission reserves each alpha raster before allocation. Each raster
  is limited to 128 MiB. Aggregate picture permits remain limited to 512 MiB.
- PNG expansion, alpha scans, raster sampling, blending and decoded output
  opacity scans check cancellation at row boundaries.

## Ownership details

The PNG worker retains straight source pixels only through the final sampling
request. Its copied alpha raster owns a separate permit across the response
channel. A sampled all-zero raster becomes a `ZeroAlpha` response, which keeps
the Source observation and releases the unused raster permit before send.

No native framework object crosses the movie callback. Existing capacity-one
picture channels, serialized PNG decoding, track joins, leases, epochs and
publication recovery remain in force.

## Private observation seam

The `cfg(test)` frame observer binds one exact plan hash and at most 512 expected
frame hashes. It receives a borrowed canvas after runtime coverage succeeds and
before frame handoff. It hashes the borrowed bytes without cloning the canvas.
An RAII guard removes the observer after success or failure. No environment
hook, public API, receipt field or production trace was added.

The bounded native canary creates and prepares an isolated Project inside its
test executable. It binds the guard to that test-prepared plan hash. It then
uses the public export, verification and completed-replay paths. Its executable,
plan and receipt identities remain separate from the ordinary CLI producer.

## Design deviations and clarifications

There is no arithmetic or ownership deviation from the selected synthesis.
The implementation uses `DecodedPicture`, `StraightRgba8` and `AlphaRaster16`
as private names for the selected representation boundaries.

A final private-boundary review found that flat slice bounds alone could let an
invalid x coordinate alias the next source row. `StraightRgba8::pixel` now checks
x and y explicitly. Alpha and opaque sampling also share the Mapping source-
extent guard. A 2x2 source against a 4x1 Mapping is the regression case.

The implementation keeps a zero-alpha response's resolved bounds for source
observation checks. It does not retain the zero raster or its permit. This is
the selected source-lineage behavior, made explicit in the execution enum.

Plan2 through Plan6 keep their existing image-evidence behavior. New sorting
and uniqueness rules apply only to Plan7. This preserves historical plan bytes.

The first read-only implementation review found two stale schema allowlists in
public verification and staging recovery. Both now admit Plan7. Verification
reuses `verify_plan_sources`. Plan7 staging recovery uses the central decode
evidence validator. Plan2 through Plan6 retain their earlier recovery path.

The preserved A02 follow-up review found no remaining P1 blocker after that
repair. It predates the final source-extent hardening and reference freeze.
Those later results are recorded here without rewriting either review.

The independent A03 pure fixtures live in the preserved alpha artifact tree.
Tests bind `alpha-fixture-a03.json` by SHA-256
`afdfb1848940b9063640871bf834c90c29ba2a2d4049811843514621dccb9ddc`.
They do not run or rewrite the A01, A02 or A03 reference programs.

## Verification completed

- All 133 non-ignored Rust tests pass. The private 72-frame native canary is a
  separately invoked ignored test.
- The strict historical snapshot, Plan2 through Plan6 and receipt hash test
  passes without changed fixture bytes.
- Production decoding matches the independent A03 grayscale-alpha, indexed
  `tRNS` and RGB `tRNS` facts.
- Production mapping and alpha arithmetic match every BGRA byte in all four A03
  pure canvases. The corrected high-scale crop-edge case passes.
- Tests cover hidden RGB, zero and partial alpha, masks, opacity, track order,
  contain bars, signed clipping, cropped holes, permits and cancellation.
- A sole alpha clip without placement, motion or mask normalizes to canvas
  placement and Plan7.
- An unused transparent lineage ancestor retains the opaque Plan3 selector.
- Forged alpha facts, policy and per-image evidence fail central validation.
- A public Plan7 export passes output verification and completed replay.
- Recovery reclaims a valid retired Plan7 stage and retains a self-consistent
  stage whose alpha evidence is missing.
- The allocation-free native pixel-buffer scan accepts alpha 255 and rejects a
  non-opaque decoded output sample.
- The isolated native canary matches all 72 borrowed pre-handoff BGRA frame
  hashes from `reference-summary-a02.json`, SHA-256
  `e39a9b8c87a8a57260261cb304173db79110e7cead8e565c6eafe72ec8f6765a`.
- The canary then encodes NativeColorMasterV1 and passes public verification
  and completed replay. Its test executable hash is
  `6311fb53655cce8429d34ee718cb347a25fff41c9b08dae2c083aa99ca8365de`.
- The instrumented plan, artifact receipt and verification IDs are respectively
  `1e5012eef0a5b57a5d0609f7f810679b28b782c0b7f15af70555614e59b3f220`,
  `0b4cdfe5c3cc612d55b07d1ef33b010f0c07f2474d5c07c6d4743cc5c19c9074`
  and `bb38df8e485c59eae3f5ea8e1eed962706f288a11a928b87846bdf411e0938a1`.

Formatting, Clippy with warnings denied and the release build pass.

## Proof boundary

A16 remains the accepted bounded mask, mastering and publication result. This
unit does not change its sources, outputs, receipts or evidence.

Transparent alpha is implemented and pure-pixel verified. The instrumented
72-frame movie-plus-PNG pre-encode comparison passes. The ordinary production
CLI export remains pending. Native ROI comparison, clock and EOF manifests,
exact PCM24, lifecycle cancellation and negative controls remain root-owned
proof work.

This implementation establishes no H.264 fidelity, managed color, process peak
memory, playback, hearing, creative acceptance or complete-film result.
