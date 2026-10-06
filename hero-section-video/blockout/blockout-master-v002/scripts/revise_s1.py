"""Camera-only revision of the user's saved master. Never regenerate scene assets."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'inputs/base-user-saved-v001.blend'
assert Path(bpy.data.filepath).resolve()==BASE.resolve(),'Open the preserved base snapshot'
S=bpy.context.scene;cam=S.camera;target=bpy.data.objects['CAM_LOOK_TARGET']
S.frame_set(1);C=bpy.data.objects['CN_FRAME'].matrix_world.copy();Ci=C.inverted()
old={}
for f in range(0,1393):
    S.frame_set(f)
    old[f]={'camera':cam.matrix_world.copy(),'target':target.matrix_world.translation.copy(),'container':bpy.data.objects['A01_CONTAINER'].matrix_world.translation.copy()}
excluded={cam.name,target.name,'CAMERA_PATH'}
samples=[0,1,24,48,72,96,110,145,159,160,216,456,648,900,1200,1392]
def preservation_signature():
    h=hashlib.sha256()
    for f in samples:
        S.frame_set(f)
        for o in sorted(S.objects,key=lambda o:o.name):
            if o.name in excluded:continue
            h.update(o.name.encode());h.update(str(o.hide_render).encode())
            h.update(json.dumps([[round(v,5) for v in row] for row in o.matrix_world]).encode())
    return h.hexdigest()
before=preservation_signature()
def hermite(p0,p1,v0,v1,u,span):
    return (2*u**3-3*u*u+1)*p0+(u**3-2*u*u+u)*span*v0+(-2*u**3+3*u*u)*p1+(u**3-u*u)*span*v1
P0=Vector((3.6,-8.8,3.8));P1=Vector((4.5,-9.8,6.5))
V0=Vector((.01,-.003,.03));V1=Vector((.01,-.02,.04))
T1=Vector((.8,-1.25,3.05));TV1=Vector((0,0,-.05/96))
P2=Ci@old[160]['camera'].translation;T2=Ci@old[160]['target']
V2=Ci.to_3x3()@((old[161]['camera'].translation-old[159]['camera'].translation)/2)
TV2=Ci.to_3x3()@((old[161]['target']-old[159]['target'])/2)
for f in range(160):
    S.frame_set(f)
    if f<=96:
        u=f/96;p=hermite(P0,P1,V0,V1,u,96)
        t=Ci@old[f]['container'];t.z-=.05*u
    else:
        u=(f-96)/64
        p=hermite(P1,P2,V1,V2,u,64);t=hermite(T1,T2,TV1,TV2,u,64)
    cp=C@p;ct=C@t
    up=bpy.data.objects['A02_SHIP'].matrix_world.to_3x3()@Vector((0,0,1))
    z=(cp-ct).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
    m=Matrix((x,y,z)).transposed().to_4x4();m.translation=cp
    cam.matrix_world=m;cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f)
    target.location=ct;target.keyframe_insert('location',frame=f)
for obj in [cam,target]:
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for kp in fc.keyframe_points:
                        if kp.co.x<160:kp.interpolation='LINEAR'
guide=bpy.data.objects.get('CAMERA_PATH')
if guide and guide.type=='CURVE':
    points=guide.data.splines[0].points
    for point,f in zip(points,range(1,1393,6)):
        S.frame_set(f);point.co=(*cam.matrix_world.translation,1)
after=preservation_signature()
assert before==after,'Non-camera state changed'
later_error=0
for f in range(160,1393):
    S.frame_set(f)
    later_error=max(later_error,max(abs(cam.matrix_world[i][j]-old[f]['camera'][i][j]) for i in range(4) for j in range(4)),(target.matrix_world.translation-old[f]['target']).length)
assert later_error<1e-6,'Later camera changed'
S.frame_start=0;S.timeline_markers['S1'].frame=0
S['master_version']='v002';S['camera_revision']='S1 low angle at 0 to reference high angle at 96; reconnect to original camera by 160'
S['generator']='scripts/revise_s1.py, applied to inputs/base-user-saved-v001.blend'
S.name='PNPLINE_MASTER_v002'
S.render.filepath=str(ROOT/'preview/frames/frame-')
S.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'master-v002.blend'))
evidence={'version':'v002','base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'noncamera_sample_frames':samples,'noncamera_state_before':before,'noncamera_state_after':after,'later_camera_frames':[160,1392],'later_camera_max_matrix_error':later_error,'changed':'Camera and look target keys 0..159; camera guide; S1/start marker 0; version/output metadata','end_reference':'inputs/s1-end-reference.png'}
(ROOT/'review/preservation.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
print(json.dumps(evidence,indent=2))
