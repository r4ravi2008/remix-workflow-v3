# Alpha implementation review A03

Status: read-only review of the final extent-safety delta after
`alpha-implementation-review-a02.md`. I did not modify runtime code, fixtures,
proof outputs, metadata, or either earlier review. I did not run Cargo, tests,
Clippy, release builds, native export, or media playback.

## Result

No P1 implementation finding remains in the reviewed delta. One P2 provenance
documentation discrepancy remains in the frozen implementation notes.

The final source adds coordinate checks at
`/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/alpha_picture.rs:58-74`.
`StraightRgba8::pixel` rejects an x or y coordinate outside the checked source
extent before calculating its row-major offset. The offset multiplication is
checked, and the final four-byte slice is bounded by the owned RGBA vector.

Alpha sampling validates the mapping source extent and requested visible bounds
before allocation at `alpha_picture.rs:156-171`. Every Q16 bilinear tap then
passes through the checked source-coordinate accessor. The alpha raster remains
limited to 128 MiB before allocation at `alpha_picture.rs:123-135`.

Opaque and alpha sampling now share the source-extent guard in
`/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/composition.rs:157-166`
and `composition.rs:283-302`. This prevents a source with different dimensions
from using a mapping built for another source. The shared requested-bounds guard
also keeps raster writes inside the mapping's visible canvas bounds.

The added regression at
`/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/alpha_picture.rs:410-434`
covers both out-of-range source coordinates and a 2x2 source supplied to a 4x1
mapping. The existing composition tests cover the opaque wrong-extent path.
Mapping construction clips signed placement to the canvas before these guards
run. I found no unchecked coordinate path reachable from the current plan
compiler and worker response path.

Alpha blending also validates canvas extent, raster length, checked destination
bounds, premultiplied channel coverage, and Q16 layer weights at
`alpha_picture.rs:232-298`. The final changes therefore preserve the A02
source-lineage and ownership checks while closing the row-aliasing case.

## Native canary identity

The private canary remains explicitly marked `#[ignore]` at
`/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/layers.rs:904-906`.
Its identity bindings are internally consistent:

- The authored fixture constant is
  `622822d8a7e59222cf80d81e94d6b706747670110ba27f20f17051e822ae13e0`.
  The current `fixtures-authored-a01.json` hashes to that value.
- The reference summary constant is
  `e39a9b8c87a8a57260261cb304173db79110e7cead8e565c6eafe72ec8f6765a`.
  The current `reference-summary-a02.json` hashes to that value.
- The primary and transparent image constants match the two compressed asset
  hashes stored in the reference summary.
- The reference contains 72 unique native references for timeline frames 0
  through 71.
- The authored strict profile is `native_color_master_v1`.

The test binds the observer to the prepared Plan7 document hash. It checks the
timeline document hash, 72-frame timeline, 144,000 audio sample frames, two
alpha image evidence records, and their source RGBA hashes before export.
The observer hashes borrowed pre-handoff canvases. The test then calls public
export, verification, and completed replay. The source marks the producer as
`ordinaryCliProducer: false`, so this is an isolated test producer.

The saved selector evidence confirms one passing ignored test. The selector
record and log are respectively
`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01/canary-selector-repair-a02.json`
and
`/Users/aira/projects/remix-gpt-coding-agent/artifacts/scratch-video-goal-20261005/native-project-a01/alpha-native-unit-a01/code-gates-a01/instrumented-canary-selector-a02.log`.
The log reports 72 observed frames, plan
`1e5012eef0a5b57a5d0609f7f810679b28b782c0b7f15af70555614e59b3f220`, executable
`6311fb53655cce8429d34ee718cb347a25fff41c9b08dae2c083aa99ca8365de`, receipt
`868bebb89557674f99c6a696f96b492485cb94520fb709e15973f42d163129c4`, and
verification
`32b7a3ae1aa17c2662441a054b708911675269060c6e81240509438eed1c8c8b`.

The implementation notes list the same plan and executable, but list receipt
`0b4cdfe5c3cc612d55b07d1ef33b010f0c07f2474d5c07c6d4743cc5c19c9074` and
verification
`bb38df8e485c59eae3f5ea8e1eed962706f288a11a928b87846bdf411e0938a1`.
Those two IDs do not occur in the saved selector evidence. This is a P2
documentation and provenance mismatch. It does not invalidate the passing
selector run, but closure should identify the selector log as authoritative or
record the supersession explicitly.

I did not independently execute the ignored test. I inspected its saved
selector record and output log instead.
The ordinary CLI export, native ROI comparison, timing/EOF manifests, exact
PCM24 proof, playback, hearing, and creative acceptance remain outside this
review. Root owns those checks.

## Reviewed hashes and drift

Current SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/alpha_picture.rs` | `c1d755ebb0dea89db971560a3a0897d4c4c88a7f136bfe0e0f2273e6c38ce132` |
| `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/composition.rs` | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` |
| `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/crates/editor/src/layers.rs` | `310041424e5f2f0f09c400b79195e2a3ac2110ccd6fa4475247c74ad1bc6c033` |
| `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/docs/design/alpha-implementation-notes-a01.md` | `933909d49cb106846d84710c8d0373c3db257ad4302289e1e7256ef015958dc0` |
| `/Users/aira/projects/remix-gpt-coding-agent/apps/video-studio/docs/design/alpha-implementation-review-a02.md` | `9c1e8b50bb28e3cf24ac75e356cb1df03157ce2c3d0319150826f33179c1042a` |

Canary evidence hashes:

- `canary-selector-repair-a02.json`: `aac2d9dcf0988391473977f0e82f26ffac839a0c3e787ef467f6b9fbbef527d9`.
- `instrumented-canary-selector-a02.log`: `6da742a8af98934f53c89da9122a14ae1a0a0c73e5eb3eae5512e08d2c11ceb4`.

The report is limited to source inspection, hash checks, and fixture/reference
identity checks plus inspection of the saved canary selector evidence. It does
not convert the implementation notes' reported 133 tests into an independently
executed acceptance claim.
