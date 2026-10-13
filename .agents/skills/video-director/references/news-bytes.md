# News bytes and factual stories

Use with [video-director](../SKILL.md) when the user supplies an interesting news item, article, link, excerpt or true story to turn into a video. Telugu is the initial language; the same verification and production contract can support another requested language. If the story is explicitly fiction, label it and use the general narrative path rather than treating invented details as reporting.

## Bind the item and verify its story

Accept a single supplied item as the lead. Read the original and verify the facts needed for the chosen angle; do not require the user to research or send a second article first. A screenshot/excerpt establishes what it says, not that its claims are true. If the item is not supplied yet, the skill setup can finish but episode research and production await that input.

Keep the supplied item, source URLs, publisher/author, publication/update dates, event date/timezone and verification-as-of time. Prefer the original announcement, document, study, data, court record or direct attributable statement. Corroborate material disputed, surprising or consequential claims with suitable independent reporting when available. Several syndicated copies are one evidentiary source. Search and read live sources for current facts; never use model memory as a news feed. Recheck developing stories before finalizing the export and show an as-of date/time when necessary. Use the user's timezone for the episode's reporting timestamp while preserving the event's timezone.

Create `sources.json` and `claims.json` in the project's `video/` folder, or equivalent records already in use:

| Record | Minimum contents |
|---|---|
| Source | Stable ID, exact URL/document, title/publisher, published/updated/event dates where known, accessed-at time, relevant passage/data and its context, credibility/limitations |
| Claim | Stable ID, precise fact and qualifiers, supporting source IDs, status (`verified`, `attributed`, `disputed`, `unresolved`), uncertainty, script/graphic uses, checked-at time |
| Asset | Provenance and reuse basis, depicted event/place/date, intended claim/scene, role (`evidence`, `archival`, `context`, `illustration`, `reconstruction`), required label, reviewed range |

Keep independently verified facts, attributed claims/allegations, analysis and uncertainty distinct in the narration and graphics. Check names, places, units, numbers, dates, comparison baselines and correlation-versus-causation. An official allegation remains an allegation. An estimate remains an estimate. Attribute a statement to its speaker; do not rewrite it as an established fact. Identify translations/paraphrases as such, keep direct quotations short and accurate, and use source links in the handoff/description.

An unresolved material claim cannot become a confident headline, script line or image. Remove it or say precisely what remains unknown with attribution; do not add scenes or specifics to make a thin story dramatic. If it is the story's central premise, finish the evidence assessment and identify the exact blocker before production. Preserve meaningful counterevidence and uncertainty when shortening the story. Hook, cover, captions and ending follow the same factual standard as the narration.

## Write for spoken Telugu

Choose one editorial angle: what happened, why it is interesting, and what the viewer needs to understand. Use a specific supported opening, then a compact cause/context sequence and a useful takeaway or open question that the evidence supports. A long story may need a longer format; do not force it under a target by deleting essential qualifiers or speeding narration.

Draft `script-te.md` in natural conversational Telugu, with claim IDs and pronunciation notes kept separately from spoken text. Use Telugu script for narration, visible titles and captions. Proper names/technical terms may use their established form, explained in Telugu when needed; retain exact source names/URLs in metadata. Do not romanize Telugu or copy English sentence structure word for word. Prefer short spoken sentences, familiar words and deliberate pauses. Read large numbers, dates and acronyms in a form a listener can understand and bind that reading to the exact value on screen.

Use an engaging, clear and proportionate tone. Curiosity can come from a surprising verified fact or a visual explanation; do not invent urgency, certainty, outrage or a “breaking” label. Do not add a subscribe/like outro unless the brief or series identity calls for it. A cautious source must not acquire certainty during Telugu translation. When meaning/pronunciation cannot be confidently checked, flag the exact line rather than claiming native review.

For an unspecified Short, start with a 45–60-second target and this flexible structure:

| Beat | Job | Possible visual |
|---|---|---|
| Opening | Establish the interesting verified fact/question immediately | Specific headline and relevant source image or graphic |
| What happened | State the key development with its qualifiers | Evidence, timeline or labeled contextual footage |
| Why it matters | Supply the minimum context/comparison needed | Map, number comparison, diagram or purposeful B-roll |
| Ending | Land the takeaway, uncertainty or next development | One clear concluding idea and unobtrusive source credit |

These beats can overlap and do not prescribe four shots. Estimate speech duration only for planning; the reviewed voice take controls final timing. A news byte should communicate one coherent story, not a list of unrelated headlines. Longer explainers use the same ledger with enough room for evidence and context.

## Narration, captions and sound

Use a supplied voice take when available. Otherwise use the user's selected voice/provider, or discover a supported Telugu narration tool and select a suitable non-impersonating voice within the authorized scope. Do not invent a TTS integration or switch providers silently. If voice generation is unavailable, complete the verified script, pronunciation notes and shot plan, and report narration as the blocked stage; no silent substitute completes a voiceover request.

Lock the accepted script revision before recording/generation. Save the immutable narration take, provider/voice/settings when applicable, file hash, decoded duration and full listening observations. Check Telugu intelligibility, pronunciation, values, omitted/repeated words, pauses, clipping and unnatural phrasing against every line of the script. Repair an incorrect reading before timing the edit. Captions cannot correct a wrong audible fact.

Create `speech-map.json` against that exact take: sentence/phrase IDs, source start/end seconds, spoken text, claim IDs and planned visual cues. Segment by meaning and breath; beat detection and lyric alignment are unnecessary. Align native Telugu `captions.json` or SRT to the actual speech. Condensed captions may reduce repetition while preserving meaning, numbers, qualifiers and attribution; record deliberate differences from the full transcript.

Keep captions distinct from the headline, emphasis numbers, source labels and illustrative disclosures. Render and inspect Telugu shaping, combining marks, line breaks and glyph coverage. Make mobile reading time and safe placement work in the actual picture; titles or platform controls must not obscure captions, faces or evidence. Verify current platform safe areas/specifications only when targeting that platform. Avoid tiny full paragraphs or simultaneous competing text blocks.

Music is optional and subordinate to speech. Duck an authorized background bed, preserve source sound only when relevant, and choose effects that help the explanation. A dramatic sting must not imply an explosion, event or statement absent from the evidence. Keep narration and captions as single owned roles through nested edits/wrappers.

## Plan images honestly and prove the format

Map each spoken beat to a shot or graphic with an editorial job and claim/source IDs. Choose factual maps/charts with correct dates, boundaries, scales, units and baselines; label uncertainty. Source availability does not itself establish permission to reuse the image or clip. Record the reuse basis and attribution, using supplied/owned/permitted assets or original explanatory graphics where appropriate.

Do not generate a photorealistic “actual scene” of an unrecorded real event or fabricate a person speaking. Use clearly styled explanation, licensed/owned source media or visibly labeled reconstruction. Label archival footage with the relevant context when viewers could confuse it for the current event. An “AI illustration” or “reconstruction” disclosure belongs with the shot when needed, not solely in a hidden description. Inspect the final presentation for misleading juxtaposition even when each asset is genuine.

For a new series treatment, prove the opening plus a representative information-dense passage in the chosen editor with the actual narration, intended mobile text and source/disclosure treatment. Choose a length proportional to the risk; an entire short may be the cheapest proof. Watch and hear it for clarity, pacing, truthfulness of visual implication and readable Telugu before expanding expensive generation. Reuse the style proof on later episodes while verifying each episode's own facts, narration, captions and difficult graphics.

## Review and hand off

Use [news-quality-policy.json](../assets/news-quality-policy.json) as this category's template, preserving project-specific thresholds. Use it for both `--check-policy` and final manifest audits:

```sh
python3 <video-director-dir>/scripts/quality_gate.py --template <video-director-dir>/assets/news-quality-policy.json --policy <video-dir>/quality-policy.json --check-policy
python3 <video-director-dir>/scripts/quality_gate.py --template <video-director-dir>/assets/news-quality-policy.json --policy <video-dir>/quality-policy.json --manifest <video-dir>/quality-manifest.json
```

Include claims → script → narration/speech cues → caption/graphic assets → edit → export dependencies alongside visual/audio components actually consumed. A source or claim correction invalidates every script line, reading, graphic, caption and export that relies on it. A new source confirming unchanged wording requires rechecking its evidence; it need not regenerate unchanged audio. Changed wording or qualifiers require a new script revision and checks of all consumers.

Read back all `text_events` from the actual timeline (role, stable occurrence ID, zero-based half-open `start`/`end`), then run the shared finish checker for every shot, caption/headline/source/disclosure cue and join. Review the full exact short with sound and compare its spoken/visible facts with the ledger. Check the opening claim, natural Telugu, audible values/qualifiers, phone readability, pace, honest image roles, complete ending and clean speech mix. Recheck for late news updates; a stale export needs a revision or clear accurate historical/as-of framing.

For a finished-video endpoint deliver the versioned vertical MP4, editable project/checkpoint, final Telugu script/captions and source/claim/review records. Produce a landscape or longer version only when requested. State factual verification, measured checks, actual viewing/listening, and any user approval separately. A planning-only endpoint delivers its requested records without inventing narration or renders. A completed video does not authorize upload or publication.
