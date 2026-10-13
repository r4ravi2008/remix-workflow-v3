---
name: Release Kit Studio
description: A film-first screening room for composing and reviewing complete song release kits.
colors:
  studio-ground: "#eeefea"
  paper: "#f8f9f5"
  ink: "#292e2a"
  muted-forest: "#59634f"
  divider: "#d4d9d0"
  forest: "#455d50"
  forest-deep: "#354d40"
  focus-forest: "#536f5b"
  rail-surface: "#e5e8e0"
  rail-active: "#d4dcce"
  rail-hover: "#dce2d6"
  nav-active-ink: "#364b3c"
  secondary-ink: "#4b5849"
  secondary-border: "#bdc7b8"
  secondary-hover: "#e0e6d9"
  graphite: "#242a29"
  graphite-overlay: "#182825ad"
  preview-text: "#e2e8de"
  on-image: "#ffffff"
  button-text: "#f9fbf4"
  image-shadow: "#142329"
  selected-surface: "#e2e8dc"
  selected-border: "#b9c7b0"
  format-surface: "#d4decb"
  format-border: "#8d9e80"
  form-surface: "#f5f7ef"
  form-ink: "#34432e"
  form-border: "#c4ccbc"
  upload-surface: "#e9ede3"
  notice-surface: "#e0e8d9"
  notice-ink: "#465b3c"
  error-surface: "#f3e4d9"
  error-ink: "#804329"
  status-amber: "#b3a47d"
typography:
  display:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(25px, 2.2vw, 34px)"
    fontWeight: 650
    lineHeight: 1.3
    letterSpacing: "-1.2px"
  headline:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 650
    letterSpacing: "-0.4px"
  title:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 650
  body:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.65
  utility:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "10px"
    fontWeight: 600
    lineHeight: 1.8
  nav:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 550
    lineHeight: 1.4
  film-title:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(18px, 2.3vw, 35px)"
    fontWeight: 500
    lineHeight: 1.25
    letterSpacing: "-0.6px"
  button:
    fontFamily: "Studio, Manrope, Helvetica Neue, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 650
    lineHeight: 1.6
rounded:
  micro: "2px"
  badge: "3px"
  control: "4px"
  upload: "5px"
  circle: "50%"
spacing:
  hairline: "1px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
  2xl: "24px"
  section: "31px"
  page: "37px"
components:
  button-primary:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.button-text}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "11px 16px"
    height: "42px"
  button-primary-hover:
    backgroundColor: "{colors.forest-deep}"
    textColor: "{colors.button-text}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.secondary-ink}"
    typography: "{typography.button}"
    rounded: "{rounded.control}"
    padding: "11px 16px"
    height: "42px"
  output-item:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "13px 11px"
    height: "63px"
  output-item-selected:
    backgroundColor: "{colors.selected-surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "13px 11px"
    height: "63px"
  input-field:
    backgroundColor: "{colors.form-surface}"
    textColor: "{colors.form-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.control}"
    padding: "12px"
  upload-block:
    backgroundColor: "{colors.upload-surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.upload}"
    padding: "21px"
  nav-item:
    backgroundColor: "transparent"
    textColor: "{colors.muted-forest}"
    typography: "{typography.nav}"
    rounded: "{rounded.upload}"
    padding: "12px"
    height: "44px"
  nav-item-active:
    backgroundColor: "{colors.rail-active}"
    textColor: "{colors.nav-active-ink}"
    typography: "{typography.nav}"
    rounded: "{rounded.upload}"
    padding: "12px"
    height: "44px"
  screening-aperture:
    backgroundColor: "{colors.graphite}"
    textColor: "{colors.on-image}"
    typography: "{typography.film-title}"
    size: "16:9, 9:16, or 1:1"
    width: "100%"
  production-boundary:
    backgroundColor: "transparent"
    textColor: "{colors.muted-forest}"
    typography: "{typography.utility}"
    padding: "21px 0 0 14px"
---

# Design System: Release Kit Studio

## Overview

**Creative North Star: "The Screening Room"**

Release Kit Studio treats a release as a screening: the film is the largest surface, with its deliverables held beside it. The design uses a warm gray studio ground and graphite surround. Forest controls and fine dividers keep attention on authored artwork.

The shipped preview labels its river-dusk photograph as illustrative. The image gives a cinematic appearance without a claim that a rendered film exists.

Typography stays in one Studio/Manrope family. A compact utility layer supports a measured release title, clear section heads, and a responsive film title over the image. Media apertures keep output proportions visible as the page moves from a rail-led desktop review to a film-first mobile stack. On mobile, a horizontal output strip remains visible. Local audio inspection and browser draft storage sit beside an explicit disconnected cloud-production boundary.

**Key Characteristics:**

- Film-first screening aperture with visible 16:9, 9:16, and 1:1 output proportions.
- Warm gray ground, graphite media surround, forest-green controls, and pale tonal surfaces.
- Single-family Manrope hierarchy with compact utility labels and restrained tracking.
- Honest distinction between illustrative preview, local draft work, and cloud production.

## Colors

The palette is low-chroma and studio-like. Warm gray and pale paper carry most of the screen. Graphite frames the image, and forest green marks action, selection, and focus.

### Primary

- **Forest green:** The primary control color for save actions, active affordances, and the shared icon family.
- **Deep forest:** The pressed or hover state for primary actions.
- **Focus forest:** The visible keyboard focus ring and related interaction cue.

### Secondary

- **Status amber:** A small production-state signal for the disconnected cloud boundary.
- **Notice and error tones:** Pale green and warm clay surfaces use darker semantic text. This keeps feedback separate from the primary action color.

### Neutral

- **Studio ground and paper:** Page, skip-link, and input-adjacent light surfaces.
- **Ink and muted forest:** Headings and secondary copy. Muted text is the reusable secondary foreground.
- **Rail surfaces:** The desktop navigation ground, active selection, and hover tint.
- **Graphite and overlay:** The screening surround and its small format badge.
- **Fine divider:** The one-pixel rule used to pace the page and separate production regions.
- **Format and selected surfaces:** Pale green-gray fills and borders used to identify output shapes and the selected manifest row.

### Named Rules

**The Quiet Green Rule.** Forest is an action and state color. Keep the warm ground, pale surfaces, and photographic frame dominant. The accent must remain legible and rare.

**The Honest Boundary Rule.** Keep illustrative preview, saved local draft work, and disconnected cloud production visibly distinct. Never make a sample frame read as a completed render.

## Typography

**Display Font:** Studio, backed by the local Manrope webfont (with Helvetica Neue, Arial, sans-serif fallback)

**Body Font:** Studio/Manrope (with Helvetica Neue, Arial, sans-serif fallback)

**Label/Mono Font:** No separate label or mono face. Utility labels stay in the same family.

**Character:** The single family keeps the room quiet and contemporary. Weight, size, and restrained negative tracking make the release title and film title authoritative. Small copy stays compact and operational. It does not become decorative chrome.

### Hierarchy

- **Display** (650, `clamp(25px, 2.2vw, 34px)`, 1.3, `-1.2px`): The release title at the top of the editor canvas.
- **Headline** (650, `17px`, `-0.4px`): Major section headings and the manifest title.
- **Title** (650, `13px`): Layer titles, output names, and other compact content headings.
- **Body** (400, `12px`, 1.65–1.9): Form copy, descriptions, explanations, and state details.
- **Utility** (600–750, `9px`–`11px`, up to `1.4px` tracking): Rail labels, format metadata, and compact status text. Uppercase is reserved for functional navigation labels.
- **Film title** (500, `clamp(18px, 2.3vw, 35px)`, 1.25, `-0.6px`): The release title over the screening image, with smaller fixed sizes for portrait and square apertures.

### Named Rules

**The Single-Family Rule.** Keep display, body, controls, and utility labels in Studio/Manrope. Use the shipped weight and size steps. Do not add a second display face.

## Layout

Desktop uses a two-part shell: a sticky 206px release rail and a flexible main canvas capped at 1580px. The main area starts with 37px top padding and fluid horizontal padding from 22px to 52px. The review region keeps the screening surface fluid and reserves a 237px manifest column with a 31px gap. At 1600px and above the manifest widens to 265px.

At 1150px the rail contracts to 172px, the manifest to 200px, and the review gap to 22px. At 900px the rail becomes a top bar with the release library hidden by default. The review remains a film-plus-manifest grid.

At 650px the page becomes a single column with 18px side padding: The film appears first. The manifest follows in a horizontal scroll strip of 151px cards. Song fields stack.

Artist fields use a two-column lower-density grid.

The creative-layer trio remains visible as three compact columns on the mobile capture.

The spacing rhythm favors 8px, 12px, 16px, 20px, and 24px intervals, with 31px section padding and a 37px page start. One-pixel rules create the major pauses instead of cards or heavy borders.

**The Artifact-First Rule.** Keep the screening aperture and its directly related output description before configuration forms. The creator sees the planned result before they supply every detail.

## Elevation & Depth

The system is flat at rest. Depth comes from tonal layering, the graphite screening surround, fine divider rules, and the authored photograph. Only the film title has a persistent, restrained text shadow.

The shadow keeps the title legible over the image. It is a media-legibility treatment, not a general card elevation language.

### Shadow Vocabulary

- **Film-title legibility** (`text-shadow: 0 1px 9px #142329`): Protects white title text over variable photographic detail.

### Named Rules

**The Flat Studio Rule.** Use tonal surfaces and one-pixel dividers for structure. Do not turn ordinary output rows or form sections into shadow cards.

## Shapes

Media apertures are squared and preserve their source proportions. Controls and output rows use quiet 4px corners. The upload zone opens to 5px with a dashed border. The format badge is 2px and the draft badge is 3px.

Circles are reserved for the artist avatar and upload affordance. Borders stay one pixel, with the upload boundary as the only dashed treatment.

## Components

The component language is restrained and tactile through color/state changes rather than lift: compact controls, pale selected rows, and clear focus treatment keep the editor canvas calm.

### Buttons

- **Shape:** Squared control corners (`4px`) with a 42px desktop minimum height.
- **Primary:** Forest fill, light text, 11px × 16px padding, and a dark-forest hover state.
- **Hover / Focus:** Primary buttons darken on hover. All buttons, links, inputs, selects, and textareas use a 2px focus outline with 4px offset in focus forest.
- **Secondary:** Transparent ground, muted green text, one-pixel border, and a pale green hover fill. The mobile control reduces to 40px minimum height and 9px × 12px padding.

### Cards / Containers

- **Screening viewer:** A graphite 16:9 surround holds an inner 16:9, 9:16, or 1:1 film frame. The selected format changes the aperture and its adjacent description together.
- **Output rows:** Output rows are transparent at rest. Selected rows use a pale fill. Every row has a 4px corner and a 63px desktop minimum height. Only the selected row shows an arrow.
- **Upload block:** Pale upload surface, 1px dashed boundary, 5px corner, and 21px desktop padding.
- **Shadow strategy:** Flat surfaces and rules. See Elevation & Depth for the single title-text shadow.

### Inputs / Fields

- **Style:** 12px text on a pale form surface, 1px border, 4px corner, 12px padding, and 1.65 line-height. Textareas remain vertically resizable with a 70px minimum height.
- **Focus:** The shared focus ring provides the state. Caret color follows the forest action color.
- **Upload control:** The native file control stays visible and receives the same pale border and compact file-selector treatment.

### Navigation

- **Desktop:** A sticky vertical rail carries the brand mark, functional studio navigation, saved releases, and local preview identity. Active navigation uses a pale green block and darker forest text.
- **Responsive:** At 900px the rail becomes a top bar. At 650px navigation labels collapse to 44px icon controls while accessible labels remain in the markup. The user can reopen the saved-release library as a full-width rail region.

### Screening Viewer & Format Strip

This is the signature component. A selected output changes the screening aperture, `object-position`, title placement, and adjacent output description as one state. Desktop keeps the manifest beside the film. Mobile moves the manifest below the creative layers into a horizontal, scroll-snapped strip and keeps the true format icons.

## Recommended and prohibited actions

These rules describe durable behavior in the shipped design. Current functional labels are not a license to add decorative chrome.

### Do:

- **Do** keep the film or illustrative screening surface as the largest first-view artifact, with formats directly beside or beneath it.
- **Do** preserve true output proportions and update the aperture description as one interaction.
- **Do** use forest for primary actions, active states, selected output rows, and keyboard focus with a quiet ground.
- **Do** label illustrative artwork, local draft behavior, and cloud availability with their actual state.
- **Do** keep music-responsive motion in the environment and protect people, lyrics, and consequential story details.
- **Do** keep original-script lyrics and their secondary copy in the same deliberate hierarchy as the rest of the studio.

### Do not:

- **Do not** introduce a second display face, generic saturated dashboard blue, or a high-chroma surface that competes with the film.
- **Do not** flatten landscape, portrait, and square outputs into one generic preview or detach a selected format from its description.
- **Do not** imply a rendered film, uploaded audio, or connected production worker from a frontend-only preview.
- **Do not** add detached shadow cards, gradients, or heavy rounded containers to a flat studio system.
- **Do not** treat functional utility labels such as `VISUAL DIRECTION` as a reusable decorative kicker or eyebrow pattern.
- **Do not** inherit muted small-text usage without a check of the actual foreground and surface pair. The current muted token is verified at 5.47:1 on the warm-gray body. It is 5.10:1 on the rail.
