import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
rows=[]
for f in range(330,541,5):
 s.frame_set(f);U=s.objects['US_FRAME'].matrix_world
 row={'f':f}
 for label,pts in {'title':[(x,53,z) for x in [-20,20] for z in [1,23]],'statue':[(-36,7,z) for z in [-2,9]],'city':[(x,30,z) for x in [-25,25] for z in [1,12]]}.items():
  row[label]=[list(world_to_camera_view(s,s.camera,U@Vector(p))) for p in pts]
 rows.append(row)
(R/'review/projection-probe.json').write_text(json.dumps(rows,indent=2))
for row in rows:
 if row['f']%15==0:print(row['f'],{k:[[round(v,2) for v in p[:2]] for p in row[k]] for k in ['title','statue']})
