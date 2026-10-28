"""City remains rotated180; clear voyage corridor and re-reach the original lift.
Source actor trajectories and time axis are preserved. No collider is hidden.
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];s=bpy.context.scene
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()=='ce36841b9e3418efe1611fdbd9645b6ed9d332ff5db4278974024274d9d6cebb'
out=R/'candidate-v003.blend';assert not out.exists()
old=[]
for f in range(157):
 s.frame_set(f);old.append(s.objects['P01_SPREADER'].matrix_world.copy())
s.frame_set(0);s.objects['SF_CN_LAYOUT'].location.y-=4.6;bpy.context.view_layer.update()
D=s.objects['SF_CN_LAYOUT'].matrix_world.copy();DI=D.inverted();jib=s.objects['CR_SLEW_JIB']
cfg=json.loads((R.parent/'s2-styleframe-match-v001/review/crane-style-proposal-v019.json').read_text());A=Vector(cfg['beam_endpoints'][0]);B=Vector(cfg['beam_endpoints'][1]);u=(B-A).normalized();L=(B-A).length
pivot=DI@jib.matrix_world.translation;load=DI@old[72].translation;delta=Vector((load.x-pivot.x,load.y-pivot.y,0));radius=delta.length
factor=2.05
# Deform in the unslewed jib coordinates. Preserve cross-sections and the bearing.
for o in jib.children:
 if o.type!='MESH' or o.name.startswith('CR_ROTATING_BEARING'):continue
 M=o.matrix_local.copy();MI=M.inverted();pts=[M@v.co for v in o.data.vertices];center=sum(pts,Vector())/len(pts)
 for vert,p in zip(o.data.vertices,pts):
  if o.name.startswith(('CR_CAB','CR_MACHINERY')):q=p+u*center.dot(u)*(factor-1)
  else:q=p+u*p.dot(u)*(factor-1)
  if o.name.startswith('CR_CAB'):
   side=Vector((-u.y,u.x,0));q+=side*(-1.45-center.dot(side))+Vector((0,0,.5))
  vert.co=MI@q
 o.data.update()
# Stop terrace's underwater front batter from protruding through the arrival lane.
terrain=s.objects['US_LAND_TERRACE']
for i in [4,5]:terrain.data.vertices[i].co.y=3.3
terrain.data.update()
heading=(math.atan2(delta.y,delta.x)-math.atan2(u.y,u.x)+math.pi)%math.tau-math.pi
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def key(o,paths,f):
 for path in paths:o.keyframe_insert(path,frame=f)
affected=['CR_SLEW_JIB','CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD','P01_SPREADER']+[o.name for o in s.objects if o.name.startswith('CR_WORKING_CABLE')]
for n in affected:s.objects[n].animation_data_clear()
spre=s.objects['P01_SPREADER'];spre.rotation_mode='QUATERNION';prev={}
for f in range(157):
 p=DI@old[f].translation;a=smooth((f-100)/38);ang=heading*(1-a)+math.radians(45)*a;rr=radius+(L*.47-radius)*a;direction=Matrix.Rotation(ang,3,'Z')@u
 p.z+=2.4*smooth((f-138)/18)
 p.x=pivot.x+direction.x*rr;p.y=pivot.y+direction.y*rr
 jib.rotation_euler.z=ang;key(jib,['rotation_euler'],f)
 car=s.objects['CR_TROLLEY_CARRIAGE'];car.location=(p.x,p.y,6.85);car.rotation_euler.z=math.atan2(u.y,u.x)+ang;key(car,['location','rotation_euler'],f)
 head=s.objects['CR_SUSPENSION_HEAD'];head.location=(p.x,p.y,6.16);key(head,['location'],f)
 spre.location=D@p;spre.rotation_quaternion=old[f].to_quaternion();key(spre,['location','rotation_quaternion'],f)
 fold=1-smooth((f-88)/12);hx=.27+1.13*fold;hy=.17+.43*fold
 for i,c in enumerate(sorted([s.objects[n] for n in affected if n.startswith('CR_WORKING_CABLE')],key=lambda o:o.name)):
  sx=-1 if i<2 else 1;sy=-1 if i%2==0 else 1;bottom=p+Vector((sx*hx,sy*hy,.10));top=Vector((p.x+sx*hx,p.y+sy*hy,6.14));dv=top-bottom
  c.location=(top+bottom)/2;c.scale=(1,1,dv.length);q=dv.to_track_quat('Z','Y')
  if c.name in prev and q.dot(prev[c.name])<0:q.negate()
  prev[c.name]=q.copy();c.rotation_quaternion=q;key(c,['location','rotation_quaternion','scale'],f)
for n in affected:
 for l in s.objects[n].animation_data.action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
s['city_rotation_contact_fix']='Under validation';s.frame_set(156)
(R/'review/build-v003.json').write_text(json.dumps({'city_offset_world_y':4.6,'jib_longitudinal_factor':factor,'load_radius':radius,'park_slew_degrees':45,'park_hoist_height':5.4,'US_terrace_front_bottom_y':3.3,'changed_actions':affected},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out));print('FIX_SAVED',out)
