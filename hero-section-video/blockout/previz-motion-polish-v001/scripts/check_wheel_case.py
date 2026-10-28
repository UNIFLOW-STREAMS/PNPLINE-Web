import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;s.frame_set(736);I=s.objects['US_FRAME'].matrix_world.inverted();o=s.objects['A03_TRAILER_WHEEL_0.25-0.85'];c=(I@o.matrix_world).translation
ground=[]
for n in ['US_QUAY','US_LAND_TERRACE','E07_INBOUND_ROAD','E09_MANEUVER_YARD']:
 g=s.objects[n];tree=BVHTree.FromPolygons([I@g.matrix_world@v.co for v in g.data.vertices],[list(p.vertices) for p in g.data.polygons]);hit=tree.ray_cast(c+Vector((0,0,5)),Vector((0,0,-1)),20)[0]
 if hit is not None:ground.append(hit.z)
error=abs(min((I@o.matrix_world@v.co).z for v in o.data.vertices)-max(ground));print('WHEEL_CASE_ERROR',error,flush=True);assert error<.002,'Retimed sampling exposes polygon wheel penetration'
