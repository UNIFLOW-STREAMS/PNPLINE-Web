"""Explicit local reproduction/verification runner. Each command records its real exit code."""
import argparse,json,subprocess,sys,shutil,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());B=Path('C:/Program Files/Blender Foundation/Blender 5.1/blender.exe');S=C['scene'];source=R/'inputs/master-s4-fix.blend';dest=R/'master-s4-s5-boundary-v001.blend';p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','reproduce','before','after']);a=p.parse_args();records=[]
def run(label,args):
 start=time.time()
 with (R/'logs'/f'{label}.log').open('w',encoding='utf8') as log:r=subprocess.run([str(x) for x in args],stdout=log,stderr=subprocess.STDOUT,encoding='utf8',errors='replace')
 records.append(dict(label=label,argv=[str(x) for x in args],returncode=r.returncode,seconds=time.time()-start));(R/'logs'/f'commands-{a.stage}.json').write_text(json.dumps(records,indent=2),encoding='utf8');print(label,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
def blender(file,script,*args):return [B,'-b',file,'--python-exit-code','1','--python',R/'scripts'/script,'--',*args]
if a.stage=='verify':
 run('after-signature',blender(dest,'capture_scope.py','--scene',S,'--config',R/'config.json','--output',R/'review/after-signature.json'))
 run('after-validation',blender(dest,'validate_saved.py','--scene',S,'--config',R/'config.json','--output',R/'review/after-validation.json'))
 run('contacts',blender(dest,'capture_contacts.py','--scene',S,'--output',R/'review/contacts.json'))
 run('after-regression',[B,'-b',dest,'--python-exit-code','1','--python',R/'regression/scripts/test_scene.py'])
elif a.stage=='reproduce':
 out=R/'review/reproduced.blend'
 run('reproduce-build',blender(source,'revise_boundary.py','--input',source,'--output',out,'--config',R/'config.json','--scene',S))
 run('reproduce-signature',blender(out,'capture_scope.py','--scene',S,'--config',R/'config.json','--output',R/'review/reproduced-signature.json'))
 run('reproduce-stills',blender(out,'render_review.py','--scene',S,'--output-dir',R/'review/reopened','--frames','648,720'))
else:
 file=source if a.stage=='before' else dest;folder=R/'preview'/f'{a.stage}-frames'
 run(f'{a.stage}-sequence',blender(file,'render_review.py','--scene',S,'--output-dir',folder,'--start',C['preview_start'],'--end',C['preview_end']))
 for frame in [600,608,620,632,648,660,672,684,696,708,720,732,744,756,768,780,792]:
  shutil.copyfile(folder/f'{frame:04d}.png',R/'review'/a.stage/f'{frame:04d}.png')
 run(f'{a.stage}-encode',[shutil.which('ffmpeg'),'-hide_banner','-y','-framerate',C['fps'],'-start_number',C['preview_start'],'-i',folder/'%04d.png','-frames:v',C['preview_end']-C['preview_start']+1,'-c:v','libx264','-crf','20','-pix_fmt','yuv420p',R/'preview'/f'{a.stage}.mp4'])
 run(f'{a.stage}-probe',[shutil.which('ffprobe'),'-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',R/'preview'/f'{a.stage}.mp4'])
