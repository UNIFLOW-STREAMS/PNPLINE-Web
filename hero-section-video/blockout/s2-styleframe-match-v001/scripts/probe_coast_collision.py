import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene;o=s.objects['SF_COAST_FOLDED_FACE'];n=512;ps=[v.co.copy()for v in o.data.vertices];fs=[list(p.vertices)for p in o.data.polygons];bv=BVHTree.FromPolygons(ps,fs)
for f in [221,235,250,262]:
 s.frame_set(f);di=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();o=s.objects['SF_HULL_BLUE'];hp=[di@o.matrix_world@v.co for v in o.data.vertices];hb=BVHTree.FromPolygons(hp,[list(p.vertices)for p in o.data.polygons]);hits=bv.overlap(hb);idx=sorted(set(v%n for a,b in hits for v in fs[a]));print(f,'bbox',[[min(p[j]for p in hp),max(p[j]for p in hp)]for j in range(3)],'coast',[(i,list(ps[i]))for i in idx[::max(1,len(idx)//5)]])
