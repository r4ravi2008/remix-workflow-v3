---
name: upload-remix-to-youtube
description: Private-draft YouTube upload for completed remix workspaces. Use when the user wants a rendered remix uploaded and configured in YouTube Studio, wants an existing draft resumed or updated, or when remix-full-pipeline reaches an explicitly requested upload handoff. Applies metadata, thumbnail, playlist, audience, disclosure, and end-screen settings, verifies the saved draft, and leaves publication to the user.
---

# Upload Remix to YouTube

Treat the **private draft** as the terminal deliverable. Save configured videos with `Private`
visibility, return their Studio URLs, and leave every public, unlisted, or scheduled transition to
the user.

## 1. Resolve the upload package

1. Read the repository's `.remix-workspace-root.json`, then the remix workspace's `meta.json`.
2. Resolve requested assets in this order: explicit user input, `meta.json`, workspace scan.
   Default to the long-form video; include the Short only when explicitly requested.
3. Read [studio-field-map.md](references/studio-field-map.md) before translating workspace data
   into Studio fields.
4. Read [receipt-schema.md](references/receipt-schema.md) before creating or updating upload state.
5. Validate each requested video with `ffprobe`, read its metadata source, and compute its SHA-256.
6. Reconcile newer user files or instructions before continuing; retire stale paths in `meta.json`.

Complete this step when every requested asset has one verified video path, one metadata source,
one fingerprint, and either a resolved thumbnail/end-screen plan or an explicit skipped reason.

## 2. Bind the channel

1. Invoke `chrome:control-chrome` and follow its setup and browser-selection rules. Use the user's
   existing Chrome session because YouTube Studio depends on account state.
2. Open YouTube Studio and read back the active channel name and channel ID before mutating it.
3. Match the channel against an existing receipt or an explicit user instruction. If neither fixes
   the channel identity, ask the user to confirm it.
4. If authentication or 2FA blocks Studio, ask the user to complete it in Chrome and resume from
   the same step.

Complete this step when the visible Studio channel identity matches the intended channel.

## 3. Resume or upload once

1. Inspect `youtube-upload-receipt.json` first. When it contains a video ID for the same asset
   fingerprint, open that draft and continue configuring it.
2. When a receipt is absent or incomplete, inspect recent Studio content for the same filename,
   title, and upload time before starting another upload.
3. Create the receipt with state `planned`, then upload one requested asset at a time.
4. Set visibility to `Private` at the earliest available point.
5. Persist the resulting video ID and Studio URL as soon as YouTube exposes them, before applying
   later settings.

Complete this step when each requested asset maps to exactly one private YouTube video ID and the
receipt has state `uploaded_private`.

## 4. Configure the private draft

1. Apply every resolved field from [studio-field-map.md](references/studio-field-map.md).
2. Upload the custom thumbnail when an actual image file exists. Record the missing asset when the
   workspace contains only thumbnail text or color suggestions.
3. Add configured playlists.
4. Configure the long-form end screen in the upload flow or Studio Editor. Resolve elements using
   the precedence in the field map and verify their timing and targets visibly.
5. Wait for YouTube's processing and checks long enough to observe a final state. Preserve
   `checks_pending` when YouTube has not finished rather than treating it as ready.

Complete this step when every applicable field is visibly applied and every inapplicable or blocked
field has a specific receipt reason.

## 5. Save and prove the draft

1. Reconfirm `Private` visibility immediately before saving.
2. Save the draft.
3. Reopen its Details page and read back title, description, audience, altered-content disclosure,
   thumbnail, playlists, and visibility.
4. Open Editor and read back the end-screen elements and targets for eligible long-form videos.
5. Record the observed values, checks state, video ID, watch URL, Studio URL, and verification time
   in the receipt. Set `ready_for_manual_publish` only when all applicable checks match.
6. Update `meta.json` with the receipt pointer and `status.youtube_private_draft_ready`.
7. Return the private draft's Studio URL, verification summary, and any pending checks. End the run
   there.

Complete the skill only when the receipt and live Studio state agree. The authorized final state is
a saved private draft; publication remains a manual user action.

## Recovery invariants

- Treat a stored video ID as ownership of the remote draft: update that video instead of uploading
  another copy.
- Treat an uncertain upload result as a lookup task in Studio, not permission to retry blindly.
- Keep the original source `meta.json.youtube_url` unchanged.
- Preserve a private, resumable draft when configuration or verification stops partway through.
- Report an upload as ready only from live Studio readback, not from clicks, progress bars, or local
  state alone.
