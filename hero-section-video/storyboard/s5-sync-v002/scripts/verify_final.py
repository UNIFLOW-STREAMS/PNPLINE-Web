import json,sys,hashlib
from pathlib import Path
from PIL import Image
B=Path(__file__).resolve().parents[1];OLD=B.parent/'s5-sync-v001'
sys.path.insert(0,str(B/'scripts'));from lineage import digest,require,validate_expression
sys.path.insert(0,str(OLD/'scripts'));from contracts import validate_run,validate_role,validate_panel,checked_file
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
raw=load(OLD/'render-record.json');sel=load(B/'storyboard-selection.json');m=load(B/'storyboard-manifest.json');expr=load(B/'line-art-record.json')
validate_run(raw);validate_expression(expr,raw,B/'storyboard-selection.json')
require(m['selection_sha256']==digest(B/'storyboard-selection.json'),'selection changed')
require(m['expression_record_sha256']==digest(B/'line-art-record.json'),'expression record changed')
require(m['packager_sha256']==digest(B/'scripts/package_final.py'),'packager changed')
comparison=load(B/'review/current-master-comparison.json')
checked_file(comparison['old_path'],m['source']['sha256'])
checked_file(comparison['current_path'],comparison['current_sha256'])
require(comparison['old_sha256']==m['source']['sha256'] and comparison['motion_camera_equivalent_for_preview'],'saved source changed substantively; re-render required')
require(m['source']['sha256']==raw['source']['sha256'],'source mismatch')
require([p['id'] for p in m['panels']]==[p['id'] for p in sel['panels']],'panel set changed')
for p in m['panels']:
 validate_panel(p,raw);validate_role(p['id'],p['actual_state']['metrics'])
 e=next(i for i in expr['images'] if i['id']==p['id']);require(e['frame']==p['frame'],'frame mismatch')
 checked_file(p['line_art']['path'],p['line_art']['sha256']);require(e['sha256']==p['line_art']['sha256'],'wrong expression parent')
 require(p['line_art']['raw_parent_sha256']==p['raw_sha256'],'raw link mismatch')
 im=Image.open(p['path']).convert('RGB');li=Image.open(e['path']).convert('RGB');x,y,w,h=p['image_region'];require(li.size==(w,h) and li.tobytes()==im.crop((x,y,x+w,y+h)).tobytes(),'panel cropped or changed expression')
 require(p['camera_state']==e['camera_state'],'camera mismatch')
 checked_file(p['comparison']['path'],p['comparison']['sha256'])
for path,h in m['font_hashes'].items():checked_file(path,h)
v=load(B/'preview/video-record.json');checked_file(v['path'],v['sha256']);require(v['source']['sha256']==m['source']['sha256'],'video source mismatch')
play=load(B/'review/playback.json');require(play['video_sha256']==v['sha256'] and play['ended'] and play['playback_rate']==1,'playback missing')
dec=load(B/'review-decisions.json');require(dec['frames']['status']=='selected' and dec['style']['status']=='selected','selection missing')
result={'pass':True,'source':m['source'],'raw_frames_verified':len(raw['images']),'panels':6,'line_art_camera_projection_equal':6,'panel_expression_pixel_regions_equal':6,'role_state_checks':6,'master_unchanged':True,'preview_playback_pass':True,'technical_only':True,'final_artistic_approval':dec['final_artistic_approval'],'manifest_sha256':digest(B/'storyboard-manifest.json'),'expression_record_sha256':digest(B/'line-art-record.json')}
(B/'review/final-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
