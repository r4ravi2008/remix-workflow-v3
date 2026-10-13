# Tailscale generation and local Resolve pilot

This guide records the earlier Tailscale and local Resolve pilot. It does not describe the standalone Rust editor.

The frontend runs on Cloudflare. Pal Pal's footage generation uses the configured RTX workstation over Tailscale. Editing and rendering use Resolve Studio on the local Mac. No cloud GPU rental or Windows Resolve installation is needed.

Preserve the healthy shared ComfyUI server. Reserve GPU generation and Mac Resolve independently.

## Verified route

- Saved Herdr machine: `WSL box.`. Available shell `w3:p7` in `/home/r4ravi2008/projects/remix-workflow-v3`, with real `HERDR_ENV=1`.
- Tailscale SSH target: `r4ravi2008@rkwindows11-1`, which resolves to `rkwsl-ubuntu.taile19ad1.ts.net`. WSL hostname: `rkwindows11`.
- GPU: RTX 4070 Ti, 12,282 MiB. WSL GPU query executable: `/usr/lib/wsl/lib/nvidia-smi`.
- ComfyUI: `127.0.0.1:8188`. Keep it private and preserve other owners' jobs.
- Shared reservation: `runs/.gpu-inference-lease.json`, acquired exclusively and released after the owned job is terminal.
- Run directory: `runs/pal-pal-release-kit-01a0ff81-r01` on the native WSL filesystem. Verify the frozen snapshot there. Do not use an old mounted iCloud catalog.

Rediscover pane IDs, queue state and reservations before later runs.

## Local Mac Resolve

The user clarified that Resolve is installed locally on the Mac. Live native MCP readback identifies **DaVinci Resolve Studio 21.1.0.17** on `airas-MacBook-Pro.local`. The scripting connection works. No license key was read or recorded.

1. Before any change, examine the current Resolve project, owner, and render state.

2. Before you switch projects, save the current project.

3. Export its checkpoint.

4. Use the local scripting connection and the installed 21.1 SDK.

   Network scripting is unnecessary.

5. Keep keys out of chat, manifests, logs, images, and source control.

6. Transfer exact generated originals from the remote run to the Mac.

7. Before media import, compare the hashes.

8. Keep the canonical WAV unchanged.

9. Use a separate project: `PAL PAL - RELEASE KIT PILOT - R01`, project ID `bb1161d8-9a0b-459a-b4a6-fecabd72a7c8`.

   Diagnostic timeline IDs and exact artifacts belong in the external workspace's `resolve-local/` records.

10. Verify exported pixels and audio, not just the render queue.

    Fusion effects visible in a node viewer must also appear in the delivered file.

11. Keep failed export attempts and their reasons.

The included `resolve_preflight.py` is an earlier NVIDIA-host preflight. It requires a GPU query. Do not treat it as proof of Mac readiness.

This Mac pilot uses live native Resolve API readback plus filesystem hashes and export verification. A production Mac agent needs its own host-appropriate capability probe.

Two isolated layouts were exported at 1920×1080, 24 fps, 93 frames / 3.875 seconds. Version `v04` is the current review candidate. Both files fully decode. The reviewer inspected their Telugu layers in first/middle/last frames.

Decoded audio has 0.999813 cosine similarity to the unchanged canonical PCM excerpt at zero offset. Earlier `v01`–`v03` exports omitted Fusion layers and remain rejected evidence.

The repair reconnected MediaOut inside an undo transaction and saved/reloaded the project. These actions restored the layers in Edit and in `v04`. The individual contributions of those actions were not isolated.

Normal-speed watching, listening, candidate acceptance and the six full-kit outputs remain pending. The operator released the run-owned Mac reservation after saved-project and terminal-render readback.

## Production and delivery gates

Both execution hosts must save submission intents, preserve attempts, serialize ownership and checkpoint asset/project/timeline IDs. Plan native-script lyrics and environment music response against the exact WAV. Vertical edits require their own compositions. The short local diagnostic uses editable Kohinoor Telugu Text+ layers and a measured RMS envelope that drives masked scene lights.

It does not establish full-song lyric sync or a beat grid.

The pilot first proves one representative scene through generated footage, Resolve lyric/motion composition, encoding, transfer, hash/decode checks and picture/audio review. Only reviewed pilot footage can expand into a full kit. Export the six requested deliverables.

Record their exact hashes. Watch/hear the full film. Keep user acceptance separate.

The hosted frontend prepares device-local drafts and does not submit jobs. The recommendation is that product agents on the GPU workstation and Mac claim tenant-authorized jobs through outbound authenticated API connections. Use narrow asset capabilities and recoverable receipts.

Cloudflare Workers must not assume private tailnet access. Keep Resolve and ComfyUI interfaces private.

The Mac must stay available for finishing until a dedicated licensed rendering host is introduced. After local completion, release the owned reservation. Preserve shared runtime resources.

No rental resources were allocated. 
