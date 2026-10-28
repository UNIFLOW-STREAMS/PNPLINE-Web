import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;cam=s.camera;t=s.objects['CAM_LOOK_TARGET']
rows={};cn=s.objects['CN_FRAME'].matrix_world.copy();inv=cn.inverted()
for f in range(0,1393):
 s.frame_set(f)
 rows[f]={'p':list(inv@cam.matrix_world.translation),'t':list(inv@t.matrix_world.translation),'q':list(cam.rotation_quaternion),'world_p':list(cam.location),'world_t':list(t.location),'lens':cam.data.lens,'ship':list(inv@s.objects['A02_SHIP'].matrix_world.translation)}
details={'scene':s.name,'objects':len(s.objects),'camera_parent':str(cam.parent),'target_parent':str(t.parent),'camera_constraints':[c.type for c in cam.constraints],'camera_rotation_mode':cam.rotation_mode,'cn':list(map(list,cn)),'names':sorted(s.objects.keys()),'camera_actions':{},'frames':rows}
for o in [cam,t]:
 details['camera_actions'][o.name]=[[fc.data_path,fc.array_index,len(fc.keyframe_points),[(float(k.co.x),k.interpolation) for k in fc.keyframe_points if 94<=k.co.x<=99 or 214<=k.co.x<=218]] for l in o.animation_data.action.layers for st in l.strips for b in st.channelbags for fc in b.fcurves]
(R/'review/baseline.json').write_text(json.dumps(details,indent=2))
print('BASELINE',len(s.objects),cam.rotation_mode,len(cam.constraints),str(cam.parent),str(t.parent))
print([n for n in s.objects.keys() if n.startswith('CN_LM_SPHERE')])
