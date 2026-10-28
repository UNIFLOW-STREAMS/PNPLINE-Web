import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;rows=[]
for f in range(73):
 s.frame_set(f);p=s.camera.matrix_world.translation
 for x in [-1.25,0,1.25]:
  for z in [-.5,0,.5]:
   t=s.objects['A01_CONTAINER'].matrix_world@Vector((x,0,z));d=t-p
   hit=s.ray_cast(bpy.context.evaluated_depsgraph_get(),p,d.normalized(),distance=d.length)
   rows.append({'frame':f,'sample':[x,z],'first_object':hit[4].name if hit[0]else None})
blocked=[r for r in rows if r['first_object']and r['first_object'].startswith('CR_LEG_')]
tag=sys.argv[sys.argv.index('--')+1]if '--'in sys.argv else 'city-s1'
(R/'review'/f'{tag}.json').write_text(json.dumps({'blocked_samples':blocked,'rows':rows},indent=2));print('CRANE_LEG_BLOCKED',len(blocked));assert not blocked,'Crane leg blocks hero cargo sample'
