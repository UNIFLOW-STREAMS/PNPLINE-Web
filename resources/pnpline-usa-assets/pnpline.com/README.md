# PNPLINE public art source inventory

Generated: 2026-09-15T13:10:22.0932330+00:00

This directory is produced by `tools/extract-pnpline-art-assets.ps1`. It contains public visual resources observed on `https://www.pnpline.com/` and provenance metadata. Collection does **not** establish publication rights or approval for use on another site. Every asset defaults to `rightsStatus: unverified` and `approvalStatus: unreviewed`.

## Run summary

- Crawled pages: 61
- Discovered asset references: 533
- Unique assets: 45
- Images: 33
- Videos: 0
- Icons and SVG: 12
- Downloaded assets: 43
- SHA-256 deduplications: 0
- Skipped references: 427
- Failed assets: 9
- Recorded errors: 10
- Total bytes: 11194669

## Files

- `asset-manifest.json`: unique assets, hashes, sources, discovery context, variants, and review status.
- `pages.json`: crawled pages, per-page asset IDs, font-icon metadata, and remote streaming references.
- `skipped.json`: unsupported, excluded, or policy-limited references.
- `errors.json`: request, parsing, and per-asset failures.
- `assets/`: downloaded binaries and extracted inline SVG files.

Re-run without `-Refresh` to preserve an existing content-addressed file when its SHA-256 matches. Use `-Refresh` to replace the file after downloading the current response. Use `-DownloadVariants` only when WordPress/CDN derivatives are also required.