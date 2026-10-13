# Rust producer runner controls A02 parent source review

Root read the full normalized A01-to-A02 source and contract delta, the manifest, and the recipe. All five rows match, totaling 139,143 bytes. The explicit domain aggregate recomputes to 7421ed2533053ebe893dcebc809017d1ab4db27318f1038bb607d5fbb90b762d. A04 prefix and pure helper are byte-identical. The in-memory concatenation matches 121,285 bytes and ea13054c96d220bff55b386ef6cde6ce4537ef46951b93514e13e1b0af45e0ef. No assembly file or executable was created.

A02 closes the five original A01 groups within static scope. Root found one remaining P2 bound: the new loader polling and pipe readers have limits, but child.wait remains unconditional after kill and on early pipe/nonblocking failures. Failed kill or stalled reap can block the finite case beyond its declared timeout. Replace each loader wait with one bounded try_wait cleanup helper. Preserve actual reap and status facts. Do not change A04 production code or the ten cases.

A02 remains frozen and unexecuted. A03 is a minimal additive repair. Independent A02 source review is pending. No compiler, control, child, native producer, authority, media, or audiovisual acceptance occurred.
