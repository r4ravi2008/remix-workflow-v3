# Rust producer qualification A05 source peer review

## Result

The A05 Rust repair is correct, but the frozen package has one P2 documentation identity defect.

I found no P1 and no Rust code P2. The Rust source is ready for the fixed diagnostic build after a narrow documentation-only successor corrects the Runner identity.

This review is source-only. I did not compile, import, execute, or modify the package.

## P2: the public documents misidentify the fixed Runner subject

The implementation and manifest bind `rust-producer-runner-a04`, its A04 build, and its 35 measured files. Three document statements instead name A05:

- `README.md:14` says the Runner diagnostic binds the A05 source package;
- `README.md:39` calls the saved Runner evidence A05 evidence;
- `qualification-contract-a05.md:58` says the Runner subject includes the fixed A05 source package.

`source-rationale-a05.md:27-31` states the correct A04 identity. The code also fixes the Runner manifest, executable, receipts, and source rows to A04.

This defect does not change a path, hash, graph row, or Rust branch. It does make the public contract name a different subject from the cryptographically bound subject. A narrow successor must identify the Runner source and evidence as A04. No runtime or evidence-matrix change is required.

## A04 repair verification

`qualification.rs` imports the crate-level `CHILD_LOG_BYTES` constant. This closes the preserved A04 `E0425` compile failure at the two runner-preflight checks.

Both saved preflight `environment` values are objects with ten string pairs. A05 now hashes each object with sorted UTF-8 key/value map framing:

- build: 531 encoded bytes; `30825699acd893f54089d18dae56da0bd51d556ed04052eb4a99e0ffae7ef118`;
- control: 543 encoded bytes; `c08f170497ca3cb720dd947dd710ce9a4a29a9b8c525b83b8e86eaeebba1094d`.

I independently reproduced both byte counts and hashes from the fixed preflight JSON files. The framing includes the domain, one zero byte, pair count, and every key and value length and byte sequence.

The command and argument hashes remain unchanged. The 63-row Runner graph and ten ordered control cases remain unchanged.

## Verified receipts

| Item | Verified result |
| --- | --- |
| `source-package-manifest-a05.json` | 79,505 bytes; `b3a1fb9852ab533238d388990f2aabeafbbcd614be16ba38dced3ad82ed736eb` |
| Package source rows | 8 of 8 matched; 135,452 bytes |
| Source aggregate | `bbb959d52766139cf5fc3316ec58f390ca6d6db13381a155e1c181485624ca6a` |
| External rows | 154 of 154 matched; 30,575,316 bytes |
| External aggregate | `dd35cec53e6ea19429b743f5d145e8e96a8ff28cb75c3f0edead28ddceae790f` |
| A02 predecessor | Package, source/external aggregates, parent review, and peer review matched |
| A03 predecessor | Package, source/external aggregates, parent review, and peer review matched |
| A04 predecessor | Package, source/external aggregates, reviews, failed build evidence, and static follow-up matched |
| Direct dependency archives | Exact `libc`, `sha2`, `serde`, and `serde_json` archives matched |

The source aggregate reproduces with the declared UTF-8 path ordering. The external aggregate reproduces with the declared role-then-path ordering.

All absolute imported files and the local qualification source are bound. The fixed recipe names all four required dependency archives and uses the A05 attempt TMPDIR.

The A05 attempt, evidence, diagnostic-output, and reader-control paths are currently absent. The imported trust root still has no production pin.

## Evidence boundary

A05 remains uncompiled and unexecuted. This review does not prove compiler compatibility or control success.

The Runner RoleIndex byte count and SHA-256 remain pending actual publication and independent review. Trust data must not be authored before that receipt is qualified.

This package creates no trust data, authorization, native execution, media result, or product authority.

This review is same-model-family and nonblind. No cross-family review is available or claimed.
