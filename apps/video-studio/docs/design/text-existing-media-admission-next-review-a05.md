# Existing-media admission next design A05: independent peer review

## Scope and evidence

This is a source and design review of the frozen A05 successor. I read A05, the
preserved A04 design and review, and the current admission, publication, error,
receipt, and export seams. I did not edit product source, build, test, execute a
helper, invoke native media, or change application state.

| Item | SHA-256 |
| --- | --- |
| A05 design | `2a444f8dc5c92afa7d0524a42aa83b821e13ef0281fdbf5acfc34d4c52862f57` |
| A04 design | `accdf7c3f326791c33de5a72a1d34d241eca19867de79acd95f38f87762fb64f` |
| A04 independent review | `8465b04bdfaa6dc78f06387e3bbb303f946dd38b4ce1b52b7a841dbc7b3548eb` |
| A03 design | `ff76cab393b1c92468243622e817523b9c4d7f3fd47eef373e6708892b67509b` |
| A03 independent review | `4cd1333ee1ddea5ad8190187ace626f09cb79dd32cf429c3ca7d659041cafbd5` |

The nine A04-bound product sources still match. A05 also binds the two newly
inspected seams:

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
| `lib.rs` | `499156ec54f3046ce2901bb01ec5361ed755739911624166c971cd42e4bc04f9` |
| `publication.rs` | `4c04efc42972b9fad8f48f4be4e025fdecc6be89876109e6cbbc049bdd15f06a` |

## Result

A05 correctly repairs the two A04 findings at the contract level. The Plan8
error sequence checks a borrowed code's ASCII grammar and byte length, formats
into a fixed 4,097-byte probe, reserves the accepted ledger charge, and only
then allocates the two `StudioError` strings. The fixed overflow record retains
bounded tags and lengths, without the oversized source text.

The conversion matrix names direct errors, `io`, `rusqlite`, JSON, database
`job.error`, cancellation, disconnect, callbacks, worker joins, panic
classification, fencing, publication, uncertain commit, and unknown adapters.
The explicit Plan8 discriminator preserves the existing Plan2 through Plan7
parser, conversions, fixtures, and error behavior.

The `PreparedExport` correction is also sound. `M_prepared_plan` removes the
bare `ExportPlan` root, adds the wrapper and its 64-byte `plan_id`, and retains
the plan body once. A05 separately charges the `ActiveClaim.plan_id` clone and
the `ArtifactReceipt.plan_id` clone. It does not falsely call the current
borrowed publication seam a move.

Plan8 remains blocked at the design gate. Three bounded-accounting issues remain.

## P2: publication wrappers and serialized database bodies are not in the peak

A05 defines `S_stored_header` and `S_receipt_bytes`, but the current publication
call path retains more owners at the same time. `store_artifact` returns a
`StoredArtifact` and an `AvailableReceipt`; `PublicationGuard::complete` then
receives both while the borrowed `PreparedExport` and `AvailableArtifact` remain
live. The current types are visible at `publication.rs:173-187` and
`publication.rs:236-287`.

`AvailableArtifact` owns a file handle, path buffer, observation, and hash.
`AvailableReceipt` owns a file handle, path buffer, observation, and receipt
bytes. Each receipt check also creates a second `vec![0; self.bytes.len()]` for
descriptor readback. A05's `S_stored_header` only names `StoredArtifact` and
`M_receipt_nested`; it does not name these wrapper headers, path capacities,
handle records, or the readback buffer multiplicity.

The database handoff has another live allocation. `complete` calls
`serde_json::to_string(&stored)` at `publication.rs:551-567` while all receipt
owners remain live. The uncertain-commit readback repeats that serialization at
`publication.rs:631-694`. This is a `StoredArtifact` body, not the
`ArtifactReceipt` body represented by `S_receipt_bytes`. It has no bounded body
term or phase multiplicity in A05.

The verification return path is also still open. `store_verification` creates an
unbounded JSON byte vector at `exports.rs:1008-1047`; `save_verification` then
returns `StoredArtifact`, `ArtifactVerification`, and `ExportResult` together at
`exports.rs:1116-1141`. A05 says this requires a separate inventory, but does not
provide that inventory or its finite wrapper multiplicities.

Add explicit terms before Plan8 implementation approval. The terms must cover
`AvailableArtifact`, `AvailableReceipt`, the bounded receipt readback vector, a
bounded `StoredArtifact` database body, and the verification file/body and return
wrappers. State the maximum simultaneous count for normal completion and
uncertain-commit recovery. Reuse a canonical serialized body only when the exact
drop boundary is recorded. Otherwise, charge each live serialization separately.

## P2: receipt and claim nested ownership is named but not yet finite

`M_receipt_nested` is still a placeholder. A05 lists the reachable fields, but
lines 895-907 defer every nested cap to implementation. The current
`ArtifactReceipt` includes a `PathBuf`, one `BuildIdentity` graph with two
content hashes, three direct `ContentHash` fields, and `NativeMeasurements`.
The latter contains two track records with codec strings, optional PCM records,
optional streaming evidence,
optional format evidence with a variable `compatible_brands` vector, optional
24-bit comparison, and optional video-color tuples with three strings each.
Those fields require numeric byte and multiplicity bounds before
`S_stored_header` can be evaluated.

The claim count is also incomplete. `exports.rs:1216-1223` creates one
`ActiveClaim` and passes `claim.clone()` into the renewal worker. Both claims
coexist during execution. `H<ActiveClaim> + string_policy(64)` accounts for one
header and the `plan_id` clone, but the design does not state the two-claim
multiplicity or the corresponding `intent` and `request_hash` clone charges.
The phrase “existing bounded identity terms” does not fix that phase count.

The verification path similarly clones `stored.receipt_id` and
`receipt.output_sha256` while retaining the `StoredArtifact`, and then returns
both the stored artifact and verification in `ExportResult`. Give
`ArtifactReceipt`, `ArtifactVerification`, `ActiveClaim`, and `ExportResult` a
field-by-field table with exact optional and repeated counts. Include the
receipt technical graph, path limits, and every clone at the phase where it is
live. A source-change inventory gate must reject a new receipt or evidence field
until its row and bound are added.

## P2: the bounded error probe does not prove a nonallocating source formatter

A05 correctly forbids `format!`, `.to_string()`, and `Into<String>` before the
probe limit. It then permits a bounded `Display` probe for `io`, `rusqlite`, and
JSON errors. A bounded destination does not prevent a `Display::fmt`
implementation from allocating internally. In particular, a rusqlite error can
carry a boxed source error, and callback or panic adapters can receive custom
error values. The `Plan8ErrorProbe` term only charges the destination buffer.

Require source-specific, nonallocating adapters for known errors, or classify
opaque/custom errors with a fixed tag and overflow record. If a Display path is
retained, prove that formatter's allocation behavior and charge any source-owned
temporary. The control must instrument the source boundary, not only inspect the
final probe capacity.

The same issue appears in failure persistence. `close_failed_claim` calls
`error.to_string()` twice at `exports.rs:1388-1433` before writing the database
error column. Even a bounded `StudioError` can produce a new combined string of
up to `64 + 2 + 4,096` bytes. A05 names close-failed-claim in the conversion
matrix but adds no persistence-copy term or bounded database writer. Add one
bounded persistence representation and its phase charge, or record code/detail
columns without constructing that combined string.

## Closed checks

The 64-byte code and 4,096-byte detail limits are byte limits. The 65-byte code,
4,097-byte detail, multibyte UTF-8, invalid-code, overflow-retention, and
capacity controls are correctly required before Plan8 allocation.

The wrapper correction avoids double-counting `ExportPlan`, keeps the
`PreparedExport` wrapper live across preparation and execution, and charges the
receipt's cloned `plan_id`. The compatibility boundary selects Plan8 before
deserializing its body and leaves legacy schemas and bytes untouched.

## Verification limits

This is a same-family source and design review. No Plan8 runtime exists at these
hashes. I did not validate `size_of`, allocator capacities, serializer behavior,
channel storage, publication recovery, or any native or media result. The
separately run Runner A03 controls do not establish those claims.

