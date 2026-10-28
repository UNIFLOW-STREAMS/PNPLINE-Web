import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;s.frame_set(156);di=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();o=s.objects['EARTH_CONTINUOUS_OCEAN'];dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);m=e.to_mesh();ps=[di@o.matrix_world@v.co for v in m.vertices];bv=BVHTree.FromPolygons(ps,[list(p.vertices)for p in m.polygons]);e.to_mesh_clear()
for x,y in [(-27,10),(-35,10),(12,10),(20,10),(0,0)]:
 hit=bv.ray_cast(Vector((x,y,80)),Vector((0,0,-1)))[0];print(x,y,'actual',list(hit)if hit else None,'analytic',math.sqrt(140**2-x*x-y*y)-140)
