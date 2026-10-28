import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene;s.frame_set(156);ps=[]
for o in s.objects['SF_CLOUD_RIGHT'].children_recursive:
 if o.type in ['MESH','CURVE']:ps += [world_to_camera_view(s,s.camera,o.matrix_world@Vector(v))for v in o.bound_box]
r={'width':max(p.x for p in ps)-min(p.x for p in ps),'height':max(p.y for p in ps)-min(p.y for p in ps),'source':bpy.data.filepath}
Path(__file__).resolve().parents[1].joinpath('review/cloud-before.json').write_text(json.dumps(r,indent=2));print(r)
