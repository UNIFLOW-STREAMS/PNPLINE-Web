import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'curvature-rework-v001/scripts'))
from mapping import surface,normal,CENTER
s=bpy.context.scene;s.frame_set(349);U=s.objects['US_FRAME'];I=U.matrix_world.inverted();deps=bpy.context.evaluated_depsgraph_get()
def mesh(o):
 ev=o.evaluated_get(deps);me=ev.to_mesh();T=I@ev.matrix_world;v=[T@p.co for p in me.vertices];f=[tuple(p.vertices)for p in me.polygons];ev.to_mesh_clear();return v,f
def design(x,y):return(.8480480909*x+.5299192667*y-19.6070099,-.5299192667*x+.8480480909*y+6.6222191)
def F(x,y,z):return Matrix.Translation(surface(x,y,z))@Vector((0,0,1)).rotation_difference(normal(x,y)).to_matrix().to_4x4()
def us(o):
 while o:
  if o.name=='US_FRAME':return True
  o=o.parent
 return False
def bounds(v):return([min(p[i]for p in v)for i in range(3)],[max(p[i]for p in v)for i in range(3)])
def overlaps(a,b):return all(a[0][i]<=b[1][i]and b[0][i]<=a[1][i]for i in range(3))
root=s.objects['CE_REAR_SPACE_NEEDLE_ROOT'];old=list(root['ce_anchor']);members={o.name for o in root.children_recursive if o.type=='MESH'and not o.hide_render}|{'UST_NEEDLE_CITY_PAD'}
vv=[];ff=[]
for n in members:
 v,f=mesh(s.objects[n]);k=len(vv);vv+=v;ff.extend(tuple(i+k for i in p)for p in f)
bb=bounds(vv);corners=[Vector((x,y,z))for x in [bb[0][0],bb[1][0]]for y in [bb[0][1],bb[1][1]]for z in [bb[0][2],bb[1][2]]]
obstacles=[];cache={};ground=[]
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}or o.hide_render or not us(o)or o.name in members:continue
 if o.name in {'US_LAND_TERRACE','CE_NY_CURVED_LAND'}:
  v,f=mesh(o);ground.append(BVHTree.FromPolygons(v,f));continue
 obstacles.append((o.name,bounds([I@o.matrix_world@Vector(p)for p in o.bound_box])))
positions=sorted([(x,y)for x in range(-38,21)for y in range(44,77)],key=lambda p:math.dist(p,(-24,52)))
for idx,p in enumerate(positions):
 x,y=design(*p);D=F(x,y,old[2])@F(*old).inverted();newbb=bounds([D@v for v in corners]);near=[n for n,b in obstacles if overlaps(b,newbb)]
 n=normal(x,y);hit=[g.ray_cast(surface(x,y,70),-n,90)[0]for g in ground];hs=[(v-CENTER).length-140 for v in hit if v is not None]
 if not hs or abs(max(hs)-.68)>.04:continue
 tv=[D@v for v in vv];tree=BVHTree.FromPolygons(tv,ff);clear=True
 for name in near:
  if name not in cache:
   v,f=mesh(s.objects[name]);cache[name]=BVHTree.FromPolygons(v,f)
  if tree.overlap(cache[name]):clear=False;break
 if clear:
  (R/'scripts/needle-location.json').write_text(json.dumps({'design_xy':p,'tested_candidates':idx+1}));print('NEEDLE_PLACEMENT',p,'tested',idx+1,flush=True);break
 if idx%100==0:print('SEARCH',idx,flush=True)
else:raise RuntimeError('No supported collision-free city placement')
