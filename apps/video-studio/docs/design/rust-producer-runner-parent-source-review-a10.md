# Rust producer runner A10 parent source review

ROOT rejects A10 before compilation. Preserve its source package, manifest, and source measurement unchanged. Prepare the narrow successor separately. ROOT found three P1 groups and two P2 groups.

## Measured closure

Manifest: 55,008 bytes, SHA-256 `4341874179dd193ad23b5b9d0e9ea03eab37db09e533261c0d5d3d3b6dfd77ed`.

The fifteen source files contain 417,283 bytes. Their framed aggregate is `8ee9a5750d0ef5c72b53df7a8668c9eadae1450989d1b7cb555e64c5757da82c`. The 106 external rows contain 10,714,908 bytes. Their framed aggregate is `0a0315f760aedc4b761bf09fd00bab00d0fbd0a070f2d411b7f9222a0ff043b3`.

ROOT executed only the read-only source helper A01. ROOT authenticated its exact held source bytes before execution under isolated, nonoptimized Python with bytecode writes disabled. It imported no project or process utility. The external launch receipt is 1,190 bytes, SHA-256 `225e8eb96605aab9416823b85f3ab418b720d737fed4e90ae240f274e23c8a57`.

The saved source proof contains 484 files and 131,563,623 bytes. Its 570,326 bytes hash to `bd0e3d475af75c5c6e8213fbd1ce4232fd8ef8cc1815656b99b57a009fd406e8`. All nine identity fields match before and after. ROOT independently reopened the complete current closure after source review. The helper checked 27 literal import edges across 23 Rust source files.

ROOT read the complete A09-to-A10 library delta and all remaining source, recipe, fixture, contract, schema, rationale, and entry-point deltas. `pure.rs` remains byte-identical to A09. These observations are source evidence only.

## P1: resumed terminal status is not retained before later cleanup

In `src/lib.rs`, successful resumed waits update local `status` around lines 3680 and 3736. They do not immediately update `child.initial_status` or `child.initial_reaped`.

The `pipe_drain_timeout` path around lines 3758–3772 then calls `darwin_cleanup_child`. That helper unconditionally calls `darwin_kill_and_reap_observed`, which signals the direct PID before waiting. The direct terminal status was already consumed. This path can signal a reused PID, lose the consumed status, and supervise an `ECHILD` result indefinitely.

Other pipe, poll, and log errors after a successful wait share the problem. A final loop exit with unresolved cleanup can also form `ChildOutcome` before Drop completes exceptional supervision. The early-terminal branch records direct status correctly, but leaves remaining group supervision and its signal facts to Drop after constructing the outcome.

Immediately retain every consumed terminal status on the process owner. Make cleanup of an already reaped direct child group-only. Complete and record exceptional closure before constructing an outcome. Keep descriptors held until closure. Drop remains a final ownership guard, not the source of missing report facts.

## P1: group absence is not latched

`darwin_supervise_exceptional_owner` recomputes group absence on each iteration. If an owned group disappears before the direct terminal status is consumed, a later iteration can signal a new group with the same numeric PGID.

Latch the first observed owned-group absence. After that observation, never signal that numeric group again. Direct-child ownership and terminal consumption remain separate facts.

## P1: region truncation has a deterministic control-code mismatch

`region_scan_end_is_valid` returns false whenever `cap_exhausted=true`. The injected truncation branch therefore emits `loaded_region_walk_cap_exceeded`, while `a08_allowed_code` requires `loaded_region_walk_truncated`. The real cap branch emits `loaded_region_walk_failed` rather than the cap cause.

Keep rejection derived from the shared predicate. Bind the emitted error to the actual cause and preserve the fixed eleven-variant schedule. Correct the corresponding source expectations coherently.

## P2: cleanup can replace the initiating failure

The resumed loop overwrites `killed_reason` with `ReapFailure` after a reap deadline and again on pipe-drain failure. That loses the initiating cancellation, timeout, or log-overflow cause before terminal publication.

Retain the initiating cause and record cleanup failure separately. Eventual terminal and group closure must still be required before return. Do not turn a closed failed attempt into successful pending completion.

## P2: descriptive metadata does not match saved behavior

`output-schema-a10.md` describes an A10 authorization operation and implementation. The actual authorization intentionally remains `native_text_rust_a05_attempt` and `rust_a05`.

`source-rationale-a10.md` says production calls `esrch_termination_facts`; no such production call remains. The direct-build recipe's process-field list omits eight saved `cleanup_supervision_*` fields. The renamed focused source also describes an historical A05 leaf name.

Correct these descriptions and the process-field schedule against the final implementation. Do not fabricate a production predicate call merely to match the prose.

## Boundary

No A10 Rust compilation, private control, bootstrap, authorization stage, native producer, media, GPU, or Resolve operation occurred. Source measurement establishes no native output correctness, product integration, WATCHED, HEARD, or creative acceptance. The prior A09 package remains unchanged.
