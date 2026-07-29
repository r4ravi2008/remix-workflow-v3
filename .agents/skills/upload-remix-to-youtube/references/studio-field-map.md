# YouTube Studio field map

Use this map while building the upload plan and while performing final readback. Workspace data is
the desired state; visible YouTube Studio values are the observed state.

## Details

| Studio field | Source | Resolution rule |
|---|---|---|
| Video file | `meta.json.files.final_video` or `files.short_video` | Prefer explicit user input, then state, then workspace scan |
| Title | `youtube-metadata.json.title` | Validate against the currently selected asset before applying |
| Description | `youtube-metadata.json.description` | Preserve credits, original-song link, and hashtags |
| Tags | `youtube-metadata.json.tags` | Apply the complete validated list |
| Category | `youtube-metadata.json.category` | Default to `Music` only when absent |
| Audience | `youtube-metadata.json.madeForKids` | Require a resolved boolean; use it for YouTube's audience field |
| Language | `meta.json.language` | Apply when Studio exposes the field |
| Thumbnail | `meta.json.files.youtube_thumbnail` or explicit image | Use only an actual readable image, not thumbnail copy suggestions |
| Playlist | explicit user instruction, then prior receipt defaults | Record `skipped_no_playlist` when unresolved |
| Visibility | skill invariant | Select `Private` |

## Altered or synthetic content

Set the disclosure from how the selected audio and visuals were produced, independently of title or
description wording.

- Set `Yes` for Suno- or ACE-Step-generated music and for realistic generated or meaningfully
  altered visuals.
- Set `No` only when workspace evidence establishes that the uploaded content does not meet the
  disclosure condition.
- Ask the user when the workspace evidence is genuinely ambiguous.

Record the applied boolean and its evidence in the receipt.

## End screen

Configure end screens only for eligible long-form videos. Use this precedence:

1. current user instruction;
2. explicit end-screen defaults in an earlier receipt for the same channel;
3. one `Best for viewer` video element plus `Subscribe`;
4. when the channel has an eligible prior public long-form upload, add it as a specific second video.

Use the final 20 seconds when the video and Studio permit it. For videos shorter than 25 seconds,
record `ineligible_duration`. Verify each element's type, target, placement, and timing in Editor.

## Short branch

Upload a Short only when the user explicitly includes it. Derive its title and description from the
long-form metadata plus `hashtags`, keep it private, and track it as a separate asset and video ID.
End-screen configuration is a long-form concern unless Studio visibly offers an eligible Short
editor flow and the user requested it.

## Checks

Record the visible processing, copyright, and restrictions states. A completed clean check is
`complete`; an unfinished YouTube check is `pending`; a visible claim or restriction is `attention`.
Use `checks_pending` or `needs_attention` instead of `ready_for_manual_publish` until the user can
review the result.
