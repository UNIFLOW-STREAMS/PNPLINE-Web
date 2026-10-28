"""Add a separate fast review video without changing source timing or panels."""
from pathlib import Path
import json, hashlib, subprocess
B=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
original=B/'preview/main.mp4';quick=B/'preview/main-2x.mp4'
v=load(B/'preview/video-record.json')
assert sha(original)==v['sha256']
raw=load(B.parent/'s5-sync-v001/render-record.json')
assert raw['source']['sha256']==v['source']['sha256']
assert len(raw['images'])==325 and raw['expected_frames']==list(range(624,949))
for i in raw['images']:
 assert sha(Path(i['path']))==i['sha256']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=avg_frame_rate,nb_frames,duration','-of','json',str(quick)],text=True))['streams'][0]
assert probe['avg_frame_rate']=='24/1' and int(probe['nb_frames'])==325 and abs(float(probe['duration'])-325/24)<.00001
save(B/'preview/quick-video-record.json',{'purpose':'preview playback only; 2x of original 12fps animation','source_blend_sha256':raw['source']['sha256'],'source_render_record_path':str(B.parent/'s5-sync-v001/render-record.json'),'source_render_record_sha256':sha(B.parent/'s5-sync-v001/render-record.json'),'source_original_video_sha256':sha(original),'path':str(quick),'sha256':sha(quick),'source_frames':[624,948],'frame_count':325,'video_fps':24,'duration_seconds':325/24,'frame_mapping':'quick t=(master_frame-624)/24; original t=(master_frame-624)/12','master_animation_changed':False,'source_frames_dropped':False,'probe':probe})
page=B/'review.html';content=page.read_text(encoding='utf-8')
old='<section><h2>연속 프리뷰 · f624–948 · 12fps · 27.08초</h2><video id="preview" controls preload="metadata" src="preview/main.mp4"></video><button id="play">처음부터 원속도 재생</button><p id="status">재생 대기</p></section>'
new='<section><h2>연속 프리뷰 · f624–948</h2><p>빠른 검토 영상: 24fps · 13.54초 · 원본 325프레임 모두 사용. 원속도: 12fps · 27.08초. 콘티의 본편·프리뷰 시각 표기는 원속도 기준입니다.</p><video id="preview" controls preload="metadata" src="preview/main-2x.mp4"></video><div class="speeds"><button id="play">빠른 프리뷰 · 2배속</button> <button id="play15">1.5배속</button> <button id="play1">원속도 · 1배속</button></div><p><a href="preview/main-2x.mp4">빠른 영상 파일</a> · <a href="preview/main.mp4">원속도 영상 파일</a></p><p id="status">빠른 프리뷰 준비됨</p></section>'
assert old in content, 'unexpected review page structure'
content=content.replace(old,new)
oldjs="const v=document.getElementById('preview'),s=document.getElementById('status');document.getElementById('play').onclick=()=>{v.currentTime=0;v.playbackRate=1;v.dataset.started=performance.now();v.play();s.textContent='원속도 재생 중';};v.onended=()=>{v.dataset.elapsed=(performance.now()-Number(v.dataset.started))/1000;s.textContent='전체 재생 완료';};"
newjs="const v=document.getElementById('preview'),s=document.getElementById('status');function playReview(mode){const fast=mode===2;v.src=fast?'preview/main-2x.mp4':'preview/main.mp4';v.load();v.playbackRate=fast?1:mode;v.dataset.mode=String(mode);v.dataset.started=String(performance.now());v.play();s.textContent=mode+'배속 재생 중';}document.getElementById('play').onclick=()=>playReview(2);document.getElementById('play15').onclick=()=>playReview(1.5);document.getElementById('play1').onclick=()=>playReview(1);v.onended=()=>{v.dataset.elapsed=String((performance.now()-Number(v.dataset.started))/1000);s.textContent=v.dataset.mode+'배속 전체 재생 완료';};"
assert oldjs in content, 'unexpected review script'
page.write_text(content.replace(oldjs,newjs),encoding='utf-8')
report=B/'report.md';with_text=report.read_text(encoding='utf-8')+'\n## 프리뷰 속도 조정\n\n사용자는 “프리뷰 재생만 빠르게”를 선택했다. 동일한 f624–948의325프레임을 24fps로 재인코딩한 2배속 검토 영상(`preview/main-2x.mp4`)을 추가했다. 길이는13.541667초이며 누락 프레임이 없다. 검토 페이지에서 2배속·1.5배속·원속도를 선택할 수 있다. 원본 12fps 영상, Blender 키프레임·동작, 선택된 여섯 프레임과 manifest의 원속도 시간은 그대로다. 재생만 빠른 영상의 시각은 `(master_frame-624)/24`로 환산한다. 증거는 `preview/quick-video-record.json`과 브라우저 재생 기록을 따른다.\n'
report.write_text(with_text,encoding='utf-8')
readme=B/'README.md';readme.write_text(readme.read_text(encoding='utf-8').replace('- [원속도 연속 영상](preview/main.mp4)','- [빠른 2배속 영상](preview/main-2x.mp4) · [원속도 연속 영상](preview/main.mp4)'),encoding='utf-8')
dec=B/'review-decisions.json';d=load(dec);d['preview_speed_choice']={'answer':'프리뷰 재생만 빠르게','source':'actual user answer in current conversation','scope':'preview playback only; original master, source motion, selected frames and original-speed video unchanged','fast_video':str(quick)};save(dec,d)
with (B/'progress.md').open('a',encoding='utf-8') as f:f.write('\nUser steering: “지금 프리뷰 렌더링을 보면 너무 느리다.” Clarification answer: “프리뷰 재생만 빠르게”. Added full-frame 2x file and page speed controls; original master/timing/selected frames preserved.\n')
hashes=B/'hashes.json';h=load(hashes)
for p in [quick,B/'preview/quick-video-record.json',page,report,readme,dec,B/'progress.md']:
 h[str(p.relative_to(B)).replace('\\','/')]=sha(p)
save(hashes,h)
print('FAST_PREVIEW_READY',str(quick),probe)
