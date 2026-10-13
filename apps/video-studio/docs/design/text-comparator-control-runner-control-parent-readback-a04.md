# Combined comparator controls A03+A04 — failed attempt readback

One fixed external invocation exited with status 1 before any result row. The
attempt is preserved. Neither the comparator runner nor its children qualified.

The invocation used the fixed CPython 3.12 path with `-I -B`, the reviewed A04
source, the unit working directory, and a closed six-value environment. External
preflight measured 57 unique regular files totaling 23,343,285 bytes. All current
bytes, SHA-256 values, and nine identity fields matched after the child closed.
The dedicated temporary directory remained empty. No timeout or signal occurred.

The child loaded A03 and reached the real A09 positive binder. It stopped with
`RunnerFailure: overlay_order:overlay.rows[26]`. Stdout is empty. The complete
3,342-byte traceback is retained in `stderr.bin` with SHA-256
`a37614a8bcbfe9786b811c64dc056966652540cd0e86764ce637c1a53a248d02`.

## Narrow defect

The frozen A09 overlay groups Pillow rows 0–25 before NumPy rows 26–44. That
order matches the fixed runtime helper's package specification. Runner A03
instead orders package labels by UTF-8 bytes. The Pillow-to-NumPy transition
therefore fails its `overlay_order` check at row 26.

The successor must use the explicit accepted package order and retain strict
path order within each package, duplicate rejection, exact package labels,
source hashes, and A09 relationships. It must preserve the saved overlay bytes.
This finding concerns actual fixed-input compatibility. It does not justify
normalizing or rewriting the historical A09 evidence.

## Saved evidence

The report is `comparator-source-controls-attempt-a04/report.json`: 2,448 bytes,
SHA-256 `8c61b89156eef3d2e11fb063c7514abb9b4a21841c94b5906fb1dd32b1cfa106`.
Its preflight is 33,834 bytes, SHA-256
`48512b67655ee1dc32e5fa2d83ac362976f64e13ecf9db0892899e738099e8d6`.
Root read the complete report and traceback after the attempt.

No inner child, native producer, media operation, GPU generation, Resolve
operation, playback, hearing, viewing, or creative acceptance occurred. The
previous source reviews remain preserved. Their scoped conclusions did not
establish successful execution. A narrow source and control repair is in progress.
