import bpy,json,math
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;s.frame_set(1075);root=Path(bpy.data.filepath).parent
m=json.loads((root/'review/candidate-curvature-v003-build.json').read_text())
rows=[]
for g in m['groups']:
 vals=[]
 for n in g['members']:
  o=s.objects[n]
  if o.type=='MESH' and not o.hide_render:
   rr=[(o.matrix_world@v.co).length for v in o.data.vertices]
   if rr:vals.append((min(rr),max(rr),n))
 if vals:rows.append((g['name'],sorted(vals)[:3]))
print('GROUP_MIN_RADII',json.dumps(rows))
print('FOUNDATION_INVERSION',[(o.name,min((o.matrix_world@v.co).length for v in o.data.vertices)) for o in s.objects if o.name.startswith('CV_FOUNDATION') and min((o.matrix_world@v.co).length for v in o.data.vertices)<140.64])
for n in ['UC_LIBERTY_ISLAND_CAP','UC_BRIDGE_PIER','UC_BRIDGE_PIER.001']:
 o=s.objects.get(n)
 if o:print('SPECIAL',n,o.parent.name,[(o.matrix_world@v.co).length for v in o.data.vertices][:16])
prev=None;vel=[]
for f in range(380,1393):
 s.frame_set(f);o=s.objects['CAM_MASTER'];p=o.matrix_world.translation.copy();q=o.matrix_world.to_quaternion()
 if prev:vel.append((f,(p-prev[0]).length,math.degrees(q.rotation_difference(prev[1]).angle)))
 prev=(p,q)
print('CAMERA_MAX_SPEED',sorted(vel,key=lambda v:v[1],reverse=True)[:12]);print('CAMERA_MAX_ANGLE',sorted(vel,key=lambda v:v[2],reverse=True)[:12])
