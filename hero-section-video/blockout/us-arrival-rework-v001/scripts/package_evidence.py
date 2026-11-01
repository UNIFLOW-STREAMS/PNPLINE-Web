"""Consolidate exact-file evidence; does not assign artistic acceptance."""
import json,hashlib,subprocess,argparse,re
from pathlib import Path
from PIL import Image,ImageChops
p=argparse.ArgumentParser();p.add_argument('--version',default='v010');args=p.parse_args();version=args.version
if not re.fullmatch(r'v\d{3}',version):raise ValueError('Expected version such as v010')
R=Path(__file__).resolve().parents[1];C=R/f'candidate-arrival-{version}.blend'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
digest=sha(C);result={'candidate_sha256':digest,'source_sha256':sha(R/'inputs/current-v004.blend')}
for name in ['preservation','collisions','visibility','motion','reproduction']:
 p=R/'review'/f'candidate-arrival-{version}-{name}.json';data=read(p)
 assert data.get('sha256',data.get('candidate_sha256'))==digest,(name,'stale evidence')
 result[name]={'path':str(p.relative_to(R)),'sha256':sha(p)}
candidate_still=R/f'review/arrival-{version}/f0450.png'
if not candidate_still.is_file():candidate_still=R/f'review/evidence-{version}/f0450.png'
a=Image.open(candidate_still).convert('RGB');b=Image.open(R/f'review/reproduced-{version}/f0450.png').convert('RGB')
result['reproduction_pixels']={'size':list(a.size),'same_dimensions':a.size==b.size,'identical_rgb':a.size==b.size and ImageChops.difference(a,b).getbbox() is None}
assert result['reproduction_pixels']['identical_rgb']
before=read(R/'review/current-v004-inherited-regression.json');after=read(R/f'review/candidate-arrival-{version}-inherited-regression.json')
result['inherited_regression']={'baseline_tests':before['tests'],'candidate_tests':after['tests'],'same_failures':before['failures']==after['failures'],'baseline_failures':before['failures'],'candidate_failures':after['failures'],'baseline_errors':before['errors'],'candidate_errors':after['errors']}
assert before['tests']==after['tests']==24 and before['failures']==after['failures'] and not before['errors'] and not after['errors']
base={r['frame']:r for r in read(R/'review/current-v004-motion.json')['rows']};current=read(R/f'review/candidate-arrival-{version}-motion.json')['rows']
keys=['height','roll_degrees','speed','angular_speed','roll_rate'];outside=[r for r in current if r['frame']<=300 or r['frame']>528.25]
result['motion_outside_max_error']={k:max(abs(r.get(k,0)-base[r['frame']].get(k,0)) for r in outside) for k in keys}
inside=[r for r in current if 300<=r['frame']<=528]
result['motion_inside_maxima']={k:max((abs(r.get(k,0)),r['frame']) for r in inside) for k in ['speed','angular_speed','roll_rate','roll_degrees']}
result['videos']={}
for label,sourcehash in [('baseline-v004',result['source_sha256']),(f'candidate-{version}',digest)]:
 folder=R/'preview'/label;meta=read(folder/'metadata.json')
 assert meta['sha256']==sourcehash and meta['first']==288 and meta['last']==720 and meta['stride']==1 and meta['fps']==12
 assert all((folder/f'f{f:04d}.png').is_file() for f in range(288,721))
 video=R/'preview'/f'{label}.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)],text=True))['streams'][0]
 assert probe['nb_read_frames']=='433' and probe['r_frame_rate']=='12/1' and probe['width']==640 and probe['height']==360
 result['videos'][label]={'path':str(video.relative_to(R)),'sha256':sha(video),'probe':probe,'render_metadata':meta}
result['artistic_acceptance']='Requires actual playback and independent review; this script does not judge appearance.'
(R/f'review/{version}-evidence-summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['videos','inherited_regression']},indent=2));print('VIDEO_VALIDATION',list(result['videos']))
