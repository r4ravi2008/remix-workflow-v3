# Native preparation design A05: parent review

Root read all 1,051 lines of A05 after reading the complete A04 baseline and its peer findings.
A05 is 37,998 bytes with SHA-256 `336e19dd491ac04843e31cb4b93b189e5cfb982c0312e55cf123fc182a0ad1d0`.
Root checked producer arguments and observer arguments against their saved source parsers.
Root inspected the actual Swift build and pure-control input structures.
No helper, gate, control, producer, observer, comparator, compiler, or native process ran.

A05 repairs the whole-pipeline assembly problem.
Rust, Swift, observer, and comparator authorities have separate stages.
The accepted comparator variant is uninhabited while its evidence remains pending.
Machine-readable acceptance replaces a caller-supplied verdict.
The corrected readiness hash and finite stage limits are explicit.

One P2 artifact-model gap remains before implementing these role schemas.
Independent same-family design review remains pending.

## P2: heterogeneous observations are counted as regular-file roles

The Swift role table declares thirteen build inputs and thirteen pure-control inputs.
Those numbers are dictionary field counts in the actual reports.
They are not counts of regular files.

`swift-build-attempt-a02/report.json` has thirteen `closureBefore` fields:

- regular-file observations for the compiler, helper, manifest, Python executable, and SDK settings;
- invocation symlink observations for the compiler, Python, and SDK;
- directory observations for the SDK and source root;
- two path Strings;
- a list containing twenty-one source-file rows.

`swift-pure-controls-attempt-a03/report.json` also has thirteen `inputsBefore` fields.
The fields include seven files, seven logs, six binaries, four held binary aliases, the build closure, three directories, and boolean join results.
Its thirteen keys cannot expand into thirteen `MeasuredArtifact` regular-file rows.

The universal observation rule currently opens only regular files.
The binary role index has only file size/hash and optional Mach-O fields.
It cannot encode the invocation symlink or directory facts needed by these joins.
Resolving an invocation to a regular executable does not preserve the separately recorded invocation-link identity.

Define an exact typed expansion adapter for every heterogeneous report field.
Distinguish regular files, invocation links, directory authorities, scalar constraints, and aliases.
Either give those observations explicit kind-specific wire forms or keep non-file facts in a separately typed authority section.
Specify each field's expansion, role names, order, count, and alias rule.
Generate the cardinalities from that closed expansion, rather than from the number of dictionary keys.

Apply the same rule to Rust toolchain launcher and SDK invocation facts where they are non-regular observations.
Do not silently drop them or label them regular files.

Add controls for an unchanged resolved executable with a replaced invocation link, a replaced directory authority, and a nested source-list mutation.
Each mutation must invalidate the appropriate stage aggregate or join before launch.

## Remaining stage boundaries

The source-only Rust role-index and qualification work can proceed after this observation model is repaired.
Its native runner still requires source review, pure controls, and an exact authorization before any producer launch.
Swift, observer, and comparator stages remain separately unavailable while their qualifications are incomplete.

Any future observer successor must define its exact report filename and writer ownership.
The current A06 observer writes the report itself and requires an A06 filename for `--actual-proof`.
A05's generic `report.json` command is a future contract, so it must not be used with the current A06 observer unchanged.

This design review establishes no native execution, text feasibility, product integration, playback, hearing, or creative acceptance.
