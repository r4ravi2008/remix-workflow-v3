# Parent Rust probe source review A01

The parent read all 5,523 Rust source lines and the complete Cargo manifest, schema and rationale.
The package remains unbuilt and unexecuted. Preserve A01 before repairing a separate A02 package.
No native failure is established by this source review.

## Execution blockers

1. **The retained-observation reservation has no checked representation derivation.** A fixed 4 MiB permit covers every parsed record, repeated shaping tree, copied face-table identity, setter trace and temporary glyph conversion. Per-case caps alone do not prove their aggregate fits. Account actual vector capacities and coexisting conversions before allocation, or derive a conservative checked aggregate from every representation and enforced count. The exact inputs total 104 UTF-16 units and 251 UTF-8 bytes, but the implementation does not currently use those totals to close this representation bound. Do not replace the reservation with an unmeasured assertion.
2. **Hash scratch is undercounted.** `sha256_file_raw` allocates a 64 KiB `BufReader` and a separate 64 KiB stack buffer. The frozen ledger reserves only 64 KiB. Use one buffer or charge both, and recompute the largest overlap.
3. **Failure observations are discarded.** `run_repetition` obtains complete shaping evidence and then calls `validate_shape_structure` before saving it. A range, image-bound or run-status rejection leaves only an error string. Preserve the complete causal shape before validation can reject it. Likewise preserve actual selected-face inventory details on quick mismatch and table-length/hash failures. Never convert these mismatches into acceptance.
4. **Repeat stability omits the reference surface.** The clip mask hash is compared across repetitions, but the full clip-reference hash is not. Every complete supported draw must have stable geometry, counts, bounds and bytes. Include clip-reference evidence. Independent native PNG output remains separately observed.
5. **A permit ends before its buffer lifetime.** `run_orientation` drops the canonical-copy permit while its 221-byte vector remains alive through the native RGBA snapshot. Drop the buffer first or retain its permit through the buffer's final use.

## Required boundary corrections

- Bound input reads before allocation. `read_admitted` currently calls `fs::read` after a metadata-size reservation and checks the resulting length afterward. Keep the exact frozen-input checks, but enforce the admitted read extent before vector growth.
- Bound event serialization during writing. `EventLog::append` uses `serde_json::to_vec` before checking 64 KiB. Use a limited writer or derive and enforce a valid preallocation bound for every emitted event. Do not ignore failed event writes while claiming the complete event sequence was preserved.
- Distinguish the constant bound TrueType scalar from actual native observations. The native API returns table payloads, names and metrics; it does not return the original SFNT header scalar. The shared face hash can use the bound scalar without claiming a native header readback.
- Bind exact maximum lengths before copying native PostScript names and framework strings, or include a checked charge for their actual copies. Frozen raw font identity is not a general bound on a foreign fallback face's copied metadata.
- Keep `CGRectNull`, empty and infinite observations distinct. The SDK permits a null context for origin-relative ideal bounds. Do not claim whitespace necessarily returns a particular bound before execution. A failed bound check must retain its complete observation for diagnosis.
- Preserve the hard antialias, guard, clip, source, fallback and matrix gates. Smoothing and subpixel equal hashes remain observational.
- Freeze source/schema, actual lock/features/toolchain/SDK, build command, binary and framework tuple before the first native call. API import and FFI typechecking remain unverified.

## Preserved strengths

The fingerprint domain, two-byte count and four-byte table lengths match the selected contract.
Foreign face inventory is checked before table payload copies.
The context field drops before its stable backing buffer.
Native ImageIO receives the native bitmap snapshot without a manual row-reversal input.
Mask RLE streams losslessly without allocating a second complete canonical mask.
The output tracker uses exclusive creation and reserves the 256 MiB write budget.
The exact three-repeat and decisive antialias gates are present.

These strengths do not override the execution blockers. Product integration, native feasibility,
watching, hearing and creative acceptance remain false.
