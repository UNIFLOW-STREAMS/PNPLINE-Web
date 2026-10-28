"""Extend the right water bend and its matching land cutout, static geometry only."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
water=s.objects['SF_BASIN_WATER_SURFACE'];wall=s.objects['SF_BASIN_OUTER_WALL'];land=s.objects['SF_FRONT_LAND']
changes=[]
for i in range(96):
 u=(i-16)/28;shift=3.6*math.sin(math.pi*u)**2 if 0<u<1 else 0
 if not shift:continue
 for obj,indexes in [(water,[i]),(wall,[i,i+96]),(land,[i+96])]:
  for j in indexes:
   obj.data.vertices[j].co.x+=shift
   obj.data.vertices[j].co.y-=shift*(2.5/3.6)
 changes.append([i,shift])
# Retopologize the land rim radially to avoid crossed/coplanar triangles where
# the enlarged opening approaches the old coastline. Preserve the original
# coast silhouette except for the margin needed beside the enlarged water.
coast=s.objects['SF_COAST_FOLDED_FACE'];oldrim=[Vector((v.co.x,v.co.y))for v in list(land.data.vertices)[:96]]
center=Vector((-5,21))
def cross(a,b):return a.x*b.y-a.y*b.x
for i in range(96):
 wp=water.data.vertices[i].co;delta=Vector((wp.x,wp.y))-center;direction=delta.normalized();hits=[]
 for j,a in enumerate(oldrim):
  b=oldrim[(j+1)%96];edge=b-a;den=cross(direction,edge)
  if abs(den)<1e-8:continue
  t=cross(a-center,edge)/den;u=cross(a-center,direction)/den
  if t>0 and 0<=u<=1:hits.append(t)
 assert hits
 p=center+direction*max(max(hits),delta.length+1.2)
 land.data.vertices[i].co.x=p.x;land.data.vertices[i].co.y=p.y
 for index in [i,i+96]:
  coast.data.vertices[index].co.x=p.x;coast.data.vertices[index].co.y=p.y
 coast.data.vertices[i+96].co.z=math.sqrt(max(1,140**2-p.x*p.x-p.y*p.y))-140-.05
for o in [water,wall,land,coast]:o.data.update()
bpy.context.view_layer.update();version=out.stem.rsplit('-',1)[-1]
(R/f'review/waterway-change-{version}.json').write_text(json.dumps({'source':bpy.data.filepath,'objects':[o.name for o in [water,wall,land,coast]],'shape':'smooth sin-squared right-bend displacement (+3.6 X, -2.5 Y maximum), and radially matched coast rim','changes':changes},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
