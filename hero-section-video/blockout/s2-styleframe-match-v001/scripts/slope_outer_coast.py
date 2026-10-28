"""Replace vertical lateral shore walls with outward, sea-sealed aprons; preserve the upper rim."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
o=s.objects['SF_COAST_FOLDED_FACE'];n=len(o.data.vertices)//2
assert n==512
rim=[v.co.copy()for v in o.data.vertices[:n]];oldtoe=[v.co.copy()for v in o.data.vertices[n:]]
di=s.objects['SF_CN_LAYOUT'].matrix_world.inverted();sea=s.objects['EARTH_CONTINUOUS_OCEAN'];ev=sea.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
bv=BVHTree.FromPolygons([di@sea.matrix_world@v.co for v in me.vertices],[list(p.vertices)for p in me.polygons]);ev.to_mesh_clear()
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*t*(10+t*(-15+6*t))
width=[];toes=[]
for p,old in zip(rim,oldtoe):
 left=1-smooth(-26,-19,p.x);right=smooth(7.5,11.5,p.x)
 rear=1-smooth(24,31,p.y)
 dx=(8*right*smooth(-3,1,p.y)-5.8*left*smooth(3,7,p.y))*rear
 q=Vector((p.x+dx,p.y,old.z));hit=bv.ray_cast(Vector((q.x,q.y,80)),Vector((0,0,-1)))[0]
 assert hit is not None
 # Unchanged berth remains exactly original. Newly extended toe is submerged 6 cm.
 w=min(1,abs(dx)/.15);q.z=old.z*(1-w)+(hit.z-.06)*w
 width.append(dx);toes.append(q)
verts=[];faces=[];rings=20
for j in range(rings+1):
 t=j/rings
 for p,q,dx in zip(rim,toes,width):
  blend=min(1,abs(dx)/.5)
  depth=t*(1-blend)+t**1.30*blend
  verts.append((p.x+(q.x-p.x)*t,p.y,p.z+(q.z-p.z)*depth))
for j in range(rings):
 for i in range(n):
  k=(i+1)%n;faces.append((j*n+i,j*n+k,(j+1)*n+k,(j+1)*n+i))
m=bpy.data.meshes.new('SF_COAST_SLOPED_v032');m.from_pydata(verts,[],faces);m.update()
for mat in o.data.materials:m.materials.append(mat)
o.data=m
for p in m.polygons:p.use_smooth=True
out=R/'review/layout-proposal-v032.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'review/coast-change-v032.json').write_text(json.dumps({'source':'layout-proposal-v031.blend','object':o.name,'rim_count':n,'rings':rings+1,'left_max_outset_m':-min(width),'right_max_outset_m':max(width),'toe_sea_overlap_m':.06,'upper_land_unchanged':True,'front_berth_unchanged_x_range':[-19,7.5],'width_by_vertex':width},indent=2))


