# Native editor core

Rust implements CORE-01 through CORE-08. Historical P0 tests passed. Independent source review is complete. Current full validation remains incomplete. See [measured progress](../PROGRESS.md). Trusted promotion to `verified` is unavailable for all features.

P0 supports one track of solid RGBA clips without overlap. P0 also supports local SQLite revisions, stable intents, strict JSON, and native PNG frames. Movie media, audio, text, layers, and GPU processing remain future work. The implementation pieces below describe current boundaries and identified remaining work.

1. From the `native-editor` directory, run `cargo build --workspace --locked`.
2. Run the CLI examples from the same directory.

Each example uses the same local state directory. [CLI examples](../CLI-EXAMPLES.md) contains the complete sequence and request files.

## CORE-01. Capability and schema discovery

### What it does

An agent discovers executable commands and their input and output shapes before it requests an edit. Discovery also identifies the binary, protocol, and resource limits.

### Scenario

A creator requests a Telugu song promo. The agent discovers local project edits and PNG previews. It reports that movie export and captions remain unavailable. The creator can inspect a background fixture. The fixture is not a finished promo.

### Inputs and result

The current command is `engine.capabilities`, with empty input. Rust `editor-cli` generates schemas from Rust types. Discovery returns tools, implemented IDs, executable hash, protocol and identity versions, schema hash, and limits.

```sh
	target/debug/native-editor tools
	target/debug/native-editor schema project.commit
```

### Behavior rules

- Discovery is stateless and creates no project database.
- The schema hash identifies the complete sorted tool contract. The contract includes input and output schemas.
- For explicit protocol discovery, `expectedSchemaSha256` must be null. Subsequent calls must use the discovered hash.
- Unknown commands return `unknown_tool`. Known future capabilities return `unsupported_capability`.
- Planned commands remain visible through `progress`. Discovery cannot make those commands executable.

### Implementation pieces

- CORE-01.1. Register the six implemented tools in `Registry`.
- CORE-01.2. Generate input, response, and envelope schemas from Rust types.
- CORE-01.3. Hash the schema contract and publish actual executable identity.
- CORE-01.4. Reject protocol and schema mismatches before domain execution.

### Verification

- CORE-01-A, discovery.

  1. Run `tools`.
  2. Compare names with the compiled registry.
  3. Independently hash the executable.
  4. Assert discovery creates no state directory.

- CORE-01-B, schema boundary.

  1. Independently canonicalize all discovered schemas.
  2. Compare their hash.
  3. Send an unknown field.
  4. Assert `invalid_input` without storage creation.

Registered cases include `P0-DISCOVERY` and `P0-SCHEMA`.

### Status and dependencies

Implemented in Rust P0, with no prerequisite. Historical P0 checks passed. See [measured progress](../PROGRESS.md). [The specification](../SPEC.md) defines protocol ownership.

## CORE-02. Local project revisions

### What it does

An agent creates local projects and reads current or historical revisions. Edits preserve earlier snapshots.

### Scenario

A creator requests a four-second background test. The agent creates 96 frames at 24 fps on a 64 by 64 canvas. An edit creates revision one. After a restart, the agent reads revision zero. The agent makes sure that the original empty timeline remains.

### Inputs and result

The current command is `project.create`. Inputs are `projectId`, `intentId`, `name`, and `timeline`. A timeline declares duration, canvas, and rational frame rate. A rational rate stores a numerator and denominator.

```sh
	target/debug/native-editor call project.create examples/project.json --state .state/cli-example
	target/debug/native-editor call project.inspect examples/inspect.json --state .state/cli-example
```

Creation returns revision zero and `projectSha256`. Inspection returns a snapshot and hash. Rust owns each project's SQLite database.

### Behavior rules

- Frame-rate terms must be positive. Equivalent rates normalize to the same reduced fraction.
- Inspection selects an immutable revision or reads the latest snapshot.
- Missing projects and revisions return specific errors.
- A different creation intent for a project that exists returns `project_exists`.
- P0 limits each canvas axis to 2048 pixels. P0 limits timeline duration to 10,000,000 frames. This local store provides no tenant authorization.

### Implementation pieces

- CORE-02.1. Validate identifiers, names, and timeline limits.
- CORE-02.2. Normalize rational rates before you calculate their hashes.
- CORE-02.3. Store immutable snapshots with canonical hashes.
- CORE-02.4. Read revisions and reject snapshot corruption.

### Verification

- CORE-02-A, restart.

  1. Create a project.
  2. Commit an edit.
  3. Launch a fresh CLI process.
  4. Read both revisions.
  5. Independently recompute each snapshot hash.

- CORE-02-B, rate boundary.

  1. Compare `30000/1001` with `60000/2002`.
  2. Assert equivalent creation replay.
  3. Reject a zero denominator before creation of the project directory.

Registered cases include `P0-CREATE` and `P0-RATIONAL-RATE`. Unicode names do not establish Indic text rendering.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-01. Historical P0 checks passed. See [measured progress](../PROGRESS.md). Sample conversion and multi-track migration remain [later work](../IMPLEMENTATION.md).

## CORE-03. Stable command intents

### What it does

An agent retries uncertain edits without duplication. A stable intent identifies one command in one project.

### Scenario

The agent adds a four-second background but loses the response. It repeats unchanged input with `background-v1`. The editor returns the original revision and `replayed: true`. The creator still has one edit. A color change requires a new intent.

### Inputs and result

The current command is `project.commit`. Inputs are `projectId`, `expectedRevision`, `intentId`, and edits. Rust storage owns the intent and original result.

```sh
	target/debug/native-editor call project.commit examples/put-clip.json --state .state/cli-example
```

The fingerprint binds normalized typed input, tool, identity version, and protocol version. Transport `requestId` does not identify the edit.

### Behavior rules

- The editor replays identical completed intents before it examines the current revision, even after later edits.
- Changed command content under an intent that exists returns `intent_conflict`.
- Creation, edits, and renders share project-scoped intents. Different projects can reuse intent strings.
- New edits compare `expectedRevision` inside the transaction. Stale edits cannot overwrite the successful revision.
- Render replay remeasures artifacts. Pending recovery requires snapshot and renderer bindings that match. General media recovery remains future work.

### Implementation pieces

- CORE-03.1. Compute canonical typed command fingerprints.
- CORE-03.2. Store absent, pending, and completed intent states where applicable.
- CORE-03.3. Return original completed results without duplicate revisions.
- CORE-03.4. Reject changed intents and preserve revision conflicts during concurrent calls.

### Verification

- CORE-03-A, old replay.

  1. Commit revision one.
  2. Commit revision two.
  3. Then replay the first request.
  4. Assert the original result returns and current inspection stays at revision two.

- CORE-03-B, conflict.

  1. Change RGBA values under the first intent.
  2. Assert `intent_conflict`.
  3. Independently inspect unchanged revision content.

Registered cases include `P0-REPLAY`, `P0-INTENT-CONFLICT`, `P0-CONCURRENT-EDIT`, and `P0-CRASH-RECOVERY`.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-02. Historical P0 checks passed. See [measured progress](../PROGRESS.md). The [specification](../SPEC.md) defines recovery.

## CORE-04. Typed timeline transaction

### What it does

An agent edits solid clips in one atomic transaction. All edits produce one revision, or no edits persist.

### Scenario

A creator tests two chorus backgrounds at 24 fps. The agent commits blue at frames 0 through 47 and gold at frames 48 through 95. Frame 48 becomes gold. If gold exceeds the timeline, neither edit persists.

### Inputs and result

The current command is `project.commit`, with `clip.put` and `clip.remove` edits. Clips declare ID, start frame, positive duration, and solid RGBA source. Put replaces an ID that matches. Remove requires an ID that exists.

The runnable `examples/put-clip.json` contains one clip. Rust commits the validated snapshot and intent together. Success returns revision and hash.

### Behavior rules

- Intervals include the start frame and exclude the end frame. Adjacent clips can touch without overlap.
- P0 supports one visual track. Overlaps fail.
- Integer arithmetic checks overflow and timeline bounds. Floating-point seconds cannot identify clip boundaries.
- Empty transactions, unknown removals, and excessive edit counts fail. The revision stays unchanged.
- Multiple tracks, media offsets, retiming, and transitions need later schemas and migration. No fallback renderer supplies those behaviors.

### Implementation pieces

- CORE-04.1. Decode edits into the Rust `Edit` enum.
- CORE-04.2. Apply clip replacement and removal to an uncommitted snapshot.
- CORE-04.3. Validate final intervals, order, and clip limits.
- CORE-04.4. Commit one immutable revision after every edit passes.

### Verification

- CORE-04-A, adjacent intervals.

  1. Commit the two 48-frame clips.
  2. Inspect exact clip positions.
  3. Independently decode preview pixels at frames 47 and 48.

- CORE-04-B, rollback.

  1. Combine a valid put with removal of a missing clip.
  2. Assert `invalid_input` and exact equality with the pre-edit snapshot and hash.

Registered cases include `P0-TRANSACTION`, `P0-STALE-REVISION`, `P0-RESOURCE-LIMIT`, and `P0-CLIP-BOUNDS`.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-03. Historical P0 checks passed. See [measured progress](../PROGRESS.md). [The layer contract](../LAYERS.md) remains proposed P2 and P3 behavior.

## CORE-05. Native frame preview

### What it does

An agent renders an exact revision and frame into PNG. The preview preserves all solid RGBA channels and alpha.

### Scenario

Before footage edits, the creator examines a background. The agent renders revision one, frame zero. Every pixel in the 64 by 64 PNG is `[12, 25, 48, 255]`. This is a still preview.

### Inputs and result

The current command is `frame.render`. Inputs are project ID, revision, intent, frame index, and `format: "png-rgba8"`.

```sh
	target/debug/native-editor call frame.render examples/frame.json --state .state/cli-example
```

Rust computes pixels and encodes PNG on the CPU. The receipt records artifact ID, private path, snapshot hash, revision, intent, frame, dimensions, bytes, output hash, and build.

### Behavior rules

- The requested frame must be in the timeline. Uncovered ranges produce `[0, 0, 0, 0]`.
- PNG output uses eight-bit RGBA. P0 declares no color-management or layer-composition behavior.
- The renderer generates the artifact path. The caller cannot choose an output path.
- The renderer stages and promotes pending output before the completed receipt commits. Recovery adopts available bytes only after a deterministic comparison.
- Altered completed artifacts fail integrity checks without replacement. Movie export and GPU rendering remain unavailable.

### Implementation pieces

- CORE-05.1. Select the active clip at exact boundaries.
- CORE-05.2. Produce RGBA pixels and PNG bytes.
- CORE-05.3. Bind pending intents and durably promote output.
- CORE-05.4. Save receipt and render result together.

### Verification

- CORE-05-A, all pixels.

  1. Decode the PNG independently.
  2. Compare every channel against the fixture.
  3. Do a test of an active clip.
  4. Do a test of an uncovered boundary frame.

- CORE-05-B, recovery and bounds.

  1. Interrupt promotion.
  2. Then retry unchanged input.
  3. Independently compare final bytes and bindings.
  4. Reject `frame == durationFrames` without completed output.

Registered cases include `P0-NATIVE-PIXELS`, `P0-RECEIPT-BINDING`, `P0-RENDER-REPLAY`, and `P0-CRASH-RECOVERY`. Pixel checks do not establish motion review or creative approval.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-04. Historical P0 checks passed. See [measured progress](../PROGRESS.md). Export and composition remain [later phases](../IMPLEMENTATION.md).

## CORE-06. Artifact integrity

### What it does

An agent checks actual PNG bytes against the stored receipt and project revision.

### Scenario

Another program changes one byte in yesterday's background PNG. The agent verifies the original artifact ID. Verification returns `artifact_integrity_mismatch`. The agent preserves the changed file for diagnosis. The editor does not replace the damaged evidence.

### Inputs and result

The current command is `artifact.verify`. Inputs are only `projectId` and `artifactId`. Rust resolves the project's stored receipt.

```sh
	target/debug/native-editor verify pal-pal-cli-test <returned-artifact-id> --state .state/cli-example
```

Replace the placeholder with the returned artifact ID. Success returns receipt, measured hash, byte count, and `verified: true`. This result reports integrity. The result does not promote a capability.

### Behavior rules

- Verification rejects caller-supplied hashes, paths, or receipts as unknown fields.
- The receipt must match its own structured hash, project snapshot, revision, dimensions, and generated path.
- The file length, exact byte hash, PNG decoding, dimensions, and RGBA8 format must match the receipt.
- Missing artifacts, altered bytes, wrong project lookup, and symlink paths fail. Verification does not repair output.
- A receipt self-hash provides integrity records. The self-hash does not authenticate acceptance evidence. Independent expected-pixel checks remain separate from this verifier.

### Implementation pieces

- CORE-06.1. Resolve the project's registered receipt.
- CORE-06.2. Examine receipt and immutable snapshot bindings.
- CORE-06.3. Remeasure bytes and decode PNG format.
- CORE-06.4. Return typed measurements or preserve evidence on an integrity failure.

### Verification

- CORE-06-A, unchanged artifact.

  1. Independently hash the file.
  2. Decode dimensions.
  3. Compare both with fresh verification output and the stored receipt.

- CORE-06-B, tamper.

  1. Flip one output byte.
  2. Assert that verification and render replay reject the file.
  3. Then read back the still-altered bytes.

Registered cases include `P0-TAMPER`, `P0-FORGED-RECEIPT`, and `P0-RECEIPT-BINDING`. Integrity does not establish creative approval.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-05. Historical P0 checks passed. See [measured progress](../PROGRESS.md). [Trusted promotion](../SPEC.md) remains unimplemented.

## CORE-07. Native CLI process lifecycle

### What it does

An agent invokes bounded commands with structured retry guidance. The CLI controls its lifetime. The library cannot terminate its host.

### Scenario

An agent loses the process after it submits a background edit. It preserves the intent. A fresh process inspects the project. If necessary, the process retries unchanged input. The creator sees one edit without a duplicate revision.

### Inputs and result

The current operation is `call`. File input supplies a tool input object. Stdin supplies one envelope with protocol version, request ID, schema handshake, tool, and input.

```sh
	target/debug/native-editor call project.inspect examples/inspect.json --state .state/cli-example
```

The Rust CLI owns framing, deadlines, and exits. `Editor::execute` returns typed results. The CLI needs no server or Effect credentials.

### Behavior rules

- Strict JSON rejects duplicate keys, extra documents, unknown fields, and unsafe integers.
- Stdout contains one JSON response. Diagnostics use stderr. Request IDs and intents remain separate.
- Success exits zero. Request rejection exits two. Storage failures, internal failures, and timeouts exit one.
- The execution and result-selection deadline defaults to 30 seconds. `--deadline-ms` accepts 1 through 30000 milliseconds. Timeout selects one structured failure.
- The CLI completes the selected response without a second writer or arbitrary flush cutoff. The caller drains stdout and owns the total process timeout.
- External termination can prevent responses. The agent must preserve the intent. The agent must inspect state. General render-job cancellation remains future work.

### Implementation pieces

- CORE-07.1. Parse file requests and stdin envelopes.
- CORE-07.2. Bound input to 1 MiB and response JSON to 4 MiB.
- CORE-07.3. Map typed errors to exits.
- CORE-07.4. Prevent duplicate responses during watchdog termination.

### Verification

- CORE-07-A, framing.

  1. Submit a valid envelope.
  2. Assert one response, a request ID that matches, empty diagnostics, and exit zero.
  3. Submit duplicate keys.
  4. Assert rejection.

- CORE-07-B, deadline.

  1. Block stdin or pause work at a test checkpoint.
  2. Drain stdout.
  3. Assert bounded execution termination and one complete response.
  4. Pause a large-response reader.
  5. Then drain stdout.
  6. Assert no duplicate or truncated response.

Registered cases include `P0-PROTOCOL`, `P0-CANCELLATION`, and `P0-RESOURCE-LIMIT`. Crash hooks are test-only and cannot establish power-loss proof.

### Status and dependencies

Implemented in Rust P0. Depends on CORE-01. CORE-02 and CORE-03 supply recovery. Historical P0 checks passed. See [measured progress](../PROGRESS.md). [Future adapters](../SPEC.md) remain separate.

## CORE-08. Agent workflow checks

### What it does

An agent distinguishes implemented features, plans, and unpromoted evidence. Local checks find prohibited dependencies and execution paths.

### Scenario

A creator requests a full Pal Pal film. The agent reads `progress`, which reports core families implemented, movie export planned, and no promoted evidence. The agent offers the PNG exercise. Full-film production and review remain open.

### Inputs and result

The current operation is `progress`. It accepts no promotion input.

```sh
	target/debug/native-editor progress
```

Rust CLI reports compiled IDs, build identity, states, dependencies, and empty evidence. Rust tests inspect dependencies and source paths. Effect and UI apps remain separate.

### Behavior rules

- The compiled implementation determines executability. A change to a ledger or local acceptance file cannot enable a tool.
- Current progress reports core families as `implemented`, other families as `planned`, and no family as `verified`.
- An artifact verifier's `verified: true` does not promote a feature.
- Native execution cannot use FFmpeg, libav, bindings, Python-renderer fallback, or Resolve execution. The current implementation claims no GPU use.
- Trusted promotion needs implementation. Dependency-name and source checks provide bounded proof.

### Implementation pieces

- CORE-08.1. Publish compiled IDs and build identity.
- CORE-08.2. Ignore state-directory ledger edits.
- CORE-08.3. Examine dependencies and invocation paths.
- CORE-08.4. Implement trusted acceptance promotion. This piece remains proposed.

### Verification

- CORE-08-A, progress authority.

  1. Run `progress`.
  2. Assert exact core implementation states, planned remaining states, and empty evidence.
  3. Compare executable identity with an independent file hash.

- CORE-08-B, forged promotion.

  1. Place a fake ledger and a receipt that reports success in the state directory.
  2. Assert progress is unchanged and a future tool still returns `unsupported_capability`.

Registered cases include `P0-PROGRESS-AUTHORITY` and `P0-RUNTIME-POLICY`. Technical checks remain distinct from creative approval.

### Status and dependencies

Rust P0 implements bounded checks. Depends on CORE-01. Historical P0 checks passed. See [measured progress](../PROGRESS.md). [Trusted promotion](../SPEC.md) is proposed. Future adapters require separate evidence.
