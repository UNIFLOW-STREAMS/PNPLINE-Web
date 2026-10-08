"""Fresh-process saved-state metrics. OBB collision approximation, not continuous physics."""
import bpy,sys,json,math,argparse,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--config',required=True);p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(Path(a.config).read_text(encoding='utf-8-sig'));s=bpy.data.scenes[a.scene];bpy.context.window.scene=s;U=bpy.data.objects['US_FRAME'].matrix_world.copy();I=U.inverted();C=s.camera;T=bpy.data.objects['CAM_LOOK_TARGET'];out=Path(a.output)
def descendants(name):
 o=bpy.data.objects[name];return [x for x in [o,*o.children_recursive] if x.type=='MESH' and not x.hide_render]
vehicle=list({o.name:o for name in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET'] for o in descendants(name)}.values());ground_names={'US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD','US_WATER','OCEAN_DISC','WORLD_GROUND','EARTH_CONTINUOUS_OCEAN'}
ground=[]
for name in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 o=bpy.data.objects[name];ground.append((name,BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])))
def box(o):
 pts=[I@o.matrix_world@Vector(v) for v in o.bound_box];axes=[(I.to_3x3()@o.matrix_world.to_3x3().col[i]).normalized() for i in range(3)];return pts,axes
def overlaps(A,B):
 ap,aa=A;bp,ba=B
 for i in range(3):
  if min(max(v[i] for v in ap),max(v[i] for v in bp))-max(min(v[i] for v in ap),min(v[i] for v in bp))<=.001:return False
 for axis in aa+ba+[x.cross(y) for x in aa for y in ba]:
  if axis.length_squared<1e-10:continue
  axis=axis.normalized();av=[v.dot(axis) for v in ap];bv=[v.dot(axis) for v in bp]
  if min(max(av),max(bv))-max(min(av),min(bv))<=.001:return False
 return True
def state(o):
 m=o.matrix_world;lm=I@m;return dict(world_position=list(m.translation),world_quaternion=list(m.to_quaternion()),local_position=list(lm.translation),local_quaternion=list(lm.to_quaternion()),world_matrix=[list(r) for r in m])
rows=[];collisions=[];cam_collisions=[];visibility={};boundary_state={};previous=None;max_speed=0;max_angle=0;max_lens=0;max_hitch=0;max_relative=0;max_gap=0;baseline_relative=None
obstacles=[o for o in s.objects if o.type=='MESH' and not o.hide_render and o not in vehicle and o.name not in ground_names]
def visible_samples(objects):
 dg=bpy.context.evaluated_depsgraph_get();group={o.name for o in objects};total=inside=visible=0
 for o in objects:
  if o.type!='MESH':continue
  for poly in o.data.polygons:
   verts=[o.matrix_world@o.data.vertices[v].co for v in poly.vertices];center=sum(verts,Vector())/len(verts)
   normal=(o.matrix_world.to_3x3()@poly.normal).normalized()
   if o.name!='E07_INBOUND_ROAD' and normal.dot(C.matrix_world.translation-center)<=0:continue
   for v in verts:
    pt=center.lerp(v,.65);total+=1;screen=world_to_camera_view(s,C,pt)
    if not(0<=screen.x<=1 and 0<=screen.y<=1 and screen.z>0):continue
    inside+=1;ray=pt-C.matrix_world.translation;hit,loc,n,index,obj,m=s.ray_cast(dg,C.matrix_world.translation,ray.normalized(),distance=ray.length+.01)
    if hit and obj and obj.name in group:visible+=1
 return dict(samples=total,in_frame=inside,visible=visible,fraction=visible/max(total,1))
for j in range(cfg['preview_start']*4,cfg['preview_end']*4+1):
 f=j/4;s.frame_set(math.floor(f),subframe=f%1);row=dict(frame=f,camera=state(C),target=state(T),lens=C.data.lens,vehicle=state(bpy.data.objects['A03_TRAILER']))
 if previous:
  dp=(Vector(row['camera']['world_position'])-Vector(previous['camera']['world_position'])).length*4;from mathutils import Quaternion
  qa=Quaternion(row['camera']['world_quaternion']).normalized();qb=Quaternion(previous['camera']['world_quaternion']).normalized();ang=math.degrees(2*math.acos(min(1,abs(qa.dot(qb)))))*4
  row['speed_m_frame']=dp;row['angle_deg_frame']=ang;max_speed=max(max_speed,dp);max_angle=max(max_angle,ang);max_lens=max(max_lens,abs(row['lens']-previous['lens'])*4)
 previous=row
 hitch=(bpy.data.objects['TRACTOR_HITCH'].matrix_world.translation-bpy.data.objects['TRAILER_HITCH'].matrix_world.translation).length;max_hitch=max(max_hitch,hitch)
 rel=bpy.data.objects['A03_TRAILER'].matrix_world.inverted()@bpy.data.objects['A01_CONTAINER'].matrix_world
 if f==632:baseline_relative=rel.copy()
 if f>=632 and baseline_relative:max_relative=max(max_relative,max(abs(rel[r][c]-baseline_relative[r][c]) for r in range(4) for c in range(4)))
 support=[]
 for o in vehicle:
  if '_WHEEL_' not in o.name:continue
  center=(I@o.matrix_world).translation;bottom=min((I@o.matrix_world@v.co).z for v in o.data.vertices);hits=[(name,tr.ray_cast(center+Vector((0,0,3)),Vector((0,0,-1)),10)[0]) for name,tr in ground];hits=[(n,v.z) for n,v in hits if v is not None];name,z=max(hits,key=lambda q:q[1]);gap=bottom-z;max_gap=max(max_gap,abs(gap));support.append(dict(name=o.name,gap=gap,ground=name))
 row['support']=support;row['hitch_gap']=hitch
 # Nearby broad-phase avoids China/remote warehouse work; SAT tests complete moving assembly.
 vp=[(o,box(o)) for o in vehicle];cp=(I@C.matrix_world).translation
 nearby=[]
 for ob in obstacles+vehicle:
  B=box(ob);lo=Vector([min(v[i] for v in B[0]) for i in range(3)]);hi=Vector([max(v[i] for v in B[0]) for i in range(3)])
  if all(lo[i]-.1<cp[i]<hi[i]+.1 for i in range(3)):
   lp=ob.matrix_world.inverted()@C.matrix_world.translation;bl=Vector([min(v[i] for v in ob.bound_box) for i in range(3)]);bh=Vector([max(v[i] for v in ob.bound_box) for i in range(3)])
   closest=Vector([max(bl[i],min(bh[i],lp[i])) for i in range(3)])
   if (ob.matrix_world@closest-C.matrix_world.translation).length<.1:cam_collisions.append([f,ob.name])
  if f>=648 and ob not in vehicle:
   for vo,A in vp:
    if overlaps(A,B):collisions.append([f,vo.name,ob.name])
 if f in [648,660,672,696,720]:
  visibility[str(int(f))]={name:visible_samples(descendants(name)) for name in ['E08_WAREHOUSE','A03_TRACTOR','A01_CONTAINER','A02_SHIP','E07_INBOUND_ROAD']}
 if f in [648,672,720]:
  cargo=bpy.data.objects['A01_CONTAINER'];spr=bpy.data.objects['P02_SPREADER_FRAME'];cb=[I@o.matrix_world@Vector(v) for o in descendants('A01_CONTAINER') for v in o.bound_box]
  sprlow=min((I@spr.matrix_world@Vector(v)).z for v in spr.bound_box)
  boundary_state[str(int(f))]=dict(**row,container=state(cargo),container_relative=[list(r) for r in rel],doors={name:state(bpy.data.objects[name]) for name in ['A01_DOOR_L','A01_DOOR_R']},hoist=state(spr),hoist_bottom=sprlow,container_top=max(v.z for v in cb),ship=state(bpy.data.objects['A02_SHIP']))
 rows.append(row)
metrics=dict(camera_speed_max=max_speed,camera_angle_max=max_angle,lens_rate_max=max_lens,hitch_gap_max=max_hitch,container_relative_drift_max=max_relative,wheel_ground_abs_gap_max=max_gap,vehicle_obstacle_overlap_count=len(collisions),camera_inside_obstacle_count=len(cam_collisions))
data=dict(file=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),scene=s.name,fps=s.render.fps,version=bpy.app.version_string,build=bpy.app.build_hash.decode(),sampling='Every quarter frame; OBB SAT 1mm penetration threshold. Ground separately ray sampled below all 8 wheel centers. Camera 0.1m sphere against local mesh boxes, including vehicle. Hollow EARTH_CONTINUOUS_OCEAN excluded from solid OBB obstacles. Road normals are two-sided for visibility. Not a continuous collision guarantee.',metrics=metrics,collisions=collisions,camera_collisions=cam_collisions,visibility=visibility,states=boundary_state,rows=rows)
out.write_text(json.dumps(data),encoding='utf8');print(json.dumps(metrics,indent=2));print('COLLISION_EXAMPLES',collisions[:12],cam_collisions[:12]);print('VISIBILITY',json.dumps(visibility))
