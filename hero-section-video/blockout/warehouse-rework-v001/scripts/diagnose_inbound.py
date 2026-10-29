import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];rows={}
for filename in ['inputs/arrival-v010.blend','candidate-warehouse-v003.blend','candidate-warehouse-v005.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(R/filename));S=bpy.context.scene;rs=[]
 for f in [900,908,912,916,920,930,940,952]:
  S.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();origin=S.objects['CAM_MASTER'].matrix_world.translation;hits=[]
  for o in S.objects['W01_NEW_PALLET'].children:
   if '_BOX_' not in o.name:continue
   d=o.matrix_world.translation-origin;hit,loc,n,face,obj,m=S.ray_cast(deps,origin,d.normalized(),distance=d.length+.05)
   hits.append(obj.name if hit else None)
  rs.append({'frame':f,'hits':hits,'visible':sum(bool(x and x.startswith('W01_NEW_PALLET')) for x in hits)})
 rows[filename]=rs
(R/'review/inbound-visibility-diagnosis.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
