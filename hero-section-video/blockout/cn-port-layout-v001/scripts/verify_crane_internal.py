"""Independent moving subassemblies: jib members vs trolley/head/spreader.
Rail-wheel rolling contact and attached pin/carriage connections are excluded;
stay, pylon, boom, cabin crossings are not permitted.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;file=Path(bpy.data.filepath)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
jib=[o for o in s.objects['CR_SLEW_JIB'].children_recursive if o.type=='MESH' and not o.hide_render and not o.name.startswith(('CR_ROTATING_BEARING','CR_TROLLEY_RAIL'))]
mobile=[o for root in ['CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD','P01_SPREADER'] for o in s.objects[root].children_recursive if o.type=='MESH' and not o.hide_render];hits={}
for k in range(625):
 t=k/4;s.frame_set(int(t),subframe=t%1);jt=[(o.name,tree(o)) for o in jib]
 for o in mobile:
  mt=tree(o)
  for n,bt in jt:
   if mt.overlap(bt):hits.setdefault(n+' | '+o.name,[]).append(t)
 if k%120==0:print('INTERNAL',t,len(hits),flush=True)
result={'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'frames':[0,156],'step':.25,'samples':625,'unexpected':hits,'pass':not hits}
(R/'review'/f'{file.stem}-internal.json').write_text(json.dumps(result,indent=2));print('INTERNAL_RESULT',not hits);assert not hits
