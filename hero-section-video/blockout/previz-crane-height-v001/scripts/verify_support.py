import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(0)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])
def under(o,n):
 while o:
  if o.name==n:return True
  o=o.parent
 return False
def moving(o):
 while o:
  if o.animation_data and o.animation_data.action:return True
  o=o.parent
 return False
changed=json.loads((R/'delivery.json').read_text())['changed_static_geometry']
env=[(o.name,tree(o))for o in s.objects if o.type=='MESH' and not o.hide_render and under(o,'CN_FRAME')and not under(o,'CR_COMPACT_GANTRY')and not moving(o)]
hits={}
for n in changed:
 t=tree(s.objects[n])
 for en,et in env:
  if t.overlap(et):hits[n+' | '+en]=True
I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();land=s.objects['SF_FRONT_LAND'];lt=BVHTree.FromPolygons([I@land.matrix_world@v.co for v in land.data.vertices],[list(p.vertices)for p in land.data.polygons]);feet={}
for o in s.objects:
 if not o.name.startswith('CR_FOOT_'):continue
 pts=[I@o.matrix_world@v.co for v in o.data.vertices];z=min(p.z for p in pts);cs=[]
 for p in pts:
  if p.z>z+.001:continue
  hit=lt.ray_cast(p+Vector((0,0,2)),Vector((0,0,-1)),4)[0];cs.append(None if hit is None else p.z-hit.z)
 feet[o.name]=cs
checks={'raised_supports_clear_static_environment':not hits,'four_feet_remain_supported':len(feet)==4 and all(x is not None and abs(x)<.002 for c in feet.values()for x in c)}
r={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'static_crossings':hits,'feet':feet}
(R/'review/support.json').write_text(json.dumps(r,indent=2));print('SUPPORT',r);assert all(checks.values())
