# Observer runtime snapshot A05 parent review

Status: source-only. The parent read all 772 source lines, all 284 contract
lines, the rationale, and the 94-line independent peer review.
The helper was not run. Its fresh attempt directory remains absent.

| Artifact | SHA-256 |
| --- | --- |
| A05 helper | `c3e520304944171dd40a76a5240ce5ccffafa662264267b3a3036e3bf14b745d` |
| A05 contract | `e812fbda0bc93098c173d63fc9bba3e577aa980844039ccb608bb65840406187` |
| A05 rationale | `c74cc237c931862ec05aaf6ddf1b9a21fc9de23e2d8c7e5c77991be79891cc10` |
| A05 peer review | `a8520f8bf027cc238ccfeb8e9be460d7792fd89ca96f9457e1305edd8d7e4e51` |

The parent confirms all three peer P2 findings.
RECORD paths protect the leaf with `O_NOFOLLOW` but do not hold every parent.
The success path lacks an exact attempt-directory allowlist and final held report.
The 8 MiB capture wording omits runtime-manifest and RECORD captures.

A06 must traverse confined parent descriptors, retain the final report handle,
and enumerate the bounded output allowlist before success.
The capture contract must cover every captured input.

The current implementation charges capture bytes after collecting and joining
chunks. This is a successful-result bound, not a preallocation bound.
The author was asked to admit the descriptor's expected capture size first,
or state the existing bound's precise scope. No physical memory claim is allowed.

The root separately refreshed provider runtime metadata to bundle 26.1009.11318.
Static readback matched the runtime manifest and its distribution row counts:
238 Pillow rows and 1,310 NumPy rows, including declared bytecode files.
This does not measure every current dependency file or establish loaded images.
The historical A03 closure remains preserved.

Preserve A05 source, contract, rationale, and reviews.
Review the A06 repair before producing a fresh unqualified filesystem snapshot.
No import, helper, control, compiler, native, GPU, or Resolve process ran.
