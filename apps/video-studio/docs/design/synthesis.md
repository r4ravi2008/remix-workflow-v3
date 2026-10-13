# Selected design

Use Candidate A's persistent project aggregate.
The parent agrees with the independent judge's 25.5/30 versus 16.5/30 assessment.
Both complete candidates and their sketches were read before selection.
No candidate dropped out. Available reviewers are GPT models; cross-family review was unavailable.

## Caller contract

`Studio::create_project` creates an immutable initial revision with a stable intent.
`Project::commit` stages immutable imports and atomically validates and advances a revision.
`Project::export` prepares, persists, executes, reopens and reconciles a movie export.
`Project::prepare_export` and `Project::execute_plan` expose the same immutable plan when inspection helps.
`Project::record_review` stores evidence against exact revision, plan, output and renderer hashes.
`Project::evaluate_policy` reports pending or failed evidence without inventing perception.
The direct CLI adapts these operations. Effect adapters own tenant authorization and external jobs.

## Grafts and corrections

Graft Candidate B's immutable evaluation plan into the private export implementation.
Graft its canonical audio binding, richer stored lineage and promoted-but-unreceipted recovery state.
Keep Candidate A's native presentation-sample index, checked media ticks and explicit representation map.
Persist origin declarations in every stored asset; an import must not lose generation receipts.
Separate timeline and source sample clock domains.
Bind usable ranges and supersession to immutable assets and review evidence.
Key each application mapping, job, attempt, review and worker claim by tenant.

Reject Candidate B's dangling graph roots, string-parameter effects and nominal-rate source-frame authority.
Reject mandatory caller coordination of renderer stages.
Reject any pilot certificate that accepts a later final artifact.
Reject implicit font fallback, proxy substitution and provider retry after an unknown submission.

## Verification status

The native experiment now reopens a 24-frame H.264/AAC MP4 successfully.
Every video PTS is exactly n/24. Independent MP4 parsing finds 24 video samples.
Independent native audio reading returns 48,000 stereo PCM frames at 48 kHz.
The AAC sample table contains 50,176 ticks; the reader trims 2,176 ticks to the one-second presentation.
Waveform lag is zero on both channels. Correlation is 0.9999769 and 0.9999687.
First-frame PSNR is 42.70 dB. These observations apply only to this bounded fixture.
Clippy passes with warnings denied. Playback, listening and creative acceptance remain unverified.

The judge's earlier receipt snapshot said reopening was pending.
The newer measurements supersede that status, not the historical design judgment.
The native AV1 first-sample probe succeeds; VP9 remains explicitly unsupported.
Full original-source indexing and arbitrary movie composition remain implementation work.

## Build units

Start with one native library crate and one thin CLI crate in a workspace.
Use private modules for model, project storage, planning, review and macOS media.
Extract crates only when an independently enforced dependency boundary requires it.
Keep experiments outside the product workspace until their ownership and recovery rules are implemented.
Build and verify complete behavior units. The full general editor and Panja acceptance remain the goal.
