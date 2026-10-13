# Alpha implementation review A01

Status: read-only review of the selected alpha implementation. No runtime, fixture,
proof-output, metadata, or historical document was changed. The review read the full
selected synthesis and judgment, then compared current editor sources with the preserved
A11 source archive and manifest.

## Result

### P1 — Plan7 is rejected by public verification and staging recovery

`Project::verify_export` still accepts only `plan.schema` values `2..=6` at
`apps/video-studio/crates/editor/src/exports.rs:758-761`. A valid alpha export uses
schema 7, so public receipt readback returns `plan_tampered` before source, receipt,
or decoded-output verification. The one-shot `export` path can publish before this
readback is attempted, which makes the failure especially misleading.

`Project::reconcile_export_staging` repeats the stale allowlist at
`apps/video-studio/crates/editor/src/exports.rs:1153-1163`. A stale schema 7 stage is
retained instead of reaching the existing plan validation and reclamation path. This
blocks the selected Plan7 recovery behavior.

The other dispatches I checked already include schema 7: plan replay and mapping
validation (`project.rs:307-318`, `plan.rs:568-601`), composition preflight
(`composition.rs:669`, `composition.rs:751-753`), native profile and writer selection
(`movie.rs:49-50`, `movie.rs:107-108`, `movie.rs:177-185`), and the layer executor.
The two `exports.rs` allowlists are therefore the remaining release blocker.

### P2 — Staging recovery should share central Plan7 evidence validation after P1 repair

After the allowlist is widened, `reconcile_export_staging` calls only
`validate_picture_mapping_cancellable` at `exports.rs:1163`. It does not call
`validate_decode_evidence`, which is the central check for one sorted image evidence
record per directly used asset and the recomputed `source_alpha_id`.

The stored plan hash prevents ordinary body edits. A self-consistent malformed plan
and stage could still reach recovery disposition without the same evidence check used
by `Project::verify_plan_sources`. This is a defense-in-depth gap in the recovery
entry point. Use the central source/evidence validator before accepting a schema 7
stage for recovery, while preserving the existing schema2–6 behavior.

## Verified implementation areas

- `image.rs` expands into straight RGBA8, hashes those bytes before BGRA conversion,
  hashes row-major alpha bytes, validates extrema and counts, and emits optional alpha
  metadata only when a byte is below 255. The opaque branch still performs the old
  channel swap and keeps the optional field absent.
- `model.rs` validates `ImageAlphaV1` coherence and validates alpha facts during
  snapshot validation. The descriptor remains the authority for source alpha.
- `alpha_picture.rs` keeps straight RGBA source pixels private, uses an eight-byte
  `PremulBgra16`, checks the 128 MiB raster bound before allocation, uses checked
  UNORM16/Q16/Q32 arithmetic, rejects premultiplied channels above coverage, and
  counts positive effective coverage before final byte rounding.
- `composition.rs` remains the geometry authority. The alpha sampler consumes its
  crop-clamped bilinear footprint, and the shared mapping preserves signed placement,
  contain bars, integer destination bounds, and the existing pixel-center geometry.
- `layers.rs` reserves the raster permit before alpha allocation. The PNG source cache
  and source permit retire after the last raster is sampled and before the copied
  response is sent. The raster and permit remain owned by the capacity-one response
  until the compositor consumes them. Movie AVFoundation readers, outputs, samples,
  and pixel buffers remain callback-confined; only owned Rust pixels and source PTS
  cross the worker boundary.
- The compositor consumes workers in timeline track order, blends bottom to top, and
  rejects a frame with zero positive contribution before handing it to the writer.
  A fully transparent active image remains a `Source` observation with `ZeroAlpha`.
  A crop that samples only an alpha hole reaches runtime coverage failure after the
  conservative prepare check.
- `plan.rs` selects schema 7 from directly used alpha images only. A single alpha image
  without author placement receives normalized canvas placement. An alpha ancestor that
  is only in `source_closure` does not promote an opaque schema 3 plan. Schema 7 image
  evidence is a sorted set by asset hash; length and ordered asset equality reject
  duplicates, omissions, or reordering. Every alpha evidence record recomputes its
  source identity from the immutable descriptor.
- `movie.rs` deduplicates Plan7 image evidence by asset, re-decodes each selected image
  against the stored descriptor, and binds the decoder executable identity. Its output
  verifier scans every decoded video sample with `require_opaque_native`, checks every
  row alpha byte, and requires the expected frame count and completed reader status.
  This is the correct output-alpha check for the opaque native writer.
- `pixels.rs` checks native BGRA format, stride, bounded extent, read-only locking, and
  every output alpha byte without copying the decoded output frame.

## Schema and evidence audit

| Area | Current outcome |
| --- | --- |
| Plan compile and replay | Accepts 2..=7; selects 7 only for directly used alpha. |
| Central mapping/evidence validation | Accepts 2..=7; rejects Plan7 policy, identity, order, count, and direct-alpha mismatches. |
| Image import and decode | Straight RGBA and alpha facts are recomputed from immutable PNG bytes. |
| Movie input proof | Existing measured native source path remains authoritative; no H.264-only restriction was added. |
| Layer dispatch and preflight | 4..=7 uses bounded layered execution; Plan7 evaluates every local frame. |
| Writer/profile dispatch | 4..=7 uses the existing native layered writer path. |
| Public verification | **P1: stale 2..=6 allowlist.** |
| Staging recovery | **P1: stale 2..=6 allowlist; P2: no shared evidence validation after repair.** |
| Artifact receipt/output alpha | Receipt schemas remain profile-dependent; decoded output is checked opaque frame by frame. |

## A11 comparison and source drift

The preserved source archive is
`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/source-native-unit-a11.tar.gz`.
Its SHA-256 is
`271bf0fff3a289ea69e7ce2c9fb626944ac3b7fc89ce6ba3b434df008edd8c08`, with 139
manifest files. `alpha_picture.rs` did not exist in that archive.

The following hashes were captured at review start and again after the source review.
Only `alpha_picture.rs` and `image.rs` changed while this review was in progress.
The current after-review hashes are the hashes to use for any follow-up review.

| Current source | A11 archive hash | Before review | After review |
| --- | --- | --- | --- |
| `crates/editor/src/alpha_picture.rs` | absent | `a7b7d39ddbdb8ab0686e3eeffbb4d07f9cf6eb65cd7bf3a85d269122f147ce1d` | `3cbf31081a7cf0c72e71649592a4808445819b41cd58e0b24ef8c65067c381a5` |
| `crates/editor/src/composition.rs` | `ca59fcf528151df7c723208057827e1ec663d39979b0374ac526f25b82937eae` | `426322dd9a8188bd90c93e409373a739d52edeaac6c7eded4b0a8b01f1ff4810` | `426322dd9a8188bd90c93e409373a739d52edeaac6c7eded4b0a8b01f1ff4810` |
| `crates/editor/src/framing.rs` | `c4e6082146f276f6838af468240c8834e506aecb28cf0b01c2c9c3ac65009888` | `c4e6082146f276f6838af468240c8834e506aecb28cf0b01c2c9c3ac65009888` | `c4e6082146f276f6838af468240c8834e506aecb28cf0b01c2c9c3ac65009888` |
| `crates/editor/src/image.rs` | `85e8e369f2f6494e2b68b3d5a32cf23b70d1d5be89d8a27ebae3ff4822878e56` | `1b1358c31c305727e617cc267a82c064b43d4ce4dc84d23d3d7ef634465d1b1d` | `6acb1310003874d2233a885113649f34aef69c4af14694b5357d53884269eca2` |
| `crates/editor/src/layers.rs` | `16736bbb544f9a5618cf811bca5a922ff8e91f634caba3805a443bf3327edd08` | `9564e90b66ef53140531c8ea4f6a57383e1a8d2243d2be5486626e0ad26aa70a` | `9564e90b66ef53140531c8ea4f6a57383e1a8d2243d2be5486626e0ad26aa70a` |
| `crates/editor/src/mask.rs` | `a1cd2c87e15f806239172a63d398e7e692a5f8ca696818ed9190afc2beb8acaf` | `a1cd2c87e15f806239172a63d398e7e692a5f8ca696818ed9190afc2beb8acaf` | `a1cd2c87e15f806239172a63d398e7e692a5f8ca696818ed9190afc2beb8acaf` |
| `crates/editor/src/media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `crates/editor/src/model.rs` | `5687842cb458a81f569b5665466c962e932de54dc51def48edfacaa96e3c1f75` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `crates/editor/src/movie.rs` | `05eb47cd416f8486c55698c0513e9b3a479545d0d8d1a2408651f145631b9012` | `2ccd1408c3cbb061f004c37871730c5de55c5ed5f290c1db5602fb4d72ec8780` | `2ccd1408c3cbb061f004c37871730c5de55c5ed5f290c1db5602fb4d72ec8780` |
| `crates/editor/src/plan.rs` | `fb1e1857e38f04505e765c7545529221165cfede6c05d679ad4dedb635509fd0` | `af959648ae11e936bf80ce9a502eabbf50f2069f3a4ea6445930b8892aa0e1ba` | `af959648ae11e936bf80ce9a502eabbf50f2069f3a4ea6445930b8892aa0e1ba` |
| `crates/editor/src/project.rs` | `009c45a663997b5007e8594d9dc7a5766937913f014f5d5990555237353c563f` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `crates/editor/src/pixels.rs` | `021785727d1cb3d8aa0b5197b57634193385e372a4cecd604c44d71e2ebc70e9` | `9f2c1d86971d28ccbb89bb4678d2ea44cb8358e9d85e46451da4b7c7a2a02216` | `9f2c1d86971d28ccbb89bb4678d2ea44cb8358e9d85e46451da4b7c7a2a02216` |
| `crates/editor/src/lib.rs` | `74389b3212a0c5b7ac08564a11b96287338684007e7f328935dc23bf11d2566c` | `59e8107ac8e9afd11c551856e4cef606d5d85476d6d294455c498afda62a0b33` | `59e8107ac8e9afd11c551856e4cef606d5d85476d6d294455c498afda62a0b33` |

## Verification limits and coordination

I did not run Cargo, tests, native export, output decode, or the 72-frame observer.
The reported 131 passing tests and four independent A03 pixel canvases were treated as
A's report, not as independently rerun evidence. Ordinary native output, Plan7 receipt
readback, cancellation, staged recovery, and full-film acceptance remain unverified.
No creative, color-management, H.264 ROI, or audio acceptance claim follows from this
code review.

`alpha_picture.rs` and `image.rs` changed after the review began. Native_design_a owns
those edits. Please ask A to confirm these two files are frozen before closure; the
hash drift makes those sections unstable for a final judgment. The review findings
above are based on the after-review hashes.
