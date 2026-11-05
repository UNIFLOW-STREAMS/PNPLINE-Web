import bpy,sys,json,hashlib,time,argparse,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;source=Path(bpy.data.filepath)
def sha(p):
 with open(p,'rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
p=argparse.ArgumentParser();p.add_argument('--mode',default='audit-bench');p.add_argument('--engine',default='CYCLES');p.add_argument('--samples',type=int,default=40);p.add_argument('--width',type=int,default=1920);p.add_argument('--start',type=int,default=0);p.add_argument('--end',type=int,default=989);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source_hash=sha(source);(R/'audit/source-sha.json').write_text(json.dumps(dict(source=str(source),sha256=source_hash,pid=os.getpid()),indent=2))
if a.mode=='audit-bench':
 old=json.loads((R.parents[2]/'output/scroll-previz-pacing-v001/data/source-scene.json').read_text());cfg=json.loads((R/'approved-pacing.json').read_text(encoding='utf-8'))
 info=dict(source=str(source),sha256=source_hash,camera=s.camera.name,frame_start=s.frame_start,frame_end=s.frame_end,fps=s.render.fps/s.render.fps_base,markers={m.name:m.frame for m in s.timeline_markers},view=s.view_settings.view_transform,look=s.view_settings.look,exposure=s.view_settings.exposure,engine=s.render.engine,resolution=[s.render.resolution_x,s.render.resolution_y],samples=s.cycles.samples,camera_samples=[])
 assert info['camera']=='CAM_MASTER' and info['frame_start']==0 and info['frame_end']==989 and info['fps']==30
 assert all(info['markers'][v['id']]==v['startFrame']for v in cfg['sections'])
 for f in range(990):
  s.frame_set(f);c=s.camera.evaluated_get(bpy.context.evaluated_depsgraph_get());info['camera_samples'].append(dict(frame=f,matrix=[list(row)for row in c.matrix_world],lens=c.data.lens,dof=c.data.dof.use_dof,focus_distance=c.data.dof.focus_distance,fstop=c.data.dof.aperture_fstop))
 info['approved_camera_position_max_error']=max((sum((v['matrix'][i][3]-o['position'][i])**2 for i in range(3)))**.5 for v,o in zip(info['camera_samples'],old['camera_samples']))
 (R/'audit/scene.json').write_text(json.dumps(info,indent=2));print('AUDIT',info['approved_camera_position_max_error'],flush=True)
s.render.resolution_x=a.width;s.render.resolution_y=round(a.width*9/16);s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_persistent_data=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=15
pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.035;s.cycles.adaptive_min_samples=min(16,a.samples);s.cycles.seed=29;s.cycles.use_animated_seed=False
if a.mode=='audit-bench':
 out=[]
 for engine,w,f in [('CYCLES',1920,132),('CYCLES',1920,842),('CYCLES',1280,132),('CYCLES',1280,842),('BLENDER_EEVEE',1920,132),('BLENDER_EEVEE',1920,842)]:
  s.render.engine=engine;s.render.resolution_x=w;s.render.resolution_y=round(w*9/16);s.frame_set(f);s.render.filepath=str(R/'review'/f'{engine}-{w}-f{f:04}.png');t=time.perf_counter();bpy.ops.render.render(write_still=True);out.append(dict(engine=engine,width=w,frame=f,seconds=time.perf_counter()-t,samples=a.samples));(R/'review/benchmark.json').write_text(json.dumps(out,indent=2));print('BENCH',out[-1],flush=True)
else:
 s.render.engine=a.engine;s.frame_start=a.start;s.frame_end=a.end;s.frame_step=1;s.render.filepath=str(R/'frames'/'f')
 def done(sc,*rest):
  with (R/'review/frame-times.jsonl').open('a')as log:log.write(json.dumps(dict(frame=sc.frame_current,time=time.perf_counter()))+'\n')
 bpy.app.handlers.render_post.append(done);bpy.ops.render.render(animation=True)
assert sha(source)==source_hash
print('SOURCE_UNCHANGED',source_hash,flush=True)
