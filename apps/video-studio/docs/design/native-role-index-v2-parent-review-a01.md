# Native RoleIndexV2 A01 parent source review

Disposition: rejected before compiler or vector execution. The parent read all
six Rust sources, five documents, and the manifest. The parent matched eleven
file identities and independently recomputed the source aggregate.

Manifest SHA-256:
`f16c1382e436f6eb81ce3f2f590017bd5ed9ce2876432651c485d04211bd7021`.
Source aggregate:
`ffb15798029a9d38367307f4d0a0b71cd66bb479c4fb77321d912f7fb2634b86`.
The eleven bound files total 67,317 bytes. The A01 package remains preserved.

## P2: generic wire validation adds adapter policy

The validator rejects empty indices, duplicate list members or dependencies,
same-role alias endpoints, scalar paths above 4,096 bytes, and empty relative
path components. A06/A07 permit these structures within their other bounds.
The validator also evaluates directory and alias semantic claims. Those checks
belong to exact adapters. Generic wire validation must preserve the same
language as the independently authored decoder.

The located-under prefix check accepts lexical `/root/../escape` if presented
as a domain semantic check. Remove generic semantic qualification. Future
adapters must establish their relationships from fresh observations.

## P2: fixture authority omits fields

The fixture contract cannot define an independent every-field comparison.
Publish descriptive values for all 79 rows, all identities, paths, scalar and
Mach-O fields, options, lists, aliases, and the ordered 65-dependency list.
Freeze this logical fixture before deriving expected decoder results.
Do not share numeric wire tags as the expected-model authority.

## P2: CLI and diagnostics retain unbounded values

The CLI collects all arguments before validating their count or lengths.
Error detail can copy an unrestricted role or render an unrestricted scalar
byte array. Bound argument retention and diagnostic detail before constructing
the retained values. State the exact output cap and test its central path.

## Additional peer finding

The peer review found allocation-heavy validation before the 4 MiB encoded
admission pass. Admit encoded size and aggregate references before secondary
maps or graph storage. Use borrowed reference iteration and a stated logical
secondary budget. A logical budget does not establish a process RSS cap.

The wire emission appeared consistent with A06/A07 in source. No compiler,
encoder, decoder, control, vector, native producer, or media operation ran.
