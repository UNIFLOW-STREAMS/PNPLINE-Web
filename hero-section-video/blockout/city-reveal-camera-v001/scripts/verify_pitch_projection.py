"""Verify optical correction without changing physical eye path or focal length."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];candidate=Path(bpy.data.filepath)
def capture():
 s=bpy.context.scene;c=s.camera
 action=c.data.animation_data.action
 keys=[(fc.data_path,fc.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in fc.keyframe_points]) for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
 points={};outside={}
 for f in range(440,649):
  s.frame_set(f);points[f]=list(c.matrix_world.translation)
 for f in [0,408,439,439.5,440,648,648.5,649,672,900,1392]:
  s.frame_set(int(f),subframe=f%1);outside[f]=(c.data.lens,c.data.shift_x,c.data.shift_y)
 return keys,points,outside
after=capture();bpy.ops.wm.open_mainfile(filepath=str(R/'candidate-city-reveal-v004.blend'));before=capture()
eye_error=max(abs(a-b) for f in after[1] for a,b in zip(after[1][f],before[1][f]))
projection_error=max(abs(a-b) for f in after[2] for a,b in zip(after[2][f],before[2][f]))
result={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'focal_length_action_unchanged':after[0]==before[0],'max_eye_position_error_vs_v004':eye_error,'max_projection_error_outside_window':projection_error}
(R/'review'/f'{candidate.stem}-projection-preservation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert result['focal_length_action_unchanged'] and eye_error<1e-4 and projection_error<1e-6
