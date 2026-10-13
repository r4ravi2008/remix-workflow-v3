# Rust A03 build-closure review

## Disposition

The saved closure is green for its stated purpose: an exact, path-bound record of the failed A03 release compilation. I found no P1 or P2 closure defect.

This review does not approve native probe execution. A03 produced no executable because compilation stopped at one preserved `E0308` error.

## Verified record

- The four drivers preserve the intended sequence: offline lock failure, online lock resolution, locked fetch plus offline metadata, then offline release compilation.
- The initial offline failure is retained. Cargo could not resolve `objc2-image-io` from the existing local index.
- The generated `Cargo.lock` is 8,415 bytes with SHA-256 `ad54196e9d7d985a74a17eadf2ac19a02d59f1225582a57fd5d21cde9fb0d83a`.
- The dependency closure is `06f970a1f145b9906c7443ac0672af5d8389942a2c9d78c70d5d75a7a6b73c67`.
- That closure records 35 registry packages, 35 archives, and 1,847 extracted source files.
- Every archive hash equals its `Cargo.lock` checksum. The offline metadata package set equals the closure package set.
- All ten direct dependency versions, default-feature settings, and requested feature sets match `Cargo.toml` and `dependency_policy()`.
- The resolved feature sets match the dependency closure.
- The A04 compile driver used `--offline`, `--locked`, `--release`, and target `aarch64-apple-darwin`.
- It selected the recorded absolute Cargo and Rust compiler paths. It also set the recorded SDK and deployment target.
- The compile log has SHA-256 `3786b6b29b9e11d6c7a5dc99db42785c9f3c749625dfe3152b43382f30035b54`.
- The attempt report has SHA-256 `d75275d2a6cbfdff00e44e5147f16ddf933ec7819a69246e742d530955826c56`.
- The compiler returned 101. The sole error is the typed-to-opaque `CFDictionary` mismatch at `native.rs:249`.
- The log also retains two unused-import warnings and one unnecessary-`mut` warning.
- The attempt correctly records build failure, absent binary, and false native, probe, product, playback, and creative states.

I independently rehashed the 1,897 unique frozen A03 records after the attempt. These comprise 14 package files, 1,847 dependency files, 35 archives, and `Cargo.lock`. No hash or size differed.

I also enumerated each current dependency source tree. Every recorded package has the exact current file set, count, and byte total.

## Authority and limits

The evidence binds path contents, absolute command arguments, reported versions, dependency archives, resolved metadata, SDK observations, and the compiler diagnostic.

It does not attest the loaded Cargo, compiler, linker, or SDK process images. It also does not freeze the complete inherited build environment.

Those limits do not weaken the preserved failure claim. They prevent stronger reproducible-binary or loaded-toolchain claims.

The closure records no native framework call, rendered output, playback, hearing, or product integration. Those states remain unverified.

## Gate

The separately reviewed A04 source may proceed to its own frozen format, typecheck, and build gate. That successor must use a new source freeze and build record.

This was a same-model-family review. No cross-family reviewer was available.
