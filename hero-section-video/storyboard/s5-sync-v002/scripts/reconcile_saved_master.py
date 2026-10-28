"""Record the exact frozen render source and equivalent later scene save."""
from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=load(B/'review/current-master-comparison.json')
assert c['motion_camera_equivalent_for_preview'] and sha(Path(c['old_path']))==c['old_sha256'] and sha(Path(c['current_path']))==c['current_sha256']
m=load(B/'storyboard-manifest.json')
assert m['source']['sha256']==c['old_sha256']
m['source']['path']=c['old_path']
m['current_saved_master']={'path':c['current_path'],'sha256':c['current_sha256'],'rendered_source_motion_camera_equivalent_in_f624_948':True,'comparison_record':'review/current-master-comparison.json','comparison_sha256':sha(B/'review/current-master-comparison.json')}
for p in m['panels']:
 p['source']['path']=c['old_path']
save(B/'storyboard-manifest.json',m)
d=load(B/'review-decisions.json');d['final_package']['manifest_sha256']=sha(B/'storyboard-manifest.json');d['current_saved_master']={'sha256':c['current_sha256'],'same_S5_animation_and_geometry_as_rendered_source':True,'source':'read-only Blender comparison after user save; review/current-master-comparison.json'};save(B/'review-decisions.json',d)
play={'pass':True,'video_sha256':sha(B/'preview/main-2x.mp4'),'duration_s':13.541667,'current_time_s':13.541667,'ended':True,'media_error':None,'effective_speed':2,'media_playback_rate':1,'observed_wall_seconds':13.616,'mode':'2','source_frame_count':325,'source_blend_snapshot_sha256':c['old_sha256'],'current_saved_master_sha256':c['current_sha256'],'source_equivalence_record':'review/current-master-comparison.json','method':'Clicked fast preview button and observed HTML video element at start/end via CUA'}
save(B/'review/quick-playback.json',play)
report=B/'report.md';report.write_text(report.read_text(encoding='utf-8')+'\n출처 추가 확인: 현재 기준 경로의 저장본 SHA는 `'+c['current_sha256']+'`로 바뀌었고 저장 프레임은 907에서 521로 바뀌었다. 검토 영상은 SHA `'+c['old_sha256']+'`의 보존 사본에서 출력되었다. Blender에서 전체 S5 프리뷰 f624–948의 325프레임에 대해 카메라·렌즈·304객체 월드 행렬 및 메시 형상을 직접 대조했으며 차이가 없었다. 따라서 이 구간의 영상 내용은 현재 저장본과 같다. 두 파일의 경로와 해시, 검증 항목은 `review/current-master-comparison.json`에 기록했다.\n',encoding='utf-8')
page=B/'review.html';text=page.read_text(encoding='utf-8');text=text.replace('기준: master-s5-integration-v001.blend · SHA 8c76f0e1… · 마스터 무수정.','기준: master-s5-integration-v001.blend · 현재 저장본 SHA cc2dec40… · 프리뷰 구간 동작 동일.');page.write_text(text,encoding='utf-8')
with (B/'progress.md').open('a',encoding='utf-8') as f:f.write('\nRoot cause investigation: user-visible master path was saved later, hash changed from8c76f0e1 tocc2dec40; saved frame907→521. Full f624–948,304-object world matrices, all camera matrices/lens and meshes equal. Updated final manifest to reference frozen exact render source and current equivalent save; original rendered record remains immutable. 2x browser playback ended13.541667s in13.616s, no media error.\n')
hashes=B/'hashes.json';h=load(hashes)
for p in [B/'storyboard-manifest.json',B/'review-decisions.json',B/'review/current-master-comparison.json',B/'review/quick-playback.json',report,page,B/'progress.md',B/'scripts/verify_final.py',B/'scripts/reconcile_saved_master.py',B/'scripts/compare_saved_master.py',B/'scripts/add_fast_preview.py']:
 h[str(p.relative_to(B)).replace('\\','/')]=sha(p)
save(hashes,h)
print('RECONCILED',c['old_sha256'],c['current_sha256'])
