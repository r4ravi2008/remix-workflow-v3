# Rust producer runner A16 current source readback peer review

This addendum reviews the saved A16 readback and authenticated helper receipt.
It does not change the frozen A16 source peer review. I did not import,
compile, execute, or run controls, native code, media code, or a producer.

## Saved evidence

The current source readback is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a16-parent-source-readback-a01.json`

It is 720,492 bytes with SHA-256
`434c25d2aee42c7affe94264ede7f3207b3b1dc455617ce442cfc1680378d3af`.

The authenticated helper receipt is:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a16-readonly-helper-external-authenticated-launch-a01.json`

It is 1,448 bytes with SHA-256
`a6e6afd43a47899b8919edb10e5b1b9d063148a213af5a7b3ba1c8ecd31a29cf`.

The helper remains 14,766 bytes with SHA-256
`433cae78cdb0b09bcbfb75b90bab28f193ec0bdfd83e717e23caf2f3043e48e2`.
The A16 manifest remains 98,788 bytes with SHA-256
`5c22f08360ab78e07933d3fea68b6c986bc331092bea27ddee2a3681fb90b659`.

The helper stdout log is 858 bytes with SHA-256
`a2b45d6ab80d6ceab2b8f3344d28f32a53a8512a9983e3418171b2495d5c90ae`.
The helper stderr log is empty, with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Independent closure check

The readback declares 616 inputs and 163,472,808 bytes. Its `inputsBefore`
and `inputsAfter` arrays each contain 616 rows and are byte-for-byte equal.
The declared `inputsMatched` value is true.

I reopened every declared path as a regular file. I recomputed every SHA-256
digest in bounded chunks. I compared bytes and all nine recorded identity
fields: device, inode, mode, link count, UID, GID, size, modification time,
and change time. All 616 rows matched the saved records.

The 616 paths and their device/inode pairs were unique. The current rehash
total was 163,472,808 bytes. No row failure occurred.

The readback retains the frozen A16 source aggregate of 15 rows and 463,576
bytes with SHA-256
`b4eef131436e37f8461b9e5350abab572eedffcc4e62d388a62fb2b7c51a2a07`.
It retains the external aggregate of 159 rows and 39,721,126 bytes with
SHA-256
`760b5988448e5ec3e204342bf0216fb2ca56a80e9712bc177e14fbcf8345712c`.

The readback records 27 explicit compile imports and 23 imported Rust source
files. Every recorded import source and target appears in the 616-row closure.
No source/target import pair is duplicated.

The saved readback binds the manifest receipt and helper receipt to the same
current bytes, hashes, and identities. The helper receipt has matching
before/after identity, `descriptorClosed: true`, `isolated: true`,
`optimize: 0`, `dontWriteBytecode: true`, and
`executedFromExactHeldMeasuredBytes: true`.

## Execution and acceptance boundary

The authenticated receipt records false for project-code import, process
utility import, compiler execution, controls execution, native producer
execution, native result acceptance, product integration, watched, heard, and
creative acceptance.

The readback itself records false for compiler execution, controls execution,
authorization creation, native producer execution, native result acceptance,
product integration, loaded-runtime attestation, watched, heard, and creative
acceptance. It also records `parsedFromHeldMeasuredBytes: true` and
`processUtilityImported: false`.

This is measured source-closure and helper-execution evidence. It does not
prove a Rust compile, a control run, a loaded Rust binary, a native producer,
media output, or product acceptance.

## Disposition

The saved helper receipt is internally consistent with the current helper and
manifest. The complete current closure rehash passed with no identity, byte,
digest, import, or aggregate mismatch.

I found no P1, P2, or P3 issue in this current-readback scope. The result is
unqualified source evidence and remains separate from later compiler, control,
native, media, watched, heard, and creative evidence.
