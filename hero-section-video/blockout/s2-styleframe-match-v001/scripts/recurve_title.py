"""Recurve only the title and reposition its flanking clouds from v004."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
old=json.loads((R/'review/title-arc-v004-config.json').read_text())
new=dict(old,radius=28.0,yaw_degrees=-8.0,midpoint=[-4.0,28.0])
def bend(v,c):
 a=v.x/c['radius'];r=c['radius']+v.y;yaw=math.radians(c['yaw_degrees'])
 x=r*math.sin(a);y=r*math.cos(a)-c['radius']
 return Vector((c['midpoint'][0]+math.cos(yaw)*x-math.sin(yaw)*y,c['midpoint'][1]+math.sin(yaw)*x+math.cos(yaw)*y,v.z))
def unbend(p,c):
 yaw=math.radians(c['yaw_degrees']);dx=p.x-c['midpoint'][0];dy=p.y-c['midpoint'][1]
 x=math.cos(yaw)*dx+math.sin(yaw)*dy;y=-math.sin(yaw)*dx+math.cos(yaw)*dy+c['radius']
 return Vector((c['radius']*math.atan2(x,y),math.hypot(x,y)-c['radius'],p.z))
s=bpy.context.scene;s.frame_set(156);delta={}
for ch in 'CHINA':
 root=s.objects['SF_CHINA_'+ch];before=root.location.copy();after=bend(unbend(before,old),new);delta[ch]=after-before
 for o in root.children:
  if o.type=='MESH':
   for v in o.data.vertices:v.co=bend(unbend(before+v.co,old),new)-after
   o.data.update()
 root.location=after
s.objects['SF_CLOUD_LEFT'].location+=delta['C']
s.objects['SF_CLOUD_RIGHT'].location+=delta['A']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
bpy.context.view_layer.update()
version=out.stem.rsplit('-',1)[-1]
(R/f'review/title-arc-{version}-config.json').write_text(json.dumps(new,indent=2))
(R/f'review/title-recurve-{version}.json').write_text(json.dumps({'source':bpy.data.filepath,'output':str(out),'old':old,'new':new,'delta':{k:list(v)for k,v in delta.items()},'scope':'Only title mesh vertices/root positions and two cloud root positions; no camera or actor changes'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
