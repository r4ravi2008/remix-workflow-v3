# Rust producer runner A10 root orchestration source peer review A01

## Disposition

**Rejected for execution pending repair.** The wrappers have one P1 identity
failure and four P2 evidence or failure-handling gaps. The shared A09 process
utility A04 remains source-accepted with no P1 or P2 finding. That acceptance
does not authorize a caller, compiler, control process, bootstrap, or producer.

This is a same-model-family, nonblind source review. I read the complete three
A10 wrapper sources, the rationale, the preparation receipt, the referenced
A09 contract and output schema, and the complete A04 utility review pair. I did
not import, compile, execute, test, launch a child, run a probe, or use native,
media, GPU, Resolve, playback, listening, or creative workflows.

The A10 native source writer is still under repair. This review does not review
or qualify that candidate.

## Frozen identities

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `rust-producer-runner-a10-readonly-root-source-measurement-a01.py` | 14,766 | `021fe5e963f13a4678afa414e7de59ae3aad0da09123c74d0497aac94184c2b0` |
| `native_runner_fixed_compile_a10.py` | 18,236 | `34250b279c53dd96ac280eba7a0183dd57629a68eb5e6b1c5aa7d15968849038` |
| `native_runner_fixed_controls_a10.py` | 20,607 | `17a468f0a45723b6459edbc636734959e167aee920630a241accfef8c8f2de3b` |
| `orchestration-rationale-a01.md` | 2,552 | `38959df671be9a7cf2f086cb2aef005c66df940552acad48f01f399cc4f53c2e` |
| `preparation-receipt-a01.json` | 2,079 | `6e6d3ed680ef27c5849abedd2b1274f76146e37faf8438dd2b228dfd87858999` |

The receipt records `callerSourceAccepted=false`, `rootGatePresent=false`, and
false compiler, control, and native execution flags. The two A10 orchestration
review paths named by the future gate do not exist yet. The A10 source readback,
bootstrap, build attempt, and control attempt are also absent.

The receipt binds the A04 utility at 46,572 bytes with SHA
`b903a9aff1cc2d8dae73b16800f177322b000b2983e5a45206a639326727d47d`.
Its rationale is 910 bytes, SHA
`9c9dfceecc27187ab254dcfd812e2432d57790e912249d50ee2f9c40bc79d48f`.
The A04 receipt is 870 bytes, SHA
`d50e7c4229599c98273aabcd52dae19d2ca6d2563824ec91918cf6d4369641a3`.
The A04 parent and peer review hashes are respectively
`7dea7f28e0da745944151e84ff9784928586548652a035d185d0cc11b8098488` and
`f7ced48cb3d61a0e22439354ae6e451208e38313f15c252ced480f62e3a560d8`.

For comparison, the A09 contract is 7,906 bytes, SHA
`faa9681b31c339f3005589d56b29f69a7fbc77511fbd36c486988fca1774a130`, and the
A09 output schema is 5,052 bytes, SHA
`d5afb4b6bf985e51c643c5ff63e11710f2a6c137578c78292232c55f5206621b`.

## P1 findings

### P1.1: `source-manifest-a10.json` is an A09 manifest

The current 51,013-byte `rust-producer-runner-a10/source-manifest-a10.json`
has SHA `e0433445a7f9c782a7ed7a729844451d77853a0a8dac251b688b5aea18609943`.
Its parsed subject is `rust-producer-runner-a09`. Its state, source root,
aggregate domains, external rows, bootstrap paths, and control paths are A09.
The listed source files include `direct-build-recipe-a09.json`,
`output-schema-a09.md`, `src/a05_focused_controls.rs`, and
`src/a09_launch_controls.rs`.

The current A10 directory contains A10-named files and `src/a10_*` controls.
The manifest's 15 rows do not match those files. A read-only rehash found only
the unchanged `src/pure.rs` row matching. The other rows are absent or have
different bytes and hashes. The A10 directory contains 15 source files, but
its current `Cargo.toml`, README, recipe, schema, fixtures, contract,
rationale, focused controls, launch controls, `lib.rs`, and `main.rs` all have
different identities from the manifest rows.

The source helper requires package `rust-producer-runner-a10` and source root
`P` at lines 205–210. The compile caller repeats the package equality check at
lines 92–100. Therefore the helper and caller reject the frozen package before
source closure or build admission. The recipe also requires the A10 manifest,
so the stale row set cannot be treated as a harmless label.

Regenerate the A10 manifest from the current intended A10 files. Recompute the
framed source and external aggregates. Bind the corrected manifest to the
recipe, source readback, caller review, and future root gate. Preserve this
review and the stale manifest as historical failure evidence.

The identity drift also reaches the bootstrap boundary. The A10 contract and
recipe source closure name an A10 bootstrap path, while the stale manifest and
recipe preconditions name an A09 bootstrap and A09 source manifest. Choose one
reviewed A10 bootstrap contract and bind every path, role, and hash to it before
any child launch.

## P2 findings

### P2.1: The callers do not authenticate their own source before starting work

Both callers authenticate the held A04 utility before `exec(compile(data, ...))`.
That is a sound utility handoff. The callers only measure their own
`Path(__file__)` after the interpreter has already loaded and begun executing
the caller. The receipt lists caller hashes, but neither caller compares its
own bytes with an expected receipt before creating an attempt or invoking the
utility.

The future root gate must bind the exact helper, compile caller, controls
caller, receipt, and review bytes before either caller starts. A fixed launcher
must reject a changed caller before side effects. This is a source identity
boundary, not a claim of general host-tamper protection.

### P2.2: Compile admission relies on Python `assert` for security-relevant checks

The compile caller uses `assert` for package, recipe, source-readback,
dependency, output, per-phase, and Mach-O checks at lines 92–125, 187, 201,
214, and 220–225. Python removes these checks under `-O`.

The Rust command vectors do not constrain the Python interpreter mode. Replace
these assertions with the authenticated utility's explicit `require` path, or
bind a fixed non-optimized interpreter invocation in the external caller gate.
The source helper and controls caller already use explicit conditions for most
of their checks.

### P2.3: Caller-side failures can bypass final report publication

After the compile caller creates the attempt and writes `preflight.json`, its
own Mach-O parsing, inventory, identity, and final-anchor failures raise
directly before `report.json` is saved at lines 168–251. The controls caller has
the same shape after it launches the private control: inventory, parsing,
report-join, process-absence, and anchor failures can raise before
`controls-run-report-a01.json` is saved at lines 157–298.

The A04 utility retains the owned process on exceptional cleanup, but it cannot
publish a caller-side causal record that the caller never writes. Add a bounded
caller failure writer and `finally`-style descriptor closure. The record must
retain the utility phase result, partial inventory, parser or anchor code, and
partial publication identity. A caller failure must not look like an absent
attempt or an unqualified successful phase.

### P2.4: The control report join does not derive every A09/A10 obligation

The controls caller validates the fixed IDs, many row orders, nested report
equality, pure results, process-field mappings, normal marker PID, and broad
PID/group absence. This is useful source validation.

The join still accepts several self-reported summary facts. It does not require
the combined report's `exactCaseOrder`, `resultCount`, `passedCount`, or
`preservedRealLifecycleCaseCount`, nor the focused report's
`allControlsPassed`. It records but does not reject `parse_failures` for
malformed private JSON. Failure variants do not require marker absence, an
explicit saved failure or reap-failure disposition, and the variant-specific
no-resume/SIGCONT expectations. The join checks `reaped` only when adding a
terminal wait check; a self-reported failure row can therefore pass without the
full A09 terminal truth required by the contract.

Derive all aggregate fields from parsed rows. Reject every unparsed JSON entry.
For each launch ID, require the A09/A10 expected marker, stop, resume, SIGCONT,
reap, terminal-code, and foreign-group relation. Keep injected fault labels
separate from kernel observations. Bind the resulting A10 output schema after
the native A10 source writer finishes; the current A09-derived manifest and
the future A10 schema are not yet a coherent acceptance subject.

## Correctly bounded source behavior

The read-only helper uses bounded regular-file reads with `O_NOFOLLOW` and
`O_NONBLOCK`. It checks the opened descriptor and pathname identity before and
after reading. It rejects duplicate JSON keys, nonfinite values, oversized
objects, and unbound Rust include edges. Its exclusive readback writer uses a
descriptor-relative create, bounded chunks, `fsync`, held-file readback, and a
parent-directory sync.

The callers read the utility through one held descriptor, verify its exact size
and SHA-256, and execute those exact bytes. They reconstruct the fixed Rust
vectors, environment, output paths, limits, and absent-attempt conditions. The
compile schedule is four 60-second phases. The private control schedule is one
360-second phase with 21 pure cases, 10 preserved lifecycle cases, 15 focused
cases, 11 launch variants, and five nested review variants. The callers retain
the original cwd and attempt anchors and ask the A04 utility to report process
and group closure.

The A04 review correctly permits exceptional cleanup supervision beyond normal
deadlines. Forced orchestration termination and arbitrary host security remain
outside that in-process guarantee. These limits must remain explicit in any
future A10 receipt.

## Scope boundary

This review establishes no compiler result, control result, bootstrap, producer
child, native output, media output, product integration, loaded-runtime
attestation, WATCHED, HEARD, playback, listening, or creative acceptance.
The A10 root gate is absent. The native A10 source writer remains pending.
