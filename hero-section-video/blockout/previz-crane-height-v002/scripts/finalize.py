from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[1];out=R/'master-previz-crane-height-v002.blend'
sha=hashlib.sha256(out.read_bytes()).hexdigest();assert sha=='61a08f1be06c6239ba40fcb40ee35628457fb2f4328432e945eb6316156225e6'
srcsha='c21292bb055930d745ad37e9a3f4f732743043d5528429c030b9f366ff6e1942'
assert hashlib.sha256((R/'inputs/base.blend').read_bytes()).hexdigest()==srcsha
checks={}
for name in ['after-short-rope.json',out.stem+'-lift.json','connections.json','scope.json',out.stem+'-dense.json',out.stem+'-internal.json']:
 r=json.loads((R/'review'/name).read_text());assert r['sha256']==sha
 ok=all(r['checks'].values())if 'checks'in r else r['pass'];assert ok,name;checks[name]=ok
red=json.loads((R/'review/before-short-rope.json').read_text());assert not all(red['checks'].values())
for label,expected in [('before',srcsha),('after',sha)]:
 m=json.loads((R/'review'/label/'metadata.json').read_text());assert m['sha256']==expected and m['frames']==list(range(0,157,2))
 subprocess.run(['ffmpeg','-v','error','-i',str(R/'review'/f'{label}.mp4'),'-f','null','-'],check=True)
summary={'file':str(out),'sha256':sha,'source_sha256':srcsha,'pass':True,'checks':checks,'visual_review':'Compared f0 and lowering sequence: rope nearly reeled in, container visibly higher with camera unchanged; f72 landing identical.','baseline_regression_failed':True,'limits':'Dense sampled BVH tests exclude intended attached bearing/rail/twistlock contact; unrelated S4-S7 contact geometry unchanged.'}
(R/'verification-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
d=json.loads((R/'delivery.json').read_text());d.update(status='Verified and adopted',verification=str(R/'verification-summary.json'),review_url='http://127.0.0.1:18779/review.html',initial_rope_length_m=.200037,previous_rope_length_m=.700037,camera='unchanged');(R/'delivery.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
registry=R.parent/'latest-previz.json';old=json.loads(registry.read_text());assert old['sha256']==srcsha
assert hashlib.sha256(Path(old['file']).read_bytes()).hexdigest()==srcsha
(R/'inputs/previous-latest-previz.json').write_text(json.dumps(old,indent=2),encoding='utf-8')
old.update(file=str(out),sha256=sha,adopted_on='2026-10-29',choice='Raised crane with tighter initial hoist ropes',delivery=str(R/'delivery.json'),verification=str(R/'verification-summary.json'),status='Adopted; initial rope and collision checks passed')
registry.write_text(json.dumps(old,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# 첫 프레임 인양 줄 길이 수정

최종 파일: `master-previz-crane-height-v002.blend`

첫 프레임에서 컨테이너·인양 장치·내부 화물을 50cm 더 올렸습니다. 노출된 줄 길이는 70cm에서20cm로 줄었습니다. 카메라와 크레인 형상·높이는 바꾸지 않았습니다.

추가 높이 차이는 f72까지 부드럽게 줄어들며 기존 안착 위치·시점으로 연결됩니다. f72 이후 변경 대상의 모든 곡선을 1/8프레임 간격으로 대조했고 정확히 동일합니다. 나머지 액션 및 형상도 동일합니다.

원본에서 줄 길이 검증이 실패하고 수정본에서 통과하는 것을 확인했습니다. 인양 헤드와 스프레더 사이의 충돌·여유, 네 줄의 연결점, 내부 화물, 크레인 내외부 간섭 검사를 통과했습니다. 근거는 `verification-summary.json`과 `review/*.json`에 있습니다.

`review.html`은 v001과 v002의 동일 카메라 프리뷰 비교입니다. f0–156, 원본12fps 시간, 2프레임 간격 샘플. 이전 파일은 수정하지 않았으며 `inputs/base.blend`에도 보존했습니다. 커밋하지 않았습니다.
''',encoding='utf-8')
print('FINALIZED',out,sha)
