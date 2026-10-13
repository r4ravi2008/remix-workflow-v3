# Local network GPU through Herdr

Load the installed `herdr` skill before any Herdr control. Check for a real Herdr-managed caller (`HERDR_ENV=1`). If absent, connect to the existing session instead of stopping: inspect `herdr status`, `herdr session list --json`, and `herdr machine list --json` from a terminal, then attach to the existing local session or select the enabled remote machine with `herdr --machine <label-or-id>`. Work inside an existing managed agent or available shell pane, and verify `HERDR_ENV=1` there. Connecting does not set that variable in the outside caller; never set it manually or control an unqualified focused pane from outside.

Discover the installed CLI with `herdr --help` and relevant command-group help. List saved machines and select the exact enabled label/ID. Use that same `--machine <id>` prefix for every remote discovery/read/control command; `herdr status` describes only the local server. A host nickname in an old trace, local `w1:p1`, or last week's `w2:p8` is not a current remote identity.

Inspect remote workspace/pane/agent lists and the existing worker's state/output. Verify actual GPU/VRAM, runtime version, listening service/port, active queue and run directory before changing anything. Reuse the healthy runtime and current owned job. Do not restart Herdr, kill a session, reinstall a working model stack or send a command into a busy foreground process because an observation timed out.

Use the agent surface for a recognized existing agent when the user authorized that coordination; use the pane surface for an available shell. Read current CLI syntax rather than copying opaque IDs or commands from this reference. Prompts should identify exact shot IDs, snapshot hashes, workflow settings, output directory, resource constraints and completion evidence. Submission success only proves input was sent. On `agent_prompt_stalled`, timeout, unknown, or target-not-found, rediscover/get/read first; inspect queue, receipt and filesystem before resending. Do not answer another agent's approval dialog automatically.

## Transfer from the authoritative machine

An observed Urvashi failure exposed an old 55-entry catalog through WSL `/mnt/c` while the Mac's selected catalog had 47 current anchors. Those historical counts are examples, not expected values.

Create a run-specific snapshot on the authoritative host. Stage it in a new remote run directory using an authorized transfer channel, preferably a verified native filesystem for active inference. Run the same snapshot verification there; compare catalog IDs, physical file count, bytes and hashes, then check the workflow's actual load-image paths against those files. Stop on mismatches. Never merge stale files by basename or infer synchronization from a mounted path.

Keep generation metadata on the execution host and copy each completed original plus its receipt/graph/history back promptly. Verify bytes and SHA-256 after the transfer. Preserve failed originals and generated-vs-derived provenance. A local network worker has no rental bill by default, but it can still be shared: do not clear its queue or stop another owner's process.
