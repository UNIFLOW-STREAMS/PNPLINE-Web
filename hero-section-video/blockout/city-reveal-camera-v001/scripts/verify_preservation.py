"""Compare source and candidate; only the two camera-parent relationships may change."""
import bpy,sys,json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];file=Path(bpy.data.filepath)
helpers=(R.parent/'curvature-rework-v001/scripts/audit_preservation.py').read_text().split("if __name__=='__main__':")[0]
exec(compile(helpers,'existing-preservation-helpers','exec'))
candidate=file;allowed={'CAM_MASTER','CAM_LOOK_TARGET'}
def evaluated():
 s=bpy.context.scene;camera={};objects={}
 for f in [0,1,380,408,439,439.5,440,648,648.5,649,672,900,1392]:
  s.frame_set(int(f),subframe=f%1);camera[f]=[float(v) for n in allowed for row in s.objects[n].matrix_world for v in row]
 for f in [479,509,600]:
  s.frame_set(f);objects[f]=digest({o.name:list(map(list,o.matrix_world)) for o in s.objects if o.name not in allowed and not o.name.startswith('CR_REVEAL_')})
 return camera,objects
after=snap();ac,ao=evaluated()
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'curvature-rework-v001/candidate-curvature-v004.blend'));before=snap();bc,bo=evaluated()
diff={'protected_objects':[n for n,v in before['objects'].items() if n not in allowed and after['objects'].get(n)!=v], 'source_actions':[n for n,v in before['actions'].items() if after['actions'].get(n)!=v], 'source_geometry':[n for n,v in before['geometry'].items() if after['geometry'].get(n)!=v],'source_materials':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'evaluated_non_camera':ao!=bo}
for k in ['world','timeline','view','camera']:diff[k]=after[k]!=before[k]
camera_error=max(abs(a-b) for f in bc for a,b in zip(ac[f],bc[f]));diff['outside_window_camera']=camera_error>1e-4
result={'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'protected_objects':len(before['objects'])-2,'camera_max_error_outside_window':camera_error,'differences':diff}
(R/'review'/f'{candidate.stem}-preservation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert not any(bool(v) for v in diff.values())
