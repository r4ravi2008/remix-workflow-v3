# Rust producer qualification A04 parent build readback

The single fixed A04 library compilation failed with exit 1. The diagnostic binary was not compiled or invoked. No control ran and no generated output exists. Preserve the failed attempt. A05 requires one import repair.

Root read the complete 2,299-byte compiler stderr. Two E0425 diagnostics identify CHILD_LOG_BYTES at qualification.rs:1249 and :1292. The constant exists at the crate root. Import crate::CHILD_LOG_BYTES into the qualification module, or qualify these two uses. The other two messages are inherited unused-import and unused-variable warnings. No compiler invocation was repeated.

Root independently reopened all 239 preflight inputs, totaling 98,993,398 bytes. Every size, SHA-256, and nine-field identity matches the preflight, before, after, and current observations. Root compared the exact library argv and complete ten-variable environment against the frozen recipe. The declared three commands match preflight. Only command zero started.

The compiler PID 90339 is reaped and currently absent. No timeout, overflow, termination request, or held stream remains. Stdout is empty. The owned tmp directory is empty. The reader-control and future-evidence directories are absent. All seven canonical diagnostic output paths are absent.

Saved immutable evidence:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| preflight.json | 146,578 | ed45862270f83edb950e98a111218038448d4235e502c2771259951ea08a807f |
| report.json | 285,183 | 3ac64c1de32552d0933faf26cc858bb58bb3013de5789ee03fcf2479aa34c64e |
| 0-stdout.log | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| 0-stderr.log | 2,299 | b9d9cc9de1359f3d71d7a2b5ab7172afb8d644d3bcb0e8f871f086b059a01099 |
| parent-current-readback-a01.json | 143,361 | a2f74686e2ab7ac70dcae77f59f9273024071911041894bcf8882d8849a439a9 |

These files are under rust-producer-qualification-a04-attempt-a01. The additive current readback contains all independently reopened input rows and exact saved-file receipts. It does not alter the original outer report.

The eight scope booleans remain false: native producer executed, accepted value constructible, execution authorized, trust pin present, product integration allowed, WATCHED, HEARD, and creative accepted. File identity readback does not attest loaded runtime images. Separate actual-evidence peer review remains pending. Native and audiovisual acceptance remain absent.
