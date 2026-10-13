# Native Rec.709 output implementation notes A01

Status: runtime implementation and development checks complete; independent native-output acceptance remains pending.

## Bound contract

The implementation follows `alpha-color-synthesis-a01.md`, SHA-256
`ecccf35c2e881358edad94cca8c14f82f61b795dcbd7c11ae3f2010d64ab5a6f`.
It also follows `alpha-color-judgment-a01.md`, SHA-256
`b28f396be43ed0163f71b52c051a5d8e91939c616a8a53a4adae26844175f8b2`.

## Implemented shape

- `MovieProfile::NativeColorMasterV2` is a closed caller-visible profile.
- `NativeFormatContract` derives QuickTime, ProRes 4444, PCM24LE stereo48kHz, and the complete Rec.709 writer properties.
- V2 attaches the Rec.709 Core Video tuple to every input pixel buffer using `ShouldPropagate`.
- V2 immediately reads each input attachment back before appending the pixel buffer.
- Verification reads the Core Media tuple from every nonempty encoded video sample.
- Verification reads the Core Video tuple and propagation mode from every decoded output buffer.
- Missing, partial, wrong, non-string, non-propagating, or changing tuples fail verification.
- Receipt4 requires `video_color.encoded_samples` and `video_color.decoded_buffers` to equal `ITU_R_709_2` in all three fields.
- V1 and H.264 neither inspect nor serialize V2 color evidence.

Plan selection remains feature-based across schemas 2 through 7. The profile does not create Plan8.
Receipt2 and Receipt3 bytes remain compatible because `video_color` is appended, optional, and skipped when absent.
Receipt schema, extension, codec, PCM evidence, and color evidence remain derived by `NativeFormatContract`.

No production container color parser was added. Existing publication, lease, cancellation, and recovery logic remains unchanged.

## Tests added or extended

- Plan2 through Plan7 retain their existing schemas when V2 is selected.
- Strict profile decoding rejects caller overrides for codecs, rates, extensions, color values, and attachment mode.
- Exact tuple tests reject missing, partial, wrong, changing, and non-propagating framework values.
- A native pixel-buffer test proves attachment readback without changing BGRA sample bytes.
- A native V2 Project export records Receipt4, re-verifies identical evidence, and replays the completed receipt.
- Receipt validation covers the H.264, V1, and V2 profile-schema-evidence cross product.
- Publication derives Receipt4 from the V2 plan contract.
- Staging recovery accepts a valid V2 Plan7 stage and retains forged Plan7 evidence.
- The exact legacy plan and receipt hash fixture remains green.

The existing ignored V1 alpha canary now uses a private profile-selecting helper.
The new ignored V2 canary is `isolated_rec709_prepared_plan_matches_every_independent_native_alpha_frame`.
It binds `fixtures-authored-a02.json` to SHA-256
`4e1e1c8bde98c40506f3d2f68333f92c42d7c6a93f300d874be96cf05670f753`.
It preserves the frozen 72-frame reference and asserts Receipt4 with exact V2 color evidence.
Its producer line includes the selected profile, receipt schema, and stored color evidence.

## Development checks

- `cargo fmt --all` completed.
- `cargo check --workspace` passed.
- `cargo test --workspace` passed 139 non-ignored tests with no failures; two native canaries remained ignored.
- `cargo clippy --workspace --all-targets -- -D warnings` passed.

The ignored V2 canary was not run in this implementation task. No ordinary export was produced.

## Source hashes

| File | SHA-256 |
| --- | --- |
| `crates/editor/src/plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `crates/editor/src/native_format.rs` | `e33d9f9ff7de3e0b8793b5301a465bebcccbe3f4ab496c8454929d498cb19f23` |
| `crates/editor/src/movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `crates/editor/src/lib.rs` | `499156ec54f3046ce2901bb01ec5361ed755739911624166c971cd42e4bc04f9` |
| `crates/editor/src/exports.rs` | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` |
| `crates/editor/src/publication.rs` | `4c04efc42972b9fad8f48f4be4e025fdecc6be89876109e6cbbc049bdd15f06a` |
| `crates/editor/src/layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `crates/editor/tests/project_invariants.rs` | `bdb50c9afe08c1287a38e4c03c8a9852aedd9ff77919373e883605d70cae745f` |
| `crates/cli/src/main.rs` | `6bc90118bf22fe74e8ae01caef9d7783cc76d210b6d9a8da30a60a161f1fe369` |

## Proof boundary

V2 records the observed output tuple. It does not establish source color management.
Source orientation, aperture, sample aspect ratio, and source color metadata remain unverified.
The profile performs no ICC, gamma, or source-gamut conversion.

The implementation does not claim H.264 fidelity, playback review, hearing, creative acceptance, or film acceptance.
The independent alpha/native-output report, unchanged 34 dB gate, exact PCM proof, and external `colr/nclc 1/1/1` observation remain pending.
Native grading and text remain planned capabilities.
