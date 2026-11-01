"""Render matching China expansion diagnostics or the unchanged scene camera.

Never saves the loaded blend. Diagnostic cameras exist only in this process.

Examples (run through Blender --background FILE --python render_review.py --):
  after --views overview,top,beijing,guangzhou --width 1600
  before --views overview,top,beijing,guangzhou --width 1600
  after --actual --width 1600
  after --actual --frames 0,57,96,132,165,185,210,253,315,390,530,720,989

Use the same script/options against the integrated source and the expansion
candidate for geometric before/after comparisons. Poses are fixed in the
SF_CN_LAYOUT frame, independent of the source's object count or bounding box.
"""
import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_FRAMES=[0,57,96,132,165,185,210,253,315,390,530,720,989]
VIEWS={
    'hero':{'bounds':[[-66,65],[-22,73],[-27,27]],'direction':[.6,-1.4,1.65],
            'margin':1.02,'description':'Final high-angle China expansion hero, matched before/after'},
    'overview':{'bounds':[[-67,66],[-39,73],[-27,42]],'direction':[1.0,-1.65,1.12],
                'margin':1.055,'description':'Expanded China city and front harbor, local front-right view'},
    'top':{'bounds':[[-67,66],[-39,73],[-27,42]],'direction':[0,0,1],
           'margin':1.045,'description':'China local XY plan; north/back is upward'},
    'beijing':{'bounds':[[-62,-26],[-11,56],[-22,29]],'direction':[-1.15,-1.55,1.15],
               'margin':1.07,'description':'West Beijing district from local front-left'},
    'guangzhou':{'bounds':[[27,66],[0,56],[-22,31]],'direction':[1.25,-1.55,1.10],
                 'margin':1.07,'description':'East Guangzhou district from local front-right'},
    'beijing_rear':{'bounds':[[-65,-25],[24,71],[-27,25]],'direction':[-1.1,1.45,1.2],
                    'margin':1.06,'description':'Rear west hills, Great Wall and stadium; supplemental occlusion check'},
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def camera_state(camera):
    data=camera.data
    return {'name':camera.name,'matrix_world':[list(row)for row in camera.matrix_world],
            'lens':data.lens,'type':data.type,'ortho_scale':data.ortho_scale,
            'shift_x':data.shift_x,'shift_y':data.shift_y,
            'sensor_fit':data.sensor_fit,'sensor_width':data.sensor_width,'sensor_height':data.sensor_height,
            'clip_start':data.clip_start,'clip_end':data.clip_end}


def diagnostic_camera(scene,name,definition,aspect):
    frame=scene.objects['SF_CN_LAYOUT'].matrix_world.copy()
    bounds=definition['bounds']
    center=Vector([(lo+hi)/2 for lo,hi in bounds])
    backward=Vector(definition['direction']).normalized()
    up_hint=Vector((0,1,0)) if name=='top' else Vector((0,0,1))
    right=(-backward).cross(up_hint).normalized()
    up=right.cross(-backward).normalized()
    points=[Vector(p) for p in itertools.product(*bounds)]
    horizontal=[(p-center).dot(right) for p in points]
    vertical=[(p-center).dot(up) for p in points]
    width=max(horizontal)-min(horizontal)
    height=max(vertical)-min(vertical)
    horizontal_center=(max(horizontal)+min(horizontal))/2
    vertical_center=(max(vertical)+min(vertical))/2
    center+=right*horizontal_center+up*vertical_center
    eye=center+backward*260
    camera_data=bpy.data.cameras.new('__REVIEW_'+name+'_DATA')
    camera=bpy.data.objects.new('__REVIEW_'+name,camera_data)
    scene.collection.objects.link(camera)
    rotation=Matrix((right,up,backward)).transposed().to_4x4()
    rotation.translation=eye
    camera.matrix_world=frame@rotation
    camera_data.type='ORTHO'
    camera_data.sensor_fit='HORIZONTAL'
    camera_data.ortho_scale=max(width,height*aspect)*definition['margin']
    camera_data.clip_start=.1
    camera_data.clip_end=600
    camera_data.lens=50
    scene.camera=camera
    return camera,{'name':name,'description':definition['description'],
                   'local_bounds':bounds,'local_direction':definition['direction'],
                   'local_eye':list(eye),'local_target':list(center),
                   'local_up':list(up),'layout_matrix_world':[list(row)for row in frame]}


def render_settings(scene,width,height):
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.resolution_percentage=100
    scene.render.pixel_aspect_x=1
    scene.render.pixel_aspect_y=1
    scene.render.use_border=False
    scene.render.film_transparent=False
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    shading=scene.display.shading
    shading.light='STUDIO'
    shading.color_type='MATERIAL'
    shading.show_shadows=False
    shading.show_cavity=True
    shading.cavity_type='BOTH'
    shading.curvature_ridge_factor=1.25
    shading.curvature_valley_factor=1.10
    shading.show_specular_highlight=True
    shading.show_object_outline=False
    shading.background_type='WORLD'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('label',help='For example before or after')
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--views',help='Comma-separated hero,overview,top,beijing,guangzhou,beijing_rear')
    mode.add_argument('--actual',action='store_true',help='Use the existing active scene camera without changing its data')
    parser.add_argument('--frames',help='Actual camera frame numbers, comma-separated')
    parser.add_argument('--frame',type=int,default=0,help='Diagnostic view scene frame (default0)')
    parser.add_argument('--width',type=int,default=1600)
    parser.add_argument('--height',type=int,help='Default1000 for diagnostics,900 for1600 actual-camera previews')
    parser.add_argument('--expect-sha',help='Optional expected source SHA256')
    parser.add_argument('--views-config',help='Optional JSON overriding entries in VIEWS; use same file for before and after')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    assert args.label.replace('-','').replace('_','').isalnum(),'Unsafe output label'
    assert args.width>=320
    scene=bpy.context.scene
    source=Path(bpy.data.filepath)
    assert source.is_file(),'Load a source/candidate blend before executing this script'
    source_hash=sha(source)
    if args.expect_sha:
        assert args.expect_sha==source_hash,'Unexpected source hash'
    active_camera=scene.camera
    assert active_camera and active_camera.name=='CAM_MASTER','Unexpected actual camera'
    saved_frame=scene.frame_current+scene.frame_subframe
    mode_name='actual'if args.actual else'diagnostic'
    folder=ROOT/'review'/f'{args.label}-{mode_name}'
    folder.mkdir(parents=True,exist_ok=True)
    if args.actual:
        native_aspect=(scene.render.resolution_x*scene.render.pixel_aspect_x)/(scene.render.resolution_y*scene.render.pixel_aspect_y)
        height=args.height or round(args.width/native_aspect)
    else:
        height=args.height or round(args.width*.625)
    render_settings(scene,args.width,height)
    metadata={'source':str(source),'sha256':source_hash,'mode':mode_name,'label':args.label,
              'width':args.width,'height':height,'fps':scene.render.fps/scene.render.fps_base,
              'source_saved':False,'temporary_camera_only':not args.actual,
              'preview_settings':'Workbench STUDIO/material/cavity BOTH/specular; cast shadows off; production settings are untouched on disk',
              'rendered':[]}
    started=time.time()
    if args.actual:
        frames=[int(f)for f in args.frames.split(',')]if args.frames else DEFAULT_FRAMES
        assert len(frames)==len(set(frames))
        for frame in frames:
            assert scene.frame_start<=frame<=scene.frame_end
            scene.frame_set(frame)
            assert scene.camera==active_camera
            before=camera_state(active_camera)
            output=folder/f'f{frame:04d}.png'
            scene.render.filepath=str(output)
            bpy.ops.render.render(write_still=True)
            assert camera_state(active_camera)==before,'Render unexpectedly altered the actual camera'
            metadata['rendered'].append({'frame':frame,'file':str(output),'camera':before})
            print('CITY_ACTUAL_RENDERED',frame,flush=True)
    else:
        definitions=dict(VIEWS)
        if args.views_config:
            definitions.update(json.loads(Path(args.views_config).read_text(encoding='utf-8')))
        views=args.views.split(',')
        assert views and all(name in definitions for name in views)
        scene.frame_set(args.frame)
        actual_before=camera_state(active_camera)
        for name in views:
            camera,view=diagnostic_camera(scene,name,definitions[name],args.width/height)
            output=folder/f'{name}.png'
            scene.render.filepath=str(output)
            bpy.ops.render.render(write_still=True)
            view.update({'frame':args.frame,'file':str(output),'camera':camera_state(camera)})
            metadata['rendered'].append(view)
            scene.camera=active_camera
            data=camera.data
            bpy.data.objects.remove(camera,do_unlink=True)
            bpy.data.cameras.remove(data)
            assert camera_state(active_camera)==actual_before,'Diagnostic render altered CAM_MASTER'
            print('CITY_DIAGNOSTIC_RENDERED',name,flush=True)
    whole=math.floor(saved_frame)
    scene.frame_set(whole,subframe=saved_frame-whole)
    scene.camera=active_camera
    assert sha(source)==source_hash,'Source file changed during read-only review'
    metadata['elapsed_seconds']=time.time()-started
    (folder/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('CITY_REVIEW_DONE',mode_name,args.label,source_hash,flush=True)


if __name__=='__main__':
    main()
