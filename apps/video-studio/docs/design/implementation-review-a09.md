# Implementation review A09

## Result

No P1 defect remains in the reviewed source-frame inspection unit.

The request binds one immutable revision, asset, source measurement, and presentation ordinal.
The decoder checks every prefix PTS before returning the selected coded frame.

The fresh 16-frame catalog uses sequence 5 and hardened source measurements.
All 16 PNGs reconstruct to their declared RGBA hashes.

An independent observer passed all 15 checks across three selected frames.
The final saver passed two iCloud cases and the isolated ownership fault probes.

One P2 source-binding limit remains.
AVFoundation opens the pathname separately from the retained and hashed source file descriptor.
The before-and-after observations do not exclude a replacement that is restored between observations.

The receipt and discovery output state this limit accurately.
The full hybrid film remains incomplete and unaccepted.

## Review boundary

The reviewed project is `panja-hybrid-scratch-01a10fbd`.

The fresh catalog binds revision `618c34626ab00ee749be3639afc026c52f745acb32e5d6bf0e97e9217041c599` at sequence 5.
Its parent is sequence-4 revision `9b543f456907585ad9a128a40540b56cabd8da0dba90613421bca80733afd980`.

The movie assets and source-measurement hashes are:

- OG AV1: asset `a2247e96ab4335eb6b365ef52b6203e53377c6cf317ebb2e156789e6bd470b7f`, measurement `9d45f154abd136e0589185e30287e350e39195ad484528a4e138eae439c5b24f`.
- Publisher H.264: asset `b78939035919803ad33cd60979be7f1fb28798d8a34404c2881371300ce167ca`, measurement `39ba9414ffab868d506be8a3a9dd9920d49abaad955f198d41138f58cc749a09`.

Both measurements bind hardened probe producer `552afe76372dfa4d726062630253781050c48447f85cb16fb9279a041899f81b`.
Its Mach-O UUID is `3822e3fb3fc73720a44ad52931e8cb15`.

The 16-frame catalog used frozen decoder A04.
Its SHA-256 is `5439b204f99775d10b16901142e0eabb3487b6d7f9e2344ccd48f487fd0fc85e`.
Its Mach-O UUID is `880b3b4769a33df5923eae5f47d83b2a`.

The final saver is frozen decoder A06.
Its SHA-256 is `168e6518df01f657fec992229de7f98a4282e39c1a598aba0a3b9370f561476a`.
Its Mach-O UUID is `76cc25ced14936fe83d64ebbb477c6fc`.

A04 and A06 use the same frame decoder and source verifier.
A06 changes output finalization after the A04 catalog completed.

The shared Cargo lock hash is `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.

The main evidence files are:

- A04 catalog: `native-frame-inspections-a03/catalog.json`, SHA-256 `a12d1ef0650c681600d62e07b7b3e0db8b4ec725eee2f4166b045f07125c8041`.
- All-frame equivalence report: `pixel-equivalence-to-a01.json`, SHA-256 `e2747e55f9cd58ed24467ec5c888f5d248f13f0ce6928effa530c11424b83c71`.
- Independent A03 report: SHA-256 `7b05bc578edaac673fcd8dfc98d28c40f3521f61978cc79564e6ee954c1d0fff`.
- Independent observer: SHA-256 `76fb370919d36592d1106c6b19f06591cfa3f5070c84fc514d02a58e20217959`.

The separate H3 motion diagnostic and its GPU work are outside this review.

## Defects found and fixed during review

### Failure cleanup could delete a competing file

The first saver removed its output directory after a failed write.
It identified ownership from the pathname alone.

An isolated actor created `receipt.json` after the product created the directory.
The product returned an error and then deleted the actor's file and directory.

The saver now retains every partial directory and file after an error.
It writes `request.json` first to identify the attempted inspection.

### Path-based writes allowed directory substitution

The first retention fix still reopened every output by pathname.

An isolated `RENAME_SWAP` probe exchanged the new directory with a foreign directory.
The product wrote its PNG and receipt into the substituted directory and returned success.

`OwnedDirectory` now pins the canonical parent and new directory with open file descriptors.
It creates the directory with `mkdirat` and each file with `openat`.

Every file uses `O_CREAT | O_EXCL | O_NOFOLLOW`.
The saver checks parent, directory, and file device and inode identities before success.

The final A06 probe exchanged the target directory atomically.
A06 returned `inspection_ownership_changed` and preserved the foreign marker.

A second probe exchanged the parent directory.
A06 returned the same structured error and wrote nothing into the foreign parent.

### Output ctime rejected valid cloud persistence

A04 required ctime stability while hashing the saved files.

The iCloud refresh completed 11 frames before rejecting `panja-000960`.
The three output files remained present and byte-consistent.

The PNG contained 2,289,061 bytes and matched SHA-256 `6148de51190f3a794b95748ec666243d8df1106018af4045f891321a4fd813a7`.
The saved request also matched the receipt request.

All three files later contained `com.apple.provenance`.
Their ctimes were four to six seconds later than their mtimes.

This is strong evidence of a metadata-only update.
The exact actor and timing were not observed.

A06 no longer treats ctime changes as content changes.
It retains file identity, length, mtime, and complete SHA-256 checks.

Two A06 inspections then succeeded in the same iCloud workspace.
Their receipt IDs are:

- `panja-000960`: `09308c802bebb4a35553adf858578f01f927e92671d0e88b16c284036319477d`.
- `og-001680`: `6ce83346922eb0cdb56eea816bcb5ca3935938b18d7bd0248b2d04293867be99`.

Both complete output sets contain `com.apple.provenance`.
Their raw receipt hashes equal the returned receipt IDs.

## Request binding and preflight

`Project::inspect_frame` first reopens the exact requested revision.
It rejects a missing revision or an asset absent from that revision.

The request must contain the exact stored-asset document hash.
This binds bytes, origin, descriptor, and optional probe identity.

The operation requires a measured movie with successful native first-frame decode.
It validates coded dimensions against the 128 MiB pixel limit.

The presentation ordinal must exist in the immutable sample index.
The decoder copies the indexed prefix through that ordinal.

Observed copied-state failures were:

- Missing revision: `revision_missing`.
- Missing asset: `source_frame_error`.
- Wrong measurement: `measurement_conflict`.
- Audio asset: `wrong_stream`.
- Out-of-range ordinal: `source_frame_error`.
- Changed CAS bytes: `asset_tampered`.

None of those failures created an output directory.

An A06 copied-state tamper changed one byte in the OG CAS copy.
A06 returned `asset_tampered` before creating the requested output directory.

The CLI performs inspection before `save_new`.
An existing output directory is therefore detected after decoding.

This ordering preserves a clean output tree after decode failures.
It can waste a prefix decode when the requested output already exists.

## Source clock and pixel authority

The product requests BGRA output from AVFoundation.
It checks each decoded output PTS against the same ordinal in the immutable index.

The check uses exact rational equality.
It does not infer a nominal rate or a timestamp offset.

The 16-frame catalog covers these presentation ordinals:

- OG AV1: 120, 480, 840, 1200, 1560, 1608, 1656, 1680, 1728, and 2160.
- Publisher H.264: 360, 960, 1920, 2880, 3840, and 4800.

Each stored PTS equals `ordinal * 512 / 12288` for these sources.
The last H.264 inspection therefore reaches exactly 200 seconds.

Every selected frame is 1920 by 1080.
The product copies tight coded pixels, converts BGRA to RGBA, and encodes a deterministic RGBA PNG.

I rehashed every saved receipt and PNG in the A04 catalog.
Every raw receipt hash equals its catalog receipt ID.

I decoded all 16 PNGs with a separate standard-library PNG reader.
Every reconstructed RGBA hash equals the receipt value.

The A04 frames are pixel, clock, and PNG equivalent to all 16 historical A01 references.
The historical files remain the actual image-generation references.

The fresh catalog does not rewrite that creative lineage.
It establishes exact technical equivalence under the hardened sequence-5 bindings.

## Independent observation

The A03 independent report checks `og-001608`, `og-001680`, and `panja-001920`.

It passes dimensions, ordinal, RGBA hash, PTS, and PNG hash for each frame.
That is 15 passing checks.

The observer is a separate executable and code path.
It shares AVFoundation with the product decoder.

The observer reads extension-bearing workspace source paths.
Those paths have the same complete SHA-256 identities as the project CAS assets.

The preserved A01 helper failure used an extensionless CAS path directly.
AVAsset inferred no video track and returned a helper failure.

The product was not implicated.
The product supplies an explicit MIME override after checking the container header.

The A01 failure record remains preserved with `productDefectObserved: false`.

## Output ownership and persistence

`FrameInspection` exposes immutable receipt and PNG getters.
`save_new` consumes the inspection and requires a new directory.

The directory is created with mode `0700`.
The three files are created with mode `0600`.

The saver keeps each open file descriptor through final verification.
It verifies the descriptor-relative entry, inode, file type, byte count, mtime, and SHA-256.

It then syncs the directory and parent before returning paths.

The A06 isolated probes established these behaviors:

- A normal save produced coherent `request.json`, `source-frame.png`, and `receipt.json`.
- A pre-existing directory returned `io_error` and preserved its exact file.
- A competing `receipt.json` returned `io_error` and preserved that foreign receipt.
- Atomic directory and parent exchanges returned `inspection_ownership_changed`.
- Continuous PNG mutation returned `inspection_ownership_changed` and retained all partial files.

The competing-receipt case also retained the completed request and PNG.
The caller can inspect the exact partial state after an unknown outcome.

No public operation verifies or resumes a saved frame directory.
A retry at the same path returns `io_error` because exclusive creation is intentional.

This is a P2 recovery gap for automated callers.
Add a read-only `asset.verify-frame-inspection` operation before using these directories as durable review records.

That verifier should recompute the receipt ID, request equality, PNG size, PNG hash, and decoded RGBA hash.
It should classify complete, partial, foreign, and corrupt directories without deleting them.

## Backward reads

The receipt schema does not change stored revisions or source measurements.
Frame inspection remains an external read operation on project state.

A06 reopened sequence-4 revision `9b543f45...` on copied state.
That revision has no source probe identity for the OG asset.

The resulting receipt correctly stored `source_probe: null`.
It produced the same first-frame PTS, RGBA hash, and PNG hash as sequence 5.

The sequence-5 receipt includes hardened probe A03.
The two receipts remain distinct because their revision and measurement bindings differ.

No inspection advanced a project head or created an intent record.

## P2: AVFoundation does not consume the verified source descriptor

`VerifiedSource` opens the CAS path with `O_NOFOLLOW`.
It retains that descriptor through decode.

It checks device, inode, size, mtime, ctime, and complete SHA-256 before decode.
It repeats the same checks and full hash after decode.

`media::with_track` separately gives AVFoundation the canonical pathname.
AVFoundation does not consume the retained descriptor.

A precise actor could replace the pathname after the first observation.
The actor could restore the original inode before the second observation.

Same-dimension media with matching prefix PTS could then produce pixels under the wrong asset identity.
The current checks would not prove which vnode AVFoundation decoded.

This scenario requires deliberate concurrent mutation of the owned CAS.
It did not occur in the reviewed artifacts.

The receipt scope states that changes between observations are not excluded.
Discovery repeats the same qualification.

For an exclusive binding, decode a private hardlink or copy whose inode matches the verified descriptor.
An AVFoundation adapter that consumes an already-open descriptor would also close this gap.

## Performance and proof limits

Every inspection decodes from ordinal zero through the selected ordinal.
The 16-frame catalog repeats those prefixes independently.

The 90-second decode deadline is checked between sample reads.
It cannot interrupt a blocked `copyNextSampleBuffer` call.

The outer track operation has a 120-second receive timeout.
The reviewed sources completed, including H.264 ordinal 4800.

No receipt records elapsed time, peak memory, or cancellation latency.
This unit does not establish arbitrary-source throughput.

The product returns coded raster pixels.
It does not apply or verify display orientation, clean aperture, sample aspect ratio, or color metadata.

The independent checks cover three of 16 frames.
The all-frame checks independently validate file and PNG structure, but reuse product-produced receipts.

No complete source playback was watched.
No full song was heard.
No creative acceptance occurred.

This unit does not prove motion quality, editing continuity, composition, or final-film delivery.

## Validation

`cargo fmt --all -- --check` passed.

`cargo test --locked --workspace` passed all 35 tests.

`cargo clippy --locked --workspace --all-targets -- -D warnings` passed.

All reviewer fault probes used copied state and output under `/tmp`.
No reviewer probe changed the original database, CAS, source files, catalog, or frame receipts.

No GPU or Resolve operation ran during this review.

Cross-family model review was unavailable.
This document does not claim one.
