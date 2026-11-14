# PNPLINE Framer refinement v2

An English landing page for sellers, brands and factories evaluating China-to-US freight, US warehousing, fulfillment and domestic delivery. The primary journey is to understand scope, review preparation and costs, then prepare quote inquiry details.

This is a new implementation at `F:/pnpline-landing/output/pnpline-web-framer-v2`, previewed at `http://127.0.0.1:3210`. Existing sites remain separate. The approved 25-view concept set is at `F:/pnpline-landing/output/pnpline-air-full-concept-v1`; `CONTENT-COVERAGE.json` maps every concept to a section or interactive state. The website uses semantic text, working tabs and disclosures rather than image-only pages.

## Product truth

Supplied service and explanatory content is the source of truth. Do not invent guarantees, prices, capacities, certifications or supported integrations. Scope, handling conditions, responsibilities and charges require shipment-specific confirmation. Illustrative logistics artwork is not proof of a particular facility.

The quote form is a preview only. It validates required cargo, email, consent, positive quantities and custom units. Unknown volume can be marked `Not sure`. Draft changes use this tab's `sessionStorage`, under `pnpline-inquiry-draft-air-v1`, and restore on reload; Clear form removes them. Storage failure does not block input. No sending backend is connected; successful checks must never be described as sent inquiries. `/privacy` explains the preview's data handling.

## Approved constraints

The user confirmed on 2026-11-05 that the original bright film should display immediately. They will later supply a source with a deep-blue background. Preserve original video bytes, `hero-mapping.js` and `hero-pacing.json`: scrolling advances frames using the original viewport-based timing, not autoplay or total-page progress.

Never add a whole-video wash, brightness/saturation filter or blend treatment. The film fills the viewport. `app/media-theme.ts` currently sets `sourceBackground` to `light`, giving exposed headings navy text. After replacing it with dark source footage, set `dark` for white foreground text. This setting changes text only. Reduced motion uses the still poster.

The visual direction uses self-hosted Smiley Sans 400 for key headings, Alibaba PuHuiTi for body and general headings, translucent blue panels and natural-material transparent logistics artwork. Quote introduction and form share one white surface to retain contrast over the dark final scene.

## Status and provenance

This documents the new English site, not the earlier variants on ports 3098/3099. Implementation sources: `app/air-landing.tsx`, `app/air.css`, `app/quote-inquiry.tsx`, `app/hero-services.tsx`, `app/media-theme.ts`. Approved direction: current PNPLINE identity with Framer layout refinement. Existing checks: `.impeccable/review/qa.json`. Visual system and composition: `DESIGN.md`; Framer source: `design-refs/framer.DESIGN.md`. Replacement media and an inquiry delivery service remain future work.

