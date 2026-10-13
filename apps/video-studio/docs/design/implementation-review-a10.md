# Implementation review A10

## Result

No P1 or P2 correctness defect remains in the reviewed saved-frame verifier.

The verifier accepts a complete record only after checking its semantic receipt identity, saved request, project revision, current source, PNG bytes, and decoded RGBA.

The A01 verifier returned `complete_verified` for all 16 sequence-5 frame records.
Each result binds the exact verifier executable and contains no perceptual or creative claim.

Review found one P2 classification defect in A01.
The corrected A02 verifier now returns `unverifiable_retained` for an unreadable directory.
No tested failure deleted or changed a frame record.

The full compositor and hybrid film remain incomplete.

## Review boundary

The reviewed project is `panja-hybrid-scratch-01a10fbd`.

The 16-record product report used `video-studio-frame-verifier-a01`.
Its SHA-256 is `2ab8f567cfd3e815628318fd7326f1450ea9fdaf9873dd7b971849f30b1e5c04`.
Its Mach-O UUID is `6def15fc8a293da49137f70725ec235a`.

The corrected verifier is `video-studio-frame-verifier-a02`.
Its SHA-256 is `beaade72828c4f0caf99c204fabaaf0cace6234039dcbeed74a4f64e7da2ff5a`.
Its Mach-O UUID is `b23f5fbdb6f63d8488e755f89cae8d04`.

The Cargo lock hash is `e1499a56b2de8f306dd29bddd44a72a4d2d420e1b3591cff8ba777b5eb123448`.

The reviewed implementation hashes are:

- `frame_verification.rs`: `b7df59ec6fcaa138ba52620d6da190144689e691f03b1c3062e266cbdbbe5c02`.
- `frame_directory_verification.rs`: `56df3782f7d043cce1e34affcf756304deee743dd3a40fb56f1954819f20639a`.
- `frame.rs`: `29464b4f53aa478fbfe567f9529d3b9a064b458f182628765e526358a80cb8b3`.
- `lib.rs`: `9e484cb1d015c94170471b6896ff779a0e664fe37ebbf78ad743e61a86772101`.
- CLI `main.rs`: `8ccf5f3dfb2684064f555f635a6246966f70d61cf9ea056f614d9c4a56541eec`.

I also traced revision loading, source verification, build identity, and stored media invariants.

I used copied state and copied frame directories for behavioral fault probes.
I did not operate the GPU or DaVinci Resolve.

Cross-family model review was unavailable.

## Defect found and fixed during review

The A01 verifier constructed its result before directory enumeration.
However, `fs::read_dir`, entry reads, and file-type reads used `?` outside the classification closure.

Those errors left the method before the state mapping to `UnverifiableRetained`.

I reproduced this A01 defect with a copied, otherwise complete record:

1. I changed the copied directory mode to `000`.
2. The A01 verifier exited with status 1.
3. The CLI returned `io_error: Permission denied (os error 13)`.
4. The copied directory and its three files remained present.
5. I restored the copied directory permissions.

That behavior contradicted the advertised classification of unavailable frame directories.
It forced callers to coordinate a separate transport-error branch for an ordinary retained state.

The current implementation maps path and enumeration I/O failures through `unavailable`.
That helper returns `unverifiable_retained` with the exact error text.

The corrected A02 probe used another copied complete record with mode `000`.
It exited successfully and returned `unverifiable_retained`.
Its reason was `Permission denied (os error 13)`.

The copied record's before-and-after byte manifests were identical.
A02 also returned `complete_verified` for a readable copy of the same record.

The new integration regression checks classification, retained request bytes, and unchanged project head.
The defect is fixed.

## Receipt and request identity

The request contains only a directory and expected `receipt_id`.
This is sufficient for one-call verification after project selection.

The verifier reads `receipt.json` with a 1 MiB bound.
It rejects symbolic-link leaves and changing file identities.

It parses the receipt into the schema type and hashes the serialized value.
The resulting identity is semantic JSON identity, not raw JSON byte identity.

A copied receipt and request remained `complete_verified` after whitespace-only reformatting.
The observed receipt ID remained `68e73f45032aa5a8714fc72e6336505dc96f0445eaed1dd6832359c2c5cfd278`.

This behavior matches the CLI capability text, which says “semantic receipt ID.”
Callers must not interpret the result as an authentication of raw JSON formatting.

The saved request is parsed separately.
Its semantic document hash must equal the request embedded in the receipt.

The copied request-mismatch probe returned `corrupt_retained`.
The expected-receipt mismatch probe also returned `corrupt_retained`.

These states mean the directory does not satisfy the caller's expected record.
They do not prove which actor changed the record or request.

## Revision and source relationship

The verifier loads the exact receipt revision.
Project inspection rehashes the stored snapshot before returning it.

The verifier then checks:

- The receipt project equals the opened project.
- The asset exists in that revision.
- The stored-asset document hash equals `source_measurement`.
- The asset byte count and source probe equal the receipt.
- The asset remains a natively decodable movie.
- The coded dimensions equal the receipt dimensions.
- The presentation ordinal exists.
- The prefix count equals ordinal plus one.
- The indexed presentation timestamp equals the receipt timestamp.

A copied source-measurement mismatch returned `corrupt_retained`.
A receipt for another project returned `foreign_retained`.

The verifier opens the current CAS object through `VerifiedSource`.
That object binds device, inode, size, mtime, ctime, and expected SHA-256.

It hashes the complete source before reading the PNG.
It hashes the same open source again after the PNG check.

A copied state with a changed source object returned `unverifiable_retained`.
The reason was `asset_tampered`.

This distinction is correct.
The saved frame record was internally readable, but the current source store could not establish its relationship.

The verifier also reopened a copied sequence-4 record.
That revision has `source_probe: null`.
It returned `complete_verified` with the expected PNG and RGBA hashes.

This confirms backward reading across the guarded source-measurement refresh.

## PNG byte and pixel verification

The PNG read is bounded by the maximum owned RGBA frame size plus 2 MiB.
The verifier checks the exact PNG byte count and SHA-256 before decoding.

It requires RGBA, eight-bit samples, exact coded dimensions, and no animation control.
The expected RGBA extent is validated before allocation.

The verifier decodes one complete image and hashes the decoded RGBA bytes.
It calls `finish`, so malformed trailing PNG data cannot produce completion.

The copied PNG-byte mutation returned `corrupt_retained`.
A valid PNG with a changed receipt RGBA claim also returned `corrupt_retained`.

`png_sha256` and `rgba_sha256` remain absent for those corrupt results.
They are present on the complete results.

The verifier does not decode the source movie again.
Therefore, RGBA equality proves saved-PNG consistency with the bound receipt.
It does not independently reproduce the frame from the movie.

## Classification matrix

The corrected A02 verifier produced these results on copied records:

| Copied condition | State | Material reason |
|---|---|---|
| Complete record | `complete_verified` | No reasons |
| Missing receipt | `partial_retained` | Required files absent; ownership unproven |
| Unknown extra file | `foreign_retained` | Unknown or non-regular entry |
| Foreign project receipt | `foreign_retained` | Receipt belongs to another project |
| Changed PNG byte | `corrupt_retained` | PNG differs from receipt |
| Changed saved request | `corrupt_retained` | Request differs from receipt |
| Invalid receipt JSON | `corrupt_retained` | Invalid JSON |
| Wrong expected receipt ID | `corrupt_retained` | Receipt differs from expected ID |
| Changed RGBA claim | `corrupt_retained` | Decoded pixels differ from receipt |
| Changed source measurement | `corrupt_retained` | Receipt differs from revision measurement |
| Unsupported receipt schema | `unverifiable_retained` | Schema unsupported |
| Changed current source object | `unverifiable_retained` | Source bytes or identity changed |
| Unreadable directory | `unverifiable_retained` | Permission denied during enumeration |

The verifier never deletes or writes a target record.

I recorded inode, mode, size, mtime, ctime, and SHA-256 for 33 copied entries.
I then repeated the complete, partial, foreign, corrupt, unsupported, and unavailable probes.

The before-and-after manifests were byte-identical.
Both manifest hashes were `a61a6e19df262856731c86d33761fa67353d69ff2c49828e957bf6ee2b580824`.

## Product evidence

`frame-record-verification-a01/report.json` has SHA-256 `28346c09ce80a92cde8bd96d5a3878415ccb197315417d40f6c87279161a2e46`.

The report contains 16 records.
All 16 states are `complete_verified`, and all reason lists are empty.

I compared the report against every saved CLI response and the A04 catalog.
The record sets and ordering match exactly.

For every record, I independently checked these byte relationships:

- The raw compact receipt SHA-256 equals the expected and observed receipt ID.
- The saved request equals the receipt request.
- The PNG SHA-256 equals the receipt, catalog, and verifier result.
- The current source byte count equals the receipt.
- The current source SHA-256 equals the selected asset hash.
- The result's verifier SHA-256 equals the frozen executable's actual SHA-256.

The 16 records reference two source CAS objects.
Both source objects passed complete SHA-256 remeasurement.

A02 did not produce a second 16-record product report.
I ran A02 against a complete sequence-5 copy, a sequence-4 copy, and every classification probe in this review.
Those results match A01 except for the corrected unavailable-directory classification.

The product verifier decoded all 16 PNGs and returned their receipt-bound RGBA hashes.
This review did not use a second PNG implementation for that decoding step.

The earlier A09 evidence independently reconstructed every catalog PNG.
Its three-frame independent observer also checked pixels and timestamps against native decoding.

The A10 report states `movieRedecoded: false` and `creativeAccepted: false`.
Those statements accurately preserve the proof boundary.

## Tests and static checks

The current workspace passed all 39 tests:

- 27 editor unit tests.
- 1 frame-directory verification test.
- 8 project-invariant tests.
- 3 replay-and-cleanup tests.

`cargo clippy --workspace --all-targets -- -D warnings` passed.
`cargo fmt --all -- --check` passed.

The PNG unit tests cover changed bytes, changed pixel claims, dimensions, allocation limits, and bounded document reads.

The frame-directory regression reproduces an enumeration failure.
It also proves retained bytes and an unchanged project head.

## Truthful capability boundary

`complete_verified` establishes a read-time relationship among:

- The caller's expected semantic receipt ID.
- The saved request and receipt.
- The immutable project revision and source measurement.
- The current complete source bytes.
- The exact saved PNG bytes.
- The decoded PNG RGBA bytes.

It does not establish raw receipt JSON byte identity.
It does not freshly decode the movie.
It does not attest the historical decoder process.

It also does not establish playback, hearing, creative acceptance, display orientation, aperture, sample aspect ratio, or color accuracy.

The source and directory checks remain observations before and after work.
They do not exclude changes that occur and are restored between observations.

These limits are stated in the result scope and capability inventory.

A10 closes the A09 recovery gap for complete, partial, foreign, corrupt, and unavailable retained frame directories.

No P1 or P2 issue blocks the next bounded editor unit.
The general compositor, exact film review, and full Panja hybrid film remain unimplemented and unaccepted.
