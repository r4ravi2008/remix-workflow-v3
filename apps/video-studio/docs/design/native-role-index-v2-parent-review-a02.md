# Native RoleIndexV2 A02 parent source review

Disposition: scoped source repairs pass for the two fixed commands. Independent
review, compiler compatibility, controls, and cross-decoder equality are pending.

The parent read all six Rust files, five documents, the source manifest, and
every logical-fixture row. The parent read the logical JSON through a compact
lossless display. No encoder or decoder produced those displayed values.

The parent reopened all 24 file-backed bindings: thirteen package files,
eight predecessor/decoder bindings, two designs, and one peer review.
Every current identity matched. The thirteen package files total 181,791 bytes.
The earlier author message reported 22 bindings; the manifest contains 24.

Manifest: 5,369 bytes, SHA-256
`ebe268388896fb97ac46277aea71c43d1dfdb13af22ed10cbdc8c9f8c8241c98`.
The independently recomputed aggregate is
`1ddbbaf55adb2e183363d3b88062697c66c533e735be03e905674d525e18215a`.
Its domain, path order, lengths, and raw digest encoding match the manifest.

## Source repairs

The encoder counts complete encoded bytes before structural graph allocation.
It uses the immutable row slice for both encoding passes. Its bounded sinks
check every append. The graph borrows references and precharges edge pairs,
indegrees, offsets, and queue slots under the separate 32 MiB logical cap.
Duplicate references contribute separate edges and matching indegree updates.

Generic structure now permits empty indices, duplicate ordered references,
same-role alias endpoints, scalar paths above 4,096 bytes, and empty relative
components. It still rejects invalid grammar, field bounds, option presence,
missing references, wrong symlink targets, and cycles. Alias and directory
semantic facts remain adapter-owned. The fixed fixture comparison does not
qualify observed filesystem truth.

The logical fixture states all fields for 79 rows and the ordered 65-element
dependency list. Its descriptive variants match the inspected Rust fixture.
Its SHA-256 is
`fb45c24ecee8a80a3787c7f9a211c0758d058b64949c89bbd535023ce507efaf`.
The independent controls must derive expected fields from this frozen JSON.

The CLI consumes three arguments individually and checks byte limits before
UTF-8 retention. Ordinary structural failures use bounded counts or validated
roles. Terminal JSON is capped at 32 KiB. A failed exclusive write may leave a
partial file; durability and parent-descriptor authority remain unclaimed.

## Limits

The fixture adapter compares with a second model from its own Rust constructor.
That check alone does not prove the constructor matches the logical JSON.
The later independently derived every-field comparison remains required.
The general error constructor truncates an already constructed String; it does
not establish a physical allocation bound for arbitrary future callers.
The two fixed commands consume bounded arguments and fixed fixture rows.

The parent did not read all 87,788 patch bytes; complete current source and
predecessor source were read directly. The patch identity matched its manifest.
No Rust source parsing or formatting ran. No compiler, encoder, decoder,
control, vector, loader, gate, native framework, or media operation ran.
No acceptance authority exists.
