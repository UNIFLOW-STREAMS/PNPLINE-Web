import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
def tree(o):
 T=I@o.matrix_world;return BVHTree.FromPolygons([T@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
containers=[o for o in s.objects if o.get('pt_role')=='container']
newcranes=[o for o in s.objects if o.get('pt_role') in ['crane','quay_fixture']]
original=[o for o in s.objects if o.type=='MESH' and o.name.startswith(('UC_CONTAINER','US_YARD_STACK','UC_RAIL','UC_STATIC_CRANE'))]
for o in s.objects:
 if o.type=='MESH' and o.name.startswith(('UC_','CE_')) and 'BUILDING' in o.name:original.append(o)
trees={o.name:tree(o) for o in containers+newcranes+original};errors=[]
for o in containers:
 for other in newcranes+original:
  hits=trees[o.name].overlap(trees[other.name])
  if hits:errors.append([o.name,other.name,len(hits)])
for i,o in enumerate(containers):
 for other in containers[i+1:]:
  # The material submeshes of one container intentionally share corner castings/rails.
  if o.name.rsplit('_',1)[0]==other.name.rsplit('_',1)[0]:continue
  hits=trees[o.name].overlap(trees[other.name])
  if hits:errors.append([o.name,other.name,len(hits)])
report={'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'passed':not errors,'container_meshes':len(containers),'other_meshes':len(newcranes+original),'intersections':errors}
(R/'review/static-clearance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['passed']
