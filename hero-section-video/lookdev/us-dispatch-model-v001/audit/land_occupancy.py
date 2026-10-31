import bpy,json,math
from pathlib import Path
from mathutils import Vector
s=bpy.context.scene;U=s.objects['US_FRAME'].matrix_world;I=U.inverted();out=[]
def inverse(p):
 q=Vector(p)-Vector((0,0,-140));rho=math.hypot(q.x,q.y);a=math.atan2(rho,q.z);return [q.x/rho*a*140,q.y/rho*a*140] if rho else [0,0]
for o in s.objects:
 if 'cv_anchor' in o:
  a=list(o['cv_anchor'])
  if a[0]>64 and a[1]<65:out.append({'name':o.name,'anchor':a,'children':[x.name for x in o.children][:6]})
land=s.objects['US_LAND_TERRACE'];pts=[I@land.matrix_world@v.co for v in land.data.vertices]
inv=[inverse(p) for p in pts]
res={'anchors':out,'land_xy_extent':[[min(p[i] for p in inv)for i in range(2)],[max(p[i]for p in inv)for i in range(2)]], 'land_points':inv}
Path(__file__).with_suffix('.json').write_text(json.dumps(res,indent=2));print('ANCHORS',json.dumps(out));print('EXTENT',res['land_xy_extent'])
