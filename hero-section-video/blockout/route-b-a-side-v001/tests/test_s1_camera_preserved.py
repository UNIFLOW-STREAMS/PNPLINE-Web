import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;before=[]
for f in range(73):s.frame_set(f);before.append(s.camera.matrix_world.copy())
candidate=bpy.data.filepath;bpy.ops.wm.open_mainfile(filepath=str(R/'inputs/base.blend'));s=bpy.context.scene;error=0
for f,m in enumerate(before):
 s.frame_set(f);error=max(error,max(abs(m[i][j]-s.camera.matrix_world[i][j])for i in range(4)for j in range(4)))
tag=Path(candidate).stem
(R/'review'/f'{tag}-s1-camera.json').write_text(json.dumps({'file':candidate,'max_error':error,'pass':error<.0001},indent=2));print(error);assert error<.0001,'S1 close camera should not orbit when only the city reveal needs retargeting'
