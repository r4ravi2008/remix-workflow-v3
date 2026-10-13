# Test the standalone local Editor CLI

This guide documents the historical Python and FFmpeg prototype. The proposed no-FFmpeg local path is specified in the [standalone Rust editor](../native-editor/README.md). These commands still select the historical implementation.

The Rust specification is saved before runtime changes.

The editor runs directly on this Mac at `http://127.0.0.1:1340`. It uses Bun, SQLite, local files, and native Python/FFmpeg. Cloudflare, Workerd, Docker, Tailscale, Resolve, and a GPU are not required. The prepared demo is a two-second synthetic film, three Shorts, a thumbnail, and square artwork.

It includes Telugu captions, independent framing, and masked film reactivity.

## Start the service

1. Open the app directory.

   ```sh
   cd /Users/aira/projects/remix-gpt-coding-agent/apps/release-kit-studio
   ```

2. If setup is incomplete, prepare the local fonts and demo.

   ```sh
   bun run editor:local:setup
   ```

   Setup requires `python3`, `ffmpeg`, `ffprobe`, `fc-match`, and `fc-cache`.
   It downloads pinned Google Noto fonts into the private local state directory.

3. If the standalone service is stopped, start it in this terminal.

   ```sh
   bun run editor:local
   ```

   Keep this terminal active. Expect `ready: true` and port 1340.
   Press Control-C to stop the server and cancel its active native render.

## Inspect and edit

Use another terminal in the same app directory.
The wrapper loads private credentials automatically.

1. Examine the actual runtime.

   ```sh
   bun run editor:local:cli health
   ```

   Expect `hosting: "local-bun"` and `rendering: "local-python-ffmpeg"`.

2. Inspect the saved demo project.

   ```sh
   bun run editor:local:cli call project.inspect .local/editor-local/demo/inspect.json
   ```

3. List the supported CLI commands.

   ```sh
   bun run editor:local:cli help
   ```

4. Validate the six-output project.

   ```sh
   bun run editor:local:cli validate .local/editor-local/demo/project.json kit
   ```

5. Preview the sample framing edit in JSON.

   ```sh
   bun run editor:local:cli edit .local/editor-local/demo/project.json .local/editor-local/demo/edits.json
   ```

6. Save the sample framing edit as revision 2.

   ```sh
   bun run editor:local:cli call project.edit .local/editor-local/demo/apply-edits.json
   ```

   The film clip changes to `centerX: 0.4` and `zoom: 1.1`.
   A replay of the same request returns the same revision.
   Further edits need the current `expectedRevision` and a new `intentId`.

## Render and verify

1. Submit the prepared six-output render at revision 1.

   ```sh
   bun run editor:local:cli call render.start .local/editor-local/demo/render.json
   ```

   The prepared sandbox already has a verified revision-1 render.
   A replay of this intent returns that job.
   To render an edit, change `revision` to 2 and use a new `intentId`.

2. Put the returned `jobId` into `.local/editor-local/demo/job.json`.

   ```json
   { "jobId": "RETURNED_JOB_ID" }
   ```

3. Examine that job.

   ```sh
   bun run editor:local:cli call render.status .local/editor-local/demo/job.json
   ```

   `ready` means stored-byte technical verification completed. The server updates jobs automatically. `render.reconcile` checks the same job immediately.

`render.cancel` terminates that job's owned native process. If observation ends, inspect the same job before you submit another intent.

4. Verify the prepared film independently.

   ```sh
   bun run editor:local:cli call artifact.verify .local/editor-local/demo/artifact.json
   ```

   If you use another job, update `artifact.json` and `preview.json` with its ID.

5. Save a review clip and four full-resolution frames.

   ```sh
   bun run editor:local:cli preview .local/editor-local/demo/preview.json .local/editor-local/my-preview
   ```

6. Download the prepared film.

   ```sh
   bun run editor:local:cli download 004df3d3-cc57-4fa8-beed-b93a80903076 film .local/editor-local/my-film.mp4
   ```

7. Download the prepared release kit ZIP.

   ```sh
   bun run editor:local:cli archive 004df3d3-cc57-4fa8-beed-b93a80903076 .local/editor-local/my-kit.zip
   ```

   Downloads verify sizes and hashes. The ZIP verifier checks all eight entries.
   Destination files and preview directories must not already exist.
   Technical verification does not record watching, listening, or creative acceptance.

## Persistent state and isolation

`.local/editor-local/editor.sqlite` stores revisions, jobs, and receipts. `.local/editor-local/objects/` stores private media. `.local/editor-local/scratch/` stores native logs and work files.

`connection.json` and `credentials.json` remain ignored and mode 600. The local bearer credential renews for 30 days when the server starts.

A service restart preserves completed jobs and edited projects.
An interrupted, unconfirmed render needs reconciliation or explicit cancellation.
The server never automatically repeats an unknown render outcome.

Set `EDITOR_LOCAL_STATE` to use another isolated state directory. Set `EDITOR_LOCAL_PORT` to use another loopback port. Run `bun run test:editor-local` for the isolated native integration check. The previous `.local/cli-playground/editor` wrapper targets Workerd and is not this local mode.

