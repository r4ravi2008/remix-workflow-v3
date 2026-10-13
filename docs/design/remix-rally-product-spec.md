# Remix Rally Product Spec

## Problem Statement

Song requests are scattered across YouTube comments. The creator has no durable queue, duplicate requests fragment support, and viewers cannot see what is popular, selected, in production, or released. Engagement ends after the comment, while the creator repeatedly scans threads and answers the same status questions.

The creator needs a public, community-informed remix queue that turns disconnected comments into one transparent song journey, rewards useful participation, and keeps artistic and publishing decisions under creator control.

## Solution

Build Remix Rally, a public queue and lightweight audience game. The home page ranks canonical song requests; each request page shows the path from request to release; points, badges, and limited seasons reward participation without changing voting power.

Keep the deployed application deliberately small. A FoldKit and Effect SPA styled with Tailwind CSS is served by Cloudflare Worker Static Assets. A Worker exposes public commands, creator commands, and one protected agent-write interface. D1 owns tracks, aliases, requests, votes, stages, rewards, and audit history. Alchemy Run declares the Worker, assets, D1, bindings, secrets, domains, and isolated environments.

YouTube discovery and song resolution are not application subsystems. A scheduled Codex automation invokes a song-sync skill. The skill reads comments through a YouTube MCP adapter, interprets each comment directly, searches the web and music catalogs for the exact recording, matches the result to Remix Rally's internal catalog, and submits a structured resolved request through the protected Worker interface. The agent has no direct D1 access. Ambiguous results create no canonical catalog mutation and are returned for review.

Audience engagement replies are a separate skill and workflow. They remain exact-text, exact-comment, human-approved before any external publication.

## User Stories

1. As an audience member, I want to see the active remix queue immediately, so I understand current community support.
2. As an audience member, I want every request to show its stage, so I know whether it is voting, queued, in progress, released, declined, or merged.
3. As an audience member, I want to search before submitting, so I can support an existing request.
4. As an audience member, I want to submit a song URL and optional remix style, so the intended song is clear.
5. As an audience member, I want to upvote, downvote, change, or remove my vote, so the queue reflects my current preference.
6. As an audience member, I want accidental duplicate votes prevented, so totals remain credible.
7. As an audience member, I want a concise ranking explanation, so ordering does not feel arbitrary.
8. As an audience member, I want creator priority labeled with a public-safe reason, so editorial judgment is transparent.
9. As an audience member, I want a stable link for each canonical song, so I can share and revisit it.
10. As an audience member, I want duplicate links redirected to the canonical request, so contributions survive merges.
11. As an audience member, I want my request and support credit preserved after a merge, so deduplication is lossless.
12. As an audience member, I want creator-authored progress updates, so I have a reason to return.
13. As an audience member, I want a request page to become a release page after publication, so the journey has a payoff.
14. As an audience member, I want a release archive, so I can discover completed community requests.
15. As an audience member, I want to see requests I submitted or supported, so I can track my participation.
16. As an audience member, I want bounded points and badges, so participation feels recognized.
17. As an audience member, I want rewards kept separate from voting power, so the system is not pay-to-win or tenure-to-win.
18. As an audience member, I want a limited Remix Rally season with a theme and collective goal, so the queue feels like an event.
19. As an audience member, I want clear wording that votes inform rather than guarantee production, so creator judgment remains understood.
20. As an audience member, I want failed optimistic actions visibly reconciled, so I never mistake an unrecorded action for success.
21. As an audience member, I want public pages to omit raw YouTube profiles and moderation details, so participation does not expose unnecessary personal data.
22. As the creator, I want new request comments discovered on a chosen schedule, so I do not manually inspect every video.
23. As the creator, I want a stable source comment ID to make repeated scans safe, so one comment cannot create duplicate demand.
24. As the creator, I want the agent to identify the exact recording rather than only a loose title, so covers, live versions, remasters, and regional variants do not collapse incorrectly.
25. As the creator, I want each resolved request to include source text, source URLs, a canonical YouTube video, external aliases, and evidence URLs, so the result is auditable.
26. As the creator, I want the agent to search the internal catalog before proposing a track, so support attaches to an existing canonical song whenever possible.
27. As the creator, I want ambiguous or conflicting identities returned as needs review without a catalog write, so unsupported guesses never become truth.
28. As the creator, I want to correct or reject review-only results, so exceptional cases remain manageable.
29. As the creator, I want merges to retain sources, supporters, vote history, and audit events, so consolidation loses nothing.
30. As the creator, I want deterministic ranking with a policy version, so results can be explained and reproduced.
31. As the creator, I want to set fan-visible stages independently from private remix workspace state, so production details are not leaked.
32. As the creator, I want an audit history of merges, priorities, stages, and agent writes, so consequential changes are traceable.
33. As the creator, I want the song-sync schedule disabled independently from the app, so scanning can stop without taking the queue offline.
34. As the creator, I want engagement replies handled separately from ingestion, so catalog updates cannot accidentally publish comments.
35. As the creator, I want any proposed reply bound to the exact channel, comment, and text revision, so approval cannot drift.
36. As an operator, I want the agent to write only through a protected, versioned Worker command, so D1 invariants stay local to the app.
37. As an operator, I want the Worker to validate schema, authorization, source uniqueness, and alias ownership atomically, so partial catalog writes cannot occur.
38. As an operator, I want every agent submission to return a durable receipt, so the skill advances its checkpoint only after confirmed storage.
39. As an operator, I want receipts to distinguish created, matched, already processed, needs review, conflict, and retryable failure, so recovery is explicit.
40. As an operator, I want logs to redact credentials and raw comment text by default, so diagnostics do not become a data leak.
41. As an operator, I want development, preview, and production resources isolated, so tests cannot mutate production state.
42. As an operator, I want Alchemy Run to declare all deployed Cloudflare resources and bindings, so dashboard-only drift does not become architecture.
43. As an operator, I want promotion blocked when declared and observed targets differ, so the Worker cannot attach to the wrong D1 database.
44. As an operator, I want stale-sync and catalog-integrity alerts, so silent automation failure becomes visible.
45. As a developer, I want browser, creator, and agent payloads defined by shared Effect Schemas, so invalid boundary data fails closed.
46. As a developer, I want FoldKit state expressed through an immutable Model, typed Messages, and Commands, so UI behavior is explicit and testable.
47. As a developer, I want Tailwind CSS to own the responsive visual system, so public and creator views remain coherent without React component libraries.

## Implementation Decisions

- The interface combines a queue-first home, a journey-first request page, and a deliberately light seasonal game layer. A generic fan-community platform is deferred.
- Public routes are `/`, `/r/:requestId`, `/me`, and `/releases`. Creator routes begin at `/studio`. Request creation is a duplicate-aware sheet opened from the queue.
- FoldKit and Effect own client state. The SPA uses one immutable Model, typed Messages, pure updates, fan-safe route projections, and Commands for Worker effects.
- Tailwind CSS owns layout, typography, color, responsive behavior, and interaction states. React, TanStack Start, and React component libraries are excluded.
- Cloudflare Worker Static Assets serves the Vite build. Worker-first `/api/*` routes prevent the SPA fallback from intercepting commands.
- The Worker exposes intent-oriented commands rather than CRUD mirrors of D1 tables.
- D1 is authoritative for internal `trackId`, track aliases, request sources, canonical requests, votes, ranking policy versions, stages, rewards, and audit events.
- Provider identifiers are aliases, never primary keys. Supported aliases can include YouTube video IDs, ISRC, MusicBrainz, Apple Music, Spotify, Shazam, and future catalogs.
- The protected seam is `upsertResolvedRequest(resolvedRequest) -> receipt`. The request contains `sourceEventId`, source metadata, exact resolved track metadata, canonical YouTube video ID, optional external identifiers, evidence URLs, and optional requested style.
- `sourceEventId` is the ingestion idempotency key. Repeating a successful submission returns the existing result and adds no duplicate demand.
- The Worker owns validation and atomic catalog mutation. The MCP adapter and Codex skill never write directly to D1.
- The song-sync skill interprets comments directly. There is no separate application classifier, confidence engine, prompt store, enrichment queue, or provider-adapter subsystem.
- The skill searches authoritative or high-quality web and catalog sources, identifies the exact recording, searches the internal catalog, and submits evidence with its result.
- Conflicting aliases or ambiguous recording identity produce `needs_review` with no canonical track or alias creation.
- The skill advances its scan checkpoint only after a durable Worker receipt. Retryable failures preserve the prior checkpoint.
- Public voting uses a signed pseudonymous session, D1 uniqueness, rate limiting, and Turnstile when risk warrants it. Creator routes use Cloudflare Access.
- Ranking is deterministic and versioned. Community score and labeled creator priority remain distinct. Points and badges never modify vote weight.
- Alchemy Run declares only the smaller deployed application: Worker, Static Assets, D1, bindings, secrets, custom domains, and isolated environments.
- Scheduling, YouTube credentials, catalog credentials, web research, and agent execution remain outside the deployed app with Codex automation and MCP adapters.
- Engagement-reply drafting and sending remain a separate approval-gated skill. Ingestion has no capability to publish a YouTube reply.

## Testing Decisions

- The primary app test seam is the production-built Worker boundary with isolated D1 and browser-visible assertions.
- Contract fixtures cover valid resolved requests, repeated `sourceEventId`, existing internal matches, new tracks, conflicting aliases, malformed evidence, ambiguous resolution, unauthorized writes, and retryable D1 failure.
- Tests assert that ambiguous or conflicting submissions create no canonical track, alias, request, or audit success event.
- Tests assert that a repeated successful source returns the prior receipt without increasing support twice.
- Browser tests cover queue discovery, duplicate-aware submission, voting and vote changes, optimistic reconciliation, canonical redirects, ranking explanations, stages, rewards, creator merges, and creator priority.
- FoldKit Story tests cover pure Model and Message transitions where browser tests would obscure state, especially optimistic voting, navigation, and duplicate handling.
- FoldKit Scene tests verify accessible behavior through roles, labels, keyboard actions, status announcements, focus restoration, reduced motion, and responsive layouts.
- A fixture-only song-sync run submits known comments and verifies exact receipts and D1 readback.
- A live dry run reads current comments and performs research but requires an explicit write flag before calling the protected interface.
- Replay tests run the same live or fixture batch twice and verify convergence on identical catalog and request state.
- Infrastructure tests verify deterministic names, environment isolation, Worker-first routing, SPA fallback, required bindings, secrets, preview cleanup, and promotion allowlists.
- Deployment verification reads back the exact Worker revision, domain route, D1 binding, health response, protected-write authorization failure, and one synthetic safe transaction.
- Scheduling is enabled only after fixture and live dry runs demonstrate exact-track resolution, durable receipts, replay safety, and stale-sync alerting.

## Out of Scope

- In-app YouTube polling, OAuth ownership, comment classification, prompt/model hosting, enrichment jobs, catalog provider adapters, Cloudflare Cron, Cloudflare Queues, dead-letter queues, or Workers AI.
- Direct MCP or agent access to D1.
- Automatically producing the highest-ranked request or guaranteeing a release date.
- Autonomous replies, moderation, priority changes, stage changes, remix generation, upload, or publication.
- Treating a loose song title, opaque confidence score, or single vendor identifier as sufficient canonical identity.
- Multi-creator tenancy, paid votes, cash prizes, transferable rewards, or increased voting power from points or tenure.
- Real-time WebSockets or Durable Objects before an observed need exists.
- Public exposure of raw comments, author profiles, moderation state, MCP credentials, research prompts, or private remix-workspace state.
- Final brand name, domain, Cloudflare account, scan cadence, preferred catalog evidence order, season theme, and permanent audience identity model.

## Further Notes

- Rollout order: prove FoldKit Static Assets and the protected write interface; launch the manual queue; run the song-sync skill against fixtures; run a live read-only dry run; enable guarded writes; then schedule scanning.
- Community support informs rather than dictates creative priority. Any creator override shown publicly needs a concise explanation.
- A recording is canonical only inside Remix Rally. External catalogs provide aliases and evidence; they do not own the internal identity.
- The app remains usable when the agent is offline. A stale-sync indicator communicates freshness without coupling public availability to automation availability.
- The companion System Design RFC contains the architecture diagram, data contract, failure behavior, operational gates, and milestones.
