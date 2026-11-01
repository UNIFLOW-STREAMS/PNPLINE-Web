# PNPLINE directional daylight v002

Feedback: v001 produced too little visible change. This variant changes light direction and key/fill balance more strongly.

- Source: latest hero-material-v001.blend, SHA256 recorded in source.json.
- World strength .45 -> .12; camera background retained.
- CN key: 420000W, size45m, position(-200,-110,135), target(-120,0,65); fill18000W.
- US key: 520000W, size50m, position(-10,-80,205), target(80,28,125); rim55000W, size80m.
- Warehouse: general ceiling220W, aisle260W; local task lights450/550/320W at7.5m in warehouse authoring chart.
- AgX Medium High Contrast and exposure+.3 retained.
- Four previews: 110,332,720,820 at960x540, Cycles OptiX,32 samples,min32,adaptive.02,seed29,OIDN. Original previews reused from the same source hash and same rendering parameters; metadata retained.
- review/comparison: left ORIGINAL, right V002. No grading or exposure adjustment applied to the comparison images.
- Saved blend retains original production render settings. Only lighting/world and3 additional light objects differ. Geometry, material, action, camera and non-light object fingerprints match on reopen. See verification.json.
- This is a stronger lighting study reviewed on four still frames; full animation playback is not included.

Reproduction: Blender5.1 source file --python scripts/lighting.py -- build. Source -- before; candidate -- after; candidate -- verify. Then Python scripts/package.py. Output paths follow the script directory.
