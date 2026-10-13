# Native preparation direct harness A03 failed controls readback

The direct harness compiled with `panic=abort` and Rust thin LTO.
It then aborted on the first assertion before any passed line.
No saved-report control completed.

The prior A06 attempt failed linking fixed LLVM21 dependency bitcode with Apple's LLVM17 linker.
Root preserved that attempt and added `-C lto=thin` in a fresh A07 attempt.
Rust consumed the existing bitcode before the system linker.
The A07 build exited zero. The direct invocation exited with signal 6.

The A07 report is 6,906 bytes with SHA-256
`04ef6b587e1303436d41991f7863d3a4ae813b87e83b0fca161c97079a32d19b`.
All 125 input identities matched. Their bytes total 79,983,171.
Root read the complete abort diagnostic and the closed argv adapter.
The rejection is `tool_argv_value`, observation 2, token 0.

The fixed historical toolchain report records the launcher
`/Users/aira/.cargo/bin/rustc` in that argv position.
The adapter incorrectly expects the resolved stable toolchain executable there.
The report separately records the resolved executable.
A minimal successor must preserve this distinction and the closed argv check.
The frozen report, A03 harness, A04 library, and failed attempts remain preserved.

Successful harness compilation establishes compilation only.
No accepted authority, native producer, loaded code, media, GPU, Resolve,
watched, heard, or creative acceptance occurred.
