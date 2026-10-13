# Existing-media admission next design A04: independent peer review

## Scope and evidence

This is a source and design review. I read the frozen A04 design, the preserved A03
design and reviews, the A03 admission contract, and the current Rust model and admission
seams. I did not edit product source, build, test, execute a helper, invoke native media,
or change state.

| Item | SHA-256 |
| --- | --- |
| A04 design | `accdf7c3f326791c33de5a72a1d34d241eca19867de79acd95f38f87762fb64f` |
| A03 design | `ff76cab393b1c92468243622e817523b9c4d7f3fd47eef373e6708892b67509b` |
| A03 independent review | `4cd1333ee1ddea5ad8190187ace626f09cb79dd32cf429c3ca7d659041cafbd5` |
| Admission contract A03 | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |

The nine current source files still match the hashes bound by A04:

| Source | SHA-256 |
| --- | --- |
| `model.rs` | `eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1` |
| `plan.rs` | `17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1` |
| `project.rs` | `a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c` |
| `composition.rs` | `88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5` |
| `media.rs` | `490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d` |
| `layers.rs` | `3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655` |
| `movie.rs` | `5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3` |
| `pcm.rs` | `7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a` |
| `exports.rs` | `13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc` |

## Result

A04 closes the broad A03 old-media field-inventory finding at the design level. Its
`M_source_old`, `M_draft_old`, and `M_plan_old` tables cover the current Snapshot and
ExportPlan media owners, including nested strings, vectors, sample timings, warning and
decode records, lineage inputs, measured labels, canonical audio labels, evidence, and
identity metadata. The A04 count domains inherit the A03 JSON, per-value, local-vector,
and selected-timeline bounds.

One P2 remains in the application-owned error overhead. It is small but concrete. Plan8
must remain disabled until it is resolved and measured.

## P2 finding: `StudioError.code` is an uncharged heap string

The current `StudioError` is `code: String` plus `detail: String` in
[`lib.rs`](../../crates/editor/src/lib.rs#L58-L63). A04 charges `H<StudioError>` and one
`string_policy(4,096)` detail buffer in `O_prepare`, `O_replay`, and the 32 execution error
slots. It does not charge or bound the `code` string capacity.

`H<StudioError>` covers both String headers, not either heap allocation. The current
`StudioError::new` copies its code, and `From<std::io::Error>`, `From<rusqlite::Error>`,
and `From<serde_json::Error>` can create details before the capped formatter described by
A04. Therefore the stated overhead is not exhaustive for the current type.

Repair one of these ways before implementation approval:

1. Use a fixed bounded error-code representation for Plan8 and account for its inline size.
2. Keep `String`, define a maximum code length, reserve it before construction, and add
   `string_policy(max_code_bytes)` to every live error slot and preparation error owner.
3. Route every fallible conversion through a bounded constructor that preserves the fixed
   overflow record without first allocating an unbounded detail or code.

The repair must cover prepare, replay, execution, owner-transition records, cancellation,
channel failure, callback failure, and worker-join paths. A negative control should exceed
the code or detail budget before typed error construction.

## Ownership and lifetime checks

The A04 source table closes the A03 media ownership gap. It explicitly charges:

- Snapshot and ExportPlan roots, map node high-water, map keys, and nested values;
- all four Origin variants and their source-edge vectors;
- image, movie, and audio descriptor strings and nested sample, warning, label, alpha,
  and measurement records;
- timeline, track, clip, identity, source-range, curve, motion, and mask storage;
- canonical `AudioBinding`, `VideoUse.presentation_ordinals`, `AudioUse`, and both evidence
  vectors; and
- source, draft, plan, tree, validation, compile, serialization, channel, path, error,
  callback, Arc, and worker-control owners.

The move ledger correctly keeps source and destination tree permits live during partition,
charges timeline-to-use identity clones twice, and transfers selected fields without double
charging moved nested allocations. The source-remnant term prevents a moved selected timeline
from appearing in both source and draft, while retaining unselected source owners until their
declared drop boundary.

The phase equations now include `C_old_validate`, `C_old_compile`,
`C_old_plan_validate`, and `O_prepare`. Replay drops raw JSON and parser scratch before
worker creation. Execution starts from one immutable plan owner and keeps `J_live = 0`.
These rules close A03's source/draft overlap and omitted-preparation-term findings.

The exact `size_of` values, channel control envelopes, and concrete fixed-record multiplicities
remain implementation gates. That is consistent with A04's design-only status. An
implementation must publish the inventory named by `OldMediaChargeKind::COUNT` and reject
any unlisted variable-capacity owner.

One conditional boundary needs to be stated during implementation: `PreparedExport` contains
an owned `plan_id` hash alongside `ExportPlan` (`plan.rs`), and `prepare_export` computes it
before storage (`project.rs`). If that wrapper remains pipeline-owned during `store_peak`, its
hash capacity must be included or the handoff boundary must be explicit. The A04 plan-root
wording does not by itself identify this wrapper.

## Channel-order and measured-label checks

A04 correctly keeps `MediaDescriptor::Audio.measured_channel_labels` (`CL`) separate from
`AudioBinding.channel_order` (`CO`). It requires a measured-label count equal to the source
descriptor's bounded channel count, a canonical-order count equal to that descriptor, and
exactly two labels for the selected canonical source. It separately limits measured and
canonical label bytes and the canonical basis string.

The required zero, one, eight, and nine channel cases, independent CL/CO mutations, and
selected stereo checks are sufficient to prevent a measured label from being treated as an
authoritative channel-order decision. The design does not claim that label bytes or labels
are equal across the two records.

## Input bounds and compatibility

A04 inherits A03's 64 MiB body, depth, count, per-string, per-warning, per-label, local
vector, source-edge, sample, timeline, track, clip, evidence, and curve-key limits. Its
token gate measures decoded bytes before typed construction, and its bounded visitor repeats
counts and checks actual capacities after `try_reserve_exact`. This closes the previous
unbounded existing-media string and vector boundary, subject to the error-owner repair above.

The compatibility statement is coherent. The design keeps `ExportRequest`, Snapshot schema1,
Plan2 through Plan7, legacy serializers, historical receipt bytes, and legacy worker behavior
unchanged. Plan8 uses additive entry points and a private table selected before the body read.
The required fixture readback remains a later implementation proof; this review did not run it.

## Verification limits

This is a same-family design review. It reuses the A03 contract, A03 design, and the same
current Rust source family. It does not independently implement the ledger or validate the
claimed capacities. No Plan8 runtime exists at the bound source hashes.

The review therefore does not establish allocator metadata, physical memory, RSS, SQLite
page-cache memory, native framework or codec buffers, native decoding coverage, throughput,
output correctness, cancellation behavior, Plan2–7 byte readback, playback, hearing, or
creative acceptance. Root's separate Runner A03 controls do not provide any of those claims.
