# Swift runner A03 source controls: parent readback

The reviewed source-control script ran once through the bundled Python interpreter with an empty inherited environment. It called the actual capture machine through fake process, selector, clock, pipe, signal, and wait implementations. The rejecting `subprocess.Popen` sentinel was installed before runner module execution. No compiled Swift binary ran.

The process exited with status 1. The exclusive result file contains 54 cases: 53 passed and one failed.

| Evidence | SHA-256 |
| --- | --- |
| Reviewed source-control script A03 | `518799ff5379700c01d6b0bd643f1559f7c40d119b29f63206f5f2ec01b38a08` |
| Reviewed runner A03 | `d0d89138412caa6760a72ceb41bea24d61ca2b5a74eb9dc00e83b8eadc3e990c` |
| Source-control readiness | `f966fc1b09b059d5ca445804e50e2df4f96032b97ed5f81b91247e7d327c0467` |
| Result, 6,360 bytes | `3e9226bad76e75de439770dfb989272d2095c0b92ea4450dabc2bc6070c22f85` |
| Current Python file, 18,058,560 bytes | `4158f03e1bae2b759f25a1ba1fbdab8bfb7161eba4caf22e28f0915986625bbc` |

The failing case is `held-binary-path-replacement-detected`. It reports `ControlFailure: held binary descriptor changed`.

The control renames the held binary before replacing its original pathname. It requires `descriptorMatchedBefore=true`. That equality includes metadata such as ctime. A rename can change ctime while preserving the held inode and its original bytes. The assertion therefore exceeds the control's necessary replacement-detection obligation.

Preserve the A03 result and source. A new control revision must verify original retained bytes, UUID, inode, and other unchanged identity fields. It must compare the metadata-derived equality truthfully and require detection of the replacement pathname. Production drift rejection must retain its full metadata checks.

The gate for four compiled controls remains unmet. The native producer, duplicate PNG control, CoreText, ImageIO, GPU, Resolve, playback, hearing, and creative acceptance remain unverified. Interpreter and dependency file observations do not attest loaded images.

The earlier notes' `ac60...` Python hash was stale. The actual saved Swift build report contains the current `4158...` hash. The readiness readback confirmed that match; no build evidence was rewritten.
