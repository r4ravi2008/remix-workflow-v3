# Existing-media admission next design A07: independent peer review

## Result

A07 closes the terminal picture-evidence and fixed-digest findings.
It also repairs the retained outer owners at failure closure.

Two P2 ownership gaps remain.
Plan8 implementation must wait for another design successor.

There are no P1 findings.
Plan8 remains disabled, so these gaps affect design readiness only.

## Review scope

I read the complete A07 design and the complete normalized A06-to-A07 patch.
I checked the four A06 peer and parent findings against current source.

I independently rehashed all fourteen product files named by A07.
Every file matches A07's recorded SHA-256 value.

I authored the A06 baseline used by the A07 author.
This review is independent of A07 authorship, but it is nonblind to the baseline shape.
The reviewer and author use the same model family.

No product source, helper, build, test, process, native media, or project state changed.

| Evidence | SHA-256 |
| --- | --- |
| A07 design | `eb195c7672252b080f24e8a33f52a4e9d4592888c5fcab40be47309b45e4324c` |
| A06 design | `c53ea732da16a384c71e1a3f52e65cfda2ca5c9b5bf0ba702ddb20087e858502` |
| Normalized A06-to-A07 patch | `6b160e2753abd2d855515ec4b12622dfdcef00671ad3754fc151738c4a8ed64e` |
| A06 independent review | `178e938867d6606bb33bf9eab4da049b0ad8520e219c2c2f0e3e3f869242983e` |
| A06 parent review | `1a48a069d86b953eaf21d8bca38aa0daa29b555149dafe6573223a1993f0a45c` |

## P2: request preparation and hashing do not have a complete owner schedule

A07 defines one retained `ExportRequest` and one resulting `ContentHash`.
That pair is correct after preparation completes.

The selected A03 private APIs still take `ExportRequest` by value.
Current `Project::export` retains the outer request while passing `request.clone()` into preparation.

The second request owns three additional String allocations.
No A07 preparation peak charges that clone.

The Plan8 request identity also needs one exact hashing schedule.
Current `ContentHash::document` creates a complete JSON `Vec<u8>` before producing the hash String.
A03 instead requires a private domain-separated Plan8 identity.
A07 does not define its encoding, buffer cap, hashing scratch, or drop boundary.

`M_export_outer_variable` cannot cover either owner.
It contains only the retained request and the completed hash.

The successor must select one exact schedule:

1. Borrow the retained request during Plan8 preparation and change the private signature accordingly.
2. Keep the by-value signature and charge the cloned request through every preparation peak.

The successor must also define one bounded Plan8 request-identity encoding.
It may stream a fixed binary encoding directly into SHA-256.
Alternatively, it may charge one finite canonical buffer before allocation.

The control schedule must exercise maximum intent, timeline, and hash lengths.
It must reject an uncharged request clone or serializer buffer.

## P2: recovery and publication omit live lease-control ownership

A07 correctly keeps both claims and the cloned renewal `Project` until `quiesce` joins.
Those terms do not include the complete `ExportLease` owner.

A06 explicitly places these owners in `O_execute_A05`:

- the `ExportControl` Arc allocation and live Arc handles;
- the stop channel and its slots;
- the renewal `JoinHandle`;
- the worker closure and fixed captures.

`R_recovery_running_A07` includes none of that fixed overhead.
The receipt, measurement, and prejoin formulas therefore undercharge the running lease.

After `quiesce`, `complete_legacy` owns the returned `ExportControl` through `PublicationGuard`.
The outer export frame also retains its earlier control clone unless Plan8 drops it explicitly.

`C_claim_quiesced` contains only one `ActiveClaim`.
`H<PublicationGuard>` contains only a borrowed control reference.
Neither term owns the Arc allocation or the control handles.

The omission also exists in A06's normal `P_publication_base` inherited by A07.
A07's failure peak covers one remaining control, but success and recovery peaks do not.

The successor must define two closed terms:

```text
O_lease_running
  = ExportLease root
  + control Arc allocation and exact handle count
  + stop channel
  + JoinHandle
  + fixed worker closure and capture records

O_control_quiesced
  = control Arc allocation
  + exact live ExportControl handles
```

Every prejoin recovery peak must include `O_lease_running`.
Every applicable normal-publication and postjoin recovery peak must include `O_control_quiesced`.

The owner ledger must record explicit drops before removing either term.
Shadowing a control binding does not prove its owner has dropped.

Add controls for running recovery, successful join, join failure, normal publication, and uncertain completion.
Each control must mutate one handle or channel charge and require ledger failure.

## Closed A06 findings

### Terminal picture evidence

`terminal_picture_peak_A07` conservatively retains the complete A06 execution peak.
It adds the outer export owners and `M_picture_execution` at the actual construction point.

The move into the caller preserves one scope String.
The planned 512-byte and early-release controls are sufficient for this boundary.

### Verification collision hashing

The fixed digest comparison removes the second hexadecimal String.
It keeps canonical bytes, expected identity, file chunk, digest state, and both fixed arrays live together.

The legacy formatter remains restricted to Plan2 through Plan7.
The source gate and mutation control make that restriction reviewable.

### Failure closure outer owners

The failure formula now retains the prepared plan, request, request hash, main claim, and control allocation.
It applies the same owner rule to execution, recovery, verification, cancellation, and fencing.

This closes the A06 failure-closure finding.
It does not close the earlier preparation clone and hashing gap above.

### Recovery claim transition

A07 no longer uses `C_claim_quiesced` before the actual join.
The running and quiesced claim terms now change at the correct transition.

The remaining recovery finding concerns lease-control overhead.
It does not reopen the two-claim or renewal-project schedule.

## Compatibility

A07 adds no public type or serialized field.
Its fixed-digest comparator is private to the explicit Plan8 route.

All fourteen current source hashes match the A07 table.
No source implements the proposed Plan8 path at those hashes.

The claimed Plan2-through-Plan7 byte preservation remains a future implementation control.
This review does not convert that design requirement into tested compatibility evidence.

## Acceptance boundary

A07 is not ready for Plan8 implementation while the two P2 findings remain.

This review establishes no physical-memory bound, native output, playback, hearing, creative acceptance, full-editor acceptance, or full-film completion.
