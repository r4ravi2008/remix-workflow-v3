# Supervisor A02 post-drift ROOT disposition

State: **original reviewed source bytes freshly rejoined; source accepted;
unimported and unexecuted**.

The source author disclosed edits after the frozen A02 handoff and ROOT review.
The author changed the supervisor, contract, and manifest, then restored their
original bytes. The rationale did not change. Continuous immutability was
broken. Restored hashes cannot establish continuous identity across that period.

The transient source was 33,753 bytes, SHA-256
`e40418c55ea5a132eec5cd302d165e60fa965567b9ac958a59a48635a7bfec47`.
The transient contract was 5,231 bytes, SHA-256
`f253245aa76aca610db664c780f958d701810cfd097616565fbad225020aa941`.
The transient manifest SHA-256 was
`1385bc318351b0048976c5c5e130308548c0ef1842e4944f0111b2b70f80aed0`.
The peer also observed a partially restored 33,173-byte source, SHA-256
`c907506ee4fdeca3d992f70b3e90d8d1d051f9ac71def6e6b5f39c882e57cc84`.
None of those transient subjects receives acceptance or execution authority.

ROOT fully read the final 7,640-byte peer report, SHA-256
`8aee2f768f6b0d9f3e6fbf18be31dfcad92a9b2af52dff05a36d82b4e04e32ae`.
ROOT then reopened all nine current manifest, source, and external files through
held no-follow descriptors. Every original reviewed byte pin, both aggregates,
and all nine before/after identity fields matched in this fresh observation.
The separate saved rejoin proof explicitly sets continuous immutability false.

The current 33,116-byte supervisor retains SHA-256
`50600911ab331f2c2a03ea814f3783a83007e9b647318a8fe74d7ef3b477a863`.
ROOT and peer source acceptance applies to these freshly rejoined bytes only.
Both reviews found zero remaining P1/P2 within the bounded source contract.

Future callers must authenticate these exact current bytes through their own
held-source and operation gates. No import, control, native, media, product,
watching, hearing, or creative acceptance follows from this source disposition.
