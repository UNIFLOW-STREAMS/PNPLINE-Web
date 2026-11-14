# PNPLINE — Framer refinement v2

Preview: http://127.0.0.1:3210

This separate English landing-site revision adapts the Framer DESIGN.md in
`design-refs/framer.DESIGN.md` to PNPLINE's established visual identity.
The previous `output/pnpline-web-air-v1` site remains untouched (port 3101).

## Run

```sh
npm install
npm run dev
# Production:
npm run build
npm run start
```

Local dependencies currently use a junction to the existing installation.
For an independent checkout or deployment, install from package-lock.json.
Public media is copied into this version, including the original videos.

## What changed

- Floating navigation with left-aligned logo, centered links and pill actions.
- Two equally weighted service columns with all four miniature 3D artworks.
- A United States location label on the warehouse card.
- Consistent section rhythm, heading measures and compact reading surfaces.
- Refined card edges, rounded controls, aligned actions and sidebar FAQ tabs.
- Responsive single-column service cards below 700px.

All existing service descriptions, detail states, comparison tables, FAQ and
quote validation remain. Quote checking is still a local preview, not delivery.

## Preserved constraints

Original full-screen video, viewport-based scroll pacing and media controller;
no whole-video filter, wash, blend effect or opacity reduction. Smiley Sans 400
and Alibaba PuHuiTi remain. Blue card backgrounds remain at 50% alpha, with
5px backdrop blur on desktop and 4px on mobile. The source is still bright;
`app/media-theme.ts` supports a future dark-background film via foreground only.

## Design source

https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/framer/DESIGN.md

This is a community analysis, not Framer's official design system. PNPLINE's
adaptations and explicit exceptions are documented in DESIGN.md.
