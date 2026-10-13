# Swift A11 parent source review

A11 is rejected before compiler or native execution. Root read every A10-to-A11 source change, all new shared/control source, the complete schema, rationale, allocation ledger and control contracts, and all fifteen manifest rows. The preserved package is unbuilt and unexecuted.

Manifest SHA-256: `2450a08ddf3e1ab3434e4f06ecb41ae6d3c131c5cedfe2f53a61dab1ce6b0e67`.
Producer SHA-256: `754d55702da0b0a069af8dad9d8c59bbc230f64b2d32869f2876c4d67c603207`.

## P1: changed boundary digest

`png-consumer-control.swift:139` changed the expected digest for bytes one through eight while replacing the version label. The preserved A10 digest and root's independent SHA-256 calculation are `66840dda154e8a113c31dd0ad32f7f3a366a80e8136979d8f5a101d3d29d6f72`. A11 instead contains `...a111d...`. The valid boundary control would fail its own expected digest. Version changes must preserve digest literals.

## P1: terminal publication changes frozen event facts

`probe.swift:4265-4307` predicts one terminal report event. It appends that event, then calls `writeExclusive(reportData, recordEvent: false)`. The writer's `probe.swift:2304-2310` path still reserves and releases the 65,536-byte failed-file-prefix scratch owner. Both operations append allocation events. The final guard therefore compares the report with two additional event lines that the fixed point did not predict. The successful final publication cannot satisfy its declared event count and byte total. This defect is inherited from the earlier writer path.

The repair must admit terminal publication owners before the fixed point and keep publication from adding unpredicted events. It must preserve bounded descriptor-prefix evidence and conservative failure charges. A shared control must exercise the actual terminal accounting implementation.

## P2: new reservation maps have no owner admission

`probe.swift:1074-1075` adds two `[String: Int]` reservation dictionaries. Later reserve/write operations insert label keys and count values. No matching logical charge or enforced entry/key-payload bound covers those dictionary headers, buckets and owned label storage. A source claiming every application-owned owner remains below 16 MiB must admit and bound these owners before growth, or use a bounded representation with an explicit charge.

The derived persisted bound, exact source-control compile mapping and shared numeric event admission are useful source changes. They do not close these findings. Independent A11 review remains pending. A12 must preserve A11 and repair the combined findings in a separate package. Root A04 compiler checks and native gates remain deferred.
