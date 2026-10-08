import subprocess,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];B='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
def run(name,file,script,args):
 with (R/'logs'/name).open('w',encoding='utf-8') as log:subprocess.run([B,'--background','--factory-startup',str(R/file),'--python-exit-code','1','--python',str(R/'scripts'/script),'--',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
run('reopen-render.log','master-v005.blend','render_evidence.py',['reopen','216,278,330,380,422,450,456'])
matches={f:ImageChops.difference(Image.open(R/f'review/after/f{f:04}.png').convert('RGB'),Image.open(R/f'review/reopen/f{f:04}.png').convert('RGB')).getbbox() is None for f in [216,278,330,380,422,450,456]}
assert all(matches.values()),matches
run('source-replay.log','inputs/base-v005.blend','revise_s3.py',['review/source-replay.blend'])
run('source-replay-capture.log','review/source-replay.blend','scene_evidence.py',['states-replay.json'])
a=json.loads((R/'review/states-after.json').read_text());b=json.loads((R/'review/states-replay.json').read_text());assert a==b,'Source replay differs from final evaluated state'
videos={}
for p in (R/'preview').glob('*.mp4'):
 d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)],text=True));v=next(s for s in d['streams'] if s['codec_type']=='video');n=277 if p.name=='s2-tail_s3_s4-head.mp4' else 241
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(960,540,'12/1',n)
 videos[p.name]={'frames':n,'fps':12,'size':[960,540],'duration':d['format']['duration']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'inputs/base-v005.blend')=='de03eca6e92f7c03ab967a44ed434531e5506536669a8383d69ac1bbf056ad0d'
result={'reopen_rgb_identical':matches,'source_replay_all_1393_states_exact':True,'baseline_preserved':True,'final_blend_sha256':sha(R/'master-v005.blend'),'videos':videos}
(R/'review/reopen-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
