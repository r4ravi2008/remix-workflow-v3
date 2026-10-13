# Comparator runner design A07 parent review

Status: complete source-only read of the 384-line design.
A07 remains unimplemented and creates no execution authority.

Reviewed design SHA-256:
`aca084ef713034ac15303f035b5b3a998a48b1ed875245c36585b846fa3f8a9e`.

A07 repairs the child-loader shape and removes authorization from the source
closure. The captured loader has path, integer bytes, and SHA-256 only.
Wrapper filesystem observations remain separate.
The 15-second policy now correctly identifies A03 as its source.

## P2: the package still includes the authorization that pins the package

The final package bullet requires the source-closure authorization.
The authorization later pins the accepted package manifest hash.
Those two records therefore still form a hash cycle.

Exclude the authorization from both the package manifest and source closure.
Create the external authorization last, after both records are frozen.
The authorization can then pin both records without either record pinning it.

## P2: the accepted child wire example is stale

The accepted A13 example uses schema 1.
The actual A13 control and output contract use schema 2.
The A14 repair is required to retain schema 2 and freeze all ordered row fields.

The final runner contract must use the exact accepted successor schema.
It must verify per-row fields and values, including qualification boundaries.
The current A13 count mismatch prevents final result-table acceptance.

## Runtime integration constraint

The current snapshot helper publishes one JSON report containing runtime and
dependency facets. A07 assumes separate runtime binding and closure files.
The successor must either alias both roles to that exact report, or require
separately reviewed derivative records. It cannot consume nonexistent files.

## Disposition

Preserve A07. Close the two P2s and runtime integration constraint in A08.
Bind the accepted A14 wire contract and accepted runtime snapshot contract.
No runner, comparator control, native producer, GPU, or Resolve process ran.
