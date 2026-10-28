import bpy,sys,json,math,hashlib,ast
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1];s=bpy.context.scene;s.frame_set(156)
cfg=json.loads((R/'route-config.json').read_text());regional=cfg['regional_roots']
def below(o,names):
 while o:
  if o.name in names:return True
  o=o.parent
 return False
vs=[];fs=[];owners=[]
for o in s.objects:
 if o.type!='MESH'or o.hide_render or not below(o,{'CN_FRAME','US_FRAME'}):continue
 offset=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(offset+i for i in p.vertices)for p in o.data.polygons);owners.extend([o.name]*len(o.data.polygons))
env=BVHTree.FromPolygons(vs,fs)
ship=s.objects['A02_SHIP'];hull=s.objects['SF_HULL_BLUE'];hm=ship.matrix_world.inverted()@hull.matrix_world;hv=[hm@v.co for v in hull.data.vertices];hf=[tuple(p.vertices)for p in hull.data.polygons]
visible_points=[Vector((x,y,z))for x in [-5,0,5]for y,z in [(-1.5,2),(0,4),(1.5,2)]]
rows=[];usrows=[];carrier=[];samples=list(range(1393))+[f+t for f in [143,144,145,169,170,171,339,340,455,456,457,509,510,511,647,648,671,672]for t in [.25,.5,.75]]
source_name=bpy.data.filepath
for f in sorted(samples):
 s.frame_set(int(f),subframe=f%1);sm=ship.matrix_world;cm=s.camera.matrix_world;um=s.objects['US_FRAME'].matrix_world;ui=um.inverted();cargo=s.objects['A01_CONTAINER'].matrix_world
 usrows.append([f,*[v for n in regional for row in (ui@s.objects[n].matrix_world)for v in row]])
 if 72<=f<=510:carrier.append([f,*[v for row in(sm.inverted()@cargo)for v in row]])
 if f<96 or f>672:continue
 p=cm.translation;near=env.find_nearest(p);blocked=[];uv=[]
 for test in visible_points:
  wp=sm@test;delta=wp-p;hit=env.ray_cast(p,delta.normalized(),delta.length-.05)
  blocked.append(owners[hit[2]]if hit[0] is not None else None);q=world_to_camera_view(s,s.camera,wp);uv.append([q.x,q.y,q.z])
 ht=BVHTree.FromPolygons([sm@v for v in hv],hf);coll=sorted(set(owners[b]for a,b in ht.overlap(env)))if 144<=f<=510 else []
 rows.append({'frame':f,'camera':list(p),'q':list(cm.to_quaternion()),'ship':list(sm.translation),'ship_q':list(sm.to_quaternion()),'camera_ship_local':list(sm.inverted()@p),'occluders':blocked,'uv':uv,'nearest_environment_distance':near[3]if near[0]is not None else None,'nearest_object':owners[near[2]]if near[0]is not None else None,'camera_radial_height':p.length-140,'hull_environment_collisions':coll,'lens':s.camera.data.lens})
np.savez_compressed(R/'review'/f'{label}-local-samples.npz',us=np.asarray(usrows),cargo=np.asarray(carrier))
(R/'review'/f'{label}-metrics-raw.json').write_text(json.dumps({'file':source_name,'sha256':hashlib.sha256(Path(source_name).read_bytes()).hexdigest(),'rows':rows,'sample_scope':'Every integer frame 0..1392 plus quarter-frame boundary samples. Environment BVH uses actual rendered CN/US static meshes at f156, excludes ocean and moving independent vehicles. Nine representative ship points for occlusion, not pixel-exact visibility. Visible blue hull triangle overlap.','US_root_names':regional},indent=2))
print('ASSESS_COMPLETE',label,len(rows))
