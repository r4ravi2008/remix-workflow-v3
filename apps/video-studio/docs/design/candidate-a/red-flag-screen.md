# Design red-flag screen

This screen applies the architect skill's required red flags to Candidate A.

## Shallow module

### Screen

The public Rust surface has two handles and whole operations:

- `Studio::open`, `capabilities`, `create_project`, and `project`.
- `Project::head`, `inspect`, `commit`, `export`, `verify_artifact`, `record_review`, and `evaluate_policy`.

`commit` hides import staging, hashing, probing, alias resolution, lineage validation, timeline validation, revision identity, conflicts, and recovery.

`export` hides capability checks, source decode, timestamp mapping, composition, text shaping, audio mix, encode, mux, job recovery, output measurement, and promotion.

### Result

Pass with one watch item.

`ChangeSet` is necessarily rich because the editor is general.
Convenience builders must not become another public service hierarchy.
They should only construct the same typed value.

## Information leakage

### Screen

AVFoundation, Core Media, Core Video, Core Image, Core Text, and Metal types remain inside `video-studio-macos`.

SQLite rows, aggregate paths, leases, and staging files remain private.

CLI DTOs convert into domain values.
The core does not re-export wire envelopes.

Effect adapters consume versioned CLI schemas.
They do not update native storage or implement a timeline reducer.

File paths are import locators only.
Content hashes and measured descriptors become stored identity.

### Result

Pass.

The largest leakage risk is duplicating capability names in the CLI and Effect adapter.
The CLI schema and adapter bindings must be generated from the native registry.

## Temporal decomposition

### Screen

The crate map follows knowledge ownership:

- `video-studio-core` owns project and editing semantics.
- `video-studio-macos` owns Apple framework adaptation.
- `video-studio-cli` owns transport and process lifetime.
- `video-studio-acceptance` owns independent observations.

Probe, decode, composite, mix, encode, and verify are internal operations.
They are not public service modules that pass a shared request in sequence.

Internal files such as `asset.rs` and `timeline.rs` group invariants that act at different times.

### Result

Pass.

The macOS adapter has files named for framework tasks.
They remain private implementation units behind one `MacOsMediaPlatform`.

## Pass-through method

### Screen

The CLI adds schema checks, size limits, cancellation, deadlines, output framing, and exit-code policy.
It is not a same-shape forwarder.

The Effect adapter adds authentication, tenant mapping, budget control, GPU recovery, worker supervision, and receipt verification.
It is not a native editor wrapper with no policy.

`Project` delegates to the aggregate internally.
The handle exists to bind project identity and storage ownership.

### Result

Pass.

Do not add public `Renderer`, `Decoder`, `Encoder`, or `ProjectRepository` facades that forward the same arguments.

## Interface depth

The caller provides only irreducible decisions:

- Project, base revision, branch, and stable intent.
- Exact assets, expected hashes, and origins.
- Timeline semantics and output profile.
- Actual review observations and actors.

The implementation owns the procedural complexity.
One export call covers a complete durable movie operation.

The interface is deeper than a stage-oriented media pipeline.

## Shared-state check

Project edits compare one branch head inside a short transaction.
Conflicting writers produce one winner and one explicit conflict.

Long exports do not share an unfenced mutable output.
Each job owns staging state and a fencing epoch.

GPU workers do not write native project state.
The Effect adapter merges a verified completed original through a normal project commit.

### Result

Pass.

## Source-of-truth check

Each invariant has one authority:

| Invariant | Authority |
| --- | --- |
| Edit state | Immutable `ProjectSnapshot` |
| Current line of work | Branch head |
| Imported bytes | Content-addressed blob and measured hash |
| Exact source timing | Immutable presentation-sample index |
| Source substitution | Explicit `SourceBinding` and mapping receipt |
| Derived ancestry | Lineage graph |
| Export completion | Source-bound artifact receipt plus fresh measurement |
| Review state | Derived policy evaluation over matching records |
| GPU attempt state | Separate Effect/Herdr job store |

### Result

Pass.

## Remaining rejection triggers

Reject or redesign Candidate A if implementation produces any repeated pattern below:

- Callers must invoke probe, index, decode, render, encode, or promote in order.
- CLI and library use different edit semantics.
- The Effect adapter reconstructs revisions or source lineage.
- A file extension or nominal frame rate decides codec or timing behavior.
- Asset paths appear in stored timeline identity.
- A review row has a mutable trusted `accepted` flag.
- Export recovery needs a database write lock for the whole movie.
- Framework objects cross into the project snapshot.
- More than one module can promote an artifact.
- Missing native codec support starts a fallback process.

