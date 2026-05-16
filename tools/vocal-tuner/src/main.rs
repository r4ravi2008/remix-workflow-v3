use std::process;

fn main() {
    if let Err(err) = vocal_tuner::cli::run() {
        eprintln!("vocal-tuner: {err}");
        process::exit(1);
    }
}
