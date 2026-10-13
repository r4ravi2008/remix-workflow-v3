# Existing-media admission next design A03: independent review

## Scope and evidence

This is a read-only design review. I read the frozen A03 design, the A03 text admission
contract, the four A02 findings, the pinned editor sources, and the A03 allocation evidence.
I did not build, test, execute a helper, invoke native media, change state, or edit product code.

| Item | SHA-256 |
| --- | --- |
| `text-existing-media-admission-next-design-a03.md` | `ff76cab393b1c92468243622e817523b9c4d7f3fd47eef373e6708892b67509b` |
| A02 independent review | `c2ca5ef489c6f3178b2942e73a2691f1ac59537a3042b79d72b680749d212d07` |
| `text-admission-contract-a03.md` | `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f` |
| `allocation-ledger-a03.md` | `df53988319155d71a88c6b3cb29c14340bbf9a2e77966f8adb269624cdc9133f` |
| Payload A03 parent readback | `c7b2c6be9538d703f62ecc0f1cdb29290013906a546050b838c263683e73a2fc` |
| Payload A03 measurement wrapper | `c02245a4df8a440094bc8a5c05bcc473586ffea4ac5d555f11f14d45e6080aa6` |
| Payload A03 runner report | `83f6196e6e69194d6c69c4509ba50e157226f707ffbd4f00797a5c9ee08f89bf` |

The current source files named by A03 still match its bound hashes:

```text
model.rs       eaad52b1b1c8624654b1308c6b582a9a74cb6ae4870f461eaad2c2f057dcc9b1
plan.rs        17973f3039bf635a02302ebcf0aab8c57d9abd99a00afbe8372ae47d14636ae1
project.rs     a53132da6ff9ccdc6e21a32a7b73d0c833ffb7a35ff177815d6707129480698c
composition.rs 88be6c764fbba6172e519a749abb3bc2651d846016b66c71313618d0461c87b5
media.rs       490fe7871d4521fbd586810bd0ae13d84ca4288bb8c610035b9cb4ea72c91b4d
layers.rs      3b698ffd94edb71e59dcc422fed1a353890c9fbee00dd1ae2d2e6df045660655
movie.rs       5f2a4b45bb90c55ede5708198d09bd8517d6507de2129bb3c09227b1e79c52e3
pcm.rs         7ff87caa9a49b3b5b78a6aacfa10e798069ccf9e7f4216a60464c2c7b20dc76a
exports.rs     13994abea3ae1d42fe4bb7517102cff8a97dcb0b79cb4e2af4c09bec0df6c3fc
```

## Result

A03 closes all four A02 design findings in its stated shape. No P1 finding remains.

Plan8 remains disabled until the implementation supplies the missing old-media ownership
charge and passes the full-domain controls. The A03 payload evidence does not establish
product integration, physical memory, native execution, or audiovisual acceptance.

## A02 finding status

### B-tree high-water lifetime: closed in design

A03 separates logical length from retained node storage. A positive map or set permit is
acquired before insertion, remains held through moves, `clear`, and final logical length zero,
and releases only after container drop and observed zero outstanding node requests.

The explicit retained-empty-root observation matches the inspected Rust 1.94 removal path.
The zero-high-water case is restricted to a never-populated container. Nested keys and values
remain separate charges. The required controls include both new font maps, with domains 256
and 64, so the A02 future-font-map gap is closed in the design.

The A03 control is still a requested-layout observation. It does not prove allocator metadata,
physical pages, RSS, SQLite page-cache memory, or native framework allocation.

### Source and draft overlap: closed in design

A03 validates the source while retaining no selected normalized result or draft. It drops
`J_revision`, `W_parse`, and `C_validate` before it acquires draft permits or moves the selected
timeline into `M_draft` and `T_draft`. The later shape peak includes source, draft, compile,
and gate owners. Finalization drops draft-only and compile owners before plan validation.

The selected timeline has one owner in each phase. A03 also requires any representation that
cannot move a field to charge source and destination copies concurrently. This resolves the
A02 schedule ambiguity.

### Explicit route and legacy errors: closed in design

The additive `prepare_plan8_export` and `export_plan8` methods select `Route::Plan8TextV1`
before either plan table or revision body is read. The unchanged legacy methods select
`Route::Legacy`. A03 removes the impossible promise of a pre-body `plan8_route_required`
error from a legacy call. A text-bearing legacy request therefore follows the existing parser
and rejection behavior, as the available API permits.

The route-first transaction, private Plan8 table, nullable export route marker, and
fail-closed verification, recovery, reconciliation, and publication lookups are coherent.
The implementation must preserve the old body query and serializer after the common route
precheck. That is a proof obligation, not a remaining design defect.

### SQLite byte chunks and legacy boundary: closed in design

A03 fixes the revision query to `CAST(body AS BLOB)` and the Plan8 query to a BLOB `substr`.
It binds one-based byte offsets, exact chunk lengths, BLOB result type, row identity, final
byte count, and raw-byte hashing before parsing. The Plan8 path does not call the legacy
inspect, replay, or document-hash path. The common route precheck is additive, while legacy
queries and serializers remain unchanged after it.

The required multibyte, short-chunk, wrong-type, changed-row, offset-overflow, and final-count
controls are concrete and sufficient for this boundary.

## P2 finding: old-media charge is still under-specified

A03 names `M_source`, `T_source`, and `C_validate`, and it adds count, string, and vector
policies. Its preparation equations still omit the explicit old-media validation and owner
terms required by the A03 text admission contract:

```text
shape_peak = M_source + T_source + M_draft + T_draft + C_compile + G
execute_peak = M_plan + T_plan + R_active + G + P_media + O_execute + J_live
```

The contract requires `C_old_prepare` and `O_prepare` in the preparation peaks. The current
model has old-media owners that need an explicit finite charge, including movie `samples`,
descriptor warnings, image warnings, decode errors, audio labels, timeline and track vectors,
clip vectors, lineage inputs, and `AudioBinding.channel_order`. The current model also stores
`MediaDescriptor::Audio.channels` as an unbounded scalar relative to the new Plan8 policy.

A03 bounds several related quantities, but it does not state which concrete owner charges cover
all old-media struct headers, capacities, nested strings, `channel_order` labels, and validation
overhead. `M_source` cannot be a name for an unmeasured remainder when the 512-MiB decision is
the admission authority. The contract explicitly requires an old-media charge or fail-closed
admission.

The independent Payload A03 readback records this unresolved fact: current timeline, track,
audio counts, descriptor sample counts, and existing strings still need explicit admission caps
or actual-length charges. Its measured maximums are useful observations, but they do not close
this product boundary.

Repair before implementation approval:

1. Define `C_old_prepare` and `O_prepare`, or explicitly expand the existing symbols with a
   field-by-field owner table and checked `size_of`/capacity rules.
2. Bound and charge `AudioBinding.channel_order` separately, or state that it is the measured
   channel-label domain and prove the identity.
3. Bound every old-media vector and string before its pipeline-owned copy, including unselected
   assets and timelines.
4. Include those terms in every preparation, replay, and execution peak, or reject Plan8 until
   the charge exists.

This is a P2 implementation-readiness finding. It does not reopen the four A02 repairs.

## Verification limits and required next gate

The A03 ledger reports 2,378 capacity rows, 28 B-tree rows, seven precreation rows, a maximum
logical precreation charge of 132,369,399 bytes, and a maximum B-tree request of 7,548,968
bytes. Those observations are bounded and internally useful. They cover only the measured
payload fixtures and requested Rust layouts.

The evidence explicitly says that product integration is false, native execution is false,
and physical-memory admission is false. It also does not run the declared 256/64 font-map
domains or the 400,006 identifier domain. Those remain required implementation controls.

No Plan8 runtime, legacy compatibility, or media-output acceptance claim follows from this
review. The old Plan2–7 byte and behavior promise remains a design requirement for the later
implementation proof.
