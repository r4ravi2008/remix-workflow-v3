# Implementation review A11

## Result

No P1 or P2 correctness defect remains in the reviewed static PNG image unit.

The editor now owns opaque PNGs as typed image assets.
Each image has one source sample, `[0, 1)`, and requires `Hold { ordinal: 0 }`.

Schema-3 plans keep PNG evidence separate from timestamp-checked movie evidence.
The optional serialized field preserves historical schema-2 plan documents and hashes.

Review found two PNG input-validation defects.
The first implementation ignored bytes after IEND.
The first repair still accepted corrupt ancillary-chunk CRCs through the PNG library's recovery default.

Both defects are fixed in producer A03.
The capability inventory wording is corrected in inventory-only CLI A04.

The A02 movie remains the exact pixel and clock proof.
A03 proves strict validation of the same PNG bytes and prepares a fresh plan.
This split is valid because the A03 change only disables checksum recovery.

This unit does not complete the general compositor or the full hybrid film.

## Review boundary

The reviewed project is `panja-hybrid-scratch-01a10fbd`.

The main implementation hashes are:

- `image.rs`: `85e8e369f2f6494e2b68b3d5a32cf23b70d1d5be89d8a27ebae3ff4822878e56`.
- `model.rs`: `3b015d8b8fe9c36760f08e288f519fd02b62e636fc42f9113ad4330741fae137`.
- `plan.rs`: `2c55811fd863cbb48cb41c9c30a05f632ed53daf2ea5a72902183e3b4fc19152`.
- `movie.rs`: `3f8b61fdb8242db9b5929763684361efbffc4c38ab3b30fbb3d3af80f2ebdeee`.
- `project.rs`: `d54afa91b8000b5f04d9c21c339e1748456a88fa98d0765efb5b0e7aaa09572b`.
- CLI `main.rs`: `74880455310af922739924eef0bb4519a4a888c2847919e5804eb76469aaf1be`.

The pinned `png` dependency is exactly version `0.17.16`.
The Cargo lock hash is `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.

The evidence uses three distinct binaries:

- A02 export producer: `c5050ea6d4ae953522388624043d5fe042bf2334cea61aaabeaffb4a3cc16774`.
- A03 strict-input producer: `dcbe4bc46ff08dd52802b617faad417eaf946bd2b771b932a7eb8d315dd8547c`.
- A04 inventory-only CLI: `b9da1dadfb85f23c4ff410aecda5798ba93934221842db2f828e9248afddd66a`.

Their Mach-O UUIDs are `e1e01b3d3995399b92e710338b14d6db`, `e937f9f50efe3b97bf799307881454bd`, and `993d787ccb113ff09096889fde125b7b`.

I used APFS-cloned stores for behavioral failure probes.
I did not change the original store, run the GPU, or operate DaVinci Resolve.

Cross-family model review was unavailable.

## Defects found and fixed during review

### Bytes after IEND were ignored

The original decoder called `Reader::finish` and described the result as a complete PNG stream.
That library call stops after IEND.

I reproduced successful imports for two invalid files:

- A valid PNG followed by arbitrary bytes.
- Two complete PNG streams concatenated into one file.

The asset SHA-256 covered those bytes, but the descriptor and rendered pixels ignored them.
That contradicted the complete-stream contract.

`validate_png_boundary` now parses every chunk extent before decoding.
It requires the first zero-length IEND chunk to end at EOF.

Trailer and concatenated-image regressions now pass.

### Ancillary CRC recovery remained enabled

The first boundary repair relied on the PNG decoder for checksum validation.
However, `png` 0.17.16 defaults `skip_ancillary_crc_failures` to true.

I created a valid one-pixel PNG with a corrupt `tEXt` CRC.
Frozen A02 imported that file successfully on a copied store.

A03 constructs explicit `DecodeOptions` with both recovery flags disabled:

- `ignore_crc` is false.
- `skip_ancillary_crc_failures` is false.

Frozen A03 rejected the same copied fixture with `invalid_image` and a `CrcMismatch` detail.
The new regression checks a valid post-image `tEXt` chunk and its zero-CRC mutation.

### Supported precision and alpha wording was ambiguous

The decoder already expanded lower-depth grayscale and indexed PNGs.
The original behavior document described only eight-bit inputs.

The document and tests now state the actual support boundary.
RGB and RGBA inputs are eight-bit.
Grayscale and indexed inputs may use lower depths and expand losslessly to eight-bit RGBA.

The final discovery text says “non-opaque alpha.”
That wording preserves support for RGBA images whose decoded pixels are fully opaque.

## Decoder and immutable asset checks

Image import reads through a descriptor opened with `O_NOFOLLOW | O_CLOEXEC`.
The read is bounded, and its byte count must equal the opened file metadata.

The project copies the expected bytes into its content-addressed store.
The expected SHA-256 and byte count must match before probing.

The PNG decoder then enforces:

- Exact PNG signature and terminal IEND boundary.
- Strict critical and ancillary CRC checks.
- Complete IDAT decode and `Reader::finish`.
- The existing 128 MiB decoded-frame bound.
- No APNG animation controls.
- No sixteen-bit samples.
- No decoded pixel with alpha below 255.

The descriptor stores dimensions and SHA-256 of decoded RGBA bytes.
The renderer swaps red and blue only after computing that RGBA identity.

Every plan preparation reopens each used image from the CAS.
It rechecks asset bytes, decodes the complete PNG, and compares the full stored descriptor.

A03 remeasured the same two actual PNG assets at sequence 9.
The resulting revision is `1bd422f2175ce5468fe4efc24593677897570c5c04cbe0767bbac5a3f6234572`.

The strict decoder retained these exact measurements:

| Asset SHA-256 | Dimensions | Decoded RGBA SHA-256 |
|---|---:|---|
| `0e38532679abfb53386659762888dba87dcad8ff7d3377f0ffe9eccb355fe8d3` | 1920x1080 | `639b400d1d360b1d8033ac5c30979641edf9305be4031e8c4832e24fd2c439ca` |
| `a03eacfe29ac98847657121bd341fc1c02b32e6a51212d4c97885fd5fd38e175` | 1942x809 | `10d036af3216c938949b0be6c6a538674b9156b5c1c9b6ad8daeb98e0d71c8ec` |

The extracted still retains typed lineage to movie asset `a2247e96...` at source sample 1560.
The illustrated anchor remains labeled `unaccepted-generated-image`.

The decoder does not apply ICC profiles, gamma, working-color conversion, or display orientation.
The descriptor and capability inventory state the source-sample boundary.

## Revision, cadence, plan, and replay invariants

`MediaKind::Image` and `MediaDescriptor::Image` extend the existing asset model.
They do not encode a PNG as a one-frame movie.

Snapshot validation requires an image source range of exactly `[0, 1)`.
It also requires hold cadence at ordinal zero.

The atomic invariant test rejects source-presentation cadence and a two-sample range.
The project head remains unchanged after each failed commit.

Plan compilation emits one presentation ordinal zero for every held timeline frame.
Movie clips continue to use their indexed presentation timestamps.

Image plans use schema 3.
They store dimensions, RGBA SHA-256, asset identity, and exact decoder executable SHA-256.

A03 prepared plan `0adc4849ea58db94be372b3af79945dfddbf64ae92cb6ced0f36f9b0f2c4772b`.
I recomputed that ID from the exact stored plan body.

The plan contains two image evidence entries bound to A03.
It also contains selected-range movie evidence for the twelve motion frames.

`image_decode_evidence` defaults to empty and is omitted when empty.
Therefore, an old schema-2 document serializes exactly as before.

Frozen A03 replayed historical schema-2 plan `193c51fabd83382e6c320173930109a2065c2fdb0887c7a3722becbf2dda5fc4` from a copied store.
The replay retained schema 2 and contained no image evidence field.

## Native frame evaluation

The existing picture track can alternate movie clips and image holds.
No caller coordinates a separate image renderer.

For each image clip, the worker performs one strict decode and one declared framing operation.
It emits owned BGRA frames through the existing channel of capacity two.

The output frame clock remains the timeline clock.
An image does not provide or invent source timestamps.

The bounded implementation clones the framed image for each emitted frame.
The current profile limits the timeline to 240 frames and each owned BGRA frame to 128 MiB.

The product proof covers ordinary 1920x1080 and 1942x809 inputs at a 2560x1440 canvas.
It does not measure maximum-bound memory use or throughput.

This design extends the shared media and framing model.
It avoids recreating the historical PNG-only renderer boundary.
Layers, motion, masks, text, grading, and scalable audio remain later editor operations.

## A02 product and independent evidence

The exact A02 export is:

- Output SHA-256: `ab65129d7bf451b193c764443a1731d0ecdb502b6889e1730a74e5b9760625ac`.
- Output bytes: 1,290,102.
- Revision: `1f36eb734ab558b92e88557c980143b43c72ca5b1349da2ede920d2c8b95eb92`.
- Schema-3 plan: `1511c0f42ae30c9ae1e2026d64ff5f978544d34521bcacfdb657b0f2a2e59347`.
- Artifact receipt: `8e0bc864df8f07f0ddf831000ac4601d49909d927030bbe67de03b13b6d0dd53`.
- Fresh verification: `5016e79ef7ea23816e5db4f752b472d036cc92911a36340a800b9d8bd0c3bc54`.

The 48-frame plan maps:

- Frames 0 through 11 to the extracted real-source PNG hold.
- Frames 12 through 35 to the illustrated anchor PNG hold.
- Frames 36 through 47 to movie presentation ordinals 0 through 11.

All three clips use declared contain framing.
The audio clip selects canonical asset `cc4ab40e...` over samples `[0, 96000)`.

The independent report SHA-256 is `3bade5a43e6ebca564d072a2c031272ba6dd6ef59d6165e52b469f17eb688d16`.
Its comparison script SHA-256 is `c3160a565c977d47abb00a6e19baeb27403041a9194689c9eb92150bf1e6f5dd`.

I independently reran the report relationships without rewriting saved evidence.
The checks established:

- The exact output and producer hashes.
- All 48 decoded output RGBA hashes.
- Exact output PTS at `n/24` for every frame.
- Primary reader completion at EOF.
- Exact Pillow RGBA expansion for both PNG descriptors.
- All 48 bilinear contain comparisons above 34 dB.
- Minimum RGB PSNR of 40.10120022711628 dB.
- Twelve movie-source RGBA and clock matches against saved native observations.
- Exactly 96,000 decoded stereo sample frames.
- Zero-offset cosine similarities of 0.9999705560560845 and 0.9999708586933836.

Pillow provides an independent PNG decoder for the image cases.
The native output and movie-source observations share AVFoundation.
The report states that limitation.

A03 did not encode a third movie.
Its strict plan proves that the same exact PNG bytes pass the repaired decoder with unchanged RGBA.
The A02 movie proves the unchanged framing, frame transport, encoder, and output verification path.

## Tests and capability inventory

The current workspace passed all 47 tests:

- 33 editor unit tests.
- 1 frame-directory verification test.
- 10 project-invariant tests.
- 3 replay-and-cleanup tests.

`cargo clippy --all-targets --all-features -- -D warnings` passed.
`cargo fmt --all -- --check` passed.

The six focused PNG tests cover channel identity, alpha, precision, truncation, critical corruption, animation, trailers, concatenation, lower-depth expansion, and ancillary CRC rejection.

Frozen A04 reproduced saved `discover-a04.json` exactly.
The inventory now reports schema-2 movie plans, schema-3 image plans, and opaque static PNG scope.

## Truthful acceptance boundary

This review accepts the bounded static PNG implementation and its mixed image/movie technical diagnostic.

It establishes exact image bytes, decoded RGBA, one-sample hold semantics, typed lineage, immutable plans, frame clocks, and encoded technical correspondence.

It does not establish color-managed output, display-orientation behavior, playback, hearing, motion quality, story quality, or creative acceptance.

The A02 audio evidence is a zero-offset numerical comparison.
It is not a listening result.

The illustrated anchor remains technically measured and creatively unaccepted.
The two-second diagnostic is not the 273-second film or the hardest musical and action pilot.

The general compositor, full audio model, text, masks, motion, color, tenant orchestration, complete film, and final human review remain incomplete.
