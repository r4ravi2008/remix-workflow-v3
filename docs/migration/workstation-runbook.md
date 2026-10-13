# Remix workstation source migration

The public source repository is
<https://github.com/r4ravi2008/remix-workflow-v3>, branch `main`.
The Mac source checkout was `/Users/aira/projects/remix-gpt-coding-agent`, based
on `15c28719209195edd2a7364ad25506ae83339534`. Publication was prepared in an
isolated checkout. The original working tree, index, branch and running worker
were preserved. No workstation connection, deployment or service cutover was
part of this source publication.

Read [source-manifest.json](source-manifest.json) for the exact published paths
and hashes. Read [validation.md](validation.md) for measured checks and limits.
The manifest excludes itself to avoid a circular hash.

## Clone in a future authorized workstation session

Run these commands locally on the workstation after its execution is authorized.
They are instructions, not actions performed by this migration.

```sh
mkdir -p "$HOME/projects"
git clone --branch main --single-branch \
  https://github.com/r4ravi2008/remix-workflow-v3.git \
  "$HOME/projects/remix-gpt-coding-agent"
cd "$HOME/projects/remix-gpt-coding-agent"
git remote -v
git status --short --branch
git rev-parse HEAD
```

Compare `HEAD` with the delivered remote hash. If that directory already exists,
inspect its remote, branch, worktrees and changes before doing anything to it.
Do not replace it. The Mac's folder name differs from the GitHub repository name;
the explicit clone destination above preserves the familiar project path.

## Prepare a machine-local workspace

The ignored `.remix-workspace-root.json` must point to an existing absolute
directory on the workstation. The following creates a separate workspace root
and refuses to overwrite an existing configuration.

```sh
python3 - <<'PY'
import json
from pathlib import Path
workspace = Path.home() / "remix-workspaces"
workspace.mkdir(exist_ok=True)
with Path(".remix-workspace-root.json").open("x") as stream:
    json.dump({"workspaceRoot": str(workspace)}, stream, indent=2)
    stream.write("\n")
PY
```

For existing songs, separately copy the authoritative workspace and accepted
media after identifying its owner and current `meta.json`. Preserve originals,
hashes, provider lineage, databases and editable projects. Rewrite only the
machine-local paths that must change. Git contains neither the Mac's iCloud
workspace nor scratch films, model weights, cached environments or worker state.
Historical evidence paths in documentation do not establish that those files
exist in a fresh clone.

## Install dependencies through the workstation's approved environment

The core pipeline requires Python, uv, Node/npm, FFmpeg/FFprobe, yt-dlp and the
browser/provider integrations selected for the workflow. Python 3.12 is required
for ACE-Step, whose manifest constrains Python to `>=3.12,<3.13`. The existing
ACE-Step lock selects CUDA package indexes for Linux; validate the workstation's
driver, CUDA runtime and model capacity separately. No GPU job or model download
was performed as part of source publication.

With those tools available in the workstation's declared development environment:

```sh
uv sync --frozen --project tools/acapella-extractor --extra dev
uv sync --frozen --project tools/ace-step-generator --group dev
npm ci --prefix tools/video-generator/template
npm ci --prefix tools/visual-sequence
```

The two npm lockfiles are included. Remotion packages are pinned together at
`4.0.441`. Recreate dependencies on the target; the Mac's `node_modules`, Python
virtual environments and Rust targets contain host-specific binaries. Installation
and a complete music workflow have not been tested on NixOS. Verify the approved
Nix development environment can load the Python/native dependencies before
starting a production project. Keep any required provider credentials in the
workstation's approved local secret configuration, outside Git. Browser sessions
must be established on that host; do not export Mac cookies or copy credentials
into the repository.

Optional apps have separate manifests and entry points:

| Component | Source/setup | Target limitation |
| --- | --- | --- |
| GPU router | `apps/gpu-router`; `bun install --frozen-lockfile`, `bun run check` | Hosted deployment and GPU providers are separate actions. |
| Release Kit application | `apps/release-kit-studio`; `bun install --frozen-lockfile`, `bun run check` | Local/hosted worker settings and private state are not included. |
| Rust native editor P0 | `apps/release-kit-studio/native-editor`; its README and AGENTS map | Portable Rust foundation; Linux runtime was not tested here. Its scope is bounded PNG/project operations. |
| Video Studio renderer | `apps/video-studio`; its README and WORK record | macOS AVFoundation implementation. It is not a Linux renderer. |
| Video Studio application prototype | `apps/video-studio/application` | Effect/native adapters are prototype work; no hosted or full-film acceptance is implied. |
| Resolve helpers | Repo skills and selected tool/script docs | Configure Resolve and its scripting integration on the workstation separately. |
| FL Studio workflows | Selected workflow/integration documentation | Configure the workstation installation and integration separately; no Mac app/plugin binaries are included. |

Song-specific scripts under `scripts/` and `tools/video-generator/` retain
historical workspace, Resolve and provider assumptions. Inspect their paths,
source contracts, output destinations and ownership before execution. They are
preserved tools, not a general unattended Linux runner. Do not run legacy RunPod
setup, allocation, transfer or shutdown utilities merely to test the clone.

## Validate before production

```sh
python3 scripts/audit_workflow_portability.py
node --test tools/shared/workspace-root.test.js \
  tools/video-generator/init-video.test.js tools/visual-sequence/*.test.js
(cd tools/acapella-extractor && uv run --extra dev pytest tests)
(cd tools/ace-step-generator && uv run --group dev pytest tests)
```

The portability auditor reports credential-like literals and historical
path locations without printing their values. Review those locations; it is a
focused publication check, not a complete security assessment.

For a core pipeline canary, read `AGENTS.md`, `prompts/README.md` and the relevant
phase skill. Use a new test slug and synthetic/local inputs, run the required
steps in order, and inspect the outputs. A canary must not reuse a live worker's
project or queue. The native editor's README lists its independent P0 verifier
commands. A full-song render, GPU generation, Resolve/FL Studio session and
provider/browser integration need separate checks on the target.

## Keep the current worker ownership until cutover

A Mac Release Kit worker was observed running during publication, using
`apps/release-kit-studio/agent/service.ts`. It remained running and unchanged.
The Mac service installer uses `launchctl`; it is Mac-specific and must not be
run on NixOS. Do not start a second worker, scheduler, queue consumer or provider
workflow while the Mac still owns the current jobs.

After workstation validation, a separately authorized cutover should inventory
the Mac worker and queue, record ownership/leases and in-flight work, verify
portable project state and accepted files, then assign exactly one active owner.
Keep the Mac checkout and current services until that cutover is approved and
verified. This source migration does not authorize their removal or shutdown.
