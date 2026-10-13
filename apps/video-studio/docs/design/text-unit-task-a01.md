# Native text unit A01 task

Produce a candidate architecture for one bounded native text and story-graphics capability.
The grounding is `text-grounding-a01.md`; read it in full before designing.
Use architect's runner prompt and rationale template. Read current source at every proposed seam.

## Required caller result

The existing `Project::commit`, `prepare_export`, `export`, `verify_export`, cancellation and reconciliation operations must remain the complete caller workflow.
The caller imports exact licensed font bytes and authors text in the project snapshot.
The native renderer shapes and draws in process with CoreText and CoreGraphics.
It must never register a font globally, look up a system family, silently substitute a font, or invoke a renderer subprocess.

The first unit supports exact UTF-8 without normalization, one static SFNT face, explicit language and LTR direction, one solid RGBA8 style, and single-line text.
TTC/OTC, variable fonts, color fonts, bidi paragraphs, wrapping, per-range styles, rotation, effects and animated strings are deferred with explicit rejection.
Telugu and a second complex Indic script are required technical fixtures.
This general capability does not add film lyrics or change the canonical song.

Text joins the existing bottom-to-top picture ordering, sparse spans, signed clipping, opacity and axis masks.
Fixed raster dimensions are required initially; x/y/opacity motion may be reused if its contract is exact.
No width/height animation or glyph-mask resampling is required.
Invisible text cannot fabricate positive frame coverage.

Exact font bytes, face table identity, text bytes and UTF-16 coverage, language, direction, size, style, layout, glyph observations, native backend and raster policy must be bound.
Preparation and execution use one policy owner. Execution reshapes and compares immutable preparation evidence.
No native framework object crosses a track channel.
Allocation admission precedes owned allocations; bounded native calls retain an explicit cancellation limitation.

Snapshot schema1 and all existing Plan2–7/Receipt2–4 bytes and behavior remain exact when text is absent.
Font storage must not pretend that a font has a timed SourceRange.
Every new-plan gate in replay, render, verify and recovery must use the same central validator.
The existing BuildIdentity and output profiles remain unchanged when text is absent.
Freeze a real Plan7 legacy serialization fixture before runtime integration.

## Candidate deliverables

Write caller usage first, then complete type/signature sketches, module map, normalized identities, pseudocode, rationale and alternatives.
Resolve all twenty decisions in the grounding document.
State exact caps, quantization, raster coordinate transform, face fingerprint algorithm, font rejection rules and alpha rounding.
Include an isolated native feasibility probe as the first implementation step, before product integration.
Describe independent shaping/raster fixtures, exact pure vectors, tamper controls and ordinary native output proof.
Use `not implemented` bodies; do not modify or build the product runtime.
Do not edit the other candidate, judge, frozen proof files, project state, film metadata, GPU or Resolve.

## Architect phase list

1. [x] Ground current source and installed native APIs.
2. [ ] Sketch two structurally distinct complete candidates.
3. [ ] Agree through parent scoring, independent judging and synthesis.
4. [ ] Implement a selected isolated feasibility probe, then the bounded runtime contract.
5. [ ] Scrap and re-ground if probe or implementation reveals a wrong architecture.

## Arena phase list

1. [x] Frame the task and private comparison rubric.
2. [ ] Fan out candidates to isolated paths.
3. [ ] Cross-judge complete candidates.
4. [ ] Pick after reading both in full.
5. [ ] Graft the useful alternative decisions into one coherent contract.
6. [ ] Verify the synthesized design and native behavior.

All review agents available here share the same model family. Review independence is task and artifact separation, not model-family diversity.
