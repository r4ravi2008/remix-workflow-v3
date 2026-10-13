# Rust producer runner A10 source peer review

## Disposition

**Rejected before compilation.** One P1 group and two P2 groups remain.

A10 closes most of the eight frozen A09 finding groups. The region-truncation
launch row still cannot produce its required result. Two evidence documents
also overstate or omit facts from the implemented source.

This review is source-only, same-model-family, and nonblind. Root disclosed
early feedback incorporated by the writer. I independently traced the saved
A09 findings through the frozen A10 source.

I did not import, compile, probe, test, bootstrap, authorize, stage, or execute
the package. I did not start a child, native framework, media tool, GPU, or
Resolve.

## Frozen source receipt

I read the A09 root review, peer review, and rejection disposition. I reviewed
the complete A09-to-A10 Rust changes and the changed contracts and schedules.

I rehashed every saved source row and every external `(role,path)` row. I also
independently reproduced both framed aggregates.

| Item | Bytes | SHA-256 |
| --- | ---: | --- |
| `source-manifest-a10.json` | 55,008 | `4341874179dd193ad23b5b9d0e9ea03eab37db09e533261c0d5d3d3b6dfd77ed` |
| 15 source rows | 417,283 | `8ee9a5750d0ef5c72b53df7a8668c9eadae1450989d1b7cb555e64c5757da82c` |
| 106 external `(role,path)` rows | 10,714,908 | `0a0315f760aedc4b761bf09fd00bab00d0fbd0a070f2d411b7f9222a0ff043b3` |
| `src/lib.rs` | 181,377 | `22d129ba8aa19be8e82473cbec6d9828eec424d121c5c7da06980e98a7a00a18` |
| `src/a10_launch_controls.rs` | 21,491 | `05a38fd54b5f3939fc8f442bcd4504c9c7cfa33327eb265641024c089c879b9a` |
| `src/a10_focused_controls.rs` | 67,417 | `021976611799f8eb3917af2dad5b86ae8ac2fcab1ee4f2a775dfec4c8f3d5e54` |
| `src/pure.rs` | 6,459 | `c2a6ab8948b2762034007cd50c5188c622b48a7ec9f5242e72ca13a7b06a8739` |
| `direct-build-recipe-a10.json` | 19,801 | `0c5a6709cf5f8aab1da1bdd41aca7dbfd3e5b7095b870b94a96d00ec15bed87b` |
| `pure-fixtures-a10.json` | 15,816 | `dc34010ef79ad1b5c22b6b2e243c5d2e3c4363d34aaa97d04ee5656af1263be6` |

All rows match their declared byte counts and hashes. Source paths are unique.
External `(role,path)` pairs are unique. The closure pins the rejected A09
manifest, both A09 reviews, and the A09 rejection disposition.

## P1 finding

### P1.1: The region-truncation row always returns the wrong terminal code

`region_scan_end_is_valid` rejects every call with `cap_exhausted=true`. See
`src/pure.rs:181-187`.

The injected truncation path passes `cap_exhausted=true`. It selects
`loaded_region_walk_truncated` only when the predicate returns true. Therefore,
that path always returns `loaded_region_walk_cap_exceeded`. See
`src/lib.rs:3031-3038`.

The launch schedule accepts only `loaded_region_walk_truncated` for this row.
See `src/a10_launch_controls.rs:297-310`. The fixed eleven-row launch schedule
therefore cannot pass.

The same inversion affects actual cap exhaustion. The post-loop branch again
passes `cap_exhausted=true`, then emits `loaded_region_walk_cap_exceeded` only
when the predicate returns true. It instead returns
`loaded_region_walk_failed`. See `src/lib.rs:3067-3077`.

Keep the shared predicate for normal end-of-walk admission. Classify injected
truncation and actual cap exhaustion from their distinct observed causes. Bind
each cause to its declared terminal code.

## P2 findings

### P2.1: The ESRCH rationale claims a production seam that does not exist

`source-rationale-a10.md:82-84` says `esrch_termination_facts` is called by both
production and private controls. The only call is the private fixture adapter
at `src/a10_focused_controls.rs:1112`. Production does not call this predicate.

The private fixture also supplies `term_retry_allowed=false` as authored input.
See `pure-fixtures-a10.json:262-271`. It does not prove production's captured
ESRCH and retry decision.

Production now captures signal results and errno directly. That repair is
present. Correct the rationale and bound the pure row as model-only evidence,
or route the production observation through the shared classifier.

### P2.2: The direct recipe omits eight saved process fields

`ProcessObservation` saves eight exceptional-supervision fields. The output
schema describes them. See `src/lib.rs:548-555` and
`output-schema-a10.md:45-50`.

`direct-build-recipe-a10.json:331-369` declares
`process_observation_fields`, but omits all eight fields:

- `cleanup_supervision_entered`
- `cleanup_supervision_checks`
- `cleanup_supervision_group_attempts`
- `cleanup_supervision_group_delivered`
- `cleanup_supervision_group_errno`
- `cleanup_supervision_direct_attempts`
- `cleanup_supervision_direct_delivered`
- `cleanup_supervision_direct_errno`

Add the implemented fields to the recipe. This keeps the direct-build contract
aligned with the report schema and exceptional-owner evidence.

## Eight-group accounting

1. **Stopped versus terminal status:** closed in source. A10 records
   `stopped_wait_status` separately from terminal `wait_status`. Only a terminal
   status proves reap completion.
2. **Retained unresolved ownership:** closed in production source. The
   exceptional owner retains child and descriptor ownership until terminal wait
   and owned-group absence. It does not signal a consumed direct PID. P2.2 is a
   documentation omission for the resulting saved facts.
3. **Authority joins before `SIGCONT`:** closed in source. After the review
   rendezvous, A10 rereads the sidecar and both reviews. It then revalidates
   qualification, typed authorization, and path anchors before resume.
4. **Per-launch codes and process shapes:** the executable and cwd rows now use
   their reachable boundaries. P1.1 leaves the region-truncation row
   impossible.
5. **KILL, errno, and ESRCH facts:** production captures each signal result and
   errno immediately. Retry is suppressed after direct ESRCH or terminal wait.
   P2.1 limits the claimed private evidence.
6. **Region predicates and errno:** errno capture is immediate, and normal
   clean-end admission uses the shared bounded predicate. P1.1 leaves
   truncation and cap classification inverted.
7. **Typed changed paths:** closed in source. Each mutation binds exact expected
   paths, actual changed paths, and the expected rejection cause.
8. **Five review variants:** closed in source and documents. The fixture,
   recipe, schema, rationale, and control result use the five exact variants.

## Scope limits

A10 remains uncompiled and unexecuted. Static source agreement does not prove
Rust compilation, control completion, child lifecycle, bootstrap acceptance,
producer output, native behavior, media output, playback, hearing, or creative
approval.

The review does not provide independent-source-origin evidence. It evaluates
the frozen source and its declared external closure only.
