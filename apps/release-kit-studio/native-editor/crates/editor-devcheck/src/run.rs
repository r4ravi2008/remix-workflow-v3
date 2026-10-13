#[path = "intent_scenarios.rs"]
mod scenarios;
use crate::{
    evidence, intent,
    model::*,
    policy,
    process::{self, CommandSpec, ProcessRunner},
};
use serde_json::{json, Value};
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

pub struct Verifier {
    root: PathBuf,
    directory: PathBuf,
    run_id: String,
    runner: ProcessRunner,
    sequence: u32,
}
pub struct CompletedRun {
    pub summary: Value,
    pub exit: u8,
}
impl Verifier {
    pub fn open(root: &Path) -> io::Result<Self> {
        let root = root.canonicalize()?;
        let base = root.join(".runs/verification");
        fs::create_dir_all(&base)?;
        let run_id = format!(
            "{}-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos(),
            process::pid()
        );
        let directory = base.join(&run_id);
        fs::create_dir(&directory)?;
        for path in [
            "logs",
            "receipts",
            "tests/default",
            "tests/test-hooks",
            "runtime/default",
            "runtime/test-hooks",
            "targets/default",
            "targets/test-hooks",
        ] {
            fs::create_dir_all(directory.join(path))?;
        }
        Ok(Self {
            root,
            directory,
            run_id,
            runner: ProcessRunner {
                whole_deadline: Instant::now() + Duration::from_secs(900),
            },
            sequence: 0,
        })
    }
    fn command(
        &mut self,
        record: &mut CheckRecord,
        program: &str,
        args: Vec<String>,
        profile: Option<RuntimeProfile>,
        deadline: u64,
    ) -> io::Result<Option<Value>> {
        let mut env = BTreeMap::new();
        env.insert("CARGO_NET_OFFLINE".into(), "true".into());
        env.insert("CARGO_INCREMENTAL".into(), "0".into());
        if let Some(profile) = profile {
            let name = match profile {
                RuntimeProfile::Default => "default",
                RuntimeProfile::TestHooks => "test-hooks",
            };
            env.insert(
                "CARGO_TARGET_DIR".into(),
                self.directory
                    .join("targets")
                    .join(name)
                    .display()
                    .to_string(),
            );
            env.insert(
                "NATIVE_EDITOR_EVIDENCE_DIR".into(),
                self.directory
                    .join("tests")
                    .join(name)
                    .display()
                    .to_string(),
            );
        }
        let name = format!("{:?}-{}", record.id, self.sequence);
        self.sequence += 1;
        let observed = self.runner.run(
            &self.directory.join("logs"),
            &name,
            CommandSpec {
                program: program.into(),
                args,
                cwd: self.root.clone(),
                environment: env,
                deadline: Duration::from_secs(deadline),
            },
        )?;
        let outcome = process::outcome(&observed);
        let result = if matches!(outcome, CheckOutcome::Passed) {
            serde_json::from_slice(&fs::read(&observed.stdout.path)?).ok()
        } else {
            None
        };
        if !matches!(outcome, CheckOutcome::Passed) {
            record.outcome = outcome;
        }
        let path = self
            .directory
            .join("logs")
            .join(format!("{name}.process.json"));
        evidence::write_new(&path, &observed)?;
        record.evidence.push(path.display().to_string());
        record.processes.push(observed);
        Ok(result)
    }
    fn cargo(
        &mut self,
        record: &mut CheckRecord,
        args: &[&str],
        profile: RuntimeProfile,
    ) -> io::Result<()> {
        let mut argv = vec!["--locked".into(), "--offline".into()];
        argv.extend(args.iter().map(|s| (*s).into()));
        self.command(record, "cargo", argv, Some(profile), 180)?;
        Ok(())
    }
    fn documents(
        &mut self,
        record: &mut CheckRecord,
        script: &str,
        filename: &str,
    ) -> io::Result<()> {
        let output = self.directory.join("receipts").join(filename);
        self.command(
            record,
            "node",
            vec![
                script.into(),
                "--output".into(),
                output.display().to_string(),
            ],
            None,
            30,
        )?;
        if matches!(record.outcome, CheckOutcome::Passed) {
            record.outcome = CheckOutcome::violations(evidence::receipt(&output, &self.root)?);
            record.evidence.push(output.display().to_string());
        }
        Ok(())
    }
    fn runtime(
        &mut self,
        record: &mut CheckRecord,
        profile: RuntimeProfile,
        identities: &mut Vec<RuntimeIdentity>,
        ledger: &Value,
    ) -> io::Result<()> {
        let name = match profile {
            RuntimeProfile::Default => "default",
            RuntimeProfile::TestHooks => "test-hooks",
        };
        let binary = evidence::file(
            &self
                .directory
                .join("targets")
                .join(name)
                .join("debug/native-editor"),
        )?;
        let value = self.command(
            record,
            &binary.path,
            vec!["tools".into()],
            Some(profile),
            30,
        )?;
        let Some(discovery) = value else {
            if matches!(record.outcome, CheckOutcome::Passed) {
                record.outcome = CheckOutcome::Incomplete {
                    reason: IncompleteReason::MalformedOutput {
                        detail: "Runtime discovery is not JSON".into(),
                    },
                }
            }
            return Ok(());
        };
        let mut violations = evidence::discovery(&discovery, &binary);
        evidence::write_new(
            &self
                .directory
                .join("runtime")
                .join(name)
                .join("discovery.json"),
            &discovery,
        )?;
        let mut schemas = vec![];
        for tool in [
            "artifact.verify",
            "engine.capabilities",
            "frame.render",
            "project.commit",
            "project.create",
            "project.inspect",
        ] {
            if let Some(schema) = self.command(
                record,
                &binary.path,
                vec!["schema".into(), tool.into()],
                Some(profile),
                30,
            )? {
                if schema["schemaSha256"] != discovery["schemaSha256"] || schema["tool"] != tool {
                    violations.push(Violation::new(
                        "runtime-schema",
                        None,
                        "Schema response differs from discovery",
                    ));
                }
                evidence::write_new(
                    &self
                        .directory
                        .join("runtime")
                        .join(name)
                        .join(format!("schema-{tool}.json")),
                    &schema,
                )?;
                schemas.push(json!({"name":tool,"inputSchema":schema["inputSchema"],"outputSchema":schema["outputSchema"]}));
            } else if matches!(record.outcome, CheckOutcome::Passed) {
                record.outcome = CheckOutcome::io("Missing current schema JSON");
            }
        }
        if evidence::sha(&evidence::canonical(
            &json!({"protocolVersion":1,"tools":schemas}),
        )) != discovery["schemaSha256"].as_str().unwrap_or("")
        {
            violations.push(Violation::new(
                "runtime-schema-hash",
                None,
                "Independent schema reconstruction differs",
            ));
        }
        if matches!(profile, RuntimeProfile::Default) {
            if let Some(progress) = self.command(
                record,
                &binary.path,
                vec!["progress".into()],
                Some(profile),
                30,
            )? {
                violations.extend(evidence::progress(&progress, ledger, &discovery));
                evidence::write_new(
                    &self.directory.join("runtime/default/progress.json"),
                    &progress,
                )?
            } else if matches!(record.outcome, CheckOutcome::Passed) {
                record.outcome = CheckOutcome::io("Missing progress JSON");
            }
            let demo_path = self.directory.join("runtime/default/demo");
            if let Some(demo) = self.command(
                record,
                &binary.path,
                vec!["demo".into(), demo_path.display().to_string()],
                Some(profile),
                30,
            )? {
                violations.extend(evidence::demo(&self.directory, &demo, &binary)?);
                evidence::write_new(
                    &self.directory.join("runtime/default/demo-response.json"),
                    &demo,
                )?;
                if let (Some(project), Some(artifact)) = (
                    demo["receipt"]["projectId"].as_str(),
                    demo["receipt"]["artifactId"].as_str(),
                ) {
                    if let Some(verified) = self.command(
                        record,
                        &binary.path,
                        vec![
                            "verify".into(),
                            project.into(),
                            artifact.into(),
                            "--state".into(),
                            demo_path.join("state").display().to_string(),
                        ],
                        Some(profile),
                        30,
                    )? {
                        if verified["result"]["measuredSha256"] != demo["receipt"]["sha256"]
                            || verified["result"]["verified"] != true
                            || verified["schemaSha256"] != discovery["schemaSha256"]
                        {
                            violations.push(Violation::new(
                                "fresh-artifact-verify",
                                None,
                                "Fresh artifact verification differs",
                            ));
                        }
                        evidence::write_new(
                            &self.directory.join("runtime/default/verify.json"),
                            &verified,
                        )?;
                    } else if matches!(record.outcome, CheckOutcome::Passed) {
                        record.outcome = CheckOutcome::io("Missing verification JSON");
                    }
                } else {
                    violations.push(Violation::new(
                        "demo-receipt-shape",
                        None,
                        "Demo receipt identifiers missing",
                    ));
                }
            } else if matches!(record.outcome, CheckOutcome::Passed) {
                record.outcome = CheckOutcome::io("Missing demo JSON");
            }
        }
        if !violations.is_empty() && matches!(record.outcome, CheckOutcome::Passed) {
            record.outcome = CheckOutcome::violations(violations);
        }
        identities.push(RuntimeIdentity {
            profile,
            binary,
            discovery,
        });
        Ok(())
    }
    pub fn run(mut self, mode: VerificationMode) -> io::Result<CompletedRun> {
        let started_at = process::now();
        let (source, source_error) = match evidence::source_identity(&self.root) {
            Ok(source) => (source, None),
            Err(error) => (
                SourceIdentity {
                    scope: "Source inventory unavailable; no snapshot claim".into(),
                    files: vec![],
                    sha256: evidence::sha(b"unavailable"),
                },
                Some(error.to_string()),
            ),
        };
        let verifier = evidence::file(&std::env::current_exe()?)?;
        let (ledger, ledger_error) = match evidence::json(&self.root.join("capabilities.json")) {
            Ok(value) => (value, None),
            Err(error) => (Value::Null, Some(error.to_string())),
        };
        let mut contracts = None;
        let mut intent_rows = vec![];
        let mut intent_issues = vec![];
        let mut intent_path = None;
        let contract_file =
            evidence::file(&self.root.join("docs/features/intent-contracts.json")).ok();
        let mut checks: Vec<CheckRecord> = vec![];
        let mut runtime = vec![];
        let mut artifacts = vec![];
        let mut path_fixtures = vec![];
        evidence::write_new(&self.directory.join("source-before.json"), &source)?;
        for id in mode.plan() {
            eprintln!("Running {id:?}. Evidence {}", self.directory.display());
            let mut record = CheckRecord {
                id: *id,
                outcome: CheckOutcome::Passed,
                processes: vec![],
                evidence: vec![],
            };
            let result = (|| -> io::Result<()> {
                if Instant::now() >= self.runner.whole_deadline {
                    record.outcome = CheckOutcome::Incomplete {
                        reason: IncompleteReason::TimedOut {
                            deadline_ms: 900_000,
                        },
                    };
                    return Ok(());
                }
                use CheckId::*;
                match id {
                    WorkspaceInventory => {
                        if let Some(error) = &source_error {
                            record.outcome = CheckOutcome::io(error);
                        }
                    }
                    WorkspaceOwnership => {
                        record.outcome = CheckOutcome::violations(policy::ownership(&self.root))
                    }
                    RuntimeSourcePolicy => {
                        record.outcome =
                            CheckOutcome::violations(policy::runtime_sources(&self.root))
                    }
                    DependencyPolicy => {
                        let metadata = self.command(
                            &mut record,
                            "cargo",
                            vec![
                                "--locked".into(),
                                "--offline".into(),
                                "metadata".into(),
                                "--format-version".into(),
                                "1".into(),
                            ],
                            None,
                            30,
                        )?;
                        if let Some(value) = &metadata {
                            if matches!(record.outcome, CheckOutcome::Passed) {
                                record.outcome =
                                    CheckOutcome::violations(policy::dependencies(value));
                            }
                        } else if matches!(record.outcome, CheckOutcome::Passed) {
                            record.outcome = CheckOutcome::io("Cargo metadata was not JSON");
                        }
                    }
                    CapabilityState => {
                        record.outcome = if let Some(error) = &ledger_error {
                            CheckOutcome::violations(vec![Violation::new(
                                "ledger-parse",
                                Some("capabilities.json".into()),
                                error,
                            )])
                        } else {
                            CheckOutcome::violations(policy::ledger(&ledger, &self.root))
                        };
                    }
                    GuardrailNegativeFixtures => {
                        record.outcome =
                            CheckOutcome::violations(policy::negative_fixtures(&self.root))
                    }
                    SpecificationDocuments => {
                        self.documents(&mut record, "docs/check-spec.mjs", "specification.json")?
                    }
                    FeatureDocumentCoverage => self.documents(
                        &mut record,
                        "docs/features/check.mjs",
                        "feature-coverage.json",
                    )?,
                    IntentContracts => match intent::load(&self.root, &ledger) {
                        Ok((value, rows)) => {
                            contracts = Some(value);
                            intent_rows = rows;
                        }
                        Err(error) => {
                            intent_issues.push(error.to_string());
                            intent_rows =
                                intent::documents(&self.root, &ledger, None).unwrap_or_default();
                            record.outcome = CheckOutcome::violations(vec![Violation::new(
                                "intent-contract",
                                None,
                                error.to_string(),
                            )]);
                        }
                    },
                    IntentScenarios => {
                        if let (Some(contracts), Some(file)) = (&contracts, &contract_file) {
                            self.run_intent_scenarios(
                                &mut record,
                                contracts,
                                &mut intent_rows,
                                &runtime,
                                &source,
                                file,
                            )?;
                        } else {
                            record.outcome =
                                CheckOutcome::io("Current intent contracts unavailable");
                        }
                    }
                    Toolchain => {
                        for (program, args) in [
                            ("cargo", vec!["--version"]),
                            ("rustc", vec!["-vV"]),
                            ("node", vec!["--version"]),
                        ] {
                            self.command(
                                &mut record,
                                program,
                                args.into_iter().map(String::from).collect(),
                                None,
                                15,
                            )?;
                        }
                    }
                    Format => self.cargo(
                        &mut record,
                        &["fmt", "--all", "--check"],
                        RuntimeProfile::Default,
                    )?,
                    ClippyDefault => self.cargo(
                        &mut record,
                        &[
                            "clippy",
                            "--workspace",
                            "--all-targets",
                            "--",
                            "-D",
                            "warnings",
                        ],
                        RuntimeProfile::Default,
                    )?,
                    TestDefault => self.cargo(
                        &mut record,
                        &["test", "--workspace"],
                        RuntimeProfile::Default,
                    )?,
                    BuildDefault => self.cargo(
                        &mut record,
                        &["build", "--workspace", "--all-targets"],
                        RuntimeProfile::Default,
                    )?,
                    RuntimeDefault => {
                        self.runtime(&mut record, RuntimeProfile::Default, &mut runtime, &ledger)?
                    }
                    ClippyTestHooks => self.cargo(
                        &mut record,
                        &[
                            "clippy",
                            "-p",
                            "editor-cli",
                            "--all-targets",
                            "--features",
                            "test-hooks",
                            "--",
                            "-D",
                            "warnings",
                        ],
                        RuntimeProfile::TestHooks,
                    )?,
                    TestTestHooks => self.cargo(
                        &mut record,
                        &["test", "-p", "editor-cli", "--features", "test-hooks"],
                        RuntimeProfile::TestHooks,
                    )?,
                    BuildTestHooks => {
                        self.cargo(
                            &mut record,
                            &[
                                "build",
                                "-p",
                                "editor-cli",
                                "--bin",
                                "native-editor",
                                "--features",
                                "test-hooks",
                            ],
                            RuntimeProfile::TestHooks,
                        )?;
                        if matches!(record.outcome, CheckOutcome::Passed) {
                            self.runtime(
                                &mut record,
                                RuntimeProfile::TestHooks,
                                &mut runtime,
                                &ledger,
                            )?
                        }
                    }
                    EvidenceAudit => {
                        let mut v = vec![];
                        let features = ledger["capabilities"]
                            .as_array()
                            .ok_or_else(|| io::Error::other("Ledger families are malformed"))?;
                        let mut all = BTreeSet::new();
                        for feature in features.iter().filter(|f| f["phase"] == "P0") {
                            let cases = feature["acceptanceCaseIds"]
                                .as_array()
                                .ok_or_else(|| io::Error::other("P0 cases are malformed"))?;
                            for case in cases {
                                all.insert(
                                    case.as_str()
                                        .ok_or_else(|| io::Error::other("P0 case is not a string"))?
                                        .to_string(),
                                );
                            }
                        }
                        if runtime.len() != 2 {
                            v.push(Violation::new(
                                "runtime-identities",
                                None,
                                "Both fresh runtime profiles are required",
                            ));
                        }
                        for identity in &runtime {
                            let name = match identity.profile {
                                RuntimeProfile::Default => "default",
                                RuntimeProfile::TestHooks => "test-hooks",
                            };
                            let required = if name == "default" {
                                all.iter()
                                    .filter(|s| {
                                        !["P0-CRASH-RECOVERY", "P0-CANCELLATION"]
                                            .contains(&s.as_str())
                                    })
                                    .cloned()
                                    .collect()
                            } else {
                                all.clone()
                            };
                            v.extend(evidence::suite(
                                &self.directory.join("tests").join(name),
                                &identity.binary,
                                identity.discovery["schemaSha256"].as_str().unwrap_or(""),
                                &required,
                            )?);
                        }
                        for check in &checks {
                            for p in &check.processes {
                                for stream in [&p.stdout, &p.stderr] {
                                    if !stream.truncated
                                        && evidence::file(Path::new(&stream.path))?.sha256
                                            != stream.sha256
                                    {
                                        v.push(Violation::new(
                                            "process-log-hash",
                                            Some(stream.path.clone()),
                                            "Process log changed",
                                        ));
                                    }
                                }
                            }
                        }
                        record.outcome = CheckOutcome::violations(v);
                    }
                    EvidenceInventory => {
                        if let Some(file) = &contract_file {
                            for row in intent_rows
                                .iter_mut()
                                .filter(|r| r.ledger_state == "implemented")
                            {
                                for case in &mut row.cases {
                                    intent::audit_case(
                                        case,
                                        &self.directory,
                                        &self.run_id,
                                        &source,
                                        file,
                                        &runtime,
                                        &row.section_sha256,
                                    );
                                }
                                if matches!(mode, VerificationMode::Full) {
                                    row.status = intent::aggregate(&row.cases);
                                }
                            }
                        }
                        let coverage = intent::report(
                            &self.run_id,
                            mode,
                            &source,
                            contract_file.as_ref().map(|f| HashedFile {
                                path: f.path.clone(),
                                bytes: f.bytes,
                                sha256: f.sha256.clone(),
                            }),
                            std::mem::take(&mut intent_rows),
                            std::mem::take(&mut intent_issues),
                        );
                        if matches!(mode, VerificationMode::Full)
                            && coverage.verdict != "passed-implemented-scope"
                            && !checks.iter().any(|c| {
                                c.id == CheckId::IntentScenarios
                                    && !matches!(c.outcome, CheckOutcome::Passed)
                            })
                        {
                            record.outcome = CheckOutcome::io(
                                "Intent evidence missing, stale, or incomplete at final inventory",
                            );
                        }
                        let path = self.directory.join("intent-coverage.json");
                        evidence::write_new(&path, &coverage)?;
                        record.evidence.push(path.display().to_string());
                        intent_path = Some((path, coverage.counts));
                        (artifacts, path_fixtures) = evidence::artifact_inventory(&self.directory)?;
                    }
                    WorkspaceStable => {
                        let after = evidence::source_identity(&self.root)?;
                        evidence::write_new(&self.directory.join("source-after.json"), &after)?;
                        if after != source {
                            intent_issues
                                .push("Source inventory changed during verification".into());
                            record.outcome = CheckOutcome::Incomplete {
                                reason: IncompleteReason::WorkspaceChanged {
                                    before_sha256: source.sha256.clone(),
                                    after_sha256: after.sha256,
                                },
                            }
                        }
                    }
                }
                Ok(())
            })();
            if let Err(error) = result {
                record.outcome = CheckOutcome::io(error);
            }
            checks.push(record);
            let partial = self.directory.join("run.partial.json");
            fs::write(
                &partial,
                serde_json::to_vec_pretty(
                    &json!({"runId":self.run_id,"mode":mode,"checks":checks,"verdict":RunVerdict::derive(mode,&checks)}),
                )?,
            )?;
        }

        let verdict = RunVerdict::derive(mode, &checks);
        let exit = verdict.exit_code();
        let assurance = if matches!(mode, VerificationMode::Full) && exit == 0 {
            "current-build-p0-acceptance"
        } else {
            "repository-structure-only; see individual failed or incomplete requirements"
        };
        let report = VerificationReport {
            report_version: 1,
            run_id: self.run_id.clone(),
            mode,
            assurance_scope: assurance.into(),
            started_at,
            finished_at: process::now(),
            verdict,
            source,
            verifier,
            runtime,
            checks,
            artifacts,
            path_fixtures,
            intent_coverage: intent_path
                .as_ref()
                .map(|(path, _)| evidence::file(path))
                .transpose()?,
            capability_promotion_performed: false,
        };
        let path = self.directory.join("report.json");
        evidence::write_new(&path, &report)?;
        Ok(CompletedRun {
            summary: json!({"runId":self.run_id,"mode":mode,"verdict":report.verdict,"reportPath":path,"reportSha256":evidence::file(&path)?.sha256,"intentCoveragePath":intent_path.as_ref().map(|(p,_)|p),"intentSummary":intent_path.as_ref().map(|(_,c)|c)}),
            exit,
        })
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn unique_runs_and_targets() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .parent()
            .unwrap();
        let a = Verifier::open(root).unwrap();
        let b = Verifier::open(root).unwrap();
        assert_ne!(a.directory, b.directory);
        assert_ne!(
            a.directory.join("targets/default"),
            a.directory.join("targets/test-hooks")
        );
    }
    #[test]
    fn stable_source_identity() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .parent()
            .unwrap();
        assert_eq!(
            evidence::source_identity(root).unwrap(),
            evidence::source_identity(root).unwrap()
        );
    }
}
