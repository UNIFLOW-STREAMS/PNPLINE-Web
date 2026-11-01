"""Retime all Blender actions through one clock; keep geometry and rigs intact."""
import csv, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from timing import CONFIG,TimeMap,section_at

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
source=(ROOT/CONFIG['source']).resolve()
assert sha(source)==CONFIG['source_sha256'], 'Source changed; inspect before retiming'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene
m=TimeMap()
assert (s.frame_start,s.frame_end,s.render.fps)==(0,1392,12)
assert not bpy.app.handlers.frame_change_pre and not bpy.app.handlers.frame_change_post

for prop in bpy.data.bl_rna.properties:
    if prop.type!='COLLECTION': continue
    for block in getattr(bpy.data,prop.identifier):
        ad=getattr(block,'animation_data',None)
        if not ad: continue
        assert not ad.nla_tracks, ('Unmapped NLA',block.name)
        for fc in ad.drivers:
            assert fc.driver.expression=='offset', ('Unmapped time driver',block.name)
            assert all(v.type=='SINGLE_PROP' and all(t.id==s.objects['CR_REVEAL_CAM_MASTER'] and t.data_path in ['["lens_shift_x"]','["lens_shift_y"]'] for t in v.targets) for v in fc.driver.variables)

base=np.arange(0,989+CONFIG['sample_step']/2,CONFIG['sample_step'])
base_source=np.array([m.source(float(x)) for x in base])
mapped_keys={}
inventory=[]
for action in bpy.data.actions:
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    assert not fc.modifiers, ('Unmapped modifier',action.name,fc.data_path)
                    keys=fc.keyframe_points
                    assert not fc.sampled_points, ('Unmapped samples',action.name)
                    if not keys: continue
                    old_count=len(keys)
                    # Discrete visibility changes retain exact event positions.
                    if fc.data_path in ['hide_render','hide_viewport'] or all(k.interpolation=='CONSTANT' for k in keys):
                        for k in keys:
                            new=m.output(float(k.co.x));delta=new-k.co.x
                            k.co.x=new;k.handle_left.x+=delta;k.handle_right.x+=delta
                        fc.update()
                    else:
                        # Blender FCurve.update merges keys closer than0.01frame.
                        # Mixing warped source keys with an output grid can replace
                        # an exact output sample with a nearby source-key value.
                        # One uniform1/8-frame grid avoids that collision entirely.
                        xs=base
                        ys=np.array([fc.evaluate(float(src)) for src in base_source])
                        keep=np.ones(len(xs),dtype=bool)
                        keep[1:-1]=(ys[1:-1]!=ys[:-2])|(ys[1:-1]!=ys[2:])
                        coords=np.column_stack((xs[keep],ys[keep])).astype(np.float32).ravel()
                        keys.clear();keys.add(int(keep.sum()));keys.foreach_set('co',coords)
                        for k in keys: k.interpolation='LINEAR'
                        fc.update()
                    inventory.append([action.name,bag.slot_handle,fc.data_path,fc.array_index,old_count,len(keys)])
    print('RETIMED',action.name,flush=True)

markers=[]
for mark in s.timeline_markers:
    src=mark.frame;out=m.output(src)
    mark.frame=round(out)
    markers.append({'name':mark.name,'source_frame':src,'output_frame_exact':out,'marker_frame':mark.frame})
s.render.fps=CONFIG['fps'];s.render.fps_base=1
s.frame_start=0;s.frame_end=989;s.frame_step=1;s.use_preview_range=False
s.render.frame_map_old=100;s.render.frame_map_new=100;s.sync_mode='FRAME_DROP'
s.render.resolution_x,s.render.resolution_y=CONFIG['resolution'];s.render.resolution_percentage=100
s.render.engine='BLENDER_WORKBENCH';s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.filepath='//preview/frames/f'
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL'
s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH'
s['pacing_version']='33s-30fps-v001';s['pacing_source_sha256']=sha(source)
s['time_map_file']='//time-map.json';s['pacing_clock']='shared monotone cubic; source terminal1392 -> output989'
s.frame_set(0)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D': area.spaces.active.region_3d.view_perspective='CAMERA'
target=ROOT/CONFIG['output']
assert not target.exists(), 'Refuse to overwrite a reviewed candidate'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
mapping={'source':str(source),'source_sha256':sha(source),'output_sha256':sha(target),
    'fps':30,'frame_start':0,'frame_end':989,'frame_count':990,'duration_seconds':33,
    'terminal_pose_note':'Output989 shows source1392. It is displayed until33s;990 is the exclusive end.',
    'scroll_note':'Video progress is provided only as a media coordinate. Web scroll distance remains independently configurable.',
    'sections':[{'section':r[0],'source_start':r[1],'source_end':r[2],'output_start':r[3],'output_end_exclusive':r[4],'duration_seconds':(r[4]-r[3])/30,'description':r[5]} for r in CONFIG['sections']],
    'anchors':[{'source_frame':a[0],'output_frame':a[1]*30,'seconds':a[1],'event':a[2]} for a in CONFIG['anchors']],
    'markers':markers,
    'output_frames':[{'output_frame':f,'seconds':f/30,'source_frame':m.source(f),'section':section_at(f),'media_progress':f/989} for f in range(990)]}
(ROOT/'time-map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'frame-map.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['source_frame','output_frame','output_seconds','nearest_output_frame'])
    w.writeheader()
    for src in range(1393):
        out=m.output(src);w.writerow(dict(source_frame=src,output_frame=f'{out:.6f}',output_seconds=f'{out/30:.6f}',nearest_output_frame=round(out)))
(ROOT/'review/build.json').write_text(json.dumps({'source_sha256':sha(source),'output_sha256':sha(target),'script_sha256':sha(__file__),'config_sha256':sha(ROOT/'config.json'),'curves':inventory},indent=2))
print('SAVED',target,'curves',len(inventory),flush=True)
