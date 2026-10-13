# Native picture layers unit A01

The selected design is bounded track workers with one ordered compositor.
Read `layers-judgment-a01.md` for the independent comparison and rejected alternatives.

The caller still uses `Project::commit`, `prepare_export`, `export`, and `verify_export`.
The timeline track vector defines bottom-to-top picture order.
An optional clip field adds placement:

```json
"placement": {
  "destination": {"x": -50, "y": 30, "width": 320, "height": 180},
  "opacity": 0.5
}
```

Snapshot schema remains 1. New optional fields appear last and omit absent values.
Multiple nonempty picture tracks or an explicit placement select plan schema 4.
Every schema 4 video use receives normalized placement. Absence means the full canvas at opacity 1.
Single-track plans without placement retain schema 2 or 3 and their legacy execution.
Artifact receipts remain schema 2. Their plan hash binds exact layer semantics.

The new pure compositor uses opaque BGRA inputs and opaque rectangular layer rasters.
It rasterizes only fitted source content intersecting the destination and output canvas.
Contain bars generate no pixels. Signed clipping preserves the original sampling rectangle.
Each selected movie frame must have alpha 255. PNG import keeps its existing opaque-input rule.
Working-color conversion, alpha-bearing sources, masks, animated transforms and rotation remain separate work.

Opacity has a finite float64 value in `[0, 1]`.
Execution rounds it to a fixed-point weight in `[0, 65536]`.
This gives an exact midpoint and exact endpoints.
Covered byte values blend with `(source * weight + destination * (65536 - weight) + 32768) >> 16`.
Output alpha is 255. This is coded sample-value arithmetic, with no managed-color claim.

Visible content and nonzero quantized opacity determine temporal contribution.
The visible union must cover the full timeline. Sparse overlay tracks may have gaps.
Same-track overlap remains invalid. Cross-track overlap is valid.

Native execution uses at most four nonempty track workers and one compositor.
Capacity-one request, response and composed-frame channels carry owned Rust pixels and scalar observations.
Framework objects stay inside native completion callbacks.
Cancellation preserves the shared export cause, closes channels, cancels guarded readers and joins every Rust worker.

An interval sweep admits the source/raster/cache schedule before decoding.
The admission policy is 512 MiB. Runtime reservations bound logical application-owned picture payloads.
PNG temporary storage and its configured decoder allowance are charged separately and decoded serially.
Reservation counters are not process-memory measurements. Allocator capacity, PNG internals and native buffers remain distinct.

The pure core, planner and native layer execution are implemented. Sixty-nine tests pass.
The first bounded fixture uses simultaneous movie readers, sparse PNG layers, signed placement, opacity, and exact synthetic stereo audio.
The initial independent reference used source-center coordinates as Pillow EXTENT edges. Its failed report remains saved.
The corrected reference passes every frame and placement/overlap region. Minimum full-frame PSNR is36.1206dB.
Source clocks, output EOF and synthetic audio comparisons pass. The updated producer exported fresh synthetic and canonical-audio fixtures.
The fresh72-frame A02 output has identical decoded pixels, PTS and PCM to the independently compared A01 output.
All72frames,176placement regions and112pairwise overlap regions therefore retain their declared34dB comparison gate.
The separate canonical48-frame regression passes every picture, source/output clock, container and output EOF check.
All96000stereo sampleframes match the actual24-bit master prefix at zero offset, with similarities above0.99997.
The canonical proof binds source sequence ordinals/PTS, held OG ordinal1560, PNG descriptors/RGBA, every imported file and the exact producer/observer.
Historical receipt readback passes without replacing the original206-frame movie or receipt.
The saved producer report separates admission estimates from live logical permit high-water. Reopening does not reproduce these counters.
Watching, hearing, maximum-bound throughput and full-film creative acceptance remain separate requirements.

Review A13 accepts this bounded technical unit with no remaining P1/P2 finding. Full-film and perceptual acceptance remain pending.
