# Native preparation A05 and pure harness A04 — source review

## Result

I found no P1 or P2 in the requested source-only repair.

A05 changes one saved-report expectation. It now requires the launcher recorded
in tool observation 2. The separate resolved `rustcExecutable` evidence remains
unchanged.

The A04 harness changes only its external crate binding and related labels. All
five control bodies remain byte-preserved from A03.

This is a same-family, nonblind review. I knew the preserved A07 failure and
the requested correction. I did not compile, link, import, or execute source.

## Frozen identities

The A05 source manifest is 3,292 bytes with SHA-256
`c6b9e864cf7061f8ec906e363a372259aadb0da89194980a2397418c0d6f17a5`.

| A05 file | Bytes | SHA-256 |
| --- | ---: | --- |
| `src/lib.rs` | 2,565 | `829aa1489889ff9749c0df68bf7835143d2b973c9a5f1e7544decff0abdcc5c1` |
| `src/saved_report_adapters_v1.rs` | 59,080 | `a6321d2ddf5165a3a7c9f9376a82fc6fc2f58832e0d78f958730e69a32ad0bd4` |
| `implementation-contract-a05.md` | 3,628 | `f51b1f87a17296d3b0b03abbd533f9160014018b88a3a728b3877396a353647a` |

All three manifest rows match their saved bytes. Their total is 65,273 bytes.

The harness manifest is 2,209 bytes with SHA-256
`d31ee5b56a249dee13b244ecf6d61d4beeed94633da80388812eeabce16d436a`.

| Harness file | Bytes | SHA-256 |
| --- | ---: | --- |
| `pure-test-harness-a04.rs` | 5,745 | `d0f6e604d1c48048f10762c3ec3d88b3dda0bcb0d2069ae37fb8e8bcc886fd0d` |
| `pure-test-harness-contract-a04.md` | 2,615 | `36ce00e658707668158f5cabd337a5f7176d4a7bb3dc8804abdb8b926ad898eb` |

Both harness rows match their saved bytes. Their total is 8,360 bytes.

## Repair assessment

The A04-to-A05 adapter diff changes only `TOOL_ARGV[2][0]`:

- old: `/Users/aira/.rustup/toolchains/stable-aarch64-apple-darwin/bin/rustc`;
- new: `/Users/aira/.cargo/bin/rustc`.

The fixed toolchain report records the new value in observation 2. It records
the old value separately in `rustcExecutable.path`. The adapter still validates
that separate executable observation.

The A05 crate root changes its adapter path from A04 to A05. Its other local
module paths remain unchanged. The following frozen authorities still match:

- A04 source manifest: `25e65b31679d6bb05d02249bed14595971367449f0b7a795480803abb41b9b5d`;
- A03 support manifest: `d1129e1064f1ecb82eea88e8d98706181c32ebbb5ac6a16b191b7d1615c01106`;
- RoleIndex A02 manifest: `ebe268388896fb97ac46277aea71c43d1dfdb13af22ed10cbdc8c9f8c8241c98`;
- toolchain report: `c22b5cb70e490131c14456f021cfb11a843a67140d26ec93d759fb5ac29c87c8`.

## Harness assessment

The A03-to-A04 harness diff changes the crate from A04 to A05. It updates only
the corresponding module alias, comments, and two assertion messages.

The five function bodies and their execution order remain unchanged. They
retain the following controls:

1. Saved expansion and authority counts.
2. Baseline and fresh identity mutations.
3. Every observer branch, including normal pixel failure.
4. Both combined source-control summaries.
5. Unavailable pinned acceptance.

The planned direct build still uses `panic=abort` and thin LTO. It does not use
Cargo or the Rust test harness.

## Preserved failure and remaining gate

The A07 harness build succeeded before this repair. Its execution aborted on
the first assertion with `tool_argv_value`, observation 2, token 0.

The preserved A07 report is 6,906 bytes with SHA-256
`04ef6b587e1303436d41991f7863d3a4ae813b87e83b0fca161c97079a32d19b`.
No control reached a passed line.

The A05 and A04 source manifests do not absorb that attempt as source
authority. A later build-and-control closure must bind the A07 report and its
parent readback as preserved failure provenance.

The A05 crate and A04 harness remain unbuilt and unexecuted. A later operation
must preserve the exact build commands, input identities, binary identity,
stdout, stderr, exit status, and six expected output lines.

## Scope

This review establishes source readiness for the next bounded build and pure
control attempt. It does not establish successful compilation, execution,
loaded-code identity, process launch, native frameworks, media, GPU, Resolve,
watched review, heard review, or creative acceptance.
