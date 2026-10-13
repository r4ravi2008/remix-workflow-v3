# Transparent picture assets task A01

The next unit adds intrinsic transparency to static PNG picture assets through the existing Rust editor and direct CLI.
It prepares the general editor for later graphics and native text. It does not add lyrics to the Panja film.

The preceding mastering and publication source stays frozen until the A11 checkpoint is saved.
Candidate drafting is authorized. Runtime implementation follows completed parent and independent design judgment.
No human design checkpoint was requested.

## Caller behavior

A caller imports a transparent eight-bit PNG through the existing asset import path.
The caller places that asset on a picture track using existing crop, fit, destination, motion, opacity and mask operations.
The PNG reveals lower-track pixels wherever its own alpha is zero or partial.
The caller prepares and exports through the existing Project operations.
The current output profiles receive a flattened opaque canvas.

Opaque projects keep their exact historical document bytes, schema selection and pixel arithmetic.
Transparent movie output, animated PNG, sixteen-bit PNG, managed color and broader movie-alpha import remain separate work.
The general editor and complete Panja film remain the overall objective.

## Grounding

Read the complete `alpha-grounding-a01.md` before drafting.
Its SHA-256 is `8f9e1e9bfec40dfc2108ab135a25abbfe9ee9d3923efc0de80aedc15c454e554`.
Root read all 501 lines. The final grounding questions belong to candidate design; they do not require prior human answers.

The root also checked the current [PNG alpha specification](https://www.w3.org/TR/png/#6AlphaRep).
PNG stores unassociated color samples. Alpha measures a linear opacity fraction.
The chosen unit must explicitly preserve the existing `source-sample-values-unmanaged` limitation.

## Required contract

- Keep straight source RGBA hashing before any premultiplication or channel-order conversion.
- Define source, sampled raster and opaque canvas pixel representations at their owning boundaries.
- Define precision, interpolation and every rounding point before implementation.
- Filter premultiplied color contributions and coverage to prevent hidden-color fringes.
- Apply intrinsic source alpha, clip opacity and mask coverage coherently to both color contribution and coverage.
- Preserve existing crop taps, pixel-center sampling, signed clipping, contain bars and bottom-to-top order.
- Preserve truthful source observations for transparent active images: ordinal zero, no invented PTS.
- Keep movie source ordinals and PTS checks when other layers obscure their picture.
- Distinguish active clips, geometric bounds and actual contributing alpha coverage.
- Reject an accepted output that falsely satisfies the required temporal coverage using transparent pixels alone.
- Bind reproducible measured alpha facts to source bytes and normalized execution.
- Reject forged alpha descriptors, normalized uses, schema declarations and changed PNG bytes centrally.
- Preserve all historical Snapshot1, Plan2..6, Receipt2/3 and store4 data.
- Preserve the four-worker, bounded-channel and native callback ownership boundaries.
- Account for every added pixel buffer, alpha map or intermediate representation in logical admission and live permits.
- Keep row-level cancellation and exact export claim ownership through failures.
- Use native Rust/AVFoundation output without renderer subprocesses or FFmpeg/libav.

The candidates must resolve precise preflight and runtime coverage responsibility.
They must explain sparse alpha holes, transformed crops and fully transparent sources.
An optimization must never turn a structurally active source into a gap.

## Evidence

Use independent exact integer or rational pixel vectors.
Include hidden-color fringes, zero alpha, independent opacity/mask weights, opaque equivalence, contain bars, crop, clipping, order and fractional mask edges.
Exercise RGBA, grayscale-alpha, indexed transparency and RGB `tRNS` expansion.
Preserve strict PNG terminal-boundary and CRC validation.

Prepare an actual native fixture with a freshly measured movie source and transparent PNG on separate tracks.
Include frames before, during and after a sparse overlay, plus motion, crop, mask and canonical-clock audio.
Use the already qualified NativeColorMasterV1 profile for the strict region proof.
Do not imply that the preserved H.264 failures pass that same region gate.
Keep exact source intervals, every output frame, every required nonempty region, PCM codes, clocks, format and EOF evidence.
Explicitly observe opaque output alpha rather than inferring it from the codec name.

The independent observer uses separate code and executable identity while sharing AVFoundation.
Technical pixel proof remains separate from watching, hearing, managed-color acceptance and creative approval.
Declare meaningful negative controls before execution and require a passing baseline followed by the intended specific false result.

## Design outputs

Produce two structurally distinct complete candidates in separate files.
Each candidate starts with caller usage, then types, signatures, module ownership and pseudocode.
Include rationale, rejected alternatives, compatibility, admission, cancellation and the decisive proof plan.
Do not read the sibling candidate before delivering your first complete draft.
Do not implement runtime code or change existing metadata, media or proof records.

Root reads both complete candidates and scores them before synthesis.
The independent judge reviews both complete candidates after delivery.
Available reviewers are from the same model family; this is not a blind or cross-family comparison.

## Rubric

Score each criterion from 0 to 5 using concrete evidence.

1. Caller depth: existing Project operations hide representation and execution complexity.
2. Pixel contract: interpolation, alpha association, rounding and coverage have exact reproducible semantics.
3. Bounded ownership: buffers, caches, permits, channels and native lifetimes remain explicit.
4. Durable compatibility: old bytes and opaque behavior remain exact; new plans reject inconsistent data.
5. Verifiable outcome: useful source-bound native composition and independent controls prove the stated contract.
