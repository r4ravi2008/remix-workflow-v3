# Independent RoleIndexV2 decoder A01 parent source review

No additional P1 or P2 was found in the complete structural decoder.
Independent source review remains pending. The decoder has not executed.

Root read all 781 source lines, 268 contract lines, and 111 rationale lines.
Root reread the A06 observation model and canonical wire, and the exact A07 nested-tag contract.

The source is 23,381 bytes, SHA-256 `57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b`.
The contract is 7,192 bytes, SHA-256 `679df5d0e6dcd3997c7b4a582ca8b6fa7a4ca9504baf217d8e5f98c182650b31`.
The rationale is 4,131 bytes, SHA-256 `091c8528a88d6d1728aa04b16a6d695fb4cf31781de33eee09ae8b11ac2cbf28`.

The decoder contains independently literal enum branches and imports no encoder implementation or constants.
It reads the exact magic, schema, role order, kinds, fields, nested tags, options, lengths, and signed big-endian values.
It rejects invalid path/role/UTF-8/Boolean/file-mode/size facts and unknown tags.
It preserves null directory fields and exact scalar payloads.
It checks reference existence, symlink target kind, trailing bytes, and complete graph acyclicity.
The bounded Kahn traversal handles repeated references by retaining and decrementing every edge.
The 4,096 dependency ceiling supports more than 64 inputs without a fixed bitmap.

The decoder observes no filesystem object and recomputes no adapter-specific Boolean or alias relation.
It validates structural bytes only and creates no accepted loader or trust root.
The caller still owns source-file admission before immutable input allocation.
Logical encoded-byte bounds do not establish Python allocator overhead or process RSS limits.

A later reviewed control must compare every decoded field against an independently fixed logical fixture.
It must bind the complete vector bytes, byte count, and SHA-256, and exercise the required negative matrix.
No decoder, fixture, compiler, native, media, GPU, Resolve, playback, hearing, or creative acceptance occurred in this review.
