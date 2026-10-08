"""Fresh Blender process, source replay, RGB comparison and encoded-video probes."""
import subprocess,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];B='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
def run(logname,file,script,args):
 with (R/'logs'/logname).open('w',encoding='utf-8') as log:
  subprocess.run([B,'--background','--factory-startup',str(R/file),'--python-exit-code','1','--python',str(R/'scripts'/script),'--',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
frames=[456,457,458,459,470,480,494,499,502,510,522,555,632,648,660,672,696]
run('reopen-render.log','master-s4-fix.blend','render_evidence.py',['reopen',','.join(map(str,frames))])
matches={f:ImageChops.difference(Image.open(R/f'review/final-continuity/f{f:04}.png').convert('RGB'),Image.open(R/f'review/reopen/f{f:04}.png').convert('RGB')).getbbox() is None for f in frames}
assert all(matches.values()),matches
run('source-replay.log','inputs/before-close-reveal.blend','revise_close_reveal.py',['review/source-replay.blend'])
run('source-replay-capture.log','review/source-replay.blend','scene_evidence.py',['states-replay.json'])
run('final-state-capture.log','master-s4-fix.blend','scene_evidence.py',['states-final.json'])
a=json.loads((R/'review/states-final.json').read_text(encoding='utf-8'));b=json.loads((R/'review/states-replay.json').read_text(encoding='utf-8'))
assert a==b,'Source replay differs from saved master'
videos={}
for name,n in [('s4-before.mp4',193),('s4-close-reveal-before.mp4',193),('s4-after.mp4',193),('s3-tail_s4_s5-head.mp4',253)]:
 p=R/'preview'/name;d=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)],text=True));v=next(s for s in d['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(960,540,'12/1',n)
 videos[name]={'frames':n,'fps':12,'size':[960,540],'duration':d['format']['duration']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'inputs/base-s4.blend')=='63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976'
assert sha(R/'inputs/before-close-reveal.blend')=='85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de'
result={'reopen_rgb_identical':matches,'source_replay_all_1393_states_exact':True,'baseline_preserved':True,'final_blend_sha256':sha(R/'master-s4-fix.blend'),'videos':videos}
(R/'review/reopen-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
