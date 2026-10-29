"""Modify one verified city input, preserving original camera curves outside allowed range."""
import bpy,sys,json,math,hashlib,argparse
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
R=Path(__file__).resolve().parents[1];D=R.parent/'us-city-concept-v001'
sys.path.insert(0,str(D/'scripts'));from safety import guard
cfg=json.loads((R/'scene-config.json').read_text());base=R/cfg['input']
p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=guard(R,a.output,base,cfg['input_sha256'])
if Path(bpy.data.filepath).resolve()!=base.resolve():raise ValueError('Only immutable current city input is accepted')
s=bpy.context.scene
if s.get('arrival_rework_version'):raise ValueError('Already modified')
if sum(o.get('uc_owner')=='us-city-concept-v001' for o in s.objects)!=1315:raise ValueError('Wrong city input')
cam=s.objects['CAM_MASTER'];target=s.objects['CAM_LOOK_TARGET'];u=s.objects['US_FRAME'].matrix_world.copy()
start,end=cfg['camera_interval'];hero_start,hero_end=cfg['hero_interval']
s.frame_set(450);ship450=u.inverted()@s.objects['A02_SHIP'].matrix_world.translation
original={}
# Quarter-frame keys retain a smooth finite track; endpoints take exact original transforms.
frames=[start+i/4 for i in range((end-start)*4+1)]
for f in frames+[end+.25]:
 s.frame_set(int(f),subframe=f%1)
 original[f]=(cam.matrix_world.copy(),cam.data.lens,target.matrix_world.translation.copy(),s.objects['A02_SHIP'].matrix_world.translation.copy())
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def pose(pos,look,up):
 z=(pos-look).normalized();x=up.cross(z).normalized();y=z.cross(x);m=Matrix((x,y,z)).transposed().to_4x4();m.translation=pos;return m
def desired_at(f):
 local_ship=u.inverted()@original[f][3]
 pos=Vector(cfg['camera_local_at_450']);pos.x+=cfg['camera_tracking_factor']*(local_ship.x-ship450.x)
 world=u@pos;world=world.normalized()*(140+cfg['camera_height'])
 return pose(world,u@Vector(cfg['look_local']),u.to_3x3()@Vector((0,0,1)))
def hermite(a,b,da,db,t,span):
 return a*(2*t**3-3*t*t+1)+b*(-2*t**3+3*t*t)+da*((t**3-2*t*t+t)*span)+db*((t**3-t*t)*span)
def qvec(q,ref):
 v=Vector(q)
 return -v if v.dot(ref)<0 else v
exit0=desired_at(hero_end);exit1=original[end][0];span=end-hero_end
dp0=(desired_at(hero_end+.25).translation-desired_at(hero_end-.25).translation)*2
dp1=(original[end+.25][0].translation-original[end-.25][0].translation)*2
q0=Vector(exit0.to_quaternion());q1=qvec(exit1.to_quaternion(),q0)
dq0=(qvec(desired_at(hero_end+.25).to_quaternion(),q0)-qvec(desired_at(hero_end-.25).to_quaternion(),q0))*2
dq1=(qvec(original[end+.25][0].to_quaternion(),q1)-qvec(original[end-.25][0].to_quaternion(),q1))*2
city=s.objects['UC_CITY_DISTRICT'];city.matrix_local=Matrix.Translation(Vector(cfg['city_pivot']))@Matrix.Rotation(math.radians(cfg['city_yaw']),4,'Z')@Matrix.Translation(Vector((0,-37,0)))
# Civic forecourt is constrained by the protected warehouse route. Keep its original local placement.
for o in list(city.children):
 if o.name.startswith('UC_CIVIC') or (o.name.startswith('UC_TREE') and o.type=='MESH' and sum(v.co.x for v in o.data.vertices)/max(1,len(o.data.vertices))>22):
  o.parent=s.objects['US_FRAME']
for ch,ang in zip('USA',cfg['letter_yaws']):
 o=s.objects['UC_LETTER_'+ch];o.location.y-=cfg['letter_arc_depth'] if ch!='S' else 0;o.location.z+=cfg['letter_raise'];o.rotation_euler.z=math.radians(ang)
 # Local Z is the extrusion axis, kept genuinely volumetric.
 o.scale.z*=1.08
lib=s.objects['UC_LIBERTY'];lib.location=cfg['statue_location'];lib.rotation_euler.z=math.radians(cfg['statue_yaw'])
for o in s.objects:
 if o.name.startswith('UC_STATIC_CRANE'):o.location+=Vector(cfg['decorative_crane_shift'])
 if o.get('uc_role')=='star':o.location.z+=cfg['star_raise']
 if o.name.startswith('UC_GLASS_SPIRE'):o.location.x+=10
# Genuine city plinths: rotated blocks and raised lettering must not float off the old terrace.
def solid(name,pts,bottom,top,mat,parent):
 n=len(pts);vs=[(x,y,z) for z in [bottom,top] for x,y in pts]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name+'_MESH');mesh.from_pydata(vs,[],faces);mesh.materials.append(mat);mesh.update()
 ob=bpy.data.objects.new(name,mesh);bpy.data.collections['SITE_AND_LANDSCAPE'].objects.link(ob);ob.parent=parent;ob['uc_owner']='us-city-concept-v001';ob['uc_zone']='SITE_AND_LANDSCAPE';return ob
stone=bpy.data.materials['UC_LIMESTONE'];bpy.context.view_layer.update()
# Clip ground footprint outside the protected warehouse and truck corridor.
poly=[city.matrix_local@Vector((x,y,0)) for x,y in [(-28,24),(26,24),(26,64),(-28,64)]]
for axis,bound,keep in [(0,34.2,-1),(1,16,1)]:
 result=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  pi=(p[axis]-bound)*keep>=0;qi=(q[axis]-bound)*keep>=0
  if pi:result.append(p)
  if pi!=qi:result.append(p.lerp(q,(bound-p[axis])/(q[axis]-p[axis])))
 poly=result
solid('UC_AR_CITY_FOUNDATION',[(p.x,p.y) for p in poly],-40,.68,stone,s.objects['US_FRAME'])
for ch in 'USA':
 o=s.objects['UC_LETTER_'+ch];pts=[o.matrix_local@v.co for v in o.data.vertices]
 # Axis aligned in city coordinates; broad enough to carry angled letter edges.
 lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 solid('UC_AR_LETTER_PLINTH_'+ch,[(lo[0]-.12,lo[1]-.12),(hi[0]+.12,lo[1]-.12),(hi[0]+.12,hi[1]+.12),(lo[0]-.12,hi[1]+.12)],.68,lo[2]-.015,stone,city)
# Recolor only working US crane material slots; copy meshes to avoid shared material mutation.
blue=bpy.data.materials['UC_HARBOR_BLUE'];white=bpy.data.materials['UC_WHITE']
for o in s.objects:
 if o.name.startswith(('P02_LEG','P02_BOOM')) or o.name in ['P02_TROLLEY','P02_SPREADER_FRAME']:
  o.data=o.data.copy();o.data.name='AR_'+o.name+'_MESH';o.data.materials.clear();o.data.materials.append(white if o.name.startswith('P02_LEG') else blue)
# Copy existing Actions; remove interior keys only, leaving original data and exterior intact.
for obj in [cam,target,cam.data]:
 obj.animation_data.action.use_fake_user=True
 obj.animation_data.action=obj.animation_data.action.copy()
 obj.animation_data.action.name='AR_'+obj.name+'_ACTION'
 for layer in obj.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in list(fc.keyframe_points):
      if start<=key.co.x<=end:fc.keyframe_points.remove(key)
previous_q=None
for f in frames:
 old,lens,oldtarget,ship=original[f]
 look=u@Vector(cfg['look_local']);desired=desired_at(f)
 w=smooth((f-start)/(hero_start-start))*smooth((end-f)/(end-hero_end))
 loc=old.translation.lerp(desired.translation,w);q=old.to_quaternion().slerp(desired.to_quaternion(),w)
 targetloc=oldtarget.lerp(look,w);newlens=lens*(1-w)+cfg['hero_lens_mm']*w
 if f>hero_end:
  t=(f-hero_end)/span
  loc=hermite(exit0.translation,exit1.translation,dp0,dp1,t,span)
  q=Quaternion(hermite(q0,q1,dq0,dq1,t,span)).normalized()
  targetloc=hermite(look,original[end][2],Vector((0,0,0)),(original[end+.25][2]-original[end-.25][2])*2,t,span)
  newlens=hermite(cfg['hero_lens_mm'],original[end][1],0,(original[end+.25][1]-original[end-.25][1])*2,t,span)
 if previous_q is not None and q.dot(previous_q)<0:q.negate()
 previous_q=q.copy()
 cam.location=loc;cam.rotation_mode='QUATERNION';cam.rotation_quaternion=q
 cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f)
 target.location=targetloc;target.keyframe_insert('location',frame=f)
 cam.data.lens=newlens;cam.data.keyframe_insert('lens',frame=f)
for obj in [cam,target,cam.data]:
 for layer in obj.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      if start<=k.co.x<=end:k.interpolation='LINEAR'
s['arrival_rework_version']='v001';s.frame_set(450)
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print('ARRIVAL_SAVED',str(out),hashlib.sha256(out.read_bytes()).hexdigest())
