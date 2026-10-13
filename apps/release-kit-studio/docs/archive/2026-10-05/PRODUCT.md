# Release Kit Studio

<!-- impeccable:product-schema 1 -->

This document records the Resolve-based product plan. It does not describe current standalone Rust implementation status.

## Platform

web

## Stack

The user selected Foldkit, Effect, Alchemy, and Cloudflare. The frontend is hosted on Cloudflare. Generation runs on the user's RTX 4070 Ti workstation reached over Tailscale. The existing Resolve Studio installation on the local Mac edits and renders the media.

Cloud media workers are a later deployment option.

## Users

AI music creators who release songs frequently and need a complete visual release package.

## Product Purpose

The creator uploads a finished song and its canonical lyrics. The product must return a full music video and three independently composed vertical promos. It must also return a thumbnail and square artwork. After the creator sets the required inputs and artist preferences, one click starts production.

## Operating Context

Every film integrates cinematic direction, lyric art direction, and music-responsive visuals. These layers overlap in one film. They are not mutually exclusive product modes.

A saved artist profile preserves visual identity across songs. The soundtrack remains the uploaded audio master.

The film preserves native Indic script. Production and storage must work without the creator's laptop.

## Capabilities and Constraints

- Multi-tenant platform is the intended product, with project and asset authorization scoped to the tenant.
- Resolve Studio is the selected engine. No substitution with an FFmpeg montage or Remotion film.
- At first, reserve GPU generation and Mac Resolve work independently for one job each. Worker commands and production manifests must be recoverable.
- Automatic internal quality review and bounded repairs precede delivery. A technical render alone does not establish perceptual acceptance.
- Music response must preserve faces, lyrics, and consequential story props.
- Publication to social platforms is a separate action.
- The user explicitly requested Cloudflare for the frontend.
- The first real kit uses Pal Pal Nimisham with the Tailscale GPU and local Mac Resolve. It uses the selected Telugu deep-house mix. The verified WAV is 239.68 seconds. The input binding lives in its external workspace, never in public frontend assets.
- Proposed output defaults are a full-length 16:9 1080p film, three 9:16 promos, landscape thumbnail, and square art. Final technical presets remain configurable.
- Pricing, domain, final brand name, and tenant authentication provider remain open decisions. No rented GPU is needed for the local pilot.

## Evidence on Hand

The project-local music-video-director skill and its references define production records and quality gates. They also define musical editing, kinetic lyrics, cloud/local GPU generation, and Resolve post-production. Repository scripts run locally and often apply to individual songs. They are not a deployed multi-tenant backend. Verification of a live cloud Resolve worker or release-kit API for this product remains incomplete.

## Product Principles

1. Preserve the artist's identity. Direct each song based on its own emotion and structure.

2. Keep production evidence tied to exact asset and export versions.

3. Make targeted revisions. Keep accepted unrelated work.

4. Make costs predictable through reservations, bounded retries, and resource cleanup.

5. Distinguish demonstration, saved draft, active production, and completed deliverables in the interface.

## Brand Commitments

Release Kit Studio is a provisional name, not an approved permanent brand. The user selected the screening-room direction on the design page and chose code-led implementation. Finished visual acceptance remains separate.
