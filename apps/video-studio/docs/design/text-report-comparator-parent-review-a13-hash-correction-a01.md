# Comparator A13 parent review hash correction

The preserved parent review contains a transcription error in its peer hash.
Its A13 peer-review row has an extra `c`, making that string 65 characters.

The independently measured SHA-256 of
`text-report-comparator-source-review-a13.md` is:

`6465c6389e460404c139de646e6bb93be8868c119562af871ea012202f7b5fad`

The A13 and A14 package rows use this correct 64-character hash.
Root independently matched all 38 A13 rows and all 40 A14 rows.
Those matches did not rely on the mistyped parent-review string.

This additive correction preserves the original review and its findings.
It changes no source package or execution disposition.
No comparator, control, native, GPU, or Resolve process ran.
