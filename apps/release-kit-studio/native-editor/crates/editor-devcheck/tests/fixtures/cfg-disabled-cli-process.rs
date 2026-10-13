#[cfg(any())]
mod side {
    use std::process as p;
    fn launch() { p::Command::new("sh"); }
}
