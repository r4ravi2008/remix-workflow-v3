# Picture motion and fades design task

Design the next bounded unit on the A13-reviewed static picture compositor.
Compare independent typed property curves with complete typed picture-pose keyframes.
Read the whole shape of each candidate before selecting a base.

The caller submits project data through the existing commit and export interface.
The library owns normalization, validation, frame evaluation, native workers and output evidence.
Do not expose reader, compositor, writer or temporal coordination stages to callers.

The unit animates signed integer destination rectangles and opacity.
Specify the clip-local integer-frame clock, linear and step interpolation, endpoint behavior, and exact rounding.
Specify how absent fields inherit static placement and how plans normalize that inheritance.
The normalized plan must bind the behavior of every output frame.

Keep source presentation mapping and the single identity PCM clip unchanged.
Do not add source retiming, audio envelopes, masks, rotation, alpha-bearing inputs or color management.
These remain separate general-editor units.

Snapshot schema1 absent-field bytes, plans2/3/4 and receipt2 must retain their exact hashes.
Only animation should select the new plan schema.
Do not duplicate the timeline or source trace in another plan or receipt.

Derive visible temporal coverage from the evaluated content rectangle and quantized opacity.
Consider motion through an off-screen interval, zero-opacity endpoints, source bars, sparse overlays and overlapping handoffs.
Preflight must admit the executor's actual source, cache, raster and handoff schedule before decoding.
Runtime reservations remain logical picture-payload accounting, separate from measured process/native memory.

Native framework objects stay in the existing completion callback scopes.
Only owned Rust pixels and scalar observations cross channels.
Keep cancellation, epoch ownership, port closure and worker joining intact.

The proof must use actual simultaneous movie readers and PNG layers with movement, resizing and fades.
Check every output frame, source ordinal/PTS, output PTS, placement/overlap region and reader EOF with separate code.
Declare exact pure-pixel behavior and lossy-output comparison thresholds before execution.
Include synthetic offset PCM, actual canonical24-bit PCM, legacy output readback and malformed-plan/cancellation checks.

The saved A08 source is the prior verified state.
Technical motion proof does not establish watched, heard, story or creative acceptance.
