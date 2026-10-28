"""Continuous title wrap and sinuous basin; retain v021 animation verbatim."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;s.frame_set(156)
out=Path(sys.argv[sys.argv.index('--')+1]);assert not out.exists()
old=json.loads((R/'review/title-arc-v006-config.json').read_text())
# The end-letter tangent lines enclose 80 degrees (100 degrees of turning).
span=sum(old['widths'])+4*old['gap']-(old['widths'][0]+old['widths'][-1])/2
new=dict(old,radius=span/math.radians(100),note='100 degree C-to-A tangent turn; supplementary enclosed angle 80 degrees, smoothly distributed around I')
new['midpoint']=[-4.0,29.8]
def bend(v,c):
 a=v.x/c['radius'];r=c['radius']+v.y;t=math.radians(c['yaw_degrees'])
 x=r*math.sin(a);y=r*math.cos(a)-c['radius']
 return Vector((c['midpoint'][0]+math.cos(t)*x-math.sin(t)*y,c['midpoint'][1]+math.sin(t)*x+math.cos(t)*y,v.z))
def unbend(p,c):
 t=math.radians(c['yaw_degrees']);dx=p.x-c['midpoint'][0];dy=p.y-c['midpoint'][1]
 x=math.cos(t)*dx+math.sin(t)*dy;y=-math.sin(t)*dx+math.cos(t)*dy+c['radius']
 return Vector((c['radius']*math.atan2(x,y),math.hypot(x,y)-c['radius'],p.z))
delta={}
for ch in 'CHINA':
 root=s.objects['SF_CHINA_'+ch];before=root.location.copy();after=bend(unbend(before,old),new);delta[ch]=after-before
 for o in root.children:
  if o.type=='MESH':
   for v in o.data.vertices:v.co=bend(unbend(before+v.co,old),new)-after
   o.data.update()
 root.location=after
for side,ch in [('LEFT','C'),('RIGHT','A')]:s.objects['SF_CLOUD_'+side].location+=delta[ch]

# Smooth spatial displacement: front island bulge followed by a returning
# right-bank bend. The back rim and all crane foundations remain untouched.
water=s.objects['SF_BASIN_WATER_SURFACE'];land=s.objects['SF_FRONT_LAND'];wall=s.objects['SF_BASIN_OUTER_WALL']
island=s.objects['SF_ISLAND_TOP'];iw=s.objects['SF_ISLAND_WALL'];edge=s.objects['SF_ISLAND_EDGE']
original_inner=[v.co.copy()for v in list(water.data.vertices)[96:]]
def island_shift(p):
 return (-3.3*math.exp(-((p.x+6.5)/5.6)**2)+2.0*math.exp(-((p.x-3.5)/4.0)**2))*math.exp(-((p.y-18.7)/3.6)**2)
def bank_shift(p):
 return 2.0*math.exp(-((p.x-3.5)/4.0)**2)*math.exp(-((p.y-13.5)/3.4)**2)
for i in range(96):
 p=water.data.vertices[i].co.copy();dy=bank_shift(p)
 for o,indices in [(water,[i]),(land,[i+96]),(wall,[i,i+96])]:
  for j in indices:o.data.vertices[j].co.y+=dy
 p=original_inner[i];dy=island_shift(p)
 for o,indices in [(water,[i+96]),(island,[i]),(iw,[i,i+96])]:
  for j in indices:o.data.vertices[j].co.y+=dy
 edge.data.splines[0].points[i].co.y+=dy
# Trees on the island edge follow their original nearest bank sample rigidly.
moved_trees=[]
for o in s.objects:
 if not o.name.startswith(('SF_TREE_TRUNK','SF_TREE_CROWN')) or o.type!='MESH':continue
 center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
 dist,i=min(((Vector((center.x-p.x,center.y-p.y)).length,i)for i,p in enumerate(original_inner)))
 if dist<.9:
  dy=island_shift(original_inner[i])
  if abs(dy)>.001:
   for v in o.data.vertices:v.co.y+=dy
   o.data.update();moved_trees.append(o.name)
for o in [water,land,wall,island,iw]:o.data.update()
# Front-right towers follow the returning bank rigidly, retaining their designs.
moved_buildings={}
for j in range(8,14):
 o=s.objects['SF_HIGHRISE_'+str(j)];p=o.location.copy()
 dy=max(0,island_shift(p))
 if dy>.001:o.location.y+=dy;moved_buildings[o.name]=dy
# A low continuous shore strip below the title prevents the newly curved feet
# from standing over the basin. It joins the existing land, below its top level.
D=s.objects['SF_CN_LAYOUT'];col=bpy.data.collections.new('TITLE_CURVED_SHORE');s.collection.children.link(col)
N=160;half=(sum(old['widths'])+4*old['gap'])/2+.35
vs=[]
for z,y in [(1.05,-1.3),(1.05,1.15),(-.2,-1.3),(-.2,1.15)]:
 for i in range(N+1):vs.append(tuple(bend(Vector((-half+2*half*i/N,y,z)),new)))
faces=[];n=N+1
for i in range(N):
 faces.extend([(i,i+1,n+i+1,n+i),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
faces.extend([(0,n,3*n,2*n),(N,2*n+N,3*n+N,n+N)])
mesh=bpy.data.meshes.new('SF_TITLE_SHORE');mesh.from_pydata(vs,[],faces);mesh.update()
shore=bpy.data.objects.new('SF_TITLE_SHORE',mesh);col.objects.link(shore);shore.parent=D;mesh.materials.append(bpy.data.materials['SF_white'])
shore['purpose']='Curved ground strip supporting the revised title, upper surface below the existing land'
bpy.context.view_layer.update()
ver=out.stem.rsplit('-',1)[-1]
(R/f'review/title-arc-{ver}-config.json').write_text(json.dumps(new,indent=2))
(R/f'review/title-water-change-{ver}.json').write_text(json.dumps({'source':bpy.data.filepath,'output':str(out),'old_arc':old,'new_arc':new,'letter_delta':{k:list(v)for k,v in delta.items()},'bank_objects':[o.name for o in [water,land,wall,island,iw,edge]],'trees_following_bank':moved_trees,'buildings_following_bank':moved_buildings,'added':['SF_TITLE_SHORE'],'scope':'Static lettering, cloud root positions, water/island banks, supporting shore and adjacent trees/towers. All actions, camera and crane geometry preserved.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out))
