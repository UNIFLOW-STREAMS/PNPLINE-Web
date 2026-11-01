import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;s.frame_set(0);I=s.objects['SF_CN_LAYOUT'].matrix_world.inverted()
rows={};bvhs={}
for name in ['SF_BASIN_WATER_SURFACE','SF_ISLAND_TOP']:
 o=s.objects[name];T=I@o.matrix_world;v=[T@x.co for x in o.data.vertices];f=[list(p.vertices)for p in o.data.polygons]
 bvhs[name]=BVHTree.FromPolygons(v,f)
 rows[name]={'vertices':len(v),'faces':len(f),'face_sizes':[len(x)for x in f],
             'bounds':[[min(p[a]for p in v)for a in range(3)],[max(p[a]for p in v)for a in range(3)]]}
samples=[]
for x,y in [(-3,23),(-8,22),(3,23),(-3,26),(-3,19)]:
 result={'xy':[x,y]}
 for name,bvh in bvhs.items():
  hit=bvh.ray_cast(Vector((x,y,50)),Vector((0,0,-1)))[0];result[name]=list(hit)if hit else None
 samples.append(result)
print('BASIN_TOPOLOGY',json.dumps({'meshes':rows,'island_overlap_samples':samples}),flush=True)
