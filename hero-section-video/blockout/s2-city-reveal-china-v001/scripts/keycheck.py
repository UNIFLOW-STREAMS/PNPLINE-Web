import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));out={}
 for name in ['CAM_MASTER','CAM_LOOK_TARGET']:
  obj=bpy.data.objects[name]
  for l in obj.animation_data.action.layers:
   for st in l.strips:
    for b in st.channelbags:
     for fc in b.fcurves:
      for k in fc.keyframe_points:
       if 97<k.co.x<215 and fc.data_path in ['location','rotation_quaternion']:continue
       out[(name,fc.data_path,fc.array_index,float(k.co.x))]=[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation,k.handle_left_type,k.handle_right_type]
 return out
base=read(R/'inputs/base.blend');candidate=read(Path(sys.argv[-1]));diff=[{'key':k,'base':v,'candidate':candidate.get(k)} for k,v in base.items() if candidate.get(k)!=v]
(R/'review/keycheck.json').write_text(json.dumps({'difference_count':len(diff),'differences':diff[:20]},indent=2));print('KEY_DIFF',len(diff))
if diff:raise SystemExit(1)
