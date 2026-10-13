# A08 root orchestration rejection disposition

The A08 wrapper snapshot is rejected for execution. Preserve it unchanged.
The independent source review found three P1 and four P2 findings.
The 6,842-byte peer report has SHA-256
`7bcb7a99d2520925dce749af5fe5dd46e1d4965ebbe5b6637936c159cc3d4c5e`.
Root read the complete report and agrees with its execution-blocking findings.

The review targets the immutable four-wrapper preparation snapshot.
The snapshot copies remain unexecuted. After snapshot creation, root executed
the original source-readback helper once to measure the A08 candidate.
That original helper produced the 441-input stable source receipt.
No original compile, control or staged-authorization helper executed.
No project code, compiler, child or native producer ran in that measurement.
The historical preparation receipt describes its creation-time state only.

Repair requires a separate orchestration version with these properties:

- Authenticate held, no-follow utility bytes against a fixed digest before
  executing those same bytes. Preserve the old utility and all earlier receipts.
- Close owned children across setup, selector, stream, wait and signal exceptions.
  Save bounded causal failure evidence and distinguish unresolved cleanup.
- Validate exact finite control IDs, order, counts, nested outcomes and false
  acceptance fields. A zero exit and a state label are insufficient.
- Enforce complete fixed compiler argv, environment, inputs, outputs and limits.
- Measure the actual owned PGID. Verify PID and group absence after cleanup.
- Parse or inspect only the bytes read through the authenticated held descriptor.
  Do not measure a pathname and then reopen it for content parsing.
- Retain the inventory root descriptor and traverse entries relative to held
  directories. Rejoin path anchors and enforce fixed entry and byte bounds.

This disposition does not authorize an A09 source package, build or invocation.
Root must review repaired wrappers and candidate source before dependent work.
