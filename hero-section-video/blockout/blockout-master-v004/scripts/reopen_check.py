import subprocess,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
blender='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
results={}
for mode,name in [('integrated','master-v004.blend')]:
    with (ROOT/'logs'/f'reopen-{mode}.log').open('w',encoding='utf-8') as log:
        subprocess.run([blender,'--background','--factory-startup',str(ROOT/name),'--python-exit-code','1','--python',str(ROOT/'scripts/render_evidence.py'),'--','reopen-'+mode,'96,148,216,217,234,251,252'],stdout=log,stderr=subprocess.STDOUT,check=True)
    matches={str(f):ImageChops.difference(Image.open(ROOT/'review'/mode/f'f{f:04}.png').convert('RGB'),Image.open(ROOT/'review'/('reopen-'+mode)/f'f{f:04}.png').convert('RGB')).getbbox() is None for f in [96,148,216,217,234,251,252]}
    assert all(matches.values()),matches
    results[mode]={'blend_sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'reopen_rgb_identical':matches}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/'inputs/base-v003.blend')==sha(ROOT.parent/'blockout-master-v003/master-v003.blend')=='ae1a8ea2dfbf8127b27ecd9ad999589575e87aac9eb578c970fd812e7063964e'
results['original_v003_preserved']=True
videos={}
for p in (ROOT/'preview').glob('*.mp4'):
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)],text=True))
    v=next(x for x in probe['streams'] if x['codec_type']=='video');expected=193 if 's1-tail' in p.name else 157 if p.name=='limited-connection.mp4' else 121
    assert v['width']==960 and v['height']==540 and v['r_frame_rate']=='12/1' and int(v['nb_read_frames'])==expected
    videos[p.name]={'frames':expected,'fps':v['r_frame_rate'],'size':[v['width'],v['height']],'duration':probe['format']['duration']}
results['videos']=videos
play=json.loads((ROOT/'review/playback-check.json').read_text());assert len(play['reports'])==2 and not play['errors'] and all(r['result']['ended'] and r['result']['dropped']==0 for r in play['reports'])
results['actual_playback']=play['reports']
(ROOT/'review/reopen-check.json').write_text(json.dumps(results,indent=2))
print(json.dumps({k:v for k,v in results.items() if k!='actual_playback'},indent=2))
