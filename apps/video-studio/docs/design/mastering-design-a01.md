# Selected native mastering contract A01

Status: selected for implementation. Native combined writing and fidelity remain unverified.

Use Candidate A with the parent selection and independent judgment as the complete contract.
`MovieProfile::NativeColorMasterV1` selects QuickTime/ap4h/PCM24LE stereo48kHz through existing Project operations.
One private `NativeFormatContract` owns settings, filenames, receipt version, and format verification.
One export-thread-owned writer session owns native writer, inputs, adaptor, and cancellation teardown.
Start the combined writer before any source worker. Keep existing bounded channels, clocks, and epoch fences.

Picture schemas remain2 through6. The immutable profile is an independent output-format axis.
H264 retains Receipt2 and absent optional fields. The mastering profile requires Receipt3 and observed format evidence.
Require bounded top-level ftyp parsing with a QuickTime major or compatible brand, ap4h video and lpcm audio.
Require signed, packed, interleaved, non-float, little-endian24-bit PCM,6bytes per stereo frame,48kHz.
Encoded sample descriptions must retain the same layout throughout the complete track.
New output readers use an explicit QuickTime MIME hint. Source import behavior is outside this change.

For finite f32 x, clamp x to[-1,1], multiply by8388608, round ties to even, then clamp to[-8388608,8388607].
Pack signed codes into three little-endian bytes per channel, left then right.
Writer input and output both declare that layout. Fresh comparison requires zero code delta for every selected sample.
Output clocks begin at zero. Source intervals remain[8191,152191) and[0,144000) in their respective plans.

Stage ownership accepts only the contract-derived payload name. Promotion derives the content-addressed .mov path.
Cleanup retains unknown, unreadable, mismatched, and unowned files. Recovery validates stored plan before deriving format.
Only receipt-bound promoted artifacts can complete recovered jobs. Otherwise use a fresh owned epoch.

Preserve ten legacy plan/snapshot/receipt documents, plus the canonical Plan6 document, as exact serialized fixtures.
Preserve both original failed H264 movies and the failed24Mbps probe.
Reuse the exact two masks revisions for format-only exports. Their source measurements retain the old probe producer.
The new renderer and selected-range decode evidence bind the fresh producer. Never relabel historical source measurements.

Before native exports, freeze producer/source/review/policy identities and save explicit new intents.
Bind the unchanged72 reference PNGs, reference manifest35e196ef8c041714b3eca714ca600deb9c158605fc308a9a85288bc3d1d6e011,
ROI manifest2531487be1e4e18927e88865c6e0afd982dff075e1fb7c679489781045ba6c4f, and34dB policy.
Require all72 full frames and683 nonempty ROIs per variant, complete clocks/EOF,144000 exact PCM24 frames,
container/layout readback, product verification/replay, cancellation, stale fencing, legacy readback, and negative controls.
Retain failures. This bounded proof cannot establish watched, heard, creative, managed-color, or final-film acceptance.
