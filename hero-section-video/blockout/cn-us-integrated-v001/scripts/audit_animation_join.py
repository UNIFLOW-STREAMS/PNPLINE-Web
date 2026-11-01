"""Fast evaluated camera splice probe; never saves a blend file."""
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_animation_verify as verify

scene=bpy.context.scene
us=json.loads((verify.REVIEW/'animation-source-us-contract.json').read_text())
cn_path=verify.REVIEW/'animation-source-cn-contract.json'
cn=json.loads(cn_path.read_text()) if cn_path.exists() else None
rows=[]
for tick in range(1288,2057):
    frame=tick/8
    verify.set_frame(scene,frame)
    row=verify.camera_row(scene,frame)
    camera=scene.camera.matrix_world
    q=camera.to_quaternion()
    forward=q@Vector((0,0,-1))
    cam_up=q@Vector((0,1,0))
    ship=scene.objects['A02_SHIP'].matrix_world
    up=ship.to_quaternion()@Vector((0,0,1))
    level=up-forward*up.dot(forward)
    if level.length>1e-8:
        level.normalize()
        row['roll_to_ship_up_deg']=math.degrees(math.atan2(forward.dot(level.cross(cam_up)),level.dot(cam_up)))
    screen=world_to_camera_view(scene,scene.camera,ship@Vector((0,0,2)))
    row['ship_screen']=list(screen)
    rows.append(row)
report={'sha256':verify.sha(bpy.data.filepath),'frames':[], 'joins':{}}
for frame in [165,175,185,195,210,225,235,245,253]:
    report['frames'].append(next(r for r in rows if r['frame']==frame))
for boundary in [165,253]:
    select=lambda rr:[r for r in rr if boundary-4<=r['frame']<=boundary+4]
    report['joins'][str(boundary)]={'integrated':verify.motion(select(rows)),
                                  'us':verify.motion(select(us['dense']))}
    if cn:report['joins'][str(boundary)]['cn']=verify.motion(select(cn['dense']))
(verify.REVIEW/'animation-join-probe.json').write_text(json.dumps(report,indent=2))
print('JOIN_PROBE',json.dumps({'frames':[{k:r[k] for k in ['frame','roll_to_ship_up_deg','ship_screen']} for r in report['frames']],
                              'joins':report['joins']}),flush=True)
