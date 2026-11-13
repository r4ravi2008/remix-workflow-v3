# Choose the production host: workstation first

The user's GPU workstation is the default host for video work: generation, Resolve assembly, Fusion/lyric work, rendering and heavy analysis. The Mac stays the authoritative record (repository, iCloud workspace, `meta.json`) and the mobile review handoff. Use the Mac's Resolve only when the workstation cannot do the requested stage, and say so.

## Discover the host

Load the `herdr` skill and follow gpu-footage-generation [herdr-local.md](../../gpu-footage-generation/references/herdr-local.md): `hc machine ls`, live terminals, GPU/VRAM, disk, existing queues and Resolve processes. Record the host label, GPU, Resolve edition/version and the stack you use in the project record. Run long work in your own named terminal; never take over another agent's terminal or queue.

## Resolve on the workstation needs Studio for scripted editing

| Capability | Resolve Studio | Free Resolve |
|---|---|---|
| External scripting (`scriptapp("Resolve")`) for automated assembly, Fusion lyric comps, render jobs, readback | Yes (Preferences → System → General → External scripting: Local) | No: returns `None` (Studio-only; 21.1 free removed Python entirely) |
| H.264/H.265 decode and encode on Linux | Yes | No: transcode generated MP4s to DNxHR/ProRes; no H.264/AAC delivery |
| Headless `-nogui` | Yes | Starts, but cannot be driven |

Check the edition before planning the edit (`davinci-resolve` vs `davinci-resolve-studio` package, or `GetProductName()` once connected). On NixOS, Resolve runs inside a bubblewrap FHS wrapper; pass commands through the wrapper (`davinci-resolve <cmd>`) so the scripting Python sees the same libraries, and set `PYTHONPATH`, `RESOLVE_SCRIPT_API` and `RESOLVE_SCRIPT_LIB` to the package's `Developer/Scripting` and `libs/Fusion/fusionscript.so`.

If only free Resolve exists, tell the user before assembly and offer:

1. Install and activate Studio on the workstation (the user changes their Nix profile/config and enters their licence; never rebuild their system or handle the key yourself).
2. Keep generation on the workstation and edit in an available Studio on another machine.
3. Prepare DNxHR media and an interchange timeline for a manual GUI import and render.

Do not substitute an FFmpeg montage for a requested Resolve edit. An FFmpeg rough cut is fine as a clearly labelled review aid.

## Move media between hosts

Stage inputs from the Mac with hashes, generate and render on the workstation, then copy originals, renders, receipts and the editable project back into the iCloud workspace and verify SHA-256 there. Keep workstation paths and Mac paths separate in records. Free disk on the workstation can be tight; check before large model or render jobs.

## Mobile review handoff

When the user wants to watch from a phone, place iPhone-playable H.264/AAC files under the project's iCloud workspace (for example `<revision>/review-samples/`), with clear names, a labelled rough preview if no edit exists yet, and rejected stills marked as rejected. Give the iCloud Drive relative path. A workstation-only path or localhost page is not a mobile handoff.
