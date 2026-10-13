# Alpha color implementation review A01

Status: completed bounded source review. No production source, fixture, metadata, media, GPU,
or Resolve file was changed by this review. No Cargo command was run by this reviewer.

## Review basis

The review compared the current source against:

* `alpha-color-synthesis-a01.md`, SHA-256
  `ecccf35c2e881358edad94cca8c14f82f61b795dcbd7c11ae3f2010d64ab5a6f`.
* `alpha-color-implementation-notes-a01.md`, SHA-256
  `c9e123c29266f05da99135704e5cb291b02e8c246fd6162ea6866130758678e8`.
* `color-runtime-diff-a01.patch`, SHA-256
  `ba4a0beab34315a3b4c973bc72bd1e7a0794731af2aa8fafffe3764c7f2173c5`.

All nine source hashes in the implementation notes match the current checkout. The retained
code gates report 139 non-ignored tests, formatting, Clippy, release build, and discovery passed.
The retained root review records one private V2 canary with 72 observed frames and Receipt4.

## Result

Review conclusion: No P1 or P2 remains in the reviewed V2 implementation. The review confirms the bounded
source shape. It does not convert the retained checks into ordinary native-output acceptance.

## Checked boundaries

**Profile and serialization.** `MovieProfile::NativeColorMasterV2` has a closed custom wire
variant. Its `serde(deny_unknown_fields)` path rejects caller codec, rate, extension, color,
and attachment overrides. `ExportPlan` keeps picture schemas 2 through 7. The optional final
`NativeMeasurements.video_color` field uses `default` and `skip_serializing_if`; V1, H264, and
historical receipt bytes remain unchanged when it is absent. The color evidence types also deny
unknown fields.

**Format authority.** `NativeFormatContract` remains the only production owner of profile
dispatch. V1 maps to `MasterV1`, V2 maps to `MasterV2`, and H264 remains separate. Receipt
schemas are 3, 4, and 2 respectively. V2 retains QuickTime, ProRes 4444, packed PCM24LE
stereo48kHz, and the existing stage/artifact paths. V1 rejects V2 evidence, H264 rejects
mastering and V2 evidence, and V2 requires the complete Rec.709 tuple.

**Writer input ownership.** V2 adds the complete `AVVideoColorPropertiesKey` dictionary.
`NativeWriterSession::append_picture` attaches the three Core Video values with
`ShouldPropagate`, then reads each attachment and propagation mode back before appending the
borrowed pixel buffer. The test preserves BGRA bytes after attachment. No native object crosses
the worker channel or outlives its scoped writer operation.

**Encoded observation.** The nonempty encoded-video sample loop reads all three Core Media
format-description extensions. Missing, partial, non-string, wrong, or changing tuples fail.
The retained tuple is evidence for the track; the existing encoded sample-buffer count remains
the count authority. Audio inspection remains independent and retains the PCM24 checks.

**Decoded observation.** The full decoded-video loop checks cancellation, deadline, ordinal PTS,
epoch, dimensions, opacity, and EOF as before. Every decoded buffer is checked for all three
Core Video attachments and `ShouldPropagate`. A changing middle tuple fails. The existing frame
count supplies coverage; `NativeMeasurements::compare` requires exact stored and fresh color
evidence on verify and replay.

**Receipt and recovery.** Publication derives schema 4 from the V2 plan contract. Receipt
validation requires the V2 tuple and rejects schema/profile mismatches. The source diff changes
publication fixtures and tests, not publication ordering, lease fencing, cancellation, error
closure, or staging recovery. The Plan7 recovery test accepts valid V2 evidence and retains
forged evidence. Existing Receipt2/Receipt3 and exact legacy hash fixtures remain covered.

**Canary identity.** The selected ignored canary is
`isolated_rec709_prepared_plan_matches_every_independent_native_alpha_frame`. The retained root
review binds the authored fixture SHA
`4e1e1c8bde98c40506f3d2f68333f92c42d7c6a93f300d874be96cf05670f753`, 72 frames, Receipt4,
and the V2 selector. The implementation notes predate that retained canary run and state that
it was pending at note creation; the later code-gates records are the current gate evidence.

## Retained gate records

* `code-gates-a02.json`, SHA-256
  `5810720573df0329fa0edb93850d612b3ca1e73ee60ea77ff6a6130201fe9707`.
* `code-gates-root-review-a02.json`, SHA-256
  `8bf0fbbfb40c73da932fe0f0fc4f14235c1c832d7fa5bc4703a5b4b7c14aea1b`.

Those records report `sourceDrift: false`. Their claims keep ordinary native output, watched,
heard, creative, and film acceptance false.

## Current source hashes

| File | SHA-256 |
| --- | --- |
| `crates/cli/src/main.rs` | `6bc90118bf22fe74e8ae01caef9d7783cc76d210b6d9a8da30a60a161f1fe369` |
| `crates/editor/src/plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `crates/editor/src/native_format.rs` | `e33d9f9ff7de3e0b8793b5301a465bebcccbe3f4ab496c8454929d498cb19f23` |
| `crates/editor/src/movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `crates/editor/src/lib.rs` | `499156ec54f3046ce2901bb01ec5361ed755739911624166c971cd42e4bc04f9` |
| `crates/editor/src/exports.rs` | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` |
| `crates/editor/src/publication.rs` | `4c04efc42972b9fad8f48f4be4e025fdecc6be89876109e6cbbc049bdd15f06a` |
| `crates/editor/src/layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `crates/editor/tests/project_invariants.rs` | `bdb50c9afe08c1287a38e4c03c8a9852aedd9ff77919373e883605d70cae745f` |

## Limits

The review did not run the ordinary CLI export, independent MOV atom parser, independent
pixel/audio report, playback, listening, or creative review. It does not prove source color
management, ICC, gamma, source gamut, HDR, H264 fidelity, or complete-film acceptance.
