# Workspace Root Configuration Design

## Summary

Move remix workspace storage out of the repository and into a machine-local, iCloud-backed
directory configured once per cloned repo instance. The repository will keep prompts, tools,
and templates, but all runtime workspace creation and file resolution will use a local,
untracked config file as the source of truth.

This change replaces the current hard-coded assumption that every remix lives under
`workspaces/<slug>/` at the repo root.

## Goals

- Allow the same cloned repo to use a machine-local iCloud-backed workspace root.
- Make the workspace root configurable once per clone, without relying on shell state.
- Keep generated artifacts portable across machines by storing root-relative paths.
- Update prompts and helper tools so they resolve workspace paths consistently.
- Fail fast when local setup is missing or invalid.

## Non-Goals

- No environment-variable dependency for the primary configuration path.
- No fallback to repo-root `workspaces/` when local config is missing.
- No automatic migration of existing repo-local workspaces.
- No attempt to move old historical artifacts already created in the repo.

## Current Problem

The repo currently treats `workspaces/<slug>/` as a core invariant across:

- prompt instructions
- shared prompt references
- `meta.json` examples and stored paths
- `tools/video-generator/init-video.js`
- tool README examples and operational docs

That makes the runtime output location effectively fixed to the local repo checkout, which is
not suitable when the user switches between computers and wants the active remix state to live
inside an iCloud-synced directory.

## Recommended Approach

Use a local, untracked config file in the repo plus runtime path resolution.

The config file stores a single absolute path to the external workspace root. Prompts and tools
must read that config before creating or resolving any workspace paths. Generated metadata keeps
paths relative to that configured root so the same workspace can be used on multiple machines
whose iCloud mount paths may differ.

## Configuration Model

### Files

- Tracked example file: `.remix-workspace-root.example.json`
- Real local file: `.remix-workspace-root.json`
- `.remix-workspace-root.json` must be gitignored

### Config Shape

```json
{
  "workspaceRoot": "/Users/you/Library/Mobile Documents/com~apple~CloudDocs/remix-workspaces"
}
```

### Resolution Rules

- `workspaceRoot` is an absolute path to the parent folder that contains all slug folders.
- The resolved workspace directory for slug `<slug>` is `<workspaceRoot>/<slug>/`.
- Any prompt or tool that needs a workspace path must read the local config first.
- The repo's `workspaces/` directory is no longer the operational source of truth.
- If the config file is missing, malformed, or points to a non-existent directory, execution
  stops immediately with setup instructions.

## Path Semantics

### Runtime Resolution

- Absolute paths are used only at runtime after reading `.remix-workspace-root.json`.
- The configured root is machine-local and may differ across computers.

### Stored Metadata

- `slug` remains unchanged and still names the workspace folder.
- `meta.json.workspace` becomes root-relative, for example `bella-bella-lofi/`.
- `meta.json.files.*` values become root-relative, for example:
  - `bella-bella-lofi/bella-bella-lofi-original.mp3`
  - `bella-bella-lofi/design.json`
  - `bella-bella-lofi/video/public/audio.mp3`

This keeps artifacts portable between machines while preserving a single stable workspace layout.

## Prompt Changes

### Shared Convention Updates

`prompts/references/workspace-conventions.md` becomes the canonical explanation of:

- the local config file
- the configured external workspace root
- the difference between runtime absolute paths and stored root-relative paths
- the updated `meta.json` schema examples

### Step 0 Changes

Step 0 becomes the path-resolution gatekeeper.

Updated responsibilities:

1. Read `.remix-workspace-root.json`
2. Validate that the file exists, parses, and points to an existing directory
3. Derive the slug
4. Create `<workspaceRoot>/<slug>/`
5. Write `meta.json` with root-relative paths only
6. Print a readiness summary that includes the resolved absolute workspace directory

Step 0 must no longer instruct the agent to create `workspaces/<slug>/` under the repo root.

### Other Prompt Updates

Any step that currently refers to `workspaces/<slug>/...` as an operational path should instead:

1. read the configured workspace root
2. resolve the absolute path for the current slug
3. operate on files under that resolved directory

Prompt examples may still refer to `<slug>/...` when showing stored metadata values, but should
not imply that repo-root `workspaces/` is authoritative.

## Tooling Changes

### Shared Helper

Add a small shared helper for Node-based tooling that:

- reads `.remix-workspace-root.json`
- validates the JSON shape
- validates that `workspaceRoot` exists
- resolves `<workspaceRoot>/<slug>`
- returns clear errors with the resolved path when a slug workspace does not exist

This avoids duplicating config-reading logic in every script.

### Video Generator

`tools/video-generator/init-video.js` should be updated to:

- read the local workspace-root config
- resolve the absolute workspace path from the provided slug
- scaffold the Remotion project in `<workspaceRoot>/<slug>/video/`
- stop showing repo-root `workspaces/...` copy commands in success output
- print commands/examples using the resolved workspace path model

`tools/video-generator/README.md` should be updated to match the new setup and path conventions.

## Failure Handling

The system should fail fast instead of guessing.

### Missing Local Config

Behavior:

- Stop immediately.
- Print exact setup instructions, including copying the example file and editing the real file.

### Invalid JSON

Behavior:

- Stop immediately.
- Explain that `.remix-workspace-root.json` could not be parsed.

### Missing Configured Root Directory

Behavior:

- Stop immediately.
- Print the missing absolute path from `workspaceRoot`.

### Missing Workspace For A Known Slug

Behavior:

- Stop immediately.
- Print the resolved absolute path that was expected.

## Local Setup UX

After cloning the repo, each machine performs a one-time local setup:

```bash
cp .remix-workspace-root.example.json .remix-workspace-root.json
```

Then edit:

```json
{
  "workspaceRoot": "/Users/you/Library/Mobile Documents/com~apple~CloudDocs/remix-workspaces"
}
```

Setup guidance must make the following explicit:

- `.remix-workspace-root.json` is local-only and must not be committed.
- The configured path is the parent directory that contains all slug folders.
- Different machines may point to different local iCloud mount paths while using the same synced
  workspace contents.
- The repo may still contain `workspaces/` as a legacy directory, but operationally the external
  configured root is authoritative.

## Migration Posture

- Do not automatically move existing repo-local workspaces.
- Do not add compatibility fallbacks from missing config to repo-root `workspaces/`.
- Existing repo-local workspaces can remain as historical artifacts.
- Real usage paths, examples, and instructions should be updated where they drive active workflow.

## Verification Targets

- Step 0 validates the local config before creating or resolving any workspace paths.
- `meta.json` stores root-relative paths only.
- `tools/video-generator/init-video.js` works when the configured root is outside the repo.
- Operational prompts no longer assume repo-root `workspaces/<slug>/`.
- Setup docs clearly explain the one-time per-clone local configuration step.

## Open Implementation Notes

- The repo likely has many doc references to `workspaces/<slug>/`; implementation should update
  all operational references first and then clean up supporting docs.
- The change should stay minimal: one local config file, one shared path helper, targeted prompt
  and tool updates, and no broader architecture changes.
