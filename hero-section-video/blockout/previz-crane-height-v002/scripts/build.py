"""Wind in S1 starting ropes by 0.5m; preserve camera and all f72+ motion."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;src=Path(bpy.data.filepath)
assert hashlib.sha256(src.read_bytes()).hexdigest()=='c21292bb055930d745ad37e9a3f4f732743043d5528429c030b9f366ff6e1942'
out=R/'master-previz-crane-height-v002.blend';assert not out.exists()
s.frame_set(0);up=s.objects['SF_CN_LAYOUT'].matrix_world.to_3x3()@Vector((0,0,1))
def delta(t):
 u=max(0,min(1,t/72));return .5*(1-u*u*u*(10+u*(-15+6*u)))
def curves(o):
 a=o.animation_data
 return [f for l in a.action.layers for st in l.strips for b in st.channelbags if b.slot_handle==a.action_slot.handle for f in b.fcurves]
def offset(fc,amount):
 for k in fc.keyframe_points:
  if k.co.x>=72:continue
  d=amount*delta(k.co.x);k.co.y+=d;k.handle_left.y+=d;k.handle_right.y+=d
for n in ['A01_CONTAINER','W01_NEW_PALLET','P01_SPREADER']:
 o=s.objects[n];assert o.parent is None
 for f in curves(o):
  if f.data_path=='location':offset(f,up[f.array_index])
for o in s.objects:
 if not o.name.startswith('CR_WORKING_CABLE'):continue
 assert o.parent.name=='SF_CN_LAYOUT'
 for f in curves(o):
  if f.data_path=='location'and f.array_index==2:offset(f,.5)
  if f.data_path=='scale'and f.array_index==2:offset(f,-1)
s['crane_height_revision']='v002: S1 start cargo and internal pallet +0.5m; rope 0.70m to0.20m; camera unchanged; f72 landing unchanged'
s.frame_set(0);bpy.ops.wm.save_as_mainfile(filepath=str(out))
(R/'delivery.json').write_text(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'additional_start_lift_m':.5,'landing_frame':72,'status':'Verification pending'},indent=2))
