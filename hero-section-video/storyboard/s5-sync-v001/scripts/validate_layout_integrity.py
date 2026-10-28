import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];P=R/'layout-proposal-v001';src=R/'master/source-current.blend';dst=P/'s4-s5-layout-proposal-v001.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mesh(o):return hashlib.sha256(str(([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
def describe(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();names=['A03_TRACTOR','A03_TRAILER','A01_CONTAINER','W01_NEW_PALLET','W02_INBOUND_JACK'];rows=[]
 for j in range(552*4,948*4+1):
  f=j/4;s.frame_set(int(f),subframe=f%1);rows.append({n:list((I@s.objects[n].matrix_world).translation) for n in names})
 roots=[s.objects[n] for n in ['A03_TRACTOR','A03_TRAILER','A01_CONTAINER']]
 meshes={o.name:mesh(o) for r in roots for o in r.children_recursive if o.type=='MESH'}
 return rows,meshes
base,mesh0=describe(src);proposal,mesh1=describe(dst)
maxerr=0
for a,b in zip(base,proposal):
 for n in a:
  expected=Vector((a[n][0],18-a[n][1],a[n][2]));maxerr=max(maxerr,(Vector(b[n])-expected).length)
assert mesh0==mesh1,'Approved vehicle/container mesh changed'
assert maxerr<.0002,'Event trajectory/timing changed beyond intended geographic relocation'
s=bpy.context.scene;I=s.objects['US_FRAME'].matrix_world.inverted();sys.path.insert(0,str(R.parents[1]/'blockout/s5-dock-test-v001/scripts'))
from geometry import point_distance
solids=[o for o in s.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('P02_') or o.name in ['SHIP_HULL','TRACTOR_CAB','TRACTOR_CHASSIS','A01_ROOF','A01_SIDE_L','A01_SIDE_R'])]
minimum=1e9;where=None;positions=[];rotations=[]
for j in range(552*4,948*4+1):
 f=j/4;s.frame_set(int(f),subframe=f%1);pos=s.camera.matrix_world.translation.copy();positions.append(pos);rotations.append(s.camera.matrix_world.to_quaternion())
 for o in solids:
  d=point_distance(o,pos)
  if d<minimum:minimum=d;where=(f,o.name)
print('CAMERA_CLEARANCE',minimum,where,flush=True)
assert minimum>.12,'Camera intersects crane/ship/vehicle'
acc=max((positions[i+1]-positions[i]*2+positions[i-1]).length/.25**2 for i in range(1,len(positions)-1));angular=max(2*math.acos(min(1,abs(rotations[i].dot(rotations[i+1])))) for i in range(len(rotations)-1))
assert angular<math.radians(5),'Abrupt camera orientation step'
master=R.parents[1]/'blockout/s5-integration-v001/master-s5-integration-v001.blend'
assert sha(master)==sha(src)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
result={'pass':True,'proposal_sha256':sha(dst),'source_sha256':sha(src),'original_preserved':True,'vehicle_container_meshes_unchanged':len(mesh0),'trajectory_time_samples':len(base),'max_actor_relocation_error_m':maxerr,'camera_min_clearance_crane_ship_vehicle_m':minimum,'camera_clearance_at':where,'max_camera_accel_m_per_frame2':acc,'max_camera_rotation_rad_per_quarter_frame':angular,'scope':'552-948; not a full master continuity claim'}
(P/'integrity.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
