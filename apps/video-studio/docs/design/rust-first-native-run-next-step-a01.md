# Rust first native run next-step audit A01

## Result

The smallest path is a Rust-only trust and qualification successor around the existing A04 runner.

Do not redesign the A04 child lifecycle.
Do not wait for Swift, observer, or comparator acceptance.

Four bounded changes remain:

1. Freeze and qualify the repaired A03 Rust subject adapter.
2. Implement the pinned Rust trust root and Rust qualification loader.
3. Connect that opaque qualification to an A04 runner successor.
4. Publish and review one attempt-specific authorization before the first child launch.

The subject adapter remains diagnostic evidence.
Only the pinned loader can construct production qualification authority.

## Verified base

| Component | Current evidence | Usable scope |
| --- | --- | --- |
| Native preparation A05 | Pure-control report `f68eafc1531f2c36467833b093e21db2cb26d50fc33c3aeae3dedb7f9b16a98d` | Five saved-report controls passed. Pinned acceptance remains unavailable. |
| Rust runner A04 | Built CLI `4533f514e9fb5f44755a8713a952a2b5976b81c79e21cc6d58049f2ebb836659` | The unavailable-loader branch returns exit 78 without creating output. |
| Rust runner controls | Report `22a92d6c64555fa047ced008b741643d8d68afb07caf5db81faca5a83b2d18ab` | Ten fake-child lifecycle and file controls passed. No A05 producer ran. |
| Rust subject adapter A03 | Repair is in progress | Its result is diagnostic only. It cannot authorize execution. |

The selected A05 design makes the Rust stage independent.
The A06 design adds a noncyclic pinned trust root.
The A07 design fixes the RoleIndex V2 tags.

## Exact current blockers

### 1. Pinned acceptance has no implementation

`native-preparation-implementation-a03/src/acceptance_v2.rs` still has these deliberate stubs:

- `AcceptanceTrustRootV1::open_pinned()` returns `PinnedManifestAbsent`;
- `Accepted<T>` contains `Infallible`, so it cannot carry a qualified value;
- `AcceptanceV2::require` returns `NoPinnedTrustRoot`;
- `AcceptanceV2::qualify` returns `NoPinnedTrustRoot`.

No trust manifest or acceptance record exists for this implementation.

The successor must replace these stubs with the reviewed A06 trust chain:

```text
reviewed loader source and binary
  -> compiled pin
  -> embedded exact trust-manifest bytes
  -> exact acceptance-record bytes
  -> exact subject RoleIndex V2 and two reviews
  -> private Accepted<T>
```

Keep the generic `qualify(candidate)` shortcut unavailable.
Qualification must select a closed subject key from the pinned manifest.

### 2. Rust qualification reconstruction is absent

Add one Rust-only qualification module to the native-preparation successor.
The module must call the repaired subject adapter through its fixed entry point.

The module must reconstruct these authorities from measured saved files:

- Rust source, dependency, build, toolchain, input, and PNG-control evidence;
- the accepted A04 runner source, build, and ten-control evidence;
- their exact RoleIndex V2 rows and aggregates;
- the required acceptance records and peer and parent reviews.

The A05 role schema requires five acceptance records:

1. source;
2. build;
3. input;
4. PNG control;
5. runner.

The first-unit trust manifest needs exactly two top-level entries:

- `RustProducerSourceV1`, containing the first four accepted evidence classes;
- `RustProducerRunnerV1`, containing the accepted runner evidence.

The manifest must contain no Swift, observer, orientation, or comparator entry.

The loader must return one opaque Rust qualification.
That value must retain the exact RoleIndex evidence and a private full-revalidation operation.

The repaired A03 diagnostic candidate is an input to this operation.
It is not the accepted value and cannot serialize an authorization.

### 3. The A04 runner loader is still a stub

`rust-producer-runner-a04/src/lib.rs::load_pinned_rust_qualification()` returns `MissingAcceptance`.

The successor must replace the runner-local placeholder with the opaque Rust qualification.
The caller must not supply paths, hashes, roles, commands, limits, or dispositions.

The runner must invoke full qualification revalidation at two boundaries:

1. before it creates an attempt authorization;
2. after child closure and before terminal publication.

The current `authority_before` and `authority_after` file observations remain useful report evidence.
They do not replace RoleIndex reconstruction and cross-join validation.

Keep the reviewed A04 process code unchanged where possible:

- exact A05 child command;
- cleared four-variable environment;
- fresh run directory;
- pipe draining and bounded logs;
- cancellation marker and process-group closure;
- bounded output inventory;
- causal terminal fallback.

### 4. The current authorization is static and incomplete

`QualificationData.authorization` is a pre-existing artifact.
It cannot bind the fresh run-directory name created later by `run_accepted`.

Replace that field with an attempt authorization created by the stage.
Create it after the fresh name is known and before child launch.

The authorization must bind:

- implementation and repetition;
- qualification RoleIndex artifact and aggregate;
- measured A05 executable;
- resolved output parent and fresh run-directory name;
- exact command and environment;
- process, output, and cancellation policies;
- `native_result_accepted=false`;
- `product_integration_allowed=false`.

Use descriptor-relative exclusive creation under the retained output-parent descriptor.
Retain the reviewed 4 MiB authorization limit.

The stage must expose the saved authorization for review before execution.
Execution must consume that same typed authorization without rebuilding caller-selected fields.

`ClosedProducerRun.authorization` must reference this attempt-specific file.

## Required files before the first launch

The bounded Rust-first closure needs these new data files:

1. the frozen subject RoleIndex V2 bytes and receipt;
2. the frozen runner RoleIndex V2 bytes and receipt;
3. five strict machine-readable acceptance records;
4. peer and parent review artifacts for each record;
5. one two-entry trust manifest;
6. one external bootstrap record for the loader source, built binary, and compiled pin;
7. one reviewed primary attempt authorization.

The bootstrap record cannot be authenticated by the manifest that it enables.
Root must bind that source and binary externally before use.

## Finite prerequisites

### Repaired subject adapter

Before trust data is authored, require:

- one frozen complete role and tag schedule;
- one bounded, nonblocking, no-follow vector read with before and after identity checks;
- no `baseline_passed` claim without a candidate construction;
- compile evidence and fixed source controls;
- add, remove, reorder, retag, FIFO, symlink, growth, and replacement negatives;
- two fresh reconstructions with identical RoleIndex V2 bytes and aggregate.

### Trust and Rust qualification

Require focused controls for:

- embedded manifest byte count and SHA-256;
- duplicate, missing, unknown, and wrong-type fields;
- an absent or fabricated acceptance record;
- swapped, aliased, or mutated reviews;
- subject, runner, or aggregate mutation;
- manifest-pin mutation;
- self-reference and reference cycles;
- caller construction of `Accepted<T>`;
- exact three-way equality between trust entry, acceptance record, and reconstructed subject;
- rejection of every Swift, observer, orientation, and comparator role.

### Runner successor

Re-run the existing ten A04 lifecycle controls against the changed runner binary.
Add only these qualification and authorization controls:

- missing pin creates no run directory or authorization;
- exact two-entry qualification loads;
- preflight and postflight RoleIndex values match;
- either-boundary drift closes the attempt;
- an existing authorization path is preserved and rejected;
- each bound authorization field rejects one mutation;
- prelaunch cancellation starts no child;
- `ClosedProducerRun` joins the exact authorization artifact.

No broader process, media, observer, or comparator matrix is required for this Rust-first step.

## First run boundary

After all prerequisites pass, run one bounded Rust A05 primary attempt.

Read back the exact producer binary, source closure, build manifest, authorization, process facts, inventory, and terminal report.
Keep the completion state `completed_external_qualification_pending`.

That run can establish direct native producer execution and retained output evidence.
It cannot establish output correctness, native text acceptance, product integration, playback, hearing, or creative acceptance.

Observer and comparator qualification remain later independent stages.
Swift remains a separate producer stage.

## Audit status

This audit is read-only.
No package, trust manifest, acceptance record, authorization, process, media file, or project state was created or changed.

The review is same-model-family and nonblind.
No cross-family review is claimed.
