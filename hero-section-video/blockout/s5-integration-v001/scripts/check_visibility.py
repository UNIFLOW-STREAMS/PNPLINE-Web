import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;rows=[];errors=[]
for f in range(720,949):
 s.frame_set(f);cam=s.camera;dg=bpy.context.evaluated_depsgraph_get();objects=[s.objects[n] for n in ['TRACTOR_CAB','TRAILER_CHASSIS','A01_ROOF']]
 pts=[world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for o in objects for c in o.bound_box]
 if f<900 and (min(p.x for p in pts)<0 or max(p.x for p in pts)>1 or min(p.y for p in pts)<0 or max(p.y for p in pts)>1):errors.append(['truck_crop',f])
 if f>=912:
  cargo=[o for o in s.objects if o.name.startswith('W01_NEW_PALLET_BOX')];visible=0;tested=0;occluders=set()
  for o in cargo:
   for c in list(o.bound_box)+[(0,0,0)]:
    point=o.matrix_world@Vector(c);screen=world_to_camera_view(s,cam,point);v=point-cam.matrix_world.translation
    if not(0<screen.x<1 and 0<screen.y<1 and screen.z>cam.data.clip_start):continue
    tested+=1;hit,loc,norm,index,obj,matrix=s.ray_cast(dg,cam.matrix_world.translation,v.normalized(),distance=v.length+.002)
    if not hit or obj.name.startswith('W01_NEW_PALLET'):visible+=1
    else:occluders.add(obj.name)
  rows.append({'frame':f,'visible_points':visible,'tested':tested,'occluders':sorted(occluders)})
  if visible==0:errors.append(['first_pallet_fully_hidden',f])
result={'pass_all':not errors,'errors':errors,'pallet_visibility':rows,'candidate_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'limitations':'Integer-frame points/rays plus rendered continuous review; not whole-frustum/continuous-time occlusion proof.'};(R/'review/visibility.json').write_text(json.dumps(result,indent=2));print('VISIBILITY',result['pass_all'],errors);assert not errors
