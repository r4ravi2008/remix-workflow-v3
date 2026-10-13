# Implementation review A16

## Result

Accept the bounded `NativeColorMasterV1` masks, mastering, and publication behavior unit.
No identified P1 or P2 defect remains after the A04 closure repair.

This acceptance covers the two fixed 72-frame Plan 6 exports and their bounded lifecycle evidence.
It closes the native-output gate left open by A15 and the mastering and publication code reviews.

The A04 report was created before this review.
Its `nativeOutputAccepted: false` value correctly records that earlier state.
This review supplies the final bounded technical disposition without rewriting that report.

No cross-family reviewer was available.
The separate verifier code still uses the same native AVFoundation framework.

## Findings

P1: none.

P2: none after the A04 packaging repair.

### The closure now binds its preserved failures

A03 listed the failed A01 and A02 closure files without hashing them.
A03 also claimed retained H.264 failures without binding their reports or movies.

A04 hashes all six failed A01 and A02 closure files.
It also hashes the four superseded A03 files, including the unchanged A03 report.

The A01 JSON-parser failure and A02 `id`/`label` parser failure remain preserved.
Neither failed run is relabeled as a successful closure.

A04 also binds these retained H.264 failures:

- The original report has 58 failed ROI cases across the two schema-6 outputs.
- The 24 Mbps probe report has 29 failed ROI cases at the unchanged 34 dB policy.
- Both original H.264 movies and the bitrate-probe movie retain their exact content hashes.

The original H.264 failure report SHA-256 is `68c5fbbaa2babec3f00638d80063010de115ff530cf7d69d2fc3261869125587`.
The bitrate-probe report SHA-256 is `00c4f0c0aec7e763d2832c43ca4b4802ab77aa7b7af4565d5d525a214309c6ba`.

Those H.264 results remain failures.
They do not provide an accepted fallback for the fixed master profile.

## Bound implementation and evidence

The closure binds the production CLI at SHA-256 `c12b2b5cd82428f0623f7645700d5c46690a0945ba4d927f37d538396951c3d3`.
It separately binds the instrumented crash-test producer at `ab43f7055171bc3ae95f6d43deda52f6e429d5afb7691478f754909e2eb5375a`.

The two executable identities are distinct.
The instrumented test producer is never represented as the production CLI.

The build manifest binds 29 Rust source files, 18 fixture files, 15 other build files, and `Cargo.lock`.
The closure also binds the input configuration, source assets, fixed references, and 144 decoded output PNGs.

The A04 closure files are:

| File | SHA-256 |
| --- | --- |
| `close_bounded_proof_a04.py` | `b803b1176ee83b10dee61f299d3df6531c658f57467b4ce35044ddb89973339a` |
| `closure-inputs-a04.json` | `3f92c716abd41ccd2e71b52bce715f7ed5944abfcd75783bf5dcba059e432466` |
| `closure-report-a04.json` | `d9b9138ce554ef2a41156b8db52266f5a2ee32c872f2066075bf2b581ca40454` |

The report contains 395 unique checks.
Every check passes.

I independently rehashed all 361 file-backed check rows.
Every current file matches both the expected and recorded digest.
The 40 manifest and preservation entries also match their declared digests.

## Native picture and audio result

The synthetic output is the 8,042,618-byte MOV with SHA-256 `8442d7ab54e95262aabb605111a87c7d051e41ea4721a760bb1123ba850f40c9`.
The canonical output is the 8,042,618-byte MOV with SHA-256 `0b1568be55eb47af5d144ed6cc571b8faee1cf3a79fe09f16de905fef44dfd5b`.

Each output has 72 decoded frames with the required PTS and EOF evidence.
Each variant passes every full-frame comparison.
The minimum full-frame PSNR is 46.054061 dB.

Each variant has 683 nonempty ROI comparisons and 359 declared empty regions.
Every nonempty ROI passes 34 dB.
The minimum finite nonempty ROI PSNR is 39.586659 dB.
Empty regions have no invented metric or pass claim.

The output picture comparison is decoded-output evidence.
It does not establish byte-exact equality with unavailable raw compositor buffers.
The 12 pure 8-by-8 frames remain the exact pre-encode arithmetic evidence.

Both outputs contain exactly 144,000 verified PCM24 stereo sample frames.
The maximum PCM24 code delta is zero.
The synthetic selection remains `[8191,152191)`.
The canonical 24-bit selection remains `[0,144000)`.

The media report passes 456 checks.
The graph report passes 47 checks.
The media controls reject 27 declared corruptions.
The graph controls reject 25 declared graph mutations.

These checks bind source bytes, selected source clocks, output clocks, EOF, format, plans, receipts, raw CAS roots, project paths, and renderer identities.

## Publication and compatibility result

Both accepted jobs have a completed current-epoch attempt.
Their ledger receipts, plan IDs, receipt CAS files, and MOV hashes agree.

The five production lifecycle controls pass:

1. Active public cancellation.
2. Stale-epoch fencing.
3. Real `SIGKILL` recovery under the bounded diagnostic.
4. Injected promoted-finalizing recovery.
5. Unknown-stage retention.

The lifecycle report records no cancellation or fencing receipt orphan.
It also preserves the earlier lifecycle directory with all 109 files unchanged.

The original crash report retains 833 checks and one malformed policy-hash failure.
The corrected metadata recheck passes 361 checks.
Its only declared policy change is `retainedExperiment.movies[3].sha256`.

Two legacy-finalizing negative controls pass on isolated state.
Six legacy readbacks preserve exact Receipt 2 identities across picture-plan schemas 2 through 6.
All 13 project heads remain unchanged.

I confirmed the current SQLite state through a read-only connection.
Both accepted jobs and attempts remain completed with the bound receipt and plan IDs.
The current 13 project heads still equal the saved legacy readback.

## Scope limits

This review accepts one bounded native profile and one bounded publication lifecycle.
It does not accept the whole editor or the 273-second film.

The evidence does not establish managed-color correctness, Resolve suitability, maximum throughput, or native process peak memory.
The crash controls do not establish power-loss durability or every instruction-level failure point.

The independent code shares AVFoundation with the product.
The media-control provenance records Python 3.12.8, Pillow 12.1.1, and NumPy 2.4.3.
The earlier control harness bytes were not archived and remain byte-unverifiable.

No normal-speed playback was watched.
No audio was heard.
No creative or full-film acceptance is implied.

No new native export, decoder run, GPU operation, Resolve operation, or media mutation was performed for this review.
