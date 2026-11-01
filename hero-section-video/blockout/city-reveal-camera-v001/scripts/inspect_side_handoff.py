import bpy,json
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;R=Path(__file__).resolve().parents[1];I=s.objects['US_FRAME'].matrix_world.inverted()
print('RIGS',[o.name for o in s.objects if o.type=='EMPTY' and o.name.startswith(('A01','A02','A03'))])
names=['SHIP_HULL','A01_CONTAINER','A02_SPREADER','A03_TRAILER','A03_TRACTOR','CAM_MASTER','CAM_LOOK_TARGET']
out={'source':bpy.data.filepath,'samples':[]}
for f in [408,430,440,456,479,496,500,504,512,528,552,576,592,600,608,624,640,648,672]:
 s.frame_set(f);row={'frame':f}
 for n in names:
  if n in s.objects:row[n]=[round(v,4) for v in I@s.objects[n].matrix_world.translation]
 row['lens']=s.camera.data.lens;out['samples'].append(row)
print(json.dumps(out,indent=2));(R/'review/side-handoff-source.json').write_text(json.dumps(out,indent=2))
