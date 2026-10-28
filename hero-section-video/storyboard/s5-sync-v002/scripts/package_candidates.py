"""Repackage byte-identical, freshly revalidated candidates; no Blender edits."""
from pathlib import Path
import json, sys, shutil, subprocess, html
from PIL import Image
B=Path(__file__).resolve().parents[1]; OLD=B.parent/'s5-sync-v001'; REPO=B.parents[2]
sys.path.insert(0,str(OLD/'scripts'))
from contracts import digest,checked_file,validate_run,validate_selection,validate_panel,validate_role,require
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=load(OLD/'render-record.json');oldsel=load(OLD/'storyboard-selection.json');m=load(OLD/'storyboard-manifest.json')
validate_run(r);validate_selection(oldsel,r)
require(m['selection_sha256']==digest(OLD/'storyboard-selection.json'),'selection changed')
fresh=load(B/'review/source-revalidation.json');require(fresh['pass'] and fresh['max_difference']==0,'fresh state mismatch')
checked_file(fresh['source'],r['source']['sha256'])
source={'path':fresh['source'],'sha256':r['source']['sha256']}
provenance={'original_render_record':str(OLD/'render-record.json'),'sha256':digest(OLD/'render-record.json'),'source_byte_identical':True,'fresh_state_validation':str(B/'review/source-revalidation.json'),'fresh_state_validation_sha256':digest(B/'review/source-revalidation.json'),'method':'Reuse immutable prior render output after complete dependency and PNG hashes plus fresh saved-scene camera/state comparison. No render relabeling.'}
sel={**oldsel,'baseline_adoption':'user explicitly selected s5-integration-v001 for this task','user_baseline_instruction':'s5-integration-v001를 기준으로 S5스토리보드 동기화 작업을 진행해라.','source_path':source['path']}
save(B/'storyboard-selection.json',sel)
panels=[]
for p in m['panels']:
 validate_panel(p,r);validate_role(p['id'],p['actual_state']['metrics'])
 im=Image.open(p['path']).convert('RGB');raw=Image.open(p['raw_path']).convert('RGB');x,y,w,h=p['image_region']
 require(im.crop((x,y,x+w,y+h)).tobytes()==raw.tobytes(),'panel region modified')
 dest=B/'panels'/Path(p['path']).name;shutil.copy2(p['path'],dest)
 rawdest=B/'review'/f"{p['id']}-raw.png";shutil.copy2(p['raw_path'],rawdest)
 panels.append({**p,'path':str(dest),'sha256':digest(dest),'source':source,'reuse_provenance':provenance,'review_raw_copy':{'path':str(rawdest),'sha256':digest(rawdest)},'user_approval':None,'status':'candidate'})
save(B/'storyboard-manifest.json',{'status':'structural candidates; frame and style selection pending','source':source,'selection_sha256':digest(B/'storyboard-selection.json'),'reuse_provenance':provenance,'panels':panels,'packager_sha256':digest(__file__)})
shutil.copy2(OLD/'review/candidates.png',B/'review/candidates.png')
st=load(OLD/'review/style-sample-record.json');checked_file(st['path'],st['sha256']);checked_file(st['raw_path'],st['raw_sha256'])
require(st['source']['sha256']==source['sha256'],'style source mismatch');checked_file(OLD/'scripts/style_sample.py',st['style_script_sha256'])
style=B/'line-art/sample-f766.png';shutil.copy2(st['path'],style)
save(B/'review/style-sample-record.json',{**st,'path':str(style),'reused_from':str(OLD/'review/style-sample-record.json'),'source':source})
shutil.copy2(OLD/'review/style-comparison.png',B/'review/style-comparison.png')
v=load(OLD/'preview/video-record.json');checked_file(v['path'],v['sha256']);require(v['source']['sha256']==source['sha256'],'video source mismatch');require(v['render_record_sha256']==digest(Path(r['output_dir'])/'render-record.json'),'video render mismatch')
video=B/'preview/main.mp4';shutil.copy2(v['path'],video)
save(B/'preview/video-record.json',{**v,'path':str(video),'reused_from':str(OLD/'preview/video-record.json'),'reuse_provenance':provenance})
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True));save(B/'review/video-probe.json',probe)
stream=next(s for s in probe['streams'] if s['codec_type']=='video');require(int(stream['nb_frames'])==325 and stream['avg_frame_rate']=='12/1','video mismatch')
save(B/'review/artifact-validation.json',{'pass':True,'source':source,'raw_frames_hashed':len(r['images']),'raw_panel_pixel_regions_identical':6,'roles_passed':6,'actual_f810_rejected':False,'reused_outputs':True,'fresh_scene_state_validation':fresh,'master_modified':False,'user_frame_style_selection':'pending'})
try:validate_role('S5-03A',next(i for i in r['images'] if i['frame']==810)['state']['metrics'])
except ValueError: pass
else:raise AssertionError('Actual stopped f810 incorrectly accepted')
a=load(B/'review/artifact-validation.json');a['actual_f810_rejected']=True;save(B/'review/artifact-validation.json',a)
notion_old=(OLD/'inputs/notion-s5.md').read_text(encoding='utf-8').strip();notion_new=(B/'inputs/notion-s5-current.md').read_text(encoding='utf-8').strip()
save(B/'inputs/source.json',{'source':source,'git_head':subprocess.check_output(['git','-c',f'safe.directory={REPO}','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'notion_matches_prior_snapshot':notion_old==notion_new,'model':'unconfirmed','reasoning_effort':'unconfirmed','prior_master_preserved':True})
save(B/'review-decisions.json',{'baseline':{'status':'selected','source':source,'user_instruction':sel['user_baseline_instruction'],'exact_response_timestamp':None,'client_date':'2026-10-09'},'frames':{'status':'candidate','selection_file':'storyboard-selection.json'},'style':{'status':'sample only; pending user selection'},'final_artistic_approval':None,'not_a_full_layout_master_replacement':True})
cards=''.join(f'<section><h2>{p["id"]} · {p["role"]} · f{p["frame"]}</h2><a href="panels/{Path(p["path"]).name}"><img src="panels/{Path(p["path"]).name}" alt="{p["id"]} 구조 초안"></a><p><a href="review/{p["id"]}-raw.png">무주석 원본</a> · 본편 {p["master_seconds"]:.3f}초 · 프리뷰 {p["preview_seconds"]:.3f}초</p></section>' for p in panels)
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>S5 스토리보드 · s5-integration-v001 기준</title><style>body{max-width:1200px;margin:28px auto;padding:0 22px;background:#f3f1eb;color:#202622;font:17px/1.7 system-ui}h1{font-size:30px}img,video{max-width:100%;height:auto}video{width:100%;max-height:58vh;background:#202020}section{margin:36px 0}button{font:inherit;padding:12px 20px;background:#244638;color:white;border:0;border-radius:5px}a{color:#205a47}.notice{padding:18px;background:#e0e9e2}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}@media(max-width:800px){.grid{grid-template-columns:1fr}}</style>
<h1>S5 스토리보드 동기화 · 구조 검토 후보</h1><p class="notice">기준: master-s5-integration-v001.blend · SHA 8c76f0e1… · 마스터 무수정.<br>이번에 지정하신 기준의 실제 구도를 따릅니다. 앞서 만든 full-layout-master-v001과 구도가 다릅니다.</p>
<p>후보: 01 f672 → 02 f720 → 03 f732 → 03A f766 → 04 f842 → 05 f900.<br>03은 접근, 03A는 실제 선회 중이며, 정지한 f810을 선회 장면으로 사용하지 않습니다.</p>
<p><a href="#style">흑백 윤곽 스타일 샘플</a> · <a href="#panels">개별 6장과 원본</a> · <a href="report.md">검증 보고서</a></p>
<section><h2>연속 프리뷰 · f624–948 · 12fps · 27.08초</h2><video id="preview" controls preload="metadata" src="preview/main.mp4"></video><button id="play">처음부터 원속도 재생</button><p id="status">재생 대기</p></section>
<section><h2>여섯 관찰 지점</h2><img src="review/candidates.png" alt="S5 실제 프레임 후보 6장"></section>
<section id="style"><h2>표현 방향 샘플 · f766</h2><p>동일한 3D 상태와 카메라에서 만든 흰 바탕·검은 윤곽입니다. 현재는 샘플 한 장이며, 프레임과 표현 방향 선택 후 여섯 장에 적용합니다.</p><img src="review/style-comparison.png" alt="동일 구도 원본과 Freestyle 선화 비교"><p><a href="line-art/sample-f766.png">무주석 선화 샘플</a></p></section><div id="panels" class="grid">'''+cards+'''</div><script>const v=document.getElementById('preview'),s=document.getElementById('status');document.getElementById('play').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.dataset.started=performance.now();v.play();s.textContent='원속도 재생 중';};v.onended=()=>{v.dataset.elapsed=(performance.now()-Number(v.dataset.started))/1000;s.textContent='전체 재생 완료';};</script></html>'''
(B/'review.html').write_text(page,encoding='utf-8')
print('PACKAGED: six validated structural candidates, unchanged 325-frame preview, one style sample')
