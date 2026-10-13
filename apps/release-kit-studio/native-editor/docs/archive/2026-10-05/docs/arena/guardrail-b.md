# Candidate B. Separate Rust development verifier

## Usage

The verifier is not part of the editor protocol.

1. Build the development verifier once.

```sh
cd apps/release-kit-studio/native-editor
cargo build --locked -p editor-devcheck --bin native-editor-check
```

2. Run architecture checks without a build or execution of the editor runtime.

```sh
./target/debug/native-editor-check architecture
```

3. Run the full current-build acceptance suite.

```sh
./target/debug/native-editor-check full
```

Both commands create a new directory under `.runs/verification/`. The command prints one JSON summary to stdout.

```json
{
  "runId": "20261004T214533.184Z-48172-0",
  "mode": "full",
  "verdict": "passed",
  "reportPath": ".runs/verification/20261004T214533.184Z-48172-0/report.json",
  "reportSha256": "6b9b..."
}
```

Progress goes to stderr. The complete report, command logs, checker receipts, runtime outputs, and test evidence stay in the run directory.

The interface has two modes.
It accepts no caller-supplied check list, expected verdict, receipt, timeout, project state, or output filename. `architecture` selects the fixed architecture plan. `full` selects that plan plus the fixed current-build acceptance plan.

Exit code `0` means each required check passed. Exit code `1` means at least one required check found a violation. Exit code `2` means no violation was conclusive, but at least one required check was incomplete. Usage errors use exit code `64`.

A typical full run has this shape.

```text
.runs/verification/<run-id>/
  report.json
  run.partial.json
  logs/<check-id>.stdout.log
  logs/<check-id>.stderr.log
  receipts/specification.json
  receipts/feature-coverage.json
  runtime/default/...
  tests/default/...
  tests/test-hooks/...
  targets/default/...
  targets/test-hooks/...
```

`report.json` is immutable. A retry creates a new run. Parallel runs never share a report directory, an editor state directory, or a Cargo target directory.

## Problem

The current policy check lives inside `editor-cli` acceptance tests. It scans only direct files under `editor-core/src` and only `editor-cli/src/main.rs`. It misses nested modules, new binaries, custom build scripts, and other production target paths. It converts source to lowercase before a search for the mixed-case string `Command::new(`. Thus, that search cannot match.

The two JavaScript document checkers write fixed receipt paths, which makes concurrent runs overwrite evidence. Default and `test-hooks` builds can also share one Cargo target and leave the hook-enabled binary at the expected default path. The check does not automatically bind saved evidence to current source, binary, protocol, schema, and capability identities.
Several tests use `wait_with_output`.
An inner blocked process can hang unless an outer owner enforces a deadline and drains both pipes.

The verifier must close those gaps. It must keep development orchestration outside `editor-core` and `editor-cli`. `editor-core` stays process-free. `editor-cli` stays the direct runtime interface. The verifier must not call the historical Python renderer, FFmpeg, libav, Resolve, or a future application adapter.

## Call sites

CI runs the fixed full plan and uploads one run directory.

```sh
set +e
./target/debug/native-editor-check full > native-editor-check-summary.json
status=$?
set -e
test "$status" -eq 0
```

A developer examines an ownership change before the runtime build.

```sh
./target/debug/native-editor-check architecture
jq '.checks[] | select(.outcome.kind != "passed")' \
  .runs/verification/<run-id>/report.json
```

A reviewer traces an executed command to its exact output.

```sh
jq '.checks[] | select(.id == "acceptance.default") | .processes' \
  .runs/verification/<run-id>/report.json
```

No Rust crate imports the verifier. It is a binary-only development tool.

## Report shape

The report models observed results. It cannot represent a caller assertion as a passed check.

```rust
#[derive(Clone, Copy, Serialize)]
#[serde(rename_all = "kebab-case")]
enum VerificationMode {
    Architecture,
    Full,
}

#[derive(Serialize)]
#[serde(rename_all = "kebab-case")]
enum RunVerdict {
    Passed,
    Failed,
    Incomplete,
    FailedAndIncomplete,
}

#[derive(Serialize)]
struct VerificationReport {
    report_version: u16,
    run_id: RunId,
    mode: VerificationMode,
    assurance_scope: AssuranceScope,
    started_at: Timestamp,
    finished_at: Timestamp,
    verdict: RunVerdict,
    workspace: WorkspaceIdentity,
    toolchain: ToolchainIdentity,
    verifier: BinaryIdentity,
    runtime: Option<RuntimeIdentities>,
    checks: Vec<CheckRecord>,
    artifacts: Vec<EvidenceFile>,
    capability_promotion_performed: bool,
}

#[derive(Serialize)]
#[serde(rename_all = "kebab-case")]
enum AssuranceScope {
    RepositoryStructureOnly,
    CurrentBuildP0Acceptance,
}

#[derive(Serialize)]
struct CheckRecord {
    id: CheckId,
    title: &'static str,
    outcome: CheckOutcome,
    processes: Vec<ProcessRecord>,
    evidence: Vec<EvidenceRef>,
}

#[derive(Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
enum CheckOutcome {
    Passed,
    Failed { violations: NonEmpty<Violation> },
    Incomplete { reason: IncompleteReason },
}

#[derive(Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
enum IncompleteReason {
    MissingTool { tool: String },
    UnsupportedPlatform { detail: String },
    TimedOut { deadline_ms: u64 },
    OutputLimitExceeded { stream: OutputStream, limit_bytes: u64 },
    MalformedOutput { detail: String },
    WorkspaceChanged { before_sha256: Sha256, after_sha256: Sha256 },
    IoFailure { operation: String, detail: String },
}

#[derive(Serialize)]
struct Violation {
    code: ViolationCode,
    path: Option<WorkspacePath>,
    line: Option<u32>,
    message: String,
}
```

`NonEmpty<T>` stores one required head and zero or more remaining values. A failed check therefore cannot omit its violation. The verifier derives `RunVerdict` only from required `CheckOutcome` values. No deserialized field can set either verdict.

Each external process has a complete observed record.

```rust
#[derive(Serialize)]
struct ProcessRecord {
    argv: Vec<String>,
    cwd: WorkspacePath,
    selected_environment: BTreeMap<String, String>,
    started_at: Timestamp,
    duration_ms: u64,
    exit: ProcessExit,
    stdout: CapturedStream,
    stderr: CapturedStream,
}

#[derive(Serialize)]
#[serde(tag = "kind", rename_all = "kebab-case")]
enum ProcessExit {
    Code { code: i32 },
    Signal { signal: i32 },
    TimedOut,
    SpawnFailed { error: String },
}

#[derive(Serialize)]
struct CapturedStream {
    path: EvidencePath,
    observed_bytes: u64,
    saved_bytes: u64,
    sha256: Sha256,
    truncated: bool,
}
```

The runner hashes all observed bytes while two reader threads drain stdout and stderr. It saves bytes only up to the configured limit. A truncated required command is incomplete, even when the process exits zero.

The identity section binds a report to the files and executables that the run observed.

```rust
#[derive(Serialize)]
struct WorkspaceIdentity {
    root: WorkspacePath,
    git_head: Option<String>,
    git_dirty: Option<bool>,
    source_manifest_sha256: Sha256,
    cargo_lock_sha256: Sha256,
    capabilities_sha256: Sha256,
    source_files: Vec<HashedFile>,
}

#[derive(Serialize)]
struct RuntimeIdentity {
    profile: RuntimeProfile,
    binary: BinaryIdentity,
    kernel_version: String,
    protocol_version: u8,
    identity_version: u8,
    schema_sha256: Sha256,
    implemented_feature_ids: BTreeSet<FeatureId>,
}

#[derive(Serialize)]
struct EvidenceFile {
    path: EvidencePath,
    bytes: u64,
    sha256: Sha256,
}
```

The report does not hash itself. The stdout summary hashes the final `report.json` bytes and supplies that binding without a circular field.

## Fixed check plans

`VerificationMode::plan()` returns a static list. The CLI does not accept include, exclude, allow-failure, expected-exit, or mark-passed flags.

```rust
impl VerificationMode {
    fn plan(self) -> &'static [CheckId];
}

enum CheckId {
    WorkspaceInventory,
    WorkspaceOwnership,
    RuntimeSourcePolicy,
    DependencyPolicy,
    SpecificationDocuments,
    FeatureDocumentCoverage,
    CapabilityState,
    GuardrailNegativeFixtures,
    Format,
    ClippyDefault,
    TestDefault,
    BuildDefault,
    RuntimeDefault,
    ClippyTestHooks,
    TestTestHooks,
    EvidenceAudit,
    WorkspaceStable,
}
```

The architecture plan ends at `GuardrailNegativeFixtures`. It reads source, manifests, schemas, ledgers, and documents. It does not build the editor or run a production command. Its report always says `repository-structure-only`.

The full plan includes each architecture check. Its next checks have this sequence:

1. The format check.
2. Default clippy and tests.
3. A fresh default build.
4. A default runtime probe.
5. Hook clippy and tests.
6. The evidence audit.
7. The final workspace stability check.

Its report says `current-build-p0-acceptance` only after those checks pass.

The default and hook commands use different run-owned targets.

```text
CARGO_TARGET_DIR=<run>/targets/default
CARGO_TARGET_DIR=<run>/targets/test-hooks
```

The verifier does not run a hook command against the default target. It builds the default binary after the default test suite and hashes that exact executable before the runtime probe. Hook evidence binds to the hook target's executable hash. A hook binary cannot masquerade as the accepted default binary.

The fixed process commands include these operations. Exact arguments live with their `CheckId` in Rust.

```text
cargo metadata --locked --format-version 1
node docs/check-spec.mjs --output <run>/receipts/specification.json
node docs/features/check.mjs --output <run>/receipts/feature-coverage.json
cargo fmt --all --check
cargo clippy --locked --workspace --all-targets -- -D warnings
cargo test --locked --workspace
cargo build --locked -p editor-cli --bin native-editor
<run>/targets/default/debug/native-editor tools
<run>/targets/default/debug/native-editor progress
<run>/targets/default/debug/native-editor demo <run>/runtime/default/demo
cargo clippy --locked -p editor-cli --all-targets --features test-hooks -- -D warnings
cargo test --locked -p editor-cli --features test-hooks
```

The JavaScript checkers must require `--output`. Each checker uses exclusive file creation and fails when the path exists. Neither checker writes `docs/spec-check.json` or `docs/features/coverage-check.json`. The verifier passes a distinct path inside its run directory. The current fixed-path receipts become historical artifacts and do not count as current evidence.

## Enforceable ownership policy

The workspace adds one member.

```toml
[workspace]
members = [
  "crates/editor-core",
  "crates/editor-cli",
  "crates/editor-devcheck",
]
```

The dependency direction is fixed.

```text
editor-cli ------> editor-core
editor-devcheck   no runtime-crate dependency
editor-core       no workspace dependency
```

`editor-devcheck` does not depend on `editor-core` or `editor-cli`. It observes their public process behavior and filesystem evidence. Thus, the verifier cannot prove a shared implementation through the same library calls.

`WorkspaceOwnership` parses Cargo metadata and the authored manifests. It rejects unknown workspace members until the compiled policy assigns a role. It rejects build dependencies and custom build targets for both runtime crates. It rejects a dependency edge from either runtime crate to the verifier. It rejects a dependency from `editor-core` to `editor-cli`.

Direct runtime dependencies use a reviewed allowlist. The resolved production closure rejects names that contain `ffmpeg`, `libav`, `python`, `node`, `bun`, `tauri`, `effect`, `cloudflare`, or known binding variants. The policy examines dependency aliases by resolved package name, not the local alias.

`RuntimeSourcePolicy` recursively visits each `.rs` file in each runtime crate's production source tree. The policy also scans Cargo target paths outside `src` . Test, bench, and example targets have separate policy and cannot become production targets unnoticed. Symlinks fail the check. Parse errors fail the check. The scanner rejects custom build scripts, `include!` source generation, unsafe code, prohibited renderer strings, and process APIs.

The scanner parses Rust with `syn`. It does not convert source to lowercase or search for one path syntax. It resolves `use` aliases within each file and examines Rust paths.

`editor-core` rejects each `std::process` path.
`editor-cli` permits only fully qualified `std::process::exit`. It rejects `Command`, `Child`, `Stdio`, process extension traits, shell execution, and process-module imports. This rule covers `src/main.rs`, `src/**/*.rs`, additional binary roots, and any Cargo target path.

`editor-devcheck` owns subprocess execution. Only `process.rs` can import `std::process`. The verifier's self-policy rejects `wait_with_output`, `Command::output`, and process imports in other verifier modules. All commands must pass through `ProcessRunner`.

These checks keep the current P0 acceptance tests unchanged.
The source policy moves out of `p0_runtime_policy`.
That test can assert the runtime-visible prohibition at a narrow level. Alternatively, that test can call no development process. The separate verifier owns repository-wide enforcement.

## Capability and state policy

The architecture checks parse `capabilities.json` into private input types. Validation then produces domain types. Unknown fields, duplicate feature IDs, cycles, invalid owner-layer pairs, invalid phase sequence, missing acceptance cases, and missing behavior contracts fail.

The current promotion policy is explicit.

```rust
enum PromotionPolicy {
    Unsupported,
}

fn check_capability_state(
    ledger: ParsedCapabilityLedger,
    policy: PromotionPolicy,
) -> Result<CapabilityLedger, NonEmpty<Violation>>;
```

With `PromotionPolicy::Unsupported`, an authored `verified` state or non-empty evidence list fails. The verifier does not edit `capabilities.json`, `docs/PROGRESS.md`, or any feature contract. A full passed report says that current-build acceptance passed. It does not promote a feature and does not use the word `verified` as a capability state.

During a full run, `RuntimeDefault` compares the exact default binary's `tools` and `progress` output with the parsed ledger. Compiled implemented IDs must map to authored `implemented` families. Each other family must stay `planned`. Runtime output must contain no verified family and no evidence supplied by the caller or a state directory.

## Fresh evidence audit

The verifier records a workspace inventory before the first check and after the last process. The inventory covers each regular file under `native-editor` except `.runs`, `target`, and `.git`.

The verifier rejects symlinks. It does not read their targets. A difference makes `WorkspaceStable` incomplete. This finds checkers that still write shared receipts. It also finds concurrent in-scope edits that make the run ambiguous.

`EvidenceAudit` accepts files only from the new run directory. It examines these bindings.

- Each checker receipt names the current capabilities and document hashes.
- Each default discovery file contains the exact SHA-256 of the run's default binary.
- Each hook discovery file contains the exact SHA-256 of the run's hook binary.
- Each discovery schema hash matches the applicable current binary response.
- Each required P0 case has fresh evidence under the correct suite directory.
- Each process JSON names an exit code and hashes its request, response, and stderr.
- The default runtime probe decodes the generated PNG independently and compares all pixels with the demo request.
- The stored artifact bytes, receipt hash, and fresh `artifact.verify` result agree.
- No evidence path escapes the run directory or crosses from the hook suite into the default suite.

The audit ignores prior `.runs` content. It does not use file modification times as proof. It binds evidence by content hashes and binary identities.

This before-and-after comparison does not freeze the operating system, Cargo cache, registry, or toolchain during a run. The report records tool versions and actual commands, but it does not authenticate those external systems.

## Bounded process ownership

`ProcessRunner` owns each external command.

```rust
struct ProcessRunner {
    limits: ProcessLimits,
}

struct ProcessLimits {
    deadline: Duration,
    terminate_grace: Duration,
    stdout_bytes: u64,
    stderr_bytes: u64,
}

impl ProcessRunner {
    fn run(
        &self,
        run: &RunDirectory,
        check: CheckId,
        command: CommandSpec,
    ) -> ProcessRecord;
}

struct CommandSpec {
    program: ToolName,
    args: Vec<String>,
    cwd: WorkspacePath,
    environment: BTreeMap<String, String>,
    deadline: Duration,
}
```

The verifier starts each child in a new process group on Unix and a Job Object on Windows. Two threads drain stdout and stderr immediately. The parent polls the child with nonblocking calls.

At the fixed deadline, the runner terminates the group.
It waits for the grace period before it kills remaining processes.
The runner then reaps the child and joins both drain threads. A missing platform implementation produces `UnsupportedPlatform`, not a pass.

The runner removes build-injection environment variables such as `RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS`, and Rust compiler wrappers. It records the selected environment that affects the build. Tool identity checks record `cargo --version`, `rustc -vV`, and `node --version`. Missing Cargo or Node makes the required check incomplete.

The verifier itself does not call `wait_with_output`. An inner acceptance test can block.
The outer deadline for the process group still ends the suite and records an incomplete outcome.

## Negative fixtures

Fixtures live under `crates/editor-devcheck/tests/fixtures/`. `architecture` runs them through the same analyzers used on the repository.

| Fixture | Required observation |
| --- | --- |
| `nested-core-process` | A nested module imports `std::process::Command as Runner`. Source policy reports a core process violation. |
| `new-cli-module-process` | A second CLI module invokes a child renderer. Source policy reports the file and line. |
| `custom-build-path` | A manifest names `tools/build-native.rs`, which launches `ffmpeg`. Ownership reports both the build target and renderer violation. |
| `aliased-ffmpeg-dependency` | A dependency key named `codec` resolves to package `ffmpeg-next`. Dependency policy reports the resolved package. |
| `forged-promotion` | A ledger claims `verified` with `passed: true`. Capability policy reports unsupported promotion. |
| `shared-receipt-output` | Two checker invocations target one file. The second exclusive create fails and cannot replace the first bytes. |
| `blocked-child-output` | A child fills both pipes and sleeps. The runner drains the logs. It kills the process group and reports timeout. |
| `parallel-runs` | Two verifier runs receive distinct run directories and distinct default and hook Cargo targets. |

The first four fixtures prevent the specific omissions in the current source policy. The promotion fixture proves that a caller-authored pass flag has no authority. The last three prove evidence isolation and bounded process behavior.

## Module map

```text
crates/editor-devcheck/
  Cargo.toml
  src/main.rs       CLI parse, one stdout summary, and ExitCode
  src/model.rs      report, verdict, identity, violation, and check types
  src/run.rs        fixed plans, unique run ownership, and final report commit
  src/process.rs    process groups, deadlines, stream drains, and command records
  src/policy.rs     Cargo ownership, Rust source policy, ledger, and document checks
  src/evidence.rs   file hashes, runtime probes, PNG inspection, and fresh-evidence audit
  tests/fixtures/   negative workspace and process fixtures
```

`main.rs` calls one deep interface.

```rust
fn main() -> ExitCode {
    let mode = Cli::parse(std::env::args_os())?;
    Verifier::open(compiled_workspace_root())?.run(mode).finish()
}

impl Verifier {
    fn open(root: WorkspaceRoot) -> Result<Self, StartupError>;
    fn run(self, mode: VerificationMode) -> CompletedRun;
}

impl CompletedRun {
    fn finish(self) -> ExitCode;
}
```

`run.rs` is the only coordinator. Policy checks call pure analyzers. Process execution stays in `process.rs`. The evidence parser stays in `evidence.rs`. No layer forwards the same argument list to another layer.

## Future automation, expressions, and Lua

`native-editor-check` is a development command. It is not an editor tool, protocol operation, or capability family. Agents continue to automate the runtime through `native-editor` and its six typed tools.

Planned animation expressions belong to a future Rust expression AST and evaluator inside the editor domain. They describe values over time. They do not execute workflow scripts or spawn processes.

An optional future Lua adapter belongs in a separate crate or application. The adapter can translate Lua calls into the same typed Rust API used by other callers. `editor-core` must not depend on a Lua runtime. Lua must not query SQLite, write artifacts, bypass limits, select fallbacks, or redefine expression semantics. This design adds no Lua dependency and no embedded interpreter.

## Shape rationale

The report types model the verification domain directly. `CheckOutcome` separates failure from incomplete execution. `RuntimeProfile` separates default and hook identities. This applies Model the Domain and Type System Discipline. Illegal states do not rely on synchronized booleans.

CLI arguments, JSON, Cargo metadata, JavaScript receipts, and runtime output are untrusted at their boundaries. The verifier parses them into private domain types once. Internal checks then trust those types. This applies Boundary Discipline.

Each run owns its evidence, targets, logs, test state, and report. Nothing requires a global lock or a `latest` pointer. This applies Separate Before Serializing Shared State and fixes the current receipt and target collisions.

The verifier is the tool that does and proves the work. You can run it again. It applies Build the Lever. The full plan exercises the actual binary, decodes actual output, and audits fresh identities. It applies Prove It Works.

The caller chooses only `architecture` or `full`. The fixed plan hides the command sequence, deadlines, output management, hash bindings, and verdict derivation. This applies Minimize Reader Load. A developer does not need to learn the verifier's implementation to use it safely.

The public interface is two modes and one JSON summary. The implementation can grow new internal checks without new CLI coordination flags. The module is deep because a small interface hides substantial policy and process control.

## Assurance boundary

This verifier enforces repository development rules. It is not a sandbox for hostile Rust, hostile proc macros, a compromised compiler, or arbitrary third-party build scripts. Dependency allowlists and locked metadata make changes reviewable. They do not prove that dependency code is harmless.

The report is content-addressed for review and reruns. It is not signed or authenticated against an attacker who controls the workspace or verifier binary. A later trusted promotion system needs a separate authority and threat model.

An architecture pass proves only current repository structure. A full pass adds actual P0 execution against the exact binaries named in the report. Neither pass proves movie, audio, text, layers, GPU, hosted deployment, playback, listening, or creative acceptance.

## Tradeoffs accepted

- We accept a third workspace crate to keep development process control outside both runtime crates.
- We accept Rust implementations for policy and evidence checks for typed outcomes and one authoritative report.
- We accept separate default and hook compilation costs for an unambiguous production binary identity.
- We accept fixed command deadlines and log limits for bounded, reproducible runs.
- We accept an explicit crate-role registry to make each new workspace ownership a reviewed decision.
- We accept no trusted feature promotion in this tool to avoid a partial receipt-authority design.

## Strongest competing alternative

The strongest alternative adds `native-editor verify-development architecture|full` to `editor-cli`. It reuses the current executable and avoids a third crate. It puts Cargo, Node, process groups, log capture, fixture workspaces, and repository policy in the runtime binary.
That binary also owns the argument parser and protocol framing.

If we select this alternative, the runtime binary needs development-only dependencies or feature gates. Its source policy examines the same executable that owns the policy.
The distributed runtime then has a wider command interface.

That alternative wins on workspace size. It loses on ownership and interface depth. If we select this alternative, each runtime consumer sees development verification concerns. Only repository developers need those concerns. The separate executable keeps `editor-cli` focused on direct editor execution and gives the verifier one coherent responsibility.

A shell or JavaScript orchestrator is another viable implementation shortcut. It makes process limits, typed incomplete states, Windows process ownership, and report schema easier to drift. It also repeats the shared-receipt problem that triggered this work. It is weaker than the separate Rust verifier.

## Open questions and risks

- Does the first implementation need full Windows support?
  Alternatively, can Windows full mode report `unsupported-platform` until Job Object control exists?
- Do we keep the current fixed-path document receipts as labeled historical snapshots?
  Alternatively, do we remove those receipts after links move to immutable run evidence?
- When test names cover more cases than the specification table, which P0 test-to-case mapping does the compiled acceptance registry need?
- What fixed deadline and stream limits fit the slowest supported development machine without a long wait for a real hang?

## Implementation sequence

1. Add the binary-only `editor-devcheck` crate with report types, two CLI modes, and exclusive run-directory creation.
2. Add `ProcessRunner` with process groups, concurrent stream drains, fixed limits, and timeout fixtures.
3. Add Cargo ownership and recursive Rust source policy. Prove the current omissions with negative fixtures.
4. Change both JavaScript checkers to require an exclusive run-owned output path. Remove fixed receipt writes.
5. Add ledger, document, and no-promotion checks. Wire the complete architecture plan.
6. Add isolated default and hook targets. Run current P0 tests unchanged before any test refactor.
7. Add the default runtime probe and fresh evidence audit. Bind source, lockfile, binaries, protocol, schema, ledger, receipts, and pixels.
8. Add parallel-run and workspace-stability tests. Run architecture and full modes twice to prove non-overwrite behavior.

## Synthesis decision

The parent owns arena synthesis.
This candidate recommends the separate verifier.
The verifier keeps the current runtime boundary and puts development process authority in one binary.
