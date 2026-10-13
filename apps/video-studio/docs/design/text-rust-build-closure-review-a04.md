# Rust A04 build-closure review

## Disposition

The saved A04 build closure is green for its stated path-bound purpose.
I found no P1 or P2 defect in the recorded lock, dependency, or release-build chain.

The release build completed and produced the recorded Mach-O file.
The executable was not run during the build or this review.
Native text feasibility and output acceptance remain unverified.

## Verified chain

- The source freeze binds all 14 reviewed A04 source and contract files.
- The separate correction record binds the complete `src/model.rs` SHA-256.
- The preserved A05 attempt stopped on its absent gate with an empty `steps` array.
- The A05 attempt did not start Cargo.
- The A06 driver resolved the A04 lock offline and read locked metadata.
- The A04 lock differs from A03 only by the root package name.
- The root dependency lists are equal.
- All 35 non-root package records are byte-equivalent between both locks.
- All ten direct policies, 35 package archives, and 1,847 cached source records equal A03.
- The A07 command used `--offline`, `--locked`, `--release`, and target `aarch64-apple-darwin`.
- The command used the recorded Cargo path, Rust compiler path, SDK, and deployment target.
- The release command returned zero after 13.81 seconds.
- The log records three dead-code warnings and no error.
- The saved binary is 1,168,656 bytes.
- Its SHA-256 is `37e5a9be513347eabbf0f313158340e5a8211220354ab619b492e08a1dbe95b5`.
- The build report remains `probeExecuted: false` and `productIntegrationAllowed: false`.

I independently rehashed the 1,897 unique post-build records.
They comprise 14 source files, 1,847 dependency files, 35 archives, and `Cargo.lock`.
Every current byte count and SHA-256 matches its frozen descriptor.

I also rehashed the build gate, A07 helper, build log, step record, attempt report, and binary.
Their current identities match the recorded values.

## Authority boundary

This evidence proves a successful compile and link from the recorded path contents and command configuration.
It does not attest the loaded Cargo, compiler, linker, SDK, or framework process images.
It does not freeze the complete inherited environment.

The A07 success path rechecks Cargo, Rust, SDK settings, framework plists, source files, dependencies, archives, and the lock.
The report stores the full expected identities and a zero-error postcheck count.
That is sufficient for this bounded path-level build claim.

The separately authored schema-2 native build manifest and pure comparator are outside this build-closure review.
They require their own identity gate before native execution.

## Acceptance boundary

This review accepts only the A04 isolated release-build closure.
It does not accept native API behavior, font selection, glyph shaping, alpha-mask orientation, memory use, product integration, playback, hearing, lyrics, or creative quality.

No native probe, product process, GPU operation, or Resolve operation ran during this review.

## Exact reviewed identities

| File | SHA-256 |
| --- | --- |
| `rust-source-freeze-before-build-a04.json` | `609581356799af5f63408a6e1d490485b5e9e2c5117536e08fcacd588e978a10` |
| `rust-review-model-hash-correction-a04.json` | `395cc76d1d81a9ef0cd03f36357d7c70c4023cff959b6d3e614da4631fd388b4` |
| `rust-format-transfer-review-a04.json` | `a674b29884514787d35272562d7ad6535b7c490bbcdd494210661925a2baf746` |
| `rust-source-lock-release-a04.json` | `4cc512a94f61909a78708bb3b1b4ef04cd1c28f1259d81afb75179249a4fa0da` |
| `run_rust_build_a06.py` | `fb9e6cc76f43515f2b622ea40678d8cb437094fb533f61aa5bd828d493cd7904` |
| `rust-build-attempt-a06/report.json` | `85b998c8ff0c6d6481dae3bd3c69539573cbb22039ad98557c55f6f4d015e408` |
| `feasibility-rust-a04/Cargo.lock` | `6547ed5e910e28a208c38fb8307f4bfc23709f9acc3c0c6e26de978721dd28c4` |
| `rust-dependency-source-closure-a04.json` | `f4eb713a3fa3ee3f89fe9ba5350b518b942971879ab97d0cc11f406c48fe99fa` |
| `rust-lock-dependency-review-a04.json` | `3c2053f54a524840933936b085f112e212acde7d22673bfef6d7349b3047d433` |
| `rust-compile-release-a04.json` | `24cd4f35c8b555a3159b3d0b61eb8f5819542c5b2a3072c5ec0038afb25c4c8c` |
| `run_rust_build_a07.py` | `9bcb134366fc5eedce26413ef0c69d30c55baf1fe066fc198dd9bb7338823c50` |
| `rust-build-attempt-a07/release-build.log` | `d041293a0669b01b275a0ad89528e55683db998200e9c0d353e9c8f7beaf928a` |
| `rust-build-attempt-a07/release-build.json` | `1f9ed015b99e0af2bfd7e404bf8394f4bad60956b9039532ec4dc078860d2894` |
| `rust-build-attempt-a07/report.json` | `276772687e588f3e2e44ede0de88801d4533dfb514a139075b6a6c7445310e87` |
| `native-text-feasibility-rust-a04` | `37e5a9be513347eabbf0f313158340e5a8211220354ab619b492e08a1dbe95b5` |

This review is within the same model family. No cross-family reviewer was available.
