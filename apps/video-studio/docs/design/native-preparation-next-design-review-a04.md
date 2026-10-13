# Native text preparation next design review A04

## Disposition

I found no P1 in the preserved design artifact because it creates no executable authority.

Five P2 findings block implementation of a gate or runner from this design.
Comparator A11 is root-rejected, so it cannot satisfy the design's only comparator variant.
Comparator A12 remains pending and cannot enter any authorization by version substitution.

The A04 source identity is:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `native-preparation-next-design-a04.md` | 28,211 | `099dfd7fec7f394f0151541288d2e6dd75c8eae11b0673d2f2a1b056bbbc01a0` |

No helper, gate, control, compiler, producer, observer, comparator, GPU process, or Resolve process ran during this review.

## P2: whole-preparation assembly defeats staged authorization

The caller supplies Rust, Swift, comparator, and observer qualifications to one `assemble` call.
Any missing prerequisite makes `assemble` return a diagnostic that cannot authorize execution.

That rule conflicts with two later statements:

- the first implementation unit should authorize only the two Rust attempts;
- an unresolved question should block only its affected authorization.

Comparator A11 is now rejected, and no accepted observer successor exists.
The shown API therefore cannot authorize even the intended Rust-only first unit.

Use stage-specific typestate or stage-specific constructors.
For example, Rust authorization should require only the accepted Rust qualification and shared immutable policy.
Swift, observer, and comparator qualifications should extend that state in later transitions.

The comparator may become version-parametric only through a closed, reviewed variant.
An acceptable shape is `AcceptedComparator::A12(ComparatorQualificationA12)` after A12 qualifies.
Do not accept a version string, directory suffix, `latest` lookup, or generic source manifest.

Adding A12 must add its exact source roles, schemas, controls, closures, reviews, and acceptance record.
The A11 role table and hashes cannot be reused for A12.
A pending comparator value must remain unable to serialize any comparator authorization.

## P2: qualification types do not represent their declared role sets

The prose role graph is deeper than the sketched types.
An implementation cannot reconstruct the declared closed role index from those types.

`SwiftQualificationA15` omits these listed artifacts:

- the build preflight;
- one of the runner wire-schema or rationale documents;
- the no-child control source, rationale, peer review, parent review, and readiness record;
- the pure-control preflight;
- distinct source-review and result-review subjects for the compiler build.

The design also has no `RustQualificationA05` type or exact Rust role inventory.
That omission affects the first implementation unit directly.

`AcceptedReviewSet` contains one subject and a caller-supplied disposition enum.
It does not bind the disposition to a machine-readable acceptance artifact.
One review set also cannot represent two independently reviewed control sources or results without an explicit package subject.

Define exact wire schemas for every qualification.
Each accepted disposition must come from a parsed record that names the subject hashes and review hashes.
The caller must not construct `AcceptedNoP1OrP2` from an unverified Markdown path.

The role-index JSON also needs one specified canonical encoding.
Define field order, integer domains, path encoding, duplicate rules, and schema version.
Both the builder and runner must implement that same closed specification independently.

## P2: observer authority remains an unspecified input

The caller accepts `accepted_observer_closures`, but the design defines no corresponding qualification type.
`ObserverAuthorization` holds only a source artifact and runtime artifact.

It omits these required authorities:

- observer source closure and exact source successor;
- interpreter and installed-runtime closure;
- peer and parent reviews;
- orientation report schema;
- exact producer-sidecar contract;
- the typed producer attempt, executable, gate, and output-inventory join;
- explicit path-identity, binary-execution, exclusivity, and source-lifetime facts.

The existing runtime is stale.
The A03 observer review also leaves pathname-label and provenance corrections open.
The design correctly states both facts, but its public shape can still accept two bare artifacts.

Define separate reviewed Rust and Swift observer qualifications.
Each variant must close its exact source and runtime roles before it can authorize one producer attempt.
The report must preserve the distinction between observed path identity and established execution identity.

## P2: non-producer process and output contracts are incomplete

Only `ProducerAuthorization` carries a closed environment.
Observer and comparator authorizations omit the interpreter, argument vector, working directory, environment, stdin policy, and runtime aggregate.
The two comparator-control stages have limits but no authorization shape.

This omission matters for Python imports and optimization behavior.
An exact source hash does not close `PYTHONPATH`, user-site imports, interpreter flags, or the selected runtime.

Define one exact command contract for each observer, control, and comparator child.
Bind the accepted interpreter, source, arguments, environment, working directory, stdin, and runtime closure.
The runner must launch only that command and recheck every authority after closure.

The producer stage has cumulative byte and entry caps.
The observer, control, and comparator stages list individual file sizes without complete directory inventory limits.
This conflicts with the claim that every partial output remains under stage byte and entry caps.

Each stage needs one fresh descriptor-owned root and one exact output policy.
Use an allowlist or finite cumulative limits for files, directories, entries, logs, reports, fallbacks, and cancellation markers.
Specify whether runner-owned records count in those totals.

If the runner sends process-group signals, it must create and record the new process group before launch completion.
Otherwise, keep control limited to the direct child and retain descendant attestation as false.

## P2: two copied artifact identities are invalid

The Comparator A11 README row records this SHA-256:

`1eb295208fd4cbc65215e796cedefa32261edb227427951cb7aaf6ad08441555`

The preserved A11 package manifest and current README bytes record:

`cacf608a6ba6a1880ea20064ed5762be89d864c60a82d2d3027df937355bbb74`

The no-child readiness row contains only 62 hexadecimal characters.
The preserved readiness record has this SHA-256:

`a49877ffcd8ffcfcbf4adc8c22759daa9c168980c20e62612a5c6fb64651cdc3`

Either error makes the declared cross-joins fail before authorization.
Generate identity tables from retained descriptor reads or accepted manifests.
Do not copy hashes through prose as gate authority.

## Confirmed boundaries and useful shape

The design correctly preserves the A03 release-build and PNG-control step separation.
It also separates comparator source identity from actual-validator control evidence.

The saved Swift four-control report has SHA-256
`43a58d030bc7d4f2d6ddb799871472517e68bece09f70b675bd8e1f0f07c6632`.
It records four passed controls and no native producer start.
It also records that the duplicate PNG executable did not start.

The parent readback has SHA-256
`7f7312a84190033b7e76743b28dee9c550b04bff9b1f20622613d23ff568a10d`.
Its scope remains four path-bound pure-control results.

The no-child result has SHA-256
`3bc886782705a3402ba22537752bb7495d692185a9fd2ac72e0e494941ee6110`.
It records `sourceOnly: true`, `processLaunchAllowed: false`, and `nativeExecutionAllowed: false`.

A04 therefore scopes the accepted pure-control evidence correctly.
Those records do not qualify the Swift producer, ImageIO, Core Text, or native output.

The producer limits are finite and distinguish logical evidence bounds from RSS or framework memory.
The cancellation text also keeps descendant-reaping attestation false.
These parts are suitable inputs to a corrected stage-specific design.

## Required successor before implementation

1. Preserve A04 and its rejected A11 observations.
2. Complete exact A12 source and control review without silently changing A04.
3. Freeze A12 controls, runtime and source closures, readbacks, reviews, and root acceptance.
4. Add A12 as one explicit accepted comparator variant with its own exact role table.
5. Split producer, observer, and comparator qualification into stage-specific transitions.
6. Define complete Rust, Swift, observer, control, and comparator wire roles.
7. Correct the two copied identities and regenerate the aggregate from exact files.
8. Review the resulting helper and gate source before any process execution.

The statement that A04 closes the A03 parent defect is premature.
A04 identifies the missing evidence classes, but no accepted comparator qualification exists yet.

## Review limits

This was a same-model-family, nonblind design review.
It was not a cross-family review.

The review establishes no native feasibility, native execution, output correctness, product integration, playback, hearing, lyrics, film quality, or creative acceptance.
