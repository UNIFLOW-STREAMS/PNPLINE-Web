"""Editable dense action samples, shared time map, local C1 camera patches."""
import bpy,sys,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from motion import TimeMap,hermite,patch_tangent
from contact_repair import repair
cfg=json.loads((R/'config.json').read_text());source=R/'inputs/source.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256']
def bags(action):return [bag for l in action.layers for st in l.strips for bag in st.channelbags]
def patched(fc,f):
 if not (fc.data_path in ['location','rotation_quaternion','lens']):return fc.evaluate(f)
 for start,node,end in cfg['camera_patches']:
  if start<=f<=end:
   v0=(fc.evaluate(start+.25)-fc.evaluate(start-.25))/.5
   v1=patch_tangent(fc.evaluate(start),fc.evaluate(end),end-start)
   v2=(fc.evaluate(end+.25)-fc.evaluate(end-.25))/.5
   a,b,v,w=(start,node,v0,v1) if f<=node else (node,end,v1,v2)
   return hermite(fc.evaluate(a),fc.evaluate(b),v,w,(f-a)/(b-a),b-a)
 return fc.evaluate(f)
for variant in ['A','B']:
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 m=TimeMap(cfg['source_end'],cfg['easing'],cfg['compression_B'] if variant=='B' else [])
 assert all(not o.animation_data or (not o.animation_data.drivers and not o.animation_data.nla_tracks) for o in s.objects),'Unmapped driver or NLA'
 active=[];camera_bags=set()
 for o in list(s.objects)+[s.camera.data]:
  ad=o.animation_data
  if ad and ad.action:
   active.append(ad.action)
   if o in [s.camera,s.camera.data,s.objects['CAM_LOOK_TARGET']]:camera_bags.add((ad.action.name,ad.action_slot.handle))
 actions=sorted(set(active),key=lambda a:a.name)
 grid=set(np.arange(0,1392.00001,cfg['sample_step']).tolist())
 for action in actions:
  for bag in bags(action):
   for fc in bag.fcurves:
    grid.update(float(k.co.x) for k in fc.keyframe_points if 0<=k.co.x<=1392)
 times=np.array(sorted(grid));out_times=np.array([m.forward(t) for t in times]);inventory=[]
 for action in actions:
  for bag in bags(action):
   camera=(action.name,bag.slot_handle) in camera_bags
   for fc in bag.fcurves:
    if not fc.keyframe_points:continue
    original_count=len(fc.keyframe_points)
    if fc.data_path in ['hide_render','hide_viewport']:
     # Boolean animation retains its original transition keys and interpolation.
     for k in fc.keyframe_points:
      x=float(k.co.x)
      if 0<=x<=1392:k.co.x=m.forward(x)
     fc.update();continue
    values=np.array([patched(fc,t) if camera else fc.evaluate(t) for t in times])
    if np.ptp(values)<1e-10:indices=[0,len(times)-1]
    else:
     # Remove only interior samples of an exactly constant plateau.
     diff=np.diff(values);keep=np.ones(len(values),dtype=bool)
     keep[1:-1]=(diff[:-1]!=0)|(diff[1:]!=0);indices=np.where(keep)[0]
    coords=np.column_stack((out_times[indices],values[indices])).ravel()
    fc.keyframe_points.clear();fc.keyframe_points.add(len(indices));fc.keyframe_points.foreach_set('co',coords)
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    fc.update();inventory.append([action.name,bag.slot_handle,fc.data_path,fc.array_index,original_count,len(indices),camera])
  print('ACTION',variant,action.name,flush=True)
 # Preserve the source wheel phase and height until the contact-scope decision.
 # Failed dense-height/road proposals remain isolated in review/.
 contact=repair(s,m);max_correction=contact['max_vertical_correction_m']
 markers=[]
 for marker in s.timeline_markers:
  src=marker.frame;out=m.forward(src);marker.frame=round(out);markers.append({'name':marker.name,'source_frame':src,'exact_output_frame':out,'marker_frame':marker.frame})
 s.render.fps=24;s.render.fps_base=1;s.frame_start=0;s.frame_end=round(m.output_end);s.frame_step=1;s.use_preview_range=False;s.sync_mode='FRAME_DROP'
 s.render.resolution_x,s.render.resolution_y=cfg['resolution'];s.render.resolution_percentage=100;s.render.engine='BLENDER_WORKBENCH';s.render.use_border=False;s.render.use_crop_to_border=False
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
 s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.world.color=(.18,.18,.18)
 s['motion_polish_variant']=variant;s['source_sha256']=cfg['source_sha256'];s['time_map_file']=f'//time-map-{variant}.json'
 s.render.filepath=f'//frames-{variant}/';s.frame_set(0)
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
 path=R/f'master-motion-polish-{variant}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
 time_map={'variant':variant,'source_sha256':cfg['source_sha256'],'blend_sha256':sha(path),'fps':24,'source_fps':12,'source_end':1392,'output_end':m.output_end,'duration':(s.frame_end+1)/24,'easing':cfg['easing'],'compression':cfg['compression_B'] if variant=='B' else [],'rows':[{'source_frame':float(t),'output_frame':float(o),'output_second':float(o/24),'scroll_progress':float(o/m.output_end)} for t,o in zip(times,out_times)],'events':{k:{'source_frame':v,'output_frame':m.forward(v),'output_second':m.forward(v)/24} for k,v in cfg['events'].items()},'markers':markers}
 (R/f'time-map-{variant}.json').write_text(json.dumps(time_map,indent=2),encoding='utf8')
 (R/'review'/f'build-{variant}.json').write_text(json.dumps({'variant':variant,'source_sha256':sha(source),'blend_sha256':sha(path),'script_sha256':sha(__file__),'motion_script_sha256':sha(R/'scripts/motion.py'),'contact_script_sha256':sha(R/'scripts/contact_repair.py'),'config_sha256':sha(R/'config.json'),'wheel_correction_max_m':max_correction,'wheel_policy':'approved road/contact correction, preserve XY/rotation','contact':contact,'curves':inventory},indent=2),encoding='utf8')
 print('SAVED',variant,path,time_map['duration'],flush=True)


