# Rust producer runner A17 source peer review

Review state: complete source-only peer review. The A17 Rust package has no new source P1 or P2. One inherited A08 scalar check needs a versioned wrapper update.

## Reviewed identities

The reviewed package is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a17`

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `direct-build-recipe-a17.json` | 47,943 | `6fa505ab5f491e09044f78c814c86a92bb5531716dd2321bde504c4a1f130e50` |
| `source-manifest-a17.json` | 122,137 | `4a018cbf2547b58c86993e59829a6b87fe7e40604681190bed006669e8dbd48b` |

The manifest records 15 source rows and 204 external rows. The source aggregate is 476,168 bytes with SHA `c9a71afea48698b620f40bb851b4d99ef61f758a6d1d783943a4a937e5c1c60f`. The external aggregate is 41,322,619 bytes with SHA `41d3e55c523574ef54f37eb3e145cf9daa3635ddc7e9f3dcdb7f5781049e112a`.

The manifest state is `source_authored_a17_pending_root_peer_review_unbuilt_unexecuted`. It records `compiled=false`, `executed=false`, `native_child_started=false`, and `product_integration_allowed=false`. The review gate still requires the root and peer receipts before compilation.

## Independent source and closure checks

I used standalone read-only JSON parsing, regular-file reads, byte counts, SHA-256, and the documented framed aggregate encodings. I did not import or execute the A17 helper, Rust crate, compiler, control binary, producer, or native framework.

All 15 source rows exist and match their manifest byte counts and SHA-256 values. Recomputing the source aggregate with the manifest's domain and framing reproduced the declared value. All 204 external `(role, path)` rows exist and match their declared bytes and hashes. Recomputing the external aggregate reproduced the declared value. No external row was missing or changed.

The A17 recipe has 221 `source_closure` keys. The current A08 loop in `rust-producer-runner-a16-root-orchestration-preparation-a08/native_runner_fixed_compile_a16.py:489-515` checks 116 `_sha256` and `_bytes` companion fields. A standalone replay of that exact suffix and alias logic passed all 116 fields. The alias

`a11_incomplete_handoff_root_disposition_sha256 -> a11_incomplete_handoff_disposition`

also resolves to the matching proof row. The four path-only closure values without a suffixed companion remain outside that loop's contract: `a03_controls_manifest`, `runner_source_manifest`, `bootstrap_record`, and `a15_build_attempt_root`.

The three repaired A15 companion paths are present in `direct-build-recipe-a17.json:387-389` and match their manifest rows:

| Companion | Bytes | SHA-256 |
| --- | ---: | --- |
| `a15_controls_failure_log` → `rust-producer-runner-a15-build-attempt-a01/2-stderr.log` | 13,844 | `4796480e8524cbc9700996fabfd12f4bd88df9f55c387589fa17ed09f22363e9` |
| `a15_compile_measurements` → `compile-measurements-a01.json` | 716,266 | `ad691555e69d9cf2bfcd5a1d4f0c9da56cdf54ef9d04c1b9c618e50e0918ebe7` |
| `a15_compile_terminal_closure` → `compile-terminal-closure-a01.json` | 1,248 | `795946bfbae78a3500ec2a627c8dee9af0aa14321bdf9ebe2a574a7520e735cd` |

## Inherited wrapper migration note

The current A08 wrapper still performs this subject check at lines 490-495:

```python
type(closure.get('a15_external_evidence_rows')) is int and
closure['a15_external_evidence_rows'] == m['external_aggregate']['rows']
```

The A17 recipe has `a15_external_evidence_rows=159`, `a16_external_evidence_rows=198`, and `a17_external_evidence_rows=204` at lines 386 and 459-460. The A17 manifest has 204 external rows. Therefore, running the unchanged A08 wrapper against A17 would reject the recipe before the suffix checks, even though the 116 companion checks pass.

This is a P3 migration note, not an A17 Rust source defect. An A17 successor wrapper must select `a17_external_evidence_rows` and require the current external aggregate row count of 204. It must retain the exact companion and alias checks. The historical A08 wrapper remains unchanged.

## Current root readback

The root supplied a later authenticated readback without asking this review to rerun any helper. The bound file is `rust-producer-runner-a17-parent-source-readback-a01.json`, with 764,624 bytes and SHA `70d509163202c8bf01ca60deeb824f92b2fc0f3b87c800a1f0ee3734e1861e82`. It records 655 input rows, 164,928,922 bytes, 27 imports, and 23 Rust files. The authenticated helper receipt has 1,448 bytes and SHA `eaaddde7528a6ac564c9bc3761934f6f432a7be77c2842a3fe971c4081055872`.

The root reopened all 655 rows through held descriptors and matched all nine identity fields. The exact source-closure loop then passed all 116 scalar and path joins with zero missing joins. This confirms the three repaired A15 companion paths against the current 204-row closure. The root parent review is `apps/video-studio/docs/design/rust-producer-runner-parent-source-review-a17.md`, 3,446 bytes, SHA `c23c6126402965d1ef9445f1fdf43ae7b6bd0801fae09b7d00bb03f16fe91797`.

The current wrapper scalar is `a17_external_evidence_rows=204`. The inherited `a15_external_evidence_rows=159` and `a16_external_evidence_rows=198` values are unused metadata. The actual A16 predecessor count was 159. The unused A16 value is a P3 metadata correction to preserve in any successor, not a reason to change A17 Rust source.

## Source delta and build recipe

A paired comparison with A16 found the expected A17 path and label changes plus three documentation-only corrections across the 14 non-recipe files. It found no Rust logic change. `src/pure.rs` remains byte-identical. The protected 64-character SHA literal set is unchanged across corresponding files.

The recipe declares four direct `rustc` commands: production library, production CLI, controls library, and controls CLI. It declares no Cargo build. The commands retain the `aarch64-apple-darwin` target, edition 2024, `panic=abort`, thin LTO, fixed dependency archives, and fixed external crates. The environment uses `clear_environment=true` with the declared ten keys. The build and control limits remain bounded, including 1 MiB build logs, 4 MiB child logs, and an 8-second launch rendezvous timeout. These are recipe facts, not build or runtime evidence.

## Disposition and limits

The A17 package is structurally consistent after the three repaired companion paths. Its source and external rows, aggregate hashes, suffixed closure fields, alias, commands, environment, limits, protected hash literals, and current 655-row readback pass this review.

The A17 package remains unbuilt and unexecuted by this review. The supplied root readback does not establish a compiler result, process lifecycle result, native framework result, media result, product qualification, or acceptance authority. The A08 scalar must be replaced in a versioned successor wrapper before that wrapper can be used for A17.
