---
name: PNPLINE Framer refinement
description: Editorial typography, structured service galleries and floating translucent surfaces over the original full-screen logistics film.
---

# PNPLINE Framer refinement v2

Route `/`, mode Persuade. The previous Air-based site is preserved separately.
Source reference: [Framer analysis](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/framer/DESIGN.md), captured in `design-refs/framer.DESIGN.md`.
This is an adaptation of the repository's analysis, not an official Framer implementation.

## Visual direction

Use Framer's oversized editorial hierarchy, gallery spacing, light-edge floating
surfaces, rounded selection controls and concise action hierarchy. PNPLINE's
industrial subject, cyan/blue palette, existing fonts, content and source film
take precedence over Framer's black canvas and multicolor atmospheric tiles.

## Tokens

| Role | Value |
|---|---|
| Ink / navy | #092d50 / #062c57 |
| Blue / cyan | #06568b / #00abe1 |
| Primary / secondary on-glass text | #f8fcff / #d4e5f3 |
| Link accent | #80e8ff |
| Card fill | linear-gradient(145deg, rgb(6 44 87 / .5), rgb(6 86 139 / .5)) |
| Card blur | 5px desktop, 4px at 800px and below |
| Card shadow | 0 20px 48px rgb(3 24 47 / .3), 0 4px 12px rgb(3 24 47 / .18) |
| Card edge | rgb(226 244 255 / .3); top rgb(255 255 255 / .55) |
| Radius | 20px desktop, 16px mobile; 100px action pills |
| Content width | 1102px for standard sections, with 24px side gutters (1150px overall); wide display headings and footer content up to 1552px; navigation up to 1600px |
| Gutter | clamp(20px, 5vw, 88px) |
| Section padding | clamp(64px, 7vw, 108px) |
| Panel padding | clamp(24px, 3.2vw, 48px) |
| Card gap | 24px desktop, 18px mobile |

## Typography

Keep self-hosted Smiley Sans at weight 400 for the hero and major statements;
never synthesize bold. Hero remains clamp(66px,7.6vw,144px), major section titles
use clamp(66px,6.6vw,128px), with -.02em tracking. The large Fulfill statement
retains its existing special display treatment. Mobile has explicit smaller sizes.
Alibaba PuHuiTi carries body, controls and normal titles. Service titles are
24–32px, primary service descriptions 18px desktop/16px mobile, details 16px/15px.
Long prose retains comfortable 1.6–1.75 line height rather than Framer's dense 1.3.

## Composition

- Full-viewport original film sits behind the complete document, with normal page scrolling.
- Floating navigation sits 16px from the top; logo left, links center, quote right.
- Hero pairs the existing statement with primary quote and secondary service actions.
- Four service cards use a consistent 2-column gallery, becoming one column below 700px.
- All service illustrations use the new 1536×1024 miniature series under `public/assets/service-miniatures`.
- Warehouse location is stated as HTML beside the illustration; imagery remains illustrative.
- Customer cards emphasize channel-specific copy instead of repeating decorative artwork.
- Section headlines and short introductions form an editorial split on wide screens.
- Introductions have a local 50%-alpha white reading surface over bright footage;
  dark-source mode uses 50%-alpha navy. These surfaces do not cover the video globally.
- Detail content uses existing tabs, disclosures, tables and preparation lists.
- FAQ category navigation sits beside questions on desktop and above them on mobile.
- Quote details stay on the existing white reading surface, with rounded inputs and pill submission.

## Interaction and accessibility

Keep semantic tabs and their ArrowLeft/Right, Home/End behavior, native details,
visible focus rings, mobile menu Escape handling and skip link. Primary controls
are at least 44px apart from the 40px compact header quote action. Motion remains
small hover feedback; reduced-motion disables transitions and loads a still poster.
Do not add entrance animations, scroll locks or more viewport-based chapter holds.
Tables scroll locally on mobile. Selected tabs use white fill and navy text.

## Invariants

Keep original media files, hero-mapping.js and hero-pacing.json byte-identical.
The scroll controller keeps the active video mounted beneath the startup poster. No full-video filter, wash, blend mode or opacity reduction.
Blue cards retain exactly .5 background alpha; foreground artwork and text remain
opaque. No factual copy changes, unverified facility claims, fixed quotes or
delivery promises. The inquiry form remains a local preview with tab-scoped draft
storage and must never report that an inquiry was sent.

## Implementation and evidence

`app/air.css` contains the inherited functional/responsive foundation.
`app/framer.css` is the explicit refinement layer, imported afterward by layout.tsx.
`app/air-landing.tsx` adds the unified service imagery, location label and hero action.
`qa-framer.cjs` checks the retained journeys and media invariants.
Screenshots and the QA report are stored under `.impeccable/review`.




## Canonical illustration system — Industrial 3D v1 (2026-11-10)

For new or revised raster illustrations, follow [ASSET-STYLE.md](ASSET-STYLE.md) and the five canonical assets in `public/assets/industrial-3d-v2/`. This supersedes earlier illustration-style notes only; typography, UI tokens and video behavior remain unchanged. Do not reintroduce the old photoreal warehouse panorama.
