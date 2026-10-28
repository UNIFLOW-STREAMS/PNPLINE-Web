import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;rows={}
for f in [0,72,156,180,216,240,250,430,450,475,510]:
 s.frame_set(f);h=s.objects['SF_HULL_BLUE'];hb=BVHTree.FromPolygons([h.matrix_world@v.co for v in h.data.vertices],[tuple(p.vertices)for p in h.data.polygons]);items={}
 for n in ['SF_COAST_FOLDED_FACE','US_LAND_TERRACE']:
  o=s.objects[n];ps=[o.matrix_world@v.co for v in o.data.vertices];fs=[tuple(p.vertices)for p in o.data.polygons];tree=BVHTree.FromPolygons(ps,fs);hits=tree.overlap(hb);inds=sorted(set(i for face,_ in hits for i in fs[face]))
  items[n]={'vertex_count':len(ps),'hit_vertices':[(i,list(o.data.vertices[i].co))for i in inds]}
 rows[f]=items
(R/'review/shore-probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
