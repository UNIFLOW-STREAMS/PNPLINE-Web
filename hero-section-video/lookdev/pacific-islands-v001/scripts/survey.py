import bpy, math
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
s=bpy.context.scene; cam=s.camera; sea=s.objects['EARTH_CONTINUOUS_OCEAN'];ship=s.objects['A02_SHIP']
def xyz(v):return tuple(round(a,1) for a in v)
def hit(u,v):
 corners=cam.data.view_frame(scene=s);lo=min(p.x for p in corners);hi=max(p.x for p in corners);bo=min(p.y for p in corners);to=max(p.y for p in corners)
 M=sea.matrix_world.inverted()@cam.matrix_world
 orig=M.translation;direction=M.to_3x3()@Vector((lo+(hi-lo)*u,bo+(to-bo)*v,corners[0].z))
 ok,pos,n,ix=sea.ray_cast(orig,direction.normalized())
 return sea.matrix_world@pos if ok else None
if __name__=='__main__':
 print('SEA',sea.matrix_world,sea.dimensions)
 print('ROUTES',[(o.name,o.type,o.hide_render) for o in s.objects if 'route' in o.name.lower() or 'wake' in o.name.lower()][:100])
 for f in range(155,326,8):
  s.frame_set(f)
  p=hit(.29,.57);q=ship.matrix_world.translation
  print(f,xyz(q),xyz(world_to_camera_view(s,cam,q)),xyz(p) if p else None,round((p-q).length,1) if p else None)
