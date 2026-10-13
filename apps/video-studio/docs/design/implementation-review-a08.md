# Implementation review A08

## Result

No P1 defect remains in the reviewed A08 import-provenance unit.

The importer now uses Core Media output DTS beside output PTS and output duration.
It preserves differing raw DTS, PTS, and duration in `EncodedTiming`.

New and guarded-refreshed measurements bind probe schema 1 to an exact `BuildIdentity`.
The refresh guard fixes the media kind and preserves bytes, origin, and the prior metadata token.

The first producer-identity implementation had a pathname race.
A second implementation still accepted a same-UUID pathname replacement.
The final implementation closes both reproduced races before opening project state.

The A02 product export passed all 24 independent technical checks.
This result covers one 24-frame H.264 range and 48,000 stereo PCM frames.

One P2 evidence limit remains.
The production sequence-4 measurement predates the final executable-acquisition hardening.
Its archived producer supports the recorded identity, but the producer did not self-enforce that identity against pathname races.

The general compositor and complete hybrid film remain incomplete.

## Review boundary

The reviewed source video has SHA-256 `b78939035919803ad33cd60979be7f1fb28798d8a34404c2881371300ce167ca`.
It contains 65,616,935 bytes and 6,462 indexed H.264 presentation samples.

The canonical audio has SHA-256 `cc4ab40ef82dddb8d20aa5a6b8d1e68036d4e6ecd264b27e403b7719bfbb5bd8`.
It is 24-bit interleaved PCM stereo at 48 kHz for 13,104,000 sample frames.

The reviewed revisions are:

- Sequence 2: `29ec243126ea83f087335a54bfdf20b4334f6c656fe8732036511406ddedc903`.
- Sequence 3: `624021b2286728d87df3972867ff47fd5f6ccbd4761a0d728cc7266a810e7470`.
- Sequence 4: `9b543f456907585ad9a128a40540b56cabd8da0dba90613421bca80733afd980`.

Their source-measurement hashes remain:

- Sequence 2: `78430ab6c45ed7687c06143a1942dbbb9ec1383b7c82e6da240e133f6bb652f9`.
- Sequence 3: `b6f3b1f29ea1435f8848cc864f7540aa9a97d7469b9b78db1d300cbe8217f31d`.
- Sequence 4: `3f9e3902d87573c578bafabb8f039334189b25a68bbbfefdd8168f3a1ab3e90b`.

The A02 product producer is `video-studio-source-clock-producer-a02`.
Its SHA-256 is `7a9782340ca8087fc12511f84e26bac6cb43c20126b05b468729727c72fb8600`.

The final identity-hardening binary is `video-studio-frame-inspector-a02`.
Its SHA-256 is `a3fa63d5d1ef1c35260e71c2d4ea3a8daf7b88ee2e20d4adc2eba2c77d14bc30`.
Its Mach-O UUID is `3f77c5785607371b84093238d3c0cb93`.

That later binary also contains source-frame inspection work.
This review covers only its executable-identity, import, inspection, and replay paths.
The separate source-frame unit remains outside this review.

## Source-clock authority

The native A02 clock diagnostic observes one zero-sample compressed buffer first.
That buffer has no numeric raw or output DTS and is correctly skipped.

The first nonempty compressed sample reports these clocks:

- Raw PTS: `512/12288`.
- Output PTS: `0/12288`.
- Raw DTS: `0/12288`.
- Output DTS: `-512/12288`.
- Raw and output duration: `512/12288`.

The first decoded frame appears at `0/12288`.
The output clock therefore matches decoded presentation without an inferred offset.

The sequence-4 index contains all 6,462 nonempty compressed samples.
The output PTS sequence starts at zero and advances by 512 ticks.

Every sample preserves a raw PTS exactly 512 ticks after its output PTS.
Every sample also preserves a raw DTS exactly 512 ticks after its output DTS.

The first four output DTS values are `-512`, `512`, `1024`, and `0` ticks.
The stored order therefore preserves native decode reordering rather than forcing presentation order onto DTS.

All stored raw and output durations equal 512 ticks for this source.
No product code guesses or applies a fixed offset.

The standalone diagnostic reads eight buffers and then cancels its readers.
Its `fullDecode`, `watched`, `heard`, and `creativeAccepted` fields are false.

The complete 6,462-sample index comes from the product import reader.
Selected-range plan evidence independently decodes only source ordinals 0 through 23.

## Probe identity and executable acquisition

`StoredAsset.measurement` now stores `NativeProbeIdentity` inside the revision document.
The identity includes schema, executable hash, Cargo lock hash, host, native backend, and architecture.

The production sequence-4 measurement binds these values:

- Probe schema: `1`.
- Executable: `7a9782340ca8087fc12511f84e26bac6cb43c20126b05b468729727c72fb8600`.
- Cargo lock: `8493110f33b9aad347ce49b2a0389d16fc8998829e94ad997bce9c4bc0919f8d`.
- Host: `Version 26.0.1 (Build 25A362)`.
- Backend: `objc2 0.3.2 / AVFoundation bundle 2360.79.5.2`.
- Architecture: `aarch64`.

The initial implementation measured the current executable pathname after source probing.
A copied-store reproduction replaced that pathname while the original process remained active.

The commit succeeded and recorded the replacement executable hash.
That result did not identify the code performing the probe.

The first fix compared the pathname Mach-O UUID with the loaded image UUID.
A second reproduction changed an unsigned padding byte while retaining the same UUID.

That commit also succeeded and recorded the replacement file hash.
The running executable and recorded file therefore still differed.

The final implementation acquires and caches `BuildIdentity` in `Studio::open`.
This call occurs before project state, source copying, or native probing.

The implementation now checks all of these properties:

- The opened file device and inode match the kernel vnode for the loaded executable mapping.
- The mapping contains the loaded Mach-O header address.
- File mtime and ctime are not later than the kernel process launch time.
- The file UUID matches the loaded image UUID.
- File metadata remains stable through complete SHA-256 measurement.

The local `ProcRegionInfo` binding matches the macOS SDK layout.
Its size is 96 bytes, with address and size at offsets 80 and 88.

Controlled probes used `POSIX_SPAWN_START_SUSPENDED` on disposable executable copies.
This method loaded the executable before each mutation and resumed it afterward.

The final frozen binary produced these results:

- Intact executable: opened sequence 5 successfully.
- Different-UUID atomic replacement: `executable_identity_changed` for the mapped-image inode mismatch.
- Same-UUID atomic replacement: the same structured inode-mismatch failure.
- Same-inode byte change after launch: `executable_identity_changed` for a post-launch inode change.

The same-UUID replacement retained UUID `3f77c5785607371b84093238d3c0cb93`.
Its SHA-256 changed to `ea6c625b18ff60fe16920c866291d69b1462394d32173ce5e767eca77815c14b`.

An isolated correct refresh with the hardened binary committed sequence 6.
Its measurement records executable `a3fa63d5d1ef1c35260e71c2d4ea3a8daf7b88ee2e20d4adc2eba2c77d14bc30`.
It also records UUID `3f77c5785607371b84093238d3c0cb93`.
Its Cargo lock is `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.

That copied-store retry returned the same revision with `replayed: true`.
No production revision or original executable changed during these probes.

## Refresh guard and atomicity

`AssetImport.previous_measurement` remains part of the canonical request hash.
The guard compares it with the complete prior `StoredAsset` document hash.

Before opening the requested path, the commit now checks:

- The expected asset exists in the selected base revision.
- The exact byte count remains fixed.
- The complete `Origin` value remains fixed.
- The prior measurement token matches.
- The requested media kind matches the stored descriptor kind.

The commit repeats the immutable comparisons after staging.
The immediate transaction still checks the project head before publication.

Final-binary copied-store probes returned these structured failures:

- Wrong prior token: `measurement_conflict`.
- Changed origin: `origin_conflict`.
- Changed byte count: `origin_conflict`.
- Movie-to-audio change: `wrong_stream`.
- Unknown expected asset: `measurement_missing`.
- Correct guard with a missing path: `io_error`.

Only the corrected refresh intent appeared in the copied intent table.
The corrected commit advanced the copied head once, from sequence 5 to sequence 6.

Its immediate retry did not advance the head.
The copied staging directory was empty after all probes.

## Backward revision and request compatibility

`StoredAsset.measurement` remains optional and omits `None` during serialization.
`EncodedTiming.dts` follows the same compatibility rule.

`BuildIdentity.executable_uuid` is also optional.
Existing producer documents therefore retain their canonical bytes.

The final binary reopened sequences 2, 3, and 4 at their exact revision hashes.
It reproduced each source-measurement hash listed above.

Sequence 2 contains no `encoded_time` or probe identity.
Sequence 3 contains encoded PTS and duration, without encoded DTS or probe identity.
Sequence 4 contains all three raw clocks and its schema-1 probe identity.

The final binary replayed these exact import requests:

- `source-h264-clock-diagnostic-v1` to sequence 2.
- `refresh-panja-source-output-clock-v1` to sequence 3.
- `refresh-panja-output-dts-probe-identity-v1` to sequence 4.

Their request hashes remain:

- `6367c89c7efdf07d959f6fa46852d09c4dc20a91ce17094acc8b417ed5e2175b`.
- `9c797e92cb24262c4e49433d0b72fa3b0429425e1a89cc061879fee7482a1961`.
- `82af2025e7058d929edc55729045099d94f73055fe3057f086fa707f1da5c6cf`.

The final binary also replayed both stored export plans:

- Sequence-3 plan `096e80927a41df60f555d9d1fef64ac9e746cbd6a2634d3079aa62dff0df066b`.
- Sequence-4 plan `193c51fabd83382e6c320173930109a2065c2fdb0887c7a3722becbf2dda5fc4`.

No compatibility probe rewrote an old revision, request, or plan.

## Product export evidence

The A02 product output has SHA-256 `b96bdc925d362b0ea1333ba21b34fed6f28a95c0a9a8104171a51a4193092a2c`.
Its exact size is 640,834 bytes.

The artifact receipt is `e45fcdb1ff5a709c1db83290b9dffa7437e395311b7e0c9acda62c88d24e6e52`.
The initial verification is `2fce411d2dfc5c5878a60806d60a0d6960e1472cc25336510c31ed6dbfc908cc`.

The product export JSON has SHA-256 `c66013d453b98e3775806604024a799c155df08d20747c5c7a7681fb066bd916`.
The independent report has SHA-256 `db67347036aecd97fb1576607a156c67ca59be4ab98a97b453729871d2136a77`.

The independent verifier passed all 24 declared checks.
It confirms 24 H.264 frames at 2560 by 1440.

Every output PTS and declared source ordinal matches.
The minimum every-frame PSNR is `45.211483074847145` dB.

The output contains 48,000 decoded stereo PCM frames.
Both channels have zero-sample best lag.

The measured correlations are `0.9999769192056728` and `0.9999686975209157`.
The AAC track contains 50,176 encoded ticks before 2,176 ticks of native trim.

The report binds source video, canonical audio, output, receipt, and producer binary.
It also confirms no libav link.

No normal-speed watch or listen occurred.
Human and creative acceptance remain false.

## Capability and proof limits

Discovery now qualifies exact probe identity as a property of new or guarded-refreshed measurements.
It explicitly states that legacy measurements remain unbound until refresh.

The canonical audio in sequence 4 is one such legacy measurement.
Its exact bytes receive independent export verification, but its original probe lacks `NativeProbeIdentity`.

Discovery also states the one-measured-stream-per-file limit.
The current asset model cannot preserve several independently selected streams from one container.

The refresh guard now prevents changing between movie and audio descriptors.
It does not remove the single-stream model limit.

The complete compressed index is not complete decoded-source evidence.
Only the selected 24-frame range received plan-bound native decode coverage here.

Orientation, clean aperture, sample aspect ratio, color metadata, and sync flags remain unverified.
The A02 evidence does not establish those properties.

The product sequence-4 probe identity predates the final vnode and timestamp checks.
A guarded production refresh with a hardened frozen binary would close that self-enforcement gap.

The later frozen binary reports source-frame inspection capability.
This A08 review does not accept or reject that separate review unit.

The editor still lacks general layers, masks, motion, color operations, text, and audio mixing.
The full Panja hybrid film remains incomplete.

## Validation

`cargo fmt --all -- --check` passed.

`cargo test --locked --workspace` passed all 31 tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings` passed.

All behavioral probes used isolated state and disposable executable copies under `/tmp`.
No GPU or Resolve operation ran.

Cross-family model review was unavailable.
This document does not claim one.
