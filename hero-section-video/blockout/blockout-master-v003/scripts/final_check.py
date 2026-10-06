import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
before={f:Image.open(ROOT/'review'/f'camera-f{f:04}.png').convert('RGB').copy() for f in [0,96]}
with (ROOT/'logs/reopen.log').open('w',encoding='utf-8') as log:
 subprocess.run(['C:/Program Files/Blender Foundation/Blender 5.1/blender.exe','--background','--factory-startup',str(ROOT/'master-v003.blend'),'--python-exit-code','1','--python',str(ROOT/'scripts/render_s1.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
reopen={str(f):ImageChops.difference(before[f],Image.open(ROOT/'review'/f'camera-f{f:04}.png').convert('RGB')).getbbox() is None for f in before}
assert all(reopen.values())
same_end=ImageChops.difference(Image.open(ROOT.parent/'blockout-master-v002/review/camera-f0096.png').convert('RGB'),Image.open(ROOT/'review/camera-f0096.png').convert('RGB')).getbbox() is None
assert same_end
base=sha(ROOT/'inputs/base-v002.blend');assert base==sha(ROOT.parent/'blockout-master-v002/master-v002.blend')
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(ROOT/'preview/master-v003.mp4')],text=True))
video=next(s for s in probe['streams'] if s['codec_type']=='video');assert int(video['nb_read_frames'])==1393
results=[read('logs/'+n) for n in ['test-result.json','s1-test-result.json','framing-test-result.json']]
assert all(r['failures']==r['errors']==0 for r in results)
play=read('review/playback-check.json');assert play['result']['ended'] and not play['errors']
result={'reopen_rgb_pixels_identical':reopen,'S1_end_pixels_identical_to_v002':same_end,'original_v002_preserved':True,'base_sha256':base,'tests_passed':sum(r['tests'] for r in results),'frame_count':1393,'duration_seconds':probe['format']['duration'],'actual_playback':play['result']}
(ROOT/'review/final-check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
manifest={'version':'v003','revision':read('review/revision.json'),'verification':result,'base':'inputs/base-v002.blend','master':'master-v003.blend','source':'scripts/raise_camera.py','full_preview':'preview/master-v003.mp4','change_preview':'preview/S1-low-to-high.mp4','notes':'User-requested camera translation; rotation/lens unchanged; existing scene retained'}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
sheet=Image.new('RGB',(1280,390),(236,240,242));draw=ImageDraw.Draw(sheet)
for x,path,label in [(0,ROOT.parent/'blockout-master-v002/review/camera-f0000.png','BEFORE / FRAME 0'),(640,ROOT/'review/camera-f0000.png','AFTER / SAME CAMERA ROTATION')]:
 sheet.paste(Image.open(path).resize((640,360)),(x,30));draw.text((x+12,10),label,fill=(25,35,45))
sheet.save(ROOT/'review/framing-comparison.png')
paths=[p for p in ROOT.rglob('*') if p.is_file() and 'frames' not in p.relative_to(ROOT).parts and p.name not in ['hashes.json','master-v003.blend1','gui.pid']]
entries={p.relative_to(ROOT).as_posix():{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(paths)}
(ROOT/'hashes.json').write_text(json.dumps({'algorithm':'SHA-256','files':entries},indent=2),encoding='utf-8')
assert all(sha(ROOT/n)==v['sha256'] for n,v in entries.items())
print(json.dumps(result,indent=2))
