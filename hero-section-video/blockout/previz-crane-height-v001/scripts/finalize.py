from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[1];out=R/'master-previz-crane-height-v001.blend';sha=hashlib.sha256(out.read_bytes()).hexdigest()
assert sha=='c21292bb055930d745ad37e9a3f4f732743043d5528429c030b9f366ff6e1942'
source_sha='64a206b9104e6c8f0cd0f4c2232bcac8789df47bd2e06cc3207743a87d70ce98'
assert hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest()==source_sha
previous=R.parent/'previz-city-rotation-fix-v001/master-previz-city-rotation-fix-v002.blend'
assert hashlib.sha256(previous.read_bytes()).hexdigest()==source_sha
files=['green-lift.json','scope.json','support.json','contact.json',out.stem+'-dense.json',out.stem+'-internal.json','reviewer-fractional.json']
results={}
for name in files:
 r=json.loads((R/'review'/name).read_text());assert r.get('sha256',r.get('candidate_sha256'))==sha
 ok=all(r['checks'].values())if 'checks'in r else r['pass'];assert ok,name;results[name]=ok
red=json.loads((R/'review/baseline-lift.json').read_text());assert not all(red['checks'].values())
for label,h in [('before',source_sha),('after',sha)]:
 m=json.loads((R/'review'/label/'metadata.json').read_text());assert m['sha256']==h and len(m['frames'])==79
 subprocess.run(['ffmpeg','-v','error','-i',str(R/'review'/f'{label}.mp4'),'-f','null','-'],check=True)
summary={'file':str(out),'sha256':sha,'source_sha256':source_sha,'pass':True,'checks':results,'baseline_regression_failed':True,'visual_review':'Before/after f0,24,48,72,100,138 inspected; clean container roof and unchanged landing. Raised crane remains visible in later overview.','preview':{'range':[0,156],'sample_step':2,'source_fps':12,'video_fps':24,'duration_s':157/12},'limitations':'BVH geometry checks use scoped collision pairs and sampled frames; intentional attached mechanical contacts excluded. Original unrelated S4-S7 contact geometry remains unchanged.'}
(R/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
d=json.loads((R/'delivery.json').read_text());d.update(status='Verified and adopted',verification=str(R/'verification-summary.json'),review_url='http://127.0.0.1:18778/review.html',preserved_source=str(previous));(R/'delivery.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
registry=R.parent/'latest-previz.json';old=json.loads(registry.read_text());assert Path(old['file'])==previous
(R/'inputs/previous-latest-previz.json').write_text(json.dumps(old,indent=2),encoding='utf-8')
old.update(file=str(out),sha256=sha,adopted_on='2026-10-29',choice='City rotation with raised crane and corrected internal payload',delivery=str(R/'delivery.json'),verification=str(R/'verification-summary.json'),status='Adopted; crane-height and payload gates passed')
registry.write_text(json.dumps(old,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# 크레인 높이 및 내부 화물 수정

최종 파일: `master-previz-crane-height-v001.blend`

- 크레인 상부 +3m. 네 다리의 바닥 위치를 유지하고 상부를 연장했습니다.
- 컨테이너 시작점 +2.5m. f72의 기존 안착 위치·시점으로 부드럽게 연결됩니다.
- 초록색 상자는 `W01_NEW_PALLET` 내부 화물입니다. 잘못된 독립 높이 애니메이션을 고쳐 컨테이너 내부 위치를 유지합니다. 가시성을 끄지 않았습니다.
- S1 카메라와 타깃을 높아진 시작점에 맞춰 함께 이동했습니다. f72 이후 카메라·컨테이너·화물은 원본과 동일합니다.
- 케이블과 빈 인양 장치 복귀 높이를 맞췄습니다.

수정 전 저장본은 `inputs/base.blend`, 원본 최신 파일은 변경하지 않았습니다. 원본은 이전 등록 이후 사용자가 다시 저장한 SHA256 64a206… 버전입니다.

## 검증

원본 실패 → 수정본 통과 회귀 검증. S1 내부 화물 289개 샘플, 크레인 외부 간섭 1041개 샘플, 내부 간섭 625개 샘플, 정적 지지부·접지 검사를 통과했습니다. f72 이후 28개 애니메이션 곡선은 1/8프레임 간격에서 원본과 오차 0입니다. 전체 시간축의 보호 대상 동작도 동일합니다. 자세한 결과와 파일 해시는 `verification-summary.json` 및 `review/*.json`에 있습니다.

`review.html`에서 f0–156 수정 전후 영상을 비교할 수 있습니다. 640×360 Workbench 프리뷰이며 원본 12fps 시간, 2프레임 간격 샘플을 24fps 영상으로 인코딩했습니다. 재생 속도 선택은 프리뷰에만 적용됩니다.

기존 S4–S7 창고 접촉 형상은 이번 요청 범위 밖이며 그대로 보존했습니다. Git 커밋은 수행하지 않았습니다.
''',encoding='utf-8')
print('FINALIZED',out,sha)
