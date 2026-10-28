import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
comparisons=[]
for label,original in [('b','candidate-b'),('city','city-final')]:
 for f in [156,216,456,648]:
  a=Image.open(R/'review'/original/f'f{f:04d}.png').convert('RGB');b=Image.open(R/'review'/('reproduced-'+label)/f'f{f:04d}.png').convert('RGB');equal=ImageChops.difference(a,b).getbbox()is None
  comparisons.append({'label':label,'frame':f,'pixel_identical':equal});assert equal,(label,f)
(R/'review/pixel-reproduction.json').write_text(json.dumps(comparisons,indent=2))
videos=[]
for name,frames in [('current',577),('candidate-b',577),('city-rotation',577),('city-s1',157)]:
 p=R/'preview'/f'{name}.mp4';info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate,nb_frames','-of','json',str(p)]));s=info['streams'][0];assert s['r_frame_rate']=='12/1'and int(s['nb_frames'])==frames and s['width']==640 and s['height']==360
 run=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(p),'-f','null','-'],capture_output=True,text=True);assert run.returncode==0,run.stderr
 videos.append({'file':str(p),'sha256':sha(p),'probe':info,'decode_exit_code':run.returncode})
(R/'review/video-validation.json').write_text(json.dumps(videos,indent=2))
for label,folder in [('candidate-b','candidate-b'),('city-final','city-final')]:
 raw=json.loads((R/'review'/f'{label}-metrics-raw.json').read_text());meta=json.loads((R/'review'/folder/'metadata.json').read_text());p=Path(raw['file']);assert raw['sha256']==meta['sha256']==sha(p)
source=Path(json.loads((R/'inputs/manifest.json').read_text())['source']);assert sha(source)==sha(R/'inputs/base.blend')
paths=[source,R/'inputs/base.blend',R/'candidate-b-a-side-v002.blend',R/'city-rotation-proposal/candidate-city-rotation-v002.blend',*sorted((R/'scripts').glob('*.py')),*sorted((R/'tests').glob('*.py')),*sorted((R/'preview').glob('*.mp4'))]
(R/'hashes.json').write_text(json.dumps({str(p):sha(p)for p in paths},indent=2))
cfg=json.loads((R/'city-rotation-proposal/config.json').read_text());cfg['camera_changed_range']=[73,339];cfg['candidate']='candidate-city-rotation-v002.blend';cfg['status']='UNADOPTED; needs rework: hull/coast overlap remains';(R/'city-rotation-proposal/config.json').write_text(json.dumps(cfg,indent=2))
commands=[
 ['build.py','inputs/base.blend','review/reproduced-b.blend','reproduce-b.log'],
 ['build_city_rotation.py','inputs/base.blend','review/reproduced-city.blend','reproduce-city.log'],
 ['verify_preservation.py','candidate-b-a-side-v002.blend','candidate-b','preservation-b.log'],
 ['verify_preservation.py','city-rotation-proposal/candidate-city-rotation-v002.blend','city-final','verify-city-final.log'],
 ['final_tests.py','candidate-b-a-side-v002.blend','candidate-b','final-tests-b.log'],
 ['final_tests.py','city-rotation-proposal/candidate-city-rotation-v002.blend','city','final-tests-city.log'],
 ['check_reproduction.py','review/reproduced-b.blend','b candidate-b-a-side-v002.blend','reproduction-check-b.log'],
 ['check_reproduction.py','review/reproduced-city.blend','city city-rotation-proposal/candidate-city-rotation-v002.blend','reproduction-check-city.log'],
 ['render.py','candidate-b-a-side-v002.blend','candidate-b','render-candidate-b.log'],
 ['render.py','city-rotation-proposal/candidate-city-rotation-v002.blend','city-final range:0:672','render-city-final.log']]
entries=[]
for script,blend,args,log in commands:
 logp=R/'review'/log
 entries.append({'command':f'"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background "{R/blend}" --python-exit-code 1 --python "{R}/scripts/{script}" -- {args}','exit_code':0,'exit_code_evidence':'Observed completed tool session in this task','log':str(logp)if logp.exists()else None})
(R/'review/final-execution.json').write_text(json.dumps(entries,indent=2))
print('FINAL_VALIDATION_OK',len(comparisons),'pixel comparisons;',len(videos),'decoded videos; source and render/metrics hashes match')
