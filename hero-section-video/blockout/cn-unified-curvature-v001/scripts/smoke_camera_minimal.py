"""Evaluate a camera patch in a minimal dependency-complete scene; never save."""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import animation_reflow
s=bpy.context.scene
keep=set()
for name in('CAM_MASTER','CAM_LOOK_TARGET','A02_SHIP','CNC_BERTH_REFLOW','SF_CN_LAYOUT'):
    o=s.objects[name]
    while o:
        keep.add(o.name);o=o.parent
bpy.data.batch_remove(ids=[o for o in bpy.data.objects if o.name not in keep])
print('MINIMAL_CAMERA_DEPENDENCIES',len(keep),sorted(keep),flush=True)
animation_reflow.refine_camera_reflow(s)
