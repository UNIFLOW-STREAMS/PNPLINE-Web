import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene;cam=S.camera
colliders=[o for o in S.objects if o.type=='MESH' and o.name!='EARTH_CONTINUOUS_OCEAN' and not o.name.startswith('WAKE_')]
hits=[];last=None;maxstep=0;maxangle=0;clearance=1e9
for f4 in range(0,645):
    t=f4/4;S.frame_set(int(t),subframe=t-int(t));p=cam.matrix_world.translation.copy();q=cam.matrix_world.to_quaternion()
    clearance=min(clearance,p.length-S['radius'])
    if last:
        maxstep=max(maxstep,(p-last[0]).length)
        maxangle=max(maxangle,math.degrees(2*math.acos(min(1,abs(q.dot(last[1]))))))
    last=p,q
    for o in colliders:
        if o.hide_render:continue
        c=o.matrix_world.inverted()@p
        if all(min(v[i] for v in o.bound_box)-.12<c[i]<max(v[i] for v in o.bound_box)+.12 for i in range(3)):hits.append({'frame':t,'object':o.name})
result={'quarter_frame_samples':645,'range':[0,161],'camera_obb_hits':hits,'minimum_globe_clearance':clearance,'max_quarter_frame_step':maxstep,'max_quarter_frame_rotation_deg':maxangle,'method':'Camera point against local mesh boxes expanded .12; not exact continuous mesh collision'}
(ROOT/'review/motion-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2));assert not hits;assert clearance>0
