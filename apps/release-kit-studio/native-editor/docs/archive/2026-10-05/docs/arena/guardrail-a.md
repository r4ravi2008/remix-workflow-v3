# Candidate A: development checks in the current Rust CLI

Status: design only. This candidate executed no repository code or Cargo command.

Architect phases: Ground is complete. Sketch is complete. Agree awaits arena synthesis. Implement and Scrap are outside this design task.

## Usage (caller's view)

1. Use the current binary name.
2. Add `check`.
3. Keep `verify <project> <artifact>` bound to stored artifact verification.
4. Compile development checks explicitly.

The default editor stays independent of development tools.

```sh
# The caller supplies a fresh bootstrap target directory.
CARGO_TARGET_DIR=/tmp/native-editor-bootstrap-20261004-a cargo build \
  --locked --offline -p editor-cli --features development-checks

/tmp/native-editor-bootstrap-20261004-a/debug/native-editor check architecture \
  --root apps/release-kit-studio/native-editor \
  --out /tmp/native-editor-check-architecture-20261004-a

/tmp/native-editor-bootstrap-20261004-a/debug/native-editor check full \
  --root apps/release-kit-studio/native-editor \
  --out /tmp/native-editor-check-full-20261004-a
```

`--out` must name a new directory. Current directories, which include abandoned runs, fail without modification.
The binary prints one compact JSON result with the report path and exits nonzero for required failed or incomplete checks.
The detailed `report.json` records every required check, exact command, exit, identity, hash, and evidence path.
A missing tool becomes `incomplete`. It cannot become a successful check or silently disappear.

An architecture pass says architecture checks passed. It says nothing about render output or creative approval.
A full pass binds actual native acceptance to newly built default and test-hook binaries from this source snapshot.

Three actual call sites define the interface:

```rust
// main.rs: dispatch development checks before constructing the runtime watchdog.
#[cfg(feature = "development-checks")]
if raw_args.first().map(String::as_str) == Some("check") {
    let checked = CheckRequest::parse(&raw_args[1..])?;
    let report = verification::run(checked)?;
    emit_check_summary(&report)?;
    return exit(report.exit_code());
}
// Existing tools/schema/progress/call/verify/demo path stays on Arguments and Registry.
```

```rust
// CLI-owned verification orchestration; caller does not coordinate individual stages.
let report = verification::run(CheckRequest::new(
    CheckMode::Full,
    OwnedWorkspace::discover(root)?,
    NewRunDirectory::reserve(out)?,
))?;
assert_ne!(report.exit_code(), 0); // example: clippy is missing
```

```rust
// Policy regression fixture uses the same policy evaluator as the command.
let findings = Policy::current().inspect(&fixture_with_nested_core_spawn)?;
assert!(findings.iter().any(|f| f.rule == RuleId::CoreProcessApi));
```

No `--passed`, expected hash, evidence-import, feature-promotion, or production `--state` option exists on `check`.
The default build rejects `check` with a structured unsupported-development-command error.
`engine.capabilities` keeps its six typed editor tools. Development checks are not an edit capability.

## Problem and grounding

Rust owns the edit semantics and direct CLI. `editor-core::Editor::execute(Command)` already hides revisions, transactions, pixels, and receipts.
`protocol::Registry` derives schemas from Rust types. `progress()` deliberately clears evidence and prevents trusted promotion.

The CLI currently installs a 1–30000 millisecond watchdog before every operation. That watchdog cannot own a development build sequence.
Acceptance uses `CARGO_BIN_EXE_native-editor` and supports `NATIVE_EDITOR_EVIDENCE_DIR`. These are useful boundaries for proof of the current build.

The current tests exercise replay, concurrency, pixels, stored receipts, tampering, schema mismatch, unsupported tools, deadlines, and crash hooks.

`p0_runtime_policy` has concrete gaps. It reads only immediate `editor-core/src` entries and only CLI `main.rs`.
It converts source to lowercase before it searches for mixed-case `Command::new(`. Thus, that check cannot match.
It misses nested source, future CLI modules, workspace build scripts, feature edges, and dependency ownership.

Both document checkers write fixed repository receipts. Parallel verification can overwrite another run's document evidence.
These defects need one owned inventory and isolated output paths. More textual instructions cannot correct these defects.

The candidate used these inputs:

- Workspace and crate manifests
- CLI main and protocol
- Core public entry point
- Actual acceptance tests
- Both document checkers
- AGENTS, SPEC, ARCHITECTURE, WORKFLOW, and PROGRESS
- Architect runner, rationale, and red-flags
- Applicable architecture principle leaves
This candidate applies boundary-discipline, foundational-thinking, encode-lessons-in-structure, separate-before-serializing-shared-state,
and minimize-reader-load. The parent's arena provides the structurally different alternative candidate.

## Shape: report and check data first

All types below are in the cfg-gated CLI verification module. They do not enter `editor-core` or process protocol schemas.

Wire report structs derive `Serialize` and `JsonSchema`. Only trusted constructors create verdicts and identities.
Current `editor_core::sha256`, `canonical_bytes`, `PROTOCOL_VERSION`, `IDENTITY_VERSION`, and `VERSION` supply shared identity functions and values.
Current `protocol::Registry` supplies the compiled schema contract. Acceptance still reads information from actual child binaries.

```rust
use std::path::{Path, PathBuf};
use std::time::Duration;
use serde::Serialize;
use schemars::JsonSchema;

#[derive(Serialize, JsonSchema)]
pub enum CheckMode { Architecture, Full }
pub struct CheckRequest {
    mode: CheckMode,
    workspace: OwnedWorkspace,
    run: NewRunDirectory,
}
pub struct OwnedWorkspace { root: PathBuf }
pub struct NewRunDirectory { root: PathBuf } // reserved with create_dir, never create_dir_all
pub struct SourceSnapshot { root: PathBuf, identity: SourceIdentity }
#[derive(Serialize, JsonSchema)]
pub struct Sha256(String); // exactly 64 lowercase hex characters
#[derive(Serialize, JsonSchema)]
pub struct RelativeEvidencePath(PathBuf); // confined beneath this run; no symlinks

#[derive(Serialize, JsonSchema)]
pub struct SourceIdentity {
    files: Vec<SourceFile>, // sorted, unique relative paths; exact bytes included in tree hash
    tree_sha256: Sha256,
    cargo_lock_sha256: Sha256,
    git_head: Option<String>, // context only; content hash remains authoritative
}
#[derive(Serialize, JsonSchema)]
pub struct SourceFile { path: PathBuf, bytes: u64, sha256: Sha256 }
#[derive(Serialize, JsonSchema)]
pub struct BinaryIdentity {
    path: RelativeEvidencePath,
    binary_sha256: Sha256, // measured from file bytes
    schema_sha256: Sha256, // observed from this binary's tools output
    protocol_version: u8,
    identity_version: u8,
    kernel_version: String,
    build_configuration: BuildConfiguration,
    discovery: EvidenceFile,
}
#[derive(Serialize, JsonSchema)]
pub enum BuildConfiguration { Default, TestHooks, DevelopmentChecks }
#[derive(Serialize, JsonSchema)]
pub struct EvidenceFile { path: RelativeEvidencePath, bytes: u64, sha256: Sha256 }
#[derive(Serialize, JsonSchema)]
pub enum CheckVerdict {
    Passed,
    Failed { findings: Vec<Finding> },
    Incomplete { reason: IncompleteReason },
    NotApplicable { reason: String },
}
#[derive(Serialize, JsonSchema)]
pub enum IncompleteReason {
    MissingTool { tool: String },
    UnsupportedPlatform { required_operation: String },
    PrerequisiteFailed { check: CheckId },
    TimedOut,
    SourceChanged,
    EvidenceUnavailable { detail: String },
}
#[derive(Serialize, JsonSchema)]
pub struct CheckObservation {
    id: CheckId,
    required: bool, // derived from the compiled mode plan, never accepted from the caller
    scope: String,
    verdict: CheckVerdict,
    commands: Vec<CommandObservation>,
    evidence: Vec<EvidenceFile>,
}
#[derive(Serialize, JsonSchema)]
pub struct CommandObservation {
    executable: PathBuf, // resolved actual executable
    arguments: Vec<String>,
    cwd: RelativeEvidencePath,
    environment: Vec<(String, String)>, // explicit nonsecret overrides only
    started_at: String,
    elapsed_ms: u64,
    outcome: ProcessOutcome,
    stdout: EvidenceFile,
    stderr: EvidenceFile,
}
#[derive(Serialize, JsonSchema)]
pub enum ProcessOutcome {
    Exited { code: i32 },
    Signaled { signal: i32 },
    TimedOut { group_terminated: bool },
    SpawnFailed { detail: String },
}
#[derive(Serialize, JsonSchema)]
pub struct Finding { rule: RuleId, path: PathBuf, line: Option<u32>, detail: String }
#[derive(Serialize, JsonSchema)]
pub enum RuleId {
    CrateOwnership, DependencyOwnership, ForbiddenMediaBackend, CoreProcessApi,
    RuntimeProcessApi, BuildScript, UnclassifiedSource, UnsafeCode, DynamicSource,
    CapabilityState, ContractSchema,
}
#[derive(Serialize, JsonSchema)]
pub enum CheckId {
    SourceInventory, ManifestOwnership, DependencyGraph, SourcePolicy,
    Specification, FeatureCoverage, CapabilityState, PolicyNegativeFixtures,
    Format, DefaultBuild, HookBuild, DefaultAcceptance, HookAcceptance,
    DevelopmentAcceptance, DefaultClippy, HookClippy, DevelopmentClippy,
    BinaryIdentity, RuntimeSchema, FinalSourceIdentity,
}
#[derive(Serialize, JsonSchema)]
pub struct Report {
    report_version: u16,
    mode: CheckMode,
    run_directory: PathBuf,
    verifier_binary_sha256: Sha256,
    source: SourceIdentity,
    tool_versions: Vec<(String, String)>,
    tested_binaries: Vec<BinaryIdentity>,
    checks: Vec<CheckObservation>,
    limits: RunLimits,
    runtime_scope: String,
    review_scope: String, // measured checks only; creative review remains open
}

impl Report {
    /// Zero only when every required check passed and snapshot identity stayed stable.
    pub fn exit_code(&self) -> i32 { unimplemented!() }
}
```

`Passed` needs the expected exit and parsed evidence predicates. Exit zero alone does not establish native schema identity.
The report never contains a field that promotes a capability. `progress()` remains authoritative for compiled implementation state.

## Signatures and ownership

```rust
#[derive(Serialize, JsonSchema)]
pub struct RunLimits {
    total_ms: u64,           // fixed 30-minute maximum
    child_max_ms: u64,       // per-check fixed limits, at most 10 minutes
    log_bytes: u64,          // fixed 64 MiB per stream
}
pub struct VerificationError { detail: String }
pub struct Policy; // compiled concrete rule table, no caller-extensible framework
pub struct Inventory {
    files: Vec<OwnedSource>,
    packages: Vec<OwnedPackage>,
    resolved_graph: Option<ResolvedGraph>, // None produces incomplete dependency evidence
}
pub struct OwnedSource { path: PathBuf, bytes: Vec<u8>, owner: SourceOwner }
pub enum SourceOwner { CoreRuntime, CliRuntime, Verification, Acceptance, Documentation }
pub struct OwnedPackage {
    name: String,
    manifest: PathBuf,
    targets: Vec<CargoTarget>,
    dependencies: Vec<OwnedDependency>,
}
pub struct CargoTarget { name: String, kind: String, source: PathBuf }
pub struct OwnedDependency {
    alias: String,
    package: String,
    kind: DependencyKind,
    target_condition: Option<String>,
    optional: bool,
    enabling_features: Vec<String>,
}
pub enum DependencyKind { Normal, Development, Build }
pub struct ResolvedGraph { packages: Vec<ResolvedPackage>, edges: Vec<ResolvedEdge> }
pub struct ResolvedPackage { id: String, name: String, version: String, source: Option<String> }
pub struct ResolvedEdge { from: String, to: String, kind: DependencyKind, target: Option<String> }
pub struct CommandSpec {
    executable: PathBuf,
    arguments: Vec<String>,
    cwd: PathBuf,
    environment: Vec<(String, String)>,
    deadline: Duration,
    stdout: PathBuf,
    stderr: PathBuf,
}
pub struct ProcessRunner { run_root: PathBuf, limits: RunLimits }

impl CheckRequest {
    pub fn parse(args: &[String]) -> Result<Self, VerificationError> { unimplemented!() }
    pub fn new(mode: CheckMode, workspace: OwnedWorkspace, run: NewRunDirectory)
        -> Result<Self, VerificationError> { unimplemented!() }
}
impl OwnedWorkspace {
    pub fn discover(root: impl AsRef<Path>) -> Result<Self, VerificationError> { unimplemented!() }
    pub fn snapshot(&self, run: &NewRunDirectory) -> Result<SourceSnapshot, VerificationError> { unimplemented!() }
}
impl NewRunDirectory {
    pub fn reserve(path: impl AsRef<Path>) -> Result<Self, VerificationError> { unimplemented!() }
    pub fn publish(&self, report: &Report) -> Result<EvidenceFile, VerificationError> { unimplemented!() }
}
impl Policy {
    pub fn current() -> Self { unimplemented!() }
    pub fn inspect(&self, inventory: &Inventory) -> Result<Vec<Finding>, VerificationError> { unimplemented!() }
}
impl ProcessRunner {
    pub fn run(&mut self, command: CommandSpec) -> CommandObservation { unimplemented!() }
}
/// Completes the compiled mode plan; failed prerequisites produce explicit incomplete observations.
pub fn run(request: CheckRequest) -> Result<Report, VerificationError> { unimplemented!() }
```

The public API hides inventory rules, command plans, tool discovery, source snapshots, targets, deadlines, logs, identities, and report publication.
Only mode, root, and fresh output location remain visible. No caller coordinates policy stages or imports transport structs.

| Module | Knowledge hidden |
| --- | --- |
| `editor-cli/src/main.rs` | Top-level early dispatch. Current editor command watchdog |
| `editor-cli/src/verification/mod.rs` | Fixed check plan, report contract, aggregate result, immutable publication |
| `editor-cli/src/verification/policy.rs` | Recursive source classification, Cargo ownership, source and capability policy |
| `editor-cli/src/verification/process.rs` | Child groups, bounded waits, log drain, evidence paths, tool resolution |
| `editor-cli/tests/acceptance.rs` | Current actual-process native behavior and independent PNG byte checks |
| `editor-cli/tests/verification.rs` | Development command, negative fixtures, concurrent runs, failure evidence |

1. Use optional CLI dependencies `syn` with full and visit parsers, and `toml`.
2. Only if necessary, add a small pinned platform process-control dependency.
3. Keep default CLI dependencies and `editor-core` dependencies unchanged.
4. Do not add a third crate, server, or generic checker plugin registry.

## Enforceable guardrails

### Cargo ownership

1. Discover workspace members and every target through Cargo metadata.
2. Make sure that metadata names both permitted members and no other members.
3. Parse all dependency kinds, features, target sections, aliases, patches, and sources.
4. For new ownership, get a reviewed policy change.
5. Permit only the current core normal dependencies.
6. Ban core development and build dependencies that import CLI or future application layers.
7. Allow CLI development parser and process dependencies only behind `development-checks`.
8. Prove that the default resolved graph excludes those dependencies.
9. Scan all resolved package names and source identities for FFmpeg, libav, bindings, and application dependencies.
10. Include dependencies with renamed keys in that scan.
11. Pin the reviewed graph, package, and source identities.

Native dependency build scripts such as bundled SQLite differ from forbidden workspace build scripts. Metadata uses `--locked --offline`. Missing cached dependencies produce incomplete evidence without network access or lockfile mutation.

### Source inventory

1. Make a recursive inventory of all owned files, not only `src` or `main.rs`.
2. Include nested modules, tests, examples, benches, build scripts, manifests, and lockfile.
3. Reject symlinks, external module paths, workspace build scripts, `include!`, unclassified executable source, unexpected crate targets, and dynamic source generation.
4. Also scan cfg-disabled branches.

A feature cannot hide a prohibited backend.

### Source policy

1. Use `syn` to parse Rust.
2. Track direct paths and import-alias paths.
3. Forbid process APIs throughout core.
4. Ban `std::process::Command`, spawn APIs, and aliases throughout normal CLI modules.
5. Permit `std::process::exit` only at the CLI terminal owner that exists now.
6. Permit process creation only in verification/process.rs and acceptance tests.
7. Prove that verification modules are cfg-gated.
8. Prove that only early `check` dispatch can reach the verification modules.
9. Reject unknown macros that can hide executable tokens.
10. Allow only macros that exist now and have review approval.
11. Include the current retry macro and type derives.
12. Reject unsafe and extern FFI in owned core source until review approves a named native boundary.
13. Add a normalized literal scan for historical renderer paths and forbidden executables.

Examples of bans in documents are not runtime findings. This is a restrictive repository policy. It is not a theorem about arbitrary Rust or all third-party dependencies.

### Capability state

1. Parse ledger state strictly.
2. Accept only known IDs, native Rust owners, native-only prerequisites, acyclic phases, valid contract paths, and known implementation states.
3. Reject `verified` claims while trusted promotion is unimplemented.
4. Compare compiled progress against actual discovery and implemented IDs.
5. Never accept caller or historical receipt claims as current-build evidence.

### Runtime schemas

1. Preserve Rust-derived schemas.
2. Read information from each newly built binary with `tools` and every `schema` command.
3. Make sure that protocol and identity versions, schema hash, and six tool names are correct.
4. Make sure that the eight bounded CORE families and progress behavior are correct.
5. Reuse actual acceptance for duplicate keys, unsupported tools, invalid inputs, receipt tampering, replay, and hooks.

A schema transport test adds to Rust semantic tests. It does not redefine semantic validation in JavaScript.

### Document checks

1. Change both document checkers to stdout-only by default.
2. Support `--report <new-file>` with exclusive creation.
3. Invoke both document checkers inside the snapshot with separate report paths.
4. Keep their scope as document structure only.

Node is a development check prerequisite. Node is never a native editor runtime dependency.

Architecture mode executes inventory, manifest and graph policy, source policy, document checks, capability-state checks, and embedded policy-negative fixtures. It does not compile the renderer or claim actual runtime acceptance.
Full mode includes architecture mode plus all builds, native acceptance, schema/identity checks, fmt, and clippy.
The mode plan fixes required checks at compile time. `NotApplicable` applies only to checks outside that mode.

The integrated policy exception is narrow and structural. It is not permission for renderer fallback or general CLI subprocess dispatch.
Replace the old blanket `p0_runtime_policy` test with the same policy evaluator's regression coverage.

Duplicate old substring assertions leave policies that conflict and repeat the case mismatch.

## Isolated execution and evidence

1. Reserve a new run directory atomically.
2. Before child processes start, write `started.json` with exclusive creation.
3. Make a snapshot of source and required documentation in `inputs/release-kit-studio/native-editor`.
4. Copy the parent package manifest for the checker's historical-package checks.
5. Copy only referenced current evidence necessary to resolve local document links.
6. Record that evidence as historical input.
7. Reject unsafe links without access to their targets.
8. Calculate hashes of all copied inputs.
9. After collection, compare the copied inputs with source bytes.
10. After the run, calculate hashes of the original owned inputs again.

Source changes make the original-tree claim incomplete even when snapshot acceptance passed. The immutable snapshot stays sufficient to reproduce the actual test inputs.

1. Use separate `cargo-default`, `cargo-hooks`, and `cargo-development` targets inside each run.
2. Set `NATIVE_EDITOR_EVIDENCE_DIR` separately for every acceptance configuration.
3. Before you construct argv, validate all operational paths as UTF-8.
4. Reject paths that argv cannot represent accurately.
5. Remove caller Cargo target, rustflags, wrapper, and hook variables.
6. Set approved overrides explicitly.
7. Reject repository Cargo configuration or environment wrappers that bypass the reviewed build plan.

Runs can share Cargo registry caches with read-only access. Runs never share generated targets and reports.

1. Run fmt.
2. Run the default build.
3. Run the hook build.
4. Run development acceptance.
5. Run default acceptance.
6. Run hook acceptance.
7. Run all related clippy configurations.
8. Use `--locked --offline` and explicit packages and features.
9. Use `-D warnings` on clippy.
10. Limit Cargo checks to their check deadlines.
11. Drain build stdout and stderr concurrently into separate files.
12. Replace any unbounded acceptance `wait_with_output` with a test-harness helper that enforces its own process-group deadline.

The outer Cargo deadline stays a separate limit.

1. Set child process groups.
2. On timeout, terminate the group.
3. Reap the child.
4. Close the pipes.
5. Record termination results.
6. If safe descendant termination is unavailable, mark full mode unsupported before you spawn builds.
7. If a stream exceeds its limit, terminate the group.
8. Record incomplete evidence for that stream.
9. Never stop the stream read while the child continues to write.
10. Before publication, audit all retained evidence files for existence, confined paths, byte counts, and hashes.
11. Accept only fresh discovery and acceptance evidence for this run.
12. Run the default binary last for tools, schema, and progress identity.
13. Keep default binary evidence distinct from hook binary evidence.

Historical document links cannot satisfy current checks. No check calls the historical Python renderer or FFmpeg.

1. Write `report.json.tmp` with exclusive creation.
2. Flush the file.
3. Publish `report.json` without replacement of an current file.

An interruption leaves `started.json`, completed check records, and child logs. It never creates a final successful receipt. A repeated command needs a new output path. Parallel runs have no shared writer for generated files.

Path errors before reservation return a structured CLI error. After reservation, failures become observations whenever publication stays possible.

## Meaningful negative fixtures

1. Use small isolated source and manifest fixture trees with the real policy evaluator.
2. Do not use assertions that reproduce the policy evaluator's implementation.
3. Supply fixtures for all the conditions in the list below.
4. Do a test of each fixture's exact violated rule and file location.
5. Include permitted current-source fixtures to find excessive bans.

The required fixtures cover these conditions:

- Nested core `Command`
- Imported aliases
- Mixed case banned literals
- CLI side-module spawn
- Cfg-disabled spawn
- Workspace `build.rs`
- Renamed forbidden dependency
- Optional dependency and target dependency
- Application-layer dependency
- External module path
- Unknown executable macro
- Symlink
- Forged verified capability
- Report path that escapes the run

1. Use actual fake child executables for missing tool, failed exit, output flood, hung descendant, and malformed checker JSON.
2. Do a test of two concurrent verification commands with different targets and output roots.
3. Assert that neither run's receipt or log changes the other run.
4. Do a test of an current output root.
5. Do a test of a partial abandoned run.
6. Assert that both stay byte-identical after rejection.
7. Keep native tests for independent pixel decode, altered artifact rejection, deadline recovery, and production hook immunity.
8. Do not replace runtime tests with manually written JSON success responses.

## Tradeoffs accepted

- We accept a cfg-gated development API inside editor-cli in exchange for one familiar executable and shared Registry knowledge.
- We accept an explicit process-policy exception in exchange for bounded Rust-owned development orchestration.
- We accept a bootstrap build before checks run again in exchange for no third executable or verification crate.
- We accept restrictive source and macro rules in exchange for enforceable ownership with the current small Rust source tree.
- We accept Node for the current documentation checks. This keeps their current coverage during this bounded update.
- We accept three isolated Cargo targets in exchange for unambiguous default, hook, and verifier build identities.

## Alternatives considered

A separate Rust development executable is the strongest alternative. It keeps subprocess dependencies completely outside the production CLI crate.
It loses shared private Registry access. It adds a new package, entry point, and boundary for schema tests.
Its interface depth is equally strong if it owns the full run. It wins when the verifier grows beyond this compact check plan.

Candidate A wins now because Cargo features structurally exclude its extra dependencies and early dispatch concentrates the user interface.
For future hosted checks or deployment orchestration, the recommendation is to repeat grounding. Extraction of the verifier is then probable.

A shell or Node task runner avoids the feature exception. But scripts must then coordinate target selection, log drain, identities, and receipts.
It has weaker interface depth and conflicts with Rust ownership of native verification orchestration.
Checks inside editor-core lose immediately. Process orchestration is outside the reusable library's ownership.

## Synthesis decision

Candidate A proposes the integrated CLI as the base. The parent arena must compare Candidate B and record the actual synthesis decision.
This sketch claims no independent review or runtime pass.

## Open questions and risks

- Does an optional development feature satisfy the user's expectation of one rerunnable verification CLI?
  The design defaults to yes. A default production build stays narrow.
- Which macro and dependency identities need explicit review before future native codec work?
  The current policy intentionally rejects unreviewed expansions.
- Is a later Rust port of documentation checkers preferable to the Node development prerequisite?
  This candidate keeps that separate from the bounded guardrail change.

## Implementation sequence

1. Add strict report types, exclusive run reservation, early check dispatch, and feature-gated modules.
2. Implement recursive inventory and real negative fixtures.
3. Replace the inadequate source-policy test.
4. Implement bounded group execution, isolated targets, snapshot identities, and failure publication tests.
5. Give document checkers exclusive explicit report paths.
6. Make sure that parallel outputs stay isolated.
7. Connect actual Cargo and current acceptance commands.
8. Examine new default and hook binary and schema identities.
9. Update ownership docs and exact rerun examples.
10. Independently review reports and current-build evidence.

Next implementation steps:

1. Create the feature-gated verification module.
2. Do a test to make sure that reservation of an current run preserves every byte.
