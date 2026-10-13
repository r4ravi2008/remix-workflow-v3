# PNG image behavior unit

The editor will import opaque static PNGs and hold them on the existing picture track.
This makes image conditioning lineage representable without inventing movie sample clocks.

`MediaKind::Image` selects `MediaDescriptor::Image` with PNG format, dimensions and decoded RGBA hash.
An image source range contains exactly one sample: `[0, 1)`. Its cadence must be `Hold { ordinal: 0 }`.
Movie timing and prior project revisions retain their existing semantics.
The plan will record image decode evidence separately from timestamp-checked movie evidence.
New image plans use schema3. Historical schema2 plans remain readable without changing their document hashes.

The bounded decoder uses the pinned Rust PNG library in process. It does not launch a renderer or use FFmpeg.
It validates the complete PNG stream, dimensions and expanded pixels.
Supported samples are eight-bit RGB/RGBA and eight-bit or lower-depth grayscale/indexed PNGs expanded losslessly to RGBA.
Sixteen-bit samples, animation and non-opaque alpha are rejected explicitly.
Each decoded image remains within the existing128MiB frame bound.
ICC, gamma and color conversion are unimplemented. Decode receipts describe source sample values only.

The native movie writer frames the decoded BGRA image through the existing contain, cover, stretch and crop operation.
Static image holds, alternating images, a real generated anchor and canonical audio will receive independent pixel and clock checks.
Tests cover non-opaque alpha, corrupt/truncated streams, trailing bytes, ancillary checksums, wrong cadence/range and immutable lineage.
This unit does not implement layers, general motion, color grading, text or scalable audio.
It does not satisfy the film's musical or creative gates.
