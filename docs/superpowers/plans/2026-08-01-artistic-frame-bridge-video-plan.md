# Artistic Frame-to-Frame Video Plan

## Goal

Replace regularly timed still-image crossfades with short, generated motion shots that begin from one stylized anchor frame and arrive at the next stylized anchor frame. Preserve the existing still sequence as the source of truth and retain cover-art/placeholder fallbacks.

## Recommended Product Shape

Use a hybrid timeline for every adjacent anchor pair:

```text
anchor A hold -> generated bridge A-to-B -> anchor B hold
```

The model generates only the middle motion. Remotion pins the exact source images at the boundaries and adds a very short deterministic blend if the generated clip's first or last decoded frame is not visually close enough to its anchor. This gives the artistic benefit of generative video without trusting a probabilistic model to produce exact edit points.

Do not distribute transitions at equal wall-clock intervals. Place them on musical phrases and section changes derived from `lyrics-timestamps.json`, section metadata, and audio energy. A bridge should normally lead into a downbeat, chorus, drop, or emotional lyric change.

## Provider Decision

### Primary: Veo 3.1 Fast first/last-frame through fal.ai

Use `fal-ai/veo3.1/fast/first-last-frame-to-video` for the first prototype.

Reasons:

- It explicitly accepts both `first_frame_url` and `last_frame_url`.
- It supports 4, 6, and 8 second clips at 720p or 1080p in 16:9 and 9:16.
- The repository already uses `@fal-ai/client`, fal storage uploads, and a fal credential for frame stylization.
- Generating without model audio is appropriate because the remix remains the canonical soundtrack.
- The current published fal price is $0.10 per second without audio at 720p/1080p, making a 6-second test bridge approximately $0.60.

Official references:

- [fal.ai Veo 3.1 Fast first/last-frame API](https://fal.ai/models/fal-ai/veo3.1/fast/first-last-frame-to-video/api)
- [Google first-and-last-frame generation guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames)

### Quality tier: Veo 3.1 standard

Use `fal-ai/veo3.1/first-last-frame-to-video` only for hero transitions or when Fast fails artistic review. Its published no-audio price is $0.20 per second at 720p/1080p.

- [fal.ai Veo 3.1 first/last-frame API](https://fal.ai/models/fal-ai/veo3.1/first-last-frame-to-video/api)

### Low-cost fallback: Wan 2.1 FLF2V

Use `fal-ai/wan-flf2v` for comparison tests and budget fallback. It accepts start/end images and produces roughly five seconds at its default 81 frames and 16 fps. Its published price is $0.40 per 720p generation.

- [fal.ai Wan 2.1 first/last-frame API](https://fal.ai/models/fal-ai/wan-flf2v/api)

Provider choice must stay behind an adapter. Model IDs, prices, and limits change; they must not be embedded in the visual manifest.

## Artistic Direction System

Create one workspace-level `motion-direction.json` containing:

- a one-sentence visual thesis for the song;
- character and identity invariants;
- palette and lighting progression;
- allowed camera moves;
- recurring motifs such as wind, fabric, particles, rain, smoke, petals, reflections, or painted light;
- forbidden changes such as new text, costume replacement, extra people, face mutation, photographic texture, or scene cuts;
- energy profiles for intro, verse, chorus/drop, bridge, and outro.

Generate a specific prompt for each anchor pair from:

```text
global art direction
+ visible action connecting A to B
+ one camera move
+ one environmental motion motif
+ section energy and emotional intent
+ identity/composition constraints
+ negative constraints
```

Prefer motivated movement over generic morphing. Examples:

- a slow dolly through drifting rain as a face turns toward camera;
- fabric and hair lifted by a bass pulse while painted light travels across the scene;
- a controlled orbit that reveals the next composition;
- particles collapsing into the geometry of the destination frame;
- a dreamlike reflection or shadow transformation that hides a difficult spatial change.

Use no more than one principal camera move and one dominant transformation per bridge. This keeps the anime/cel-art language coherent and reduces anatomical drift.

## Workspace Contract

Add these outputs without replacing `image-sequence.json`:

```text
motion-direction.json
transition-prompts.json
generated-transitions/
  <slug>-frame-001-to-frame-002.mp4
  <slug>-frame-002-to-frame-003.mp4
motion-sequence.json
```

Suggested `motion-sequence.json` shape:

```json
{
  "version": 1,
  "provider": "fal",
  "model": "fal-ai/veo3.1/fast/first-last-frame-to-video",
  "transitions": [
    {
      "id": "frame-001-to-frame-002",
      "from_frame_id": "frame-001",
      "to_frame_id": "frame-002",
      "video_path": "generated-transitions/<slug>-frame-001-to-frame-002.mp4",
      "duration": 6,
      "timeline_start": 18.0,
      "timeline_end": 24.0,
      "prompt_id": "transition-001",
      "request_id": "provider-request-id",
      "seed": 1234,
      "sha256": "...",
      "qa": {
        "decode_ok": true,
        "start_anchor_score": 0.0,
        "end_anchor_score": 0.0,
        "approved": false
      }
    }
  ]
}
```

Persist request IDs immediately so interrupted runs resume instead of purchasing duplicate generations. Record failures and rejected candidates; do not overwrite approved clips unless `--overwrite` is explicit.

## Pipeline Changes

### Phase A: One-pair artistic proof

1. Choose a visually compatible adjacent pair from an existing completed workspace.
2. Write the workspace visual thesis and one bridge prompt by hand.
3. Generate three candidates with Veo Fast, 6 seconds, 720p, no audio, fixed recorded seeds.
4. Generate one Runway Gen-4.5 candidate for an independent artistic comparison; retain Wan as the budget fallback if both primary options disappoint.
5. Inspect identity, anatomy, camera motion, temporal coherence, and arrival at frame B.
6. Put the best candidate between the exact anchors in a 10–12 second Remotion preview.
7. Do not scale to a full song until this proof is artistically approved.

### Phase B: Generation CLI

Add `tools/visual-sequence/generate-transitions.ts` with commands such as:

```bash
npm run --prefix tools/visual-sequence transitions:plan -- <slug>
npm run --prefix tools/visual-sequence transitions:generate -- <slug> --transition=frame-001-to-frame-002 --candidates=3
npm run --prefix tools/visual-sequence transitions:verify -- <slug>
```

Responsibilities:

- read `meta.json`, `selected-visual-frames.json`, `image-sequence.json`, and `motion-direction.json`;
- validate adjacent anchor assets and matching dimensions;
- upload anchors and submit non-blocking fal queue requests;
- persist request IDs before polling;
- download clips atomically;
- normalize them with FFmpeg to the render contract;
- write `motion-sequence.json` only from verified local files;
- resume completed/submitted transitions safely.

Use a provider interface so Veo Fast, Veo standard, and Wan can share orchestration while mapping their different request fields internally.

### Phase C: Automated technical QA

For every downloaded clip:

1. Decode the complete file with FFmpeg.
2. Verify duration, dimensions, frame rate, codec, and absence of an audio stream.
3. Extract the first, middle, and final decoded frames.
4. Compare boundary frames with source anchors using perceptual similarity, not byte equality.
5. Detect black frames, letterboxing, unexpected text/watermarks, and frozen output.
6. Create a contact sheet and a low-resolution preview for human artistic review.
7. Reject rather than silently use clips that fail technical checks.

Model conditioning does not guarantee pixel-identical endpoints. The renderer therefore shows the exact A and B anchor images outside the generated clip and uses a short 3–6 frame blend when needed.

### Phase D: Remotion integration

Extend the sequence-aware layouts to load `motion-sequence.json` and render generated clips with Remotion's `OffthreadVideo`. Keep the current still sequence as fallback when a transition is missing, rejected, or fails to decode.

Renderer rules:

- generated clip audio is always muted;
- exact anchor images own the edit boundaries;
- clips may be retimed slightly to land on a musical cue, but avoid large speed changes;
- the bridge ends on the destination downbeat;
- existing lyrics and audio-reactive overlays remain above the generated footage;
- long-form and Short manifests are separate unless a clip has been explicitly validated for both crops.

Official rendering references:

- [Remotion OffthreadVideo](https://www.remotion.dev/docs/offthreadvideo)
- [Remotion TransitionSeries](https://www.remotion.dev/docs/transitions/transitionseries)

### Phase E: Musical placement

Replace equal segmentation with a transition planner:

1. Derive candidate boundaries from lyric sections, line starts, instrumental gaps, and audio-energy changes.
2. Snap destination-frame arrival to the strongest nearby phrase/downbeat.
3. Select 4, 6, or 8 seconds based on available musical lead-in.
4. Keep still holds where motion would compete with an important lyric.
5. Reserve the strongest motion prompts and standard-quality model for chorus/drop transitions.

The first version may use the existing lyric section timings plus deterministic heuristics. Beat tracking can be added later if the current audio analysis does not expose reliable downbeats.

## Acceptance Criteria

The MVP is complete when:

- one approved bridge visibly begins from anchor A and arrives at anchor B;
- the original remix is the only audible soundtrack;
- the clip passes full decode and media-property checks;
- exact anchors hide endpoint drift without a visible flash or jump;
- a Remotion preview proves the bridge appears in the active sequence-aware layout;
- retrying the command does not resubmit a completed provider request;
- missing/rejected motion falls back to the existing still-frame behavior;
- provider/model/request/seed/prompt/checksum and approval state are recorded;
- no full-song generation occurs without a cost estimate and explicit approval of the one-pair artistic proof.

## Recommended Rollout

1. Approve this architecture and choose an existing workspace for the proof.
2. Implement only the provider adapter, one-pair generator, technical QA, and preview component.
3. Generate four candidate clips total: three Veo Fast and one Runway Gen-4.5.
4. Review them side by side and lock the motion language.
5. Add batch planning, resumability, full-song placement, and Short support only after the proof succeeds.

This staged rollout limits cost and gives the artistic direction a chance to become deliberate before automation amplifies it across an entire song.
