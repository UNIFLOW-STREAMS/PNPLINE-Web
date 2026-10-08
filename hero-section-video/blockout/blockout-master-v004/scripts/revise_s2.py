"""Two bounded camera alternatives; never regenerate or change scene assets.
limited: integrated boundary-preserving revision.
candidate: historical S2-only ending proposal with an unjoined S3.
integrated: user-approved B23 and S3 join, f217..251, original from f252.
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];S=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'inputs/base-v003.blend').resolve()
mode=sys.argv[sys.argv.index('--')+1]
assert mode in ['limited','candidate','integrated']
base=json.loads((ROOT/'review/baseline-full.json').read_text())['frames']
cam=S.camera;target=bpy.data.objects['CAM_LOOK_TARGET']
def local(f,key):return Matrix(base[f]['ship']).inverted()@(Matrix(base[f]['camera']).translation if key=='p' else Vector(base[f]['target']))
end=215 if mode=='limited' else 216
frames=[97,124,148,180,end]
points=[local(97,'p'),Vector((4,-10.8,7)),Vector((2,-13,8)),Vector((-8,-20,12) if mode=='limited' else (-8,-13,8.5)),local(end,'p') if mode=='limited' else Vector((-17,-10,8))]
targets=[local(97,'t'),Vector((.6,-.7,3.6)),Vector((.1,0,3.7)),Vector((1,0,2.8)),local(end,'t') if mode=='limited' else Vector((-1.5,0,.6))]
def derivatives(values,key):
    out=[local(97,key)-local(96,key)]
    for i in range(1,len(frames)-1):out.append((values[i+1]-values[i-1])/(frames[i+1]-frames[i-1]))
    out.append((local(216,key)-local(214,key))/2 if mode=='limited' else (values[-1]-values[-2])/(frames[-1]-frames[-2])*.35)
    return out
dp=derivatives(points,'p');dt=derivatives(targets,'t')
def evaluate(values,deriv,f):
    i=next(i for i in range(len(frames)-1) if frames[i]<=f<=frames[i+1])
    span=frames[i+1]-frames[i];u=(f-frames[i])/span
    return (2*u**3-3*u*u+1)*values[i]+(u**3-2*u*u+u)*span*deriv[i]+(-2*u**3+3*u*u)*values[i+1]+(u**3-u*u)*span*deriv[i+1]
S.frame_set(97);prev=cam.rotation_quaternion.copy()
for f in range(98,215 if mode=='limited' else 217):
    S.frame_set(f);ship=bpy.data.objects['A02_SHIP'].matrix_world.copy()
    p=ship@evaluate(points,dp,f);t=ship@evaluate(targets,dt,f)
    up=ship.to_3x3()@Vector((0,0,1));z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized()
    q=Matrix((x,y,z)).transposed().to_quaternion()
    if q.dot(prev)<0:q.negate()
    cam.location=p;cam.rotation_quaternion=q;target.location=t
    cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f);target.keyframe_insert('location',frame=f);prev=q.copy()
if mode=='integrated':
    # Approval: user explicitly accepted the proposed f216..251 camera/target
    # changes. Preserve the accepted S2 curve exactly and join in world space.
    start=[]
    for f in [215,216]:
        S.frame_set(f);start.append((cam.matrix_world.translation.copy(),target.matrix_world.translation.copy()))
    p0,t0=start[1];vp=p0-start[0][0];vt=t0-start[0][1]
    p1=Matrix(base[252]['camera']).translation;t1=Vector(base[252]['target'])
    ep=(Matrix(base[253]['camera']).translation-Matrix(base[251]['camera']).translation)/2
    et=(Vector(base[253]['target'])-Vector(base[251]['target']))/2
    def join(a,b,va,vb,u):return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*36*va+(-2*u**3+3*u*u)*b+(u**3-u*u)*36*vb
    for f in range(217,252):
        S.frame_set(f);u=(f-216)/36
        p=join(p0,p1,vp,ep,u);t=join(t0,t1,vt,et,u)
        up=bpy.data.objects['A02_SHIP'].matrix_world.to_3x3()@Vector((0,0,1))
        z=(p-t).normalized();x=up.cross(z).normalized();y=z.cross(x).normalized();q=Matrix((x,y,z)).transposed().to_quaternion()
        if q.dot(prev)<0:q.negate()
        cam.location=p;cam.rotation_quaternion=q;target.location=t
        cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_quaternion',frame=f);target.keyframe_insert('location',frame=f);prev=q.copy()
for obj in [cam,target]:
    for layer in obj.animation_data.action.layers:
      for strip in layer.strips:
       for bag in strip.channelbags:
        for fc in bag.fcurves:
         for kp in fc.keyframe_points:
          if 98<=kp.co.x<=(214 if mode=='limited' else 251 if mode=='integrated' else 216):kp.interpolation='LINEAR'
S['master_version']='v004';S['camera_revision']='S2 bounded camera revision: '+mode
S['generator']='scripts/revise_s2.py '+mode+' applied to inputs/base-v003.blend'
S['source_basis']='Saved v003 ae1a8ea2dfbf8127b27ecd9ad999589575e87aac9eb578c970fd812e7063964e; S2 boards 01-05 and supplied Bandicam recording reviewed; see report-s2-camera.md for limitations'
S['camera_guide_warning']='Existing CAMERA_PATH is the preserved pre-v004 guide; use review/camera-path-top.png for revised paths. Viewport overlays are hidden.'
S['s2_acceptance']='LIMITED: B23 retained; close K5 unmet' if mode=='limited' else 'APPROVED camera integration: close K5 and S3 join through f251; proxy-model differences remain' if mode=='integrated' else 'HISTORICAL S2 PROPOSAL: S3 join not applied in this file; use master-v004.blend'
S.name='PNPLINE_MASTER_v004' if mode=='integrated' else 'PNPLINE_LIMITED_v004' if mode=='limited' else 'PNPLINE_S2_CANDIDATE_v004'
S.frame_set(96)
if mode=='integrated':
    S.use_preview_range=True;S.frame_preview_start=84;S.frame_preview_end=276
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
   area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
name='master-v004.blend' if mode=='integrated' else 'limited-v004.blend' if mode=='limited' else 's2-target-candidate-v004.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/name))
(ROOT/'review'/('path-'+mode+'.json')).write_text(json.dumps({'mode':mode,'frames':frames,'camera':[list(v) for v in points],'target':[list(v) for v in targets],'position_derivatives':[list(v) for v in dp],'target_derivatives':[list(v) for v in dt],'changed_frames':[98,214 if mode=='limited' else 251 if mode=='integrated' else 216],'space':'S2 evaluated ship local; integrated join is world Hermite 216..252','guide':'Existing CAMERA_PATH is preserved unchanged; use separate review plots for the revised path.'},indent=2))
