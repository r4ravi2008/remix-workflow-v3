# Existing-media admission next design A08: independent peer review

## Result

A08 closes both A07 ownership findings at the design level. I found no
additional P1 or P2 finding in the reviewed scope.

The A08 contract remains design-only. Plan8 is disabled until an implementation
derives concrete layouts, measures capacities, and passes the declared source,
route, lifetime, cancellation, and compatibility controls.

## Review scope and identities

I read the complete frozen A08 design. I compared its A08 amendment with the
complete A07 design and A07 independent review. I checked the request,
profile, claim, lease, publication, and prepared-plan shapes against the
fourteen current product source files named by A08.

No product source, helper, build, test, process, native media, or application
state changed. This is a same-family, nonblind design review.

| Evidence | SHA-256 |
| --- | --- |
| A08 design | `5f8f1db1610d622c255cca8505c106e6ba678111394c1a81e40d39dee69ed81d` |
| A07 design | `eb195c7672252b080f24e8a33f52a4e9d4592888c5fcab40be47309b45e4324c` |
| A07 independent review | `2f13cfea10a0a3a3491923baeae80b0146f3b2cbf8681c7bee10804ed52336e1` |

The fourteen product bindings in A08 all match the current files:

| File group | Current result |
| --- | --- |
| `model.rs`, `plan.rs`, `project.rs` | exact A08 hashes |
| `composition.rs`, `media.rs`, `layers.rs`, `movie.rs`, `pcm.rs` | exact A08 hashes |
| `exports.rs`, `lib.rs`, `publication.rs`, `identity.rs`, `native_format.rs`, `export_stage.rs` | exact A08 hashes |

## A07 request-preparation finding is closed

A07 required an explicit treatment of the request clone and request-identity
encoding. A08 provides both.

The Plan8 private preparation seam takes `&ExportRequest` and
`&ContentHash`. The two public Plan8 entry points own one request each and do
not call `request.clone()` or clone identity strings. The request hash uses a
closed streaming encoding with a 30-byte domain prefix, checked length fields,
the 64-byte revision digest, one profile tag, and two big-endian bitrate
fields only for H264. The stated maximum of 363 encoded bytes is arithmetically
consistent with the 128-byte intent and timeline limits.

The separate `M_request_hash` owner and `C_request_hash_scratch` lifetime are
explicit. The scratch drops before revision or plan body reads. The controls
cover boundaries, profile variants, byte mutations, unknown tags, legacy-hash
inequality, and forbidden serializer or formatting allocation.

## A07 lease-control finding is closed

A08 replaces the inherited unbounded lease on the Plan8 route with private
`Plan8ExportLease`, `Plan8RenewalCapture`, and `Plan8ClosedLease` shapes.
The capacity-one stop channel, one worker capture, control handles, Arc block,
join handle, and channel backing each have named ownership terms.

The running term includes the lease root, renewal capture, Arc control block,
stop-channel policy, and the caller's prejoin control handle. The quiesced
term contains one closed wrapper and one Arc block. The A08 transition requires
stop, successful join, and prejoin-handle drop before the running term is
released. Publication borrows the non-cloneable quiesced wrapper.

The execution, recovery, normal-publication, uncertain-completion, and
failure formulas use the correct running or quiesced term. The controls cover
full queues, one signal attempt, worker panic, join failure, cancellation,
fencing, normal publication, recovery, and explicit postjoin drops.

The private terms match the current source shape: `ActiveClaim` owns intent,
request hash, plan ID, epoch, and owner PID; the current lease owns one
control, one stop sender, and one optional join handle; and the renewal worker
currently owns a cloned `Project` and `ActiveClaim`. A08 changes only the
proposed Plan8 path and keeps the legacy `prepare_export`, `export`, request
hash, lease, worker, and serialized behavior outside that route.

## Source and compatibility checks

The A08 request fields match `ExportRequest`: intent, revision, timeline, and
profile. Its closed identity tags match the three current `MovieProfile`
variants. Its claim and lease formulas match the current `ActiveClaim`,
`ExportLease`, and `ExportControl` field boundaries. Its publication formulas
retain the A07 prepared plan, claims, receipt, stored artifact, verification,
picture evidence, failure body, and join ordering.

A08 preserves Snapshot schema 1, Plan2 through Plan7 serialized bodies,
legacy request hashing, legacy lease behavior, legacy error conversion, and
legacy public struct literals. The compatibility controls require byte-level
readback and route isolation. They do not claim that those controls have run.

The old-media admission contract remains closed around bounded BLOB reads,
no draft during source validation, source/draft owner transfer, retained
positive B-tree permits, finite source and plan domains, and separate measured
channel labels versus canonical audio order. A08 changes none of those rules.

## Review limit

This review establishes no implementation, `size_of` result, allocator or RSS
bound, SQLite memory bound, native-framework bound, codec support, media
output, playback, listening, GPU use, Resolve behavior, full-editor
acceptance, or creative approval. The stated A08 formulas and controls remain
unimplemented design obligations.
