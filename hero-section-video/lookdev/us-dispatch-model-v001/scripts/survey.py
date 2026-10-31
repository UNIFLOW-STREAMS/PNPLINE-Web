import bpy,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(900)
U=s.objects['US_FRAME'].matrix_world;I=U.inverted();rows=[]
for o in s.objects:
 if any(w in o.name.upper() for w in ['WH_','E07','E08','E09','E10','E11','E12','ROAD','GROUND','A04','A05','DEST','LAND','FRAME']):
  pts=[I@o.matrix_world@Vector(p) for p in o.bound_box] if o.type in ['MESH','CURVE','FONT'] else [I@o.matrix_world.translation]
  rows.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,pos=list(I@o.matrix_world.translation),min=[min(p[i] for p in pts) for i in range(3)],max=[max(p[i] for p in pts) for i in range(3)],materials=[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []))
(R/'review/survey.json').write_text(json.dumps(rows,indent=2));print('SURVEY',len(rows))
