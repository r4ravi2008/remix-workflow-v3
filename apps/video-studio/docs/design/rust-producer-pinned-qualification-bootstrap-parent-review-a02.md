# Rust producer pinned qualification A02 bootstrap parent review

Root accepts the external bootstrap within source, compiled binary and pin scope. No P1 or P2 remains. Separate bootstrap peer review is pending. The positive diagnostic has not run.

The external bootstrap is 11,781 bytes with SHA-256 `a3e5f06152992ff3c04959aa608ba73c8b839f780ddfcdef2cca8ad0d92bfd78`. It binds the exact A02 source manifest, recipe, accepted source reviews, transitive A01 authority, compile evidence, measured library and diagnostic, source pin, embedded manifest and four expected vectors. The bootstrap remains outside the two-entry trust manifest. Its root and peer reviews must finish before one diagnostic invocation.

Both prescribed compiles returned zero. The measured compiler commands and ten-variable environment match the fixed recipe. The compiler PIDs and groups, 94566 and 94569, were reaped and are absent. No timeout, overflow, termination signal or held stream occurred. The owned TMPDIR is empty. The diagnostic output root is absent.

Root independently derived the complete input set. All 319 inputs, totaling 102,817,105 bytes, match before, after and current content and nine recorded identity fields. This set includes A01's transitive authority, all four recipe vector leaves and both completed source reviews. Root also matched both generated outputs, all four compiler logs, the preflight and report. Root fully read the 25,116-byte library stderr. It contains 65 unused or dead-code warnings and no errors. The other three streams are empty.

The library has 16,903,808 bytes and SHA-256 `452e577e57b62ec81d76659d2b1bb994dd2656ad19e783e1b564a27c5f561cdb`. The diagnostic has 4,094,480 bytes and SHA-256 `b249acf29bbcd93af2ae4709968f1d22ae85473d68a6415e65f544772d9166e0`. Root independently parsed the diagnostic's arm64 Mach-O header, executable type and 19 load commands. Its UUID is `a3b05adca78a30348d40e78a11fa9b15`.

Root independently extracted the pin from the measured source. Schema 1, byte count 2,664 and SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707` match the exact manifest. The complete manifest byte string occurs once in the compiled diagnostic. Each of the four complete expected RoleIndex byte strings also occurs once. These disk observations and the reviewed fixed compile establish the bound compiled artifact. They do not attest a loaded runtime image or prove that the loader has run.

The compile report is 385,079 bytes with SHA-256 `bec6a15af0362cc7f154874857c5c0bbfec25525a162d77cf24acbbccde07edc`. Root's independent current readback is 190,549 bytes with SHA-256 `e0316cf2aede3ce1799ee4df55cf1947e75f9ae337f23ce69446d65c2f36c18c`. The preflight is 191,440 bytes with SHA-256 `3e14146c8dd6706b7371479141cf63869769f2c228e96189d6df5711a56c90de`.

After separate peer review, one fixed no-argument positive invocation may use this exact diagnostic and environment. Its result must independently reproduce the expected Source and Runner vectors before root and peer review can accept runtime qualification evidence. Historical controls must not replay. The saved compile and bootstrap records remain unchanged after that invocation.

This review is same-model-family and nonblind. No opaque runtime qualification, execution authorization, native producer output, product integration, WATCHED, HEARD or creative acceptance is established.
