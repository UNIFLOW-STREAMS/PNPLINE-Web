# PNPLINE #61: Scene 01 moodboard and styleframes

This directory contains the partial visual deliverable requested for GitHub issue #61.

## Review entry points

- `moodboard.png`: 10-source property moodboard. See `moodboard-sources.json` for attribution and restrictions.
- `comparison.png`: A/B/C side-by-side comparison.
- `preview/index.html`: interactive clean, Chinese UI overlay and safe-area review.
- `qa.md`: qualitative comparison and known defects.
- `manifest.json`: file, generation and integrity record.

Open `preview/index.html` locally in a browser. Query parameters are supported, for example `?variant=c&mode=mask`.

## Status

- A, `daylight logistics`: selected direction; newly generated image status is `review_pending`.
- B, `dusk cinematic`: comparison only; not selected.
- C, `top-down technical`: comparison only; not selected.
- Overall issue #61: not completed or closed by this partial deliverable.

All three clean images are generated concept visuals, not actual PNPLINE facilities. The Chinese H1 in the review overlay comes from the current page IA but still carries the IA requirement to verify the actual service scope; it is therefore marked as temporary review copy.

## Image sizing

The built-in image tool produced 1672×941 PNG originals. Each original is preserved in `originals/`. The 2048×1152 comparison asset was produced by removing one bottom pixel to obtain exact 16:9, then upscaling with Lanczos. These files are review derivatives, not native 2048×1152 generations.

## Mobile composition handoff

The mobile keyframe must be a separate portrait composition. Move the hero pallet and blue route into the lower-center vertical journey, retain the warehouse/transport hint in the upper third, and reserve the upper-left/top 35–40% for UI. A centered crop of the desktop frame is not an acceptable mobile asset.

## Tool record

- Orchestration session: Codex GPT-5-based session; exact model variant and reasoning effort were not exposed, so `gpt-5.6-sol/high` is not claimed.
- Image generation: built-in `imagegen`; provider model ID and seed were not exposed.
- Image processing: FFmpeg/FFprobe for exact-ratio review derivatives, board/comparison composition and dimensions.
- Browser skill: `playwright-interactive` was inspected but its required `js_repl` tool was unavailable. Browser review used bundled Playwright 1.62.1 with installed Chrome 153.0.8010.36 instead.
- Image inspection: the normal local `view_image` path failed because the Windows sandbox helper did not initialize. Non-destructive FFmpeg thumbnails were displayed through the tool output for visual review.

Creative review used the installed `creative-director` skill as a brief-compliance and comparative-critique framework. Skill attribution: Serge Shima, `creative-director-skill`, CC BY 4.0.

## Source precedence note

The latest GitHub #61 decision record and current GitHub #24 scope were treated as authoritative. The local Wayfinder map still contains legacy domain and earlier pilot wording that does not affect this visual deliverable; those unrelated source files were not changed. The homepage H1 comes from docs/pnpline-cn-page-ia.md, where its actual service scope still requires verification, so the overlay labels it as temporary review copy.
