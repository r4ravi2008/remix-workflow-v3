# Closed Rec.709 mastering synthesis

The production repair adds NativeColorMasterV2 and Receipt4.
Candidate A is the base. Root read both complete designs and the complete independent judgment.
Root scored A 32/35 and B 28/35. The independent judge scored A 32/35 and B 26/35.
The independent judgment is alpha-color-judgment-a01.md, SHA b28f396be43ed0163f71b52c051a5d8e91939c616a8a53a4adae26844175f8b2.

## Public contract

The caller selects {"kind":"native_color_master_v2"} through the existing ExportRequest.profile.
The closed profile accepts no matrix, bitrate, transfer, ICC, gamma or conversion override.
Picture feature schemas stay 2 through 7.
The profile and renderer already bind the plan hash.
The V2 master retains QuickTime, AP4H, opaque 32BGRA and exact PCM24LE stereo48kHz.

NativeColorMasterV1 retains its existing untagged writer, Receipt3 and no color evidence.
H264 retains its existing writer and Receipt2.
The new optional NativeMeasurements.video_color field is appended and omitted when None.
V1 and H264 require None. V2 requires Some.
Historical receipt, plan, verification and artifact bytes remain unchanged.

NativeVideoColorEvidence contains encoded_samples and decoded_buffers.
Each is a NativeColorTupleEvidence with color_primaries, transfer_function and y_cb_cr_matrix strings.
Every recorded string is the observed framework value ITU_R_709_2.
Counts remain in video_track.sample_buffers and video_frames.
No extra counters, tuple digest, container field or Plan8 is added.

## Private authority and ownership

NativeFormatContract remains the single owner of format dispatch, settings, attachment policy, receipt schema and measurement requirements.
The V2 writer adds the complete AVVideoColorPropertiesKey Rec.709 tuple.
NativeWriterSession::append_picture attaches the matching Core Video tuple with ShouldPropagate before every input append.
The session immediately reads back the values and propagation mode.
Missing, wrong or unpropagating input metadata fails before append.
Pixels allocation, workers, channels and publication ordering remain unchanged.
No native object crosses a worker channel.

Every nonempty compressed video sample must report the complete Rec.709 CMFormatDescription tuple.
Every decoded output buffer must report the matching complete Core Video tuple.
The existing loops retain their count, PTS, epoch, cancellation, deadline, alpha and EOF checks.
The receipt is constructed only after all loops complete.
NativeMeasurements::compare requires exact color evidence on reverify and completed replay.
V1 observations deliberately omit color evidence, even when native decoding infers attachments.

## Proof boundary

The product does not add a recursive MOV color parser.
Its claim is the exact measured encoded and decoded native tuple.
The existing bounded ftyp reader remains unchanged.
The independent proof selects the AP4H sample entry and requires exactly one colr nclc 1/1/1 atom.
This representation is a property of the bounded artifact, not a universal Receipt4 layout claim.
The independent parser needs missing, wrong, duplicate, truncated and extent sensitivity controls.

The same frozen 72-frame picture instructions, reference pixels, 752 region records and 34 dB floor remain authoritative.
All 516 nonempty comparisons must pass. The 236 empty comparisons remain metric-free.
The selected 144000 stereo PCM24 frames must remain exact with zero offset and complete clocks and EOF.
Fresh ordinary exports, public verify and completed replay must pass with the frozen new producer.
The private pre-encode 72-frame hash canary remains required.

Meaningful metadata tests exercise missing, partial, wrong and changing native tuples, including a middle sample or buffer failure.
Input attachment tests reject wrong values and propagation modes and preserve BGRA samples.
Receipt tests reject wrong schemas, missing V2 evidence and color evidence on historical profiles.
Historical schema2–7 and actual V1/H264 receipts must reverify without re-rendering or rewriting their receipt bytes.
Existing lifecycle tests, Receipt4 publication validation, active cancellation and the profile-derived recovery seam remain required.
The prior publication lifecycle evidence remains retained. No unrelated lifecycle redesign or resweep is added.

## Scope and limits

This profile defines the numeric native encode/decode mapping for the already composed source sample values.
It performs no PNG ICC, gamma, source gamut, HDR or natural-color conversion.
The complete settings and buffer-attachment pair is the tested mechanism.
The original failed alpha master and source snapshot remain preserved.
Native output acceptance remains pending until the ordinary independent proof and required controls pass.
WATCHED, HEARD, creative acceptance and full-film acceptance remain false.
