"""Raise supported gantry and S1 lift; bind the independent pallet to cargo's pose.
Preserve the source landing and downstream animation instead of hiding payload.
"""
import bpy,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;source=Path(bpy.data.filepath)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='64a206b9104e6c8f0cd0f4c2232bcac8789df47bd2e06cc3207743a87d70ce98'
out=R/'master-previz-crane-height-v001.blend';assert not out.exists()
s.frame_set(72);cargo=s.objects['A01_CONTAINER'];pallet=s.objects['W01_NEW_PALLET'];relative=cargo.matrix_world.inverted()@pallet.matrix_world;D=s.objects['SF_CN_LAYOUT'].matrix_world.copy();up=D.to_3x3()@Vector((0,0,1));times=[i/4 for i in range(625)]
names=['A01_CONTAINER','W01_NEW_PALLET','CAM_MASTER','CAM_LOOK_TARGET','P01_SPREADER'];original={n:[] for n in names}
for t in times:
 s.frame_set(int(t),subframe=t%1)
 for n in names:original[n].append(s.objects[n].matrix_world.copy())
def smooth(t):
 t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
def lift(t):return 2.5*(1-smooth(t/72)) if t<72 else 0
def hoist(t):return lift(t) if t<=78 else 3*smooth((t-78)/60)
def curves(o):
 ad=o.animation_data
 return [fc for l in ad.action.layers for st in l.strips for bag in st.channelbags if bag.slot_handle==ad.action_slot.handle for fc in bag.fcurves]
def replace_location(o,values,end):
 for fc in curves(o):
  if fc.data_path!='location':continue
  props=['interpolation','easing','handle_left_type','handle_right_type','amplitude','back','period']
  keep=[{'co':list(k.co),'left':list(k.handle_left),'right':list(k.handle_right),**{p:getattr(k,p) for p in props}} for k in fc.keyframe_points if k.co.x>=end]
  fresh=[{'co':[t,v[fc.array_index]]} for t,v in values.items() if t<end];rows=fresh+keep;assert all(a['co'][0]<b['co'][0] for a,b in zip(rows,rows[1:]))
  fc.keyframe_points.clear();fc.keyframe_points.add(len(rows));fc.keyframe_points.foreach_set('co',np.array([r['co']for r in rows],dtype=np.float32).ravel())
  for k,r in zip(fc.keyframe_points,rows):
   if 'left' in r:
    for p in props:setattr(k,p,r[p])
    k.handle_left=r['left'];k.handle_right=r['right']
   else:k.interpolation='LINEAR';k.handle_left_type='VECTOR';k.handle_right_type='VECTOR'
 # Source retained keys and handles stay exact; no automatic handle recomputation.
values={n:{} for n in names}
for i,t in enumerate(times):
 delta=up*lift(t);cm=original['A01_CONTAINER'][i].copy();cm.translation+=delta
 values['A01_CONTAINER'][t]=cm.translation
 values['W01_NEW_PALLET'][t]=(cm@relative).translation
 for n in ['CAM_MASTER','CAM_LOOK_TARGET']:values[n][t]=original[n][i].translation+delta
 values['P01_SPREADER'][t]=original['P01_SPREADER'][i].translation+up*hoist(t)
for n in names:replace_location(s.objects[n],values[n],157 if n=='P01_SPREADER' else 72)
# Upper structure rises3m; four feet/bogies stay on the existing shore surface.
s.frame_set(0);root=s.objects['CR_COMPACT_GANTRY'];geo=[]
for o in root.children:
 if o.type!='MESH':continue
 if o.name.startswith(('CR_LEG_','CR_PORTAL_BRACE','CR_PORTAL_TIE','CR_LOWER_CROSS')):
  for v in o.data.vertices:v.co.z+=3*max(0,(v.co.z-1.41)/(6.12-1.41))
 elif o.name.startswith(('CR_FIXED_SLEW_SEAT','CR_FIXED_PORTAL_CAP')):
  for v in o.data.vertices:v.co.z+=3
 else:continue
 o.data.update();geo.append(o.name)
s.objects['CR_SLEW_JIB'].location.z+=3
for n in ['CR_TROLLEY_CARRIAGE','CR_SUSPENSION_HEAD']:
 for fc in curves(s.objects[n]):
  if fc.data_path=='location' and fc.array_index==2:
   for k in fc.keyframe_points:k.co.y+=3;k.handle_left.y+=3;k.handle_right.y+=3
# Rebuild all four ropes from actual raised crosshead and hoist positions.
cables=sorted([o for o in s.objects if o.name.startswith('CR_WORKING_CABLE')],key=lambda o:o.name);prev={}
for c in cables:c.animation_data_clear()
for t in times:
 s.frame_set(int(t),subframe=t%1);p=D.inverted()@s.objects['P01_SPREADER'].matrix_world.translation;head=D.inverted()@s.objects['CR_SUSPENSION_HEAD'].matrix_world.translation;fold=1-smooth((t-88)/12);hx=.27+1.13*fold;hy=.17+.43*fold
 for i,c in enumerate(cables):
  sx=-1 if i<2 else 1;sy=-1 if i%2==0 else 1;bottom=p+Vector((sx*hx,sy*hy,.10));top=head+Vector((sx*hx,sy*hy,-.02));dv=top-bottom;assert dv.z>.4,(t,dv.z)
  c.location=(bottom+top)/2;c.scale=(1,1,dv.length);q=dv.to_track_quat('Z','Y')
  if c.name in prev and q.dot(prev[c.name])<0:q.negate()
  prev[c.name]=q.copy();c.rotation_quaternion=q
  for path in ['location','scale','rotation_quaternion']:c.keyframe_insert(path,frame=t)
for c in cables:
 for fc in curves(c):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
s['crane_height_revision']='Upper structure +3m; initial lift +2.5m; internal pallet follows container during S1; f72 landing preserved'
s.frame_set(0);s.use_preview_range=False;bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'delivery.json').write_text(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'crane_upper_raise_m':3,'container_initial_raise_m':2.5,'landing_frame':72,'changed_static_geometry':geo,'status':'Verification pending'},indent=2));print('SAVED',out)
