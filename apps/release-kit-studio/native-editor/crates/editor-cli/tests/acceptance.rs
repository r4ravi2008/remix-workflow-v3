use flate2::read::ZlibDecoder;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
#[cfg(feature = "test-hooks")]
use std::process::Child;
use std::process::{Command, Output, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Barrier};
use std::time::{Duration, Instant};

const BINARY: &str = env!("CARGO_BIN_EXE_native-editor");
static SEQUENCE: AtomicU64 = AtomicU64::new(0);
fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
fn canonical(value: &Value) -> Vec<u8> {
    fn write(value: &Value, output: &mut String) {
        match value {
            Value::Object(map) => {
                let mut keys: Vec<_> = map.keys().collect();
                keys.sort_by_key(|key| key.encode_utf16().collect::<Vec<_>>());
                output.push('{');
                for (i, key) in keys.into_iter().enumerate() {
                    if i != 0 {
                        output.push(',');
                    }
                    output.push_str(&serde_json::to_string(key).unwrap());
                    output.push(':');
                    write(&map[key], output);
                }
                output.push('}');
            }
            Value::Array(array) => {
                output.push('[');
                for (i, item) in array.iter().enumerate() {
                    if i != 0 {
                        output.push(',');
                    }
                    write(item, output);
                }
                output.push(']');
            }
            _ => output.push_str(&serde_json::to_string(value).unwrap()),
        }
    }
    let mut output = String::new();
    write(value, &mut output);
    output.into_bytes()
}
struct Run {
    directory: PathBuf,
    state: PathBuf,
    schema: String,
    sequence: AtomicU64,
    preserve: bool,
}
impl Run {
    fn new(case: &str) -> Self {
        let preserve = std::env::var_os("NATIVE_EDITOR_EVIDENCE_DIR").is_some();
        let base = std::env::var_os("NATIVE_EDITOR_EVIDENCE_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|| std::env::temp_dir().canonicalize().unwrap());
        fs::create_dir_all(&base).unwrap();
        let directory = base.join(format!(
            "{}-{}-{}",
            case,
            std::process::id(),
            SEQUENCE.fetch_add(1, Ordering::SeqCst)
        ));
        fs::create_dir(&directory).unwrap();
        let state = directory.join("state");
        let output = Command::new(BINARY).arg("tools").output().unwrap();
        assert!(output.status.success());
        let discovery: Value = serde_json::from_slice(&output.stdout).unwrap();
        fs::write(directory.join("discovery.json"), &output.stdout).unwrap();
        Self {
            directory,
            state,
            schema: discovery["schemaSha256"].as_str().unwrap().into(),
            sequence: AtomicU64::new(0),
            preserve,
        }
    }
    fn envelope(&self, tool: &str, input: Value) -> Value {
        json!({"protocolVersion":1,"requestId":"acceptance-request","expectedSchemaSha256":if tool=="engine.capabilities" {Value::Null} else {self.schema.clone().into()},"tool":tool,"input":input})
    }
    fn raw(&self, bytes: &[u8]) -> (i32, Value) {
        let mut child = Command::new(BINARY)
            .args(["call", "--state"])
            .arg(&self.state)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        child.stdin.take().unwrap().write_all(bytes).unwrap();
        let output = child.wait_with_output().unwrap();
        let sequence = self.sequence.fetch_add(1, Ordering::SeqCst);
        fs::write(
            self.directory.join(format!("request-{sequence}.json")),
            bytes,
        )
        .unwrap();
        fs::write(
            self.directory.join(format!("response-{sequence}.json")),
            &output.stdout,
        )
        .unwrap();
        fs::write(self.directory.join(format!("process-{sequence}.json")),serde_json::to_vec(&json!({"exitCode":output.status.code(),"requestSha256":sha(bytes),"responseSha256":sha(&output.stdout),"stderr":String::from_utf8_lossy(&output.stderr)})).unwrap()).unwrap();
        decode_output(output)
    }
    fn call(&self, tool: &str, input: Value) -> (i32, Value) {
        self.raw(&serde_json::to_vec(&self.envelope(tool, input)).unwrap())
    }
    fn ok(&self, tool: &str, input: Value) -> Value {
        let (code, response) = self.call(tool, input);
        assert_eq!(code, 0, "{response}");
        response
    }
    fn reject(&self, tool: &str, input: Value, error: &str) -> Value {
        let (code, response) = self.call(tool, input);
        assert_eq!(code, 2, "{response}");
        assert_eq!(response["error"]["code"], error, "{response}");
        response
    }
    fn create(&self) -> Value {
        self.ok("project.create", create("project", "create"))
    }
    fn inspect(&self) -> Value {
        self.ok("project.inspect", json!({"projectId":"project"}))
    }
    fn commit(&self) -> Value {
        self.ok(
            "project.commit",
            commit("edit", 0, vec![put("solid", 0, 4, [12, 25, 48, 160])]),
        )
    }
    fn render(&self, frame: u64, intent: &str) -> Value {
        self.ok("frame.render", render(frame, intent, 1))
    }
    fn artifact_path(&self, receipt: &Value) -> PathBuf {
        self.state
            .join(receipt["projectId"].as_str().unwrap())
            .join(receipt["path"].as_str().unwrap())
    }
}
impl Drop for Run {
    fn drop(&mut self) {
        if !self.preserve {
            let _ = fs::remove_dir_all(&self.directory);
        }
    }
}
fn decode_output(output: Output) -> (i32, Value) {
    let code = output
        .status
        .code()
        .expect("structured response has an exit status");
    let response: Value = serde_json::from_slice(&output.stdout).unwrap_or_else(|error| {
        panic!(
            "one JSON response required: {error}; stdout={:?}; stderr={:?}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        )
    });
    assert!(output.stdout.len() <= 4_194_304);
    assert_eq!(response["protocolVersion"], 1);
    assert_eq!(response["schemaSha256"].as_str().unwrap().len(), 64);
    match response["status"].as_str() {
        Some("success") => {
            assert_eq!(code, 0, "success must exit 0");
            assert!(response.get("error").is_none());
            assert!(response.get("result").is_some());
            assert!(response.get("replayed").is_some());
            assert_eq!(response.as_object().unwrap().len(), 6);
        }
        Some("error") => {
            let internal = matches!(
                response["error"]["code"].as_str().unwrap(),
                "storage_failure"
                    | "internal_failure"
                    | "protocol_mismatch"
                    | "process_timeout"
                    | "process_interrupted"
            );
            assert_eq!(
                code,
                if internal { 1 } else { 2 },
                "error exit class differs from its code"
            );
            assert!(response.get("result").is_none());
            assert!(response.get("replayed").is_none());
            assert_eq!(response.as_object().unwrap().len(), 5);
        }
        _ => panic!("discriminated response required"),
    }
    (code, response)
}
fn create(project: &str, intent: &str) -> Value {
    json!({"projectId":project,"intentId":intent,"name":"తెలుగు \"native\" project","timeline":{"frameRate":{"numerator":30000,"denominator":1001},"durationFrames":6,"canvas":{"width":3,"height":2}}})
}
fn put(id: &str, start: u64, duration: u64, rgba: [u8; 4]) -> Value {
    json!({"kind":"clip.put","clip":{"id":id,"startFrame":start,"durationFrames":duration,"source":{"kind":"solid","rgba":rgba}}})
}
fn commit(intent: &str, revision: u64, edits: Vec<Value>) -> Value {
    json!({"projectId":"project","intentId":intent,"expectedRevision":revision,"edits":edits})
}
fn render(frame: u64, intent: &str, revision: u64) -> Value {
    json!({"projectId":"project","intentId":intent,"revision":revision,"frame":frame,"format":"png-rgba8"})
}

fn pixels(path: &Path) -> (u32, u32, Vec<u8>) {
    let bytes = fs::read(path).unwrap();
    assert_eq!(&bytes[..8], b"\x89PNG\r\n\x1a\n");
    let (mut offset, mut width, mut height) = (8, 0, 0);
    let mut compressed = vec![];
    while offset < bytes.len() {
        let length = u32::from_be_bytes(bytes[offset..offset + 4].try_into().unwrap()) as usize;
        let kind = &bytes[offset + 4..offset + 8];
        let data = &bytes[offset + 8..offset + 8 + length];
        match kind {
            b"IHDR" => {
                width = u32::from_be_bytes(data[..4].try_into().unwrap());
                height = u32::from_be_bytes(data[4..8].try_into().unwrap());
                assert_eq!(&data[8..], [8, 6, 0, 0, 0]);
            }
            b"IDAT" => compressed.extend_from_slice(data),
            b"IEND" => assert!(data.is_empty()),
            _ => {}
        }
        offset += length + 12;
    }
    assert_eq!(offset, bytes.len());
    let mut scanlines = vec![];
    ZlibDecoder::new(&compressed[..])
        .read_to_end(&mut scanlines)
        .unwrap();
    let stride = width as usize * 4;
    assert_eq!(scanlines.len(), height as usize * (stride + 1));
    let mut result = vec![];
    for line in scanlines.chunks_exact(stride + 1) {
        assert_eq!(line[0], 0, "fixture encoder promises unfiltered scanlines");
        result.extend_from_slice(&line[1..]);
    }
    (width, height, result)
}

#[test]
fn p0_discovery() {
    let run = Run::new("P0-DISCOVERY");
    let response = run.ok("engine.capabilities", json!({}));
    let result = &response["result"];
    assert_eq!(result["binarySha256"], sha(&fs::read(BINARY).unwrap()));
    assert_eq!(result["identityVersion"], 1);
    let names: Vec<_> = result["tools"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| v["name"].as_str().unwrap())
        .collect();
    assert_eq!(
        names,
        [
            "artifact.verify",
            "engine.capabilities",
            "frame.render",
            "project.commit",
            "project.create",
            "project.inspect"
        ]
    );
    run.reject("imaginary.tool", json!({}), "unknown_tool");
    run.reject("MEDIA-01", json!({}), "unsupported_capability");
    assert!(!run.state.exists());
}
#[test]
fn p0_schema() {
    let run = Run::new("P0-SCHEMA");
    let discovery: Value =
        serde_json::from_slice(&Command::new(BINARY).arg("tools").output().unwrap().stdout)
            .unwrap();
    let mut schemas = vec![];
    for tool in discovery["tools"].as_array().unwrap() {
        let name = tool["name"].as_str().unwrap();
        let output = Command::new(BINARY)
            .args(["schema", name])
            .output()
            .unwrap();
        assert!(output.status.success());
        let schema: Value = serde_json::from_slice(&output.stdout).unwrap();
        for key in ["inputSchema", "outputSchema", "envelopeSchema"] {
            assert_eq!(
                schema[key]["$schema"],
                "https://json-schema.org/draft/2020-12/schema"
            );
        }
        assert!(schema["envelopeSchema"]["required"]
            .as_array()
            .unwrap()
            .contains(&json!("expectedSchemaSha256")));
        schemas.push(json!({"name":name,"inputSchema":schema["inputSchema"],"outputSchema":schema["outputSchema"]}));
    }
    assert_eq!(
        run.schema,
        sha(&canonical(&json!({"protocolVersion":1,"tools":schemas})))
    );
    let mut input = create("project", "create");
    input["extra"] = true.into();
    run.reject("project.create", input, "invalid_input");
    assert!(!run.state.exists());
}
#[test]
fn p0_rational_rate() {
    let run = Run::new("P0-RATIONAL-RATE");
    run.create();
    let inspected = run.inspect();
    assert_eq!(
        inspected["result"]["snapshot"]["timeline"]["frameRate"],
        json!({"numerator":30000,"denominator":1001})
    );
    let mut normalized = create("project", "create");
    normalized["timeline"]["frameRate"] = json!({"numerator":60000,"denominator":2002});
    assert_eq!(run.ok("project.create", normalized)["replayed"], true);
    let mut zero = create("another", "create");
    zero["timeline"]["frameRate"]["denominator"] = 0.into();
    run.reject("project.create", zero, "invalid_input");
    assert!(!run.state.join("another").exists());
}
#[test]
fn p0_transaction() {
    let run = Run::new("P0-TRANSACTION");
    run.create();
    let before = run.inspect();
    run.reject(
        "project.commit",
        commit(
            "bad",
            0,
            vec![
                put("good", 0, 2, [1, 2, 3, 4]),
                json!({"kind":"clip.remove","clipId":"missing"}),
            ],
        ),
        "invalid_input",
    );
    assert_eq!(run.inspect()["result"], before["result"]);
    run.ok(
        "project.commit",
        commit(
            "good",
            0,
            vec![put("a", 0, 2, [1, 2, 3, 4]), put("b", 2, 2, [5, 6, 7, 8])],
        ),
    );
    assert_eq!(
        run.inspect()["result"]["snapshot"]["clips"]
            .as_array()
            .unwrap()
            .len(),
        2
    );
}
#[test]
fn p0_replay() {
    let run = Run::new("P0-REPLAY");
    run.create();
    let first = run.commit();
    run.ok(
        "project.commit",
        commit("later", 1, vec![put("solid", 0, 4, [9, 8, 7, 6])]),
    );
    let replay = run.ok(
        "project.commit",
        commit("edit", 0, vec![put("solid", 0, 4, [12, 25, 48, 160])]),
    );
    assert_eq!(first["result"], replay["result"]);
    assert_eq!(replay["replayed"], true);
    assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 2);
    let snapshot = &run.inspect()["result"]["snapshot"];
    assert_eq!(
        sha(&canonical(snapshot)),
        run.inspect()["result"]["projectSha256"]
    );
}
#[test]
fn p0_intent_conflict() {
    let run = Run::new("P0-INTENT-CONFLICT");
    run.create();
    run.commit();
    let before = run.inspect();
    run.reject(
        "project.commit",
        commit("edit", 0, vec![put("solid", 0, 4, [0, 0, 0, 0])]),
        "intent_conflict",
    );
    run.reject("frame.render", render(0, "edit", 1), "intent_conflict");
    run.reject(
        "project.commit",
        commit("create", 1, vec![put("solid", 0, 4, [1, 1, 1, 1])]),
        "intent_conflict",
    );
    assert_eq!(run.inspect()["result"], before["result"]);
    run.ok("project.create", create("other", "edit"));
}
#[test]
fn p0_stale_revision() {
    let run = Run::new("P0-STALE-REVISION");
    run.create();
    run.commit();
    let before = run.inspect();
    let error = run.reject(
        "project.commit",
        commit("stale", 0, vec![put("solid", 0, 4, [0, 0, 0, 0])]),
        "revision_conflict",
    );
    assert_eq!(error["error"]["details"]["currentRevision"], 1);
    assert_eq!(error["error"]["retry"], "inspect_then_rebase");
    assert_eq!(run.inspect()["result"], before["result"]);
}
fn concurrent(run: &Run, tool: &str, inputs: Vec<Value>) -> Vec<(i32, Value)> {
    let barrier = Arc::new(Barrier::new(inputs.len()));
    std::thread::scope(|scope| {
        let workers: Vec<_> = inputs
            .into_iter()
            .map(|input| {
                let barrier = Arc::clone(&barrier);
                scope.spawn(move || {
                    barrier.wait();
                    for _ in 0..30 {
                        let output = run.call(tool, input.clone());
                        if output.1["error"]["code"] != "store_busy" {
                            return output;
                        }
                        std::thread::sleep(Duration::from_millis(5));
                    }
                    panic!("bounded identical-intent retry did not resolve contention")
                })
            })
            .collect();
        workers
            .into_iter()
            .map(|worker| worker.join().unwrap())
            .collect()
    })
}
#[test]
fn p0_concurrent_edit() {
    let run = Run::new("P0-CONCURRENT-EDIT");
    run.create();
    let outcomes = concurrent(
        &run,
        "project.commit",
        vec![
            commit("left", 0, vec![put("left", 0, 2, [1, 2, 3, 4])]),
            commit("right", 0, vec![put("right", 0, 2, [4, 3, 2, 1])]),
        ],
    );
    assert_eq!(outcomes.iter().filter(|v| v.0 == 0).count(), 1);
    assert_eq!(
        outcomes
            .iter()
            .filter(|v| v.1["error"]["code"] == "revision_conflict")
            .count(),
        1
    );
    assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 1);
}
#[test]
fn p0_native_pixels() {
    let run = Run::new("P0-NATIVE-PIXELS");
    run.create();
    run.commit();
    let solid = run.render(0, "solid-frame");
    assert_eq!(
        pixels(&run.artifact_path(&solid["result"])),
        (3, 2, [12, 25, 48, 160].repeat(6))
    );
    let blank = run.render(4, "blank-frame");
    assert_eq!(
        pixels(&run.artifact_path(&blank["result"])),
        (3, 2, [0, 0, 0, 0].repeat(6))
    );
}
#[test]
fn p0_receipt_binding() {
    let run = Run::new("P0-RECEIPT-BINDING");
    run.create();
    let committed = run.commit();
    let receipt = run.render(2, "bound")["result"].clone();
    assert_eq!(receipt["projectId"], "project");
    assert_eq!(receipt["revision"], 1);
    assert_eq!(receipt["frame"], 2);
    assert_eq!(receipt["intentId"], "bound");
    assert_eq!(
        receipt["projectSha256"],
        committed["result"]["projectSha256"]
    );
    assert_eq!(receipt["rendererVersion"], "native-rgba-png/0.1.0");
    assert_eq!(receipt["binarySha256"], sha(&fs::read(BINARY).unwrap()));
    let bytes = fs::read(run.artifact_path(&receipt)).unwrap();
    assert_eq!(receipt["sha256"], sha(&bytes));
    assert_eq!(receipt["bytes"], bytes.len());
    let mut unsigned = receipt.clone();
    unsigned.as_object_mut().unwrap().remove("receiptSha256");
    assert_eq!(receipt["receiptSha256"], sha(&canonical(&unsigned)));
    let verification = run.ok(
        "artifact.verify",
        json!({"projectId":"project","artifactId":receipt["artifactId"]}),
    );
    assert_eq!(verification["result"]["verified"], true);
    run.ok("project.create", create("other", "create"));
    run.reject(
        "artifact.verify",
        json!({"projectId":"other","artifactId":receipt["artifactId"]}),
        "artifact_not_found",
    );
}
#[test]
fn p0_tamper() {
    let run = Run::new("P0-TAMPER");
    run.create();
    run.commit();
    let receipt = run.render(0, "frame")["result"].clone();
    let path = run.artifact_path(&receipt);
    let mut bytes = fs::read(&path).unwrap();
    bytes[30] ^= 1;
    fs::write(&path, &bytes).unwrap();
    run.reject(
        "artifact.verify",
        json!({"projectId":"project","artifactId":receipt["artifactId"]}),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "frame.render",
        render(0, "frame", 1),
        "artifact_integrity_mismatch",
    );
    assert_eq!(fs::read(path).unwrap(), bytes);
}
#[test]
fn p0_forged_receipt() {
    let run = Run::new("P0-FORGED-RECEIPT");
    run.create();
    run.commit();
    let receipt = run.render(0, "frame")["result"].clone();
    let path = run.artifact_path(&receipt);
    let mut changed = fs::read(&path).unwrap();
    changed[30] ^= 1;
    fs::write(&path, &changed).unwrap();
    let changed_hash = sha(&changed);
    let mut forged = receipt.clone();
    forged["sha256"] = changed_hash.clone().into();
    forged.as_object_mut().unwrap().remove("receiptSha256");
    forged["receiptSha256"] = sha(&canonical(&forged)).into();
    for (key, value) in [
        ("sha256", json!(changed_hash)),
        ("expectedSha256", json!(changed_hash)),
        ("path", json!(path)),
        ("receipt", forged),
    ] {
        let mut input = json!({"projectId":"project","artifactId":receipt["artifactId"]});
        input[key] = value;
        run.reject("artifact.verify", input, "invalid_input");
    }
    run.reject(
        "artifact.verify",
        json!({"projectId":"project","artifactId":receipt["artifactId"]}),
        "artifact_integrity_mismatch",
    );
    assert_eq!(fs::read(path).unwrap(), changed);
}
#[test]
fn p0_resource_limit() {
    let run = Run::new("P0-RESOURCE-LIMIT");
    for (key, value) in [("width", 2049), ("height", 0)] {
        let mut input = create("project", "create");
        input["timeline"]["canvas"][key] = value.into();
        run.reject("project.create", input, "invalid_input");
        assert!(!run.state.exists());
    }
    let oversized = vec![b' '; 1_048_577];
    let (code, response) = run.raw(&oversized);
    assert_eq!(code, 2);
    assert_eq!(response["error"]["code"], "invalid_input");
    assert!(!run.state.exists());
    let mut input = create("project", "create");
    input["timeline"]["durationFrames"] = 10_000_001u64.into();
    run.reject("project.create", input, "invalid_input");
    assert!(!run.state.exists());
    let mut unsafe_number = run.envelope(
        "project.inspect",
        json!({"projectId":"project","revision":9_007_199_254_740_992u64}),
    );
    let output = run.raw(&serde_json::to_vec(&unsafe_number).unwrap());
    assert_eq!(output.1["error"]["code"], "invalid_input");
    assert!(!run.state.exists());
    unsafe_number["input"]["revision"] = 9_007_199_254_740_991u64.into();
    assert_eq!(
        run.raw(&serde_json::to_vec(&unsafe_number).unwrap()).1["error"]["code"],
        "project_not_found"
    );
}
#[test]
fn p0_create() {
    let run = Run::new("P0-CREATE");
    let outcomes = concurrent(
        &run,
        "project.create",
        vec![create("project", "left"), create("project", "right")],
    );
    assert_eq!(outcomes.iter().filter(|v| v.0 == 0).count(), 1);
    assert_eq!(
        outcomes
            .iter()
            .filter(|v| v.1["error"]["code"] == "project_exists")
            .count(),
        1
    );
    let winner = if outcomes[0].0 == 0 { "left" } else { "right" };
    let replay = run.ok("project.create", create("project", winner));
    assert_eq!(replay["replayed"], true);
    assert_eq!(replay["result"]["revision"], 0);
    let mut changed = create("project", winner);
    changed["name"] = "changed".into();
    run.reject("project.create", changed, "intent_conflict");
    let another = Run::new("P0-CREATE-IDENTICAL");
    let outcomes = concurrent(
        &another,
        "project.create",
        vec![create("project", "same"), create("project", "same")],
    );
    assert!(outcomes.iter().all(|v| v.0 == 0));
    assert_eq!(
        outcomes.iter().filter(|v| v.1["replayed"] == false).count(),
        1
    );
}
#[test]
fn p0_render_replay() {
    let run = Run::new("P0-RENDER-REPLAY");
    run.create();
    run.commit();
    let first = run.render(0, "frame");
    let path = run.artifact_path(&first["result"]);
    let original = fs::metadata(&path).unwrap().modified().unwrap();
    let replay = run.render(0, "frame");
    assert_eq!(replay["replayed"], true);
    assert_eq!(replay["result"], first["result"]);
    assert_eq!(fs::metadata(&path).unwrap().modified().unwrap(), original);
    fs::remove_file(&path).unwrap();
    run.reject(
        "frame.render",
        render(0, "frame", 1),
        "artifact_integrity_mismatch",
    );
    assert!(!path.exists());
}
#[test]
fn p0_clip_bounds() {
    let run = Run::new("P0-CLIP-BOUNDS");
    run.create();
    for edits in [
        vec![put("a", 0, 3, [1, 1, 1, 1]), put("b", 2, 2, [2, 2, 2, 2])],
        vec![put("a", 5, 2, [1, 1, 1, 1])],
        vec![put("a", 0, 0, [1, 1, 1, 1])],
        vec![put("a", 9_007_199_254_740_990, 2, [1, 1, 1, 1])],
        vec![],
    ] {
        run.reject(
            "project.commit",
            commit("invalid", 0, edits),
            "invalid_input",
        );
        assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 0);
    }
    run.ok(
        "project.commit",
        commit(
            "adjacent",
            0,
            vec![put("a", 0, 2, [1, 2, 3, 4]), put("b", 2, 2, [5, 6, 7, 8])],
        ),
    );
    for (frame, expected) in [(1, [1, 2, 3, 4]), (2, [5, 6, 7, 8]), (4, [0, 0, 0, 0])] {
        let receipt = run.render(frame, &format!("boundary-{frame}"));
        assert_eq!(
            pixels(&run.artifact_path(&receipt["result"])).2,
            expected.repeat(6)
        );
    }
    run.reject("frame.render", render(6, "outside", 1), "invalid_input");
    run.reject(
        "frame.render",
        render(0, "missing", 99),
        "revision_not_found",
    );
    run.reject(
        "project.inspect",
        json!({"projectId":"project","revision":99}),
        "revision_not_found",
    );
}
#[test]
fn p0_protocol() {
    let run = Run::new("P0-PROTOCOL");
    for bytes in [
        b"{".as_slice(),
        b"{}",
        b"{\"a\":1,\"a\":2}",
        b"{\"a\":{\"b\":1,\"b\":2}}",
        b"{} {}",
    ] {
        let (code, response) = run.raw(bytes);
        assert_eq!(code, 2);
        assert_eq!(response["error"]["code"], "invalid_input");
        assert_eq!(response["requestId"], Value::Null);
    }
    let mut request = run.envelope("engine.capabilities", json!({}));
    request
        .as_object_mut()
        .unwrap()
        .remove("expectedSchemaSha256");
    let (_, response) = run.raw(&serde_json::to_vec(&request).unwrap());
    assert_eq!(response["error"]["code"], "invalid_input");
    assert_eq!(response["requestId"], Value::Null);
    for (key, value, error) in [
        ("protocolVersion", json!(2), "protocol_mismatch"),
        ("expectedSchemaSha256", json!("wrong"), "protocol_mismatch"),
        ("unexpected", json!(true), "invalid_input"),
    ] {
        let mut request = run.envelope("project.create", create("project", "create"));
        request[key] = value;
        let (_, response) = run.raw(&serde_json::to_vec(&request).unwrap());
        assert_eq!(response["error"]["code"], error);
    }
    let duplicate =
        serde_json::to_string(&run.envelope("project.create", create("project", "create")))
            .unwrap()
            .replace("\"width\":3", "\"width\":3,\"width\":3");
    assert_eq!(
        run.raw(duplicate.as_bytes()).1["error"]["code"],
        "invalid_input"
    );
    assert!(!run.state.exists());
    for id in ["../escape", "a/b", "", "-prefix", "తెలుగు"] {
        let mut input = create("project", "create");
        input["projectId"] = id.into();
        run.reject("project.create", input, "invalid_input");
    }
}
#[test]
fn p0_progress_authority() {
    let output = Command::new(BINARY).arg("progress").output().unwrap();
    assert!(output.status.success());
    let progress: Value = serde_json::from_slice(&output.stdout).unwrap();
    for feature in progress["capabilities"].as_array().unwrap() {
        assert_ne!(feature["state"], "verified");
        assert_eq!(feature["evidence"], json!([]));
        if feature["id"].as_str().unwrap().starts_with("CORE-") {
            assert_eq!(feature["state"], "implemented");
        } else {
            assert_eq!(feature["state"], "planned");
        }
    }
    let run = Run::new("P0-PROGRESS-AUTHORITY");
    fs::create_dir_all(&run.state).unwrap();
    fs::write(
        run.state.join("capabilities.json"),
        br#"{"capabilities":[{"id":"MEDIA-01","state":"verified","command":"imaginary.tool"}]}"#,
    )
    .unwrap();
    fs::write(
        run.state.join("forged-acceptance.json"),
        br#"{"outcome":"VERIFIED","passed":true}"#,
    )
    .unwrap();
    run.reject("MEDIA-01", json!({}), "unsupported_capability");
    let output = Command::new(BINARY)
        .arg("progress")
        .arg("--state")
        .arg(&run.state)
        .output()
        .unwrap();
    assert_eq!(
        serde_json::from_slice::<Value>(&output.stdout).unwrap(),
        progress
    );
}
#[test]
fn p0_runtime_policy() {
    let run = Run::new("P0-RUNTIME-POLICY");
    run.ok("engine.capabilities", json!({}));
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap();
    let output = Command::new("cargo")
        .args(["metadata", "--format-version", "1", "--locked", "--offline"])
        .current_dir(root)
        .output()
        .unwrap();
    assert!(output.status.success());
    let metadata: Value = serde_json::from_slice(&output.stdout).unwrap();
    for package in metadata["packages"].as_array().unwrap() {
        let name = package["name"].as_str().unwrap().to_lowercase();
        for forbidden in [
            "ffmpeg",
            "libav",
            "tauri",
            "effect",
            "node",
            "bun",
            "cloudflare",
        ] {
            assert!(!name.contains(forbidden), "prohibited dependency {name}");
        }
    }
    fn sources(path: &Path, output: &mut Vec<PathBuf>) {
        for entry in fs::read_dir(path).unwrap() {
            let entry = entry.unwrap();
            assert!(!entry.file_type().unwrap().is_symlink());
            if entry.file_type().unwrap().is_dir() {
                sources(&entry.path(), output);
            } else if entry
                .path()
                .extension()
                .is_some_and(|extension| extension == "rs")
            {
                output.push(entry.path());
            }
        }
    }
    for role in ["editor-core", "editor-cli"] {
        let mut files = vec![];
        sources(&root.join("crates").join(role).join("src"), &mut files);
        for file in files {
            let source = fs::read_to_string(file).unwrap();
            let normalized = source.to_lowercase();
            for prohibited in [
                "command::new(",
                "python",
                "editor-local.mjs",
                "libav",
                "ffmpeg",
            ] {
                assert!(
                    !normalized.contains(prohibited),
                    "prohibited {role} invocation {prohibited}"
                );
            }
            if role == "editor-core" {
                assert!(!normalized.contains("std::process"));
            }
        }
    }
}
#[test]
fn identity_reference_vectors() {
    let a = json!({"😀":1,"\u{e000}":2,"a":"తెలుగు\n\"\\"});
    let b = json!({"a":"తెలుగు\n\"\\","\u{e000}":2,"😀":1});
    assert_eq!(editor_core::canonical_bytes(&a).unwrap(), canonical(&b));
    assert_eq!(
        editor_core::canonical_bytes(
            &serde_json::from_str::<Value>("[333333333.33333329,1e30,4.50,2e-3,1e-27]").unwrap()
        )
        .unwrap(),
        br#"[333333333.3333333,1e+30,4.5,0.002,1e-27]"#
    );
    let max = json!({"n":9_007_199_254_740_991u64});
    assert_eq!(editor_core::canonical_bytes(&max).unwrap(), canonical(&max));
    assert_ne!(
        sha(&canonical(&json!({"n":1}))),
        sha(&canonical(&json!({"n":2})))
    );
}
#[test]
fn very_short_deadline_has_one_terminal_response() {
    let run = Run::new("P0-DEADLINE");
    for deadline in [1, 2, 5, 10] {
        for _ in 0..3 {
            let mut child = Command::new(BINARY)
                .args(["call", "--deadline-ms", &deadline.to_string(), "--state"])
                .arg(&run.state)
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .unwrap();
            child
                .stdin
                .take()
                .unwrap()
                .write_all(
                    &serde_json::to_vec(&run.envelope("engine.capabilities", json!({}))).unwrap(),
                )
                .unwrap();
            let (code, response) = decode_output(child.wait_with_output().unwrap());
            if code == 1 {
                assert_eq!(response["error"]["code"], "process_timeout");
            } else {
                assert_eq!(code, 0);
            }
        }
    }
    let started = Instant::now();
    let mut child = Command::new(BINARY)
        .args(["call", "--deadline-ms", "10", "--state"])
        .arg(&run.state)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    let held_stdin = child.stdin.take().unwrap();
    let (code, response) = decode_output(child.wait_with_output().unwrap());
    drop(held_stdin);
    assert_eq!(code, 1);
    assert_eq!(response["error"]["code"], "process_timeout");
    assert!(started.elapsed() < Duration::from_secs(1));
}
#[cfg(unix)]
#[test]
fn symlink_state_and_artifact_paths_fail() {
    use std::os::unix::fs::symlink;
    let run = Run::new("P0-PATHS");
    let outside = run.directory.join("outside");
    fs::create_dir(&outside).unwrap();
    symlink(&outside, &run.state).unwrap();
    run.reject(
        "project.create",
        create("project", "create"),
        "invalid_input",
    );
    assert!(fs::read_dir(&outside).unwrap().next().is_none());
    fs::remove_file(&run.state).unwrap();
    run.create();
    run.commit();
    let receipt = run.render(0, "frame")["result"].clone();
    let path = run.artifact_path(&receipt);
    fs::rename(&path, outside.join("stolen.png")).unwrap();
    symlink(outside.join("stolen.png"), &path).unwrap();
    run.reject(
        "artifact.verify",
        json!({"projectId":"project","artifactId":receipt["artifactId"]}),
        "invalid_input",
    );
}

#[cfg(feature = "test-hooks")]
fn paused(run: &Run, tool: &str, input: Value, hook: &str) -> Child {
    let ready = run.directory.join(format!("ready-{hook}"));
    let mut child = Command::new(BINARY)
        .args(["call", "--state"])
        .arg(&run.state)
        .env("NATIVE_EDITOR_TEST_HOOK", hook)
        .env("NATIVE_EDITOR_TEST_READY", &ready)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(&serde_json::to_vec(&run.envelope(tool, input)).unwrap())
        .unwrap();
    let start = Instant::now();
    while !ready.exists() {
        if let Some(status) = child.try_wait().unwrap() {
            panic!("hook {hook} exited before checkpoint {status}");
        }
        assert!(
            start.elapsed() < Duration::from_secs(5),
            "hook {hook} did not pause"
        );
        std::thread::sleep(Duration::from_millis(5));
    }
    child
}
#[cfg(feature = "test-hooks")]
#[test]
fn p0_crash_recovery() {
    for hook in [
        "before-transaction",
        "during-revision-commit",
        "after-commit",
    ] {
        let run = Run::new(&format!("P0-CRASH-RECOVERY-{hook}"));
        run.create();
        let input = commit("original", 0, vec![put("solid", 0, 4, [12, 25, 48, 160])]);
        let mut child = paused(&run, "project.commit", input.clone(), hook);
        child.kill().unwrap();
        let output = child.wait_with_output().unwrap();
        assert!(!output.status.success());
        let retry = run.ok("project.commit", input.clone());
        assert_eq!(retry["result"]["revision"], 1);
        assert_eq!(retry["replayed"], hook == "after-commit");
        let again = run.ok("project.commit", input);
        assert_eq!(again["result"], retry["result"]);
        assert_eq!(again["replayed"], true);
        assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 1);
    }
    for hook in [
        "before-transaction",
        "during-revision-commit",
        "after-commit",
    ] {
        let run = Run::new(&format!("P0-CREATE-CRASH-{hook}"));
        let mut child = paused(&run, "project.create", create("project", "original"), hook);
        child.kill().unwrap();
        child.wait().unwrap();
        let retry = run.ok("project.create", create("project", "original"));
        assert_eq!(retry["result"]["revision"], 0);
        assert_eq!(retry["replayed"], hook == "after-commit");
        assert_eq!(run.inspect()["result"]["snapshot"]["clips"], json!([]));
    }
}
#[cfg(feature = "test-hooks")]
#[test]
fn p0_pending_render_recovery() {
    for hook in [
        "after-pending",
        "during-file-write",
        "after-file-flush",
        "after-promotion",
        "after-receipt-commit",
    ] {
        let run = Run::new(&format!("P0-RENDER-RECOVERY-{hook}"));
        run.create();
        run.commit();
        let input = render(0, "original", 1);
        let mut child = paused(&run, "frame.render", input.clone(), hook);
        child.kill().unwrap();
        child.wait().unwrap();
        let retry = run.ok("frame.render", input.clone());
        assert_eq!(retry["replayed"], hook == "after-receipt-commit");
        let receipt = &retry["result"];
        assert_eq!(
            pixels(&run.artifact_path(receipt)).2,
            [12, 25, 48, 160].repeat(6)
        );
        let replay = run.ok("frame.render", input);
        assert_eq!(replay["replayed"], true);
        assert_eq!(replay["result"], retry["result"]);
        let artifacts = run.state.join("project/artifacts");
        let files: Vec<_> = fs::read_dir(artifacts)
            .unwrap()
            .map(|v| v.unwrap().path())
            .collect();
        assert_eq!(files.len(), 1);
        assert_eq!(files[0].extension().unwrap(), "png");
    }
}
#[cfg(all(feature = "test-hooks", unix))]
#[test]
fn p0_cancellation_releases_storage_lock() {
    let run = Run::new("P0-CANCELLATION");
    run.create();
    run.commit();
    let input = render(0, "cancelled", 1);
    let mut child = paused(&run, "frame.render", input.clone(), "during-file-write");
    let error = run.reject(
        "project.commit",
        commit("blocked", 1, vec![put("solid", 0, 4, [5, 4, 3, 2])]),
        "store_busy",
    );
    assert_eq!(error["error"]["retry"], "same_intent_bounded_backoff");
    let status = Command::new("/bin/kill")
        .args(["-TERM", &child.id().to_string()])
        .status()
        .unwrap();
    assert!(status.success());
    assert!(!child.wait().unwrap().success());
    let receipt = run.ok("frame.render", input.clone());
    assert_eq!(receipt["replayed"], false);
    assert_eq!(run.ok("frame.render", input)["replayed"], true);
    run.ok(
        "project.commit",
        commit("blocked", 1, vec![put("solid", 0, 4, [5, 4, 3, 2])]),
    );
    assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 2);
}
#[cfg(feature = "test-hooks")]
#[test]
fn deadline_terminates_work_and_same_intent_recovers() {
    let run = Run::new("P0-WORK-DEADLINE");
    run.create();
    run.commit();
    let ready = run.directory.join("deadline-ready");
    let input = render(0, "deadline", 1);
    let mut child = Command::new(BINARY)
        .args(["call", "--deadline-ms", "100", "--state"])
        .arg(&run.state)
        .env("NATIVE_EDITOR_TEST_HOOK", "during-file-write")
        .env("NATIVE_EDITOR_TEST_READY", &ready)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(&serde_json::to_vec(&run.envelope("frame.render", input.clone())).unwrap())
        .unwrap();
    let (code, response) = decode_output(child.wait_with_output().unwrap());
    assert!(ready.exists());
    assert_eq!(code, 1);
    assert_eq!(response["error"]["code"], "process_timeout");
    assert_eq!(response["requestId"], "acceptance-request");
    let retry = run.ok("frame.render", input);
    assert_eq!(retry["result"]["intentId"], "deadline");
    assert_eq!(
        pixels(&run.artifact_path(&retry["result"])).2,
        [12, 25, 48, 160].repeat(6)
    );
}

#[test]
fn request_context_does_not_change_intent_identity() {
    let run = Run::new("P0-REQUEST-IDENTITY");
    run.create();
    let first = run.commit();
    let input = commit("edit", 0, vec![put("solid", 0, 4, [12, 25, 48, 160])]);
    let mut request = run.envelope("project.commit", input);
    request["requestId"] = "different-correlation".into();
    let (code, response) = run.raw(&serde_json::to_vec(&request).unwrap());
    assert_eq!(code, 0);
    assert_eq!(response["requestId"], "different-correlation");
    assert_eq!(response["replayed"], true);
    assert_eq!(response["result"], first["result"]);
    let frame = render(0, "identity", 1);
    let expected = sha(&canonical(
        &json!({"identityVersion":1,"protocolVersion":1,"tool":"frame.render","input":frame}),
    ));
    assert_eq!(
        run.ok("frame.render", frame)["result"]["artifactId"],
        format!("frame-{}", &expected[..48])
    );
}

#[cfg(not(feature = "test-hooks"))]
#[test]
fn production_binary_ignores_crash_hook_environment() {
    let run = Run::new("P0-PRODUCTION-HOOK-POLICY");
    run.create();
    run.commit();
    let ready = run.directory.join("unexpected-hook");
    let mut child = Command::new(BINARY)
        .args(["call", "--deadline-ms", "1000", "--state"])
        .arg(&run.state)
        .env("NATIVE_EDITOR_TEST_HOOK", "after-pending")
        .env("NATIVE_EDITOR_TEST_READY", &ready)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(
            &serde_json::to_vec(&run.envelope("frame.render", render(0, "production", 1))).unwrap(),
        )
        .unwrap();
    let (code, response) = decode_output(child.wait_with_output().unwrap());
    assert_eq!(code, 0, "{response}");
    assert!(!ready.exists());
}

#[test]
fn storage_failure_exits_one_without_domain_retry() {
    let run = Run::new("P0-STORAGE-FAILURE");
    fs::write(&run.state, b"occupied by a file").unwrap();
    let (code, response) = run.call("project.create", create("project", "create"));
    assert_eq!(code, 1);
    assert_eq!(response["error"]["code"], "storage_failure");
    assert_eq!(response["error"]["retry"], "diagnose_storage");
}

#[test]
fn copied_database_cannot_substitute_project_identity() {
    let run = Run::new("P0-PROJECT-IDENTITY");
    run.create();
    run.commit();
    let receipt = run.render(0, "bound")["result"].clone();
    let target = run.state.join("substitute");
    fs::create_dir(&target).unwrap();
    fs::copy(
        run.state.join("project/project.sqlite3"),
        target.join("project.sqlite3"),
    )
    .unwrap();
    run.reject(
        "project.inspect",
        json!({"projectId":"substitute"}),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "project.create",
        create("substitute", "new-create"),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "project.create",
        create("substitute", "create"),
        "intent_conflict",
    );
    for intent in ["new-edit", "edit"] {
        let mut input = commit(intent, 1, vec![put("solid", 0, 4, [12, 25, 48, 160])]);
        input["projectId"] = "substitute".into();
        let (_, response) = run.call("project.commit", input);
        assert!(matches!(
            response["error"]["code"].as_str(),
            Some("artifact_integrity_mismatch" | "intent_conflict")
        ));
    }
    let mut input = render(0, "other-render", 1);
    input["projectId"] = "substitute".into();
    run.reject("frame.render", input, "artifact_integrity_mismatch");
    run.reject(
        "artifact.verify",
        json!({"projectId":"substitute","artifactId":receipt["artifactId"]}),
        "artifact_integrity_mismatch",
    );
    assert_eq!(run.inspect()["result"]["snapshot"]["projectId"], "project");
}

#[test]
fn unsupported_snapshot_version_fails_before_mutation_or_replay() {
    let run = Run::new("P0-SNAPSHOT-VERSION");
    run.create();
    let database = rusqlite::Connection::open(run.state.join("project/project.sqlite3")).unwrap();
    let mut snapshot = run.inspect()["result"]["snapshot"].clone();
    snapshot["snapshotVersion"] = 2.into();
    database
        .execute(
            "UPDATE revisions SET snapshot=?,hash=? WHERE revision=0",
            rusqlite::params![
                serde_json::to_string(&snapshot).unwrap(),
                sha(&canonical(&snapshot))
            ],
        )
        .unwrap();
    drop(database);
    run.reject(
        "project.inspect",
        json!({"projectId":"project"}),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "project.create",
        create("project", "create"),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "project.commit",
        commit("new", 0, vec![put("solid", 0, 4, [1, 2, 3, 4])]),
        "artifact_integrity_mismatch",
    );
    run.reject(
        "frame.render",
        render(0, "frame", 0),
        "artifact_integrity_mismatch",
    );
}

#[test]
fn completed_intent_must_bind_its_immutable_revision_and_hash() {
    for key in ["projectSha256", "revision"] {
        let run = Run::new(&format!("P0-COMPLETION-BINDING-{key}"));
        run.create();
        run.commit();
        let database =
            rusqlite::Connection::open(run.state.join("project/project.sqlite3")).unwrap();
        let stored: String = database
            .query_row("SELECT result FROM intents WHERE id='edit'", [], |row| {
                row.get(0)
            })
            .unwrap();
        let mut result: Value = serde_json::from_str(&stored).unwrap();
        result["result"][key] = if key == "revision" {
            json!(99)
        } else {
            json!("0".repeat(64))
        };
        database
            .execute(
                "UPDATE intents SET result=? WHERE id='edit'",
                [serde_json::to_string(&result).unwrap()],
            )
            .unwrap();
        drop(database);
        run.reject(
            "project.commit",
            commit("edit", 0, vec![put("solid", 0, 4, [12, 25, 48, 160])]),
            "artifact_integrity_mismatch",
        );
        assert_eq!(run.inspect()["result"]["snapshot"]["revision"], 1);
    }
}

#[test]
fn slow_reader_does_not_truncate_a_selected_response() {
    let run = Run::new("P0-SLOW-READER");
    let mut project = create("project", "create");
    project["timeline"]["durationFrames"] = 5000.into();
    run.ok("project.create", project);
    let edits = (0..4000)
        .map(|i| put(&format!("clip-{i}"), i, 1, [1, 2, 3, 4]))
        .collect();
    run.ok("project.commit", commit("many-clips", 0, edits));
    let deadline_ms = if cfg!(feature = "test-hooks") {
        2_000
    } else {
        30_000
    };
    let deadline_arg = deadline_ms.to_string();
    #[cfg(feature = "test-hooks")]
    let selected = run.directory.join("selected-response");
    let mut command = Command::new(BINARY);
    command
        .args(["call", "--deadline-ms", &deadline_arg, "--state"])
        .arg(&run.state)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(feature = "test-hooks")]
    command
        .env("NATIVE_EDITOR_TEST_HOOK", "after-selection")
        .env("NATIVE_EDITOR_TEST_READY", &selected);
    let mut child = command.spawn().unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(
            &serde_json::to_vec(&run.envelope("project.inspect", json!({"projectId":"project"})))
                .unwrap(),
        )
        .unwrap();
    #[cfg(feature = "test-hooks")]
    let started = Instant::now();
    #[cfg(feature = "test-hooks")]
    while !selected.exists() {
        if let Some(status) = child.try_wait().unwrap() {
            panic!("selected-response hook exited before selection: {status}");
        }
        assert!(
            started.elapsed() < Duration::from_secs(5),
            "selected-response hook did not observe selection"
        );
        std::thread::sleep(Duration::from_millis(5));
    }
    #[cfg(feature = "test-hooks")]
    {
        assert!(
            started.elapsed() < Duration::from_millis(deadline_ms),
            "selected-response hook observed selection after the execution deadline"
        );
        std::thread::sleep(Duration::from_millis(deadline_ms + 100));
    }
    #[cfg(not(feature = "test-hooks"))]
    {
        std::thread::sleep(Duration::from_millis(400));
    }
    assert!(
        child.try_wait().unwrap().is_none(),
        "large response should await its reader"
    );
    let output = child.wait_with_output().unwrap();
    assert!(output.stdout.len() > 64 * 1024);
    let (code, response) = decode_output(output);
    assert_eq!(code, 0);
    assert_eq!(
        response["result"]["snapshot"]["clips"]
            .as_array()
            .unwrap()
            .len(),
        4000
    );
    let child = Command::new(BINARY)
        .args(["progress", "--deadline-ms", "100"])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    std::thread::sleep(Duration::from_millis(200));
    let output = child.wait_with_output().unwrap();
    assert!(output.status.success());
    let progress: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert!(progress["capabilities"].as_array().unwrap().len() > 8);
}
