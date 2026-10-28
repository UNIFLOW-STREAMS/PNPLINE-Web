import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R/'layout-proposal-v001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();blend=P/'s4-s5-layout-proposal-v001.blend';identity=sha(blend)
for file,key in [('build-record.json','proposal_sha256'),('acceptance.json','sha256'),('integrity.json','proposal_sha256'),('render-full.json','blend_sha256'),('package-record.json','blend_sha256')]:
 data=json.loads((P/file).read_text());assert data[key]==identity,(file,'stale')
assert json.loads((P/'acceptance.json').read_text())['passed'];assert json.loads((P/'integrity.json').read_text())['pass'];assert json.loads((P/'space-validation.json').read_text())['pass_all']
master=R.parents[1]/'blockout/s5-integration-v001/master-s5-integration-v001.blend';assert sha(master)=='8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665'
playback={'method':'Cua in-app browser native video playback; page DOM read after ended','url':'http://127.0.0.1:8767/layout-proposal-v001/review.html','src':'http://127.0.0.1:8767/layout-proposal-v001/preview.mp4','duration':33.083333,'current_time':33.083333,'ended':True,'paused':True,'playback_rate':1,'elapsed_s':33.10860000000149,'error':None,'video_sha256':sha(P/'preview.mp4'),'not_user_approval':True}
(P/'playback.json').write_text(json.dumps(playback,indent=2),encoding='utf8')
review={'reviewer':'fresh-context /root/layout_proposal_final_review','model':'gpt-6-astra','reasoning_effort':'high','proposal_sha256':identity,'critical':[],'important':[],'minor_deferred':[{'finding':'Crane leg briefly crosses truck/container at f692–700','evidence':['raw-24b13b88/0696.png','raw-24b13b88/0700.png'],'disposition':'Disclosed for artistic review; no collision; optional visibility refinement after user feedback.'}],'status_note':'Reviewer observed in-progress status fields; finalized below as part of normal delivery packaging.','coverage':'Metadata, scripts, source and proposal SHA, 397 PNG hashes/frame sequence, package hashes, reference/comparison/contact images and representative renders. Playback independently checked by parent.'}
(P/'final-review.json').write_text(json.dumps(review,indent=2),encoding='utf8')
d=json.loads((R/'review-decisions.json').read_text(encoding='utf8'));d['current_question']='Separate layout proposal submitted; final adoption pending';d['layout_proposal']={'status':'submitted; final adoption pending','path':str(blend),'sha256':identity,'review_range':[552,948],'user_final_approval':None};d['user_concerns'][0]['finding']='Original-baseline finding: old S4-05 had ship left/warehouse right while original f648/f672 showed reversed screen relationships. Separate layout proposal now addresses this; no final artistic adoption inferred.';d['user_concerns'][0]['status']='addressed in submitted separate proposal; final adoption pending';(R/'review-decisions.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
with (P/'report.md').open('a',encoding='utf8') as h:
 h.write('\n## 제출 검토 결과\n\n최신 제안본 SHA-256: `'+identity+'`. 14개 구간 검사 통과. 차량·컨테이너 25개 메시 불변. 접지 최대 오차 0.00006682m, 카메라–크레인/선박/차량 최소 거리 1.67497m. 원속도 33.083333초 재생 완료, 오류 없음.\n\n독립 검토(gpt-6-astra/high): Critical/Important 0건. 남긴 연출 검토 사항: f692–700에서 크레인 기둥이 차량을 잠깐 가린다. 충돌과는 별개의 가시성 사항이며, 현재 제안 영상에 그대로 드러난다.\n\n전체 마스터 채택·선화 6장 확정은 사용자 선택 대기다. 이 제안본을 최종 마스터로 교체하지 않았다.\n')
with (R/'progress.md').open('a',encoding='utf8') as h:
 h.write('\nLayout proposal submitted: '+identity+'. Original unchanged. f552–948,397 frames/12fps; source and saved proposal provenance verified. Acceptance14/14, collision1,650,704pairs0errors; integrity pass; browser real-time playback ended at33.083333s. Fresh reviewer gpt-6-astra/high: no Critical/Important.\nFinal: minor (deferred): f692–700 crane leg briefly occludes the moving vehicle; disclosed for user artistic review.\n')
for file in ['README.md','report.md']:
 p=R/file;old=p.read_text(encoding='utf8');notice='> 최신 제출: [S4-05 기준 별도 배치·동선 제안](layout-proposal-v001/report.md) — [영상·비교 검토](layout-proposal-v001/review.html). f552–948 검토용, 원본 보존, 최종 마스터 미채택. 아래의 기존 Stage③ 후보/카메라 진단은 이전 기준 자료입니다.\n\n'
 if not old.startswith(notice):p.write_text(notice+old,encoding='utf8')
p=R/'review.html';old=p.read_text(encoding='utf8');banner='<div style="padding:24px;background:#194251;color:white"><a style="color:white;font-size:22px" href="layout-proposal-v001/review.html">최신: S4-05 기준 별도 배치·동선 제안 → 영상과 비교 보기</a><p>f552–948 검토용. 원본 보존 · 최종 마스터 미채택. 아래는 이전 진단 자료입니다.</p></div>'
if '최신: S4-05 기준 별도 배치·동선 제안' not in old:
 at=old.find('>',old.find('<body'))+1
 if at>0:old=old[:at]+banner+old[at:]
 else:old=banner+old
 p.write_text(old,encoding='utf8')
files={str(p.relative_to(P)):sha(p) for p in P.rglob('*') if p.is_file() and p.name!='hashes.json'};(P/'hashes.json').write_text(json.dumps(files,indent=2),encoding='utf8')
files={str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and p!=R/'hashes.json' and 'logs' not in p.parts and '__pycache__' not in p.parts and p.name!='live-playback.json'};(R/'hashes.json').write_text(json.dumps(files,indent=2),encoding='utf8')
print('DELIVERY_VERIFIED',identity,'files',len(files))
