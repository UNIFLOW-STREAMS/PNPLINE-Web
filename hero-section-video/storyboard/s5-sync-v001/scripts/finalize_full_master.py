import json, hashlib, re
from pathlib import Path

ROOT = Path('F:/pnpline-landing/hero-section-video')
B = ROOT / 'blockout/full-layout-master-v001'
R = ROOT / 'storyboard/s5-sync-v001'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, x): p.write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
master = B / 'master-full-layout-v001.blend'
mh = sha(master)
assert mh == read(B/'package-record.json')['master_sha256']

review = {'reviewer':'/root/full_master_final_review','mode':'fresh read-only final review', 'master_sha256':mh,
 'critical':[], 'important':[], 'minor':[{'finding':'SAT validation is f720–948, not the whole film','resolution':'Report and validation manifest explicitly state the tested interval.'}],
 'verified':['Direct Blender reopen: f0–1392, preview restriction off, 12fps, CAM_MASTER, 304 objects','S6 tail camera and both S7 outbound actors move','Source/proposal/master hashes match','All 1393 rendered PNG hashes and packaged video/contact hashes match','Build, preservation, handoff and regression code plus representative renders inspected'],
 'known_visual_limitation':'Crane briefly occludes part of vehicle at f692–700; retained from adopted proposal.', 'pass':True}
write(B/'review/final-review.json',review)

report=B/'report.md'
t=report.read_text(encoding='utf-8')
t=t.replace('실제 차량·문·창고·도크 메시의 0.25프레임 충돌 검사.','f720–948 실제 차량·문·창고·도크 메시의 0.25프레임 충돌 검사(1,650,704쌍, 금지 관통 0건).')
t=t.replace('영상 재생 및 독립 최종 검토는 별도 기록으로 남긴다.','독립 최종 검토에서 Critical/Important 지적은 없었다. 직접 재개방과 1,393개 렌더 해시도 확인했다. 브라우저 원속도 재생 결과는 `review/playback.json`에 기록한다.')
t += '\n## 최종 검사 결과\n\n전체 조건 7개, 기존 동작 23개, 차량 5개, 제안 구도 14개 검사가 통과했다. 출발 이후 바퀴 접지 오차는 최대 0.0000162m다. 인양 연결 충돌 검사는 f216–624, 도크 SAT 검사는 f720–948 범위이며, 전 구간 연속 시간 충돌 검사를 했다는 의미는 아니다.\n\n최종 마스터 SHA256: `'+mh+'`. 원본은 보존했으며 현재 마스터 지정은 `../CURRENT-MASTER.md`를 따른다.\n'
report.write_text(t,encoding='utf-8')

(B/'README.md').write_text('''# 현재 전체 통합 마스터

- 파일: [master-full-layout-v001.blend](master-full-layout-v001.blend)
- 범위: S1–S7, f0–1392, 12fps, 프리뷰 범위 제한 해제.
- [전체 영상](preview/full.mp4) · [검토 페이지](http://127.0.0.1:8768/review.html) · [검증 보고서](report.md)
- 사용자 “전체 마스터에 통합해라” 지시를 반영했다. 원본과 별도 제안본은 보존했다.
- f692–700의 짧은 크레인 가림은 채택 제안본과 동일하게 남아 있다.

현재 렌더는 raw-3e111ab2이며 render-full.json과 package-record.json이 출처를 연결한다. 다른 raw 폴더, render-stills.json, .blend1은 이전 시험·백업 자료이며 최종 결과가 아니다.
''',encoding='utf-8')
(ROOT/'blockout/CURRENT-MASTER.md').write_text('# 현재 Blender 마스터\n\n[master-full-layout-v001.blend](full-layout-master-v001/master-full-layout-v001.blend)\n\n사용자의 “전체 마스터에 통합해라” 지시에 따라 S4-05 기준 배치·동선 제안과 S1–S7 전체를 통합했다. f0–1392, 12fps. 원본 보존.\n\nSHA256: `'+mh+'`\n\n[검증 보고서](full-layout-master-v001/report.md) · [전체 영상](full-layout-master-v001/preview/full.mp4)\n',encoding='utf-8')

d=read(R/'review-decisions.json')
d['current_question']=None
d['layout_proposal']['status']='adopted for full-master integration by explicit user instruction'
d['layout_proposal']['user_final_approval']='전체 마스터에 통합해라.'
d['full_master_integration']={'authorization':'전체 마스터에 통합해라.','source':'actual user message in current conversation','status':'complete','path':str(master),'sha256':mh,'range':[0,1392]}
for c in d.get('user_concerns',[]): c['status']='layout proposal adopted and integrated into full master; historical finding retained'
d['reference_choice']['approved_master_changes']=True
d['baseline']['status']='historical Stage3 source; current master superseded by authorized full integration'
write(R/'review-decisions.json',d)
with (R/'progress.md').open('a',encoding='utf-8') as f:
 f.write('\nFull-master integration authorized by user: “전체 마스터에 통합해라.” Completed at blockout/full-layout-master-v001/master-full-layout-v001.blend, SHA '+mh+'. f0–1392/12fps. Full7, regression23, wheel5, layout14 checks pass; handoff and dock SAT pass in documented intervals; opening and adopted local composition preservation pass. Original unchanged. Fresh read-only final reviewer: no Critical/Important. Six line-art panels and style selection remain separate from this master integration.\n')
notice='> 현재 전체 마스터: [S1–S7 통합 결과](../../blockout/full-layout-master-v001/README.md). 사용자 통합 지시를 반영했으며, 아래 내용은 이전 단계의 기록입니다. 선화 후보의 최종 선택은 별개입니다.\n\n'
for name in ['README.md','report.md']:
 p=R/name
 if p.exists(): p.write_text(notice+p.read_text(encoding='utf-8'),encoding='utf-8')
banner='<div style="padding:24px;background:#174c3b;color:white"><a style="color:white;font-size:22px" href="http://127.0.0.1:8768/review.html">현재 전체 마스터: S1–S7 통합 영상과 Blender 파일</a><p>사용자의 통합 지시를 반영했습니다. 아래 자료는 이전 제안·진단 기록입니다.</p></div>'
for p in [R/'review.html',R/'layout-proposal-v001/review.html']:
 t=p.read_text(encoding='utf-8')
 p.write_text(banner+t,encoding='utf-8')
print('Final records updated for',mh)
