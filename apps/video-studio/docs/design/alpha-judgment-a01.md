# Transparent PNG design judgment A01

## Result

Use Candidate A as the whole-shape base.

Candidate A fits the current editor architecture and preserves existing native ownership. Its pixel model is exact and reviewable. Its schema transition also preserves opaque projects.

Graft Candidate B's single per-plan alpha policy and one per-asset alpha evidence binding. Do not copy B's codec registry, reader redesign, source-response shape, or alpha-bounds optimization.

A corrected synthesis can proceed autonomously. The synthesis must apply the mandatory repairs in this judgment before implementation.

This judgment accepts a design direction only. No transparent-PNG runtime or native output proof exists yet.

## Reviewed inputs

The review covered these frozen documents end to end:

- `alpha-task-a01.md`
- `alpha-grounding-a01.md`
- `alpha-candidate-a.md`, SHA-256 `3dcf2065592462d8e9ea6b5e56af49d478212f0b5a1528fb421b074e2a386c7e`
- `alpha-candidate-b-a02.md`, SHA-256 `d0f8621381332ab7007a3b7647e71d5eaaea0c0f6f3a88951ab52bc73948baff`

The review also checked the current editor APIs and relevant implementation seams. Those checks covered model, plan, project, exports, image decoding, pixels, composition, layers, movie, media, and motion.

I scored both candidates before reading `alpha-parent-scores-a01.md`. I read the parent scores only after fixing my independent scores.

This was a same-model review. Candidate A disclosed one sibling `rg` line after selecting its shape. Therefore, this review is neither blind nor cross-family.

## Scores

### Independent scores before parent-score review

| Criterion | Candidate A | Candidate B |
|---|---:|---:|
| Caller depth | 5 | 4 |
| Pixel contract | 5 | 4 |
| Bounded ownership | 4 | 3 |
| Durable compatibility | 5 | 2 |
| Verifiable outcome | 5 | 4 |
| **Total** | **24/25** | **17/25** |

### Reconciled final scores

| Criterion | Candidate A | Candidate B |
|---|---:|---:|
| Caller depth | 4 | 4 |
| Pixel contract | 5 | 4 |
| Bounded ownership | 4 | 4 |
| Durable compatibility | 5 | 3 |
| Verifiable outcome | 4 | 4 |
| **Total** | **22/25** | **19/25** |

The parent scored Candidate A at 22 and Candidate B at 20. The selected base and main grafts agree.

I accepted two parent corrections to Candidate A's score. Its caller example uses a private error constructor. Its production pre-encode proof lacks a concrete observation seam.

I raised Candidate B's ownership score after checking its full response lifetime. Its acknowledgement is coherent because its `Arc` source bytes cross the response boundary.

I did not raise Candidate B's ownership score to five. Its source-response and reader shape replace a proven boundary without a need from this unit.

I raised Candidate B's compatibility score to three. Its Plan 7 isolation is sound, but its codec restriction would reject verified existing sources.

## Criterion assessment

### 1. Caller depth

Both candidates retain the existing five-operation `Project` workflow. Neither introduces a public alpha executor or caller-managed decode pipeline.

Candidate A has the cleaner public shape. The caller imports a PNG normally, then commits, prepares, exports, and verifies.

Candidate A's example does not compile for an external caller. `StudioError::new` is crate-private.

The synthesis must remove the caller-side alpha-kind branch. `Project` validation must reject invalid media through its existing public operations.

Candidate B also keeps alpha discovery inside import and prepare. Its public workflow is acceptable.

Candidate B adds internal registries and reader concepts beyond the feature boundary. Those additions increase implementation depth without improving the caller contract.

### 2. Pixel contract

Candidate A defines the stronger pixel contract.

The source image remains straight RGBA8. The decoder hashes those exact bytes before any channel swap or premultiplication.

The alpha-aware raster stores premultiplied BGRA UNORM16 plus A16. This representation retains hidden-color behavior and prevents repeated lossy 8-bit premultiplication.

The required conversion is:

```text
C16 = C8 * 257
A16 = A8 * 257
P16 = round_nearest_away(C16 * A16 / 65535)
```

The current geometry evaluator remains authoritative. It computes source coordinates in binary64 and then quantizes fractions to Q16.

The alpha path uses Q32 bilinear weights. Each sampled premultiplied channel and alpha uses one declared rounding operation.

Layer opacity and mask weight combine in Q16:

```text
Q = round_nearest_away(opacity_q16 * mask_q16 / 65536)
```

The opaque canvas blend uses one declared final division:

```text
D = 65535 * 65536
out8 = round_nearest_away(
  (255 * P16 * Q + lower8 * (D - A16 * Q)) / D
)
```

Every resulting canvas pixel remains alpha 255. Native encoding still receives opaque BGRA.

Candidate A also preserves the existing opaque 8-bit path. That avoids silent pixel changes in old projects.

Candidate B's direct sampler is mathematically plausible. It avoids a separate alpha raster and keeps hidden RGB until sampling.

However, Candidate B's alpha classification is weaker. `Opaque` is impossible in canonical new metadata because opaque inputs must omit alpha metadata.

Candidate B's `Sparse` name also covers uniform partial alpha. That name does not describe the encoded state.

Candidate B's proposed nonzero bounds need an exact transformed bilinear-support rule. Without that rule, bounds can incorrectly remove a contributing edge pixel.

Do not use alpha nonzero bounds for preflight coverage in the first unit. Conservative whole-placement reasoning is sufficient.

### 3. Bounded ownership

Candidate A matches the current four-worker architecture.

The current worker requests a timeline frame before it opens or decodes a new clip. PNG work cannot begin early across a gap response.

Candidate A copies the source into an owned alpha raster. Therefore, source pixels do not cross the response boundary.

The source cache and its permit may retire after the final raster is completely sampled. They may retire before the response send.

No acknowledgement channel is required for Candidate A's copied-raster design.

The alpha raster must own a separate logical permit. The worker must acquire its full 8-bytes-per-pixel charge before allocation.

The implementation must use checked `width * height * 8` arithmetic. It must also assert the alpha sample's expected eight-byte layout.

That raster permit must cross the capacity-one response channel. It retires only after the compositor consumes the raster.

The existing request/response barrier then bounds one raster per track. It also prevents cross-frame raster accumulation.

The compositor must retain the existing capacity-one writer handoff. It must consume every raster before requesting the next frame.

The global PNG temporary allowance remains required. PNG decoding stays serialized by the existing PNG lock.

The three opaque canvas reservations remain required. Their permits must continue through writer consumption.

All estimates are logical reservations. They do not prove native framework or process peak memory.

Candidate B's acknowledgement is necessary for its own design. Its `Arc` source pixels cross each response, so the worker needs explicit retirement feedback.

That acknowledgement does not belong in Candidate A. Adding it would complicate a boundary that already copies and owns the raster.

Both designs preserve cancellation checks in decode, sampling, blending, channel waits, writer waits, and finalization.

Neither design may move AVFoundation objects out of their completion-callback scope. The existing callback-confined native operation remains authoritative.

### 4. Durable compatibility

Candidate A provides the better migration shape.

Opaque images retain absent alpha metadata. Existing descriptor, plan, receipt, and store document bytes remain unchanged.

Their backend string and opaque pixel arithmetic also remain unchanged.

Plan schema 7 applies only when a used image has non-opaque alpha metadata. Unused transparent assets do not promote a plan.

Plan 7 must compose placement, motion, masks, and alpha. It must not reinterpret schemas 2 through 6.

Receipt schema remains profile-dependent. H.264 keeps Receipt 2, Native Color Master keeps Receipt 3, and storage remains schema 4.

The new schema must be added to every current allowlist and movie execution gate. Existing schema-specific validation must remain exact.

Candidate A duplicates alpha identity on each `VideoUse`. That duplication is unnecessary and risks disagreement between repeated records.

Use Candidate B's single top-level math policy and per-asset evidence shape instead. Keep Candidate A's versioned source metadata.

The selected persisted and planned shape is:

```rust
pub struct ImageAlphaV1 {
    pub schema: u32,                 // exactly 1
    pub alpha_sha256: ContentHash,   // width * height alpha bytes
    pub minimum: u8,
    pub maximum: u8,
    pub nonzero_pixels: u64,
    pub nonopaque_pixels: u64,
}

pub enum AlphaPolicyId {
    StraightRgbaPremulUnorm16V1,
}

pub struct ExportPlan {
    // existing fields
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub alpha_policy: Option<AlphaPolicyId>,
}

pub struct ImageDecodeEvidence {
    // existing fields
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_alpha_id: Option<ContentHash>,
}
```

`MediaDescriptor::Image` gets an optional `ImageAlphaV1`. Opaque images must serialize `None` exactly as before.

`source_alpha_id` identifies one canonical document. That document binds asset hash, straight RGBA hash, and `ImageAlphaV1`.

Plan 7 contains exactly one image evidence entry per used image asset. Entries use deterministic asset-hash order.

No alpha field belongs on `VideoUse`. The existing ordered use record already binds the asset, geometry, motion, mask, and source selection.

Central plan validation must recompute each alpha identity from the source closure. Execution must reject any mismatch before worker startup.

Fresh decode must reproduce the same straight RGBA and alpha facts. Replay must enforce the same closure and plan rules.

Candidate B's `NativeCodecRegistry` is outside this task. Current `SourceDecodeEvidence` has no codec field.

The editor already uses verified AV1 movie sources in historical mask work. An H.264-only Plan 7 whitelist would recreate a codec limitation.

Keep the current verified native decode authority. Do not redesign the reader or add an unrelated codec registry.

### 5. Verifiable outcome

Candidate A proposes the stronger proof matrix. It separates pure pixel proof from decoded native output proof.

Its wording still needs one correction. The public movie pipeline does not expose raw compositor frames.

The implementation must add a private proof seam. A cfg(test) or private integration hook may hash or compare the compositor buffer before native handoff.

The seam must not create a public executor. It must not add dense persisted frame traces or alter production receipts.

The exact pure proof must cover independently authored vectors for:

- RGBA, grayscale-alpha, indexed tRNS, and RGB tRNS decoding
- hidden RGB under zero and partial alpha
- edge sampling and transparent contain bars
- Q16 opacity and mask boundaries
- bilinear rounding ties
- multiple transparent layers
- fully transparent active sources above lower layers
- effective final weight that rounds to zero
- crops whose entire sampled support falls inside transparent holes

The pure reference must not import production sampling, blending, alpha, or rounding helpers.

The native proof must use a fresh mask-capable and alpha-capable producer. It must not reuse C12 or A11 as the alpha producer.

The fixture must include a fresh transparent PNG measurement. It must retain exact source bytes and straight RGBA evidence.

The fixture must place one freshly re-probed movie and one transparent PNG on separate tracks.

It must also include placement, motion, mask, opacity, overlap, and sparse alpha.

Its timeline must include frames before, during, and after the alpha overlay.

The fixture must include both an actively transparent source and a lower visible layer. This case proves observation without false coverage.

Every native output frame requires decoded PTS, epoch, EOF, full-frame comparison, and predeclared ROI checks.

The native observer must have separately authored source and a separately hashed executable. Shared AVFoundation use must remain disclosed.

The observer must bind all source movie PTS. PNG observations remain ordinal zero with no invented source PTS.

The output observer must confirm alpha 255 for every decoded pixel.

The master path must preserve NativeColorMasterV1 format checks, PCM24 bytes, source clocks, output clocks, EOF, and bounded chunks.

The canonical audio selection is the exact 144,000-frame unity-gain, zero-pan prefix.

The H.264 export remains a compatibility smoke test. Its known alpha-edge failures must remain preserved and must not weaken the 34 dB policy.

Negative controls must cover alpha bytes, alpha metadata, policy, evidence identity, geometry, motion, mask, clocks, PCM, producer, and output bytes.

Each negative control must begin from the bound passing baseline and produce its predeclared specific false result.

The lifecycle proof must include active public cancellation. It must show no completed receipt and owned-stage cleanup by the actual actor.

Legacy readback must preserve all eleven `legacy_hashes` fixtures. It must also preserve Receipt 3 and store schema 4 readbacks.

No proof may claim watching, hearing, creative acceptance, managed-color equivalence, process peak memory, power-loss durability, or full-film completion.

## Selected contract

### Import and metadata

The existing strict PNG decoder remains the only PNG byte authority.

It must continue to enforce PNG boundaries, chunk CRCs, APNG rejection, bit-depth rules, bounded dimensions, and exact decoded length.

The decoder hashes straight RGBA before mutation. It separately hashes the alpha plane for non-opaque images.

Opaque inputs retain the current descriptor and backend bytes. Non-opaque inputs add `ImageAlphaV1` with schema 1.

Non-opaque inputs use backend text `Rust png 0.17.16 / straight RGBA8 alpha v1`.

The alpha hash covers exactly one row-major alpha byte per decoded pixel. Counts, extrema, and dimensions must agree with that byte sequence.

`ImageAlphaV1` is present only when at least one alpha byte is below 255. A fully transparent image remains valid measured input.

The alpha descriptor is immutable measurement evidence. Refresh requires the existing exact prior-measurement guard.

### Planning

Plan schema 7 is selected when at least one used image has `ImageAlphaV1`.

Plan 7 carries one `AlphaPolicyId`. It carries one alpha identity through each unique image evidence entry.

The compiler derives all alpha fields. Callers do not supply alpha policy, alpha facts, or source alpha identities.

Central validation enforces normalized placement, motion, mask, source order, image cadence, and alpha evidence before execution.

Schemas 2 through 6 reject alpha fields. Their canonical bytes and behavior remain unchanged.

### Execution

Opaque inputs keep `Raster::Bgra8` and the existing blend path.

Non-opaque PNG inputs produce a private premultiplied UNORM16 alpha raster. The raster contains BGRA16 and A16 samples.

The worker owns source pixels only while creating that raster. The response owns the raster and its permit.

The compositor evaluates placement, motion, mask, opacity, and source alpha once per output sample.

The compositor blends bottom-to-top into the existing opaque canvas. It does not mutate lower layers for zero effective weight.

The compositor checks actual coverage after all tracks contribute. A frame with no positive effective contribution fails before append or publication.

The native writer may already exist when runtime coverage fails. Documentation must not claim that no writer object started.

The failure path must retain the existing stage, fencing, cancellation, and publication rules.

### Coverage and observations

Timeline activation and source observation are independent from visual contribution.

An active image always records its selected ordinal. A PNG never invents a movie PTS.

A fully transparent active PNG still produces a source observation. It does not satisfy visual coverage.

Preflight may reject a sole image whose descriptor proves `nonzero_pixels == 0`.

Other alpha coverage remains conservative before execution. The runtime sampled alpha, mask, and opacity decide actual contribution.

Do not prune using source-alpha bounds in this unit. That optimization needs a separate exact bilinear-support contract.

## Required implementation sequence

1. Add versioned non-opaque alpha metadata while preserving opaque descriptor bytes.

2. Add the single Plan 7 alpha policy and unique per-asset alpha identities.

3. Extend central validation and every schema allowlist before enabling execution.

4. Add pure pixel types and independently authored arithmetic vectors.

5. Add logical permits before allocating 8-byte alpha rasters.

6. Preserve the existing worker barriers, PNG lock, and callback-confined native ownership.

7. Add exact runtime effective-coverage checks before frame append.

8. Add the private pre-encode proof seam without changing public APIs or receipts.

9. Freeze a fresh producer only after tests, formatting, Clippy, and legacy byte checks pass.

10. Run the bounded native master, H.264 smoke, cancellation, replay, and negative controls.

11. Keep technical acceptance separate from playback, hearing, creative review, and full-film completion.

## Explicit grafts from Candidate B

Graft the single top-level `AlphaPolicyId`. It makes the arithmetic contract explicit without repeating it per use.

Graft one alpha binding per unique image evidence entry. This avoids duplicated lineage fields across repeated `VideoUse` records.

Graft B's explicit distinction between source-byte ownership and response acknowledgement. Apply the distinction to documentation only.

Candidate A copies the raster, so it does not need B's acknowledgement channel.

Graft B's emphasis on hidden-color controls and exact negative mutations. Keep Candidate A's UNORM16 representation and formulas.

## Rejected choices

Reject Candidate A's per-`VideoUse` alpha identity. It duplicates evidence already bound through the source closure and image evidence.

Reject Candidate B's native codec registry. It broadens scope and would exclude verified existing sources.

Reject Candidate B's H.264-only Plan 7 admission. Alpha composition must not reinterpret unrelated movie support.

Reject Candidate B's reader and callback redesign. The current completion-callback native ownership is already proven.

Reject Candidate B's `Arc` source-response and acknowledgement shape for the selected implementation. It adds a lifetime that copying avoids.

Reject Candidate B's `Opaque` alpha class. Opaque images must omit alpha metadata to preserve old bytes.

Reject Candidate B's `Sparse` label. It conflates spatial sparsity with uniform partial transparency.

Reject source-alpha bounds as a first-unit coverage optimization. The draft does not define safe bilinear edge expansion.

Reject any claim that an A11 alpha fixture already exists. The alpha unit requires a fresh fixture and producer.

Reject public raw-frame APIs, persisted dense traces, and caller-selected alpha math.

## Scope boundary

This judgment selects a corrected architecture for transparent PNG composition.

It does not accept implementation, native output, publication, full-film rendering, watching, hearing, or creative quality.

The current C12/A11 runtime remains the accepted pre-alpha baseline. A new producer and bounded proof are mandatory for alpha acceptance.
