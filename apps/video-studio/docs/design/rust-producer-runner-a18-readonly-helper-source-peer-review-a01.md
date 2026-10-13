# A18 read-only helper source peer review

This is a source-only peer review of the pending A18 read-only measurement helper. I did not import, execute, compile, or launch the helper.

## Reviewed identities

- A18 helper: `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a18-readonly-root-source-measurement-a01.py`
  - 14,766 bytes
  - SHA-256 `03fdd7a09321143ad8fca4b971ec9a05bfe133adadd9f168b0fc788bb3929fa4`
- A17 helper predecessor:
  - 14,766 bytes
  - SHA-256 `71c613758f2ab9937992d45422c41a83e317edc795f25cbc912ea729f2bd9bdd`
- A17 predecessor proof bound by A18:
  - `rust-producer-runner-a17-parent-source-readback-a01.json`
  - 764,624 bytes
  - SHA-256 `70d509163202c8bf01ca60deeb824f92b2fc0f3b87c800a1f0ee3734e1861e82`
- Parent preparation review:
  - 1,508 bytes
  - SHA-256 `5f8c2a8a4846780b318fe95b7b4fee75c3819f7ab96346f52b9cfa60f236c037`

## Static delta result

The A18 source differs from A17 only in the declared A18 package, manifest, aggregate domains, output labels, and predecessor binding. The predecessor changes are exact:

- A17 package and seven current A17 labels become A18.
- A16 predecessor proof becomes the actual A17 proof.
- The proof receipt changes from 720,492 bytes and 616 rows to 764,624 bytes and 655 rows.

I reversed those fixed replacements in a separate text comparison. The resulting bytes equal the A17 helper exactly. Both sources parse successfully with Python's AST parser. The top-level function/class definition inventory is unchanged. The nested bounded JSON admission function is also unchanged.

The A18 module imports only standard-library modules: `pathlib`, `datetime`, `hashlib`, `json`, `os`, `stat`, `struct`, `sys`, `re`, and `math`. It has no project import, subprocess API, process-launch API, or native/media call.

## Current predecessor binding

The A17 proof contains:

- `inputRows=655`
- `inputBytes=164,928,922`
- `inputsMatched=true`
- 15 source rows
- 204 external rows
- source aggregate `c9a71afea48698b620f40bb851b4d99ef61f758a6d1d783943a4a937e5c1c60f`
- external aggregate `41d3e55c523574ef54f37eb3e145cf9daa3635ddc7e9f3dcdb7f5781049e112a`

Its native producer, native result, product integration, loaded-runtime, watched, heard, and creative flags are false. The A18 helper binds the proof receipt before it admits the inherited rows.

## Helper behavior

The unchanged helper logic has these bounded checks:

- `_read_at` rejects nonregular files, uses `O_NOFOLLOW|O_NONBLOCK`, reads in bounded chunks, and compares opened and pathname identities before and after reading.
- JSON input is capped at 16 MiB. Duplicate keys and nonfinite numbers are rejected.
- Encoded output is admitted before JSON allocation with node, depth, string, integer, float, and 16 MiB limits.
- `save_at` uses an exclusive regular-file create, writes through the owned descriptor, calls `fsync`, reads back through that descriptor, and checks file and parent identities.
- Source and external aggregates use deterministic row ordering and explicit domain labels.
- The final source closure compares all measured rows before and after the helper's read phase.

These checks establish bounded file and source-closure observations. They do not attest to loaded Python images, runtime libraries, native processes, or product acceptance.

## Disposition

I found no new P1 or P2 issue in the A18 source delta. The A18 manifest and package remain pending. The helper has no execution authority until that manifest is complete and independently reviewed. All future output remains diagnostic source-readback evidence only.
