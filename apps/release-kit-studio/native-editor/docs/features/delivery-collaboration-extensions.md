# Delivery, collaboration, and extensions

All 16 families in this document are planned behavior contracts. This document does not implement or verify them. The compiled Rust registry currently implements only CORE-01 through CORE-08.

Those CORE families cover strict JSON commands, immutable local revisions, and stable intents. They also cover one solid-color track with no overlap, native PNG frames, and artifact integrity. The CORE families do not prove movie, audio, text, layered-video, cloud, or plugin support.

Final CORE review and promotion of trusted evidence remain incomplete.

The earlier 81-family ledger was primarily an inventory. These contracts propose observable behavior, implementation pieces, and acceptance cases. Rust owns native editing, processing, and measurements. Effect owns the separate application workflows for Effect-owned families.

React, Tauri, and Foldkit remain unselected candidates for the separate UI application. A Cloudflare Worker cannot run a native Rust subprocess. Hosted execution requires a separate native host. No GPU provider is selected, and these contracts authorize no deployment or paid job.

The [specification](../SPEC.md) defines native ownership and source bindings. The [phase guide](../IMPLEMENTATION.md) sets implementation order.

Each proposed mutation keeps immutable revisions and stable intents. Rational frame rates and integer frame or sample positions govern timing. Unsupported behavior fails explicitly. The native path must not use FFmpeg, libav, bindings, Resolve execution, or a hidden fallback. The verification cases are requirements. They do not claim tests that passed.

Technical measurement, frame inspection, complete playback, listening, and creative approval remain separate states.

## DELIVER-01. Native codec capability registry

### What it does

The registry reports formats the native build can read or write. A codec converts between compressed media and decoded samples.

### Scenario

A creator supplies a 24 fps concert recording and requests an H.264 film with AAC audio. Before the agent schedules the job, the agent examines the execution host. The response distinguishes available H.264 decode support from unavailable AAC encode support. The creator sees the unsupported-format result before the render starts.

### Inputs and result

Planned command `codec.capabilities` accepts a requested operation and optional format constraints. Rust owns the measured capability report. Entries identify platform, backend, codec, container, pixel format, bit depth, operation, and tested limits. A container holds video and audio streams. The exact registry schema and backend-version identity remain undecided.

### Behavior rules

- Decode and encode support are separate entries. A recognized file extension does not prove decode or encode support.
- The report describes the current build and host. The report includes unavailable hardware or permissions.
- Unmeasured combinations remain unsupported. An advertised backend capability does not prove editor support.
- Primary-source research and executable experiments are necessary for SDK choice, licensing conditions, and platform coverage. That evidence is necessary for portable support.

### Implementation pieces

- DELIVER-01.1 defines typed format descriptors and unsupported reasons.
- DELIVER-01.2 probes an initial native backend and records its build and host identity.
- DELIVER-01.3 combines corpus results and probes to publish tested capability entries.

### Verification

- DELIVER-01-A compares a supported corpus entry against independent decode or encode measurements on the named platform.
- DELIVER-01-B disables the required backend or hardware. Discovery reports unavailable support, and export rejects the request before output creation.

### Status and dependencies

Planned P1, owned by Rust in native delivery. Depends on CORE-01 and CORE-02. Current command discovery does not implement codec discovery. Saved corpus evidence is necessary for each platform.

## DELIVER-02. Movie encoding and muxing

### What it does

Movie export saves evaluated frames and audio as a playable artifact. The muxer places encoded streams and timestamps in a declared container.

### Scenario

An interview editor requests frames 240 through 719 at 24 fps, with the stereo audio interval for those frames. The agent binds the revision and range. The 20-second result aligns the first word with the opening frame. The result excludes adjacent timeline frames.

### Inputs and result

Planned command `render.export` takes an immutable revision, half-open frame interval, native encoding profile, and source references. Rust owns the file and receipt. Receipts record build, source hashes, frame count, duration, stream properties, and output hash. Explicit schema decisions are necessary for audio timestamp, encoder-delay, and final-sample policies.

### Behavior rules

- Export validates DELIVER-01 capabilities before allocation. Unsupported profiles produce no completed artifact.
- Frame order follows rational timeline time. Audio uses a declared sample conversion and rounding rule.
- Temporary bytes remain incomplete until container finalization, durability, measurement, and receipt commit succeed.
- P1 first proves encode support against bounded frame and sample fixtures. Later dependencies are necessary for production timelines.
- Lossy encoding uses declared comparison tolerances. Byte identity does not prove timing or fidelity.

### Implementation pieces

- DELIVER-02.1 defines bounded export requests and stream timestamp policy.
- DELIVER-02.2 encodes frames and samples through a measured native backend.
- DELIVER-02.3 finalizes containers and commits measured artifact receipts.

### Verification

- DELIVER-02-A independently decodes the saved movie without FFmpeg. Frame count, timestamps, PCM timing, and source markers match the fixture's declared tolerances.
- DELIVER-02-B interrupts finalization or requests an unsupported profile. No partial container has a completed receipt, and retry preserves the original intent.

### Status and dependencies

Planned P1, owned by Rust. Depends on CORE-01, CORE-02, DELIVER-01, and MEDIA-01. Movie export is absent today. P2 audio and composition capabilities are prerequisites for production timeline export.

## DELIVER-03. Image sequences and still export

### What it does

Sequence export saves an image per timeline frame. Still export saves a selected frame with declared dimensions, format, and alpha policy.

### Scenario

For a commercial designer, frames 96 through 119 are necessary for a one-second package reveal at 24 fps. The agent exports 24 ordered PNG images. A compositor can identify each frame by its manifest entry. A campaign still uses export settings with separate checks.

### Inputs and result

Planned command `render.sequence` binds revision, start frame, positive frame count, image format, and numbering policy. Rust owns a sequence manifest and individual receipts. Each manifest entry binds timeline position, filename, dimensions, and hash. Still-selection schema and formats beyond PNG remain undecided. JPEG export remains planned.

### Behavior rules

- The interval is half-open. The manifest preserves chronological order independently of the order of the directory entries.
- Each requested frame has one entry only. Missing or duplicate frames prevent sequence completion.
- PNG preserves alpha. An explicit flattening policy is necessary for formats without alpha.
- The initial sequence uses bounded dimensions and counts. Separate format and reference-image experiments are necessary for color-managed, high-bit-depth formats.

### Implementation pieces

- DELIVER-03.1 defines sequence numbering and manifest identity.
- DELIVER-03.2 exports bounded frames with per-image receipts.
- DELIVER-03.3 validates complete manifests and adds still formats that have separate tests.

### Verification

- DELIVER-03-A independently decodes all 24 images. Numbering, timeline positions, dimensions, pixels, alpha, and manifest count match the fixture.
- DELIVER-03-B removes one image or duplicates a timeline position. Manifest verification rejects the missing or duplicated frame.

### Status and dependencies

Planned P1, owned by Rust. Depends on CORE-01 and CORE-02. CORE-05 provides a bounded single PNG frame today. It does not provide sequence manifests or JPEG export.

## DELIVER-04. Render queue cancellation and recovery

### What it does

The queue reports render states and reconciles interrupted jobs. Cancellation prevents publication of results from obsolete attempts.

### Scenario

A music-video render stops after a native host loses power at frame 2100. The agent reads the original job. The agent does not create a new render. Before the application resumes the job, the application examines the recipe and artifacts. The creator sees one job and accepted output even if an old host reconnects.

### Inputs and result

Planned command `render.status` reads a tenant-authorized job identity. A separate Effect application owns durable job records, attempt leases, cancellation, and recovery decisions. Rust owns execution and artifact measurements. A lease grants temporary execution authority. State names, lease durations, heartbeat rules, and cancellation schema remain open.

### Behavior rules

- A job binds one immutable recipe, revision, source set, intent, and required build identity.
- Only the current attempt can promote outputs. A stale lease cannot complete the job after reassignment.
- Cancellation and completion share one durable transition. Partial files remain incomplete.
- Resume adopts bytes only after native verification. Recomputation under the same job is necessary for unsupported checkpoints.
- A Worker controls job coordination. A separate authenticated native host executes Rust. No current GPU or paid execution path is implied.

### Implementation pieces

- DELIVER-04.1 defines durable job and attempt states.
- DELIVER-04.2 coordinates bounded leases, cancellation, and native-host calls.
- DELIVER-04.3 reconciles receipts after crashes and rejects stale attempts.

### Verification

- DELIVER-04-A kills a test host mid-job. Durable readback and native byte verification show one reconciled result under the original intent.
- DELIVER-04-B returns an old attempt after cancellation. The state store rejects promotion and exposes no completed output from that attempt.

### Status and dependencies

Planned P6, owned by Effect in a separate application. Depends on CORE-01, CORE-02, DELIVER-02, and CORE-03. P0 process recovery exists for bounded PNG work. P0 does not implement a movie queue.

## DELIVER-05. Source-bound technical QC

### What it does

Quality control, or QC, measures exports against declared sources and recipes. The report locates technical faults without a decision about artistic success.

### Scenario

A documentary contains an intentional black opening for 48 frames at 24 fps. The agent measures a saved export and finds a different black run at frames 860 through 871. The report distinguishes the opening from the gap. An audio marker reveals a 120-sample source offset.

### Inputs and result

Planned command `artifact.measure` accepts a registered artifact, source bindings, and a versioned measurement profile. Rust owns measured frame and sample observations with exact locations. Reports bind output hash, revision, sources, detector versions, and limits. Corpus experiments are necessary for thresholds and tolerances for a pass.

### Behavior rules

- Measurements use actual saved bytes and independently decoded streams. Render exit status is insufficient.
- Findings keep evidence and declared exceptions. Intentional fades are not automatically defects.
- Sync checks compare source markers or declared time mapping. A timeline label alone cannot prove audible alignment.
- Clipping and malformed-stream checks identify unsupported measurements explicitly. The checks never convert an absent detector into a pass.
- Initial detectors use small labeled fixtures. Measured error rates are necessary for detection across more inputs.

### Implementation pieces

- DELIVER-05.1 defines versioned profiles and source-bound reports.
- DELIVER-05.2 measures frame continuity, timestamps, and stream validity.
- DELIVER-05.3 measures sample alignment and clipping with labeled audio fixtures.

### Verification

- DELIVER-05-A injects a known black run and sample offset. Independent decoding confirms the exact reported intervals and offset.
- DELIVER-05-B substitutes a different song or malformed container. Source checks or decode operations reject the artifact. The operations do not give a report with a pass result.

### Status and dependencies

Planned P2, owned by Rust. Depends on CORE-01, CORE-02, DELIVER-02, and AUDIO-02. Current artifact integrity validates PNG bindings. Current artifact integrity does not establish movie QC, listening, or creative approval.

## DELIVER-06. Presets and remote rendering

### What it does

A preset names a versioned export recipe. Remote submission keeps the recipe while a different authorized native host renders.

### Scenario

A creator selects a portrait promo preset for source frames 1440 through 1919 at 24 fps. Preview and remote submission share crop, interval, and audio mapping. A missing remote encoder causes capability rejection before the agent schedules the job.

### Inputs and result

Planned command `render.submit` takes a preset version, revision, source hashes, output constraints, and stable intent. The separate Effect application owns submission and job identity. Rust validates native semantics and owns media results. Recipes record explicit settings instead of mutable preset names. Host selection and preset migration schemas remain undecided.

### Behavior rules

- Preset changes create a new version. Current recipes and revisions remain immutable.
- Before an agent schedules the job, remote hosts must satisfy codec, renderer, and resource requirements.
- Authenticated identity identifies tenant ownership. Source downloads and output writes use bounded authorization.
- Local and remote runs preserve recipe identity. Comparison tolerances are necessary for platform-dependent encoders. The recipes do not promise byte identity across those encoders.
- Alchemy, D1, and private R2 are planned application adapters. Separate native execution is necessary for Worker coordination. No GPU provider is selected.

### Implementation pieces

- DELIVER-06.1 stores versioned presets and immutable recipes.
- DELIVER-06.2 validates host compatibility and issues bounded submission tickets.
- DELIVER-06.3 reconciles remote receipts with native source and build bindings.

### Verification

- DELIVER-06-A submits a fixture to local and isolated remote test hosts. Recipe hashes, frame ranges, measured stream properties, and source bindings agree.
- DELIVER-06-B changes a preset or revokes authorization after submission. The original recipe stays fixed, and unauthorized execution or publication fails.

### Status and dependencies

Planned P6, owned by Effect outside the editor. Depends on CORE-01, CORE-02, DELIVER-04, and COLLAB-01. No preset service, deployed host, or provider readback exists for this native path.

## DELIVER-07. Release-kit profile and archive

### What it does

The optional Release Kit profile produces six source-bound song assets. The archive preserves outputs, recipes, and separate technical and human review records.

### Scenario

A creator supplies a three-minute canonical song, Telugu lyrics, artist references, and three chosen chorus intervals. The agent builds one landscape film, three portrait promos, a thumbnail, and square artwork. All six assets keep the song and accepted identity. Another song cannot silently replace the master.

### Inputs and result

Planned command `kit.build` binds the canonical audio hash and measured duration, revision, lyrics, accepted visual references, and promo intervals. Rust owns the local kit manifest and archive. The targets are:

- A 1920 by 1080 stereo MP4 film at 24 fps.
- Three 1080 by 1920 promos of at most 30 seconds.
- A 1920 by 1080 JPEG thumbnail.
- 1920 by 1920 JPEG artwork.

Tested native support is necessary for H.264 and AAC.

### Behavior rules

- Six outputs means one film, three promos, and two stills from actual assets. Placeholder frames do not satisfy production acceptance.
- The film covers the canonical song. Promos use rational timing and the same master binding.
- Cinematic scenes, native-script lyrics, and music-reactive environments use explicit layer and protection rules.
- Incomplete outputs and missing reviews cannot become approved. The package format, manifest version, and review schemas remain open.

### Implementation pieces

- DELIVER-07.1 validates source bindings and six-output recipes.
- DELIVER-07.2 exports media and stills with per-output receipts.
- DELIVER-07.3 archives manifests, sources, measured QC, and separate review records.

### Verification

- DELIVER-07-A builds a full-song corpus with real assets. Independent decode measurements must agree with all six hashes, dimensions, full-song duration, promo bounds, and source bindings. Separate recorded reviews are necessary for complete playback and listening.
- DELIVER-07-B removes one still or swaps the canonical master. Kit verification fails. Verification does not accept a five-output or substituted archive.

### Status and dependencies

Planned P5, owned by Rust. Depends on DELIVER-02, FUSION-03, FUSION-08, AUDIO-01, PHOTO-02, CORE-06, MEDIA-01, EDIT-01, DELIVER-05, and AUDIO-08. No native receipt exists for this optional profile. For the named Pal Pal scenario, production requires the current source binding and review holds.

## COLLAB-01. Project libraries and tenant authorization

### What it does

Project libraries group projects for an authenticated creator or team. Tenant authorization prevents cross-customer reads and changes.

### Scenario

Two labels use the hosted application for separate music catalogs. An agent for label A guesses the project identifier for label B. The agent requests the revision for label B. The application rejects the request before source lookup or native execution. Label A sees its catalog without disclosure of names, receipts, or media links from label B.

### Inputs and result

Planned command `project.authorize` takes an authenticated operation context and a project resource reference. The separate Effect application owns membership and authorization decisions. Authentication establishes caller identity. Results bind operation, project, and bounded execution authority. Explicit decisions are necessary for roles, token lifetime, and durable membership schemas.

### Behavior rules

- Tenant identity comes from authentication. The application never accepts caller-supplied tenant identity as authority.
- Authorization is necessary for revision, source, job, and receipt access. A valid project name is insufficient.
- Revocation prevents new operations. Revocation invalidates authority that remains in effect. The revocation uses a tested policy.
- Native hosts receive scoped tickets and trusted resource bindings. Hosted callers cannot supply arbitrary local paths.
- Local SQLite projects remain independently usable without Effect credentials. The directory layout does not give hosted tenant isolation.

### Implementation pieces

- COLLAB-01.1 defines membership and operation-specific access rules.
- COLLAB-01.2 resolves authenticated identity and issues scoped native-host tickets.
- COLLAB-01.3 enforces revocation and isolates each hosted resource lookup.

### Verification

- COLLAB-01-A exercises an authorized project through the application and test native host. Durable readback contains only the authenticated tenant's resources.
- COLLAB-01-B attempts cross-tenant revision, source, job, and receipt lookups. Each fails without native execution or private-object access.

### Status and dependencies

Planned P6, owned by Effect in a separate application. Depends on CORE-01 and CORE-02. Native local revisions exist today. Hosted libraries and authorization are absent.

## COLLAB-02. Optimistic revisions and shared editing

### What it does

Shared editing compares edits with the revision each editor saw. Compatible changes produce a revision. A stated resolution is necessary for conflicts.

### Scenario

Two agents examine revision 18. One changes the background clip's crop for frames 720 through 959. Another changes the Telugu caption during that interval. A proposed merge keeps both changes only if their fields and dependencies are independent. Caption changes to the same fields produce a conflict. The conflict prevents the removal of an edit.

### Inputs and result

Planned command `project.merge` takes a base revision, current revision, proposed typed changes, and stable intent. Rust owns validation and the new immutable revision or conflict report. Hosted authentication belongs to COLLAB-01. Merge policy, conflict paths, and change representation remain undecided.

### Behavior rules

- Rust compares the expected revision inside the commit transaction. Last-writer overwrite is not a merge policy.
- Identical intent replay returns the original result. Changed content under the same intent conflicts.
- Automatic merge starts with a documented subset of independent field edits. Explicit conflict rules are necessary for timing, track order, graph dependencies, and source substitutions.
- A rejected merge creates no partial revision. Historical snapshots and receipts stay immutable.
- The first version can reject each stale edit correctly. Separate reference cases are necessary for merge policies that permit more changes.

### Implementation pieces

- COLLAB-02.1 defines base-relative changes and conflict reports.
- COLLAB-02.2 adds atomic merge validation and stable-intent replay.
- COLLAB-02.3 enables measured independent-field rules after conservative rejection works.

### Verification

- COLLAB-02-A submits independent edits from one base. Snapshot readback must show both changes once, with one new merged revision.
- COLLAB-02-B submits caption edits that conflict. The conflict identifies the caption. Independent revision readback proves that neither update was lost.

### Status and dependencies

Planned P6, owned by native Rust. Depends on CORE-01, CORE-02, and CORE-03. Current `project.commit` rejects stale revisions. Shared merge and remote authorization remain absent.

## COLLAB-03. Clip bin and timeline ownership

### What it does

Ownership claims give temporary authority over named editing resources. Expiry and revocation release abandoned resources.

### Scenario

An assistant claims the interview bin to organize camera clips. Another editor works on the approved timeline. The assistant disconnects. After expiry, a new authenticated owner claims the bin. The old session cannot rename clips with expired authority.

### Inputs and result

Planned command `project.claim` binds authenticated actor, project, resource kind, resource ID, and requested operation. The separate Effect application owns claim records and lease tokens. Rust owns actual edit semantics. A bin is a named collection of assets.

MEDIA-02 is necessary for bin claims. A defined timeline model is necessary for timeline claims. Scope, lifetime, renewal, and revocation schemas remain open.

### Behavior rules

- Each claim has a bounded lifetime and an authority version. A resource name alone cannot authorize an edit.
- Claim enforcement must apply at the mutation boundary. A UI lock icon does not protect a resource.
- Expiry uses the authority's clock. Client clock changes cannot increase the duration of ownership.
- A stale owner cannot renew or commit after reassignment. Expected revision and stable intent checks still apply.
- The initial version claims whole resources. Measured overlap and dependency rules are necessary for partial-range claims.

### Implementation pieces

- COLLAB-03.1 defines resource scopes and claim lease records.
- COLLAB-03.2 issues, renews, releases, and revokes authenticated claims.
- COLLAB-03.3 validates claim version at mutation execution and completion.

### Verification

- COLLAB-03-A claims a bin and applies an authorized edit. Claim and revision readbacks identify the same actor and resource.
- COLLAB-03-B expires and reassigns a claim. An old token fails at the mutation boundary. The original revision stays unchanged.

### Status and dependencies

Planned P6, owned by Effect outside Rust. Ledger dependencies are CORE-01, CORE-02, and COLLAB-01. Native resource models are also necessary for claims. No claim service exists.

## COLLAB-04. Cloud media synchronization

### What it does

Synchronization transfers exact source bytes between authorized storage and execution hosts. Interrupted transfers preserve asset identity.

### Scenario

A documentary editor publishes a 2 GB camera recording for a remote test host. The upload stops halfway. The application resumes the missing transfer segments. The application then validates the complete object hash. The host receives the master bytes. A proxy remains a separate asset.

### Inputs and result

Planned command `media.publish` binds authenticated project, imported asset hash, byte count, media type, and transfer intent. Effect owns private object references and transfer state. Rust owns ingest measurements and source identity. Defined schemas are necessary for multipart transfer rules, chunk identity, retention, and proxy relationships.

### Behavior rules

- Complete-object hash and byte count must match the imported source before publication.
- Authorization covers upload, download, resume, and metadata. An object key without authorization gives no access.
- Transfer replay preserves the original content and intent. A different asset identity is necessary for changed bytes.
- Incomplete uploads cannot become usable master references. Proxies keep their own hashes and their declared relation to the master.
- Private R2 is a planned adapter. Local storage proves protocol cases. Local storage does not prove provider permissions or deployment.

### Implementation pieces

- COLLAB-04.1 defines content-addressed object and transfer records.
- COLLAB-04.2 implements bounded private transfers and interruption reconciliation.
- COLLAB-04.3 validates complete bytes before publication of authorized source references.

### Verification

- COLLAB-04-A interrupts a fixture transfer and resumes it. Independent hashes of the download match the original source and durable completion record.
- COLLAB-04-B changes a transfer segment or requests a different tenant's object. Integrity or authorization rejects publication and download.

### Status and dependencies

Planned P6, owned by Effect in a separate application. Depends on CORE-01, CORE-02, COLLAB-01, and MEDIA-01. Cloud sync is absent. Actual private-provider object and permission readback are necessary for production acceptance.

## COLLAB-05. Review annotations and notifications

### What it does

Reviews attach comments and decisions to exact rendered bytes. Notifications identify the artifact and interval for which review is necessary.

### Scenario

A reviewer marks the Telugu lyric at frame 420 as too low on a portrait promo. The agent adjusts the lyric position and exports a new hash. The old comment remains attached to the old promo. Review is necessary again for the new promo even if its display name stays unchanged.

### Inputs and result

Planned command `review.record` takes authenticated reviewer, registered artifact hash, revision, frame interval, annotation, and explicit review state. The separate Effect application owns the review record. Rust owns artifact integrity. Native-script comments remain unchanged. Notification channels, preferences, and approval-role schemas remain undecided.

### Behavior rules

- Reviews bind output hash and authenticated actor. A mutable filename cannot identify approved media.
- Technical verification, frame inspection, complete playback, listening, and creative approval use distinct states.
- Approval applies only to the named output and scope. Changed bytes do not inherit approval.
- Frame annotations use the artifact's rational rate and integer positions. Out-of-range comments fail before storage.
- Explicit configured recipient authority is necessary for notifications. The notification queue, provider delivery, and reviewer readback remain separate.

### Implementation pieces

- COLLAB-05.1 defines artifact-bound annotations and review states.
- COLLAB-05.2 enforces reviewer identity, role, interval, and hash bindings.
- COLLAB-05.3 adds opt-in notifications with independent delivery records.

### Verification

- COLLAB-05-A records a frame comment and scoped approval. Durable readback keeps reviewer identity, native-script text, interval, and exact artifact hash.
- COLLAB-05-B replaces the artifact or impersonates a reviewer. The service rejects the changed binding or identity and preserves the original record.

### Status and dependencies

Planned P6, owned by Effect outside the editor. Depends on CORE-01, CORE-02, COLLAB-01, and CORE-06. Native byte integrity exists. Annotations, notifications, and approval capture remain absent.

## EXT-01. OFX and effect plugin execution

### What it does

A plugin host runs supplied effects under a declared interface and resource policy. OFX means OpenFX, an interface family for image effects.

### Scenario

A commercial editor applies an experimental texture plugin to the background clip at frames 300 through 359. The foreground product and title remain outside the plugin's inputs. A plugin crash fails the render and identifies the operator. No clean frame silently replaces the failure.

### Inputs and result

Planned command `plugin.run` binds plugin binary hash, interface version, parameters, input buffers, frame position, and resource limits. Rust owns native validation and result measurements. The reusable library remains process-free. Isolated plugin processes belong to a native executable host. Primary-source research and experiments are necessary for interface, SDK, licensing, sandbox, and plugin choices.

### Behavior rules

- The host declares pixel format, color space, alpha convention, buffer lifetime, and thread policy before execution.
- Plugin identity and parameters enter operator and cache identity. Changed binaries cannot inherit old evidence.
- Crashes, timeouts, invalid buffers, or unsupported interfaces return explicit failures. No hidden renderer or libav dependency enters through a plugin.
- Initial support uses one bounded reference plugin. Separate experiments are necessary for broader compatibility and nondeterministic effects.
- Installed plugins do not establish proprietary effect parity or identical output.

### Implementation pieces

- EXT-01.1 researches one interface and defines a typed host contract.
- EXT-01.2 executes a bounded reference plugin with native failure isolation.
- EXT-01.3 validates buffer ownership, resource limits, and repeated-output measurements.

### Verification

- EXT-01-A runs a deterministic reference plugin over known pixels. An independent comparator validates output channels, alpha, and unchanged protected layers.
- EXT-01-B uses a plugin that crashes or has invalid buffers. The host rejects completion and keeps source bytes. The host creates no successful render receipt.

### Status and dependencies

Planned P7, owned by Rust native operators. Depends on CORE-01 and CORE-02. Real visual plugins also require native media and composition support. No plugin SDK, sandbox, or corpus is proven.

## EXT-02. Interchange EDL AAF XML and OTIO

### What it does

Interchange transfers a documented subset of timeline semantics. Reports identify unsupported semantics. Reports must not remove unsupported semantics without disclosure.

### Scenario

A documentary editor receives a cut list for ten interview clips at 30000/1001 fps. The agent imports source offsets and transitions into a new revision. The import format cannot represent a proprietary title effect. The report identifies the effect and interval for an explicit replacement decision.

### Inputs and result

Planned command `project.interchange` binds import or export direction, format and version, source document hash, source mapping, and revision. Rust owns parsed semantics, validation, and output artifacts.

EDL is an edit decision list. AAF is Advanced Authoring Format. XML is a document syntax. A named dialect is necessary. OTIO is OpenTimelineIO. Research is necessary for variants, SDKs, and licensing.

### Behavior rules

- Explicit mappings are necessary for frame rate, timecode interpretation, source offsets, and half-open intervals.
- Missing sources stay unresolved or fail under the declared policy. Similar filenames cannot substitute different source hashes.
- Import creates an atomic new revision. Current snapshots remain immutable.
- The initial version supports one measured format subset. Round-trip success applies only to that subset.
- Unsupported tracks, effects, or audio mappings produce a loss report. The command must not flatten unsupported semantics without disclosure.

### Implementation pieces

- EXT-02.1 defines a format-specific supported-semantics table.
- EXT-02.2 parses and writes bounded documents with native time and source mappings.
- EXT-02.3 compares round-trip semantics and produces explicit loss reports.

### Verification

- EXT-02-A round-trips a golden cut-list corpus. An independent reference parser confirms clip order, rational rate, intervals, and source offsets.
- EXT-02-B imports an unsupported effect or missing source. The report identifies the exact loss, or atomic rejection leaves the project unchanged.

### Status and dependencies

Planned P7, owned by Rust. Depends on CORE-01 and CORE-02. The applicable editing and media models are also necessary for real timeline interchange. No listed interchange format is implemented.

## EXT-03. Control panels and capture hardware

### What it does

Hardware bindings map device controls to native commands. Capture bindings attach measured streams to source identities and timing rules.

### Scenario

An interview editor binds a jog wheel to frame-by-frame movement on a 24 fps timeline. One detent advances one frame inside timeline bounds. The device disconnects during review. The frame stays fixed, and the binding becomes unavailable. The same device identity is necessary for reconnection.

### Inputs and result

Planned command `device.bind` takes device identity, driver or interface version, permission state, and mapping profile. Rust owns native device validation and command translation. Sample-clock identity and source receipts are also necessary for capture results. Research and real hardware experiments are necessary for device selection, SDKs, licensing, OS permissions, and capture buffers.

### Behavior rules

- The binding records the model and stable identity. A port number alone cannot establish device identity.
- Control events use bounded native commands. A panel cannot bypass revision validation or change approved edits without disclosure.
- Disconnect cancels device input in the queue and keeps project state. Reconnection never replays unbounded input.
- Initial support proves one input device. Capture, monitor latency, and professional control panels remain separate advanced pieces.
- Declared timestamp and overflow policies are necessary for capture. Hardware availability does not prove a supported video format or GPU path.

### Implementation pieces

- EXT-03.1 inventories one device interface and permission contract.
- EXT-03.2 translates measured control events into typed native commands.
- EXT-03.3 handles disconnect and adds capture only after timing experiments pass.

### Verification

- EXT-03-A exercises a real device with a logged detent sequence. Native frame readback must equal the result specified by the mapping and timeline bounds.
- EXT-03-B disconnects the device and reconnects a different identity. No stale input mutates the project. The automatic device binding fails.

### Status and dependencies

Planned P7, owned by Rust. Depends on CORE-01 and CORE-02. Native ingest and timing support are also necessary for capture. No panel, capture SDK, or device evidence exists.

## EXT-04. Optional editor and review UI

### What it does

An optional interface presents native commands, results, and review evidence. Keyboard users examine projects, request edits, and review exact artifacts.

### Scenario

A creator opens a portrait promo and uses the keyboard to select the Telugu lyric layer at frame 480. The interface submits one position edit against the displayed revision. Another editor committed a change. The creator sees a conflict. Before the creator submits the edit again, the creator examines the new revision.

### Inputs and result

Planned command `ui.connect` represents adapter connection, discovery, and protocol negotiation. The separate UI application owns presentation, focus, and accessibility. Rust owns timeline semantics and media results. Hosted interfaces use COLLAB-01 authentication and COLLAB-05 reviews. React, Tauri, and Foldkit are unselected candidates. Compatibility proof is necessary for connection schemas and generated types.

### Behavior rules

- The interface discovers executable commands and schemas. The interface cannot present planned controls as executable features.
- Each edit uses Rust commands, expected revisions, and stable intents. The interface never writes SQLite directly or duplicates the timeline reducer.
- Rendered, measured, watched, heard, and approved states appear separately with exact artifact bindings.
- The local adapter inspects artifacts and displays native measurements. The adapter can display review records from external sources with their source and binding. It does not persist watched, heard, or approved states. Hosted review writes belong to COLLAB-05.
- Interaction checks are necessary for focus, control names, conflict feedback, and review intervals. Screenshots cannot prove keyboard access.
- Effect credentials and a browser are not necessary for local native execution. Hosted execution uses a separate application and authenticated native host.

### Implementation pieces

- EXT-04.1 compares UI candidates against command and accessibility requirements.
- EXT-04.2 builds a schema-compatible adapter with keyboard-accessible native controls.
- EXT-04.3 presents artifact-bound review states and explicit conflict recovery.

### Verification

- EXT-04-A uses keyboard-only local controls to examine, edit, render, and examine a fixture's artifact. Native revision and artifact readbacks must match the displayed result. A hosted review record is not necessary for the case. The case does not create a hosted review record.
- EXT-04-B submits a stale revision or changes the schema hash. The interface reports rejection without duplicate edits or a false success state.

### Status and dependencies

Planned P6, owned by a separate UI application. A local adapter depends on CORE-01 and CORE-02 plus the native edit and render capabilities exposed by its controls. COLLAB-01 and COLLAB-05 are also necessary for hosted review. No UI stack is implemented. The Rust CLI remains independently usable.
