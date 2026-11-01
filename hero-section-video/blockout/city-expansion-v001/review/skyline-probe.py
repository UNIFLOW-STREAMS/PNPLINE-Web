"""Read-only projection and occlusion probe for additional NY silhouettes."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
sys.path.insert(0,str(R/'scripts'))
from mapping import surface,normal
from verify_geometry import inside
s=bpy.context.scene;U=s.objects['US_FRAME'];um=U.matrix_world.copy();ui=um.inverted()
config=json.loads((R/'scripts/dense_layout.json').read_text())
main=[(-35.896,18.6),(-23,5),(111,5),(111,56),(-9.438,75.735),(-23,56),(-35.896,29.4)]
polys=[main,config['terrain_polygons']['left']]
def ground(x,y):return any(inside((x,y),p) for p in polys)
def project(p):return list(world_to_camera_view(s,s.camera,p))
report={'source':bpy.data.filepath,'coordinate_space':'US authored arc XY; heights radial above ground','frames':{}}
if '--specific' in sys.argv:
 report=json.loads((R/'review/skyline-probe.json').read_text());report['specific_targets']={}
 for f in [300,315,330,349]:
  s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();cam=s.camera.evaluated_get(dg);eye=cam.matrix_world.translation;rows=[]
  for name,x,y,h,w in [('SpaceNeedle',-13,67,36,6),('OneWTC',35,44,38,7),('Rockefeller',50,44,32,7)]:
   q=Vector((0,0,1)).rotation_difference(normal(x,y));samples=[]
   for label,dx,z in [('lower',0,h*.35),('mid',0,h*.65),('top',0,h),('top_left',-w/2,h),('top_right',w/2,h)]:
    p=um@(surface(x,y,.96)+q@Vector((dx,0,z)));v=p-eye;hit,loc,n,index,obj,m=s.ray_cast(dg,eye,v.normalized(),distance=max(0,v.length-.12))
    samples.append({'label':label,'ndc':project(p),'visible':not hit,'blocker':obj.name if hit else None})
   rows.append({'name':name,'xy':[x,y],'height':h,'samples':samples})
  report['specific_targets'][f]=rows;print('SPECIFIC',f,json.dumps(rows),flush=True)
 (R/'review/skyline-probe.json').write_text(json.dumps(report,indent=2));sys.exit(0)
for f in [300,315,330,349]:
 s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();cam=s.camera.evaluated_get(dg);eye=cam.matrix_world.translation
 s.camera=cam.original
 def probe(p):
  v=p-eye;hit,loc,n,index,obj,m=s.ray_cast(dg,eye,v.normalized(),distance=max(0,v.length-.12))
  ndc=project(p);return {'ndc':ndc,'visible':not hit,'blocker':obj.name if hit else None}
 letters={}
 for ch in 'USA':
  o=s.objects['UC_LETTER_'+ch];ps=[project(o.matrix_world@Vector(v)) for v in o.bound_box]
  letters[ch]={'min':[min(p[k] for p in ps) for k in range(2)],'max':[max(p[k] for p in ps) for k in range(2)]}
 rows=[]
 for x in range(-40,81,5):
  for y in range(44,95,5):
   if not ground(x,y) or not ground(x-2,y-2) or not ground(x+2,y+2):continue
   if x<28 and y<60 and x>-30:continue
   for h in [12,18,24,30,36]:
    samples=[probe(um@surface(x,y,.96+h*t)) for t in [.35,.65,1]]
    top=samples[-1]['ndc'];valid=0<top[0]<1 and 0<top[1]<1 and top[2]>0
    if valid and any(q['visible'] for q in samples):rows.append({'xy':[x,y],'height':h,'samples':samples,'visible_count':sum(q['visible'] for q in samples)})
 report['frames'][f]={'camera_us':list((ui@cam.matrix_world).translation),'letters_ndc':letters,'candidates':rows}
 print('FRAME',f,'viable',len(rows),'letters',letters)
(R/'review/skyline-probe.json').write_text(json.dumps(report,indent=2))
print('SKYLINE_PROBE_DONE')
