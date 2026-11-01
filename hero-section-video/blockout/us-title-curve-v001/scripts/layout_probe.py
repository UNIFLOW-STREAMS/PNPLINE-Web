import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import convex_hull_2d
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'us-city-density-v001/pnpline-us-city-density-v001.blend'))
s=bpy.context.scene;s.frame_set(349);I=s.objects['US_FRAME'].matrix_world.inverted()
def pxy(p):
 d=p-Vector((0,0,-140));h=math.hypot(d.x,d.y);a=math.atan2(h,d.z)*140
 x,y=(d.x/h*a,d.y/h*a)if h else(0,0)
 return [.8480480909*(x+19.6070099)-.5299192667*(y-6.6222191),.5299192667*(x+19.6070099)+.8480480909*(y-6.6222191),d.length-140]
rows=[]
for root in s.objects:
 if not any(k in root for k in ['cv_anchor','ce_anchor','usd_anchor']):continue
 a=root;isus=False
 while a:
  if a.name=='US_FRAME':isus=True;break
  a=a.parent
 if not isus:continue
 parts=[o for o in [root]+list(root.children_recursive)if o.type=='MESH'and not o.hide_render]
 if not parts:continue
 pts=[pxy(I@o.matrix_world@Vector(c))for o in parts for c in o.bound_box]
 if not pts:continue
 vs=[Vector(p[:2])for p in pts];poly=[list(vs[i])for i in convex_hull_2d(vs)]
 rows.append({'name':root.name,'parts':[o.name for o in parts],'poly':poly,'h':max(p[2]for p in pts),'zmin':min(p[2]for p in pts),'anchor':dict((k,list(root[k]))for k in ['cv_anchor','ce_anchor','usd_anchor']if k in root)})
(R/'review/layout-source.json').write_text(json.dumps(rows,indent=2))
print('LAYOUT',len(rows),flush=True)
