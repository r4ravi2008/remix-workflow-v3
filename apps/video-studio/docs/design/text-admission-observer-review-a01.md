# Native text admission and observer review A01

## Disposition

The admission arithmetic and retained-copy model are coherent. I found no P1 defect.

Three P2 conditions remain before these helpers can receive proof credit:

1. Correct the padded-mask control. The exact 2,049-by-2,047 case is valid when charged 4,225,008 bytes.
2. Make both Python helpers fail closed under optimized Python, or replace proof-bearing `assert` statements with explicit checks.
3. Bind the actual OFL bytes and the orientation PNG's producer provenance and observer dependency versions.

These findings do not block continued isolated native probe authoring. They block execution-credit for the affected observers until repaired and frozen.

Future product integration remains blocked on measured Rust representations, current media ownership charges, bounded parsing, single-buffer serialization, and actual teardown behavior.

The reviewed files are:

- `text-admission-contract-a03.md`: `704efeb86033c0dedbca0165ab13f84ee99c1a00602ca6f0a99ead6506b4ed9f`
- `verify_orientation_a01.py`: `ed1481ad95694400b4c970aa23b01d7fd1dfcf6f0ba569509f623ae2526fbc3f`
- `verify_input_authority_a01.py`: `8c67bc3a051431ad56e2707b88d25e8735d4a6cb41d49ec35dd48a882551ab9f`

No native probe or observer proof run was performed. This review makes no process-memory claim beyond the declared logical application-owned payload.

## Admission arithmetic

### Retained Plan8 envelope

The component sums are correct:

```text
TypedPlanPermit = 53,477,376 bytes = 51 MiB
JsonPermit      = 67,108,864 bytes = 64 MiB
combined        = 120,586,240 bytes = 115 MiB
128 MiB margin  = 13,631,488 bytes = 13 MiB
```

The source snapshot subtotal is also correct:

```text
source text and curves = 27,262,976 bytes = 26 MiB
256 font records       = 12,582,912 bytes = 12 MiB
source-only total      = 39,845,888 bytes = 38 MiB
```

The contract correctly charges the three persistent text copies separately:

- `S_snapshot` under `SourceOwner`;
- `P_timeline` under `SharedOwner`;
- `P_use_source` under `SharedOwner`.

It also charges transient shaping storage under `GateOwner`. Moved ownership remains one charge. Cloned ownership becomes two charges.

The prepare equations correctly retain source, draft/final plan, gate, JSON, old media, and overhead only where their lifetimes overlap. The execute equation correctly excludes source and draft owners while retaining the shared plan, active rasters, gate, media, channels, canvas, responses, and writer.

### Padded alpha maximum

The declared maximum is correct and unique under the stated integer limits:

```text
width         = 2,049
height        = 2,047
visible       = 2,049 * 2,047 = 4,194,303 pixels
stride        = align_up(2,049,16) = 2,064
charged bytes = 2,064 * 2,047 = 4,225,008
```

The closed conservative bound is also correct:

```text
4,194,304 + 15 * 2,048 = 4,225,024 bytes
```

### Temporary gate and raster overlap

The temporary gate sum is correct:

```text
3 font-sized copies                 50,331,648
UTF-8 and UTF-16                        16,384
glyph envelope                       2,097,152
padded alpha mask                    4,225,008
item, run, font, and table records     315,392
total                               56,985,584 bytes
```

The maximum persistent text-raster calculation is also correct:

```text
one raster = 8 * 4,194,304 = 33,554,432 bytes
four tracks = 134,217,728 bytes = 128 MiB
```

The one shared `Arc` permit prevents response references from becoming extra raster-payload charges. A copied frame surface would require a new charge.

## P2: correct the padded-mask control semantics

The smallest post-probe proof currently lists “a 2,049×2,047 padded mask” among negative controls and then says each control must fail.

That tuple is the valid exact maximum. It must succeed when the permit charges 4,225,008 bytes.

Replace that one control with a paired boundary test:

1. **Positive:** accept 2,049 by 2,047, stride 2,064, with an exact 4,225,008-byte permit.
2. **Negative:** reject before allocation when the same request reserves only visible bytes, 4,194,303, or any value below 4,225,008.

An additional dimension, area, or stride-overflow case may remain negative. The valid maximum itself must not be described as a failure.

This wording defect does not change the correct maximum elsewhere in A03. It must be corrected before the post-probe admission proof is frozen.

## Orientation observer

`verify_orientation_a01.py` correctly keeps three representations distinct:

- 272 raw bytes for 17 rows at stride 16;
- 221 canonical visible alpha bytes for a 13-by-17 image;
- a separately decoded 13-by-17 native ImageIO PNG.

The raw reversal is correct:

```text
canonical[y,x] = raw[16-y,x]
```

The expected native rectangle at `(2,3,4,5)` becomes top-left bounds `(2,9,4,5)`. The observer requires exactly 20 visible bytes with value 255.

The observer also requires all 51 padding bytes to retain sentinel `0xA5`. This closes the padding-initialization condition from the protocol review.

The PNG check is genuinely separate at the observer-input level. Pillow decodes the PNG alpha plane, and the helper compares it independently with both the declared rectangle and canonical raw extraction.

The helper truthfully records that it cannot establish the producer's source lifetime. A matching PNG is independent evidence only after source review proves all of these facts:

1. The exact native producer source and binary are bound.
2. The PNG comes directly from the native RGBA bitmap snapshot.
3. The PNG path does not consume the canonical-alpha file or copied row-reversal array.
4. Raw alpha, canonical alpha, and PNG belong to one exclusive producer run.

Without those bindings, a caller could supply a PNG derived from the canonical file and defeat the intended independence. The current `nativeProducerSourceLifetimeEstablishedHere: false` field correctly prevents that overclaim.

Before use, bind the exact Python, Pillow, and NumPy versions. The final closure must bind the helper, all three inputs, the producer source and binary, and the exclusive report.

## Input-authority observer

`verify_input_authority_a01.py` correctly binds the exact manifest and case-file hashes. It then independently checks:

- each exact font byte count and SHA-256;
- the standalone TrueType scalar and table count;
- table extents, duplicate tags, overlap, directory values, and exact table hashes;
- Candidate A's domain-separated, tag-sorted face fingerprint;
- all 15 exact UTF-8 and UTF-16BE counts and hashes;
- complete zero-based line ranges and exact Q16 sizes.

Its fingerprint encoding matches Candidate A:

```text
domain NUL || u32be scalar || u16be table count
|| sorted(tag4 || u32be length || raw SHA-256 bytes)
```

The report correctly says native face observation, shaping, and rasterization remain false. This helper establishes raw input authority only. It does not prove font admissibility, fallback behavior, shaping, or pixels.

The helper does not read and rehash the actual OFL file. The manifest hash binds the declared license record, but it does not prove that the referenced local license bytes are present and exact.

Before proof use, read the manifest's license path, check its exact 4,377 bytes and SHA-256 `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb`, and include that binding in the report. Also report the pinned repository and commit from the already hashed manifest.

## P2: fail closed under optimized Python

Both helpers use `assert` for proof-bearing validation. Python removes `assert` statements under `python -O` or `PYTHONOPTIMIZE`.

`verify_input_authority_a01.py` could then emit a nominal verification report without performing most of its checks. This is a proof-integrity defect even when the intended runner normally uses unoptimized Python.

Before execution, either:

- replace every proof-bearing assertion with an explicit checked failure; or
- reject immediately when `sys.flags.optimize != 0`, then bind that condition and the exact interpreter invocation.

Explicit checks are preferable. Negative controls must demonstrate that each intended mutation exits nonzero and creates no passing report.

## Isolated observer conditions

The two helpers may be used for isolated evidence after these conditions are met:

1. Correct and freeze the exact padded-mask positive and undercharge-negative controls.
2. Remove the optimized-Python assertion gap.
3. Add the exact OFL binding to input authority.
4. Bind observer dependency versions and invocation.
5. Bind the exact native producer source and binary for PNG provenance.
6. Prove the three orientation inputs come from one exclusive producer run.
7. Add deliberate mutations for raw orientation, padding, canonical rows, PNG alpha, font bytes, table bytes, text bytes, range, size, license, and optimized execution.
8. Preserve failed reports and use new paths for repaired successors.

Passing those helpers would establish their bounded raw-input and orientation claims only. It would not establish complete native text feasibility by itself.

## Future product-integration conditions

A03 remains provisional for product use. Product integration must still supply:

1. Measured `size_of`, alignment, length, capacity, owner, and lifetime rows for every new Rust representation.
2. Checked actual-length or finite-bound charges for current Snapshot, ExportPlan, closure, sample, ordinal, canvas, response, and writer ownership.
3. A bounded token gate and bounded visitor that reserve before Plan8 strings, vectors, and maps grow.
4. One canonical JSON buffer used for hashing and storage, or a separately admitted second buffer.
5. Measured prepare and execute sweeps, including source-plan overlap, four active rasters, one gate, and old media.
6. Exact permit release on comparison failure, cancellation, disconnected response, writer abort, and recovery.
7. The corrected padded-mask positive and undercharge-negative controls.
8. Exact legacy Snapshot1, Plan2 through Plan7, and Receipt2 through Receipt4 readbacks.

Until old-media accounting is finite, Plan8 admission must fail closed. The 128 MiB and 512 MiB envelopes are logical application-owned bounds, not native or process peak-memory measurements.

## Verdict

A03 has correct arithmetic and a credible ownership model. The orientation observer distinguishes raw reversal from a separate PNG when producer provenance is bound. The input helper correctly establishes raw font and source-text authority within its stated nonnative scope.

No isolated observer should run for proof credit until the three P2 conditions are repaired and frozen. No product integration should rely on A03 until its provisional representation and old-media charges are measured and enforced.
