mod evidence;
mod intent;
mod model;
mod policy;
mod process;
mod run;

fn main() -> process::ExitCode {
    let args: Vec<_> = std::env::args_os().skip(1).collect();
    let mode = match args.as_slice() {
        [arg] if arg == "architecture" => model::VerificationMode::Architecture,
        [arg] if arg == "full" => model::VerificationMode::Full,
        _ => {
            eprintln!("Use native-editor-check architecture|full from native-editor.");
            return process::ExitCode::from(64);
        }
    };
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .parent()
        .unwrap();
    if !std::env::current_dir().is_ok_and(|cwd| cwd == root) {
        eprintln!("Run native-editor-check from native-editor.");
        return process::ExitCode::from(64);
    }
    match run::Verifier::open(root).and_then(|v| v.run(mode)) {
        Ok(completed) => {
            println!("{}", completed.summary);
            process::ExitCode::from(completed.exit)
        }
        Err(error) => {
            eprintln!("Verification incomplete: {error}");
            println!(
                "{}",
                serde_json::json!({"verdict":"incomplete","error":error.to_string()})
            );
            process::ExitCode::from(2)
        }
    }
}
