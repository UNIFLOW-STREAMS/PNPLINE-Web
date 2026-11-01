"""Source-comparative motion metrics; optional direct source handoff capture.

Run in source Blender with -- capture, or factory Blender with -- metrics.
The dense reflow samples are produced by the evaluated in-memory build audit.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[1]
REVIEW=ROOT/'review'
MODE=sys.argv[sys.argv.index('--')+1]


def norm(v):return math.sqrt(sum(x*x for x in v))
def diff(a,b):return [x-y for x,y in zip(a,b)]
def mul(q,r):
    w,x,y,z=q;a,b,c,d=r
    return [w*a-x*b-y*c-z*d,w*b+x*a+y*d-z*c,w*c-x*d+y*a+z*b,w*d+x*c-y*b+z*a]
def unit(q):
    n=norm(q);return [x/n for x in q]
def deltaq(a,b):
    a,b=unit(a),unit(b)
    if sum(x*y for x,y in zip(a,b))<0:b=[-x for x in b]
    q=mul(b,[a[0],-a[1],-a[2],-a[3]])
    if q[0]<0:q=[-x for x in q]
    length=norm(q[1:]);angle=2*math.atan2(length,q[0])
    return [math.degrees(angle)*v/length for v in q[1:]]if length>1e-12 else[0,0,0]


def metrics(rows,step):
    dt=step/30
    velocity=[[v/dt for v in diff(b['eye'],a['eye'])]for a,b in zip(rows,rows[1:])]
    acceleration=[[v/dt for v in diff(b,a)]for a,b in zip(velocity,velocity[1:])]
    jerk=[[v/dt for v in diff(b,a)]for a,b in zip(acceleration,acceleration[1:])]
    angular=[[v/dt for v in deltaq(a['q'],b['q'])]for a,b in zip(rows,rows[1:])]
    aa=[[v/dt for v in diff(b,a)]for a,b in zip(angular,angular[1:])]
    aj=[[v/dt for v in diff(b,a)]for a,b in zip(aa,aa[1:])]
    result={}
    for key,values,skip in [('speed_m_s',velocity,1),('acceleration_m_s2',acceleration,2),('jerk_m_s3',jerk,3),
                          ('angular_speed_deg_s',angular,1),('angular_acceleration_deg_s2',aa,2),('angular_jerk_deg_s3',aj,3)]:
        magnitudes=[norm(v)for v in values]
        if not magnitudes:continue
        i=max(range(len(magnitudes)),key=magnitudes.__getitem__)
        result[key]={'max':magnitudes[i],'frame':rows[i+skip]['frame']}
    result['max_position_step_m']=max(norm(diff(b['eye'],a['eye']))for a,b in zip(rows,rows[1:]))
    result['max_angle_step_deg']=max(norm(deltaq(a['q'],b['q']))for a,b in zip(rows,rows[1:]))
    return result


if MODE=='capture':
    scene=bpy.context.scene
    rows=[]
    for tick in range(253*8,257*8+1):
        frame=tick/8;scene.frame_set(int(frame),subframe=frame%1)
        row={'frame':frame}
        for label,name in [('camera','CAM_MASTER'),('ship','A02_SHIP')]:
            m=scene.objects[name].matrix_world
            row[label]={'frame':frame,'eye':list(m.translation),'q':list(m.to_quaternion())}
        rows.append(row)
    (REVIEW/'animation-source-handoff-dense.json').write_text(json.dumps(rows),encoding='utf-8')
    print('HANDOFF_SOURCE_CAPTURED',len(rows),flush=True)
elif MODE=='metrics':
    samples=json.loads((REVIEW/'animation-reflow-camera-samples.json').read_text())
    source=json.loads((REVIEW/'animation-reflow-source.json').read_text())
    extra=json.loads((REVIEW/'animation-source-handoff-dense.json').read_text())
    camera=[{'frame':r['frame'],'eye':r['eye'],'q':r['q']}for r in samples]
    old_camera=[{'frame':r['frame'],'eye':r['source_eye'],'q':r['source_q']}for r in samples]
    ship=[{'frame':r['frame'],'eye':r['ship_eye'],'q':r['ship_q']}for r in samples]if 'ship_eye'in samples[0]else[]
    old_ship=[{'frame':r['frame'],'eye':r['source_ship_eye'],'q':r['source_ship_q']}for r in samples]if ship else[]
    for row in extra:
        if row['frame']>253:
            camera.append(row['camera']);old_camera.append(row['camera'])
            if ship:ship.append(row['ship']);old_ship.append(row['ship'])
    output={'source_sha256':source['source_sha256'],'boundaries':{},'measurement_note':'Both 1/8-frame raw derivatives and native-frame derivatives are reported. The raw values amplify float32 transform quantization; native-frame comparison is the more stable visual-jitter indicator.'}
    for boundary in [75,108,165,246,253]:
        select=lambda rows:[r for r in rows if boundary-4<=r['frame']<=boundary+4]
        dense=select(camera);old=select(old_camera)
        native=[r for r in dense if r['frame'].is_integer()];native_old=[r for r in old if r['frame'].is_integer()]
        output['boundaries'][str(boundary)]={'camera_dense':metrics(dense,.125),'source_camera_dense':metrics(old,.125),
                                           'camera_native':metrics(native,1),'source_camera_native':metrics(native_old,1)}
        if ship:
            dense=select(ship);old=select(old_ship)
            native=[r for r in dense if r['frame'].is_integer()];native_old=[r for r in old if r['frame'].is_integer()]
            output['boundaries'][str(boundary)].update({'ship_dense':metrics(dense,.125),'source_ship_dense':metrics(old,.125),
                                                      'ship_native':metrics(native,1),'source_ship_native':metrics(native_old,1)})
    (REVIEW/'animation-motion-review.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print('CAMERA_JOIN_METRICS',json.dumps({k:{'new':v['camera_native'],'source':v['source_camera_native']}for k,v in output['boundaries'].items()}),flush=True)
