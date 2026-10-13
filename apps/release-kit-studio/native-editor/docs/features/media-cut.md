# Media and cut feature contracts

These proposed behavior contracts cover eight P1 Media families and four P7 Cut families. None is currently implemented or verified. The Rust core currently supports one non-overlapping track of solid clips, PNG previews, local revisions, and intents. The Rust core does not ingest movies, audio, image sequences, or camera input.

Native codecs and device SDKs stay unproven. These contracts need no external service or Effect credentials. FFmpeg, libav, bindings, and hidden fallback execution stay prohibited. The UI stack is unselected.

## MEDIA-01. Media ingest and metadata

### What it does

Import identifies actual source bytes and measures their media properties. An agent can distinguish sources before an edit.

### Scenario

A creator supplies three performance takes and a separate song master for a 24 fps music video. The agent imports all four files. Each result lists its content hash, measured duration, streams, and source timing. Import identifies camera audio. Import does not place clips on V1 or A1.

### Inputs and result

The planned command is `media.import`. Inputs include local paths, project identity, expected revision, intent, and a declared import policy. Rust's media module owns source records and measurements. Records bind byte identity, streams, dimensions, rational rates, sample counts, and available timecode. The stream-selection and variable-rate schemas stay undecided.

### Behavior rules

- Examine file content instead of file extensions. Reject bytes that change between inspection and registration.
- Keep source timestamps and distinguish unknown metadata from a measured zero. Record variable frame timing. Do not invent a constant rate.
- Register an immutable revision under the original intent. Import leaves timeline intervals unchanged.
- The first version permits only formats with proof in the native codec registry. Unsupported decoding returns a structured error without a substitute renderer.

### Implementation pieces

1. MEDIA-01.1. Define source identity and bounded stream metadata records.
2. MEDIA-01.2. Probe supported native files and measure timing and byte identity.
3. MEDIA-01.3. Commit registrations atomically with intent replay.
4. MEDIA-01.4. Add variable-rate and multistream cases after decoder experiments.

### Verification

- MEDIA-01-A.

  1. Import a reference movie and audio corpus.
  2. Independently compare bytes, dimensions, timestamp tables, and sample counts against the source records.

- MEDIA-01-B.

  1. Import truncated or unsupported content.
  2. Assert a structured rejection.
  3. Assert an unchanged revision.
  4. Assert that no accepted source record exists.

### Status and dependencies

Planned P1, owned by native Rust. Ledger prerequisites are CORE-01 and CORE-02. DELIVER-01 supplies the required codec evidence. See the [native specification](../SPEC.md). Measurement does not prove playback, listening, or approval.

## MEDIA-02. Bins and smart metadata search

### What it does

A bin groups source references without copies of the media. A smart bin uses explicit metadata conditions to find sources that match.

### Scenario

An interview project contains 40 takes tagged by speaker and camera. The agent queries speaker "Lakshmi", camera "B", and duration above 30 seconds. A smart bin lists only takes that match. The creator can examine the matches before assembly. Bin names do not change files or cuts.

### Inputs and result

The planned command is `media.search`. Inputs include revision, bin or predicates, order, and pagination limits. Rust owns bin membership, authored tags, and the query result. Results contain stable source IDs and the revision that the query uses for evaluation. Bin mutation operations, predicate syntax, and missing-value rules still need schemas. No learned scene recognition is implied.

### Behavior rules

- Initial predicates compare declared fields exactly. Keep measured metadata separate from tags that the creator supplies.
- A static bin stores explicit membership. A smart bin stores its predicate. The smart bin evaluates the predicate against a specified immutable revision.
- Declare the order and a stable tie-breaker. Pagination cannot duplicate or omit equal-valued records.
- The editor rejects unknown fields and invalid predicates explicitly. Missing metadata cannot silently match a positive condition.
- Bin changes keep source hashes and timeline positions. Advanced semantic retrieval belongs to AI-04 after separate evidence.

### Implementation pieces

1. MEDIA-02.1. Define static membership and typed metadata predicates.
2. MEDIA-02.2. Evaluate bounded queries with stable order and pagination.
3. MEDIA-02.3. Store bin and tag changes through revision transactions.
4. MEDIA-02.4. Show the provenance of measured fields in search results.

### Verification

- MEDIA-02-A.

  1. Query a labeled interview fixture.
  2. Across page boundaries, compare returned IDs and order with an independently authored expected list.

- MEDIA-02-B.

  1. Query missing metadata and an unknown field.
  2. Assert the declared missing-value result.
  3. Assert structured invalid-field failure.
  4. Assert unchanged source hashes.

### Status and dependencies

Planned P1, native Rust ownership. Ledger prerequisites are CORE-01 and CORE-02. Useful imported metadata requires MEDIA-01. No bin UI or runtime query exists.

## MEDIA-03. Proxies and optimized media

### What it does

A proxy is a smaller copy for edits with a link to its original source. Optimized media is a declared derived representation for decoding or caches.

### Scenario

A music-video creator has a supported 4K performance take on external storage. The agent requests a lower-resolution proxy for timeline inspection. The proxy shows the original source moment at frame 480. Representation changes keep the cut at frame 576. Final output uses the representation explicitly selected by the export policy.

### Inputs and result

The planned command is `media.proxy`. Inputs bind the source hash, streams, target format, dimensions, timing policy, revision, and intent. Rust owns the derived artifact and original-to-proxy mapping. Results bind both hashes, codec identity, measured timing, and seek mapping. Cache eviction and proxy format schemas stay open.

### Behavior rules

- Source identity stays the original hash. Never replace the original record with proxy bytes.
- Declare temporal mapping with rational timing and integer positions. Keep audio sample alignment when the selected format supports audio.
- Reject unsupported encode or decode combinations before work. No FFmpeg or hidden fallback can produce the proxy.
- A missing proxy permits only an explicitly declared original-source path. It cannot silently select different content or authorize proxy export.
- Start with one proven format and direct timing correspondence. Variable-rate conversion needs separate mapping experiments.

### Implementation pieces

1. MEDIA-03.1. Define representation identity and explicit selection policy.
2. MEDIA-03.2. Create a bounded proxy with a measured native encoder.
3. MEDIA-03.3. Source-position mappings and seek results.

   1. Record source-position mappings.
   2. Validate seek results.

4. MEDIA-03.4. Reconcile interrupted generation under the same intent.

### Verification

- MEDIA-03-A.

  1. Use a numbered-frame and impulse-audio corpus.
  2. Independently decode original and proxy positions at the start, midpoint, and final frame.

- MEDIA-03-B.

  1. Replace proxy bytes or remove the original.
  2. Under the declared policy, assert integrity or availability failure.
  3. Assert unchanged edits.

### Status and dependencies

Planned P1, native Rust. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. Native encoding also requires DELIVER-01 and DELIVER-02 proof. Movie proxy support stays unimplemented.

## MEDIA-04. Relink and media management

### What it does

Relink restores access when identical source content moves. Relink keeps edits unchanged because source identity does not depend on the file location.

### Scenario

A creator moves an interview recording to a local SSD. The timeline uses source frames 720 through 1439. The agent proposes the SSD file as the new location. A full hash match restores the same section. Relink rejects a different take with the same name.

### Inputs and result

The planned command is `media.relink`. Inputs identify sources, candidate paths, expected revision, and intent. Rust owns verified locations and the new immutable project revision. The result reports matches, rejected candidates, and unresolved sources. Batch atomicity, path precedence, and collection-management schemas still need decisions.

### Behavior rules

- Match exact content hash and byte count. Filenames, durations, and directory order cannot establish identity.
- Relink changes location references only. Source offsets, timeline intervals, authored tags, and historical revisions stay intact.
- Before you commit the declared batch, validate all candidates. A stale revision cannot overwrite a later location change.
- Keep unresolved findings. Do not replace missing content with black frames or a similarly named take.
- Initial management supports location repair. Media trim, transcode, and delete operations need separate operations and explicit policies.

### Implementation pieces

1. MEDIA-04.1. Define available, missing, and candidate-location states.
2. MEDIA-04.2. Search bounded local roots and measure candidate identity.
3. MEDIA-04.3. Commit verified locations with replay and conflict resolution.
4. MEDIA-04.4. Report unresolved and ambiguous location findings.

### Verification

- MEDIA-04-A.

  1. Move a source.
  2. Relink the source.
  3. Examine the new revision.
  4. Compare source hashes and each timeline interval with the original snapshot.

- MEDIA-04-B.

  1. Offer a substituted take with the same name.
  2. Assert rejection.
  3. Assert an unchanged revision.
  4. Independently calculate the hash of both files to prove the mismatch.

### Status and dependencies

Planned P1, owned by native Rust. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. Once EDIT-01 is available, its tests examine timeline preservation. No relink command is callable.

## MEDIA-05. Audio and video synchronization

### What it does

Synchronization records where separate recordings refer to the same event. An editor can then use recorder audio with camera pictures without changes to source bytes.

### Scenario

An interview camera records the clap 2 seconds after its start. A 48 kHz recorder captures the clap at sample 168000, or 3.5 seconds. The agent records a 1.5-second offset. At 24 fps, camera frame 48 maps to recorder sample 168000. The creator can inspect aligned claps and later speech sync.

### Inputs and result

The planned command is `media.sync`. Inputs bind source hashes, streams, reference, method, revision, and intent. Rust owns the sync relationship and its measurements. Results record offset, overlap, method, and any confidence result. Manual anchors come first. Timecode formats, waveform thresholds, rounding, and drift models still require schemas.

### Behavior rules

- Keep exact rational times and integer source positions. Declare sample conversion rounding before timeline use.
- Initial synchronization accepts explicit anchors and measured timecode that matches. Waveform matching needs an annotated corpus and ambiguity rejection.
- Record offset separately from drift. One clap cannot prove a long recording has no clock drift.
- Do not stretch source audio or move timeline clips implicitly. Application of a relationship is a separate edit.
- The editor rejects missing channels, invalid anchors, or insufficient overlap without a revision. Unsupported analysis has no hidden fallback.

### Implementation pieces

1. MEDIA-05.1. Define reference-clock and source-clock mappings.
2. MEDIA-05.2. Validate manual anchors and declared timecode conventions.
3. MEDIA-05.3. Persist offset relationships with source bindings.
4. MEDIA-05.4. Measure waveform matches and drift as later operators.

### Verification

- MEDIA-05-A.

  1. Use synthetic clap and timecode fixtures with known offsets.
  2. Independently examine decoded frame timing and audio impulse sample positions.

- MEDIA-05-B.

  1. Supply repeated claps or clocks with drift.
  2. Assert ambiguity or measured residual drift instead of false success.

### Status and dependencies

Planned P1, native Rust. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. AUDIO-01 and EDIT-01 enable downstream playback and edits. P2 owns timeline application. Listening and visual review stay separate.

## MEDIA-06. Checksum clone and consolidation

### What it does

A checksum clone copies media. The clone procedure does a check of each destination file against its source hash. Consolidation collects selected project sources into a declared local collection.

### Scenario

A documentary editor needs an interview project on a travel SSD. The agent copies the two camera files, recorder audio, and referenced stills into a new collection. The manifest reports source and destination hashes. A missing still stays an explicit failure. Location registration occurs after copy verification.

### Inputs and result

The planned command is `media.clone`. Inputs include sources or pinned revision, destination, intent, and copy policy. Rust owns the copy manifest and completion records. Results list verified copies, missing inputs, and incomplete destinations. Name-collision and resume schemas stay undecided. Relink stays a separate revision change.

### Behavior rules

- Start with full-file copies. Range trim and transcode operations are advanced operations that need independent timing and codec contracts.
- After the write, calculate the hash of destination bytes. A successful copy call or equal file sizes are insufficient proof.
- Never delete originals. Do not overwrite a different destination file under the same name.
- Interrupted work stays incomplete until fresh readback confirms the destination. Reuse the original intent. Keep the failure findings.
- Pin the selection to an immutable revision. Collection success cannot hide unavailable referenced sources or use hidden conversion fallback.

### Implementation pieces

1. MEDIA-06.1. Define the pinned selection and per-file copy manifest.
2. MEDIA-06.2. Copy to temporary locations with bounded storage checks.
3. MEDIA-06.3. Before promotion and the completion record, do a check of the bytes.
4. MEDIA-06.4. Continue interrupted copies without substitute content.

### Verification

- MEDIA-06-A.

  1. Clone a mixed-source project.
  2. Independently calculate the hash of each original and destination.
  3. Compare the complete manifest and missing-file count.

- MEDIA-06-B.

  1. Interrupt a copy.
  2. Corrupt its destination.
  3. Assert incomplete status and rejection until a new verified copy matches the original.

### Status and dependencies

Planned P1, owned by native Rust. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. MEDIA-04 handles subsequent location registration. No command currently clones production media.

## MEDIA-07. Camera RAW decoding

### What it does

Camera RAW decoding converts recorded sensor data into declared image buffers. The decoder keeps the source identity and the settings that produce those pixels.

### Scenario

A music-video creator supplies a camera RAW performance take with bright stage lights. After format experiments pass, the agent previews recorded settings. A second recipe changes exposure interpretation without a new write to the source. The creator compares both frames before approval.

### Inputs and result

The planned command is `media.decodeRaw`. Inputs bind source hash, format, frame, decoder, and development recipe. Rust owns decoded buffers and source-bound receipts. Results declare dimensions, bit depth, color interpretation, and settings. RAW means sensor-oriented camera data, not an ordinary compressed movie. Recipe parameters, decoder licensing, and SDK availability stay unresolved.

### Behavior rules

- Enable only individually proven camera format and platform combinations. No evidence currently establishes camera brand or SDK support.
- Bind exposure, white balance, and demosaic settings to the output. Demosaic reconstructs color from sensor samples.
- Keep development settings separate from later COLOR grading operations. Never imply equivalent output to a proprietary decoder.
- Keep original bytes and immutable recipes. Reject unavailable settings or malformed sensor data explicitly.
- Initial support must come after a measured corpus and licensing research. No FFmpeg, libav, or hidden image-conversion path can provide decoding.

### Implementation pieces

1. MEDIA-07.1. Research one permitted native decoder and collect camera fixtures.
2. MEDIA-07.2. Define sensor metadata and development recipe types.
3. MEDIA-07.3. Decode bounded frames with explicit color metadata.
4. MEDIA-07.4. Record decoder version, recipe, and output measurements.

### Verification

- MEDIA-07-A.

  1. Decode documented camera charts and reference frames.
  2. Independently examine pixel values, dimensions, metadata, and declared numerical tolerances.

- MEDIA-07-B.

  1. Request an unsupported RAW variant or corrupt a frame.
  2. Assert capability or integrity rejection without a substituted preview.

### Status and dependencies

Planned P1, native Rust. Ledger prerequisites are CORE-01 and CORE-02. MEDIA-01, DELIVER-01, and COLOR-01 require coordinated contracts. Frame inspection and creative approval stay unverified.

## MEDIA-08. Image sequence and alpha ingest

### What it does

Image sequence ingest uses numbered stills as one timed source. Alpha records pixel transparency so a later compositor can show lower layers.

### Scenario

A creator supplies 48 numbered PNG frames for a two-second transparent graphic at 24 fps. The agent imports their numeric order and declared rate. The future timeline places V3 over V1. Transparent pixels expose the performance. A missing frame 0017 blocks sequence use.

### Inputs and result

The planned command is `media.sequence`. Inputs include files or a frame-number pattern, rational rate, alpha policy, revision, and intent. Rust owns the sequence record and per-frame hashes. Results include ordered membership, dimensions, bit depth, and missing-frame findings. Padding, gap policy, color metadata, and alpha schemas stay open.

### Behavior rules

- Order by declared numeric indices, never lexicographic filenames. Reject duplicate indices and incompatible dimensions.
- Initial behavior requires contiguous frames. Unless a later explicit policy requests repeated frames, do not fill gaps with nearby frames.
- Keep declared bit depth. The editor rejects unsupported depth before registration. The editor does not reduce precision without an explicit rule.
- Distinguish straight alpha from premultiplied alpha, where RGB already includes transparency. Any conversion requires a declared rule.
- Use immutable per-frame identities and rational timing. Ingest does not implement P3 compositing. Ingest does not invoke a converter without an explicit rule.

### Implementation pieces

1. MEDIA-08.1. Parse bounded frame-number patterns and explicit membership.
2. MEDIA-08.2. Measure frame dimensions, channel depth, and alpha metadata.
3. MEDIA-08.3. Register a source manifest with exact frame hashes.
4. MEDIA-08.4. Add declared alpha conversion after reference-pixel checks.

### Verification

- MEDIA-08-A.

  1. Import numbered transparency fixtures.
  2. Independently decode each frame.
  3. Compare order, alpha values, bit depth, and duration.

- MEDIA-08-B.

  1. Remove frame 0017 or mix dimensions.
  2. Assert the exact index that causes the failure.
  3. Assert an unchanged revision.

### Status and dependencies

Planned P1, native Rust. Ledger prerequisites are CORE-01 and CORE-02. EDIT-01 and FUSION-02 provide later layer use. [LAYERS.md](../LAYERS.md) defines compositing. PNG output does not prove sequence ingest.

## CUT-01. Source tape and rapid assembly

### What it does

A source tape shows an ordered collection of source ranges as one sequence for inspection. Rapid assembly converts selected ranges into ordinary timeline clips.

### Scenario

An agent prepares an opening montage from three music-video takes at 24 fps. The creator chooses source frames 48 to 120, 240 to 288, and 0 to 96. The assembly places 72, 48, and 96 frames consecutively on V1. The nine-second montage keeps source offsets. Assembly does not flatten the montage into a movie.

### Inputs and result

The planned command is `cut.assemble`. Inputs bind ordered sources, ranges, destination, expected revision, and intent. Rust owns the source-tape mapping and assembled timeline revision. Results identify inserted clips and their exact source and timeline intervals. Sort policy, the source-tape inspection schema, and destination collision resolution stay undecided.

### Behavior rules

- Keep explicit order and source boundaries. A source-tape position maps to one source position without floating-point edit boundaries.
- Initial assembly accepts explicit ranges. It does not automatically choose the best performance or infer musical structure.
- Reject empty, out-of-bounds, or unsupported-rate mappings before the atomic commit.
- Keep audio policy per selected range. Assembly cannot silently duplicate a master song or mute camera audio.
- Use immutable revisions and stable intents. EDIT owns ordinary timeline edits. No second Cut reducer owns those edits.

### Implementation pieces

1. CUT-01.1. Define ordered source-tape entries and position mapping.
2. CUT-01.2. Validate selected ranges and rate conversions.
3. CUT-01.3. Compile assembly into the authoritative timeline transaction.
4. CUT-01.4. Add source-tape inspection and selection adapters without changes to semantics.

### Verification

- CUT-01-A.

  1. Assemble numbered-frame sources.
  2. Compare the saved clip intervals with an independent plan.
  3. Decode the adjacent frames at each join.

- CUT-01-B.

  1. Select a range beyond a source end.
  2. Assert rejection with no partial assembly or new revision.

### Status and dependencies

Planned P7, native Rust. Ledger prerequisites are CORE-01, CORE-02, MEDIA-01, and EDIT-01. [P7](../IMPLEMENTATION.md) follows native ingest and composition. Measurement does not establish creative approval.

## CUT-02. Sync bins and multicamera edits

### What it does

A sync bin groups recordings against a common clock. Multicamera editing selects which camera supplies each picture interval. Audio obeys an explicit policy.

### Scenario

An interview has a wide camera, close camera, and separate recorder audio. MEDIA-05 establishes their offsets. The agent keeps recorder audio on A1. The agent switches V1 to the close camera at frame 288 of a 24 fps timeline. Speech sample positions stay unchanged. The editor rejects a switch into an unavailable camera interval.

### Inputs and result

The planned command is `cut.multicam`. Inputs bind cameras, sync version, reference clock, switch positions, and audio policy. Rust owns the multicamera selection map and new timeline revision. The result lists camera intervals, audio routing, and unavailable spans. Angle names, overlap, and switch schema stay open.

### Behavior rules

- Freeze source hashes and sync mappings at the edited revision. Later resynchronization cannot alter old cuts.
- Initial switches use explicit frame positions. No automatic speaker selection or live direction is implied.
- Validate coverage at each selected interval. Do not fill a missing camera interval with a different angle automatically.
- Picture selection and audio routing are independent. Retention of recorder audio cannot add repeated samples at picture switches.
- Rational source-clock conversion and stable intents apply. Multicamera selection compiles into EDIT semantics without a second timeline model.

### Implementation pieces

1. CUT-02.1. Define sync-bin membership and camera coverage maps.
2. CUT-02.2. Validate switch times against synchronized source ranges.
3. CUT-02.3. Compile picture selection and explicit audio routing.
4. CUT-02.4. Expose switch and coverage readback for review.

### Verification

- CUT-02-A.

  1. Switch numbered camera fixtures with known offsets.
  2. Independently decode boundary frames.
  3. Compare continuous recorder sample indices.

- CUT-02-B.

  1. Switch into a missing camera span.
  2. Assert atomic rejection.
  3. Assert unchanged audio and revision.

### Status and dependencies

Planned P7, native Rust. Ledger prerequisites are CORE-01, CORE-02, MEDIA-05, and EDIT-01. AUDIO-01 supports the scenario's audio path. Playback and listening stay separate reviews.

## CUT-03. Source overwrite and smart insert

### What it does

Source overwrite replaces a declared timeline region with a time-aligned source. Smart insert chooses a nearby edit boundary by a declared deterministic rule.

### Scenario

A 24 fps interview timeline shows the wide camera between frames 240 and 480. A synchronized close-camera range corresponds to timeline frames 300 through 359. The agent overwrites those 60 picture frames. A1 stays unchanged. An insert request near frame 479 selects boundary 480. A 48-frame insert shifts selected downstream tracks by 48 frames.

### Inputs and result

The planned ledger command is `cut.overwrite`. Inputs bind operation, range, clock mapping, tracks, revision, and intent. Rust owns the generated EDIT transaction and new revision. Smart-insert schema, eligible boundaries, tie-break rules, and track scope stay undecided. Selection is deterministic.

### Behavior rules

- Source overwrite uses an explicit common-clock mapping. Filename similarity or displayed rounded seconds cannot establish alignment.
- Initial overwrite changes only declared destination intervals. Unaffected picture and audio intervals stay exact.
- Smart insert selects only permitted boundaries with a published distance and tie-break rule. Smart insert reports the selected boundary before commit.
- Insertion shifts only the explicit ripple scope. Locked tracks, unavailable handles, or ambiguous clock mappings reject the transaction.
- Rust EDIT operations own mutation semantics. Cut adds selection policy, immutable revision binding, and stable-intent replay without hidden execution fallback.

### Implementation pieces

1. CUT-03.1. Define aligned-source and boundary-selection requests.
2. CUT-03.2. Resolve overwrite ranges and deterministic insert boundaries.
3. CUT-03.3. Compile the requested operation into EDIT-02 transactions.
4. CUT-03.4. Return exact changed and preserved interval readback.

### Verification

- CUT-03-A.

  1. Apply the interview fixture operations.
  2. Compare each clip interval.
  3. Decode frames immediately before, within, and after the replacement.

- CUT-03-B.

  1. Supply a tied boundary or locked destination.
  2. Assert the declared tie result or explicit rejection.
  3. Assert that no unintended track shift occurs.

### Status and dependencies

Planned P7, native Rust. Ledger prerequisites are CORE-01, CORE-02, and EDIT-02. MEDIA-05 supplies alignment when recordings use different clocks. Both operations stay unimplemented.

## CUT-04. Live ingest and replay

### What it does

Live ingest records a declared input into bounded, recoverable segments. During capture, replay supplies completed segments within a documented delay.

### Scenario

During a filmed music performance, a creator wants to review the previous chorus during capture of the next verse. After device tests pass, the agent records numbered segments. Replay reads completed segments through the delayed position. Input disconnect records a gap and keeps completed segment order.

### Inputs and result

The planned command is `cut.capture`. Inputs bind device, channels, format, clock, resource limits, segment policy, and intent. Rust owns capture state, segment manifests, and completed source registration. Results report input identity, segment hashes, timestamp ranges, gaps, and terminal state. Start, stop, replay, and overflow schemas stay undecided.

### Behavior rules

- No evidence currently proves capture hardware, a device SDK, or a native capture codec. The editor rejects unsupported device or format requests before recording.
- Bound memory and disk use. Before you enable either behavior, declare whether overflow stops capture or keeps only a stated window.
- Distinguish recording, finalizing, completed, interrupted, and failed states. Replay cannot treat a partial segment as completed media.
- Keep source timestamps and segment order across restart. Input loss records a discontinuity rather than invented frames or samples.
- Start with one tested local device path. No current GPU, Resolve session, external service, or hidden fallback participates.

### Implementation pieces

1. CUT-04.1. Research one device SDK and record identity experiments.
2. CUT-04.2. Define bounded capture states, clocks, and segment policies.
3. CUT-04.3. Finalize segments with byte verification and durable manifests.
4. CUT-04.4. Expose completed replay ranges and interruption recovery.

### Verification

- CUT-04-A.

  1. Capture a hardware time-pattern source.
  2. Independently decode completed segments.
  3. Compare order, timestamps, sample continuity, and measured replay delay.

- CUT-04-B.

  1. Disconnect input.
  2. Exhaust the declared buffer.
  3. Assert the configured terminal behavior.
  4. Assert explicit gaps.
  5. Assert recovery of completed segments with their hashes unchanged.

### Status and dependencies

Planned P7, native Rust. Ledger prerequisites are CORE-01 and CORE-02. MEDIA-01, DELIVER-01, and EXT-03 need coordinated capture contracts. Technical measurements cannot establish playback, listening, or creative acceptance.
