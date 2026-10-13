# Rust producer pinned qualification A02 bootstrap peer review

Disposition: `accepted_no_p1_or_p2` for the bounded compile and external-bootstrap scope.

This is a same-model-family, nonblind peer review. It does not authorize the first diagnostic invocation. It does not establish a loaded runtime image, an opaque accepted value, native execution, native output, product authority, `WATCHED`, `HEARD`, or creative acceptance.

The external bootstrap is 11,781 bytes with SHA-256 `a3e5f06152992ff3c04959aa608ba73c8b839f780ddfcdef2cca8ad0d92bfd78`. It binds the A02 source manifest, direct build recipe, A01 predecessor authority, accepted A02 source reviews, compile report, current source and binary readback, compiled trust pin, and four expected vector leaves. The A02 source manifest is 12,090 bytes with SHA-256 `3a5cf1db90f57a53b1988c09b2bb6a8dfde9c8609f5ac3dea07a0f62510c5199`. The A02 parent source review is 3,413 bytes with SHA-256 `83a48304f961156dc52af3847944604c88b3f81b82ed4a5efa7987e127910ee9`, and the A02 peer source review is 4,662 bytes with SHA-256 `670357e434345617b6397901756fc45aa66071f8a4d3d0436937e714ad1c5ca3`. The independent source readback is 152,522 bytes with SHA-256 `397bc1d331d903525602a0a6c10ecaa0b81eaa8898810f170ff28dd39162a1d2`. The bootstrap is explicitly outside the two-entry trust manifest and does not authenticate itself. The review gate still requires one root review, one peer review, and one positive no-argument invocation.

I independently rehashed the eight A02 source rows and reproduced the declared source aggregate. The raw source rows total 179,143 bytes, and the framed aggregate SHA-256 is `7009ab7ef3546020149560cf92e915f02dd2bfbc14a7afe044c5309629a16f45`. The three direct external rows total 99,156 bytes, and their framed aggregate SHA-256 is `c3b5cbad895c66631387dc7cb69d324bda371b971020bed63a365c245aca630d`.

I followed the A01 predecessor manifest rather than treating the three A02 direct rows as the whole history. The A01 manifest is 90,182 bytes with SHA-256 `2cb9d7e25718a458ccf4788962190d66aca7c78a70602f24888bed1f8bf5c460`. Its eight source rows reproduce aggregate `9da21e8b8ed15985808611d5d053f0149a78959fb7b113b22740dffe38e05bc9`, and its 207 external rows reproduce aggregate `8eccf632114b209be23890338d5d7bf29b30bad4fcf7044c661708443d8d5036`. All declared A01 and A02 rows matched their current bytes and hashes.

The direct recipe is 15,681 bytes with SHA-256 `2c72b75b9258feecc8de13259ed22983292c693b83a52e84ae791d47edda2e4f`. I matched both recipe command vectors, the two preflight command vectors, and both saved compile command vectors. The ten environment values match the recipe and bootstrap. The preflight has 319 input rows totaling 102,817,105 bytes. The saved report and current readback match before, after, and current nine-field identities for every input row.

The saved compile report is 385,079 bytes with SHA-256 `bec6a15af0362cc7f154874857c5c0bbfec25525a162d77cf24acbbccde07edc`. The preflight is 191,440 bytes with SHA-256 `3e14146c8dd6706b7371479141cf63869769f2c228e96189d6df5711a56c90de`. Root's current source, binary, and pin readback is 190,549 bytes with SHA-256 `e0316cf2aede3ce1799ee4df55cf1947e75f9ae337f23ce69446d65c2f36c18c`.

Both declared compiles returned zero. The library is 16,903,808 bytes with SHA-256 `452e577e57b62ec81d76659d2b1bb994dd2656ad19e783e1b564a27c5f561cdb`. The diagnostic is 4,094,480 bytes with SHA-256 `b249acf29bbcd93af2ae4709968f1d22ae85473d68a6415e65f544772d9166e0`. Independent Mach-O parsing found arm64 magic `0xfeedfacf`, file type 2, 19 load commands, and UUID `a3b05adca78a30348d40e78a11fa9b15`. Both compiler PIDs, 94566 and 94569, and both process groups are recorded absent. The saved compiler logs and generated outputs match their current bytes and identities. The owned temporary directory is empty, and the diagnostic output root remains absent.

The compiled pin is schema 1 with 2,664 manifest bytes and SHA-256 `ddd6614afb7879905e3941e18269979728e57d92ffb43df84c49beb41c2f7707`. The pinned `trust_root.rs` source is 36,811 bytes with SHA-256 `ff7b2ebde7f78eb3ed2c7142609f43b9c30a65c9908d1655979f6469a59e66c2`. Independent byte inspection found the complete manifest byte string exactly once in the diagnostic. Each complete expected vector also occurs exactly once:

- source subject: 2,077 rows, 539,734 bytes, SHA-256 `16333c79eb18f41a8c2ed95777866be293ebd1ceec06865584ff14e853705bbf`;
- source final: 2,080 rows, 540,669 bytes, SHA-256 `c60e7e88aafff3d63bb7110ccf887974c732104a58d23f755000d31d7f3c902f`;
- runner subject: 63 rows, 15,579 bytes, SHA-256 `2c0a3b98623c9af3cf1d7a060efc53d3ea0793252b4d98ef90b0488925153fc2`;
- runner final: 66 rows, 16,514 bytes, SHA-256 `1f98263dd736b5f30d1906fe15b3a91ef8db6032a0e9f5fc1a02c5732536f77b`.

The bootstrap and compile evidence pass this bounded review without a P1 or P2 finding. No controls, diagnostic invocation, import, compiler, native action, or media action was run during this review. The next permitted action remains the single fixed positive invocation under the recorded environment, after the required review gate is complete.
