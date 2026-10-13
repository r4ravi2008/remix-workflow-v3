# Timeline layers and composition

This document defines planned P2 and P3 behavior.
P0 does not implement these features.
The Rust editor owns the layer model and compositing behavior.
A future UI displays the model.
Effect does not evaluate or own visual effects.

## Timeline model

A timeline contains ordered video tracks and independent audio tracks.
A video track contains timed clips.
Each track and clip has a stable identity.
A clip binds a source reference, timeline interval, source offset, transforms, and opacity.
A clip can also bind a composition graph.

Timeline intervals are half-open integer frame intervals at the declared rational frame rate.
Track order determines foreground order.
The compositor places higher video tracks over lower tracks.
Clip activation, opacity, and masks are different controls.
A missing clip does not act as an opaque black layer.

Audio tracks mix independently of visual track visibility.
The one-track P0 snapshot is a bounded first format.
P2 needs an explicit versioned migration to the multi-track format.
Historical snapshot hashes and completed intent results remain immutable through migration.

## Frame evaluation

For a requested frame, the renderer follows this sequence:

1. Resolve the immutable timeline revision and exact frame position.
2. Select active clips from each half-open interval.
3. Map timeline position to each source position with the declared offset and retiming rule.
4. Evaluate bounded effects, transform curves, and masks at that position.
5. Composite active video tracks in declared order with the color and alpha policy.
6. Return the frame and the bindings to the project and sources.

An inactive upper track lets the lower composition remain visible.
An opaque upper pixel hides lower pixels in normal compositing.
A transparent upper pixel preserves the lower pixel.
A mask controls the covered area.
A mask does not remove the clip from the timeline.

Clip opacity multiplies source alpha and mask coverage.
Normal source-over compositing uses premultiplied alpha.
Given effective source alpha `a`, premultiplied output is `source + destination * (1 - a)`.
The first P2 compositor uses linear RGB with sRGB primaries.
It uses normalized finite RGBA32F values and premultiplied alpha.

Reference buffers declare the working space.
The input boundary converts straight alpha to premultiplied alpha.
Unknown or differently tagged input spaces fail until their transform exists.
Configurable input and output transforms, HDR ranges, and gamut mapping belong to COLOR-01 and later P4 features.

The fixed P2 policy proves composition.
It does not prove a complete color-management pipeline.
P0 raw RGBA stills do not establish color-managed compositing support.

## Clip and graph ownership

Track order controls clips on different tracks.
A clip can reference a typed node graph for masks, merges, text, and effects.
Graph dependencies have stable node identities and a declared evaluation order.
Validation rejects cycles.
Cache identity includes the graph, inputs, timing, renderer build, and project bindings.

Masks can come from geometry, an image or video alpha channel, or a later tracked or keyed operator.
Mask inversion, feathering, transforms, coordinate space, and time binding need explicit parameters and tests.
Linked clips can share timing edits.
A timing link does not implicitly share visual opacity or masks.
Nested timelines need explicit time mapping and recursion rejection.

Overlap inside a track needs an explicit transition or selected policy.
The result cannot depend on database row order.
Unsupported blend modes, masks, retiming, or nodes fail before the renderer starts.
There is no hidden fallback.

## Music-video scenario

| Track | Source | Visibility and effects |
| --- | --- | --- |
| V1 | Cinematic environment | Full-width background with bounded music-reactive changes |
| V2 | Performer | Foreground extraction mask preserves the person over V1 |
| V3 | Native-script lyrics | Timed transparent text with independently keyed opacity |
| V4 | Foreground graphic | Masked particles or graphics in explicitly allowed regions |

Environment reactivity uses a protection mask for people, lyrics, and titles.
A clip selection in a UI does not authorize a change to its identity or approved timing.
An agent edits a declared layer or node through a typed transaction against an expected project revision.

## Acceptance corpus

The planned compositor needs independent reference frames for these cases:

| Case | Required observation |
| --- | --- |
| Inactive upper clip | Lower pixels remain visible before and after its exact interval |
| Opaque overlap | Upper pixels replace lower pixels in the declared stack order |
| Partial alpha | All output channels match the declared alpha and color policy |
| Masked overlap | The masked region reveals lower pixels with correct edge coverage |
| Animated mask and opacity | First, boundary, midpoint, and final sampled frames match expected values |
| Track reorder | Only the declared composition result changes. Source bindings and timings remain stable |
| Audio independence | An invisible visual track does not mute audio without an explicit audio edit |
| Protected reactive layer | People and text remain unchanged while permitted environment pixels react |
| Graph or timeline cycle | Reject the edit atomically without a new revision |
| Unsupported operator | Return a structured capability error before output |

EDIT-01, EDIT-05, EDIT-06, EDIT-08, FUSION-01, FUSION-02, FUSION-05, and FUSION-08 own these behaviors.
Each operator needs an input schema, limits, named case IDs, and an actual corpus before verification.
The current single-track PNG proof cannot promote any of these capabilities.
