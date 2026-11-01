import bpy, math, json, hashlib, shutil, array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
S=bpy.context.scene
PTR=R.parent/'latest-lookdev.json'
old=json.loads(PTR.read_text()); (R/'previous-latest-lookdev.json').write_text(json.dumps(old,indent=2))
assert Path(bpy.data.filepath).resolve()==Path(old['file']).resolve()
def digest(p):
 with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert digest(bpy.data.filepath)==old['sha256']
saved=S.frame_current; S.frame_set(0)
roots=[bpy.data.objects[n] for n in ['SF_OPEN_TOWER','SF_STEP_TOWER','SF_SPHERE_TOWER']]
allowed={o.name for p in roots for o in [p]+list(p.children_recursive)}
def protected():
 out={}
 for o in S.objects:
  if o.name in allowed or o.name.startswith('SHLM_'):continue
  out[o.name]=dict(parent=o.parent.name if o.parent else None,basis=[list(r) for r in o.matrix_basis],data=o.data.name if o.data else None,hide=o.hide_render)
 return out
before=protected()
def motion():
 out={}
 for a in bpy.data.actions:
  curves=[]
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for f in bag.fcurves:
      curves.append((f.data_path,f.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in f.keyframe_points]))
  out[a.name]=curves
 return hashlib.sha256(repr(out).encode()).hexdigest()
anim=motion()
removed=[]
for p in roots[:2]:
 for o in list(p.children_recursive):
  assert not o.animation_data and not o.constraints
  removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)

def mat(name,col,metal=0,rough=.3):
 m=bpy.data.materials.new('SHLM_'+name);m.diffuse_color=(*col,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*col,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=rough
 b.inputs['Coat Weight'].default_value=.18
 return m
glass=[mat('Blue glass '+str(i),c,.38,.24+i*.015) for i,c in enumerate([(.075,.19,.255),(.105,.235,.3),(.085,.205,.27)])]
silver=mat('Flush aluminum frames',(.34,.43,.46),.65,.31)
dark=mat('Recessed glazing joints',(.065,.105,.125),.4,.35)
stone=mat('Podium limestone',(.46,.48,.47),.1,.42)

class Batch:
 def __init__(self):self.v=[];self.f=[];self.mi=[]
 def face(self,vs,m=0):
  n=len(self.v);self.v.extend([tuple(p) for p in vs]);self.f.append(tuple(range(n,n+len(vs))));self.mi.append(m)
 def prism(self,poly,z0,z1,m=0):
  lo=[(x,y,z0) for x,y in poly];hi=[(x,y,z1) for x,y in poly]
  self.face(lo[::-1],m);self.face(hi,m)
  for j in range(len(poly)):self.face([lo[j],lo[(j+1)%len(poly)],hi[(j+1)%len(poly)],hi[j]],m)
 def finish(self,name,parent,mats):
  me=bpy.data.meshes.new(name);me.from_pydata(self.v,[],self.f);me.update()
  ob=bpy.data.objects.new(name,me);parent.users_collection[0].objects.link(ob);ob.parent=parent
  for m in mats:me.materials.append(m)
  for p,idx in zip(me.polygons,self.mi):p.material_index=idx
  return ob

def quadpanel(b,a,c,d,e,nx,nz):
 # Coplanar glass tiles within thin aluminum joints: nothing extends beyond its facade.
 a,c,d,e=map(Vector,[a,c,d,e]);normal=(c-a).cross(e-a).normalized()
 def uv(u,v):return a.lerp(c,u).lerp(e.lerp(d,u),v)
 b.face([a,c,d,e],3)
 for j in range(nz):
  for k in range(nx):
   # geometry widths: vertical seams ~0.009, floor seams ~0.007 local units
   du=.0045/max((c-a).length,.01);dv=.0035/max((e-a).length,.01)
   u0=k/nx+du;u1=(k+1)/nx-du;v0=j/nz+dv;v1=(j+1)/nz-dv
   pts=[uv(u0,v0),uv(u1,v0),uv(u1,v1),uv(u0,v1)]
   b.face([p+normal*.0015 for p in pts],(j*13+k*7)%3)

# World Financial Center: one tapered glass body, small trapezoidal opening cut through crown.
p=roots[0];body=Batch();crown=Batch()
z=11.15
lo=[(-.85,-.5,0),(.85,-.5,0),(.85,.5,0),(-.85,.5,0)]
hi=[(-.72,-.37,z),(.72,-.37,z),(.72,.37,z),(-.72,.37,z)]
for j in range(4):quadpanel(body,lo[j],lo[(j+1)%4],hi[(j+1)%4],hi[j],12 if j%2==0 else 7,75)
body.face(lo[::-1],4);body.face(hi,4)
outer=[(-.72,11.15),(.72,11.15),(.70,12.36283),(-.70,12.36283)]
inner=[(-.365,11.45),(.365,11.45),(.505,12.055),(-.505,12.055)]
# Thick watertight crown ring, true opening through front and back.
for sign in [-1,1]:
 y=sign*.37
 for j in range(4):
  pts=[(outer[j][0],y,outer[j][1]),(outer[(j+1)%4][0],y,outer[(j+1)%4][1]),(inner[(j+1)%4][0],y,inner[(j+1)%4][1]),(inner[j][0],y,inner[j][1])]
  crown.face(pts if sign==-1 else pts[::-1],0)
for ring,mi in [(outer,0),(inner,1)]:
 for j in range(4):
  a,b=ring[j],ring[(j+1)%4]
  crown.face([(a[0],-.37,a[1]),(a[0],.37,a[1]),(b[0],.37,b[1]),(b[0],-.37,b[1])],mi)
body.finish('SHLM_SWFC_tapered_curtainwall',p,glass+[silver,dark])
crown.finish('SHLM_SWFC_integrated_trapezoid_crown',p,[glass[1],silver])
# Slim perimeter frame around aperture and external corners, embedded rectangular strips.
trim=Batch()
for sign in [-1,1]:
 y=sign*.372
 for ring,width in [(inner,.032),(outer,.018)]:
  for j in range(4):
   a=Vector((ring[j][0],y,ring[j][1]));b=Vector((ring[(j+1)%4][0],y,ring[(j+1)%4][1]));v=(b-a).normalized();n=Vector((-v.z,0,v.x))*width/2
   trim.face([a-n,b-n,b+n,a+n])
trim.finish('SHLM_SWFC_aperture_reveals',p,[silver])

# Jin Mao: chamfered/octagonal stacked bays, decreasing setbacks and layered lantern spire.
p=roots[1];fac=Batch();bands=Batch()
def octagon(w):
 c=w*.70
 return [(-c,-w),(c,-w),(w,-c),(w,c),(c,w),(-c,w),(-w,c),(-w,-c)]
tiers=[(.84,0,1.05),(.79,1.05,2.03),(.735,2.03,2.94),(.68,2.94,3.78),(.625,3.78,4.55),(.57,4.55,5.25),(.515,5.25,5.88),(.46,5.88,6.44),(.405,6.44,6.93),(.35,6.93,7.35),(.295,7.35,7.70),(.24,7.70,8.02)]
for ti,(w,z0,z1) in enumerate(tiers):
 poly=octagon(w)
 for j in range(8):
  a,b=poly[j],poly[(j+1)%8]
  quadpanel(fac,(*a,z0),(*b,z0),(*b,z1),(*a,z1),max(2,round(Vector((a[0]-b[0],a[1]-b[1])).length/.115)),max(2,round((z1-z0)/.13)))
 bands.prism(octagon(w+.012),z1-.024,z1+.006)
 # Narrow attached vertical corner pilasters follow every stepped bay.
 for x,y in poly:
  bands.prism([(x-.009,y-.009),(x+.009,y-.009),(x+.009,y+.009),(x-.009,y+.009)],z0,z1)
bands.prism(octagon(.32),8.02,8.15)
for i in range(7):
 zz=8.15+i*.16;w=.29-i*.029
 bands.prism(octagon(w),zz,zz+.13)
 bands.prism(octagon(w+.015),zz+.13,zz+.15)
# Slender pointed antenna instead of oversized featureless cone.
poly=octagon(.075);zb=9.27
for j in range(8):bands.face([(*poly[j],zb),(*poly[(j+1)%8],zb),(0,0,10.137666)])
fac.finish('SHLM_JinMao_stepped_octagonal_glazing',p,glass+[silver])
bands.finish('SHLM_JinMao_attached_setbacks_and_crown',p,[silver])

pearl=roots[2];oldscale=list(pearl.scale);pearl.scale*=1.35
bpy.context.view_layer.update()
assert protected()==before,'Unrelated object transform/data changed'
assert motion()==anim,'Animation action changed'
checks=dict(source=old['file'],source_sha256=old['sha256'],unchanged_objects=len(before),unchanged_animation_hash=anim,removed_landmark_parts=removed,pearl_scale_factor=1.35,pearl_before_scale=oldscale,pearl_after_scale=list(pearl.scale),camera=S.camera.name,frame_start=S.frame_start,frame_end=S.frame_end,fps=S.render.fps)
(R/'review/checks.json').write_text(json.dumps(checks,indent=2))
S.frame_set(saved)
out=R/'pnpline-shanghai-landmarks-v001.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('SAVED',str(out),flush=True)
