# QA record

## Scope and status

This is a partial deliverable for GitHub issue #61. It does not complete or close the issue. A remains the approved direction, while the newly generated A image is `review_pending`. B and C are comparison-only.

## Visual comparison

| Check | A: daylight logistics | B: dusk cinematic | C: top-down technical |
| --- | --- | --- | --- |
| Industrial-logistics recognition | Pass: container yard, truck, forklift and pallets read immediately | Pass: same category remains clear | Pass: yard circulation is clearest |
| Miniature-scale cue | Partial: clean macro look, but it can also read as a full-scale photograph | Partial: practical-light detail helps, but dusk reduces the scale cue | Pass: elevated model-like overview is strongest |
| Material separation | Pass: metal, concrete, cardboard and wrap are clear | Pass: reflections are attractive; dark surfaces lose some separation | Pass: strong daylight separation across containers and pallets |
| Logistics plausibility | Pass with review note: vehicle and pallet relationships are generally believable | Pass with review note: independent generation means object positions do not exactly match A | Partial: route is legible, but the blue pedestrian lane and forklift crossing need safety review |
| `#00ABE1` attention cue | Pass: restrained physical ground line | Pass: visible without becoming neon | Partial: route area is visually dominant and should be reduced if C informs A |
| Left UI safe area | Pass: strongest clean negative space | Pass: pass, though horizon lights add contrast behind small text | Pass: pass, but a blue vertical lane approaches the safe-area edge |
| Forbidden brands/claims/text | Pass at review resolution | Pass at review resolution | Partial: generic ground arrows/icons appear; no claim text is present, but generated markings need full-resolution review |
| Generation defects | Minor repeated carton patterns; no obvious melted major geometry | Minor repeated carton patterns and more photographic/full-scale reading | Repeated pallet patterns; blue lane/forklift crossing is the main operational concern |

## Direction decision

`daylight logistics` remains selected. B demonstrates that reflected practical light can improve material richness, but its lower contrast and dusk exception should not enter the six-scene constant. C demonstrates clearer circulation hierarchy and a stronger miniature cue; A can borrow only the clearer route hierarchy and slightly stronger scale staging, not the top-down camera.

## A-specific review notes

- The frame passes the first-stage composition test: China departure, industrial logistics, left UI zone and the blue forward route are immediately readable.
- The miniature-scale cue is not yet unequivocal. Consider one controlled A revision after user review, using slightly stronger foreground scale evidence and a subtler depth falloff without changing the approved camera direction.
- The empty left concrete area is deliberate for UI, but the final animation must keep it visually alive through restrained parallax rather than filling it with cargo.
- The generated A asset remains `review_pending` until the user explicitly approves it.

## Browser QA inventory

- Load A/B/C clean images without broken paths.
- Switch A → B → C and return to A using visible buttons.
- Switch Clean → UI → Safe area and return to UI.
- Confirm identical Chinese copy, font sizing and line-break rules across variants.
- Confirm `概念示意` and temporary-copy disclosure remain outside the clean images.
- Confirm the mask and image share the same 2048×1152 coordinate system.
- Check 1440×900 and 390×844 viewports for clipping and horizontal overflow.
- Exploratory check 1: open C directly by query parameter.
- Exploratory check 2: open safe-area mode directly by query parameter.

Initial 390×844 captures exposed clipped review controls and a CTA/step overlap. The controls were changed to a three-column minmax(0, 1fr) grid with constrained labels, and the mobile review stage was changed to 4:3. The mobile capture and overflow diagnostic were then rerun.


Final automated browser result: **pass**. Playwright 1.62.1 with Chrome 153.0.8010.36 verified all three overlay states, the A safe-area state, control round-trip, Chinese glyph presence, and 390×844 horizontal fit. The final run reported no console errors. Machine-readable evidence is in screenshots/browser-qa-results.json.

## Explicit non-validation

This work does not validate camera continuity, scene transitions, scroll seeking, video performance, reduced-motion switching, mobile keyframes, the #24 pilot or the #62 delivery contract. A may be evaluated later as a static fallback candidate; fallback implementation is not complete.
