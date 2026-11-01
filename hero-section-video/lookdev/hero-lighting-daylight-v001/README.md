# PNPLINE daylight lighting v001

Source: F:\pnpline-landing\hero-section-video\lookdev\hero-material-v001\pnpline-hero-material-v001.blend

Separate working file: pnpline-hero-lighting-daylight-v001.blend

Source remains unchanged. The lighting variant reduces environment and fill, shapes the exterior key, neutralizes light colors and adds 3 warehouse task lights. Existing camera, geometry, materials and animation fingerprints match after reopening the saved file. Details: verification.json and changes.json.

Comparison frames: 45, 110, 200, 332, 530, 720, 820, 930. Before and after: Cycles OptiX, 1440x810, maximum64 samples, minimum32, adaptive threshold .02, OIDN, seed29, animated seed off. AgX Medium High Contrast, exposure+.3. These are still comparisons; full animation and temporal/compression review were not performed.

The saved Blender file retains its original production render settings. Preview settings are applied only in memory after saving.

Open review.html for a before/after slider and all 8 paired views. review/before and review/after contain full 1440x810 PNGs. review/comparison contains labeled pairs. review/comparison-overview.jpg shows four principal frames.

Candidate SHA256: 54442caad9ac66566f8826ea3f5ea860eef52d0cb929297593ec47943216c222

Reproduce: open the source blend with Blender 5.1 background factory-startup and run scripts/lighting.py -- build; render source with -- before; open candidate and run -- after, then -- verify; run Python scripts/package.py. Paths are recorded in scripts/lighting.py; adjust ROOT/SOURCE when moving.
