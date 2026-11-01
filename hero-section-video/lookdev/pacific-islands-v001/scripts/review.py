import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
r=Path(__file__).resolve().parents[1];s=bpy.context.scene;ship=s.objects['A02_SHIP'];cam=s.camera
def matrix(m):return [list(v) for v in m]
baseline='baseline' in sys.argv
samples={}
res=r/'review';terrains=[]
if not baseline:
 assert s.objects.get('SHIP_ROUTE') is None
 for o in s.objects:
  if o.name.startswith('Pacific |') and 'shoreline' in o.name:
   verts=[v.co.copy() for v in o.data.vertices];faces=[tuple(p.vertices) for p in o.data.polygons]
   terrains.append(BVHTree.FromPolygons(verts,faces))
minimum=999
for frame in range(150,318):
 s.frame_set(frame);samples[frame]=[matrix(ship.matrix_world),matrix(cam.matrix_world),cam.data.lens]
 for bvh in terrains:
  # All terrain is outside a bounding sphere enclosing the entire hull.
  q,_,_,d=bvh.find_nearest(ship.matrix_world.translation)
  minimum=min(minimum,d)
h=hashlib.sha256(json.dumps(samples).encode()).hexdigest()
if baseline:
 (res/'motion.sha').write_text(h)
else:
 assert h==(res/'motion.sha').read_text()
 hull=next(o for o in ship.children_recursive if o.name.startswith('VSL_Shell'))
 limit=max((ship.matrix_world.inverted()@hull.matrix_world@Vector(v)).length for v in hull.bound_box)
 assert minimum>limit,(minimum,limit)
 (res/'checks.json').write_text(json.dumps(dict(frames=[150,317],ship_and_master_camera_matrices_identical=True,minimum_center_to_land=minimum,hull_bounding_radius=limit,minimum_clearance_lower_bound=minimum-limit,terrain_count=len(terrains)),indent=2))
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 s.render.engine='CYCLES';s.cycles.device='GPU' if any(d.use for d in pref.devices) else 'CPU'
 s.cycles.samples=20;s.cycles.use_denoising=True;s.render.resolution_x=1088;s.render.resolution_y=612;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 for frame in [201,225,245]:
  s.frame_set(frame);s.render.filepath=str(res/f'crossing-{frame}.png');bpy.ops.render.render(write_still=True)
