import bpy,sys,math,random,json,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
from mathutils.bvhtree import BVHTree
from pathlib import Path
from math import sin,cos,pi,exp,sqrt,atan2
r=Path(__file__).resolve().parents[1];sys.path.insert(0,str(r/'scripts'))
from survey import hit,cam,s,ship,sea
ptr=r.parent/'latest-lookdev.json';prev=json.loads(ptr.read_text())
def digest(p):
 with open(p,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
assert digest(bpy.data.filepath)==digest(prev['versioned_copy'])==prev['sha256']
(r/'previous-latest-lookdev.json').write_bytes(ptr.read_bytes())
original_frame=s.frame_current
route=s.objects['SHIP_ROUTE'];assert route.type=='CURVE' and not route.children and route.data.bevel_depth>0
assert not any(getattr(c,'target',None)==route for o in s.objects for c in o.constraints)
bpy.data.objects.remove(route,do_unlink=True)
col=bpy.data.collections.new('Pacific crossing | offshore islands');s.collection.children.link(col)
def mat(n,h):
 rgb=[int(h[k:k+2],16)/255 for k in (0,2,4)]
 lin=[((v+.055)/1.055)**2.4 if v>.04045 else v/12.92 for v in rgb]
 m=bpy.data.materials.new('Pacific | '+n);m.use_nodes=True;m.diffuse_color=(*lin,1)
 p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Roughness'].default_value=.84
 return m
mats=[mat(n,c) for n,c in [('Tide-darkened sand','AB977B'),('Shell strand','DACAA7'),('Beach grass','ADC095'),('Coastal meadow','91AC80'),('Heather','799C74'),('Slate','737F7E'),('Lichen stone','9BA8A0'),('Pale granite','C3C9BC'),('Juniper','426A59'),('Spruce shade','3E6253'),('Spruce tips','628466'),('Sea olive','799269'),('Willow','91AA70'),('Bark','685B47')]]
def make(n,vs,fs,ids,smooth=()):
 m=bpy.data.meshes.new(n);m.from_pydata(vs,[],fs);m.update()
 for a in mats:m.materials.append(a)
 for i,p in enumerate(m.polygons):p.material_index=ids[i];p.use_smooth=ids[i] in smooth
 o=bpy.data.objects.new(n,m);col.objects.link(o);return o
shorepoints=[];centers=[]
def island(name,anchor,X,Y,rx,ry,seed,rise,ntrees,kind):
 rng=random.Random(seed);N=anchor.normalized()
 X=(X-X.dot(N)*N).normalized();Y=N.cross(X)
 def sphere(x,y):
  d=(N*140+X*x+Y*y).normalized()
  ok,p,_,_=sea.ray_cast(d*155,-d);assert ok
  return p,d
 def world(x,y,h):p,d=sphere(x,y);return p+d*h
 def coast(t):return 1+.105*sin(3*t+seed)+.08*cos(2*t+.52*seed)+.046*cos(5*t+seed*.17)+.027*sin(8*t+.2*seed)
 def radius(u,v):return sqrt(u*u+v*v)/coast(atan2(v,u))
 # An asymmetric ridge, with two lower saddles and exposed lee-side rock.
 peaks=[(-.27,.17,.96,.58,.66),(.21,.20,.73,.43,.49),(-.60,.06,.43,.31,.40)]
 if kind==1:peaks=[(.26,.07,1,.59,.65),(-.27,.22,.60,.45,.54)]
 if kind==2:peaks=[(-.18,.16,.84,.68,.63),(.36,.12,.59,.46,.52)]
 if kind==3:peaks=[(-.50,.06,.51,.44,.62),(-.14,.13,1,.49,.66),(.19,.18,.75,.36,.48),(.43,.03,.43,.31,.46)]
 def height(u,v):
  rad=radius(u,v);coastal=max(0,min(1,(1-rad)/.24))
  base=(.24+.28*(1-min(1,rad))+.04*sin(9*u+4*v))*min(1,rx/3)
  rocky=[]
  for px,py,amp,wx,wy in peaks:
   a=(u-px)/wx;b=(v-py)/wy;angle=atan2(b,a)
   rr=sqrt(a*a+b*b)*(1+.13*sin(3*angle+seed)+.08*cos(5*angle))
   rocky.append(amp*max(0,1-rr)**1.55)
  return base+rise*max(rocky)*coastal
 rings=48;inner=.83
 pts=[Vector((inner*coast(t)*cos(t),inner*coast(t)*sin(t))) for t in [2*pi*i/rings for i in range(rings)]]
 for i in range(-8,9):
  for j in range(-7,8):
   u=(i+rng.uniform(-.34,.34))/8;v=(j+rng.uniform(-.34,.34))/7
   if radius(u,v)<inner-.035:pts.append(Vector((u,v)))
 for px,py,amp,wx,wy in peaks:
  pts.append(Vector((px,py)))
  for k in range(5):
   a=2*pi*k/5+.8
   for dist in [.19,.46]:pts.append(Vector((px+cos(a)*dist*wx,py+sin(a)*dist*wy)))
 out,_,tri,*_=delaunay_2d_cdt(pts,[(i,(i+1)%rings) for i in range(rings)],[],1,1e-6)
 verts=[world(p.x*rx,p.y*ry,height(*p)) for p in out];fs=[];ids=[]
 for f in tri:
  u,v=sum((out[k] for k in f),Vector((0,0)))/len(f);z=height(u,v);face=tuple(f)
  normal=(verts[f[1]]-verts[f[0]]).cross(verts[f[2]]-verts[f[0]]).normalized()
  if normal.dot(N)<0:face=face[::-1];normal=-normal
  grade=normal.dot(N)
  matid=(7 if z>rise*.78 else (6 if normal.dot(X)<.1 else 5)) if (z>.32*rise+.22 and grade<.87) or z>.67*rise+.12 else (4 if z>.27*rise+.24 else 3)
  fs.append(face);ids.append(matid)
 last=[min(range(len(out)),key=lambda k:(out[k]-pt).length) for pt in pts[:rings]]
 for level,h,mid in [(.91,.17,2),(.982,.055,1),(1.02,-.12,0)]:
  loop=[]
  for j in range(rings):
   t=2*pi*j/rings;shape=coast(t)*level
   x=cos(t)*shape*rx;y=sin(t)*shape*ry
   loop.append(len(verts));verts.append(world(x,y,h))
   if level>1:shorepoints.append(verts[-1].copy())
  for j in range(rings):
   k=(j+1)%rings;fs.append((last[j],loop[j],loop[k],last[k]));ids.append(mid)
  last=loop
 terrain=make('Pacific | '+name+' · shoreline and ridge',verts,fs,ids,(0,1,2,3,4))
 surf=BVHTree.FromPolygons(verts,fs)
 deco=[];polys=[];colors=[]
 def stack(p,up,rads,zs,sides,materials,jitter=.1,slant=0):
  base=len(deco);spin=rng.random()*pi;xx=(X-X.dot(up)*up).normalized();yy=up.cross(xx)
  widths=[rng.uniform(1-jitter,1+jitter) for _ in range(sides)]
  for row,(rad,z) in enumerate(zip(rads,zs)):
   for k in range(sides):
    t=spin+2*pi*k/sides+row*.10
    deco.append(p+up*z+xx*(rad*widths[k]*cos(t)+slant*z)+yy*(rad*widths[k]*sin(t)))
  for j in range(len(zs)-1):
   for k in range(sides):
    a=base+j*sides+k;b=base+j*sides+(k+1)%sides
    polys.append((a,b,b+sides,a+sides));colors.append(materials[j])
  polys.append(tuple(base+(len(zs)-1)*sides+k for k in range(sides)));colors.append(materials[-1])
 positions=[];count=0
 for _ in range(ntrees*130):
  if count>=ntrees:break
  u,v=rng.uniform(-.92,.92),rng.uniform(-.92,.92)
  if radius(u,v)>.80 or height(u,v)>.45*rise+.23:continue
  if sin(6*u+seed)+cos(8*v-2*u)<-.68:continue
  x,y=u*rx,v*ry
  if any((x-a)**2+(y-b)**2<.34 for a,b in positions):continue
  p,up=sphere(x,y);p,nn,_,_=surf.ray_cast(p+9*up,-up)
  if p is None or nn.dot(up)<.81:continue
  positions.append((x,y));count+=1;h=rng.uniform(.55,1.25)*min(1,rx/3.5)
  stack(p,up,[.055*h,.037*h],[0,.44*h],5,[13])
  if rng.random()<.53:
   stack(p,up,[.25*h,.17*h,.22*h,.12*h,.15*h,.012*h],[.20*h,.44*h,.44*h,.66*h,.66*h,h],8,[9,9,8,8,10],.12,.04)
  else:
   idx=rng.choice((10,11,12));stack(p,up,[.13*h,.31*h,.29*h,.17*h,.045*h],[.22*h,.4*h,.68*h,.87*h,.93*h],8,[idx]*4,.20,.06)
 # Exposed headland stones echo the cliff facets in the city diorama.
 for j in range(int(rx*2.3)):
  t=rng.random()*2*pi;rr=rng.uniform(.93,1.08)*coast(t)
  p,up=sphere(rx*rr*cos(t),ry*rr*sin(t));size=rng.uniform(.13,.42)*min(1,rx/3)
  stack(p+up*.03,up,[size,size*.85,size*.43],[0,size*.53,size*.92],6,[5,6],.35,.2)
 make('Pacific | '+name+' · trees and tide rocks',deco,polys,colors)
 centers.append((name,list(anchor),count))
def group(frame,u,v,design):
 s.frame_set(frame);anchor=hit(u,v);assert anchor is not None
 n=anchor.normalized();right=cam.matrix_world.to_3x3()@Vector((1,0,0));x=(right-n*right.dot(n)).normalized();y=n.cross(x)
 for name,a,b,ang,rx,ry,seed,h,trees,kind in design:
  c=(anchor+a*x+b*y+Vector((0,4.5,0))).normalized()*140
  if frame==201:
   base=Vector((-84.8,8.4,(140**2-84.8**2-8.4**2)**.5));c=(base+a*x+b*y).normalized()*140
  if frame==226:c=(anchor+a*x+b*y).normalized()*140
  island(name,c,x*cos(ang)+y*sin(ang),y,rx,ry,seed,h,trees,kind)
group(201,.32,.67,[('Windward Cay',0,0,.43,3.3,1.8,16,1.55,9,1),('Needle Skerry',4.9,1.1,-.52,1.35,.85,25,1.05,0,0)])
group(225,.36,.66,[('Twin Saddle',0,0,.27,7.65,3.75,13,3.9,32,0),('East Head',9.9,1.6,-.41,2.3,1.40,39,1.35,4,1)])
group(245,.28,.54,[('Juniper Key',0,0,-.42,5.0,2.65,33,2.35,18,2)])
group(226,.275,.878,[('Cloudrest Ridge',0,0,.13,6.2,2.7,53,2.85,21,3),('Little Cape',8.5,.6,-.24,1.85,1.05,83,1.15,3,1)])
s.frame_set(original_frame)
out=r/'pnpline-pacific-islands-v001.blend'
bpy.context.preferences.filepaths.save_version=0
print('ISLANDS',centers)
(r/'review/layout.json').write_text(json.dumps(centers,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)



