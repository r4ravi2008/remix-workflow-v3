use super::*;
use crate::intent::{self, Fixture, IntentContracts, State};
use crate::process::ProcessInput;
use std::io::Write;

struct CliObservation {
    value: Value,
    code: Option<i32>,
    duration_ms: u128,
    empty_stderr: bool,
    response_bytes: u64,
}
struct Scenario<'a> {
    verifier: &'a mut Verifier,
    record: &'a mut CheckRecord,
    runtime: &'a RuntimeIdentity,
    directory: PathBuf,
    state: PathBuf,
    evidence: Vec<HashedFile>,
}
impl Scenario<'_> {
    fn invoke(
        &mut self,
        args: Vec<String>,
        input: ProcessInput,
        reader_delay: Duration,
        env: BTreeMap<String, String>,
    ) -> io::Result<CliObservation> {
        let n = self.verifier.sequence;
        self.verifier.sequence += 1;
        let name = format!("process-{n}");
        let is_call = args.first().is_some_and(|a| a == "call");
        let p = self.verifier.runner.run_controlled(
            &self.directory,
            &name,
            CommandSpec {
                program: self.runtime.binary.path.clone(),
                args,
                cwd: self.verifier.root.clone(),
                environment: env,
                deadline: Duration::from_secs(10),
            },
            input,
            reader_delay,
        )?;
        let value = serde_json::from_slice(&fs::read(&p.stdout.path)?).unwrap_or(Value::Null);
        let observation = CliObservation {
            value,
            code: match p.exit {
                ProcessExit::Code { code } => Some(code),
                _ => None,
            },
            duration_ms: p.duration_ms,
            empty_stderr: p.stderr.observed_bytes == 0,
            response_bytes: p.stdout.observed_bytes,
        };
        let path = self.directory.join(format!("{name}.json"));
        evidence::write_new(&path, &p)?;
        self.evidence.push(evidence::file(&path)?);
        self.evidence
            .push(evidence::file(Path::new(&p.stdout.path))?);
        self.evidence
            .push(evidence::file(Path::new(&p.stderr.path))?);
        self.record.evidence.push(path.display().to_string());
        self.record.processes.push(p);
        if is_call
            && (observation.value["protocolVersion"] != 1
                || observation.value["schemaSha256"] != self.runtime.discovery["schemaSha256"]
                || self.record.processes.last().unwrap().stdout.truncated
                || self.record.processes.last().unwrap().stderr.truncated
                || !observation.empty_stderr)
        {
            return Err(io::Error::other(
                "Incomplete, malformed, or mismatched current CLI response",
            ));
        }
        Ok(observation)
    }
    fn command(&mut self, args: Vec<String>) -> io::Result<CliObservation> {
        self.invoke(args, ProcessInput::Empty, Duration::ZERO, BTreeMap::new())
    }
    fn raw(
        &mut self,
        bytes: Vec<u8>,
        env: BTreeMap<String, String>,
        deadline: u64,
        delay: Duration,
    ) -> io::Result<CliObservation> {
        let path = self
            .directory
            .join(format!("request-{}.json", self.verifier.sequence));
        fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)?
            .write_all(&bytes)?;
        self.evidence.push(evidence::file(&path)?);
        self.invoke(
            vec![
                "call".into(),
                "--deadline-ms".into(),
                deadline.to_string(),
                "--state".into(),
                self.state.display().to_string(),
            ],
            ProcessInput::Bytes(bytes),
            delay,
            env,
        )
    }
    fn envelope(&self, tool: &str, input: Value) -> Value {
        json!({"protocolVersion":1,"requestId":"intent-scenario-request","expectedSchemaSha256":if tool=="engine.capabilities"{Value::Null}else{self.runtime.discovery["schemaSha256"].clone()},"tool":tool,"input":input})
    }
    fn call(&mut self, tool: &str, input: Value) -> io::Result<CliObservation> {
        self.raw(
            serde_json::to_vec(&self.envelope(tool, input))?,
            BTreeMap::new(),
            30000,
            Duration::ZERO,
        )
    }
    fn inspect(&mut self, revision: Option<u64>) -> io::Result<Value> {
        let mut input = json!({"projectId":"project"});
        if let Some(r) = revision {
            input["revision"] = r.into();
        }
        Ok(self.call("project.inspect", input)?.value["result"].clone())
    }
    fn capture(&mut self, name: &str, bytes: &[u8]) -> io::Result<()> {
        let id = self.verifier.sequence;
        self.verifier.sequence += 1;
        let original = Path::new(name);
        let stem = original
            .file_stem()
            .and_then(|s| s.to_str())
            .ok_or_else(|| io::Error::other("Missing capture name"))?;
        let extension = original
            .extension()
            .and_then(|s| s.to_str())
            .unwrap_or("bin");
        let p = self.directory.join(format!("{stem}-{id}.{extension}"));
        let mut file = fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&p)?;
        file.write_all(bytes)?;
        file.sync_all()?;
        self.evidence.push(evidence::file(&p)?);
        Ok(())
    }
    fn pixels(&mut self, response: &Value, rgba: [u8; 4], f: &Fixture) -> io::Result<Value> {
        let receipt = &response["result"];
        let relative = receipt["path"]
            .as_str()
            .ok_or_else(|| io::Error::other("Missing receipt path"))?;
        if Path::new(relative).is_absolute()
            || Path::new(relative)
                .components()
                .any(|c| !matches!(c, std::path::Component::Normal(_)))
        {
            return Err(io::Error::other("Unsafe runtime artifact path"));
        }
        let path = self.state.join("project").join(relative);
        let bytes = fs::read(&path)?;
        let copy = format!("artifact-{}.png", self.verifier.sequence);
        self.capture(&copy, &bytes)?;
        let (w, h, pixels) = evidence::png_pixels(&path)?;
        let mismatches = pixels
            .chunks_exact(4)
            .enumerate()
            .filter(|(_, pixel)| *pixel != rgba)
            .collect::<Vec<_>>();
        let first_mismatch=mismatches.first().map(|(index,pixel)|json!({"position":[index % w as usize,index / w as usize],"rgba":pixel}));
        let value = json!({"width":w,"height":h,"expectedRgba":rgba,"firstPixel":pixels.get(..4),"mismatchCount":mismatches.len(),"firstMismatch":first_mismatch,"allPixelsMatch":pixels==rgba.repeat((f.width*f.height)as usize),"decodedChannels":pixels.len()});
        self.capture(
            &format!("pixels-{}.json", self.verifier.sequence),
            &serde_json::to_vec_pretty(&value)?,
        )?;
        Ok(value)
    }

    fn finish(
        &mut self,
        rows: &mut [intent::FeatureResult],
        id: &str,
        actual: Value,
        source: &SourceIdentity,
        contracts: &HashedFile,
    ) -> io::Result<()> {
        let feature = rows
            .iter_mut()
            .find(|f| id.starts_with(&format!("{}-", f.feature_id)))
            .ok_or_else(|| io::Error::other("Missing feature row"))?;
        let case = feature
            .cases
            .iter_mut()
            .find(|c| c.case_id == id)
            .ok_or_else(|| io::Error::other("Missing case row"))?;
        case.evidence = self
            .evidence
            .iter()
            .map(|f| HashedFile {
                path: f.path.clone(),
                bytes: f.bytes,
                sha256: f.sha256.clone(),
            })
            .collect();
        case.binding = json!({"runId":self.verifier.run_id,"sourceSha256":source.sha256,"contractSha256":contracts.sha256,"featureSectionSha256":feature.section_sha256,"profile":self.runtime.profile,"binarySha256":self.runtime.binary.sha256,"schemaSha256":self.runtime.discovery["schemaSha256"]});
        intent::compare(case, actual);
        let p = self.directory.join(format!("{id}-observation.json"));
        evidence::write_new(&p, case)?;
        case.evidence.push(evidence::file(&p)?);
        Ok(())
    }
}
fn create(f: &Fixture) -> Value {
    json!({"projectId":"project","intentId":"create","name":"Creator background","timeline":{"frameRate":{"numerator":f.frame_rate,"denominator":1},"durationFrames":f.duration_frames,"canvas":{"width":f.width,"height":f.height}}})
}
fn put(id: &str, start: u64, duration: u64, rgba: [u8; 4]) -> Value {
    json!({"kind":"clip.put","clip":{"id":id,"startFrame":start,"durationFrames":duration,"source":{"kind":"solid","rgba":rgba}}})
}
fn commit(intent: &str, revision: u64, edits: Vec<Value>) -> Value {
    json!({"projectId":"project","intentId":intent,"expectedRevision":revision,"edits":edits})
}
fn render(intent: &str, revision: u64, frame: u64) -> Value {
    json!({"projectId":"project","intentId":intent,"revision":revision,"frame":frame,"format":"png-rgba8"})
}
fn snapshot_hash(result: &Value) -> bool {
    result["projectSha256"] == evidence::sha(&evidence::canonical(&result["snapshot"]))
}
impl Verifier {
    pub(super) fn run_intent_scenarios(
        &mut self,
        record: &mut CheckRecord,
        contracts: &IntentContracts,
        rows: &mut [intent::FeatureResult],
        runtime: &[RuntimeIdentity],
        source: &SourceIdentity,
        contract_file: &HashedFile,
    ) -> io::Result<()> {
        for row in rows.iter_mut().filter(|r| r.ledger_state == "implemented") {
            row.status = State::Incomplete;
            for case in &mut row.cases {
                case.status = State::Incomplete;
                case.incomplete_reason =
                    Some("Current-run public CLI scenario not completed".into());
            }
        }
        let result = (|| -> io::Result<()> {
            let f = &contracts.fixture;
            let default = runtime
                .iter()
                .find(|r| r.profile == RuntimeProfile::Default)
                .ok_or_else(|| io::Error::other("Fresh default binary missing"))?;
            let directory = self.directory.join("intent/default");
            fs::create_dir_all(&directory)?;
            let state = directory.join("state");
            let mut s = Scenario {
                verifier: self,
                record,
                runtime: default,
                directory,
                state,
                evidence: vec![],
            };
            let discovery = s.command(vec![
                "tools".into(),
                "--state".into(),
                s.state.display().to_string(),
            ])?;
            let unknown = s.call("imaginary.tool", json!({}))?;
            let future = s.call("MEDIA-01", json!({}))?;
            let names = discovery.value["tools"]
                .as_array()
                .map(|a| a.iter().map(|t| t["name"].clone()).collect::<Vec<_>>());
            s.finish(rows,"CORE-01-A",json!({"toolNames":names,"implementedFeatureIds":discovery.value["implementedFeatureIds"],"binaryMatches":discovery.value["binarySha256"]==evidence::file(Path::new(&default.binary.path))?.sha256,"noState":!s.state.exists(),"unknownExit":unknown.code,"unknownError":unknown.value["error"]["code"],"futureExit":future.code,"futureError":future.value["error"]["code"]}),source,contract_file)?;
            let mut schemas = vec![];
            let mut schema_identity = true;
            for tool in [
                "artifact.verify",
                "engine.capabilities",
                "frame.render",
                "project.commit",
                "project.create",
                "project.inspect",
            ] {
                let schema = s.command(vec!["schema".into(), tool.into()])?;
                schema_identity &= schema.code == Some(0)
                    && schema.value["schemaSha256"] == default.discovery["schemaSha256"];
                schemas.push(json!({"name":tool,"inputSchema":schema.value["inputSchema"],"outputSchema":schema.value["outputSchema"]}));
            }
            let mut invalid = create(f);
            invalid["unknown"] = true.into();
            let invalid = s.call("project.create", invalid)?;
            s.finish(rows,"CORE-01-B",json!({"schemaIdentity":schema_identity,"schemaHashMatches":evidence::sha(&evidence::canonical(&json!({"protocolVersion":1,"tools":schemas})))==default.discovery["schemaSha256"],"unknownFieldExit":invalid.code,"unknownFieldError":invalid.value["error"]["code"],"noState":!s.state.exists()}),source,contract_file)?;
            let created = s.call("project.create", create(f))?;
            let first_request = commit(
                "background-v1",
                0,
                vec![put("background", 0, 96, f.background)],
            );
            let first = s.call("project.commit", first_request.clone())?;
            let revision0 = s.inspect(Some(0))?;
            let revision1 = s.inspect(Some(1))?;
            let background = s.call("frame.render", render("background-frame", 1, 0))?;
            let background_pixels = s.pixels(&background.value, f.background, f)?;
            let second = s.call(
                "project.commit",
                commit(
                    "two-backgrounds",
                    1,
                    vec![
                        json!({"kind":"clip.remove","clipId":"background"}),
                        put("blue", 0, 48, f.blue),
                        put("gold", 48, 48, f.gold),
                    ],
                ),
            )?;
            let latest = s.inspect(None)?;
            let old0 = s.inspect(Some(0))?;
            let old1 = s.inspect(Some(1))?;
            let timeline = json!({"frameRate":{"numerator":24,"denominator":1},"durationFrames":96,"canvas":{"width":64,"height":64}});
            let expected0 = json!({"snapshotVersion":1,"projectId":"project","name":"Creator background","revision":0,"timeline":timeline,"clips":[]});
            let expected1 = json!({"snapshotVersion":1,"projectId":"project","name":"Creator background","revision":1,"timeline":timeline,"clips":[put("background",0,96,f.background)["clip"]]});
            s.finish(rows,"CORE-02-A",json!({"createExit":created.code,"firstCommitExit":first.code,"secondCommitExit":second.code,"revision0Exact":revision0["snapshot"]==expected0,"revision1Exact":revision1["snapshot"]==expected1,"independentHashes":snapshot_hash(&revision0)&&snapshot_hash(&revision1)&&snapshot_hash(&latest),"historicalAfterNewRevision":old0==revision0&&old1==revision1,"latestRevision":latest["snapshot"]["revision"]}),source,contract_file)?;
            let replay = s.call("project.commit", first_request.clone())?;
            let replay_latest = s.inspect(None)?;
            s.finish(rows,"CORE-03-A",json!({"exit":replay.code,"originalResult":replay.value["result"]==first.value["result"],"returnedRevision":replay.value["result"]["revision"],"replayed":replay.value["replayed"],"latestRevision":replay_latest["snapshot"]["revision"],"latestUnchanged":replay_latest==latest,"independentHash":snapshot_hash(&replay_latest)}),source,contract_file)?;
            let before = s.inspect(None)?;
            let conflict = s.call(
                "project.commit",
                commit("background-v1", 0, vec![put("background", 0, 96, f.gold)]),
            )?;
            let after = s.inspect(None)?;
            s.finish(rows,"CORE-03-B",json!({"exit":conflict.code,"error":conflict.value["error"]["code"],"beforeAfterEqual":before==after,"independentHashes":snapshot_hash(&before)&&snapshot_hash(&after)}),source,contract_file)?;
            let blue = s.call("frame.render", render("blue-frame", 2, 47))?;
            let blue_pixels = s.pixels(&blue.value, f.blue, f)?;
            let gold = s.call("frame.render", render("gold-frame", 2, 48))?;
            let gold_pixels = s.pixels(&gold.value, f.gold, f)?;
            s.finish(rows,"CORE-04-A",json!({"exactClips":latest["snapshot"]["clips"]==json!([put("blue",0,48,f.blue)["clip"],put("gold",48,48,f.gold)["clip"]]),"frame47":blue_pixels,"frame48":gold_pixels,"frame47Binding":blue.value["result"]["frame"]==47&&blue.value["result"]["revision"]==2,"frame48Binding":gold.value["result"]["frame"]==48&&gold.value["result"]["revision"]==2}),source,contract_file)?;
            let before = s.inspect(None)?;
            let rollback = s.call(
                "project.commit",
                commit(
                    "rollback",
                    2,
                    vec![
                        put("blue", 0, 48, f.background),
                        json!({"kind":"clip.remove","clipId":"missing"}),
                    ],
                ),
            )?;
            let after = s.inspect(None)?;
            s.finish(rows,"CORE-04-B",json!({"exit":rollback.code,"error":rollback.value["error"]["code"],"beforeAfterEqual":before==after,"independentHashes":snapshot_hash(&before)&&snapshot_hash(&after)}),source,contract_file)?;
            let alpha_commit = s.call(
                "project.commit",
                commit(
                    "alpha",
                    2,
                    vec![
                        json!({"kind":"clip.remove","clipId":"blue"}),
                        json!({"kind":"clip.remove","clipId":"gold"}),
                        put("alpha", 0, 48, f.alpha),
                    ],
                ),
            )?;
            let alpha = s.call("frame.render", render("alpha-frame", 3, 47))?;
            let alpha_pixels = s.pixels(&alpha.value, f.alpha, f)?;
            let transparent = s.call("frame.render", render("transparent-frame", 3, 48))?;
            let transparent_pixels = s.pixels(&transparent.value, [0, 0, 0, 0], f)?;
            s.finish(rows,"CORE-05-A",json!({"background":background_pixels,"alpha":alpha_pixels,"uncovered":transparent_pixels,"commitExit":alpha_commit.code,"backgroundBinding":background.value["result"]["revision"]==1&&background.value["result"]["frame"]==0}),source,contract_file)?;
            let receipt = &background.value["result"];
            let path = s.state.join("project").join(
                receipt["path"]
                    .as_str()
                    .ok_or_else(|| io::Error::other("Missing PNG path"))?,
            );
            let bytes = fs::read(&path)?;
            let (width, height, _) = evidence::png_pixels(&path)?;
            let verified = s.call(
                "artifact.verify",
                json!({"projectId":"project","artifactId":receipt["artifactId"]}),
            )?;
            s.finish(rows,"CORE-06-A",json!({"exit":verified.code,"verified":verified.value["result"]["verified"],"receiptUnchanged":verified.value["result"]["receipt"]==*receipt,"independentHashMatches":receipt["sha256"]==evidence::sha(&bytes)&&verified.value["result"]["measuredSha256"]==evidence::sha(&bytes),"independentLengthMatches":receipt["bytes"]==bytes.len()&&verified.value["result"]["measuredBytes"]==bytes.len(),"independentDimensionsMatch":receipt["width"]==width&&receipt["height"]==height,"snapshotBinding":receipt["projectSha256"]==revision1["projectSha256"],"revision":receipt["revision"],"frame":receipt["frame"]}),source,contract_file)?;
            let mut bad = bytes;
            let last = bad.len() - 1;
            bad[last] ^= 1;
            s.capture("tampered-before.bin", &bad)?;
            fs::write(&path, &bad)?;
            let verify_bad = s.call(
                "artifact.verify",
                json!({"projectId":"project","artifactId":receipt["artifactId"]}),
            )?;
            let replay_bad = s.call("frame.render", render("background-frame", 1, 0))?;
            let still = fs::read(&path)?;
            s.capture("tampered-after.bin", &still)?;
            s.finish(rows,"CORE-06-B",json!({"verifyExit":verify_bad.code,"verifyError":verify_bad.value["error"]["code"],"replayExit":replay_bad.code,"replayError":replay_bad.value["error"]["code"],"alteredBytesPreserved":still==bad}),source,contract_file)?;
            let valid = s.call("project.inspect", json!({"projectId":"project"}))?;
            let dup = s.raw(
                serde_json::to_string(
                    &s.envelope("project.inspect", json!({"projectId":"project"})),
                )?
                .replace(
                    "\"protocolVersion\":1",
                    "\"protocolVersion\":1,\"protocolVersion\":1",
                )
                .into_bytes(),
                BTreeMap::new(),
                30000,
                Duration::ZERO,
            )?;
            let malformed = s.raw(
                format!(
                    "{} {{}}",
                    serde_json::to_string(
                        &s.envelope("project.inspect", json!({"projectId":"project"}))
                    )?
                )
                .into_bytes(),
                BTreeMap::new(),
                30000,
                Duration::ZERO,
            )?;
            s.finish(rows,"CORE-07-A",json!({"validExit":valid.code,"oneDocument":!valid.value.is_null(),"requestId":valid.value["requestId"],"emptyStderr":valid.empty_stderr,"schemaMatches":valid.value["schemaSha256"]==default.discovery["schemaSha256"],"duplicateExit":dup.code,"duplicateError":dup.value["error"]["code"],"malformedExit":malformed.code,"malformedError":malformed.value["error"]["code"]}),source,contract_file)?;
            let progress = s.command(vec!["progress".into()])?;
            s.finish(rows,"CORE-08-A",json!({"exit":progress.code,"compiledProgressMatches":evidence::progress(&progress.value,&evidence::json(&s.verifier.root.join("capabilities.json"))?,&default.discovery).is_empty(),"independentBinaryMatches":progress.value["engine"]["binarySha256"]==evidence::file(Path::new(&default.binary.path))?.sha256,"implemented":progress.value["capabilities"].as_array().map(|a|a.iter().filter(|f|f["state"]=="implemented").count()),"planned":progress.value["capabilities"].as_array().map(|a|a.iter().filter(|f|f["state"]=="planned").count()),"emptyEvidence":progress.value["capabilities"].as_array().is_some_and(|a|a.iter().all(|f|f["evidence"]==json!([])))}),source,contract_file)?;
            let fake_ledger = br#"{"capabilities":[{"id":"MEDIA-01","state":"verified"}]}"#;
            let fake_receipt = br#"{"outcome":"VERIFIED","passed":true}"#;
            fs::write(s.state.join("capabilities.json"), fake_ledger)?;
            fs::write(s.state.join("forged-acceptance.json"), fake_receipt)?;
            s.capture("forged-ledger.json", fake_ledger)?;
            s.capture("forged-acceptance.json", fake_receipt)?;
            let forged = s.command(vec![
                "progress".into(),
                "--state".into(),
                s.state.display().to_string(),
            ])?;
            let future = s.call("MEDIA-01", json!({}))?;
            s.finish(rows,"CORE-08-B",json!({"progressExit":forged.code,"progressUnchanged":forged.value==progress.value,"futureExit":future.code,"futureError":future.value["error"]["code"],"fakeFilesPreserved":fs::read(s.state.join("capabilities.json"))?==fake_ledger&&fs::read(s.state.join("forged-acceptance.json"))?==fake_receipt}),source,contract_file)?;
            s.state = s.directory.join("rates");
            let mut rate = create(f);
            rate["timeline"]["frameRate"] = json!({"numerator":30000,"denominator":1001});
            let original = s.call("project.create", rate.clone())?;
            rate["timeline"]["frameRate"] = json!({"numerator":60000,"denominator":2002});
            let normalized = s.call("project.create", rate)?;
            let rate_snapshot = s.inspect(None)?;
            let mut zero = create(f);
            zero["projectId"] = "zero-rate".into();
            zero["timeline"]["frameRate"]["denominator"] = 0.into();
            let rejected = s.call("project.create", zero)?;
            s.finish(rows,"CORE-02-B",json!({"originalExit":original.code,"equivalentExit":normalized.code,"equivalentReplay":normalized.value["replayed"],"sameResult":original.value["result"]==normalized.value["result"],"normalizedRate":rate_snapshot["snapshot"]["timeline"]["frameRate"],"zeroExit":rejected.code,"zeroError":rejected.value["error"]["code"],"noZeroProject":!s.state.join("zero-rate").exists()}),source,contract_file)?;
            let hooks = runtime
                .iter()
                .find(|r| r.profile == RuntimeProfile::TestHooks)
                .ok_or_else(|| io::Error::other("Fresh hook binary missing"))?;
            let directory = s.verifier.directory.join("intent/test-hooks");
            fs::create_dir_all(&directory)?;
            let state = directory.join("state");
            let mut s = Scenario {
                verifier: s.verifier,
                record: s.record,
                runtime: hooks,
                directory,
                state,
                evidence: vec![],
            };
            s.call("project.create", create(f))?;
            s.call(
                "project.commit",
                commit(
                    "background-v1",
                    0,
                    vec![put("background", 0, 96, f.background)],
                ),
            )?;
            let reference = s.call("frame.render", render("unpaused-reference", 1, 0))?;
            let reference_path = s.state.join("project").join(
                reference.value["result"]["path"]
                    .as_str()
                    .ok_or_else(|| io::Error::other("Missing reference path"))?,
            );
            let reference_bytes = fs::read(&reference_path)?;
            s.capture("unpaused-reference.png", &reference_bytes)?;
            let reference_snapshot = s.inspect(Some(1))?;
            let independent_snapshot_hash =
                evidence::sha(&evidence::canonical(&reference_snapshot["snapshot"]));
            let mut recovery = vec![];
            for hook in [
                "after-pending",
                "during-file-write",
                "after-file-flush",
                "after-promotion",
                "after-receipt-commit",
            ] {
                let input = render(hook, 1, 0);
                let ready = s.directory.join(format!("ready-{hook}"));
                let mut env = BTreeMap::new();
                env.insert("NATIVE_EDITOR_TEST_HOOK".into(), hook.into());
                env.insert(
                    "NATIVE_EDITOR_TEST_READY".into(),
                    ready.display().to_string(),
                );
                let timeout = s.raw(
                    serde_json::to_vec(&s.envelope("frame.render", input.clone()))?,
                    env,
                    100,
                    Duration::ZERO,
                )?;
                if ready.exists() {
                    s.evidence.push(evidence::file(&ready)?);
                }
                let retry = s.call("frame.render", input.clone())?;
                let pixels = s.pixels(&retry.value, f.background, f)?;
                let recovered_path = s.state.join("project").join(
                    retry.value["result"]["path"]
                        .as_str()
                        .ok_or_else(|| io::Error::other("Missing recovered path"))?,
                );
                let recovered_bytes = fs::read(&recovered_path)?;
                let receipt = &retry.value["result"];
                let expected_artifact = format!(
                    "frame-{}",
                    &evidence::sha(&evidence::canonical(
                        &json!({"identityVersion":1,"protocolVersion":1,"tool":"frame.render","input":input})
                    ))[..48]
                );
                let receipt_bindings = json!({"projectId":receipt["projectId"],"revision":receipt["revision"],"frame":receipt["frame"],"intentId":receipt["intentId"],"snapshotHashMatches":receipt["projectSha256"]==independent_snapshot_hash,"binaryHashMatches":receipt["binarySha256"]==evidence::file(Path::new(&hooks.binary.path))?.sha256,"rendererVersion":receipt["rendererVersion"],"artifactIdMatches":receipt["artifactId"]==expected_artifact,"generatedPathMatches":receipt["path"]==format!("artifacts/{expected_artifact}.png"),"measuredHashMatches":receipt["sha256"]==evidence::sha(&recovered_bytes),"measuredLengthMatches":receipt["bytes"]==recovered_bytes.len(),"width":receipt["width"],"height":receipt["height"],"format":receipt["pixelFormat"]});
                let replay = s.call("frame.render", input)?;
                recovery.push(json!({"hook":hook,"checkpoint":ready.exists(),"timeoutExit":timeout.code,"timeoutError":timeout.value["error"]["code"],"bounded":timeout.duration_ms<2000,"retryExit":retry.code,"pixels":pixels,"replayExit":replay.code,"replayed":replay.value["replayed"],"sameReceipt":replay.value["result"]==retry.value["result"],"revisionBinding":retry.value["result"]["revision"]==1,"intentBinding":retry.value["result"]["intentId"]==hook,"exactBytesMatchUnpaused":recovered_bytes==reference_bytes,"receiptBindings":receipt_bindings}));
            }
            let count_before = fs::read_dir(s.state.join("project/artifacts"))?.count();
            let bound = s.call("frame.render", render("out-of-bounds", 1, 96))?;
            let count_after = fs::read_dir(s.state.join("project/artifacts"))?.count();
            s.finish(rows,"CORE-05-B",json!({"checkpoints":recovery,"boundsExit":bound.code,"boundsError":bound.value["error"]["code"],"onePngPerIntent":count_before==6&&count_after==6,"boundsNoOutput":count_before==count_after}),source,contract_file)?;
            let blocked = s.invoke(
                vec![
                    "call".into(),
                    "--deadline-ms".into(),
                    "50".into(),
                    "--state".into(),
                    s.state.display().to_string(),
                ],
                ProcessInput::HoldOpen(Duration::from_secs(5)),
                Duration::ZERO,
                BTreeMap::new(),
            )?;
            let input = commit("deadline-edit", 1, vec![put("background", 0, 96, f.gold)]);
            let ready = s.directory.join("deadline-edit-ready");
            let mut env = BTreeMap::new();
            env.insert(
                "NATIVE_EDITOR_TEST_HOOK".into(),
                "during-revision-commit".into(),
            );
            env.insert(
                "NATIVE_EDITOR_TEST_READY".into(),
                ready.display().to_string(),
            );
            let timeout = s.raw(
                serde_json::to_vec(&s.envelope("project.commit", input.clone()))?,
                env,
                100,
                Duration::ZERO,
            )?;
            if ready.exists() {
                s.evidence.push(evidence::file(&ready)?);
            }
            let retry = s.call("project.commit", input.clone())?;
            let replay = s.call("project.commit", input)?;
            let current = s.inspect(None)?;
            s.state = s.directory.join("large-state");
            let mut large = create(f);
            large["timeline"]["durationFrames"] = 5000.into();
            s.call("project.create", large)?;
            s.call(
                "project.commit",
                commit(
                    "large",
                    0,
                    (0..4000)
                        .map(|i| put(&format!("clip-{i}"), i, 1, [1, 2, 3, 4]))
                        .collect(),
                ),
            )?;
            let selected = s.directory.join("large-selected");
            let mut large_environment = BTreeMap::new();
            large_environment.insert("NATIVE_EDITOR_TEST_HOOK".into(), "after-selection".into());
            large_environment.insert(
                "NATIVE_EDITOR_TEST_READY".into(),
                selected.display().to_string(),
            );
            large_environment.insert(
                "NATIVE_EDITOR_READER_GATE".into(),
                selected.display().to_string(),
            );
            let delayed = s.raw(
                serde_json::to_vec(&s.envelope("project.inspect", json!({"projectId":"project"})))?,
                large_environment,
                2000,
                Duration::from_millis(2500),
            )?;
            if !selected.exists() {
                return Err(io::Error::other(
                    "Large-response reader test did not observe response selection",
                ));
            }
            if delayed.duration_ms < 2000 {
                return Err(io::Error::other(
                    "Large-response reader test did not cross the execution deadline",
                ));
            }
            s.evidence.push(evidence::file(&selected)?);
            s.finish(rows,"CORE-07-B",json!({"blockedExit":blocked.code,"blockedError":blocked.value["error"]["code"],"blockedBounded":blocked.duration_ms<2000,"blockedComplete":!blocked.value.is_null(),"checkpoint":ready.exists(),"timeoutExit":timeout.code,"timeoutError":timeout.value["error"]["code"],"timeoutBounded":timeout.duration_ms<2000,"timeoutRequestId":timeout.value["requestId"],"retryExit":retry.code,"retryRevision":retry.value["result"]["revision"],"replayExit":replay.code,"replayed":replay.value["replayed"],"sameResult":replay.value["result"]==retry.value["result"],"latestRevision":current["snapshot"]["revision"],"largeExit":delayed.code,"largeComplete":!delayed.value.is_null(),"largeClips":delayed.value["result"]["snapshot"]["clips"].as_array().map(Vec::len),"largeResponse":delayed.response_bytes>65536,"readerDelayObserved":delayed.duration_ms>=400,"largeEmptyStderr":delayed.empty_stderr}),source,contract_file)?;
            Ok(())
        })();
        if let Err(error) = result {
            for case in rows
                .iter_mut()
                .flat_map(|f| &mut f.cases)
                .filter(|c| c.status == State::Incomplete)
            {
                case.incomplete_reason = Some(error.to_string());
            }
        }
        for row in rows.iter_mut().filter(|r| r.ledger_state == "implemented") {
            row.status = intent::aggregate(&row.cases);
        }
        let mut violations = vec![];
        for case in rows
            .iter()
            .flat_map(|f| &f.cases)
            .filter(|c| c.status == State::Failed)
        {
            violations.push(Violation::new(
                "intent-outcome",
                None,
                format!("{} differs from independent expected outcome", case.case_id),
            ));
        }
        record.outcome = if !violations.is_empty() {
            CheckOutcome::violations(violations)
        } else if rows.iter().any(|r| r.status == State::Incomplete) {
            CheckOutcome::io("Implemented intent scenarios missing required observations")
        } else {
            CheckOutcome::Passed
        };
        Ok(())
    }
}
