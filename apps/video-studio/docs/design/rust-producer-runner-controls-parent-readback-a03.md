# Rust producer runner A03 controls parent saved-evidence readback

One fixed invocation passed all ten fake-process/file controls with exit 0. The process was reaped in 2.133 seconds, with no timeout or stream overflow. Stdout contains the single 10/10 JSON summary; stderr is empty.

The control binary compiled once with exit 0 and empty compiler logs. The outer runner left a stale reaped boolean after Popen.poll collected exit 0, so its original report falsely recorded compiled=false and skipped execution. The original report is preserved. build-readback-correction-a01.json records the correction. The existing binary was invoked without recompilation using the recipe's exact control-attempt-a03 path.

Root reopened all 96 original inputs totaling 75,524,974 bytes, both assembled sources, the arm64 executable, the control preflight, both streams, and all 71 generated regular files. All 173 rows match their bytes, SHA-256, and nine identity fields. The original compiler report remains unchanged. The retained FIFO was recorded with lstat and never opened.

The ten cases cover unavailable loader, exact argv, preserved nonzero failure, cancellation, log overflow, inherited-pipe group cleanup, replaced producer log, FIFO authority rejection, terminal collision fallback, and double collision preservation. Cancellation and overflow reports record TERM delivery and direct-child reap. The retained overflow log is exactly 4 MiB. The pipe-holder case records group KILL, pipe_drain_timeout, and holder absence before fallback. The single collision report preserves its sentinel and causal terminal_report_name_collision. Both double-collision sentinels remain unchanged.

Root independently checked all eight saved child PIDs and one holder PID absent. The first invocation wrapper's ownedPidAbsence array was empty because its filename filter omitted child-pid.txt and holder-pid.txt. Additive parent-control-readback-a01.json supplies those checks without changing the original invocation report. TMPDIR is empty.

The frozen production loader still returns unavailable. Test-private fake subjects produced these reports. No Rust A05 native producer, native framework, media, GPU, or Resolve process ran. Native acceptance, product integration, WATCHED, HEARD, and creative acceptance remain false. Actual-evidence peer review is pending.
