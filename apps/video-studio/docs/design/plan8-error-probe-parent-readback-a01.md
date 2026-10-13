# Plan8 error probe A01 parent readback

One direct Rust test build exited zero with no compiler output.
One direct pure control invocation exited zero.
All five named controls passed, with zero failures, ignores, or filtered controls.

Root measured the compiled arm64 Mach-O test binary:

- bytes: `996880`;
- SHA-256: `c62a4cf78d434254094eb52845bfd825fa21fcf51051e65de00a6715809e2386`;
- UUID: `2c64c8655a6734a8a19c08835828c454`.

The exact stdout is 418 bytes with SHA-256
`b5cf2c4ecf214d01bbebfcba686dcce4e4587391187f714a2d2c77d8c494b07b`.
Root matched all twelve prelaunch source/tool rows and the current compiled binary.
The postcheck covers eighteen regular files totaling 1,584,139 bytes.
The temporary directory is empty after completion.

The source manifest, exact commands, environments, tool returns, stdout, and postcheck are saved under `plan8-error-probe-a01`.
The source peer review found no P1/P2 within the inline probe scope.
The actual-evidence peer review remains pending.

The first readback checker rejected a result name containing a digit.
The corrected checker matched all five complete names without rerunning the compiler or controls.
No evidence output was written by the stopped checker.

This establishes five pure logical error-probe controls for the saved source.
It does not establish actual layout byte counts, arbitrary formatter allocation behavior, process reaping, or loaded-image identity.
StudioError String construction, ledger accounting, Plan8 routing, and production integration remain unimplemented.
No native text producer, media, GPU, or Resolve action occurred.
Plan8 remains disabled and film listening, viewing, and creative acceptance remain unverified.
