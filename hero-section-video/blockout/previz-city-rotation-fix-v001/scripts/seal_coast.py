"""After lateral relocation, reseat the sloped coast toe on the curved ocean.
Preserve the top rim, XY contour and every city/crane object transform.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156);o=s.objects['SF_COAST_FOLDED_FACE'];I=o.matrix_world.inverted();sea=s.objects['EARTH_CONTINUOUS_OCEAN'];e=sea.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh()
bv=BVHTree.FromPolygons([I@e.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);e.to_mesh_clear();n=512;assert len(o.data.vertices)==21*n
before=[];delta=[]
for i in range(n):
 p=o.data.vertices[20*n+i].co.copy();hit=bv.ray_cast(Vector((p.x,p.y,80)),Vector((0,0,-1)),160)[0];assert hit is not None
 before.append(p.z-hit.z);delta.append(hit.z-.06-p.z)
for j in range(1,21):
 for i in range(n):o.data.vertices[j*n+i].co.z+=delta[i]*(j/20)**1.3
o.data.update();out=R/'candidate-v004.blend';assert not out.exists();bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'review/coast-seal.json').write_text(json.dumps({'source':'candidate-v003.blend','file':str(out),'before_toe_sea_clearance_minmax':[min(before),max(before)],'correction_minmax':[min(delta),max(delta)],'after_toe_submerged_m':.06,'top_rim_unchanged':True,'XY_contours_unchanged':True},indent=2))
