import bpy,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];cfg=json.loads((R/'config.json').read_text())
data={}
for kind,path in [('before',(R/cfg['source']).resolve()),('after',R/cfg['output'])]:
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;cam=s.camera;truck=s.objects['A01_CONTAINER']
    port=(s.objects['US_FRAME'].matrix_world.to_quaternion()@Vector((0,0,1))).normalized()
    wh=(s.objects['CV_WH_US_FRAME'].matrix_world.to_quaternion()@Vector((0,0,1))).normalized()
    def ease(t):
        t=max(0,min(1,t));return t*t*t*(10+t*(-15+6*t))
    rows=[]
    for tick in range(420*2,641*2+1):
        f=tick/2;s.frame_set(int(f),subframe=f%1);q=cam.matrix_world.to_quaternion();eye=cam.matrix_world.translation
        up=port.lerp(wh,ease((f-460)/50)).normalized()
        roll=math.degrees(math.atan2(up.dot(q@Vector((1,0,0))),up.dot(q@Vector((0,1,0)))))
        screen=world_to_camera_view(s,cam,truck.matrix_world.translation)
        rows.append({'frame':f,'eye':list(eye),'q':list(q),'roll':roll,'screen':list(screen)})
    p=np.array([r['eye'] for r in rows]);f=np.array([r['frame'] for r in rows]);v=np.diff(p,axis=0)*2;a=np.diff(v,axis=0)*2;j=np.diff(a,axis=0)*2
    def stats(values,offset):
        mask=(f[offset:offset+len(values)]>=467)&(f[offset:offset+len(values)]<=565)
        return {'max':float(np.max(np.linalg.norm(values[mask],axis=1))),'mean':float(np.mean(np.linalg.norm(values[mask],axis=1)))}
    angular=[]
    for r,t in zip(rows,rows[1:]):
        from mathutils import Quaternion
        q1,q2=Quaternion(r['q']),Quaternion(t['q'])
        angular.append(math.degrees(2*math.acos(min(1,abs(q1.dot(q2)))))*2)
    core=[r for r in rows if 467<=r['frame']<=565]
    report={'speed_units_per_frame':stats(v,0),'acceleration':stats(a,1),'jerk':stats(j,1),
        'peak_angular_deg_per_frame':max(x for x,r in zip(angular,rows) if 467<=r['frame']<=565),
        'peak_roll_deg':max(abs(r['roll']) for r in core),
        'screen_x_range':[min(r['screen'][0] for r in core),max(r['screen'][0] for r in core)],
        'screen_y_range':[min(r['screen'][1] for r in core),max(r['screen'][1] for r in core)]}
    data[kind]={'metrics':report,'rows':rows}
    print(kind,json.dumps(report,indent=2),flush=True)
(R/'review/motion.json').write_text(json.dumps(data,indent=2))
