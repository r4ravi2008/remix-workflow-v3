# Upscaling and detail restoration

Use when the user requests upscaling or accepted low-resolution footage needs enlargement for the agreed delivery. Evaluate it after source selection and timing are stable, before the final render. Keep the established delivery resolution unless the user requests a change; a finishing pass does not imply 4K, a new frame rate, or a new creative treatment. An informational question alone does not authorize processing the film.

## Choose the source and processing route

Read the current asset catalog and Resolve timeline. Identify each candidate's native dimensions, active-picture geometry, accepted source range, handles, frame rate, and existing resize, retime, crop, grade and restoration history. Trace a 1080p conform or proxy back to its native original; its container dimensions do not establish native detail. Preserve immutable originals and the accepted edit.

Prefer source-level processing through DaVinci Resolve Studio's Super Scale when available. Verify the installed edition/build and current controls through the live integration or documentation. Blackmagic documents [2x Enhanced with adjustable sharpness and noise reduction](https://documents.blackmagicdesign.com/se/SupportNotes/DaVinci_Resolve_18.5_New_Features_Guide.pdf) and [3x/4x Enhanced in Resolve 20 Studio](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20_New_Features_Guide.pdf). These are capability references, not evidence that a particular clip benefits. Ordinary resizing and increasing export dimensions are not AI restoration.

Resolve uses the hardware on its own host; a workstation reachable through Herdr is not automatically a remote render GPU for desktop Resolve. Verify the actual processing host and available GPU memory, disk, caches and active jobs. Schedule heavy work around an existing generation/render owner. Do not restart shared services or change hardware settings for an upscale pass.

If a separate local video upscaler is justified or requested, use [gpu-footage-generation](../../gpu-footage-generation/SKILL.md) for the existing Herdr session, immutable inputs, bounded pilot and measured memory limits. Honor local-only restrictions. Do not silently substitute a hosted provider, install a large model, or occupy another job's GPU. A model that loads has not proved it can decode and save a complete clip. Temporal models need tested overlap/context and seam review when chunking. Independent generative redraws of each frame can alter likeness and flicker; ImageGen is not a substitute for video upscaling.

## Compare a small representative set

Make an isolated diagnostic using accepted footage: a face close-up, fast action and a style transformation when those occur in the film. Include consumed handles and each complete transformation. A duplicate timeline may still share Media Pool clip attributes; isolate source items or use supported instance-level controls before changing Super Scale so the accepted timeline remains recoverable.

Compare ordinary high-quality resizing with a conservative Super Scale candidate at **identical output dimensions, framing, frame rate, grade and encoding quality**. Start with 2x Enhanced where suitable; select the factor from native size and target size, not the largest available number. Use gentle sharpness/noise reduction and tune from visible results, separately for live action and animation where needed. Avoid stacking AI passes on an already enlarged derivative. Do not enable frame interpolation merely to increase resolution.

Inspect full frames at delivery size and matched face/linework details at 100%, then watch the complete samples at normal speed. Judge:

- Recognizable facial structure, hair/beard, closed-mouth performance, anatomy, hands and props.
- Stable eyes, linework and texture through movement; no flicker, crawling edges, invented detail, ringing, halos, waxy skin or lost ink/grain.
- Fast-action readability and the approved motion blur; sharpening must not invent crisp geometry inside blurred movement.
- Pose, geometry, velocity, palette and apparent sharpness throughout real-to-stylized transitions and across neighboring shots.

A sharper background with a less faithful face fails. Upscaling cannot repair wrong identity, anatomy, missing action, a cropped subject or a rejected transition. If the candidate is indistinguishable or worse, retain the accepted source with ordinary resizing. If the source itself fails the brief, route it to source repair within the existing authorization. Follow the configured review/attempt limits; no new human approval stop is required when autonomous review is already authorized. Missing playback evidence stays pending under the existing quality policy.

## Apply selectively and preserve the edit

Apply only the settings supported by the comparison. Match perceived detail across adjoining footage rather than making one shot unnaturally crisp. Keep original files and separate versioned derivatives when baking a result. For each derivative record source ID/hash, native and output dimensions, engine/version, host, settings, frame count/rate, color tags/data levels, output hash and comparison evidence. Record an explicit bypass decision for shots that do not benefit. Use existing asset/edit records; avoid a second authoritative catalog.

Upscale picture sources before final typography, titles, mattes and composites where the pipeline permits; keep those elements native to the delivery canvas. Do not use the compressed, captioned final export as the default source. If only a flattened export exists, state that limitation and test its text and transition edges before proceeding.

When reconnecting native footage or baked derivatives, preserve source in/out, handles, timecode/offset mapping, existing speed ramps or frame-selection maps, duration, composition, color management and audio ownership. Do not substitute a raw clip for a conformed plate without reproducing its time map. Check for double resizing, duplicated LUTs/mattes and stale caches or proxies masking the change. A resolution change also requires rechecking pixel-based Fusion masks, tracks, transforms, title layout and lyric clearance.

Treat a baked video as a new `motion` derivative dependent on its source; treat changed Resolve processing as a scoped `edit` revision. Revalidate the affected placements, joins and export under [quality-gates.md](quality-gates.md). Old creative acceptance does not automatically cover altered pixels, and greater pixel dimensions do not prove improvement.

## Render and verify the complete film

Read back the correct Resolve project/timeline, source paths and applied settings. Render diagnostics for the risky joins, then the complete requested film to a new versioned destination. Verify duration, frame count/rate, geometry, color, lyric/title layout, unchanged audio timing and deliberate ending. Inspect every affected shot and join in the actual export, including transitions between processed and bypassed footage. Check uninterrupted motion; equal frame counts alone cannot rule out duplicated or dropped frames.

Review the full output in motion with sound before claiming it watched/heard, using [composition-and-finish.md](composition-and-finish.md) and [resolve-and-review.md](resolve-and-review.md). Frame samples, successful rendering and objective metrics support inspection but do not establish perceptual improvement. Report processing coverage, bypasses, observed benefit and remaining limitations; deliver the complete updated film when that is the requested endpoint.

## Reusable finish prompt

Append this to an authorized full-film request and adapt the identity/style constraints to that film:

> After the requested edits are complete, perform an intelligent upscaling finish in DaVinci Resolve Studio. Preserve the approved characters, performances, palette, framing, edit timing, transitions, lyrics, titles and audio. Keep the agreed delivery resolution unless I request otherwise. Work from native original footage, before final text and compositing, rather than the compressed final export. Compare ordinary high-quality resizing against conservative 2x Enhanced Super Scale on a facial close-up, fast action and a real-to-anime transformation at identical output dimensions. Verify likeness, hair/beard, anatomy, linework, motion and transition continuity; reject flicker, halos, invented detail, waxy faces and excessive smoothing. Tune per shot and apply only demonstrable improvements, retaining the original treatment where it looks better. Keep original media and exact source/time-map bindings recoverable. Use local processing and respect active GPU jobs; no paid cloud services. Follow the existing review mode and do not add an unnecessary approval pause. Assemble and render the complete updated film in Resolve, check the exact export in motion with sound, and deliver it with a concise account of improvements and any unverified checks. Do not use upscaling to conceal footage that needs regeneration.
