# PNPLINE Industrial 3D v1

2026-11-10 · Canonical style for future PNPLINE logistics illustrations, EN and zh-CN.

## Decision

Use a midpoint between the original architectural warehouse realism and the cleaner service illustrations. Retain real construction detail and spatial depth; simplify only irrelevant scenery. The first overly simplified panorama was rejected and is not the style reference. The old photographic warehouse panorama is replaced by a wide scene built from the same visual vocabulary. All four service illustrations and the wide warehouse panorama now use the middle-ground realism target. Freight gains engineered deck, container-door and crane details; fulfillment gains powered rollers, bolted steel frames and corrugated-board detail; distribution gains realistic chassis, body panels, tires and fittings. These five assets form the reference set. Do not confuse a detailed photograph, a line icon, and a miniature illustration in the same image role.

## Style specification

| Element | Standard |
|---|---|
| Form | Semi-realistic industrial 3D; credible construction, operational detail, readable spatial depth and clear silhouettes |
| Architecture | Matte warm white and light gray; no gloss or concrete weathering |
| Branded equipment | Cyan #00ABE1 target for rack frames, conveyors, cargo boxes; natural lighting can vary rendered pixels |
| Mechanical parts | Graphite #242826 target; dark tires/chassis |
| Cartons | Warm kraft/sand, related to UI sand #E8DDCE; subtle texture |
| Camera | Elevated three-quarter, approximately 25 degrees, weak perspective; wide panorama can use a shallower view for clarity |
| Light | Broad upper-left studio key, soft contact shadow, no dramatic rim, glow or depth-of-field blur |
| Detail | Retain rack bracing, dock hardware, package variation, floor joints, conveyors and machinery; remove unrelated scenery, crowds and ornamental landscaping |
| Geography | Small US flag is allowed on the US warehouse; no vendor/manufacturer logos |
| Background | True alpha cutout; no painted rectangle or color wash; UI owns its background |
| Text and states | No rasterized titles, labels, numbers or selected states; HTML/SVG overlays, shared across locales |
| Icons | Existing Lucide outlines, currentColor, same icon size/stroke for equivalent controls |

Palette values are art-direction targets, not claims that shaded rendered pixels match exact HEX values. UI colors and video grading are separate and unchanged.

## Canonical files

- freight.png: ship, port crane and aircraft; international transport.
- warehouse.png: newly regenerated compact storage scene with rack bracing, pallet wrapping, concrete joints and dock hardware; supporting color/material reference. The new panorama master defines the target level of realism.
- fulfillment.png: open carton, scanner, printer and conveyor; picking/packing.
- distribution.png: US medium-duty box truck and pallet; domestic distribution.
- warehouse-panorama.webp: receiving left, inventory center, packing/dispatch right; same materials at scene scale.

All five are deployed under public/assets/industrial-3d-v2 in both apps. Editable-generation source and lossless master: output/asset-style-v2. Original service files and old warehouse-workflow image remain preserved.

## Framing and delivery

Service canvases remain 1536×1024. Panorama master is 2172×724; the existing 1672:455 viewport uses contain to retain the entire warehouse without distortion or cropping. Its section height and scroll mapping stay stable. Stage markers are DOM text at 22/45/74% horizontal and 86/77/75% vertical; update positions if scene composition changes. Inspect at 320, 390, 768, 1440 and 1920px before accepting a new image. Readable text stays outside the raster. Do not add outlines around transparent artwork (Jakub better-ui).

## Reuse procedure

1. Read this file before generating new PNPLINE artwork.
2. Attach warehouse-panorama-master.png as the realism/material master and the closest service subject as composition reference.
3. Use the shared prompt below; change only subject and composition.
4. Generate actual transparent output; save a versioned master and production derivative without overwriting old assets.
5. Check silhouettes and contact shadows over paper and dark backgrounds. Match apparent size in the actual card, not only source pixels.
6. Use identical image bytes in EN/ZH; localize HTML labels and alt descriptions only.
7. Reject unrelated props, baked text, photographic landscaping, toy-like proportions, mismatched lighting, or a white backplate.

## Shared generation prompt

PNPLINE Industrial 3D v1. Create a refined semi-realistic industrial 3D illustration matching the supplied warehouse-panorama-master.png style master. Architectural realism balanced with editorial product-illustration clarity; preserve spatial depth, functional joints, rack bracing, steel highlights, docks, packing machinery and pallet handling, not a toy or a photoreal aerial photograph. Matte warm-white and light-gray architecture, cyan #00ABE1 painted structural metal and vehicle bodies, graphite mechanical parts, warm kraft cardboard. Elevated three-quarter view around 25 degrees with weak perspective, broad soft upper-left studio lighting, gentle contact shadows, all objects in focus. Crisp silhouettes and restrained microtexture. Actual transparent alpha outside objects, no colored backplate, no landscape, no unrelated trees, no bloom, no dramatic lighting, no manufacturer logos. No baked titles, numbers, route lines or UI; render these in HTML. Subject: {SUBJECT}. Composition: {COMPOSITION}. Use the canonical reference image, not only this text, for every new generation. Match apparent visual size to the existing series.

## Tools and scope

Jakub better-ui: consistent image treatment and state markers; better-colors: existing semantic palette rather than a second accent scheme; better-layout: preserve viewport geometry and bilingual grouping. New panorama generated with built-in imagegen using warehouse.png as style reference and the previous panorama only for functional arrangement. No video file, filter, font or scroll controller was changed.


## Asset export revision 2

Same approved Industrial 3D v1 style, complete five-asset set. The three remaining service illustrations were regenerated using warehouse.png as the material/realism reference and their former images only for subject/composition. See service-prompts.json for exact prompts. No type, layout, card geometry, video or scroll behavior changed. Previous export remains in output/asset-style-v1 and public/assets/industrial-3d-v1.
