# Use the native editor CLI

The native CLI runs locally.
The CLI needs no Effect or server.
The first implementation handles solid RGBA clips and PNG frames.
These fixtures exercise the bounded P0 editor.
They do not render a Release Kit output.
See [PROGRESS.md](PROGRESS.md) for measured status and limits.

## Create a project and inspect a frame

Run the commands from the `native-editor` directory.

1. Build the standalone binary.

    cargo build --workspace --locked

2. Discover implemented tools.

    target/debug/native-editor tools

3. Inspect the edit request schema.

    target/debug/native-editor schema project.commit

4. Create the four-second test project.

    target/debug/native-editor call project.create examples/project.json --state .state/cli-example

The result identifies revision zero.
The canvas is 64 by 64 pixels at 24 fps.

5. Add the background clip as one atomic edit.

    target/debug/native-editor call project.commit examples/put-clip.json --state .state/cli-example

The result identifies revision one.
The input contains one stable `intentId` and an `expectedRevision`.

6. Render frame zero.

    target/debug/native-editor call frame.render examples/frame.json --state .state/cli-example

The result contains the artifact ID, stored path, dimensions, project revision, and byte hash.
Every pixel has RGBA `[12, 25, 48, 255]`.

7. Use the verifier to examine the returned artifact ID.

    target/debug/native-editor verify pal-pal-cli-test <returned-artifact-id> --state .state/cli-example

Replace the angle-bracket placeholder with the returned artifact ID.
The verifier reads the stored receipt and actual file.
The verifier accepts no caller-supplied expected hash.
`pal-pal-cli-test` is a fixture name.
It is not a Release Kit receipt.

## Replay a request after an interrupted session

1. Repeat the unchanged `project.commit` command above.

The editor returns the original revision and sets `replayed` to true.
A retry does not create a second edit.
The retry uses the same project-scoped intent.
If you change the edit but keep `background-v1`, the editor returns `intent_conflict`.

For a new edit:

1. Choose a new intent.
2. Inspect the current revision first.

    target/debug/native-editor call project.inspect examples/inspect.json --state .state/cli-example

A stale expected revision returns `revision_conflict`.
The editor preserves the other agent's change.

## Invoke from an agent

The convenience `call <tool> <file>` form supplies the current protocol envelope.
For explicit protocol negotiation:

1. Discover the schema hash.
2. Send a complete envelope on stdin.

    target/debug/native-editor call --state .state/cli-example < envelope.json

`envelope.json` uses the shape in [SPEC.md](SPEC.md).
It includes the discovered schema hash.
The CLI writes one JSON response to stdout.
Diagnostics use stderr.
Exit zero means success.

Exit two means a rejected domain request.
Exit one means a process or storage failure.

The CLI deadline covers execution and result selection.
The agent that calls the CLI must also:

1. Enforce a separate total process timeout.
2. Drain stdout.
3. Preserve the original intent when a timeout leaves the result uncertain.

## Optional Release Kit profile

These are future workflow tasks.
They are not current native CLI operations.
The agent must discover tools before each action.
The agent must read the capability ledger.

| User request | Agent work | Required proof |
| --- | --- | --- |
| Replace one Telugu lyric line | Inspect the project revision, change the caption, and render the affected range | Native-script glyphs, caption timing, and unchanged surrounding edits |
| Make a 20-second chorus promo | Select the source interval, create portrait framing, and export the excerpt | 1080 by 1920 output, exact interval, measured duration, and audio alignment |
| Reduce background reactivity | Change environment parameters and produce comparison frames plus a short preview | People and lyrics preserved, bounded background response, and motion review |
| Make a full Release Kit | Bind the canonical song and assets, then render the film, three promos, and two stills | One 1920 by 1080 24 fps stereo MP4 film, three 1080 by 1920 promos at most 30 seconds each, one 1920 by 1080 JPEG thumbnail, one 1920 by 1920 JPEG artwork file, source-bound hashes, full playback, listening, and creative review |
| Resume a stopped render | Inspect the original intent and output, reconcile, and reuse the original request | No duplicate or substituted outputs and a fresh artifact measurement |

The planned editor implements media, timeline, typography, effects, and export behavior in Rust.
[LAYERS.md](LAYERS.md) specifies the planned layer stack, timed visibility, masks, and composition checks.
A future Effect or UI app can coordinate these tasks through the same command contract.
