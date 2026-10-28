import bpy,sys,json,hashlib,time,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for variant in sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['A','B']:
 path=R/f'master-motion-polish-{variant}.blend';validation=json.loads((R/'review'/f'validation-{variant}.json').read_text())
 assert validation['pass_all'] and validation['blend_sha256']==sha(path),'Render only the validated final version'
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 run=uuid.uuid4().hex[:12];folder=R/f'frames-{variant}'/run;folder.mkdir(parents=True)
 rec={'variant':variant,'run_id':run,'status':'rendering','blend_path':str(path),'blend_sha256':sha(path),'script_sha256':sha(__file__),'config_sha256':sha(R/'config.json'),'validation_sha256':sha(R/'review'/f'validation-{variant}.json'),'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'fps_base':s.render.fps_base,'frame_start':s.frame_start,'frame_end':s.frame_end,'output_dir':str(folder),'images':[]}
 record=R/f'render-record-{variant}.json';started=time.time()
 for f in range(s.frame_start,s.frame_end+1):
  s.frame_set(f);image=folder/f'{f:04d}.png';s.render.filepath=str(image);bpy.ops.render.render(write_still=True)
  rec['images'].append({'frame':f,'sha256':sha(image)})
  if f%48==0:
   record.write_text(json.dumps(rec,indent=2),encoding='utf8');print('RENDER_PROGRESS',variant,f,s.frame_end,flush=True)
 rec['status']='complete';rec['elapsed_seconds']=time.time()-started
 assert rec['blend_sha256']==sha(path)
 record.write_text(json.dumps(rec,indent=2),encoding='utf8');print('RENDERED',variant,flush=True)
