"""Finish tree setbacks and extend dry rear coast under the curved title."""
import bpy,math,json
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;s.frame_set(156);center=Vector((-5,23));land=s.objects['SF_FRONT_LAND'];n=len(land.data.vertices)//2
inner=[Vector((v.co.x,v.co.y))for v in s.objects['SF_ISLAND_TOP'].data.vertices]
def cross(a,b):return a.x*b.y-a.y*b.x
def hit(poly,d):
 hits=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  e=b-a;den=cross(d,e)
  if abs(den)<1e-8:continue
  t=cross(a-center,e)/den;u=cross(a-center,d)/den
  if t>0 and 0<=u<=1:hits.append(t)
 return max(hits)
for j in range(45,105):
 trunk=s.objects['SF_TREE_TRUNK.'+str(j).zfill(3)];c=sum((v.co for v in trunk.data.vertices),Vector())/len(trunk.data.vertices)
 d=(Vector(c[:2])-center).normalized();p=center+d*(hit(inner,d)-.24);delta=Vector((p.x-c.x,p.y-c.y,0))
 for kind in ['TRUNK','CROWN']:
  o=s.objects['SF_TREE_'+kind+'.'+str(j).zfill(3)]
  for v in o.data.vertices:v.co+=delta
  o.data.update()
feet=[]
for ch in 'CHINA':
 root=s.objects['SF_CHINA_'+ch];o=s.objects['SF_CHINA_GOLD_'+ch];ps=[root.location+v.co for v in o.data.vertices];low=min(p.z for p in ps)
 feet += [Vector(p[:2])for p in ps if p.z<low+.15]
polar=[(math.atan2(p.y-center.y,p.x-center.x),(p-center).length)for p in feet]
coast=s.objects['SF_COAST_FOLDED_FACE'];deltas=[]
for i in range(n):
 p=Vector(land.data.vertices[i].co[:2]);d=(p-center).normalized();a=math.atan2(d.y,d.x);r=(p-center).length
 required=max((fr+.55)*math.exp(-(math.atan2(math.sin(fa-a),math.cos(fa-a))/.12)**2)for fa,fr in polar)
 nr=max(r,required);q=center+d*nr;deltas.append(nr-r)
 land.data.vertices[i].co.x=q.x;land.data.vertices[i].co.y=q.y
 for j in [i,i+n]:coast.data.vertices[j].co.x=q.x;coast.data.vertices[j].co.y=q.y
 coast.data.vertices[i+n].co.z=math.sqrt(max(1,140**2-q.x*q.x-q.y*q.y))-140-.05
land.data.update();coast.data.update();bpy.context.view_layer.update()
R=Path(__file__).resolve().parents[1];ver=Path(bpy.data.filepath).stem.rsplit('-',1)[-1]
(R/f'review/bank-support-{ver}.json').write_text(json.dumps({'tree_inset_m':.24,'rear_coast_max_extension_m':max(deltas),'water_and_inner_bank_unchanged':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
