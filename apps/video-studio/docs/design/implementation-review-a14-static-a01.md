# Implementation review A14

## Result

The reviewed motion implementation has no identified P1 or P2 correctness defect.
Do not accept the complete bounded unit yet.
Independent native output proof, corrected canonical-audio proof, and active public cancellation proof remain pending.

This review is bound to frozen producer `video-studio-producer-release-a01`.
Its SHA-256 is `d8ae6b396206a2dc684183dbebb20fb410f6ecd48a84f0e26882ec5ea4be16e3`.
`build-a01.json` binds every reviewed Rust source, both motion fixtures, and `Cargo.lock`.
The current reviewed files match that manifest.

The saved A01 test log reports 80 passing tests.
The build record reports formatting and Clippy passed.
I inspected those records but did not independently rerun the complete suite.

No cross-family reviewer was available.
Candidate A read Candidate B before drafting, so the design process was not blind.

## Findings

P1: none.

P2: none.

The remaining items are required acceptance evidence, not confirmed implementation defects.

## Motion model and immutable plan

`PictureMotion` stores independent curves for x, y, width, height, and opacity.
The implementation accepts one-key, one-frame, constant, and no-visible-delta programs.
A nonempty declared motion selects plan schema 5, including a constant program.

Every curve starts at local frame zero and uses strictly increasing in-range keys.
Only nonfinal keys carry interpolation.
The final key holds through the remainder of the clip.

Linear interpolation uses one signed `i128` rational calculation.
It rounds once, with nearest half values away from zero.
Step interpolation holds the left key until the right key's frame.

Opacity is quantized once into a range-checked integer from 0 through 65,536.
Schema-5 execution interpolates that integer representation.
The serde boundary rejects out-of-range Q16 values.

The separately authored reference covers signed half ties, values beyond exact f64 integers, steps, final holds, constants, and one-frame clips.
Its saved report covers 14 cases and 54 evaluated frames.
The Rust suite also consumes its six-frame exact BGRA fixture.
That proof is pure pre-encode behavior, without native media or decoded movie output.

Snapshot schema remains 1.
Absent optional motion omits its field, which preserves historical snapshot bytes.
Plan schema 5 stores complete normalized curves without a dense per-frame pose table.

An animated schema-5 use has motion and no static placement.
A static schema-5 use has normalized placement and no motion.
Schemas 2 and 3 reject both fields, while schema 4 retains placement only.

Central validation rebuilds the snapshot and recompiles every planned picture use.
It compares ordered track and clip identity, normalized placement or motion, source ranges, ordinals, cadence, and indexed source PTS.
Motion never changes `presentation_ordinals`.

Movie source PTS remains authoritative from the measured source sample index.
Held PNGs retain ordinal zero without a movie source PTS.
Output video and audio retain their independent frame and sample clocks.

## Runtime pose, source, and PTS binding

Each worker resolves the planned pose only after receiving the requested timeline frame.
The worker returns owned raster bytes plus scalar source, PTS, and pose observations.

The compositor recomputes the expected use and resolved pose for the same frame.
It rejects a response with the wrong track, source ordinal, source PTS, or pose.
The compositor blends tracks in declared bottom-to-top order.

Coverage preflight evaluates every frame with the resolved pose.
It uses the visible fitted source rectangle after crop, destination, and canvas intersection.
Zero opacity, an off-canvas result, or a contain bar contributes no coverage.

Rasterization and blending use the same pure mapping functions as preflight.
The current independent BGRA fixture exercises overlaps, gaps, movement, resizing, and opacity.
It does not replace the pending whole-output native comparison.

## Admission and schedule

The reviewed schedule supports the conservative admission calculation.
A worker receives a frame request before selecting a new clip or decoding a PNG.

PNG decode reserves the cached source plus compressed bytes, a second source-sized decode allowance, and the configured 128 MiB allowance.
PNG decode remains serialized by the shared mutex.
The preflight includes the global maximum PNG temporary charge.

A held PNG releases its final cache and source permit before sending its final response.
A movie releases copied source pixels and their permit before sending each raster response.
The next same-track clip cannot open until the compositor requests its frame.

Capacity-one request and response channels prevent a worker from retaining another frame's raster.
The compositor consumes all current rasters before sending the composed canvas.
It requests the next timeline frame only after that send succeeds.
The three-canvas charge covers writer and compositor backpressure under this schedule.

Preflight sums all active source caches, source copies, dynamic rasters, and three canvases.
Runtime permits reserve the corresponding application-owned payloads before allocation.

The successful synthetic A01 export admitted 171,294,800 bytes.
Its live logical high-water mark was 169,724,767 bytes across four workers.
These figures exclude allocator capacity, framework buffers, encoder memory, and total process memory.

## Cancellation, shutdown, and native ownership

Preflight, frame resolution, raster rows, blend rows, channel waits, and PNG-lock waits check the shared export control.
The checks preserve the owned epoch and classify cancellation or fencing through the existing export lifecycle.

Failure teardown sets the stop signal, retires ports, cancels native readers, and joins every Rust worker.
Final promotion separately checks cancellation and the current epoch.
I found no path that can promote a cancelled or fenced attempt.

The public cancel request reaches this control through the existing renewal loop.
Its observation latency remains bounded by that loop and blocking native calls.
The code does not claim instantaneous interruption.

Each movie worker moves one `FnOnce` track operation into its native completion callback.
Reader, output, sample-buffer, and pixel-buffer objects stay within that operation.
Only copied Rust pixels, rasters, and scalar observations cross product channels.
The returned Rust request receiver does not transfer a native object.

The current tests exercise cancellation at preflight, raster, blend, lock, channel, and lease seams.
They do not prove an active public cancellation while a native export owns its epoch.
That product-level proof remains required.

## Compatibility and capability reporting

The legacy fixture reserializes actual Snapshot 1, Plan 2, Plan 3, Plan 4, and Receipt 2 records.
It checks their exact historical hashes.
Schema-5 support does not change ArtifactReceipt schema 2.

`PictureExecutionEvidence` remains fresh producer output.
Replay and reopening omit it.
It records preflight estimates and the live logical permit high-water, without claiming process memory.

The CLI inventory reports schema-5 motion as implemented code.
It explicitly separates exact-output proof from the compiled capability.
It still reports masks, color, and text as planned.

## Saved native evidence and remaining acceptance gates

The frozen producer created and replayed a 72-frame synthetic H.264/AAC artifact.
The exact output SHA-256 is `097dd9a1a59c02a8967db82463e8b43fc6ffc42a5294c997a77280967b1174df`.
The producer reports 72 decoded video frames and 144,000 decoded stereo PCM frames.
Its product verifier uses the same library, so this is not the required independent output proof.

The first canonical A01 prepare attempt stopped with `canonical_audio_mismatch`.
That retained failure does not establish a runtime defect or the required success path.
A corrected canonical A02 revision and intent were rendering during this review.

Acceptance still requires saved evidence for all of these checks:

1. Bind the exact frozen producer, plan, receipt, output bytes, sources, and source measurements.
2. Independently verify the two simultaneous movie readers and PNG movement, resizing, fading, signed placement, sparse coverage, and contain behavior.
3. Check every selected source ordinal and source PTS, every output PTS, and the relevant reader end conditions.
4. Compare every decoded output frame and required overlap region against separate-code pixels under the predeclared 34 dB threshold.
5. Verify the synthetic interval `[8191, 152191)` with exact PCM length, clock continuity, and zero-lag comparison.
6. Complete the corrected canonical 24-bit stereo regression with its exact selected interval and master binding.
7. Cancel a running export through `project.cancel-export` while that attempt owns its epoch.
8. Show worker shutdown, no promotion, correct attempt classification, and owned-stage handling after cancellation.
9. Reopen or replay the historical schema-2, schema-3, and schema-4 records without changing their identities.

These gates establish bounded native technical behavior only.
They do not establish normal-speed watching, hearing, creative quality, maximum-bound throughput, total native memory, or the full film.
