import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
cfg=json.loads((R/'config.json').read_text());m=TimeMap(1392,cfg['easing']);path=R/'master-motion-polish-A.blend'
bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;t=m.forward(776.5);s.frame_set(int(t),subframe=t%1);I=s.objects['US_FRAME'].matrix_world.inverted()
trees=[]
for n in ['US_QUAY','US_LAND_TERRACE','E09_MANEUVER_YARD','MP_CONTINUOUS_ROAD']:
 o=s.objects[n];trees.append(BVHTree.FromPolygons([I@o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]))
gaps=[]
for o in [o for o in s.objects if o.name.startswith('A03') and '_WHEEL_' in o.name]:
 wm=I@o.matrix_world;gap=100
 for v in o.data.vertices:
  p=wm@v.co;hits=[tree.ray_cast(p+Vector((0,0,5)),Vector((0,0,-1)),20)[0] for tree in trees];gap=min(gap,p.z-max(h.z for h in hits if h is not None))
 gaps.append([o.name,gap])
result={'blend_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_frame':776.5,'gaps':gaps,'pass':all(abs(g)<.002 for _,g in gaps)}
print(json.dumps(result),flush=True)
assert result['pass'],result
