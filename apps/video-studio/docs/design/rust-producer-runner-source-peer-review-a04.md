# Rust producer runner A04 source peer review

## Disposition

The scoped A04 source review is complete. I found no new P1 or P2 finding.
A04 is a narrow source successor that repairs the preserved A03 Darwin libc
field error. Compilation of A04 remains pending.

This is a same-family, nonblind, source-only review. I read the complete
A03-to-A04 delta, A04 source and affected documents, the A04 manifest, and the
preserved A03 build report, stderr, and preflight records. I did not compile,
import, execute, or launch any package or native child.

## Manifest verification

The frozen package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a04`

`source-manifest-a04.json` has SHA-256
`961dd0e2cd7525ec8523958a97a0ac109aabfcac3393adfb1b36d846c9280576`.
All eight rows match their current bytes. They total 93,375 bytes. The
documented aggregate recomputes to
`c658f23cd62b58cfb698ee2738cecbc2bb9ac7fa8e17062dfc642d7eca9a890a`.

The source rows are:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `Cargo.toml` | 490 | `5c0118b0b9080873c760e249d978b5ef24240d3dca7e09cd4fe5e390999ad0b1` |
| `README.md` | 1,811 | `55a1fa0c75e7e83e4587e6e1921bab614ab84e03b6f730cbd95fc7686f9ccba1` |
| `output-schema-a04.md` | 3,079 | `c5ed756f746cf868a053fe0ad1a71173f97baca0348d501e9bb17d437f937b1f` |
| `pure-fixtures-a04.json` | 6,548 | `257e6f7e1eda658c457bca22735773c5a51175cc5d91a9ee67773a9dafff6387` |
| `runner-contract-a04.md` | 12,098 | `9ca8e1cff20654634d0156042ef831ddc63db80ecee38ba04b036486e06106db` |
| `src/lib.rs` | 65,284 | `2414938b08c109d4953d11ec2962aa8095f01f7cb47e2936ed2e4dd9206e055b` |
| `src/main.rs` | 96 | `b4d67b3f06c1451c6d1a0f6dd2ba7d1ccfe2d0c2dac63124ad007fa0a1187933` |
| `src/pure.rs` | 3,969 | `b76f4edd50ca097e7aadb458c2325b02b874f9fdb1162a3f887c1c1f08c4ed1e` |

The manifest marks the package `source_authored_unbuilt_unexecuted`, with no
compiled, executed, or native-child evidence.

## Delta and failed-build binding

The only runtime-source change is `src/lib.rs:1613-1617`. A04 replaces the
unavailable `st_mtimespec` and `st_ctimespec` fields with the flattened
`st_mtime`, `st_mtime_nsec`, `st_ctime`, and `st_ctime_nsec` fields. The
seconds and nanoseconds are combined into the same signed nanosecond values.
`src/pure.rs` is unchanged. Cargo, `src/main.rs`, fixtures, and documents only
rename the package and A04 identities, except for the added binding record.

The referenced fixed dependency source exists at the contract path, is 198,124
bytes, and matches SHA-256
`bb4cf053d10bba3cae21616cdf8b80e53ec8b0bcd6f4a9ab257c2c4d2379b8da`.
Its `stat` definition exposes the four flattened fields at lines 329-352.

The contract binds the preserved A03 failed build to:

- report: `rust-producer-runner-build-attempt-a01/report.json`, SHA-256
  `f2d9ff34dddca8db84fe604c730f03a1513d557185ba92b273e5c953d8421d3b`;
- stderr: `0-stderr.log`, SHA-256
  `9f0d4a3654d9b4709cfa43d9b80125d1bad01303cbdbffca8338dfc20f9e02be`;
- preflight: `preflight.json`, 52,549 bytes, SHA-256
  `067a42019829b4f655ef443580d92ab26e5c862966322a19f1149764caf6fc62`.

The report state is
`rust_producer_runner_a03_build_or_cli_failure_preserved`. Its fixed rustc
phase targets A03 `src/lib.rs`, returns code 1, and binds the same stderr
identity. The stderr contains four E0609 errors for `st_mtimespec` and
`st_ctimespec`. The attempt stopped before CLI invocation and native-child
startup, so it is valid failure evidence and not A04 build evidence.

## Limits

This review verifies source identity and the causal predecessor binding. It
does not verify that the A04 fields compile for the selected target, that
timestamp values match runtime macOS observations, or that any lifecycle,
subprocess, native, media, audio, GPU, Resolve, product, WATCHED, HEARD, or
creative behavior works.

