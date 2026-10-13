# Native text feasibility protocol A01

This freezes the two probe authors' shared input and observation contract before native execution.
It does not report native feasibility or authorize product integration.

## Inputs and process boundary

Use `native-text-unit-a01/synthetic-text-cases-a02.json`, SHA `a461e07c803793baa688b18452287ca73f3ba0e6d0f8c172458a0158e4ab513d`, 14,706 bytes and 15 cases.
Use the exact two fonts and OFL in `font-fixtures-a01/manifest.json`, SHA `04916451ea952d8ada2e5ca2d1171deaa0e1e6c0acd4652cf2bba0a77c057947`.
The pinned source is Noto commit `ffebf8c1ee449e544955a7e813c54f9b73848eac`.
Bind the actual input and font bytes before native construction.

The Rust executable is standalone and does not link the editor crate.
The Swift executable is independent of the Rust implementation.
Use direct CoreText/CoreGraphics calls only. Do not register fonts or look up a system family.
Probe execution is serialized. No GPU, Resolve, provider, production project or export state is involved.
Each run writes to a new exclusive directory. Preserve failures and partial files.
Pin source, dependencies/features/lock, compiler/SDK, binary, host and framework tuple before executing a frozen build.

## Numeric layout and extraction

Each accepted/observational text case uses the same generous authored box:

```text
W=2048, H=1024, native_stride=2048
baseline_top_left=(64,768)
native_text_position=(64,256)
canonical_main[x,y] = native_main[x,1023-y]
```

The size remains the exact case `fontSizeQ16 / 65536`. No geometry derives from ideal glyph bounds.
The text matrix and CTM remain identity and y-up. Apply the complete selected native setter tuple.

The larger guard has G=32:

```text
WG=2112, HG=1088, native_guard_stride=2112
baseline_guard_top_left=(96,800)
native_guard_text_position=(96,288)
canonical_guard[x,y] = native_guard[x,1087-y]
inner_guard[x,y] = canonical_guard[x+32,y+32]
               = native_guard[x+32,1055-y]
```

Compare all main bytes to the inner guard bytes exactly.
Every guard pixel outside `[32,2080) x [32,1056)` must be zero for a generous fixture.
Record ideal bounds and actual coverage independently. The guard observation does not claim universal raster padding.

Also render the `te-basic` case in an intentionally clipped box:

```text
WC=48, HC=48, stride=48
baseline_top_left=(4,36)
native_text_position=(4,12)
canonical_clip[x,y] = native_clip[x,47-y]
```

Render a larger reference with G=64, W=176, H=176, stride=176, baseline_top_left=(68,100), native_text_position=(68,76).
The exact clip comparison is `canonical_reference[x+64,y+64] = native_reference[x+64,111-y]`.
Compare every inner byte. Require nonzero coverage outside that clip in the larger reference.
Clipping is intentional only in this separately named control.

## Asymmetric orientation and stride control

Create an alpha-only 13-by-17 bitmap with stride16. Disable antialiasing for this coordinate control only.
With identity CTM, draw a solid alpha rectangle at native `(x=2,y=3,width=4,height=5)`.
Under the selected row hypothesis, canonical nonzero bounds must be `(x=2,y=9,width=4,height=5)` with 20 bytes equal255.
Raw bytes, padding bytes, canonical hash and bounds must be preserved.
Use a separately expressed native-image observation to establish orientation; matching copied reversal formulas alone is insufficient.
If actual native or image observations contradict the row hypothesis, record failure and reopen the design.

## Shaping and output records

For each case, both programs emit comparable JSON data with these facts:

- exact id/text/language/direction/font-size and observed UTF-8/UTF-16BE expectations;
- selected font raw hash/bytes, glyph count, units per em, PostScript name, sorted table identities and Candidate A face fingerprint;
- complete line UTF-16 range, glyph count, finite Q16 typographic metrics and image bounds;
- visual-order runs with exact ranges/status bits, full six-component text and font matrices, size, variation state and actual face identity;
- glyph IDs, Q16 positions/advances and UTF-16 indices in native visual order;
- whole-item disposition and any explicit error with its causal run/glyph evidence;
- main/guard/clip mask path, byte count, SHA, canonical coverage count/bounds, outside coverage and every comparison result;
- all native setter calls applied to the context, repeated observations, framework versions and logical allocation records.

Use the field shape in the selected A design for comparable shaping data; authors may supply clearly documented probe wrappers.
Freeze each final JSON schema and every wrapper field before execution. The parent must review them before building or running.
Do not add aliases or change interpretations after observing a result.
The comparator must ignore only producer identity, file locations and execution timing. No shaping or pixel field may be normalized away.

Repeat each complete supported draw three times within a process, using new native objects and buffers each time.
Hashes, observations, counts and bounds must match exactly across those repetitions.
Run the frozen executable in a separate fresh process to check retained evidence again.
Zero-coverage whitespace still requires complete source and shaping evidence.
The three rejection cases publish no raster. Only `text_font_fallback` or `text_missing_glyph` can satisfy them.
The two observation-only cases remain unqualified regardless of their pixel result.

## Setter evidence and controls

Bind actual source/call trace for the fixed `Allows` and `Should` setter tuple.
The SDK does not provide matching public getters for all font switches; do not claim native state readback when unavailable.
Use `te-fractional-size` to draw a separate antialias-disabled control and require binary coverage plus a differing hash.
Also record isolated smoothing, subpixel-positioning and subpixel-quantization toggles, with both `Allows` and `Should` values changed together.
Preserve equal hashes as equal observations. They do not prove that a toggle has no effect for all fonts or contexts.
The policy binds the requested native tuple and observed output. It does not claim inaccessible getter evidence.
Unexplained Rust/Swift differences or failure of the decisive antialias control stop integration.

## Probe caps and admission

This probe has narrower caps than the future product:

- exactly the two pinned fonts, each below1MiB;
- at most15 cases, source text at most128 UTF-8 bytes/64 UTF-16 units per case;
- at most64 runs and1,024 glyphs per case;
- at most128 tables, each within the exact font byte extent;
- the exact bitmap dimensions/strides above;
- three repeats, with buffers released between repeats;
- at most4MiB retained structured observations and4MiB final report bytes;
- at most16MiB concurrent explicitly owned logical payload and256MiB written files per process.

Reserve checked component sums before font/table/string/glyph/mask/output allocation.
If both main and guarded buffers, or native and canonical buffers, coexist, charge every copy.
JSON observations must contain descriptors and hashes, not retained full masks or base64 pixel arrays.
The orientation control may contain its bounded221 pixel samples for direct independent checking.
This is a logical application payload claim. Native framework internals and allocator overhead remain unmeasured.
Check cancellation before and after native calls and during bounded copies. Do not claim interruption inside a native call.

## Stop and proof boundaries

Freeze source, policy, schema and build before the first native call.
Preserve a failed or unexpected observation without changing its baseline inputs.
Repair helpers or contracts through new versions, then repeat only the affected valid proof unit.
Passing this protocol would establish bounded native feasibility on the bound host.
It would not establish product support, encoded output, cancellation SLA, process peak memory, lyrics, readability, listening or creative acceptance.
