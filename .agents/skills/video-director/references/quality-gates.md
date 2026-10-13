# Component quality gates

Every component has an intended use and an acceptance decision before dependent production uses it. This applies to imported assets as well as newly generated ones. A beautiful standalone image can fail because it does not fit its scene. An accepted set of clips can still produce a poor edit, so composition and final export have separate gates.

## Configure the bar before producing

Select the current category template before copying it into `<video-dir>/quality-policy.json`: [shared video policy](../assets/quality-policy.json) for general work, [news policy](../assets/news-quality-policy.json) for news bytes/factual stories, or the existing [music policy](../../music-video-director/assets/quality-policy.json) for music. Record the template path with the project. For music, preserve existing policy kinds, thresholds and `music-video/` paths; its compatibility CLI uses the music template by default. News audits must explicitly use the news template so factual gates cannot be omitted. If the user explicitly requests a silent video, derive and record a silent category template before production: remove `heard` timed methods, replace `full_playback_watched_and_heard` with full watched/silence verification, and preserve all visual/source/intent gates. This exception cannot apply to missing hearing capability for a requested soundtrack; music/news narration keep their audio gates.

For an existing customized copy run `python3 <video-director-dir>/scripts/quality_gate.py --template <category-template> --policy <video-dir>/quality-policy.json --check-policy`; merge missing template checks while preserving thresholds and authorized overrides. Default to `standard`, with a minimum rating of 3 for every applicable criterion. Available starting points:

| Profile | Minimum | Meaning |
|---|---|---|
| exploratory | 2 | Coherent rough work; noticeable but nonblocking craft defects allowed |
| standard | 3 | Convincing in the intended use; only minor defects that do not distract |
| meticulous | 4 | Deliberately polished; no observed distracting defects in the reviewed scope |

The 0–4 rubric is an editorial judgment scale, not a probability or automated perceptual metric. 0 means unusable/contradictory; 1 means major defects; 2 means usable rough work; 3 means good; 4 means polished. Each rating needs observations, evidence, and reviewer/method/scope. Use `null` for unreviewed or uncertain. Never average a failed face, bad timing, or incoherent scene away with high scores elsewhere.

The user can override thresholds by component kind and criterion, and add criteria or hard gates. Example: “Exploratory storyboard, meticulous faces and motion, standard everything else” becomes a storyboard override of 2, image identity and motion identity/stability overrides of 4, and defaults of 3. “No lip-sync at all” becomes a hard gate when applicable. Record concrete numeric tolerances such as a footage cap or user-required timing tolerance in the relevant gate evidence; do not invent a universal millisecond standard for lyric perception.

Profiles change craft tolerance, not explicit constraints, source integrity, required evidence, or artifact identity. Never lower the bar to clear a failed job or accommodate an exhausted budget. Only the user's changed brief/policy can relax a requested constraint. Every policy change requires re-evaluating acceptance under its new fingerprint.

## Gates by component

The selected category policy enumerates the required criteria and hard gates. The following music-derived examples apply only where that component exists; do not create audio maps or lyrics for news. Mark a criterion `not_applicable` only with a specific reason grounded in the brief, such as “abstract architecture, no faces.” An unexplained N/A is pending. A review must cover the exact asset version and its intended use.

| Kind | Evidence to inspect | Hard failures or missing evidence |
|---|---|---|
| audio | Probe plus listening; correct selected version and complete requested range | Wrong mix, corrupt file, unintended edit or missing vocal ending |
| audio_map | Beat/section overlays compared with listening across the requested range | Wrong audio binding, drift, guessed downbeats presented as measured |
| brief | User requirements mapped to choices, sources and uncertainties | Contradicted request, invented lyric meaning treated as fact |
| storyboard | Timed sequence/shot cards against audio, causal action, anchor plan, feasibility, full-range coverage, and creative proof before production | Missing section/state, hidden timeline gap, broken causal action, incomplete anchor chain, incompatible shot length, unsupported required capability, or unproven central treatment |
| source_selection | Frames/clips plus surrounding source sequence and provenance | Wrong source/character, forbidden final reuse, unsuitable composition |
| image | Immutable original, normalized full frame, 100% focal detail, canvas/matte audit, and chronological neighbors beside identity/style references | Wrong face, softness, broken anatomy, duplicate/regressive story state, incorrect interface, unwanted text/borders, inconsistent active picture, or unusable framing |
| motion | Entire usable clip at playback speed, first/last frames, accepted anchor revisions, reference comparison | Unaccepted/mismatched anchors, endpoint discontinuity, identity drift, morphing, random singing, bad cadence, insufficient usable duration |
| lyrics | Canonical/display text, rendered design at desktop/phone size, actual audio and timed playback | Wrong words/version/script, phrase truncation, missing cues, unreadable, too small/low, visually disconnected or face-covering text |
| story_graphic | Conversation ledger, actual font/panel bounds, complete message arrival/read/exit with the scene and soundtrack | Wrong sender/order, unreadable exchange, overflowing panel, face overlap, lyric/message ambiguity, or spill into the next scene |
| edit | Material brief requirements in the rendered picture, timeline ranges, every shot's focal content/focus, lyric design, causal order, coverage/mix calculation, join inventory, transition handles and rendered joins | Unrealized requested treatment, unaccepted dependencies, gaps, wrong audio, clipped subjects/architecture, soft focal action, unintended all-cuts downgrade, backward/restarted motion, unexplained black/freeze, broken continuity or wrong text semantics |
| wrapper | Embedded film, audio/text ownership and full framed composition | Duplicate audio/lyrics, stale film, stretching or clipped important content |
| export | File probe/decode, freeze/black scan, every shot/cue/join in the exact render, and full final playback with sound | Wrong render/version/settings, unintended black/freeze, cropped or soft focal subject, weak typography/joins, sync/identity/story/ending failure, or incomplete required review |

Apply the same rubric to a transition, grade, crop, retime, or typography revision as a scoped `edit` component with exact ranges and dependencies. If a new component type does not fit these categories, add its rubric before judging it. Do not silently omit a component because it lacks a preset kind.

The storyboard gate `creative_proof_reviewed` binds the [edited-passage proof](production-workflow.md#prove-one-edited-passage-before-expanding) before full production or a substantial redesign. Its evidence names the exact render, reviewed audiovisual ranges and observed realization of the central treatment. For a storyboard-only endpoint, record pass evidence that no motion/edit production is authorized; do not generate a pilot. For a bounded revision or verified inherited treatment, bind the existing proof and the changed-risk check rather than restarting the whole film. The edit gate `creative_intent_realized` maps each material requirement to observed shots/events in that revision. Asset/provider counts and a prose restatement of the brief cannot pass either gate. These checks add explicit intent evidence; they do not replace the criteria or required playback coverage.

For [upscaling](../../music-video-director/references/upscaling-and-restoration.md), review baked video derivatives as `motion` and changed Resolve processing as scoped `edit` revisions, both dependent on the accepted source. Bind the equal-output-size comparison to the exact settings and pixels; recheck identity, temporal stability, focal sharpness and adjacent joins. Source acceptance or larger dimensions alone cannot approve the processed revision.

For an expressive lyric brief, the existing `lyrics` criteria apply to the selected [lyric design](../../music-video-director/references/lyric-art-direction.md): `visual_integration` includes scene/story personality and the verified type family; `motion_quality` includes the requested entrance/hold/exit and theme handoff. Record actual evidence under those criteria, alongside timing, legibility and clearance. A readable generic subtitle does not satisfy an unrealized kinetic design. Apply only the brief's requested treatment; do not require maximal animation for every song.

## News-specific components

The news template adds `claims`, `script`, `narration` and `captions`. Facts, attribution/uncertainty, names/dates/values and verification-as-of evidence must bind the script. The full voice take must be heard against the accepted script. Captions and graphics must preserve qualifications and use rendered native Telugu glyphs. Edits/exports also require audible/visible fact checks, honest image roles and source/disclosure labels. See [news-bytes.md](news-bytes.md) for the evidence and dependency contract. Truth is a hard gate even under an exploratory craft profile; a score cannot compensate for an unsupported claim.

Storyboards use `content_map_bound` in the shared/news policies instead of music's `audio_map_bound`; speech maps and factual script beats are valid content authorities. Shared intent criteria use `intent_fit` instead of assuming every video expresses a song's emotion. Conditional character, generated-anchor or lip-sync gates require pass evidence explaining their absence when they do not apply. No cinematic character requirement authorizes inventing a factual scene.

## Acceptance and downstream use

Keep a quality manifest containing all components in the requested deliverable's dependency graph. Each record binds ID, kind, revision, intended use, artifact path(s)/SHA-256, dependency IDs/revisions, policy fingerprint, component-definition fingerprint, and reviews. `targets` identifies the requested endpoints. Dependencies must include every actual upstream component consumed, including audio, interpretation/brief, storyboard, visual/text assets, and any wrapper. Compare this graph with the real Resolve/media inventory before accepting an edit/export; a manifest cannot discover omitted clips by itself.

A component is eligible for acceptance only when:

1. Its artifact hashes match and its review names the current revision and policy.
2. Every hard gate is passed with evidence. For a conditional requirement that does not apply, record why the condition is absent as pass evidence; hard gates do not accept an unexplained N/A.
3. Every applicable criterion meets its own configured minimum with evidence.
4. Every dependency is accepted at the recorded revision.

Unknown evidence remains pending; known defects fail; changed artifacts/policy/revisions are stale; an otherwise good component with an unaccepted dependency is blocked. None may enter accepted downstream production. An isolated diagnostic preview may use candidate material only to evaluate it, must be labeled provisional, and cannot be promoted or delivered as accepted. Follow [the diagnostic/production boundary](production-workflow.md#when-perception-or-a-required-technique-is-unavailable); provisional labeling does not authorize scaling a pending creative proof. Do not spend downstream generation on a rejected storyboard or image.

Use [quality_gate.py](../scripts/quality_gate.py) to check the acceptance records. Use the existing [anchor_audit.py](../../music-video-director/scripts/anchor_audit.py) for the separate deterministic anchor canvas/name/hash preflight; its success does not approve image quality or story continuity.
For a finished edit of any category, also run [finish_review.py](../scripts/finish_review.py) with the actual Resolve timeline inventory and exact exported file. It requires a recorded decision for every shot, lyric/general text cue and join. See [composition-and-finish.md](composition-and-finish.md).

```sh
python3 <video-director-dir>/scripts/quality_gate.py --template <category-template> --policy <video-dir>/quality-policy.json --manifest <video-dir>/quality-manifest.json
```

It checks hashes, dependency closure, review completeness, policy/version binding, and threshold decisions. It does not watch, listen, verify truthfulness of evidence, or score aesthetics. Its `accepted` result means the recorded review satisfies policy; perceptual evidence must come from actual inspection. Exit 0 means every requested target passes; exit 1 means at least one does not; exit 2 means malformed or stale policy/input. The JSON report preserves per-component outcomes and reasons.
The CLI also checks the project policy against the current category template. A customized policy may set stricter thresholds and extra criteria, but cannot silently omit newer core gates or timed review methods. Exit 2 identifies a stale policy copy. Merge the missing checks deliberately, then review under the new policy fingerprint. The Hello Ammayi v4 project copy claimed migration while still lacking several current gates; inspect the actual JSON, not only its migration note.

Use `--fingerprint-components --manifest ...` to bind reviews to component definitions, including artifacts, dependencies, and intended use. Record these fingerprints only after inspecting that exact version; regenerating a fingerprint is not a substitute for re-review. See the script's `--example` for the exact manifest shape and `--fingerprint --policy ...` to obtain the policy fingerprint. Relative artifact paths resolve against the manifest directory. Review scope must name the inspected duration/frames, references, and intended downstream placement. Store the report with the project records.

## Timed review coverage

The current policy adds structured `timed_review` requirements. For motion, lyrics/captions, story graphics and scoped edits, record a positive `frame_count` from the inspected media and optional `review_ranges` as zero-based half-open frame pairs. Omission means the whole component. For motion, include the whole proposed usable range plus consumed handles; for lyrics/messages, include every cue's full entrance, display and exit, not just its midpoint. Export and music-wrapper reviews always require the whole file, even if a shorter `review_ranges` field is supplied.

Under `review.sessions`, record only viewing/listening actually performed on the component's bound revision. Example fragment for an independently verified 240-frame diagnostic:

```json
{
  "frame_count": 240,
  "review_ranges": [[0, 240]],
  "review": {
    "sessions": [
      {"method": "watched_normal_speed", "ranges": [[0, 144], [120, 240]], "evidence": "Player review of this exact diagnostic; overlapping sections included both handoffs. Findings are in review.md."},
      {"method": "heard", "ranges": [[0, 240]], "evidence": "Listened to the diagnostic soundtrack; cue landing and final phrase checked in review.md."}
    ]
  }
}
```

This fragment supplements the existing artifact hashes, component/policy fingerprints, reviewer, scope, gates and ratings. The checker unions the recorded ranges independently for each required method; overlapping or repeated coverage cannot conceal an unreviewed gap. Frame samples, decode scans and missing evidence cannot satisfy watched/heard coverage. The checker does not perceive media or prove an observation truthful. Never copy example evidence into a real review.

Existing saved project policies remain unchanged until deliberately migrated. To adopt these rules, retain the project's thresholds and constraints, merge the new applicable rules, fingerprint the revised policy, and re-review affected components. Do not silently replace a customized policy with the template or grandfather an old review into the new gates.

## Inspect, repair, recheck

Judge the component against its criteria before deciding a remedy. Log failed criterion, exact timestamp/region, observed defect, and next action: reselect, revise prompt, regenerate, trim to a newly reviewed usable range, retime, reframe, repair timing, or redesign the shot. Trimming is a new revision, with updated duration and placement constraints. Recheck the repaired component and all dependent placements; a cached approval does not survive changed pixels, audio, timing, identity references, or policy.

Use the configured `max_attempts_per_component` and any user budget. When exhausted, preserve accepted work and rejected evidence, then redesign within the brief if permitted. If the required bar remains unreachable, deliver the partial inventory and precise blocked requirements. Never silently substitute lower-quality footage or report the film complete. Missing playback capability permits independent work and bounded diagnostics under the [production boundary](production-workflow.md#when-perception-or-a-required-technique-is-unavailable). Ask for human review only when it is the remaining way to obtain required evidence; provide the exact candidate and checks to perform.
