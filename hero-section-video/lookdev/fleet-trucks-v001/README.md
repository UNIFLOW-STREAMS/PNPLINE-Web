# PNPLINE road fleet

This revision replaces the visible geometry of the inbound articulated truck and both warehouse dispatch trucks. The official seven-letter PNPLINE outline, traced from `resources/logo/PNP-LINE.webp`, is raised geometry on both long sides of each box. The inbound container is the existing working cargo object; it retains its pickup, landing and door hinges. The old inland crane assemblies and their foundations are removed; the operating quay cranes remain.

The previous integrated scene is archived in the sibling `container-ship-v001` folder. The road-fleet revision is `pnpline-fleet-trucks-v001.blend`. The unchanged canonical delivery location and the file hash are recorded in `delivery.json`.

Review: `review/after-617.png` and `review/after-880.png` use the actual animation camera. Tractor left/right and dispatch-product images use temporary studio cameras. The two yard images use the same position in the USA frame. The proof cameras and studio do not enter the saved scene.

From the repository root, with Blender 5.1 on PATH, the following PowerShell commands rebuild the versioned scene, audit its animation and render the proofs. Rebuilding does not replace the canonical scene.

```powershell
$fleet = 'hero-section-video/lookdev/fleet-trucks-v001'
$oldShip = 'hero-section-video/lookdev/container-ship-v001/pnpline-container-ship-v001.blend'
blender -b --factory-startup $oldShip --python-exit-code 1 -P "$fleet/scripts/build.py"
blender -b --factory-startup --python-exit-code 1 -P "$fleet/scripts/verify.py"
blender -b --factory-startup "$fleet/pnpline-fleet-trucks-v001.blend" --python-exit-code 1 -P "$fleet/scripts/render.py" -- tractor-left tractor-right 617 dispatch-product 880 dispatch yard
blender -b --factory-startup $oldShip --python-exit-code 1 -P "$fleet/scripts/render.py" -- yard
```

`review/verification.json` contains the world-transform, action, camera, truck-bed support, cargo clearance and logo-mesh checks. Tyres retain the original axle paths and nominal radius; their rounder tread contour differs slightly from the old faceted tyre envelope.
