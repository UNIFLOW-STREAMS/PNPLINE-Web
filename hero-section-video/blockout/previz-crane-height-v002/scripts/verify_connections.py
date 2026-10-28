import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;D=s.objects['SF_CN_LAYOUT'].matrix_world.copy();I=D.inverted();errors=[];hits={};min_gap=100
head=[o for o in s.objects['CR_SUSPENSION_HEAD'].children_recursive if o.type=='MESH'and not o.hide_render]
spreader=[o for o in s.objects['P01_SPREADER'].children_recursive if o.type=='MESH'and not o.hide_render]
cables=sorted([o for o in s.objects if o.name.startswith('CR_WORKING_CABLE')],key=lambda o:o.name)
def tree(o):return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons])
for k in range(577):
 t=k/8;s.frame_set(int(t),subframe=t%1);p=I@s.objects['P01_SPREADER'].matrix_world.translation;h=I@s.objects['CR_SUSPENSION_HEAD'].matrix_world.translation
 for i,c in enumerate(cables):
  sx=-1 if i<2 else 1;sy=-1 if i%2==0 else 1
  for z,expected in [(-.5,p+Vector((sx*1.4,sy*.6,.10))),(.5,h+Vector((sx*1.4,sy*.6,-.02)))]:
   actual=I@c.matrix_world@Vector((0,0,z));errors.append((actual-expected).length)
 for ho in head:
  ht=tree(ho)
  for so in spreader:
   if ht.overlap(tree(so)):hits.setdefault(ho.name+' | '+so.name,[]).append(t)
 min_gap=min(min_gap,min((I@o.matrix_world@v.co).z for o in head for v in o.data.vertices)-max((I@o.matrix_world@v.co).z for o in spreader for v in o.data.vertices))
checks={'head_and_spreader_no_crossings':not hits,'all_four_rope_endpoints_connected':max(errors)<.0002,'positive_head_spreader_vertical_clearance':min_gap>.02}
r={'file':bpy.data.filepath,'sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'checks':checks,'max_endpoint_error_m':max(errors),'minimum_vertical_clearance_m':min_gap,'crossings':hits,'samples':577,'step':.125}
(R/'review/connections.json').write_text(json.dumps(r,indent=2));print(r);assert all(checks.values())
