# A15/A07 actual compilation-failure disposition

ROOT and peer accept this evidence only as a closed failed attempt. The production library and CLI compiled. The private-control library returned 1 with nine Rust errors. The controls CLI was never invoked. The caller exited 0 after recording the failed candidate; that exit does not pass the four-build gate.

ROOT read the complete peer report and remeasured its current bytes through a held regular-file descriptor. The report is 7143 bytes, SHA-256 `628c9ad76df612f2a524982d9fde8ba3c2a94984294f920073fed185d722ae55`. ROOT's actual readback is 354407 bytes, SHA-256 `5c516da8ee82b4825af52f3be679fbcf58f24ae173cace44a9c08b2b82a49856`. ROOT's failure disposition is 2540 bytes, SHA-256 `7e91e99730b2e01c84cdcfd71b34f40a4d3bfa1ff564729e770914229cc5c736`.

The 594 saved inputs match before and after. All three compiler processes were reaped, their process groups were absent, and all streams and caller descriptors closed. The nine errors belong to the controls-only code. A16 may repair these errors as a separately saved successor. It requires source review and a fresh complete four-build attempt.

The measurements omit derived production-success flags; ROOT and peer infer production success from zero compiler exit codes and exact output receipts. No built binary, control driver, or native producer executed. No native result, product integration, watched, heard, or creative qualification follows from this disposition. Preserve the A15 package and failed attempt.
