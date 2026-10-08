"""Surface sample visibility supplements actual image inspection; never pixel coverage."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];S=bpy.context.scene;C=S.camera;rows=[]
names=['SHIP_HULL','SHIP_DECK','SHIP_BRIDGE','US_QUAY','US_LAND_TERRACE']+[o.name for o in S.objects if o.name.startswith(('P02_BOOM','P02_LEG'))]
for f in sorted(set([216,278,330,422,450]+list(range(366,391)))):
 S.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();origin=C.matrix_world.translation;objects={}
 for name in names:
  o=bpy.data.objects[name];visible=[]
  for face in o.data.polygons:
   # Face center plus inward vertex samples, not only bounding boxes.
   points=[face.center]+[face.center.lerp(o.data.vertices[i].co,.75) for i in face.vertices]
   for point in points:
    p=o.matrix_world@point;uv=world_to_camera_view(S,C,p)
    if not(uv.z>0 and 0<uv.x<1 and 0<uv.y<1):continue
    ray=p-origin;hit,loc,n,idx,obj,mat=S.ray_cast(dg,origin,ray.normalized(),distance=ray.length+.1)
    if hit and obj.name==name and (loc-p).length<.12:visible.append({'uv':[uv.x,uv.y],'face':face.index,'local_normal':list(face.normal)})
  objects[name]={'visible_surface_samples':visible}
 rows.append({'frame':f,'objects':objects})
(R/'review/visibility.json').write_text(json.dumps({'method':'Ray casts to polygon center and inset vertices; finite samples, not pixel area or exhaustive occlusion proof. Inspect rendered sequences too.','frames':rows},indent=2))
for r in rows:
 print(r['frame'],{n:len(v['visible_surface_samples']) for n,v in r['objects'].items()})
