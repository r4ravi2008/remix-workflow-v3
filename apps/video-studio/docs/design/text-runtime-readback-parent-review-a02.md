# Runtime snapshot readback A02 parent source review

Disposition: rejected before execution. The parent read all 451 source lines.

The reviewed source is `readback_runtime_snapshot_a02_parent.py`, 25,593 bytes,
SHA-256 `660b4871aab6381ceb3ae3905749f9fd9b99a51dc076e9eb7bb514198aa7e093`.
The source remains preserved. No readback attempt was made.

## P1: interpreter invocation compared with script arguments

Lines 24 and 197 compare `[python3, -I, -B, script]` with `sys.argv`.
CPython supplies `[script]` in `sys.argv` for this invocation. The fixed
readback therefore fails before checking the saved snapshot. Record and check
`sys.orig_argv` for the interpreter command. Separately check script arguments
through `sys.argv`. Preserve both fields in reader evidence.

## P2: new preflight and historical execution facts are mixed

Lines 212–213 require `attemptAbsent=true` in a newly created reader preflight,
although the A09 snapshot attempt already exists. Lines 424–427 publish the
snapshot tool's exit code and captured output without binding its execution
receipt. Separate current reader preflight facts from historical A09 preflight
and execution evidence. Bind any historical receipt before reporting its facts.

The explicit non-assert checks, bounded stable preflight read, exact seven-row
source set, separate reader-source binding, and identity-bearing source rows
address the earlier A01 defects in source. They remain unexecuted.

The saved A09 snapshot remains complete and unqualified. Its readback acceptance
is pending. This review establishes no native, comparator, media, playback,
hearing, or creative result.
