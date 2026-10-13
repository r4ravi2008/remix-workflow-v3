# Implementation review A15

## Result

Accept the current schema-6 masks implementation as a code-only unit.
No identified P1 or P2 defect remains in the reviewed source or contract.

This does not accept the complete bounded masks behavior unit.
No mask-capable native export or independent decoded-output proof exists yet.
The review does not accept native mask output, playback, hearing, creative quality, or the full film.

No cross-family reviewer was available.

## Findings

P1: none.

P2: none after the reviewed repairs.

## Closed findings

### Capability discovery now reports the compiled boundary

The public `discover` inventory now includes schema 6 in plan and native-export scopes.
It reports `native_picture_masks` as implemented and code-unit verified.
The same entry states that native exact-output proof remains pending.

Color and text remain separate under `native_color_text: Planned`.
The inventory no longer conflates compiled masks with those unimplemented capabilities.

The reviewed CLI source SHA-256 is `1e774fc13cfaa5e6d4b64c12b4adfa13bc8eeb67789f706c9d80f4aa99c2c1a8`.

The producer identity itself uses the corrected backend label.
`BuildIdentity.native_backend` names `objc2 AVFoundation bindings 0.3.2` and the AVFoundation bundle.
Historical stored backend strings remain byte-compatible.

### Proof policy now separates pure pixels from native decoded output

The policy now limits exact pre-encode BGRA equality to 12 independent 8-by-8 pure frames.
The future 72-frame native proof compares decoded full frames and declared ROIs.
It makes no byte-exact claim for unavailable raw compositor buffers.

The direct native worker test separately proves hidden-source execution and source-PTS rejection.
Pure composition tests prove that an absent raster leaves lower pixels unchanged.
The future native artifact must verify the combined hidden-region result.

The reviewed design SHA-256 is `878a91bd25c80be3335d040f12f0e92393bbcda2fe7050548d5ace002b0d70a1`.
The reviewed policy SHA-256 is `ba5f639c4c2c94f1cc307057bf99758bfcedb8deee61181d7da46fc1182f736f`.

## Model, serialization, and plan authority

`VideoClip.mask` and `VideoUse.mask` are appended optional fields.
Absent values omit from JSON.
Snapshot schema remains 1, Plan schema advances to 6 only when a mask is authored, and ArtifactReceipt remains schema 2.

The shared private curve grammar preserves its crate-root public reexports.
One-key, one-frame, constant, step, linear, and final-hold programs remain valid.
Mask progress accepts finite values in `[0,1]` and quantizes once to checked Q16.

Every authored mask selects schema 6, including constant masks.
Unmasked uses in a schema-6 plan receive the existing normalized placement or motion form.
Plans without masks keep the prior schema selector.

Central validation rebuilds Snapshot 1 before preflight or worker execution.
It recompiles masks and motion from the authored timeline.
It compares track and clip order, placement or motion, masks, framing, ranges, ordinals, cadence, and indexed source PTS.

Schemas 2 through 5 reject authored or planned masks.
Schema 6 requires at least one authored mask.
Plan uses remain one-to-one and ordered with timeline clips.

The eight legacy fixtures reserialize to their exact existing bytes and hashes.
They include both original Snapshot 1 forms, placement and motion snapshots, Plans 2 through 5, and Receipt 2.

## Coordinates, visibility, and pixels

`Mapping` derives one signed, unclipped `PictureWindow` from the fitted retained source content.
It intersects that content with the destination before canvas clipping.
The half-open pixel-center rule matches the selected design.

Canvas clipping changes visible bounds without changing the mask origin.
Contain bars have no layer raster and reveal earlier content.
Crop, fit, placement, and motion resolve before mask coverage.

Mask coverage uses checked `i128` arithmetic.
Layer opacity and mask coverage combine once with the specified Q16 rounding.
The implementation applies inversion before the final weight calculation.

`effective_bounds` binary-searches the monotone final nonzero-weight interval.
It handles both axes and both inversion directions.
Positive mask and opacity factors that round to zero contribute no coverage.

`evaluate_layer` is the single geometry and visibility authority.
Preflight, workers, and compositor response checks all use it.
Blend recomputes per-pixel coverage from the checked scalar observation.

Opaque input validation runs before an empty raster can return.
All output alpha remains 255.
The mask does not become source alpha or a separately allocated coverage plane.

## Worker ownership and source authority

The runtime retains one worker for each nonempty picture track, with a maximum of four.
Request, response, and composed-frame channels retain capacity one.

A worker receives its timeline-frame request before selecting a clip or decoding a PNG.
The compositor consumes every current response before sending its canvas.
It requests the next frame only after that send succeeds.

Movie source PTS remains authoritative from the immutable measured index.
The worker checks every decoded sample before selecting the requested ordinal.
The compositor rechecks clip, asset, ordinal, PTS, placement, mask, picture window, and effective bounds.

An active fully hidden clip remains a `Source` decision.
The movie worker still decodes and copies its source pixels.
It returns the actual held ordinal and PTS, but no raster.

The private H.264 test consumes held sample 1 from exact fixture bytes.
The fixture SHA-256 is `097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`.
Its sidecar SHA-256 is `761b3a18c19699bd646e8f70c602a706246887b7f9242f18f93b06a76f6e64db`.

The valid path reports the indexed PTS and no raster.
An injected sample-1 PTS change fails at the native reader comparison.

That private test does not itself compose the hidden H.264 layer over a visible PNG.
The pure pixel fixture proves the no-raster blend result separately.
The pending native output fixture must include the declared hidden overlay and lower-layer comparison.
This is an acceptance-evidence gap, not evidence of incorrect runtime behavior.

Native objects remain inside the AVFoundation completion operation.
Only owned Rust pixels, rasters, permits, and scalar observations cross product channels.
The `FnOnce` operation guard prevents duplicate callback execution.

## Admission, cancellation, and shutdown

Schema-6 preflight evaluates each active use on each timeline frame.
Coverage uses final effective raster bounds, including final-weight rounding to zero.
Fully hidden active sources remain charged.

Admission includes active source payloads, effective rasters, three canvases, and the global serialized PNG allowance.
PNG decode begins only after the clip-start request.
The shared mutex prevents overlapping PNG temporary allocations.

A PNG drops its final cached pixels and source permit before its last response becomes observable.
A movie drops copied source pixels and their permit before each response.
The bounded channel schedule therefore supports the calculated cross-frame high-water bound.

The boxed `LayerFrame` adds only bounded scalar metadata for at most four capacity-one response channels.
That allocation is outside the declared logical pixel-payload scope.
The product makes no total process-memory or native-memory claim.

Mask normalization, preflight, source pulls, raster rows, blend rows, channel waits, and PNG-lock waits check cancellation.
Worker teardown stops the shared signal, closes both port directions, and joins every Rust worker.
Promotion retains the existing cancellation and epoch fences.

No new mask-specific cancellation path bypasses the accepted A14 lifecycle.
The pending proof must still cancel an active schema-6 export through the public operation.

## Pure evidence and provenance

The independent evaluation fixture SHA-256 is `ceceb70b7b6d233399797cc374d60a6c77d3c14796df8b6f61b6cbca3aacea4d`.
It covers 10 mask cases and 29 evaluated frames.
It includes both axes, inversion, signed origins, clipping directions, one-pixel windows, and final-weight boundaries.

The independent pixel fixture SHA-256 is `fe85339abe0d8e769214a029460668cbae348c1b7d1f90348ddaf6988378f370`.
It contains 12 exact 8-by-8 BGRA frames across three tracks and six clips.
It covers contain, cover, stretch, crop, movement, resizing, sparse spans, overlap, opacity, and opaque alpha.

The separate reference script SHA-256 is `db27db073214c67d8e62ef8879e9bfc2d79a052f64904148632cced6e7b7e0d6`.
Its saved report SHA-256 is `b04754dfcaf850005d4519104974b4bdaabba1e37d77e89c637884a00f546cae`.

The report records that its author read the selected design, proof policy, and prior motion reference.
It records no product mask implementation, candidate mask draft, media binary, Pillow, GPU, or Resolve use.
The fixtures and reference predate the reviewed product mask source by their saved file times.

These facts support independent pure arithmetic provenance.
They do not establish blind or cross-family review.
They also do not establish native output behavior.

`masks-proof-inputs-a01.json` rehashes the retained A14 source and audio inventory.
Its claims correctly set new capability proof, new media, watched, heard, and creative acceptance to false.

## Validation

I independently ran these current-source checks:

- `cargo test --workspace`: 87 tests passed.
- `cargo fmt --all -- --check`: passed.
- `cargo clippy --workspace --all-targets -- -D warnings`: passed.

The saved post-box test log also records 87 passing tests.
Its current SHA-256 is `80b3e82d33624951a72b357816f75feaffd25c8faa0ab72b4624acfe24fcf727`.
The saved current Clippy log SHA-256 is `e59fca529a92d97cee4b1d001ca37e2f424078ac221a2313038119c4a024a1ec`.

## Remaining acceptance gates

The frozen producer and actual mask output do not exist yet.
Complete acceptance still requires these saved checks:

1. Freeze a fresh mask-capable producer and bind its full source manifest and corrected capability inventory.
2. Export fresh synthetic-offset and canonical 24-bit audio variants under Plan 6.
3. Bind every source byte, measurement, selected ordinal, source PTS, revision, plan, receipt, output, and product reverify.
4. Observe two simultaneous movie readers, both PNGs, motion, signed clipping, sparse intervals, both axes, inversion, and fully hidden sources.
5. Compare all decoded frames and predeclared nonempty ROIs against separate-code references at 34 dB or exact identity.
6. Record empty ROIs as empty, without a metric or pass claim.
7. Verify exact output PTS with epoch zero, video EOF, audio chunk continuity, audio epochs, sample counts, and audio EOF.
8. Compare synthetic `[8191,152191)` and canonical `[0,144000)` source intervals at the declared channel-cosine threshold.
9. Run deliberate source, receipt, mask, and clock corruptions against the final independent helpers.
10. Exercise active public cancellation and preserve the exact cleanup actor and attempt classification.
11. Reopen historical schemas 2 through 5 without changing their receipt or output identities.

Pure exact BGRA covers the 12-frame arithmetic fixture only.
Decoded H.264 evidence must remain a separate lossy-output claim.

This unit remains bounded to analytic axis reveals over opaque coded sample values.
It excludes rectangles, feathering, paths, bitmap or movie masks, tracking, Boolean masks, alpha inputs, color management, and text.
