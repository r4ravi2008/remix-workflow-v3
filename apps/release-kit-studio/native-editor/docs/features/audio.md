# Audio feature contracts

All eight families below are planned P2 behavior contracts. This document gives details. It does not supply executable audio tools or verified audio support. Current Rust commands handle one solid-color visual track and PNG frames.

Rust owns future audio timing, processing, measurement, and local storage. Effect and optional UI adapters stay outside the native editor. Local audio commands need no Effect credentials. Refer to the [native specification](../SPEC.md) and [implementation sequence](../IMPLEMENTATION.md).

For the named Pal Pal scenario, production must bind the actual canonical song's complete original master. The binding must include the byte hash, sample count, sample rate, and channel layout. Excerpts and processed copies keep that source binding.

A synthetic signal proves only a bounded technical case. The signal does not prove the song's production result. No native Pal Pal song render exists. Waveforms, measured signals, complete listening, and creative acceptance stay separate evidence states.

## AUDIO-01. Sample-accurate editing and mixing

### What it does

Sample-accurate editing places, trims, splits, fades, and combines sound at individual sample boundaries. A sample is one amplitude value per channel at a measured time.

### Scenario

An interview has a clap 1,000 samples after unwanted opening silence. The agent trims exactly 1,000 samples. The clap then occurs at timeline sample zero. Room tone on another track keeps the speaker's timing and declared channel balance.

### Inputs and result

The planned command `audio.mix` receives a revision, source hashes, sample ranges, channel maps, and gains. Rust saves the recipe and source-bound PCM. PCM contains uncompressed amplitude samples. Sample format, resampling, fade curves, and frame-to-sample rounding need schemas.

### Behavior rules

- Intervals include the first sample and exclude the end sample. Arithmetic checks reject overflow and source overrun.
- The first version mixes mono and stereo at one declared sample rate. Other rates require an explicit resampling capability.
- Rational frame conversion uses one declared rounding rule. Floating-point seconds cannot select an edit boundary.
- Edits create immutable revisions. Visual-track visibility does not mute an audio track.
- Summation must report clipping when amplitude exceeds the representable output range. Unsupported paths fail without a fallback renderer.

### Implementation pieces

- AUDIO-01.1 defines sample positions, source ranges, rate conversion, and channel maps.
- AUDIO-01.2 implements same-rate trim, split, gain, and deterministic PCM mixing.
- AUDIO-01.3 adds fades and independently measured resampling before the editor permits mixed-rate sources.
- AUDIO-01.4 saves source-bound mix receipts and checks the actual PCM bytes.

### Verification

- AUDIO-01-A, impulse placement.

  1. Trim 24,000 samples from a fixture whose impulse is at 25,000.
  2. Use an independent PCM reader to find the impulse at 1,000.

- AUDIO-01-B, invalid range.

  1. Request one sample beyond the source.
  2. Assert rejection.
  3. Assert an unchanged revision.
  4. Assert that no completed artifact exists.

- AUDIO-01-C, rational sync.

  1. At 48,000 Hz and 30000/1001 fps, map frame 1,000 to sample 1,601,600.
  2. Read the output position independently.

### Status and dependencies

Planned P2, native Rust `audio`. Ledger prerequisites are CORE-01, CORE-02, and MEDIA-01. Audio types and commands are absent from current Rust execution. Signal assertions do not prove listening approval.

## AUDIO-02. Waveforms meters and loudness

### What it does

Waveforms show where sound is strong or quiet. Meters and loudness analysis measure the sound level. Measurements help find clipping and compare mixes without estimates from display size.

### Scenario

A Telugu voice-over plays over music in a 20-second commercial. The agent measures both separately. A peak at sample 384,000 occurs eight seconds into a 48,000 Hz source. Measurements before and after a proposed level change support that change. The creator still listens for intelligibility.

### Inputs and result

The planned command `audio.measure` receives source identity, sample interval, layout, and configuration. Rust owns reports and waveform caches. Reports distinguish sample peak, estimated true peak between samples, RMS effective amplitude, and integrated loudness for the interval. The loudness standard, silence-exclusion rules, estimator, and tolerances stay open.

### Behavior rules

- Waveform buckets record their exact sample ranges and extrema. Display resolution never changes source timing.
- Analysis binds the full source hash and selected interval. A change to the mix invalidates its cached report.
- Analysis gives an explicit silence result for silence. It cannot become an arbitrary finite loudness value.
- Clipping counts and peak positions use channel labels and sample positions. A large waveform does not prove audible distortion.
- Measurement does not do automatic normalization. The editor rejects unsupported channel layouts or measurement configurations explicitly.

### Implementation pieces

- AUDIO-02.1 builds bounded waveform buckets from PCM with exact sample coverage.
- AUDIO-02.2 reports per-channel peak positions, clipping, and RMS.
- AUDIO-02.3 adds declared loudness and true-peak algorithms with reference fixtures.
- AUDIO-02.4 stores hash-bound reports and exposes measurement configuration in readback.

### Verification

- AUDIO-02-A, known peak.

  1. Place a 0.75-amplitude impulse at sample 384,000.
  2. Use an independent verifier to confirm amplitude, channel, position, and bucket coverage.

- AUDIO-02-B, silence boundary.

  1. Analyze zero-valued PCM.
  2. Assert silence.
  3. Assert zero clipping.
  4. Assert that the result does not invent finite integrated loudness.

- AUDIO-02-C, loudness corpus.

  1. Use identical declared configuration and preselected tolerances to compare reference signals against an independent implementation.
  2. If reference configuration is missing, record the case as inconclusive.

### Status and dependencies

Planned P2, native Rust `audio`. Prerequisites are CORE-01, CORE-02, and AUDIO-01. No measurement runtime exists. A report or waveform cannot establish complete listening or creative approval.

## AUDIO-03. EQ dynamics and effects

### What it does

EQ, dynamics, and effects change frequency balance, level variation, and sound character with explicit processing settings. EQ changes frequency balance. Dynamics processing changes gain as a function of signal level. Attack and release set how quickly gain reduction starts and ends.

### Scenario

An interview microphone records low rumble. The agent proposes a high-pass filter to reduce frequencies below a declared cutoff. A compressor reduces peaks above its threshold. For the 12-second comparison, the recommendation is to keep the words intelligible. Listening review assesses intelligibility.

### Inputs and result

The planned command `audio.process` receives a source-bound revision, ordered processors, settings, and sample range. Rust returns processed PCM, configuration, and latency measurements. Filter definitions, gain units, dynamics curves, buffer limits, and tail policies need schemas.

### Behavior rules

- The first operators are explicit gain and bounded filters. Compression, limiting, delay, and reverberation require separate acceptance cases.
- Processor order is part of the recipe. A change to the order of the filter and compressor cannot reuse the old result identity.
- Latency means the processor's sample delay. Timing compensation must record the exact sample shift.
- Effect tails have a declared duration policy. Export cannot cut a reverberation tail or extend a full-song profile without an explicit rule.
- The editor rejects invalid parameters and nonfinite samples. No processor claims output identical to a proprietary effect.

### Implementation pieces

- AUDIO-03.1 defines typed processor settings, units, bounds, and order.
- AUDIO-03.2 implements gain and filters with reproducible impulse and frequency responses.
- AUDIO-03.3 adds dynamics operators with declared attack, release, threshold, and clipping behavior.
- AUDIO-03.4 adds time-based effects, latency compensation, and explicit tail policies.

### Verification

- AUDIO-03-A, filter response.

  1. Process a known impulse and frequency sweep.
  2. Use independent signal analysis to compare the response with the declared response and tolerance.

- AUDIO-03-B, invalid processor.

  1. Request an unsupported filter or negative attack time.
  2. Assert rejection before any new revision or completed output.

- AUDIO-03-C, dynamics boundary.

  1. Apply known amplitude steps around the threshold.
  2. Measure gain change, timing, latency, and output clipping independently.

### Status and dependencies

Planned P2, native Rust `audio`. Prerequisites are CORE-01, CORE-02, and AUDIO-01. These operators are unimplemented. Technical response checks and speech listening stay separate.

## AUDIO-04. Buses sends automation and folders

### What it does

Audio routing sends tracks through shared controls. Automation schedules parameter changes. A bus combines signals. A send copies a controlled portion to another route.

### Scenario

A documentary has two interview tracks and music. The agent routes interviews to one dialogue bus and sends copies to a reverberation route. A volume curve lowers music between samples 480,000 and 960,000. A folder groups interviews for navigation.

### Inputs and result

The planned command `audio.route` receives an expected revision, track and bus identities, gains, and sample-positioned curves. Rust stores the routing graph in an immutable revision. Automation is a parameter curve over time. Interpolation, pan gains, solo behavior, and send placement need schemas.

### Behavior rules

- The minimum graph routes tracks to buses and buses to outputs without cycles. Validation rejects feedback routes.
- A folder changes only organization. Folder membership cannot add gain or create a route.
- Each send must declare whether it copies sound before or after track gain. The two positions cannot have ambiguous defaults.
- Automation uses integer sample positions and declared interpolation. Real-time and offline evaluations must agree to the declared precision.
- Mute, solo, and channel mapping require explicit semantics. The editor rejects unsupported layouts without a revision change.

### Implementation pieces

- AUDIO-04.1 validates stable routes, channel maps, gains, and acyclic bus graphs.
- AUDIO-04.2 evaluates direct routes and declared send positions.
- AUDIO-04.3 evaluates sample-positioned automation and persists exact curves.
- AUDIO-04.4 adds folder organization and separately specified mute and solo controls.

### Verification

- AUDIO-04-A, route sum.

  1. Route amplitude 0.2 directly.
  2. Route a second copy at gain 0.5.
  3. Use an independent PCM reader to measure 0.3 before other processing.

- AUDIO-04-B, cycle rejection.

  1. Create one request that routes bus A into bus B and bus B into bus A.
  2. Submit the single request.
  3. Assert atomic rejection of the whole request.
  4. Assert that the project hash equals its value before submission.

- AUDIO-04-C, automation boundary.

  1. Use a step curve that changes gain at sample 480,000.
  2. Compare samples 479,999 and 480,000 against independently calculated values.

### Status and dependencies

Planned P2, native Rust `audio`. Prerequisites are CORE-01, CORE-02, and AUDIO-01. Processing can use AUDIO-03 in combination. No current routing or automation command is executable.

## AUDIO-05. ADR voice recording and Foley

### What it does

Voice recording and Foley capture voice and practical sound as separate takes with source bindings. ADR means dialogue replacement that a speaker records against picture. Foley records actions such as footsteps.

### Scenario

A sentence in a documentary contains handling noise. The agent prepares a replacement cue at frame 240 of a 24 fps timeline. The speaker records two Telugu takes. Separate footsteps align with a shot of a person who walks. Original sound and each take stay available.

### Inputs and result

The planned command `audio.record` receives project identity, device, channel, sample rate, cue interval, and limits. Rust owns captured PCM, timestamps, take hashes, and selection revisions. Device APIs, permissions, clock mapping, and cue timing need platform experiments. Audio monitoring separates capture from speaker playback.

### Behavior rules

- The first capture path records a bounded mono take from an explicitly selected device. The editor rejects device substitution.
- Each new recording creates a separate take identity. Selection of a replacement never overwrites original dialogue or an earlier take.
- Rust measures input delay and clock drift. A requested start time does not prove the first captured sample's position.
- Disconnects, overruns, and dropped samples produce an incomplete take with explicit ranges. Incomplete takes cannot have complete-source status.
- Capture needs actual device support and operator permission. No synthetic recording proves hardware acceptance.

### Implementation pieces

- AUDIO-05.1 defines cue, take, device identity, and capture lifecycle states.
- AUDIO-05.2 implements one native capture path after research, with bounded PCM writes.
- AUDIO-05.3 measures latency, drift, discontinuities, and disconnect recovery.
- AUDIO-05.4 persists multiple takes and commits explicit selection against a revision.

### Verification

- AUDIO-05-A, hardware loopback.

  1. Capture scheduled impulses on a declared device.
  2. Independently measure sample count, onset delay, drift, and persisted hash.

- AUDIO-05-B, device loss.

  1. Disconnect during a bounded take.
  2. Assert incomplete status.
  3. Assert that captured bytes stay unchanged.
  4. Assert that the editor does not promote the take to a completed source.

- AUDIO-05-C, take selection.

  1. Save two takes.
  2. Select the second take.
  3. Restart the editor.
  4. Read back both hashes and the selected take without a change to the first take.

### Status and dependencies

Planned P2, native Rust `audio`. Ledger prerequisites are CORE-01 and CORE-02. Timeline placement also requires AUDIO-01 timing semantics. No implemented or tested capture device path exists. Dialogue sync and voice quality still need listening review.

## AUDIO-06. Surround and immersive audio

### What it does

Surround audio assigns sound to named speaker channels and keeps that mapping through a mix. Later immersive processing can position sound around a listener.

### Scenario

A screening uses six named channels. The agent routes narration to center and ambience to rear channels. Distinct test impulses identify each channel. A stereo review copy uses a downmix matrix. The matrix specifies each input channel's contribution to each output channel.

### Inputs and result

The planned command `audio.spatial` receives source identities, named layout, speaker mapping, and routing parameters. Rust owns labeled PCM and the recipe. Layouts, coordinates, matrix gains, and low-frequency-channel policies stay open. Object-based formats keep positions separate from speaker channels. These formats need research.

### Behavior rules

- Start with fixed named channels and explicit mapping. An unlabeled channel count cannot establish a speaker layout.
- Keep source channel identity, sample count, and timing through routing. Channels without signals contain declared silence.
- A downmix requires an explicit matrix and clipping report. The editor cannot silently discard a center or rear channel.
- Output receipts identify layout and channel order. The editor rejects unsupported destination layouts before output production.
- Immersive objects, head tracking, and headphone spatial rendering stay later experiments. No proprietary format or listening equivalence is implied.

### Implementation pieces

- AUDIO-06.1 defines named layouts, channel order, and validated speaker maps.
- AUDIO-06.2 routes fixed-channel PCM and records exact output metadata.
- AUDIO-06.3 implements explicit downmix matrices with independent gain checks.
- AUDIO-06.4 evaluates advanced spatial operators only after format and hardware experiments.

### Verification

- AUDIO-06-A, channel identification.

  1. Place distinct impulses at different sample positions in each input channel.
  2. Use an independent reader to confirm each mapped output channel and position.

- AUDIO-06-B, unknown layout.

  1. Supply six unlabeled channels for a named layout.
  2. Assert rejection without an output or new revision.

- AUDIO-06-C, downmix.

  1. Apply a declared matrix to constant per-channel fixtures.
  2. Compare each output amplitude against independently calculated sums and clipping counts.

### Status and dependencies

Planned P2, native Rust `audio`. Ledger prerequisites are CORE-01 and CORE-02. Signal execution also needs AUDIO-01 and supported delivery formats. Current code has no multichannel model. File-channel proof and listening through actual speakers are separate checks.

## AUDIO-07. Audio plugins and external processing

### What it does

Audio plugins apply processing from a specifically identified plugin. The result keeps the plugin configuration. A plugin contains processing code from a separate supplier.

### Scenario

A producer selects a plugin to reduce harsh interview sibilants. The agent records the binary identity and settings of the plugin. The agent then processes ten seconds. A 256-sample delay requires measured compensation. A crash reports failure and keeps the approved mix.

### Inputs and result

The planned command `audio.plugin` receives a source-bound revision, plugin identity, settings, layout, and sample range. Rust owns buffer semantics, latency, and output. Plugin APIs, licensing, state storage, and isolation require research. The process-free library needs a separate bounded Rust host for plugin processes.

### Behavior rules

- The first path supports one plugin API after research, with a measured fixture plugin. Installed plugins do not automatically become trusted capabilities.
- Capture exact plugin identity and settings. An updated binary cannot reuse an old processed artifact identity.
- Validate finite samples, channel formats, buffer bounds, latency, and tails. The result must identify nondeterministic output.
- A crash or timeout cannot commit a completed artifact. Never silently bypass the plugin or substitute another processor.
- Real-time external hardware inserts need a separate experiment with measured round-trip delay. Effect orchestration remains outside native signal processing.

### Implementation pieces

- AUDIO-07.1 examines and declares one supported plugin API and fixture corpus.
- AUDIO-07.2 defines bounded buffer exchange, plugin state identity, and process ownership.
- AUDIO-07.3 implements latency compensation and source-bound processed artifacts.
- AUDIO-07.4 does tests of plugin crashes, timeouts, malformed output, and later hardware inserts.

### Verification

- AUDIO-07-A, known delay.

  1. Use a fixture plugin that delays an impulse by 256 samples.
  2. Use an independent PCM reader to confirm uncompensated and compensated positions exactly.

- AUDIO-07-B, plugin crash.

  1. Terminate the isolated host during processing.
  2. Assert failure.
  3. Assert an unchanged approved revision.
  4. Assert that no completed output receipt exists.

- AUDIO-07-C, changed binary.

  1. Replace the fixture plugin with the old recipe unchanged.
  2. Assert identity mismatch instead of adoption of the old result.

### Status and dependencies

Planned P2, native Rust `audio`. Ledger prerequisites are CORE-01 and CORE-02. Buffer execution also requires AUDIO-01. Plugin API choice and isolation stay unresolved. No evidence proves plugin or external hardware support.

## AUDIO-08. Music envelopes and beat analysis

### What it does

Music envelopes measure changes in music energy. Beat analysis proposes beat positions for edits or environmental animation. An envelope gives signal amplitude for declared sample windows.

### Scenario

For the named Pal Pal scenario, the agent binds the complete original master and analyzes a chorus interval. Candidate beats animate background light. The animation keeps the performer, Telugu lyrics, and titles. The master stays intact. Motion and listening review precede creative acceptance.

### Inputs and result

The planned command `audio.envelope` receives the master hash, sample properties, interval, channel policy, window size, and configuration. Rust saves sample-positioned envelopes and beat candidates with confidence and algorithm identity. Candidates need review. Rhythm corpus, confidence calibration, bands, and window alignment stay open.

### Behavior rules

- Initial envelopes measure whole-signal energy without changes to audio. Band-specific envelopes and beat estimation are separate pieces that need explicit enablement.
- Every value identifies its sample window. Frame consumers use the declared rational time conversion, never rounded display seconds.
- Analysis of a chorus keeps the full-master hash and explicit excerpt offsets. It cannot replace the production song with an excerpt.
- For silence, speech, or ambiguous rhythm, analysis can return no beats. The editor cannot invent confidence to satisfy a requested marker count.
- Analysis proposes timing only. FUSION-08 controls environmental motion and protection masks. No beat report proves a completed music video.

### Implementation pieces

- AUDIO-08.1 defines hash-bound windowed envelopes, offsets, and channel policy.
- AUDIO-08.2 calculates bounded energy envelopes with explicit edge-window policies.
- AUDIO-08.3 adds beat candidates and confidence against an annotated rhythm corpus.
- AUDIO-08.4 exposes exact sample-to-frame lookup and rejects stale source bindings.

### Verification

- AUDIO-08-A, known energy.

  1. Analyze a fixture with declared amplitude blocks and silent ranges.
  2. Use independent calculations to confirm the coverage and values of each window.

- AUDIO-08-B, source substitution.

  1. After analysis, change one master byte.
  2. Assert stale-binding rejection before environmental animation consumes the curve.

- AUDIO-08-C, beat corpus.

  1. Before you run the corpus, set the acceptance tolerances.
  2. Compare candidates with annotated sample positions, missed beats, false positives, and confidence.

### Status and dependencies

Planned P2, native Rust `audio`. Prerequisites are CORE-01, CORE-02, and MEDIA-01. FUSION-08 consumes measurements later. Neither beat analysis nor Pal Pal production is implemented. Full playback, complete listening, and human creative approval stay unverified.
