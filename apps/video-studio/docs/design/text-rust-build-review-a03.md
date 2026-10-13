# Rust A03 build review

Rust A03 passed source review, then failed its first actual release compilation.
The probe executable never ran. No native text result exists.

Offline lock generation first failed because the local index lacked `objc2-image-io`.
The pinned version was verified in the package's published source.
Online lock generation then succeeded. The parent read the complete resulting lock.
All ten direct pins match the reviewed Cargo manifest.
The lock contains 35 checksum-bound registry dependencies and one local package.

The exact dependency fetch and metadata observation succeeded.
Before compilation, the parent bound all 35 archives and 1,847 cached source files.
The source files total 21,194,525 bytes.
These are build path identities, not loaded compiler or native process identities.

The compiler reported one error at `src/native.rs:249`.
`CFAttributedString::new` requires an opaque `CFDictionary` reference.
The source supplies a retained typed `CFDictionary<CFType, CFType>` reference.
Ground the pinned dictionary type-erasure API and repair a separate A04 package.

The compiler also reported two unused `AffineQ16` imports and one unnecessary `mut`.
Remove those warnings in A04. Format only the new A04 source.
Do not modify the reviewed A03 source, generated lock, or build records.

The failed attempt rechecked 1,897 source, archive, and lock identities.
All matched their before-build bindings.
No successful binary, runtime observation, pixel comparison, or product acceptance is claimed.

The compilation used Rust 1.94.0, target `aarch64-apple-darwin`, macOS SDK 26.1,
deployment target 26.0, and the reviewed release profile.
Its exact command and environment changes remain in the build record.

## Saved identities

- A03 Cargo.lock: `ad54196e9d7d985a74a17eadf2ac19a02d59f1225582a57fd5d21cde9fb0d83a`.
- Dependency source closure: `06f970a1f145b9906c7443ac0672af5d8389942a2c9d78c70d5d75a7a6b73c67`.
- Compiler log: `3786b6b29b9e11d6c7a5dc99db42785c9f3c749625dfe3152b43382f30035b54`.
- Failed build report: `d75275d2a6cbfdff00e44e5147f16ddf933ec7819a69246e742d530955826c56`.

The next gate is A04 source review and a new isolated compilation attempt.
Native execution remains separately gated after a successful frozen build.
