"""Finite weighted surface rays. Visibility aids require rendered-image review."""
import bpy,math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from scene_evidence import bounds
S=bpy.context.scene
def surface(names):
 C=S.camera;origin=C.matrix_world.translation;dg=bpy.context.evaluated_depsgraph_get()
 total=inside=visible=crane=0.;blockers={}
 for name in names:
  o=bpy.data.objects[name]
  if o.type!='MESH':continue
  m=o.matrix_world;normalmat=m.to_3x3().inverted().transposed()
  for face in o.data.polygons:
   if len(face.vertices)!=4:continue
   vs=[m@o.data.vertices[i].co for i in face.vertices];center=sum(vs,Vector())/4
   n=(normalmat@face.normal).normalized();cos=n.dot((origin-center).normalized())
   if cos<=0:continue
   area=(vs[1]-vs[0]).cross(vs[3]-vs[0]).length
   weight=area*cos/max((origin-center).length_squared,1)/25
   for a in [.1,.3,.5,.7,.9]:
    for b in [.1,.3,.5,.7,.9]:
     p=vs[0].lerp(vs[1],a).lerp(vs[3].lerp(vs[2],a),b);total+=weight
     uv=world_to_camera_view(S,C,p)
     if not(uv.z>0 and .01<uv.x<.99 and .01<uv.y<.99):continue
     inside+=weight;ray=p-origin
     hit,loc,_,_,obj,_=S.ray_cast(dg,origin,ray.normalized(),distance=ray.length+.04)
     # A ray to an inner wall which first hits the same assembly's exterior
     # still sees that assembly; self-occlusion is not an external obstruction.
     if hit and obj.name in names:visible+=weight
     elif hit:
      blockers[obj.name]=blockers.get(obj.name,0)+weight
      if obj.name.startswith(('P02_LEG','P02_BOOM')):crane+=weight
 return {'visible_fraction':visible/max(total,1e-10),'inframe_fraction':inside/max(total,1e-10),'crane_fraction':crane/max(total,1e-10),'blockers':{n:w/max(total,1e-10) for n,w in blockers.items()}}
def point(local):
 U=bpy.data.objects['US_FRAME'].matrix_world;uv=world_to_camera_view(S,S.camera,U@Vector(local));return list(uv)
def sample(f):
 S.frame_set(int(f),subframe=f-int(f))
 cargo=[o.name for o in bpy.data.objects['A01_CONTAINER'].children_recursive if o.type=='MESH']
 return {'frame':f,'bounds':{n:bounds(n) for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','E08_WAREHOUSE','E07_INBOUND_ROAD']},'cab':surface(['TRACTOR_CAB']),'cargo':surface(cargo),'spreader':surface(['P02_SPREADER_FRAME']),'road_points':[point(p) for p in [(18,9,.75),(22,9,.75),(26,9,.75),(30,14,.75)]],'warehouse':surface(['WAREHOUSE_BACK_WALL']) if bpy.data.objects.get('WAREHOUSE_BACK_WALL') else None}
