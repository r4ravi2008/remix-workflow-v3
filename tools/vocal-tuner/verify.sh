#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

cargo fmt --check
cargo test
cargo clippy -- -D warnings
cargo run -- --help >/dev/null

