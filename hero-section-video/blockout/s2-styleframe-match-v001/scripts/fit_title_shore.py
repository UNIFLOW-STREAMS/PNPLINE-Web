import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
old=json.loads((R/'review/title-arc-v024-config.json').read_text());base=json.loads((R/'review/title-arc-v006-config.json').read_text())
w=s.objects['SF_BASIN_WATER_SURFACE'];N=len(w.data.vertices)//2;outer=[v.co.copy()for v in list(w.data.vertices)[:N]];inner=[v.co.copy()for v in list(w.data.vertices)[N:]]
def inside(p,poly):
 hit=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if(a.y>p.y)!=(b.y>p.y)and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:hit=not hit
 return hit
def unbend(p,c):
 t=math.radians(c['yaw_degrees']);dx=p.x-c['midpoint'][0];dy=p.y-c['midpoint'][1]
 x=math.cos(t)*dx+math.sin(t)*dy;y=-math.sin(t)*dx+math.cos(t)*dy+c['radius']
 return Vector((c['radius']*math.atan2(x,y),math.hypot(x,y)-c['radius'],p.z))
def bend(v,c):
 a=v.x/c['radius'];r=c['radius']+v.y;t=math.radians(c['yaw_degrees'])
 x=r*math.sin(a);y=r*math.cos(a)-c['radius']
 return Vector((c['midpoint'][0]+math.cos(t)*x-math.sin(t)*y,c['midpoint'][1]+math.sin(t)*x+math.cos(t)*y,v.z))
feet={}
for ch in 'CHINA':
 root=s.objects['SF_CHINA_'+ch];o=s.objects['SF_CHINA_GOLD_'+ch];ps=[root.location+v.co for v in o.data.vertices];low=min(p.z for p in ps)
 feet[ch]=[unbend(p,old)for p in ps if p.z<low+.15]
results=[]
for scale in [1,1.08,1.12,1.16,1.20,1.24]:
 for y in [28,29,30,31,32]:
  c=dict(old,radius=old['radius']*scale,midpoint=[-4,y]);wet={}
  for ch,ps in feet.items():
   pts=[bend(Vector((p.x*scale,p.y,p.z)),c)for p in ps];wet[ch]=sum(inside(p,outer)and not inside(p,inner)for p in pts)
  results.append({'scale':scale,'y':y,'wet':wet,'total':sum(wet.values())})
print(json.dumps(sorted(results,key=lambda r:(r['total'],abs(r['scale']-1)*10+abs(r['y']-28)))[:15],indent=2))
if '--' in sys.argv:
 out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
 scale=1.16;c=dict(old,radius=old['radius']*scale,midpoint=[-4,31],widths=[v*scale for v in old['widths']],gap=old['gap']*scale)
 deltas={}
 for ch in 'CHINA':
  root=s.objects['SF_CHINA_'+ch];before=root.location.copy();u=unbend(before,old);u.x*=scale;after=bend(u,c);deltas[ch]=after-before
  for o in root.children:
   if o.type=='MESH':
    for v in o.data.vertices:
     u=unbend(before+v.co,old);u.x*=scale;v.co=bend(u,c)-after
    o.data.update()
  root.location=after
 for side,ch in [('LEFT','C'),('RIGHT','A')]:s.objects['SF_CLOUD_'+side].location+=deltas[ch]
 shore=s.objects.get('SF_TITLE_SHORE')
 if shore:bpy.data.objects.remove(shore,do_unlink=True)
 bpy.context.view_layer.update();ver=out.stem.rsplit('-',1)[-1]
 (R/f'review/title-arc-{ver}-config.json').write_text(json.dumps(c,indent=2))
 (R/f'review/title-shore-fit-{ver}.json').write_text(json.dumps({'source':bpy.data.filepath,'scale_along_arc':scale,'midpoint':c['midpoint'],'radius':c['radius'],'deleted_trial_object':'SF_TITLE_SHORE','purpose':'Keep the full right water bend visible and position the continuous title on the existing dry bank'},indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(out))
