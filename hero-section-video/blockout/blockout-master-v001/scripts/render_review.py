import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
S=bpy.context.scene
main=S.camera
frames=[1,60,84,96,160,216,275,325,380,420,456,510,552,580,632,648,710,760,810,842,872,900,935,966,1015,1060,1105,1158,1200,1260,1320,1392]
if '--' in sys.argv:
    args=sys.argv[sys.argv.index('--')+1:]
    if args:frames=[int(x) for x in args[0].split(',')]
S.render.resolution_x=960;S.render.resolution_y=540
S.render.image_settings.file_format='PNG'
for f in frames:
    S.frame_set(f);S.camera=main
    S.render.filepath=str(ROOT/'review'/f'main-f{f:04}.png')
    bpy.ops.render.render(write_still=True)

if len(frames)>15:
    data=bpy.data.cameras.new('REVIEW_ONLY_LENS');data.type='ORTHO';data.ortho_scale=80;data.clip_end=2000
    cam=bpy.data.objects.new('REVIEW_ONLY_CAMERA',data);S.collection.objects.link(cam)
    U=bpy.data.objects['US_FRAME'].matrix_world
    C=bpy.data.objects['CN_FRAME'].matrix_world
    def shot(name,f,p,t,scale,frame=None,guides=True):
        S.frame_set(f);data.ortho_scale=scale
        p=Vector(p);t=Vector(t)
        up=Vector((0,0,1))
        if frame is not None:p=frame@p;t=frame@t;up=frame.to_3x3()@up
        z=(p-t).normalized();x=up.cross(z).normalized()
        if x.length<.1:x=Vector((1,0,0))
        y=z.cross(x).normalized();m=Matrix((x,y,z)).transposed().to_4x4();m.translation=p;cam.matrix_world=m
        S.camera=cam;bpy.data.collections['08_REVIEW_GUIDES'].hide_render=not guides
        S.render.filepath=str(ROOT/'review'/f'{name}-f{f:04}.png');bpy.ops.render.render(write_still=True)
    shot('world-layout',325,(420,-540,480),(0,0,25),560)
    shot('china-departure',160,(32,-55,45),(0,10,2),66,C)
    shot('us-network',1200,(104,-57,90),(48,25,3),135,U)
    shot('warehouse-layout',1060,(54,-7,58),(52,31,2),43,U)
    for f in [710,760,810,842,872,900]:
        shot('S5-yard-top',f,(27,23,90),(27,23.001,0),60,U)
        shot('S5-yard-side',f,(31,0,7),(31,29,3),42,U)
    bpy.data.collections['08_REVIEW_GUIDES'].hide_render=True
    for f in [96,216,456,648,900,1200]:
        for delta in [-1,0,1]:
            S.frame_set(f+delta);S.camera=main
            S.render.filepath=str(ROOT/'review'/f'boundary-{f}-f{f+delta:04}.png');bpy.ops.render.render(write_still=True)
print('REVIEW_RENDERED',len(frames),'main frames')
# Keep a following CLI -a render on the saved main camera, resolution and path.
S.camera=main
S.render.resolution_x=768;S.render.resolution_y=432
S.render.filepath=str(ROOT/'preview'/'frames'/'frame-')
bpy.data.collections['08_REVIEW_GUIDES'].hide_render=True
