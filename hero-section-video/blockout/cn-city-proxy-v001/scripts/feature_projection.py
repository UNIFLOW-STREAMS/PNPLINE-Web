"""Frame-indexed crop evidence for landmark distinguishing features; no pass threshold."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
objects=['CN_LM_SPHERE_TOWER_upper_sphere','CN_LM_SPHERE_TOWER_lower_sphere','CN_LM_OPEN_TOP_TOWER_lintel','CN_LM_TAPERED_TOWER_body','CN_LM_STEPPED_TOWER_crown']
out={}
for f in range(96,217):
 s.frame_set(f);row={}
 for n in objects:
  o=s.objects[n];pts=[world_to_camera_view(s,s.camera,o.matrix_world@v.co) for v in o.data.vertices]
  row[n]={'min_xy':[min(p[i] for p in pts) for i in range(2)],'max_xy':[max(p[i] for p in pts) for i in range(2)],'all_front':all(p.z>0 for p in pts)}
 out[f]=row
(R/'review/feature-crops.json').write_text(json.dumps(out,indent=2));print('FEATURE_PROJECTION',len(out))
