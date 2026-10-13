# Native RoleIndexV2 A02 independent source review

## Disposition

The frozen Rust A02 source has no P1 or P2 finding for its two fixed commands.
It is ready for a separately reviewed compile attempt.
Compilation, controls, encoding, decoding, and vector comparison remain unverified.

This review is same-family and nonblind.
I authored the independent decoder controls A01 and A02.
I froze the complete A02 expected model before reading any Rust A02 source.
That freeze preserves expectation independence, but it is not independent-source-origin evidence.

No Rust source, control, decoder, encoder, helper, compiler, or native process ran during this review.
No vector or control attempt exists.

## Frozen identities

The reviewed source manifest is 5,369 bytes with SHA-256
`ebe268388896fb97ac46277aea71c43d1dfdb13af22ed10cbdc8c9f8c8241c98`.

The six Rust files are:

| File | SHA-256 |
| --- | --- |
| `src/controls.rs` | `64337e859a2f3d8be20b94f4830bdbe0d202d0fd79b0d764c8e79c934b3f7268` |
| `src/encode.rs` | `e1ee888bd812b13ce120719bab469e331290e4b63d8d7d0feafda966fe90ebe1` |
| `src/fixture.rs` | `4f30d363c509de5af9d3aeb7461b96dda662300c22fc1d6a8a5442686d49a2ab` |
| `src/main.rs` | `cdd88e0fbee17e1ce18de746558d84dedf88c1893dced2a0b2c88fe7dc821d9f` |
| `src/model.rs` | `cd3266505bffa8ef2847a9d165cb9a4ab0fa376179643a624f24d841c1f8a646` |
| `src/validate.rs` | `e52a693d9161b4e3ea6be2aa4dedaa3b2618efdbc23d72772945594435d0f8cb` |

I reopened all 24 file-backed manifest bindings.
All 13 package files, eight predecessor inputs, two designs, and one prior review matched.
I did not independently recompute the custom 13-file aggregate during this review.
The manifest binds aggregate
`1ddbbaf55adb2e183363d3b88062697c66c533e735be03e905674d525e18215a`.

The pre-source-read control freeze used logical fixture SHA-256
`fb45c24ecee8a80a3787c7f9a211c0758d058b64949c89bbd535023ce507efaf`.
The complete fixture contract SHA-256 is
`16fc743d42797e833213dc2cc00dfa6fb3af9d8295f5c8963e86a41035eafb4b`.

## Standards review

No documented-standard breach or actionable baseline smell was found.
Module ownership follows `source-contract.md`.
The model, validator, encoder, fixture adapter, controls, and CLI remain separate.

The repeated tag matches in `model.rs`, `encode.rs`, and `controls.rs` are intentional protocol checks.
They make the fixed wire values visible at each boundary.
They are not an actionable repeated-switch smell in this isolated source package.

## Specification review

### Wire and model

`model.rs` defines all seven observation variants and all nested variants.
Its literal tag values match the accepted A06/A07 wire design.

`encode.rs` emits the prefix, schema, rows, fields, options, and references in the documented order.
All integers use the required big-endian representation.
The signed timestamp fields use two's-complement `i128` bytes.

### Admission and ownership

The first sink counts encoded bytes without graph or output allocation.
It stops above 4 MiB before structural scratch allocation.

The validator counts borrowed references before allocating graph containers.
Checked arithmetic covers edge pairs, indegrees, offsets, and queue slots.
The 32 MiB limit applies before those allocations.

The later output allocation requests the counted encoded capacity.
Every append checks the counted limit and the 4 MiB protocol limit.

These are logical requested-capacity bounds.
They do not prove allocator capacity, RSS, or physical process peaks.

### Structural behavior

The validator accepts zero through 4,096 rows.
It enforces strict role order, unique row roles, field bounds, reference existence, and acyclicity.

Duplicate list members and dependencies remain separate graph edges.
The indegree updates and edge traversal preserve those duplicates correctly.

The validator permits same-endpoint aliases and adapter-owned Boolean facts.
It preserves empty relative components and scalar paths above 4,096 bytes.
It rejects only the structural path cases stated by A06/A07.

The symlink target check accepts only a regular-file or directory-authority row.
Directory option presence follows its selected authority mode.

### Complete fixture

`fixture.rs` constructs 79 sorted rows and 65 ordered dependencies.
Static review found no field mismatch with the frozen descriptive JSON.

The Rust-side `validate_complete_fixture_contract` comparison uses another call to the same constructor.
That comparison cannot prove agreement with the independent JSON.
The frozen Controls A02 every-field comparison remains required.

### Fixed commands

`main.rs` consumes exactly three bounded arguments after the executable.
It rejects an additional argument without collecting the argument list.

Both commands require absolute output paths and exclusive file creation.
A failed write can leave a partial file.
The source correctly claims no parent-descriptor authority or filesystem durability.

Terminal JSON is bounded to 32 KiB.
The control report uses its separate 64 KiB bound.
No command computes or claims a vector SHA-256.

### Pure controls

`controls.rs` covers exact tags, empty input, ordering, row and encoded limits, graph errors, field errors, and adapter boundaries.
The near-limit case charges every duplicate reference as one edge.

The near-limit typed rows are caller-owned control data.
The reported logical scratch covers validator-created containers only.

## Remaining proof boundary

A future compile can prove compatibility only with its recorded toolchain and command.
A future pure-control run can prove only the named source-control cases.

The frozen decoder Controls A02 must later compare every decoded field against the independent logical fixture.
They must also execute all 74 planned results under a reviewed isolated launcher.

`ValidationError::new` truncates after constructing its input `String`.
The fixed commands keep their own argument and error sources bounded.
No general arbitrary-caller physical allocation bound is established.

No reviewed event currently creates a loader, trust root, gate, acceptance record, native permission, or media proof.
