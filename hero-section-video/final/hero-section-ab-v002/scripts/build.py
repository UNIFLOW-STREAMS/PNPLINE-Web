import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];R.joinpath('review').mkdir(parents=True,exist_ok=True);S=bpy.context.scene;label=sys.argv[-1]
sys.path.insert(0,str(R.parent/'hero-section-ab-v001/scripts'))
from state import curves,hashed,presentation,sha
source=bpy.data.filepath;source_sha=sha(source);present=hashed(presentation())
roots=['CH_LOADER','CH_LOAD_SUPPORT','CH_LOAD_ARM_0','CH_LOAD_ARM_1','W08_LAST_LOAD','W09_OUT_CART','A04_PRIMARY']
names=set(roots)
van_names={'A04_PRIMARY','SURF_A04_PRIMARY'}
for o in S.objects['A04_PRIMARY'].children_recursive:
 if o.animation_data and o.animation_data.action:names.add(o.name);van_names.add(o.name)
for o in S.objects['CH_LOADER'].children_recursive:
 if o.animation_data and o.animation_data.action:names.add(o.name)
for name in list(names):
 p=S.objects[name].parent
 while p and p.name!='US_FRAME':
  if p.animation_data and p.animation_data.action:names.add(p.name)
  p=p.parent
objects=[S.objects[n] for n in sorted(names) if S.objects[n].animation_data and S.objects[n].animation_data.action]
untouched={a.name:hashed(curves(a)) for a in bpy.data.actions if a not in {o.animation_data.action for o in objects}}
def timewarp(f):
 # Arrival is earlier, carry takes 45f instead of 23f, retreat is gradual.
 knots=[(0,0),(778,778),(800,800),(820,830),(865,853),(875,859),(910,872),(940,940),(989,989)]
 for (a,x),(b,y) in zip(knots,knots[1:]):
  if a<=f<=b:return x+(y-x)*(f-a)/(b-a)
 return f
cache={o.name:{} for o in objects}
for f in range(779,990):
 t=timewarp(f);S.frame_set(int(t),subframe=t-int(t))
 for o in objects:
  if o.name in {'W08_LAST_LOAD','SURF_W08_LAST_LOAD'} or o.name in van_names:continue
  cache[o.name][f]=o.matrix_basis.copy()
 # Cargo stays seated in the truck through departure, then follows the original truck.
 t=timewarp(f) if f<=865 else (853+(f-865)*17/35 if f<900 else 870+(f-900)*119/89)
 S.frame_set(int(t),subframe=t-int(t))
 for o in objects:
  if o.name in {'W08_LAST_LOAD','SURF_W08_LAST_LOAD'} or o.name in van_names:cache[o.name][f]=o.matrix_basis.copy()
for o in objects:
 o.animation_data.action=o.animation_data.action.copy();o.animation_data.action.name='Load v002 | '+o.name
 for f,m in cache[o.name].items():
  o.matrix_basis=m
  for prop in ['location','rotation_quaternion' if o.rotation_mode=='QUATERNION' else 'rotation_euler','scale']:o.keyframe_insert(prop,frame=f)
 for layer in o.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      if 779<=k.co.x<=989:k.interpolation='LINEAR'
# Foot planting: each planted boot stays in world space while its partner swings.
feet={side:S.objects['Figure Load | '+side+' lace-up safety boot'] for side in ['L','R']};tracks={side:{} for side in feet};poses={}
for f in range(806,935):
 S.frame_set(f)
 for side,o in feet.items():tracks[side][f]=o.matrix_world.copy()
 poses[f]={o.name:o.matrix_basis.copy() for side in feet for o in [S.objects['Figure Load | '+side+' trouser thigh'],S.objects['Figure Load | '+side+' trouser calf']]}
def solve(a,b,l1,l2,hint):
 delta=b-a;d=max(.0001,delta.length);n=delta/d;h=hint-n*hint.dot(n)
 if h.length<.001:h=Vector((0,-1,0))
 x=(d*d+l1*l1-l2*l2)/(2*d);x=max(.001,min(d-.001,x));return a+n*x+h.normalized()*math.sqrt(max(.0001,l1*l1-x*x))
for f in range(806,916):
 S.frame_set(f)
 for j,(side,boot) in enumerate(feet.items()):
  phase=f-806+j*4;base=806+(phase//8)*8-j*4;base=max(806,base);nextf=min(934,base+8);u=(f-base)/8
  a=tracks[side][base].translation;b=tracks[side][nextf].translation
  # The stance occupies the first half of a gait cycle.
  t=max(0,min(1,(u-.5)*2));w=t*t*(3-2*t);target=tracks[side][f].translation.copy()
  up=boot.parent.matrix_world.to_3x3()@Vector((0,0,1));up.normalize();target+=up*(.035*math.sin(math.pi*t))
  if f>=910:
   blend=(f-910)/6;target=target.lerp(tracks[side][f].translation,blend)
  thigh=S.objects['Figure Load | '+side+' trouser thigh'];shin=S.objects['Figure Load | '+side+' trouser calf'];space=boot.parent.matrix_world@boot.matrix_parent_inverse;inv=space.inverted();foot=inv@target;hip=thigh.location.copy();oldknee=shin.location.copy();ank=foot+Vector((0,0,.12));oldank=inv@tracks[side][f].translation+Vector((0,0,.12));offset=ank-hip
  if offset.length>.748:ank=hip+offset.normalized()*.748;foot=ank-Vector((0,0,.12));target=space@foot
  knee=solve(hip,ank,.395,.378,oldknee-(hip+oldank)/2)
  for obj,start,end in [(thigh,hip,knee),(shin,knee,ank)]:
   delta=end-start;obj.location=start;obj.rotation_mode='QUATERNION';obj.rotation_quaternion=delta.to_track_quat('Z','Y');obj.scale.z=delta.length
   for prop in ['location','rotation_quaternion','scale']:obj.keyframe_insert(prop,frame=f)
  m=tracks[side][f].copy();m.translation=target;boot.matrix_world=m
  for prop in ['location','rotation_quaternion' if boot.rotation_mode=='QUATERNION' else 'rotation_euler']:boot.keyframe_insert(prop,frame=f)
brand=bpy.data.materials.get('STUDY | landmark brand cyan')
if not brand:
 brand=bpy.data.materials.new('Hero | brand cyan foliage');brand.use_nodes=True;p=brand.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(0,.40724,.75294,1);p.inputs['Roughness'].default_value=.8;brand.diffuse_color=(0,.40724,.75294,1)
else:
 brand=brand.copy();brand.name='Hero | brand cyan foliage';p=brand.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.8;p.inputs['Metallic'].default_value=0;p.inputs['Coat Weight'].default_value=0
selected=[]
for o in S.objects:
 if not o.name.startswith('WC |') or o.hide_render:continue
 if int(hashlib.sha256(('PNP-leaf-20261102'+o.name).encode()).hexdigest()[:8],16)%100>=35:continue
 assert len(o.material_slots)==2
 o.material_slots[1].link='OBJECT';o.material_slots[1].material=brand;selected.append(o.name)
assert all(hashed(curves(bpy.data.actions[n]))==h for n,h in untouched.items())
assert hashed(presentation())==present
S.frame_set(842);S['loader_revision']='slower planted gait v002';bpy.context.preferences.filepaths.save_version=0
out=R/f'hero-section-{label}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(R/f'{label}-changes.json').write_text(json.dumps(dict(source=source,source_sha256=source_sha,file=str(out),sha256=sha(out),animated_objects=sorted(names),timewarp=[(820,830),(865,853),(875,859),(910,872),(940,940)],truck_departure=[870,900],foliage_selected=selected,presentation_preserved=True,untouched_actions_preserved=True),indent=2));print('SAVED',label,'crowns',len(selected),flush=True)
