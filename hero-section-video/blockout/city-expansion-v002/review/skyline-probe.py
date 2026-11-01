import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface
s=bpy.context.scene;u=s.objects['US_FRAME'].matrix_world.copy();cfg=json.loads((R/'scripts/dense_layout.json').read_text())
points=[(f'GRID_{x}_{y}',x,y) for x in range(0,31,5) for y in range(60,81,5)]
points += [(b['name'],*b['xy']) for b in cfg['buildings'] if b['name'].startswith('CE_REAR_BLOCK') or b['name']=='CE_REAR_ONE_WTC']
out={}
for f in [300,315]:
 s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();eye=s.camera.evaluated_get(dg).matrix_world.translation;rows=[]
 for name,x,y in points:
  for h in [30,35,40,45,50,55,60]:
   samples=[]
   for k in [.8,1]:
    p=u@surface(x,y,.96+h*k);ndc=world_to_camera_view(s,s.camera,p);d=p-eye
    hit,loc,n,index,obj,m=s.ray_cast(dg,eye,d.normalized(),distance=max(0,d.length-.15))
    own=hit and obj.name.startswith(name)
    samples.append({'ndc':list(ndc),'visible':not hit or own,'blocker':obj.name if hit and not own else None})
   if samples[-1]['visible'] and .05<samples[-1]['ndc'][0]<.95 and .5<samples[-1]['ndc'][1]<1.08:
    rows.append({'name':name,'xy':[x,y],'height':h,'samples':samples})
 out[f]=rows;print('DONE',f,len(rows),flush=True)
(R/'review/skyline-probe.json').write_text(json.dumps(out,indent=2))
