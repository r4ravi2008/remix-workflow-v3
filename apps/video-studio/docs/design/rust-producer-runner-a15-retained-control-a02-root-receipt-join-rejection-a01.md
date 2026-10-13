# Runner A15 retained controls A02: ROOT receipt-join correction

ROOT adds one P2 to the retained A02 source rejection. The current ROOT total
is zero P1 and two P2 findings. Preserve the earlier review and disposition.
A03 is still being prepared; the author was informed before its source freeze.

## Actual receipt shapes

Accepted shared utility A04 `save_at` returns exactly four receipt fields:
`path`, `bytes`, `sha256`, and `identity`. ROOT read its complete implementation,
including the return at lines 200-201 and the full nine-field saved identity.
The compiler wrapper assigns its returned measurement receipt directly to
terminal `compileMeasurements`. Its saved terminal therefore carries all four
fields. This is the existing actual terminal schema.

Retained A02 lines 172-174 compare `terminal['compileMeasurements']` to
`receipt_reference(build_record)`. That helper deliberately returns only
`path`, `bytes`, and `sha256`. Four-field and three-field dictionaries cannot
be equal, even when they describe the same stable measurement file.
Every valid actual compiler terminal would fail retained preflight.

A03 must compare the terminal measurement receipt with the complete held
`build_record`, including its actual nine-field identity. External ROOT
readback references may retain their deliberately specified three-field shape.
Do not change the compiler terminal or native schemas to fit an incorrect
projection. This P2 is independent of the earlier raised-call execution fact.

## Remaining scope

This later correction supersedes the earlier claim that every other receipt
join passed ROOT review. Peer additive review remains pending. No candidate,
compiler, control, supervisor, utility, bootstrap, authorization, native, media,
GPU, playback, listening, or creative action ran for this check.
