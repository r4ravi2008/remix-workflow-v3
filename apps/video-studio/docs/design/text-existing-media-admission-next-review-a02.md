# Existing-media admission next design A02: independent review

## Scope and evidence

This is a read-only design review. It used file reads and source-digest checks only. It did not run tests, build code, invoke helpers, read native media, change state, or touch fixtures, GPU resources, or Resolve.

Primary design:

| File | SHA-256 |
| --- | --- |
| `text-existing-media-admission-next-design-a02.md` | `d95582f634c4f22e374cd02c029e823295a8a0d36ba2e36c0edac9094648d9a4` |
| A01 design | `d128ec8cb5114d98ef9a68fb1f5a27d174ff653445cd7819e690697234518a3e` |
| A01 independent review | `92ee1eea467968115b1997baadd9e31881cc6d7e7a4f7ecd5d7eee813f4b00f1` |
| Payload A03 root readback | `c7b2c6be9538d703f62ecc0f1cdb29290013906a546050b838c263683e73a2fc` |
| Payload A03 measurement | `124102dcb3f4c76d97d3f4faa30678c8788df118a8210f64a562f5b63952e3ca` |
| Text admission contract A03 | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |

The current source files named by A02 match their bound digests for `model.rs`, `plan.rs`, `project.rs`, `composition.rs`, `media.rs`, `layers.rs`, `movie.rs`, `pcm.rs`, and `exports.rs`.

## Review result

A02 addresses the A01 P1 gaps in bounded input admission, aggregate old-media domains, plan ownership, worker cloning, route-first persistence, and legacy compatibility. No new P1 finding remains in the design shape.

Plan8 must remain disabled until the following P2 issues and route/read-boundary decisions are repaired and tested.

## P2 findings

### P2-1: zero-entry tree policy does not model retained root storage

Lines 478–506 define `map_policy(0) = 0` and `set_policy(0) = 0`, then require a policy comparison after every removal. The pinned Rust 1.94 observation retains a B-tree root leaf after the final entry is removed. The actual zero-entry request therefore exceeds the declared zero policy.

This applies to both maps and sets. The control cannot be green while its empty-prefix assertion contradicts the retained root allocation. Define an explicit baseline for an empty container, or define the policy over retained root state rather than logical entry count. Test empty construction, final removal, `clear`, and drop separately. Keep nested key and value charges outside the node baseline.

### P2-2: selected normalized results have an incomplete preparation lifetime

Lines 323–330 move selected normalized results into `M_draft` and `T_draft` during source validation. The `source_peak` at lines 350–353 includes `J_revision`, `W_parse`, `M_source`, `T_source`, and `C_validate`, but omits the draft owners. The `shape_peak` at lines 355–356 includes the draft owners but omits `J_revision` and `W_parse`. Lines 374–375 keep the input and parser owners alive until after typed source validation.

The design must choose and record one exact schedule. It can release the raw body and parser facts before creating the draft, or it can include both input owners in the peak that contains the draft. The permit must be acquired before the first normalized result moves into the draft.

The owner list also puts selected-timeline ownership under `C_compile` at lines 399–409 while `M_draft` and `T_draft` already describe private plan construction ownership. Assign the selected timeline and each nested moved or cloned value to one owner for each phase. The final ledger must neither double count nor omit that overlap.

### P2-3: text-bearing legacy route behavior has no available discriminator

The selected API keeps the four-field `ExportRequest` unchanged and selects Plan8 only through additive methods. The same document then promises that a text-bearing call through the legacy method returns `plan8_route_required` and proves all four text-presence/method combinations.

The legacy method has no request-side route marker, and the design forbids inferring a route from Snapshot fields, plan schema, or body bytes. A revision containing text therefore supplies no fact that can produce the promised route-specific error before the legacy body path is chosen.

Choose one precise contract before implementation: make route selection the only authority and remove the error-specific promise for a caller that explicitly chose the legacy method, or persist a bounded text/route marker that the legacy method can check before typed parsing. Do not add an unbounded body sniff or silently send a text-bearing revision through the legacy parser.

### P2-4: SQLite chunk SQL must bind byte semantics and legacy precheck scope

The design measures `length(CAST(body AS BLOB))` at lines 246–249, then permits either a blob read or a generic `substr` result at lines 260–261. Revisions are currently stored as `TEXT`, while the proposed Plan8 body is `BLOB`. A `substr(body, ...)` implementation can use SQLite text character offsets while the admission length and identity use UTF-8 byte offsets.

Specify the exact byte query for each body type. For a revision, the bounded path should read `CAST(body AS BLOB)` with explicit one-based chunk offsets, exact chunk byte lengths, and a final byte-count check. For a Plan8 BLOB, use the equivalent BLOB path. Bind the query text and the type check in the implementation proof.

The persistent-routing section also says that preparation checks both plan tables in one transaction while legacy queries remain unchanged. State that the new cross-table intent precheck is an additive route guard, then preserve the existing legacy body query and serializer after the guard. Otherwise a future implementation could change historical query or type behavior while claiming legacy byte compatibility.

## A01 obligations confirmed closed in shape

The A02 design provides an explicit Plan8 caller route before revision or plan-body reads. It keeps the historical `ExportRequest` shape and Plan2–7 serializers unchanged. It separates Plan8 bodies from the legacy `plans` table and requires route-first verification, recovery, reconciliation, and publication lookup.

The bounded SQLite sequence checks body type and byte length before fetching chunks. It hashes the exact raw bytes before token admission and typed construction. The token gate rejects unknown and duplicate fields, invalid enums, excessive strings, excessive sequences, and excessive nesting without a `serde_json::Value` tree.

The count domain now includes all snapshot timelines, track and clip IDs, lineage edges, persisted movie samples, warnings, channel labels, selected ordinals, source closure, evidence, and combined keys. It includes the 400,006 selected ID limit and 400,000 lineage-edge limit required by the A01 review. It also gives selected audio a pre-construction one-track/one-clip gate.

The ownership model accounts for source, draft, finalized plan, canonical JSON, validation scratch, compile scratch, shared worker ownership, cancellation, callback teardown, response payloads, and writer lifetime. The Plan8 worker design replaces deep plan clones with one `Arc` owner and keeps its permit until workers, callbacks, responses, and the writer finish.

The one-buffer Plan8 serialization rule binds one canonical byte slice to both hash and BLOB storage. Plan2–7 retain their existing identity and storage bytes. The tree controls cover the four current media map/set shapes, sorted/reverse/shuffled insertion, growing prefixes, and shrinking prefixes. The empty-prefix repair above remains necessary.

## Remaining qualification limits

The A03 payload measurement remains an observation package. It does not establish physical memory, allocator behavior, native framework memory, process RSS, native execution, media output, or audiovisual acceptance.

The A02 design also needs a future implementation control for any new font map shape introduced by the selected Plan8 text contract. The current listed tree controls cover the current media maps and sets. A font map must either use a separately bound text-control policy or appear in the same full-domain tree evidence.

No Plan8 runtime integration is approved by this review. The four P2 repairs above require an updated design or explicit implementation contract before code review can claim complete admission coverage.
