from pathlib import Path
import json,sys,math
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from contracts import *
r=json.loads((R/'render-record.json').read_text(encoding='utf8'));s=json.loads((R/'storyboard-selection.json').read_text(encoding='utf8'));m=json.loads((R/'storyboard-manifest.json').read_text(encoding='utf8'));source=json.loads((R/'inputs/source.json').read_text(encoding='utf8'))
validate_run(r);validate_selection(s,r);checked_file(source['source'],source['source_sha256']);checked_file(source['snapshot'],source['snapshot_sha256'])
require(m['selection_sha256']==digest(R/'storyboard-selection.json'),'selection changed after packaging')
for p in m['panels']:
 validate_panel(p,r);validate_role(p['id'],p['actual_state']['metrics'])
 checked_file(p['render_record']['path'],p['render_record']['sha256'])
 im=Image.open(p['path']).convert('RGB');raw=Image.open(p['raw_path']).convert('RGB');x,y,w,h=p['image_region']
 require(raw.size==(w,h) and raw.tobytes()==im.crop((x,y,x+w,y+h)).tobytes(),'panel cropped or changed raw image')
 require(p['resolution']==r['render']['resolution'],'resolution mismatch')
stopped=next(i for i in r['images'] if i['frame']==810)['state']['metrics']
try:validate_role('S5-03A',stopped)
except ValueError:rejected=True
else:rejected=False
require(rejected,'actual stopped f810 incorrectly accepted as turning')
video=json.loads((R/'preview/video-record.json').read_text(encoding='utf8'));checked_file(video['path'],video['sha256']);probe=json.loads((R/'review/video-probe.json').read_text(encoding='utf8'))
v=next(x for x in probe['streams'] if x['codec_type']=='video');require(int(v['nb_frames'])==len(r['expected_frames']),'video frame count mismatch');a,b=map(int,v['avg_frame_rate'].split('/'));require(abs(a/b-r['fps']/r['fps_base'])<1e-6,'video speed mismatch');require(abs(float(v['duration'])-len(r['expected_frames'])*r['fps_base']/r['fps'])<.001,'video duration mismatch')
style=json.loads((R/'review/style-sample-record.json').read_text(encoding='utf8'));checked_file(style['path'],style['sha256']);checked_file(style['raw_path'],style['raw_sha256']);require(style['source']['sha256']==source['source_sha256'],'style source mismatch');require(style['style_script_sha256']==digest(R/'scripts/style_sample.py'),'review required: style changed')
notion=lambda p:p.read_text(encoding='utf8').replace('\r\n','\n').strip()
result={'pass_all':True,'role_checks':6,'raw_panel_pixel_regions_identical':6,'actual_f810_rejected_as_turning':rejected,'original_source_unchanged':True,'snapshot_identical':True,'raw_frames':len(r['images']),'video_duration':float(v['duration']),'video_fps':a/b,'notion_current_matches_snapshot':notion(R/'inputs/notion-s5-current.md')==notion(R/'inputs/notion-s5.md'),'user_selection':'pending','style_stage':'one minimal sample; six full panels pending choice','full_stage3_complete':False}
(R/'review/artifact-validation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
