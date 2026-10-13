#![forbid(unsafe_code)]

mod protocol;

use editor_core::*;
use protocol::{Registry, Request, Response};
use serde_json::{json, Value};
use std::fs;
use std::io::{Read, Write};
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Duration;

#[derive(Clone)]
struct Context {
    request_id: Option<RequestId>,
    schema_sha256: String,
}
struct Arguments {
    positional: Vec<String>,
    state: Option<PathBuf>,
    deadline_ms: u64,
}
impl Arguments {
    fn parse() -> Result<Self, EditorError> {
        let mut args = std::env::args().skip(1);
        let mut parsed = Self {
            positional: vec![],
            state: None,
            deadline_ms: 30_000,
        };
        let mut deadline_seen = false;
        while let Some(arg) = args.next() {
            match arg.as_str() {
                "--state" => {
                    if parsed.state.is_some() {
                        return Err(EditorError::invalid("Duplicate --state option."));
                    }
                    parsed.state = Some(
                        args.next()
                            .ok_or_else(|| EditorError::invalid("--state requires a directory."))?
                            .into(),
                    );
                }
                "--deadline-ms" => {
                    if deadline_seen {
                        return Err(EditorError::invalid("Duplicate --deadline-ms option."));
                    }
                    deadline_seen = true;
                    parsed.deadline_ms = args
                        .next()
                        .ok_or_else(|| EditorError::invalid("--deadline-ms requires an integer."))?
                        .parse()
                        .map_err(|_| EditorError::invalid("Invalid deadline."))?;
                    if !(1..=30_000).contains(&parsed.deadline_ms) {
                        return Err(EditorError::invalid(
                            "Deadline must be 1..30000 milliseconds.",
                        ));
                    }
                }
                flag if flag.starts_with('-') => {
                    return Err(EditorError::invalid("Unknown CLI option."))
                }
                _ => parsed.positional.push(arg),
            }
        }
        Ok(parsed)
    }
    fn state(&self) -> Result<&PathBuf, EditorError> {
        self.state
            .as_ref()
            .ok_or_else(|| EditorError::invalid("This command requires --state <directory>."))
    }
}
fn error_response(error: &EditorError, context: &Context) -> Value {
    serde_json::to_value(Response::<Value>::Error {
        protocol_version: 1,
        request_id: context.request_id.clone().into(),
        schema_sha256: context.schema_sha256.clone(),
        error: error.clone(),
    })
    .expect("error serializes")
}
fn emit(value: &Value) -> Result<(), EditorError> {
    let bytes = serde_json::to_vec(value)?;
    if bytes.len() > Limits::p0().output_bytes {
        return Err(EditorError::new(
            ErrorCode::InternalFailure,
            "Response exceeds 4 MiB.",
        ));
    }
    let mut stdout = std::io::stdout().lock();
    stdout.write_all(&bytes)?;
    stdout.write_all(b"\n")?;
    stdout.flush()?;
    Ok(())
}
fn bounded_read(mut reader: impl Read) -> Result<Vec<u8>, EditorError> {
    let mut bytes = Vec::new();
    reader
        .by_ref()
        .take(Limits::p0().input_bytes as u64 + 1)
        .read_to_end(&mut bytes)?;
    if bytes.len() > Limits::p0().input_bytes {
        return Err(EditorError::invalid("Request exceeds 1 MiB."));
    }
    Ok(bytes)
}
#[cfg(feature = "test-hooks")]
fn observe_selected_response() {
    if std::env::var("NATIVE_EDITOR_TEST_HOOK").as_deref() == Ok("after-selection") {
        if let Ok(path) = std::env::var("NATIVE_EDITOR_TEST_READY") {
            let _ = fs::write(path, b"after-selection");
        }
    }
}
#[cfg(not(feature = "test-hooks"))]
fn observe_selected_response() {}
fn editor(state: &PathBuf, binary_sha256: &str) -> Result<Editor, EditorError> {
    Editor::open(
        state,
        EditorConfig {
            limits: Limits::p0(),
            binary_sha256: binary_sha256.into(),
        },
    )
}
fn execute_request(
    request: Request<Value>,
    args: &Arguments,
    registry: &Registry,
    binary_sha256: &str,
    context: &Arc<Mutex<Context>>,
) -> Result<Value, EditorError> {
    context.lock().expect("context lock").request_id = Some(request.request_id.clone());
    if request.protocol_version != 1 {
        return Err(EditorError::new(
            ErrorCode::ProtocolMismatch,
            "Protocol version differs from version 1.",
        ));
    }
    if request.tool == "engine.capabilities" {
        if request.expected_schema_sha256.is_some() {
            return Err(EditorError::new(
                ErrorCode::ProtocolMismatch,
                "Initial discovery requires a null schema hash.",
            ));
        }
        let _: protocol::Empty = protocol::decode(request.input)?;
        return success(
            serde_json::to_value(registry.capabilities(binary_sha256))?,
            false,
            &context.lock().expect("context lock"),
        );
    }
    if request.expected_schema_sha256.as_deref() != Some(&registry.schema_sha256) {
        return Err(EditorError::new(
            ErrorCode::ProtocolMismatch,
            "Schema hash differs from the compiled contract.",
        ));
    }
    if !registry.schemas.contains_key(&request.tool) {
        return Err(protocol::tool_error(&request.tool));
    }
    let command = protocol::command(&request.tool, request.input)?;
    let execution = editor(args.state()?, binary_sha256)?.execute(command)?;
    let result = result_value(execution.result)?;
    success(
        result,
        execution.replayed,
        &context.lock().expect("context lock"),
    )
}
fn result_value(result: CommandResult) -> Result<Value, EditorError> {
    Ok(match result {
        CommandResult::Project(v) => serde_json::to_value(v)?,
        CommandResult::Inspection(v) => serde_json::to_value(v)?,
        CommandResult::Artifact(v) => serde_json::to_value(v)?,
        CommandResult::Verification(v) => serde_json::to_value(v)?,
    })
}
fn success(result: Value, replayed: bool, context: &Context) -> Result<Value, EditorError> {
    Ok(serde_json::to_value(Response::Success {
        protocol_version: 1,
        request_id: context
            .request_id
            .clone()
            .expect("successful request has correlation"),
        schema_sha256: context.schema_sha256.clone(),
        replayed,
        result,
    })?)
}
fn run(
    args: &Arguments,
    registry: &Registry,
    binary_sha256: &str,
    context: &Arc<Mutex<Context>>,
) -> Result<Value, EditorError> {
    let operation = args
        .positional
        .first()
        .map(String::as_str)
        .unwrap_or_default();
    match operation {
        "tools" if args.positional.len() == 1 => {
            Ok(serde_json::to_value(registry.capabilities(binary_sha256))?)
        }
        "schema" if args.positional.len() == 2 => {
            let tool = &args.positional[1];
            let schema = registry
                .schemas
                .get(tool)
                .ok_or_else(|| protocol::tool_error(tool))?;
            Ok(
                json!({"protocolVersion":1,"schemaSha256":registry.schema_sha256,"tool":tool,"inputSchema":schema.input_schema,"outputSchema":schema.output_schema,"envelopeSchema":schemars::schema_for!(Request<Value>)}),
            )
        }
        "progress" if args.positional.len() == 1 => Ok(protocol::progress(binary_sha256, registry)),
        "call" => {
            let request = if args.positional.len() == 1 {
                protocol::decode(protocol::parse(&bounded_read(std::io::stdin().lock())?)?)?
            } else if args.positional.len() == 3 {
                let tool = args.positional[1].clone();
                let input = protocol::parse(&bounded_read(fs::File::open(&args.positional[2])?)?)?;
                Request {
                    protocol_version: 1,
                    request_id: RequestId::new("cli-call")?,
                    expected_schema_sha256: (if tool == "engine.capabilities" {
                        None
                    } else {
                        Some(registry.schema_sha256.clone())
                    })
                    .into(),
                    tool,
                    input,
                }
            } else {
                return Err(EditorError::invalid("Use call --state <directory>, or call <tool> <input.json> --state <directory>."));
            };
            execute_request(request, args, registry, binary_sha256, context)
        }
        "verify" if args.positional.len() == 3 => {
            let input = VerifyArtifact {
                project_id: ProjectId::new(args.positional[1].clone())?,
                artifact_id: ArtifactId::new(args.positional[2].clone())?,
            };
            let request = Request {
                protocol_version: 1,
                request_id: RequestId::new("cli-verify")?,
                expected_schema_sha256: Some(registry.schema_sha256.clone()).into(),
                tool: "artifact.verify".into(),
                input: serde_json::to_value(input)?,
            };
            execute_request(request, args, registry, binary_sha256, context)
        }
        "demo" if args.positional.len() == 2 => {
            demo(PathBuf::from(&args.positional[1]), binary_sha256)
        }
        _ => Err(EditorError::invalid(
            "Use tools, schema <tool>, progress, call, verify, or demo <new-directory>.",
        )),
    }
}
fn demo(path: PathBuf, binary_sha256: &str) -> Result<Value, EditorError> {
    let state = path.join("state");
    let editor = editor(&state, binary_sha256)?;
    if path.exists() {
        return Err(EditorError::invalid("Demo requires a new directory."));
    }
    let create = CreateProject {
        project_id: ProjectId::new("native-demo")?,
        intent_id: IntentId::new("create-v1")?,
        name: "Native RGBA example".into(),
        timeline: Timeline {
            frame_rate: FrameRate::new(30000, 1001)?,
            duration_frames: FrameCount::new(60)?,
            canvas: Canvas {
                width: 16,
                height: 12,
            },
        },
    };
    let commit = CommitProject {
        project_id: create.project_id.clone(),
        expected_revision: Revision::new(0)?,
        intent_id: IntentId::new("background-v1")?,
        edits: vec![Edit::PutClip {
            clip: Clip {
                id: ClipId::new("background")?,
                start_frame: FrameIndex::new(0)?,
                duration_frames: FrameCount::new(60)?,
                source: VisualSource::Solid {
                    rgba: [12, 25, 48, 160],
                },
            },
        }],
    };
    let render = RenderFrame {
        project_id: create.project_id.clone(),
        revision: Revision::new(1)?,
        intent_id: IntentId::new("frame-zero-v1")?,
        frame: FrameIndex::new(0)?,
        format: FrameFormat::PngRgba8,
    };
    editor.execute(Command::CreateProject(create.clone()))?;
    editor.execute(Command::CommitProject(commit.clone()))?;
    let rendered = editor.execute(Command::RenderFrame(render.clone()))?;
    let CommandResult::Artifact(receipt) = rendered.result else {
        return Err(EditorError::new(
            ErrorCode::InternalFailure,
            "Unexpected render result.",
        ));
    };
    let verified = editor.execute(Command::VerifyArtifact(VerifyArtifact {
        project_id: create.project_id.clone(),
        artifact_id: receipt.artifact_id.clone(),
    }))?;
    for (name, value) in [
        ("create.json", serde_json::to_value(&create)?),
        ("commit.json", serde_json::to_value(&commit)?),
        ("render.json", serde_json::to_value(&render)?),
        ("receipt.json", serde_json::to_value(&receipt)?),
    ] {
        fs::write(path.join(name), serde_json::to_vec_pretty(&value)?)?;
    }
    let preview = fs::canonicalize(state.join(receipt.project_id.as_str()).join(&receipt.path))?;
    Ok(
        json!({"demoDirectory":fs::canonicalize(path)?,"preview":preview,"receipt":receipt,"verification":result_value(verified.result)?,"review":"Measured PNG only. Creative review remains open."}),
    )
}
fn main() {
    let registry = match Registry::new() {
        Ok(v) => v,
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(1);
        }
    };
    let context = Arc::new(Mutex::new(Context {
        request_id: None,
        schema_sha256: registry.schema_sha256.clone(),
    }));
    let startup = (|| -> Result<_, EditorError> {
        Ok((
            Arguments::parse()?,
            sha256(&fs::read(std::env::current_exe()?)?),
        ))
    })();
    let (args, binary_sha256) = match startup {
        Ok(v) => v,
        Err(error) => {
            let _ = emit(&error_response(
                &error,
                &context.lock().expect("context lock"),
            ));
            std::process::exit(error.exit_code());
        }
    };
    let terminal = Arc::new(AtomicBool::new(false));
    let watchdog_terminal = Arc::clone(&terminal);
    let watchdog_context = Arc::clone(&context);
    let deadline_ms = args.deadline_ms;
    std::thread::spawn(move || {
        std::thread::sleep(Duration::from_millis(deadline_ms));
        if watchdog_terminal
            .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
            .is_ok()
        {
            let error = EditorError::new(
                ErrorCode::ProcessTimeout,
                "Native request exceeded its bounded deadline.",
            );
            let snapshot = watchdog_context.lock().expect("context lock").clone();
            let _ = emit(&error_response(&error, &snapshot));
            std::process::exit(1);
        }
    });
    let (value, code) = match run(&args, &registry, &binary_sha256, &context) {
        Ok(value) => (value, 0),
        Err(error) => (
            error_response(&error, &context.lock().expect("context lock")),
            error.exit_code(),
        ),
    };
    if terminal
        .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
        .is_err()
    {
        loop {
            std::thread::park();
        }
    }
    observe_selected_response();
    if let Err(error) = emit(&value) {
        eprintln!("Failed to write the native response: {error}");
        std::process::exit(1);
    }
    std::process::exit(code);
}
