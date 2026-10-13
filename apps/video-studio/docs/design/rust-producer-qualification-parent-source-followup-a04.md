# Qualification A04 static environment followup

A05 needs two finite repairs: the compiler-confirmed missing constant import and one environment reconstruction group. The latter is a source/data-shape finding. No A04 diagnostic invocation occurred.

Root read both fixed runner preflight JSON files and qualification.rs:1240–1370. Both environment fields are objects with ten string key/value pairs. The qualification parser calls digest_string_list, which requires an array. After the import repair, reconstruct_fixed_runner would reject these exact saved environment objects before publication.

The two retained expected environment digests also omit values. Root independently reproduced them by iterating dictionary key names as list elements: build 91cf24e6150b65bde05199afb58779481d46a03fa4d6c3aac6e4e1e3938edbaa and control 938ee84eba7cec06fd533b346dcee93212ebbf302c35cd1091ee569d0fdc90fd. The array type mismatch blocks the fixed diagnostic. The names-only digests do not represent the captured environment values. Repair these related defects as one group.

Parse each environment as an object. Canonicalize pairs by ascending key UTF-8 bytes. Encode domain UTF-8 bytes, one NUL terminator, u32be pair count, then each key and value as u32be UTF-8 byte length followed by the exact UTF-8 bytes. Require string values. The pair count is ten. Use explicit map domains to distinguish the encoding from the earlier list format.

Root independently computed these expected static vectors from the exact fixed preflight files:

| Map | Domain | Encoded bytes | SHA-256 |
| --- | --- | ---: | --- |
| Build environment | native-text-rust-runner-build-environment-map-v1 | 531 | 30825699acd893f54089d18dae56da0bd51d556ed04052eb4a99e0ffae7ef118 |
| Control environment | native-text-rust-runner-control-environment-map-v1 | 543 | c08f170497ca3cb720dd947dd710ce9a4a29a9b8c525b83b8e86eaeebba1094d |

The build preflight is 55,320 bytes with SHA-256 aca42867562688283bcd8d5b2a600eb44870e88701979b825a0d3b19325516ce. The control preflight is 62,704 bytes with SHA-256 df1a8d40c65fc3f3d879f3621ce94d6deec12393574e7c248487b2e9063a0104. These expected vector hashes are static input calculations, not published A05 diagnostic receipts or runtime-image attestation.

Keep the existing command-matrix and control-argv hashes unchanged. Retain the 63-row role/tag schedule and the ten case dependencies. Update only the environment parser, its two expected digests, and the matching framing metadata and contract. No historical control matrix or new capability is required.

The A04 compilation failure, source package, and saved reports remain immutable. This followup changes no execution record. Production trust data, accepted values, authorization, native execution, product integration, WATCHED, HEARD, and creative acceptance remain absent.
