# Private draft receipt

Store provider state in `<workspace>/youtube-upload-receipt.json`. Store only its root-relative path
and readiness flag in `meta.json`; the receipt is the single source of truth for YouTube details.

## Schema

```json
{
  "schema_version": 1,
  "channel": {
    "id": "UC...",
    "name": "Channel name",
    "verified_at": "2026-07-26T00:00:00Z"
  },
  "assets": {
    "long_form": {
      "state": "ready_for_manual_publish",
      "source_file": "<slug>/<slug>-video.mp4",
      "source_sha256": "...",
      "metadata_file": "<slug>/youtube-metadata.json",
      "metadata_sha256": "...",
      "video_id": "...",
      "watch_url": "https://www.youtube.com/watch?v=...",
      "studio_url": "https://studio.youtube.com/video/.../edit",
      "visibility": "private",
      "applied": {
        "metadata": true,
        "audience": true,
        "altered_content": true,
        "thumbnail": "applied",
        "playlists": ["..."],
        "end_screen": "applied"
      },
      "checks": {
        "processing": "complete",
        "copyright": "complete",
        "restrictions": "none"
      },
      "last_verified_at": "2026-07-26T00:00:00Z"
    }
  },
  "updated_at": "2026-07-26T00:00:00Z"
}
```

Add `assets.short` with the same shape only when a Short was requested.

## States

Use this forward-only state sequence unless live readback discovers drift:

```text
planned -> uploaded_private -> configuring -> checks_pending -> ready_for_manual_publish
                                           -> needs_attention
```

When drift is found, move the asset back to `configuring`, correct the same remote video, and verify
again.

## Idempotency

- Match a local asset by `source_sha256` and `metadata_sha256`.
- Persist `video_id` before subsequent Studio configuration.
- Resume an asset with a `video_id`; never create a replacement merely because a later field failed.
- When no ID was captured, search recent Studio uploads by source filename, expected title, duration,
  and upload time. Record the recovered ID before continuing.
- Start a new upload only after the receipt and Studio content both establish that no matching remote
  video exists.

## meta.json update

Write only the provider pointer and aggregate readiness:

```json
{
  "files": {
    "youtube_upload_receipt": "<slug>/youtube-upload-receipt.json"
  },
  "status": {
    "youtube_private_draft_ready": true
  }
}
```

Set the readiness flag to `true` only when every requested asset has
`state: "ready_for_manual_publish"`. Keep `meta.json.youtube_url` as the original source URL.
