# Native text preparation next design review A05

## Disposition

I found no P1 because A05 creates no executable authority.

Three P2 findings block implementation of the qualification loaders or observer runner:

1. heterogeneous saved observations are counted as regular files;
2. the acceptance record has no external trust anchor;
3. the exact observer command and output ownership do not match the current A06 observer.

The first finding independently confirms the parent review.
The second and third findings come from this peer review.

The reviewed artifacts are:

| Artifact | SHA-256 |
| --- | --- |
| `native-preparation-next-design-a05.md` | `336e19dd491ac04843e31cb4b93b189e5cfb982c0312e55cf123fc182a0ad1d0` |
| `native-preparation-parent-review-a05.md` | `7aa0fc0a50059b74063486497c95dc07459a2023b68543987e9fc8709061f564` |
| `swift-build-attempt-a02/report.json` | `214864e3d4bc7af8e7698dc3c6ad78f409147a5fffaeabfc8c9898c356fcc3ea` |
| `swift-build-parent-readback-a02.json` | `cfc3aa29d7825a1d4d843a297df55e95651dcc0eef76cbbf94f0528f62a2f63a` |
| `swift-pure-controls-attempt-a03/report.json` | `43a58d030bc7d4f2d6ddb799871472517e68bece09f70b675bd8e1f0f07c6632` |
| `swift-pure-controls-parent-readback-a03.json` | `7f7312a84190033b7e76743b28dee9c550b04bff9b1f20622613d23ff568a10d` |
| `toolchain-observation-a01/report.json` | `c22b5cb70e490131c14456f021cfb11a843a67140d26ec93d759fb5ac29c87c8` |

No helper, gate, control, compiler, producer, observer, comparator, GPU process, or Resolve process ran during this review.

## P2: the universal artifact model cannot encode the saved authorities

`MeasuredArtifact` represents one regular file.
Its wire row represents file bytes, file identity, and optional Mach-O identity.

The Swift role table instead copies two top-level dictionary cardinalities:

- `swift.build.input:NN` has cardinality thirteen;
- `swift.pure.input:NN` has cardinality thirteen.

Those dictionary keys are not thirteen regular files.

The build report's `closureBefore` contains:

- five direct regular-file observations;
- three invocation-symlink observations;
- two directory observations;
- two scalar path relations;
- one `sourceRows` array containing twenty-one regular-file observations.

That closure expands to twenty-six regular files plus seven non-file facts.
Its `closureAfter` and parent readback retain the same typed structure.

The pure-control report's `inputsBefore` contains:

- six binary observations;
- seven retained file observations;
- seven log observations;
- four held-binary descriptor and pathname aliases;
- three directory authorities;
- the complete heterogeneous build closure;
- five scalar join results.

Its `inputsAfter` and parent readback retain those distinctions.
Flattening the thirteen keys into thirteen file rows drops evidence and breaks alias meaning.

The Rust toolchain roles have the same issue.
Launcher paths, SDK paths, framework directories, scalar versions, and regular files require distinct forms.

Define a closed observation sum type before implementing either qualification loader.
At minimum, it needs these variants:

- bounded regular file;
- invocation symlink with exact link bytes and resolved target relation;
- directory authority with endpoint identity;
- bounded scalar or path relation;
- retained descriptor and pathname alias;
- typed boolean join derived from measured inputs.

Each report adapter must define the exact field expansion, role order, and cardinality.
Nested arrays must expand into their actual rows.
Aliases must reference existing rows without silently creating different evidence.

The regular-file adapter must also require `bytes == identity.size`.
The current role-index encoding includes one file byte count but omits the separate `StableIdentity.size` field.

Add controls for these mutations:

1. Retarget an invocation symlink without changing the resolved executable bytes.
2. Replace a directory endpoint while preserving descendant path text.
3. Mutate one nested source row.
4. Swap one held-binary pathname while retaining its descriptor.
5. Change one derived boolean without changing its measured inputs.

Each mutation must fail the relevant qualification before process launch.

## P2: the acceptance record is caller-selected but has no trust anchor

A05 correctly removes the public `Accepted<T>` constructor.
That private type does not authenticate the disposition source.

The caller supplies an arbitrary acceptance-record path.
The record itself supplies `accepted_no_p1_or_p2` and the two review references.
The loader measures those three files and checks their internal references.

No rule pins the acceptance-record bytes to an independently accepted authority.
No rule proves that a root-owned writer created the record.
The loader intentionally does not parse either Markdown review's disposition.

A caller can therefore create a structurally valid record that asserts acceptance.
The caller can point it at measured review files that do not contain an accepted disposition.
The private constructor then converts that self-assertion into `Accepted<T>`.

Add one external trust anchor for every acceptance record.
A bounded solution can use a separately reviewed root-acceptance manifest.
That manifest must close the exact record hash, subject aggregate, review hashes, and accepted disposition.

The loader must receive the trusted manifest through a closed versioned source role.
It must not discover the manifest beside the caller-selected record.
Peer and parent review roles must be distinct and equal the trusted manifest's exact rows.

Add negative controls for a fabricated record, swapped reviews, and a correct record absent from the trust manifest.
All three must remain unable to construct `Accepted<T>`.

## P2: the exact observer contract cannot invoke the current A06 source

A05 specifies this observer output:

```text
--report RUN_ROOT/report.json
--actual-proof
```

The current `verify_orientation_a06.py` rejects that path.
Actual-proof mode requires the report filename to contain `a06` and exclude `a01` through `a05`.
It also requires the producer-sidecar filename to contain `a06`.

The current observer writes its own success report with exclusive creation.
Its failure path also attempts its own exclusive report publication.
A05 instead states that the runner owns every output file.

The current source therefore cannot satisfy the stated command and writer ownership.
This is a contract conflict, not a missing hash.

Choose one model before accepting an observer successor:

1. Keep child-owned publication and use one exact A06-compatible success/failure filename contract.
2. Change and review the observer source so it returns bounded data for runner-owned publication.

The qualification must bind the chosen source, filename, writer, collision behavior, and failure residue.
It must not treat unchanged A06 as conforming to `RUN_ROOT/report.json`.

## Exact command checks

The Rust argument names and order match `feasibility-rust-a05/src/main.rs`.
That parser rejects unknown flags, duplicate required flags, missing values, and non-absolute paths.

The Swift argument names match `feasibility-swift-a15/probe.swift`.
The Swift parser stores arguments in a dictionary.
It overwrites duplicate keys and ignores unknown key names that carry values.

The future runner must therefore remain the authority for the exact Swift argument sequence.
No caller-supplied suffix or key-value map may enter that command.

The A06 observer argument names match its parser.
Its filename and publication rules do not match A05, as described above.

## Confirmed boundaries

A05 repairs the earlier whole-pipeline assembly defect.
Rust, Swift, observer, and comparator qualifications now have separate stages.

The comparator accepted enum remains uninhabited.
Rejected A11 and pending A12 cannot serialize comparator authority.

The Rust stage excludes Swift, observer, and comparator roles.
Incomplete later evidence cannot block a future Rust-only authorization.

The process limits, active pipe draining, cancellation sequence, and direct-child reap bounds are explicit.
The design does not claim that process-group signals reap escaped descendants.

The saved Swift build proves compilation only.
The saved four-control report proves four bounded pure controls only.
Neither record establishes native producer execution or text feasibility.

## Required successor before implementation

1. Preserve A05 and both A05 reviews.
2. Replace top-level dictionary counts with typed, field-by-field expansions.
3. Version the role index to encode every required observation kind.
4. Add an external trust anchor for acceptance records.
5. Choose and bind one observer report writer and filename contract.
6. Keep comparator authority uninhabited until an exact successor qualifies.
7. Review loader and runner source before creating any authorization.

## Review limits

This was a same-model-family, nonblind review.
It was not independent-source-origin or cross-family evidence.

This review establishes no native execution, native text feasibility, product integration, playback, hearing, film quality, or creative acceptance.
