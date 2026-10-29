import bpy,math,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;rows=[];prev=None
for i in range(467*4,530*4+1):
 s.frame_set(i//4,subframe=(i%4)/4);m=s.camera.matrix_world.copy();q=m.to_quaternion();speed=turn=0
 if prev:
  speed=(m.translation-prev[0]).length*48
  turn=math.degrees(q.rotation_difference(prev[1]).angle)*48
 rows.append({'f':i/4,'speed':speed,'turn':turn,'q':list(q),'raw':list(s.camera.rotation_quaternion)})
 prev=(m.translation.copy(),q.copy())
print('PEAKS',json.dumps(sorted(rows,key=lambda r:r['turn'],reverse=True)[:5]))
(R/'review'/f'{Path(bpy.data.filepath).stem}-motion-diagnostic.json').write_text(json.dumps(rows,indent=2))
