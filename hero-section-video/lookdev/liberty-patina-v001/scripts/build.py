"""Build a solid edition of the supplied travel-print figure in its original local frame."""
import bpy,math,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from math import pi,cos,sin
r=Path(__file__).resolve().parents[1]
ptr=r.parent/'latest-lookdev.json'
prev=json.loads(ptr.read_text())
def sha(path):
 with open(path,'rb') as fp:return hashlib.file_digest(fp,'sha256').hexdigest()
assert sha(bpy.data.filepath)==prev['sha256']==sha(prev['versioned_copy'])
(r/'previous-latest-lookdev.json').write_bytes(ptr.read_bytes())
body=bpy.data.objects['UC_LIBERTY_BODY']; col=body.users_collection[0]
old=set(body.children)
assert len(old)==46 and all(o.name.startswith('UC_LIBERTY_') and not o.animation_data and not o.children for o in old)
for o in old:bpy.data.objects.remove(o,do_unlink=True)
atlas=bpy.data.images.load(str(r/'liberty-ink.png'));atlas.name='Liberty | isolated lithograph inks (sRGB)';atlas.pack()
def linear(x):
 x=x/255
 return ((x+.055)/1.055)**2.4 if x>.04045 else x/12.92
def material(name,rgb,printed=False):
 m=bpy.data.materials.new('Liberty | '+name);m.use_nodes=True;m.diffuse_color=tuple(map(linear,rgb))+(1,)
 n=m.node_tree.nodes;l=m.node_tree.links.new;p=n.get('Principled BSDF');p.inputs['Metallic'].default_value=.045;p.inputs['Roughness'].default_value=.78;p.inputs['Specular IOR Level'].default_value=.22
 p.inputs['Base Color'].default_value=m.diffuse_color;p.inputs['Emission Color'].default_value=m.diffuse_color;p.inputs['Emission Strength'].default_value=.17
 if printed:
  tex=n.new('ShaderNodeTexImage');tex.image=atlas;tex.extension='EXTEND'
  l(tex.outputs['Color'],p.inputs['Base Color']);l(tex.outputs['Color'],p.inputs['Emission Color'])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180;noise.inputs['Detail'].default_value=1.4
 bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0007;bump.inputs['Strength'].default_value=.11
 l(noise.outputs['Fac'],bump.inputs['Height']);l(bump.outputs['Normal'],p.inputs['Normal'])
 return m
ink=material('printed verdigris', (124,177,143),True)
mid=material('celadon',(114,171,139));light=material('seafoam',(151,199,158));deep=material('oxidised jade',(73,126,105))
shade=material('pine patina',(62,108,89));ochre=material('ochre enamel',(210,153,82))
unit=8.5/(791-23)
def mesh(name,verts,faces,slots,indices):
 m=bpy.data.meshes.new(name);m.from_pydata([((x-211)*unit,d*unit,(791-y)*unit) for x,d,y in verts],[],faces);m.update()
 for mat in slots:m.materials.append(mat)
 uv=m.uv_layers.new(name='Lithograph elevation')
 for p,idx in zip(m.polygons,indices):
  p.material_index=idx
  for li in p.loop_indices:
   x,d,y=verts[m.loops[li].vertex_index];uv.data[li].uv=((x-98+.5)/256,1-(y-18+.5)/774)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
 ob=bpy.data.objects.new(name,m);col.objects.link(ob);ob.parent=body;return ob
def loft(name,rows,back=mid,n=28,fold=0):
 # Rows specify printed elevation, lateral limits, centre depth and half-depth.
 vs=[];fs=[];ids=[]
 for y,left,right,d,depth in rows:
  for j in range(n):
   t=2*pi*j/n
   curve=sin(t)*(1+fold*cos(5*t+y*.004)+fold*.45*sin(3*t-y*.007))
   vs.append(((left+right)/2+(right-left)/2*cos(t),d+depth*curve,y))
 for i in range(len(rows)-1):
  for j in range(n):
   a=i*n+j;b=i*n+(j+1)%n
   fs.append((a,b,b+n,a+n));ids.append(0 if j>=n//2 else (2 if fold and (j+int(i*.25))%n in (3,4,8,9) else 1))
 fs.extend([tuple(reversed(range(n))),tuple(range((len(rows)-1)*n,len(rows)*n))]);ids.extend([1,1])
 return mesh(name,vs,fs,[ink,back,deep],ids)
def prism(name,outline,front,rear,side=mid,ridge=0):
 # Depth values can vary along the perimeter for chisel-cut facets.
 def val(v,x,y):return v(x,y) if callable(v) else v
 n=len(outline);vs=[(x,val(d,x,y),y) for d in [front,rear] for x,y in outline]
 fs=[tuple(reversed(range(n))),tuple(range(n,2*n))];ids=[0,1]
 for j in range(n):
  k=(j+1)%n;fs.append((j,k,k+n,j+n));ids.append(1)
 return mesh(name,vs,fs,[ink,side],ids)
loft('UC_LIBERTY_ROBE',[(791,122,300,0,54),(752,122,296,0,53),(680,122,288,1,49),(645,122,285,1,47),(578,122,278,0,44),(530,122,274,0,42),(500,122,272,0,41),(455,122,269,0,40),(416,122,266,1,39),(380,122,262,1,38),(350,122,258,0,37),(320,122,250,0,34),(302,122,245,0,31),(288,143,241,0,28),(279,163,241,0,23),(260,185,236,0,20),(245,199,226,0,16)],fold=.125)
loft('UC_LIBERTY_RAISED_ARM',[(339,122,162,0,27),(317,122,181,0,31),(298,122,185,0,29),(280,122,163,0,20),(253,122,152,-1,15),(230,122,145,-2,12),(192,122,138,-3,9),(160,122,136,-4,8),(135,122,136,-5,7.5),(124,122,136,-5,7)],deep,24)
# Arm carrying the tablet swings out of the mantle, then back towards the reader.
loft('UC_LIBERTY_LEFT_ARM',[(535,292,297,-22,3),(531,286,302,-22,11),(516,276,311,-19,17),(495,267,319,-16,19),(469,259,324,-13,21),(441,252,315,-8,22),(427,250,291,-5,22),(415,250,278,-3,17),(395,250,267,-1,12),(375,250,261,0,7)],mid,24)
loft('UC_LIBERTY_HAIR',[(349,239,258,1,9),(336,213,254,3,17),(318,194,249,4,21),(301,182,245,5,25),(285,170,244,4,26),(278,166,244,3,27),(259,180,240,2,25),(240,184,239,3,23),(225,190,233,3,18)],deep,24)
loft('UC_LIBERTY_HEAD',[(295,210,214,-22,5),(291,204,221,-22,10),(284,199,227,-21,15),(275,194,230,-20,18),(258,189,234,-19,20),(244,190,235,-16,21),(233,193,232,-13,19)],mid,24)
# A broken planar nose ridge gives the face relief in profile; eyes and lips use the print inks.
prism('UC_LIBERTY_NOSE',[(206,251),(208,253),(209,271),(214,274),(208,275),(205,272)],lambda x,y:-39-(y-251)*.15,-34,deep)
loft('UC_LIBERTY_CROWN',[(243,182,240,-9,29),(239,182,240,-9,30),(230,183,240,-8,29),(224,192,230,-6,24),(219,202,220,-4,17),(218,208,215,-4,12)],deep,32)
for i,(x,y,tx,ty) in enumerate([(185,238,142,238),(188,232,144,210),(198,226,171,188),(211,223,212,167),(224,227,250,188),(234,231,278,210),(238,238,289,238)]):
 dx,dy=tx-x,ty-y;h=math.hypot(dx,dy);perp=(-dy/h*4.2,dx/h*4.2)
 a=(x+perp[0],y+perp[1]);c=(x-perp[0],y-perp[1])
 mesh('UC_LIBERTY_CROWN_RAY_%02d'%(i+1),[(a[0],-12,a[1]),(c[0],-12,c[1]),(x,-18,y),(x,-3,y),(tx,-7+abs(i-3)*2.4,ty)],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(0,3,1,2)],[ink,mid,deep],[0,0,1,2,2])
prism('UC_LIBERTY_TABLET',[(306,395),(349,416),(306,505),(270,483),(269,472)],lambda x,y:-34-(y-395)*.10,lambda x,y:-25-(y-395)*.10,deep)
prism('UC_LIBERTY_LEFT_HAND',[(324,430),(337,432),(342,446),(336,473),(319,477),(311,467),(314,447),(323,446),(318,441)],lambda x,y:-42-(y-430)*.10,-30,mid)
loft('UC_LIBERTY_TORCH',[(134,122,136,-5,7),(126,122,139,-5,9),(118,122,143,-5,10),(94,122,140,-5,9),(87,120,142,-5,11)],shade,24)
loft('UC_LIBERTY_HAND',[(133,123,135,-8,5),(129,122,137,-9,7),(124,124,138,-10,7),(119,129,135,-8,4)],deep,16)
loft('UC_LIBERTY_TORCH_BOWL',[(92,122,140,-5,9),(89,113,149,-5,18),(84,105,156,-5,24),(80,104,157,-5,26),(76,109,153,-5,22),(73,114,147,-5,16),(69,104,156,-5,25)],deep,32)
# The two tongues are united below the notch, with independent convex sections above.
loft('UC_LIBERTY_FLAME',[(69,118,144,-5,10),(65,116,148,-5,13),(58,114,153,-5,15),(50,114,155,-5,13),(46,115,149,-5,11),(42,115,141,-5,10),(35,121,144,-5,9),(29,132,147,-5,6),(23,147,149,-5,1)],ochre,24)
loft('UC_LIBERTY_FLAME_TONGUE',[(57,131,153,-4,11),(51,137,155,-4,9),(47,142,156,-4,7),(43,149,156,-3,5),(38,155,157,-3,1)],ochre,20)
bpy.context.view_layer.update()
out=r/'pnpline-liberty-patina-v001.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
