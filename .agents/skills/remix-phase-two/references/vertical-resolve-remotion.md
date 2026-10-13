# Vertical Resolve and Remotion Delivery

Use this reference for every Phase Two vertical video. The Resolve edit and the
Remotion wrapper are separate deliverables with separate review gates.

## 1. Build the Resolve vertical picture master

1. Duplicate the approved landscape timeline. Never reframe the only approved
   timeline in place.
2. Set the duplicate to 1080x1920. Keep the project and source frame rates.
3. Inventory every scene or continuous shot in `resolve-scenes.json`:

   ```json
   {
     "scenes": [
       {
         "id": "scene-001",
         "start": 0.0,
         "end": 2.8,
         "label": "singer close-up",
         "focalPoint": "eyes",
         "reframe": "static"
       }
     ]
   }
   ```

4. Reframe shot by shot. Anchor faces at the eyes, performance footage at the
   hands or instrument, dance/action at the motion path, and any intentional
   on-screen text at the text block. Do not apply one center crop to the whole
   timeline.
5. If the subject moves, keyframe position and scale so the focal point remains
   inside the vertical action-safe area for the complete shot. Review the head,
   middle, and tail of that shot.
6. Prefer, in order: a better source take, a deliberate crop, a restrained
   background extension, then a blurred-fill treatment. Never crop through eyes,
   mouths, hands, instruments, or essential action merely to fill the frame.
7. Keep the vertical picture master aligned to the full approved remix timeline,
   then export `<slug>-resolve-vertical.mp4` at 1080x1920. Verify the rendered
   file has a video stream, correct dimensions, full-remix duration, and no
   blanking. Remotion owns the later short-window trim.

The Resolve picture master should be clean picture. Lyrics and equalizer belong
to the Remotion composition unless the user explicitly asks for a texted Resolve
master too.

## 2. Generate proof for every scene

Run the included helper against the rendered Resolve file and scene manifest:

```bash
.agents/skills/remix-phase-two/scripts/generate-scene-contact-sheets.sh \
  "${WORKSPACE_DIR}/${SLUG}-resolve-vertical.mp4" \
  "${WORKSPACE_DIR}/resolve-scenes.json" \
  "${WORKSPACE_DIR}/vertical-scene-review"
```

The helper samples the head, middle, and tail of every scene and paginates the
results. One midpoint frame is not enough for a moving subject.

Give the contact-sheet pages, `contact-sheet-index.json`, and the scene manifest
to a separate review sub-agent. The reviewer must inspect every labeled cell at
readable resolution and return a per-scene verdict for:

- focal subject intact throughout the shot;
- no clipped face, eyes, mouth, hands, instrument, or essential action;
- no unintended blanking, edge artifacts, captions, or watermarks;
- stable framing across the head, middle, and tail samples.

The editing agent must not self-approve this gate. Any failed scene goes back to
Resolve, then all affected contact-sheet pages are regenerated and reviewed by a
fresh sub-agent pass. Save the accepted report as
`vertical-scene-review/scene-review.md`.

## 3. Build the Remotion mobile composition

Use a 1080x1920 composition with fixed bands:

- picture: top 1536px, exactly 80% of the canvas;
- lyrics: next 192px, exactly 10%;
- equalizer and progress: bottom 192px, exactly 10%.

Use `<Video>` from `@remotion/media` for the Resolve master. The foreground
video uses `objectFit: contain` so Remotion never introduces a second crop. A
muted, blurred copy may fill unused panel edges. The selected remix remains the
only audible source.

## 4. Mobile lyric rules

- Native-script lyrics remain canonical and are the displayed text.
- Show the active lyric only in the 10% lyric band.
- Keep at least 60px horizontal inset and 18px vertical inset.
- Fit text against the real font metrics; do not guess from character count.
- Cap at two lines, use a compact line height, and keep high contrast against a
  quiet background.
- Review at full size and at a 25% mobile preview. A technically non-overflowing
  line that cannot be read at phone size still fails.
- Keep lyrics out of the bottom equalizer band and away from platform UI zones.

## 5. Final proof

After the scene gate passes, intersect the full-song scene manifest with the
selected short window, rebase those scene times to zero, and save
`resolve-scenes-short.json`. Render the Remotion short and generate a second
contact sheet from the final output using that rebased manifest. Check the first,
middle, and last frame of every included scene again so the wrapper cannot
reintroduce crop, text overflow, or blanking. Then run full-file decode and
reconcile the video-stream, audio-stream, container, and expected composition
durations before setting `status.short_video_generated`.
