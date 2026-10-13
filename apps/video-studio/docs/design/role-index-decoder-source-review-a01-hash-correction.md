# RoleIndexV2 decoder A01 review hash correction

This additive record corrects one provenance field in
`apps/video-studio/docs/design/role-index-decoder-source-review-a01.md`.
The original review remains byte-preserved.

The actual frozen decoder source is:

```text
artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/independent-role-index-decoder-a01/decode_role_index_v2_a01.py
```

Its verified SHA-256 is:

```text
57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581b
```

The prior review recorded the same digest without the final `b`:

```text
57fca7995ee886561ad7152f549c92aafd6839c84beeec63a59487527e59581
```

This is a documentation-only correction. It does not change the source,
review disposition, decoder scope, or qualification boundary.
