use crate::model::*;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fs::{self, OpenOptions};
use std::io::{self, Read, Write};
use std::path::{Path, PathBuf};
pub use std::process::ExitCode;
use std::process::{Command, Stdio};
pub fn pid() -> u32 {
    std::process::id()
}
#[cfg(unix)]
use std::os::unix::process::{CommandExt, ExitStatusExt};
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

pub const LOG_LIMIT: u64 = 8 * 1024 * 1024;
pub fn now() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}
pub struct CommandSpec {
    pub program: String,
    pub args: Vec<String>,
    pub cwd: PathBuf,
    pub environment: BTreeMap<String, String>,
    pub deadline: Duration,
}
pub struct ProcessRunner {
    pub whole_deadline: Instant,
}
fn drain(mut reader: impl Read, path: PathBuf) -> io::Result<CapturedStream> {
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)?;
    let mut hash = Sha256::new();
    let mut observed = 0u64;
    let mut saved = 0u64;
    let mut buffer = [0u8; 8192];
    loop {
        let n = reader.read(&mut buffer)?;
        if n == 0 {
            break;
        }
        observed += n as u64;
        let keep = (LOG_LIMIT - saved).min(n as u64) as usize;
        file.write_all(&buffer[..keep])?;
        hash.update(&buffer[..keep]);
        saved += keep as u64;
    }
    file.sync_all()?;
    Ok(CapturedStream {
        path: path.display().to_string(),
        observed_bytes: observed,
        saved_bytes: saved,
        sha256: format!("{:x}", hash.finalize()),
        truncated: observed > saved,
    })
}
fn empty(path: &Path) -> io::Result<CapturedStream> {
    drain(io::empty(), path.to_owned())
}
pub enum ProcessInput {
    Empty,
    Bytes(Vec<u8>),
    HoldOpen(Duration),
}
fn pause(duration: Duration, cancelled: &AtomicBool) {
    let end = Instant::now() + duration;
    while !cancelled.load(Ordering::Acquire) {
        let remaining = end.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            break;
        }
        thread::sleep(remaining.min(Duration::from_millis(5)));
    }
}
fn wait_for_reader_gate(path: &Path, cancelled: &AtomicBool) {
    while !path.exists() && !cancelled.load(Ordering::Acquire) {
        thread::sleep(Duration::from_millis(5));
    }
}
impl ProcessRunner {
    pub fn run(&self, logs: &Path, name: &str, spec: CommandSpec) -> io::Result<ProcessRecord> {
        self.run_controlled(logs, name, spec, ProcessInput::Empty, Duration::ZERO)
    }
    pub fn run_controlled(
        &self,
        logs: &Path,
        name: &str,
        spec: CommandSpec,
        input: ProcessInput,
        reader_delay: Duration,
    ) -> io::Result<ProcessRecord> {
        fs::create_dir_all(logs)?;
        let out = logs.join(format!("{name}.stdout.log"));
        let err = logs.join(format!("{name}.stderr.log"));
        let start = Instant::now();
        let started_at = now();
        let mut argv = vec![spec.program.clone()];
        argv.extend(spec.args.clone());
        let mut selected_environment = spec.environment.clone();
        for key in ["PATH", "CARGO_HOME", "RUSTUP_HOME", "RUSTUP_TOOLCHAIN"] {
            if let Ok(value) = std::env::var(key) {
                selected_environment.entry(key.into()).or_insert(value);
            }
        }
        let mut record = ProcessRecord {
            argv,
            cwd: spec.cwd.display().to_string(),
            selected_environment,
            started_at,
            duration_ms: 0,
            exit: ProcessExit::UnsupportedPlatform,
            stdout: empty(&out)?,
            stderr: empty(&err)?,
        };
        if !cfg!(unix) {
            return Ok(record);
        }
        if start >= self.whole_deadline {
            record.exit = ProcessExit::TimedOut;
            return Ok(record);
        }
        fs::remove_file(&out)?;
        fs::remove_file(&err)?;
        let mut command = Command::new(&spec.program);
        command
            .args(&spec.args)
            .current_dir(&spec.cwd)
            .stdin(if matches!(input, ProcessInput::Empty) {
                Stdio::null()
            } else {
                Stdio::piped()
            })
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        for (key, _) in std::env::vars_os() {
            let key_text = key.to_string_lossy();
            if key_text.starts_with("NATIVE_EDITOR_")
                || key_text.starts_with("CARGO_TARGET_")
                || key_text.starts_with("CARGO_PROFILE_")
                || key_text.starts_with("CARGO_BUILD_")
                || (key_text.starts_with("RUST") && !key_text.starts_with("RUSTUP_"))
                || ["CC", "CFLAGS", "CXX", "CXXFLAGS", "AR", "RANLIB", "LDFLAGS"]
                    .iter()
                    .any(|prefix| {
                        key_text == *prefix || key_text.starts_with(&format!("{prefix}_"))
                    })
                || key_text.starts_with("PKG_CONFIG_")
                || matches!(
                    key_text.as_ref(),
                    "CARGO_ENCODED_RUSTFLAGS" | "CARGO_TARGET_DIR"
                )
            {
                command.env_remove(key);
            }
        }
        command.envs(&spec.environment);
        #[cfg(unix)]
        command.process_group(0);
        let mut child = match command.spawn() {
            Ok(child) => child,
            Err(error) => {
                record.exit = ProcessExit::SpawnFailed {
                    error: error.to_string(),
                };
                record.stdout = empty(&out)?;
                record.stderr = empty(&err)?;
                return Ok(record);
            }
        };
        let cancelled = Arc::new(AtomicBool::new(false));
        let input_cancelled = cancelled.clone();
        let input_thread = child.stdin.take().map(|mut stdin| {
            thread::spawn(move || match input {
                ProcessInput::Empty => Ok(()),
                ProcessInput::Bytes(bytes) => stdin.write_all(&bytes),
                ProcessInput::HoldOpen(duration) => {
                    pause(duration, &input_cancelled);
                    Ok(())
                }
            })
        });
        let stdout = child
            .stdout
            .take()
            .ok_or_else(|| io::Error::other("missing stdout"))?;
        let stderr = child
            .stderr
            .take()
            .ok_or_else(|| io::Error::other("missing stderr"))?;
        let reader_gate = spec
            .environment
            .get("NATIVE_EDITOR_READER_GATE")
            .map(PathBuf::from);
        let reader_cancelled = cancelled.clone();
        let out_thread = thread::spawn(move || {
            if let Some(path) = reader_gate.as_ref() {
                wait_for_reader_gate(path, &reader_cancelled);
            }
            pause(reader_delay, &reader_cancelled);
            drain(stdout, out)
        });
        let err_thread = thread::spawn(move || drain(stderr, err));
        let deadline = (start + spec.deadline).min(self.whole_deadline);
        let status = loop {
            if let Some(status) = child.try_wait()? {
                break Some(status);
            }
            if Instant::now() >= deadline {
                break None;
            }
            thread::sleep(Duration::from_millis(10));
        };
        // Kill the group even after its leader exits, because descendants may retain pipe writers.
        #[cfg(unix)]
        unsafe {
            libc::kill(-(child.id() as i32), libc::SIGKILL);
        }
        cancelled.store(true, Ordering::Release);
        record.exit = match status {
            None => {
                child.wait()?;
                ProcessExit::TimedOut
            }
            Some(status) => match status.code() {
                Some(code) => ProcessExit::Code { code },
                None => {
                    #[cfg(unix)]
                    {
                        ProcessExit::Signal {
                            signal: status.signal().unwrap_or(0),
                        }
                    }
                    #[cfg(not(unix))]
                    {
                        ProcessExit::Signal { signal: 0 }
                    }
                }
            },
        };
        if let Some(input_thread) = input_thread {
            let _ = input_thread
                .join()
                .map_err(|_| io::Error::other("stdin writer panic"))?;
        }
        record.stdout = out_thread
            .join()
            .map_err(|_| io::Error::other("stdout drain panic"))??;
        record.stderr = err_thread
            .join()
            .map_err(|_| io::Error::other("stderr drain panic"))??;
        record.duration_ms = start.elapsed().as_millis();
        Ok(record)
    }
}
pub fn outcome(record: &ProcessRecord) -> CheckOutcome {
    if record.stdout.truncated || record.stderr.truncated {
        return CheckOutcome::Incomplete {
            reason: IncompleteReason::OutputLimitExceeded {
                limit_bytes: LOG_LIMIT,
            },
        };
    }
    match &record.exit {
        ProcessExit::Code { code: 0 } => CheckOutcome::Passed,
        ProcessExit::TimedOut => CheckOutcome::Incomplete {
            reason: IncompleteReason::TimedOut {
                deadline_ms: record.duration_ms as u64,
            },
        },
        ProcessExit::UnsupportedPlatform => CheckOutcome::Incomplete {
            reason: IncompleteReason::UnsupportedPlatform {
                detail: "Unix process groups required before any child work".into(),
            },
        },
        ProcessExit::SpawnFailed { error } => CheckOutcome::Incomplete {
            reason: IncompleteReason::MissingTool {
                tool: format!("{}: {error}", record.argv[0]),
            },
        },
        _ => CheckOutcome::violations(vec![Violation::new(
            "process-exit",
            None,
            format!("Command failed: {:?}", record.exit),
        )]),
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn logs() -> PathBuf {
        let p = std::env::temp_dir().join(format!(
            "devcheck-process-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&p).unwrap();
        p
    }
    #[test]
    fn timeout_flood_and_descendant_are_bounded() {
        let logs = logs();
        let runner = ProcessRunner {
            whole_deadline: Instant::now() + Duration::from_secs(10),
        };
        let flood = runner.run(&logs,"flood",CommandSpec {program:"/usr/bin/python3".into(),args:vec!["-c".into(),"import os;\nfor i in range(2000): os.write(1,b'x'*8192); os.write(2,b'y'*8192)".into()],cwd:logs.clone(),environment:BTreeMap::new(),deadline:Duration::from_secs(5)}).unwrap();
        assert!(matches!(flood.exit, ProcessExit::Code { code: 0 }));
        for stream in [&flood.stdout, &flood.stderr] {
            assert_eq!(stream.observed_bytes, 2000 * 8192);
            assert!(stream.observed_bytes > LOG_LIMIT && stream.truncated);
            assert_eq!(stream.saved_bytes, LOG_LIMIT);
            assert_eq!(fs::metadata(&stream.path).unwrap().len(), LOG_LIMIT);
            assert_eq!(
                crate::evidence::sha(&fs::read(&stream.path).unwrap()),
                stream.sha256
            );
        }
        let timeout = runner
            .run(
                &logs,
                "timeout",
                CommandSpec {
                    program: "/usr/bin/python3".into(),
                    args: vec![
                        "-c".into(),
                        "import os,time; os.fork(); time.sleep(20)".into(),
                    ],
                    cwd: logs.clone(),
                    environment: BTreeMap::new(),
                    deadline: Duration::from_millis(400),
                },
            )
            .unwrap();
        assert!(matches!(timeout.exit, ProcessExit::TimedOut));
        assert!(timeout.duration_ms < 2000);
    }

    #[test]
    fn controlled_waits_end_at_process_deadline() {
        let logs = logs();
        let runner = ProcessRunner {
            whole_deadline: Instant::now() + Duration::from_millis(100),
        };
        let record = runner
            .run_controlled(
                &logs,
                "controlled",
                CommandSpec {
                    program: "/usr/bin/python3".into(),
                    args: vec!["-c".into(), "import time; time.sleep(10)".into()],
                    cwd: logs.clone(),
                    environment: BTreeMap::new(),
                    deadline: Duration::from_millis(100),
                },
                ProcessInput::HoldOpen(Duration::from_secs(10)),
                Duration::from_secs(10),
            )
            .unwrap();
        assert!(matches!(record.exit, ProcessExit::TimedOut));
        assert!(record.duration_ms < 1000);
    }
    #[test]
    fn reader_gate_starts_delay_after_selection_marker() {
        let logs = logs();
        let gate = logs.join("selected");
        let record = ProcessRunner {
            whole_deadline: Instant::now() + Duration::from_secs(5),
        }
        .run_controlled(
            &logs,
            "reader-gate",
            CommandSpec {
                program: "/usr/bin/python3".into(),
                args: vec![
                    "-c".into(),
                    "import pathlib,sys,time; time.sleep(.2); pathlib.Path(sys.argv[1]).write_text('selected'); sys.stdout.write('x'*100000); sys.stdout.flush()".into(),
                    gate.display().to_string(),
                ],
                cwd: logs.clone(),
                environment: BTreeMap::from([(String::from("NATIVE_EDITOR_READER_GATE"), gate.display().to_string())]),
                deadline: Duration::from_secs(2),
            },
            ProcessInput::Empty,
            Duration::from_millis(300),
        )
        .unwrap();
        assert!(matches!(record.exit, ProcessExit::Code { code: 0 }));
        assert!(gate.exists());
        assert_eq!(record.stdout.observed_bytes, 100000);
        assert!(!record.stdout.truncated);
        assert!(
            record.duration_ms >= 450,
            "reader delay began before selection: {}ms",
            record.duration_ms
        );
    }
    #[test]
    fn exited_leader_cannot_leave_pipe_descendant() {
        let logs = logs();
        let r = ProcessRunner {
            whole_deadline: Instant::now() + Duration::from_secs(5),
        }
        .run(
            &logs,
            "descendant",
            CommandSpec {
                program: "/usr/bin/python3".into(),
                args: vec![
                    "-c".into(),
                    "import os,time; p=os.fork();\nif p==0: time.sleep(20)".into(),
                ],
                cwd: logs.clone(),
                environment: BTreeMap::new(),
                deadline: Duration::from_secs(1),
            },
        )
        .unwrap();
        assert!(matches!(r.exit, ProcessExit::Code { code: 0 }));
        assert!(r.duration_ms < 2000);
    }
}
