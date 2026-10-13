# Rust producer runner A02 source review addendum A01

A02 remains frozen, unbuilt, and source-rejected. Root read the complete saved peer review, SHA-256 `ffddc46caa4c3a0a199bb7b60c8b65b13498394a49ce471d2dd7f2e6aa3626ae`.

The peer adds two concrete findings to the four root findings: invalid `ExitStatusExt::code` extraction and missing in-group termination after post-reap pipe-drain expiry. Both are included in A03 repair scope. The peer's missing fixture entrypoint is a planned control gap; A02 documentation already states that the fixtures remain unexecuted. A separate finite source-control binary is being authored.

Root also identified two expressions within the compile finding. `initial_run_entries.as_ref().map(Vec::is_empty)` returns a Result, but A02 compares it with Some(false) and calls is_none(). The two `path_after.as_ref().is_none_or(...)` expressions likewise call an Option method on a Result. A03 must preserve error rejection while correcting these types.

The combined actionable scope is six groups: compile errors, blocking file opens, capture-log ownership, signal delivery facts, regular-file post-read identity, and in-group pipe-writer cleanup. No compiler or control ran during this review. Source-only, native, product, WATCHED, HEARD, and creative boundaries remain unchanged.
