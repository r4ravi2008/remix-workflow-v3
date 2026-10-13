# Native mastering output task A01

Design a native full-color-detail mastering output for the fresh Rust editor.
The existing H.264 mask fixture passes full-frame picture, audio, source clocks and EOF checks.
Its one-pixel fractional strips and some exposed lower-layer regions fail the fixed 34 dB RGB policy.
The 24 Mbps probe retains 29 failures. Raising the bitrate does not resolve this observed unit.
The measured H.264 SPS declares chroma_format_idc1, eight-bit luma/chroma and profile_idc100.
This is evidence for a subsampling limitation, not a claim that every possible H.264 encoder profile is unsupported.

The purpose is a useful mastering file that preserves composed color detail for Resolve and independent verification.
Apple documents ProRes4444 as a full-resolution RGB/Y'CbCr mastering codec.
Native writer availability on this exact host must still be proven.

Use the existing direct Project prepare/export/verify/cancel/reconcile operations.
No renderer subprocess, FFmpeg, libav, copied predecessor runtime or hidden alternative rendering path is allowed.
Keep the existing bounded track workers, source-presentation clocks, opaque BGRA composition and canonical sample mapping.
One measured48kHz stereo source remains sufficient for this dependency. Mixing, resampling and alpha-bearing inputs remain separate.

Each candidate must provide caller usage first, types/signatures, module map, native format settings, plan-version decision,
profile-specific structural verification, source and output clocks, stage/artifact extension authority, recovery behavior,
exact historical compatibility and a bounded native proof with retained failures.
Consider full-resolution ProRes4444 and suitable AAC or PCM audio in a QuickTime container.
Do not assert this host can encode that combination without a native readback.
Whole-shape alternatives are required. Describe rejected alternatives and expected extension behavior for future formats.

The new proof must preserve the exact A01 authored picture timeline, original references and every existing ROI coordinate.
Declare the new format/bitrate/audio policy before its export. Retain the original H.264 failures and post-failure bitrate probe chronology.
Keep the picture34dB threshold. Explicitly bind any revised fixture/profile to the unchanged pre-export picture reference.
Require complete output video/PCM clocks, EOF, immutable plan and receipt identity, exact sources, cancellation and legacy readback.
No watched, heard, creative or final-film acceptance can come from this technical proof.

Evidence is in artifacts/scratch-video-goal-20261005/native-project-a01/masks-native-unit-a01/:
`build-a01.json`, `fixtures-authored-a01.json`, `reference-summary-a01.json`, `reference-rois-a01.json`,
`independent-a01/verification-report-native-a01.json`, `parent-picture-preliminary-a01.json`,
`profile-probe-a02-policy.json`, `bitrate-probe-picture-a02.json`, `h264-sps-a01.json`.

Apple source: https://www.apple.com/final-cut-pro/docs/Apple_ProRes_White_Paper.pdf
H.264 chroma table: https://www.itu.int/rec/dologin_pub.asp?id=T-REC-H.264-200901-S%21Cor1%21PDF-E&lang=e&type=items
