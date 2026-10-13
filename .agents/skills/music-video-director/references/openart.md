# OpenArt motion generation through Executor

Use this branch when the user chooses OpenArt, or chooses a MiniMax video model available through OpenArt. The configured Executor integration is named `openart` and authenticates to `https://mcp.openart.ai/mcp` with OAuth. Never place OAuth tokens or other credentials in a remix workspace, skill file, prompt, or provider ledger.

## Establish the live contract

Before planning paid jobs, query the live integration for its account/workspace identity, remaining credits, video models, and relevant tool schemas. Model names, duration and resolution choices, input limits, reference modes, prices, and job-result shapes can change. Do not hardcode a historical catalog.

- If the user names MiniMax, select the exact live MiniMax or Hailuo model they requested. If it is absent, report that boundary instead of silently substituting another model.
- If the user chooses OpenArt but not a model, match the model to the accepted shot card and state the choice before the first paid batch. Prefer continuity and reference control over headline resolution.
- Confirm whether the live tool supports text-to-video, image-to-video, start/end frames, multiple references, extension, and the requested aspect ratio. Unsupported conditioning becomes an editorial bridge in Resolve, not a claimed provider feature.
- Reuse the user's existing OpenArt project/library when specified. Otherwise keep the new work in one clearly named project tied to the remix slug.

Provider setup or connection verification does not authorize a paid canary. An explicit request to generate the video authorizes a bounded first batch under the stated quality policy and budget; ask before a materially larger or more expensive batch when no useful limit can be inferred.

## Submit resumable jobs

Create the asset record before submitting. Give every candidate a stable workspace asset ID and persist at least:

- provider `openart`, exact underlying model, OpenArt project/workspace, and generation mode;
- source frame asset IDs and hashes, prompt revision, aspect ratio, requested duration/resolution, and any seed or provider options;
- submitted job/task ID, timestamps, status, attempt number, and credit snapshot or quoted cost when exposed;
- result URL or library asset ID, downloaded local path and hash, technical probe, usable range, and acceptance status.

Use asynchronous submission when the live tool supports it. Poll the recorded task rather than submitting the same candidate again. After an interruption, reconcile the remote job/library with `assets.json` before any retry. A timeout, lost agent connection, or missing local download does not prove the provider job failed.

## Bring the result into production

Download every completed candidate into the workspace promptly; remote result URLs may expire. Verify that the file is media rather than an HTML or JSON error, run a container/stream probe and full decode check, then watch the entire clip at normal speed. Apply the same face, hand, identity, unintended speech, morphing, flicker, camera, and ending checks defined in [generation.md](generation.md) and [quality-gates.md](quality-gates.md).

Keep rejected outputs and reasons in the ledger without promoting them into the accepted inventory. Only accepted, version-bound local clips may enter Resolve. OpenArt library presence, task completion, or technical decodability alone is not acceptance.
