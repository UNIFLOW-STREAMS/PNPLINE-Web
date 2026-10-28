"""Original12fps ->42fps: preserve all1,393 poses from validated motion A."""
import bpy,sys,json,hashlib,time,array
from pathlib import Path
R=Path(__file__).resolve().parent
BASE=R.parent/'previz-motion-polish-v001'
SOURCE=BASE/'master-motion-polish-A.blend'
OUT=R/'master-previz-s1-s7-3p5x-v001.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mode=sys.argv[sys.argv.index('--')+1]
validation=json.loads((BASE/'review/validation-A.json').read_text())
assert validation['pass_all'] and sha(SOURCE)==validation['blend_sha256']
def poses(scene):
 digest=hashlib.sha256();names=sorted(scene.objects.keys())
 for frame in range(1393):
  scene.frame_set(frame)
  values=[v for n in names for row in scene.objects[n].matrix_world for v in row]+[scene.camera.data.lens]
  digest.update(array.array('f',values).tobytes())
 return digest.hexdigest()
if mode=='build':
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene
 assert s.frame_start==0 and s.frame_end==1392 and s.render.fps==24
 s.render.fps=42;s.render.fps_base=1;s.frame_step=1;s.use_preview_range=False;s.sync_mode='FRAME_DROP';s.frame_set(0)
 s.render.filepath='//frames/';s['time_map_file']='//time-map-3p5x.json';s['preview_speed']='3.5x original12fps; 1.75x validated motion A24fps'
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
 tm=json.loads((BASE/'time-map-A.json').read_text());tm.update(variant='3p5x from A',fps=42,blend_sha256=sha(OUT),motion_A_sha256=sha(SOURCE),duration=1393/42)
 for row in tm['rows']:row['output_second']=row['output_frame']/42
 for row in tm['events'].values():row['output_second']=row['output_frame']/42
 (R/'time-map-3p5x.json').write_text(json.dumps(tm,indent=2),encoding='utf8')
 (R/'build-record.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':sha(SOURCE),'output':str(OUT),'blend_sha256':sha(OUT),'script_sha256':sha(__file__),'original_fps':12,'source_fps':24,'output_fps':42,'frame_count':1393,'duration':1393/42},indent=2),encoding='utf8')
 print('BUILT',str(OUT),1393/42,flush=True)
elif mode=='render':
 record=json.loads((R/'build-record.json').read_text());assert record['blend_sha256']==sha(OUT)
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));before=poses(bpy.context.scene)
 bpy.ops.wm.open_mainfile(filepath=str(OUT));s=bpy.context.scene;after=poses(s)
 assert before==after,'Changed actor/camera poses'
 assert s.render.fps==42 and s.render.fps_base==1 and s.frame_start==0 and s.frame_end==1392
 record.update(status='rendering',pose_digest=after,all_1393_poses_equal=True,engine=s.render.engine,resolution=[s.render.resolution_x,s.render.resolution_y],images=[])
 folder=R/'frames';folder.mkdir(exist_ok=True);started=time.time()
 for f in range(1393):
  s.frame_set(f);p=folder/f'{f:04d}.png';s.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  record['images'].append({'frame':f,'sha256':sha(p)})
  if f%96==0:
   (R/'render-record.json').write_text(json.dumps(record,indent=2),encoding='utf8');print('PROGRESS',f,1392,flush=True)
 assert sha(SOURCE)==record['source_sha256'] and sha(OUT)==record['blend_sha256']
 record.update(status='complete',render_seconds=time.time()-started)
 (R/'render-record.json').write_text(json.dumps(record,indent=2),encoding='utf8')
 print('RENDER_COMPLETE',flush=True)

