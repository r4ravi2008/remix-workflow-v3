# Existing-media admission A07: parent design review

Root read the complete 374-line normalized A06-to-A07 patch against the reviewed A06 baseline.
Root read the complete 165-line A07 peer review.
Root matched all fourteen current product-source hashes during the saved state update.
No product edit, helper, build, test, native process, or media execution occurred.

| Artifact | SHA-256 |
| --- | --- |
| A07 design | `eb195c7672252b080f24e8a33f52a4e9d4592888c5fcab40be47309b45e4324c` |
| Normalized A06-to-A07 patch | `6b160e2753abd2d855515ec4b12622dfdcef00671ad3754fc151738c4a8ed64e` |
| A07 peer review | `2f13cfea10a0a3a3491923baeae80b0146f3b2cbf8681c7bee10804ed52336e1` |

A07 closes the four A06 findings at design level.
The terminal picture scope keeps the full execution overlap.
The fixed collision digest removes the second hash String.
Failure persistence keeps the prepared plan and outer request owners.
Recovery keeps both claims and the cloned Project until the actual renewal join.

Two peer P2 findings remain before Plan8 implementation.
There are no P1 findings in this design-only artifact.

## P2: preparation clone and request-identity scratch remain unspecified

The retained request and resulting hash do not charge the earlier by-value preparation clone.
The selected private preparation APIs take `ExportRequest` by value.
The current export frame keeps its request while passing `request.clone()`.

Choose an explicit private borrowed-request signature or retain the cloned request charge in every preparation peak.
Define the Plan8 request-identity encoding and its finite hashing scratch.
Charge any canonical buffer until its actual drop.
Maximum-length request controls must reject an omitted clone or hashing buffer.

## P2: lease and control overhead is absent from publication and recovery

Claims and the cloned Project do not own the control Arc, channel, join handle, or worker closure.
A06 places those owners in execution overhead.
The recovery base and inherited publication base do not include that overhead.

Define the complete running lease term and the postjoin control term.
Apply them to every applicable recovery and normal-publication peak.
Use explicit handle and channel transitions, including join failure and uncertain completion.
Removing or shadowing a binding does not prove that its allocation has dropped.

## Repair boundary

Preserve A07 and its reviews.
A successor should repair these two schedules without changing its four accepted repair rules.
Plan8 remains disabled and unimplemented.
The peer authored the A06 baseline and disclosed that same-family, nonblind context.
This review establishes no physical-memory bound, native output, playback, hearing, or creative acceptance.
