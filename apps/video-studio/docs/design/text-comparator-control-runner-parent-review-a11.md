# Comparator control runner A11 parent design review

Disposition: two P2 findings remain before implementation. The parent read all
523 design lines and inspected the saved A09 entry observation and comparison.

Reviewed design: `text-comparator-control-runner-design-a11.md`, SHA-256
`a4d388ce66f9d47d9d160ac3e8c60399dc61cacf21a34eff43dbd21bc91946f6`.

## P2: domain identity omits three symlink identity fields

`ObservedSymlink` at lines 147–158 and its encoding at lines 390–392 omit
`bytes`, `mtimeNs`, and `ctimeNs`. The actual A09 entry has all nine identity
fields. The design promises every authority identity field participates in
the four-phase comparison. Retain and encode these three fields explicitly.
The primitive timestamp widths must cover the fixed A09 values.

## P2: canonical writer and domain vector remain underspecified

Lines 414–415 permit RFC 8259 control escapes without selecting their exact
form. Multiple forms can encode the same control character. Specify one exact
encoding for every control character and add a fixed escape vector.

The `domain-one` row at line 488 does not state the synthetic observed-file,
symlink, or endpoint field values. Its length and hash cannot be independently
reconstructed from that row. Publish a complete logical fixture with every
field value, without depending on the eventual implementation. Regenerate
the vector after adding the omitted symlink fields. Freeze all vector inputs
and expected bytes before implementing the digest module.

The A09 raw report binding, exact string policy, separate overlay schema,
named digest facets, and separation of phase counters from identity resolve
the previously reviewed design gaps. The remaining A10 capture and publication
requirements must be retained through an explicit exact-version reference.

The A09 report was saved. Its repaired parent readback is still under source
review; A01 execution did not establish accepted reusable readback verification.
No runner, comparator child, compiler, native, or media operation ran here.
