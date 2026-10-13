# Correct, verify, then present

Use for any correction, finishing pass, or claim that an edit is ready. Previous music-video revisions often left observable defects in a supposedly checked render; apply the same exact-export discipline to every category. Make the check specific enough to catch it before the user does.

## Carry the decisions forward

Maintain one compact correction ledger in the existing project record. Each entry records the request/source, affected shot/cue/range, observed defect, intended behavior, preserved choices, changed dependencies, rendered evidence, and status (`open`, `repaired-unreviewed`, `verified`, or `superseded-by-user`). Use IDs and exact frames after locating the user's approximate timestamp. If a scene label disagrees with a timestamp, inspect the nearby narration/music and image; do not guess which scene they meant.

Reconcile the entire accepted brief before a substantial pass: story/idea beats, factual claims when applicable, intercut role, character treatment, transitions, enabled text roles, message exchanges, intro, ending and requested formats. Read actual media and timeline contents. Folder counts, an older `meta.json` pointer, and the name “full motion” do not establish the selected source or current completion. Hash-lock the chosen catalog and preserve other branches as separate candidates. An unavailable source never authorizes swapping a different storyline or anchor family into the film.

“Fix this transition” preserves the requested transition language. Diagnose the failed timing/composite and repair it. “Go back to the previous lyrics” reverts that feature while preserving later approved message or footage fixes; do not roll the whole project back. Record old and new artifact hashes for comparison.

The latest scoped selection supersedes an earlier example or approval. Record what changed and what stayed fixed: moving lyrics into mattes changes placement, not footage or words; rejecting a new face reopens its anchor/motion chain, not the whole soundtrack. After feedback contradicts “looks good,” inspect the new complaint against the exact previously shown artifact rather than treating approval as permanent.

## Diagnose at the right scale

1. Watch the reported section with sound when available, including its neighboring shots. Inspect the storyboard for story/order complaints before moving clips.
2. For a one-frame flash, mask bleed, reset, or tracked-text flicker, inspect every frame across the affected event plus clean frames on both sides. Use legible numbered sheets and full-size crops; a ten-second sampling grid can miss these failures entirely.
3. Read corresponding Resolve clip ranges, transforms, track enable states, Fusion connections, masks, time maps, and render state. Form a cause tied to both the timeline and exported pixels.
4. Check every occurrence that shares the defective template, carrier, source geometry, or tracking method. Fixing only the timestamp named by the user leaves the same bug elsewhere.

Repeated identity failures need the [upstream character diagnosis](../../music-video-director/references/generation.md#lock-character-and-performance) before another motion retry. Compare the reference, anchor, actual provider derivative, generated output and Resolve placement. A prompt-only retry cannot repair the wrong input or a stale timeline consumer.

For full-film review, first inspect macro story order and coverage, then review in manageable contiguous sections (10–20 seconds is a useful starting point). Overlap the section boundaries enough to see every handoff. Add a dedicated inventory of all transitions, lyric cues, message panels, tracked surfaces, and ending events. Section sampling supplements continuous playback; it cannot substitute for it.

Also inspect every planned shot's critical content and focal sharpness at delivery resolution. Include the first/middle/last and the moving subject's edge extrema. A note that a source shot starts with tight headroom is an observed defect to resolve when the head is cut; lack of normal-speed playback does not make it harmless. A lyric cue can be readable yet badly integrated into the composition. A planned transition that never rendered is an unmet design choice. Use [composition-and-finish.md](composition-and-finish.md) and its exact-render event matrix to find these before reporting a review candidate.

## Repair in a duplicate and compare

Checkpoint the current project/timeline. Change the smallest unit that explains the defect. Render a diagnostic of the actual corrected timeline with its incoming and outgoing handoffs. Compare old/new at identical frames and playback speed; record the visible improvement. Once the diagnostic works, propagate the fix to equivalent occurrences and render the requested deliverable.

Keep candidate and predecessor recoverable. Accept the candidate only when it fixes the named defect without degrading locked identity, action, performance, palette or readability. If it regresses, retain/reinstate the better take for that feature and redesign the repair within the attempt limit. More generation or a larger version number is not improvement.

For a full-film request, show the integrated complete film alongside any useful diagnostic, with changed ranges identified. The user needs its musical/spoken/action setup, neighbors and consequence to judge the revision. A requested range gate still controls editing and approval; contextual review does not authorize changes beyond it.

After source replacement, framing, flip, retime, nesting, or track changes, invalidate dependent transitions and overlays. They may contain duplicated source paths, old crops, old time maps, or independent source clocks. Verify media hashes and current clip properties in Resolve, not just the generated XML or script. Read back all affected tracks, including hidden, nested, and adjustment layers.

Verify that the full export actually contains the diagnostic's new pixels. A correct Fusion graph or short render can coexist with stale cached output in the full render. If they disagree, inspect render range, selected timeline, cache/proxy state, comp activation and MediaOut; refresh only the affected state using supported controls, then rerender and compare. Do not keep rewriting a correct graph to compensate for stale output.

## Review by failure mode

| Risk | Required observation |
|---|---|
| Story regressions | Chronological actions and reactions, relationship distance, time/place, sender/recipient, and requested payoff remain coherent. |
| False full-motion claims | Moving source coverage includes opening, inserts, transitions and tail. Inspect actual character/environment movement; an editorial push or changing grain is not new generated action. |
| Glitch-like or unfinished transition | Effect has readable entry, movement, landing and clean exit at normal speed. Check source continuity, face visibility, edges, matte bands and the next second. |
| Hidden compositing defect | Look for partial dark overlays, inset rectangles, strips of incoming video, stuck silhouettes, incomplete masks and guide-like lines. A black-frame scan cannot detect all of these. |
| Typography/message defect | Inspect every cue through entrance, full display and exit, especially the longest line and moving close-ups. Confirm actual glyphs, padding, contrast, unclipped descenders, face clearance and no spill into the next scene. |
| Cropped or unfocused focal content | Inspect first/middle/last and edge extrema of every shot at full resolution and delivery size. Protect heads, architecture and key actions; compare the source and render to locate the defect. |
| Technically legible but weak lyrics | Compare alternate placements in the actual rendered picture and check hierarchy at phone size, including repeated cues and close-ups. |
| Unrealized transitions | Compare every join's intended effect or cut with the actual rendered behavior; fix unsupported API paths or record a reviewed design change. |
| Repetition | Compare adjacent and returning inserts by source range, order, scale, action and musical function. Renaming one repeated montage does not create variety. |
| Unintended change | Compare canonical/authorized audio, timing, unaffected shots, enabled tracks and approved graphics against the checkpoint. |
| Wrong delivery | Bind render job, timeline identity, settings, file hash, decoded frame count and review record to the same final version. Open the actual review path. |

## Evidence and completion

### Two-pass full-film refinement

For a substantial whole-film polish, use at least two review loops unless the user sets a different review scope. Narrow corrections need the affected ranges, their boundaries and equivalent occurrences rather than two unrelated full-film passes.

1. **Find and repair:** Review contiguous sections, usually around ten seconds with overlapping boundaries, against the accepted brief. Record timestamped observations for attention/pacing, story/emotional fit, identity/performance, motion/transformations, palette, typography and audio sync. Add frame-by-frame checks for suspect events; a regular sampling grid can miss them. Repair observed defects in a checkpointed timeline.
2. **Verify improvement and regression:** Review the newly rendered revision through the same sections, including untouched neighbors and the ending. Compare against the predecessor and confirm that the targeted improvement survived integration without reopening earlier corrections. Record remaining defects honestly and keep a better predecessor where the candidate fails.

Bind each loop to its actual export hash and reviewed ranges. Reuse the existing quality criteria and rubric; support any rating change with visible/audible observations. Quantify duration, cue/transition coverage or repeated source ranges when useful. Catchiness and sophistication require editorial judgment, and a quality score does not predict virality. These loops supplement full normal-speed playback with sound; neither sampled frames nor two records can stand in for actual perception. If viewing/listening is unavailable, mark those parts pending rather than claiming two audiovisual passes.

### State the evidence

Keep separate states: `MEASURED`, `FRAME-INSPECTED`, `WATCHED AT NORMAL SPEED`, `HEARD`, and `USER-APPROVED` when the user is the gate. Record exact file/revision, scope, method, findings and unresolved defects. A scoped “looks good” approves only that scope; later changed pixels require another check.

Use the structured timed coverage in [quality-gates.md](quality-gates.md). A full export requires watched and heard coverage of its full duration. The checker verifies the record and coverage, not whether the agent actually perceived media. Never fabricate a viewing session. Make a reasonable attempt with the available player/audio tools; if unavailable or the Mac is locked, finish independent checks, apply [the diagnostic/production boundary](production-workflow.md#when-perception-or-a-required-technique-is-unavailable), and disclose the precise outstanding evidence on any candidate handoff. Do not operate blind Resolve dialogs while locked or restart a healthy application just to evade the lock.

Before reporting “done,” close every correction in scope using rendered evidence; verify later passes did not reopen earlier defects. Check the per-event finish matrix and the project quality manifest under the current skill template. A missing matrix, missing manifest or stale copied policy cannot be described as a passed quality gate. Deliver the review file plus editable checkpoint and concise changes. A requested integrated replacement includes the replacement in Resolve and its preview render. A requested full video requires a full export. Publication remains a separate authorized action.
