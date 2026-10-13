# Runtime snapshot A09 parent source review

A09 closes the failed A08 declaration assumption at scoped source-review level.
No additional P1 or P2 was found in the reviewed change.
Independent source review remains pending. A09 has not executed.

Root read the complete normalized source change, including the formerly truncated count check.
The source patch has 536 lines, 22,544 bytes, and SHA-256 `16b2125f50d7c01625efb6a15c3eddad2ddabb51063258b7e457ef2d8df7f007`.
The contract patch has 198 lines, 9,064 bytes, and SHA-256 `8c8a9fe54ea43420545ea22749870f759d44b260e18337a5b1c8710076c8ba62`.
The rationale patch has 93 lines, 5,589 bytes, and SHA-256 `12aac33ae2f7b16a945b0df8213e7a79d30a51cee80223cbb285c50c910996ab`.
Root independently applied all three patches in memory and matched every resulting byte against A09.
A first exact difflib regeneration comparison failed because alignment differs from the stored diff.
The checked application verifies every old context/deletion, hunk count, and final source byte.
No frozen patch or source was modified.
Unchanged A08 confinement, budget, descriptor closure, output allowlist, and held final-report read were reviewed previously.

The exact source is 55,732 bytes, SHA-256 `c2ac751a7acdc9327112fad719dab751ba844162b346ff78e296e3eba3783dc4`.
The contract is 14,189 bytes, SHA-256 `bb03fddb685b5a935a2a5f789ed12bcfb42c9252e8395b85e9c6054418e1341a`.
The rationale is 6,202 bytes, SHA-256 `01683726ff727636ac6ef28d1cf894036045cd5dcac8bc911949ea0eae815603`.
The fixed overlay is 25,945 bytes, SHA-256 `975e9dbb05e45718c363ebac762c868cd3c85bc952757c4d3aff017dce11b22a`.
The root diagnostic remains 1,379,634 bytes, SHA-256 `094c49dc02a1933782dba58fb75eb838587b9a6e7ab357a7c45cf0c61e7405d2`.

Root independently reproduced all 45 overlay rows from the exact diagnostic mismatch projection.
The 1,548 diagnostic rows total 45,567,887 bytes.
Exactly 995 rows match both declared values; 508 rows have neither declared value; 45 rows differ in both.
Pillow has 26 divergence rows. NumPy has 19.

The helper binds full diagnostic and overlay bytes before parsing.
It validates complete closed row shapes, exact flags, unique package/path keys, all counts, and the mismatch projection.
Each divergent installed file must equal its fixed path and current byte/hash facts.
Every declared non-overlay row must match its RECORD declaration.
Every undeclared row receives a fresh bounded observation without claiming a declaration match.
All overlay rows must be consumed exactly once; additional divergences fail.
No distribution imports or generic mismatch suppression were added.

Schema 4 records nested installed-file observations and `recordDeclarationComparison`.
The report binds a separate overlay artifact; it does not embed the runner A09 proposed `recordDeclarationOverlay` object.
The state is exactly `current_runtime_filesystem_snapshot_complete_unqualified`.
The A09 attempt is absent. A07 and A08 empty failed attempts remain preserved.

One fresh source-bound snapshot attempt may follow completed independent source review and current parent preflight.
That narrow operation must preserve failure, recheck source inputs, and read back exact saved output.
This source review creates no runner or comparator authorization.
It does not establish provider origin, divergence cause, wheel trust, loaded images, standard-library closure, native rendering, or creative acceptance.
