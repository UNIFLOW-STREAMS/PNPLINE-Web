import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];B=R.parent;Q=B/'route-b-a-side-v001';m=json.loads((R/'delivery.json').read_text(encoding='utf-8'));v=json.loads((R/'verification.json').read_text());assert all(v['checks'].values())
assert hashlib.sha256(Path(m['file']).read_bytes()).hexdigest()==m['sha256']
a=Image.open(R/'review/f0156.png').convert('RGB');b=Image.open(Q/'review/city-final/f0156.png').convert('RGB');assert ImageChops.difference(a,b).getbbox()is None,'Overview differs from selected candidate'
m['verification']=v['checks'];m['f156_pixel_identical_to_reviewed_candidate']=True
(R/'delivery.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
index=B/'latest-previz.json'
assert not index.exists(),'Existing latest pointer requires review before replacement'
index.write_text(json.dumps({'file':m['file'],'sha256':m['sha256'],'adopted_on':m['adopted_on'],'choice':'city rotation','delivery':str(R/'delivery.json'),'known_issues':m['known_issues'],'status':m['release_status']},ensure_ascii=False,indent=2),encoding='utf-8')
(Q/'adoption.json').write_text(json.dumps({'adopted_on':m['adopted_on'],'selected':'city-rotation-v002','master':m['file'],'master_sha256':m['sha256'],'scope':'Layout/motion option adopted; known contact issues remain. B route not selected.'},ensure_ascii=False,indent=2),encoding='utf-8')
page=(Q/'review.html').read_text(encoding='utf-8');notice='<div class="notice"><strong>2026-10-29 · 도시 회전안 채택 완료</strong><br>최신 프리비즈: <code>'+m['file']+'</code><br>아래 비교는 채택 전 검토 이력입니다. 해안·선체 겹침은 후속 수정 사항으로 남습니다.</div>'
page=page.replace('<h1>',notice+'<h1>',1);(Q/'review.html').write_text(page,encoding='utf-8')
with (Q/'report.md').open('a',encoding='utf-8')as f:f.write('\n\n## 2026-10-29 사용자 채택 결정\n\n사용자가 도시 회전안을 채택했습니다. 최신 전체 프리비즈는 `'+m['file']+'`입니다. 앞선 미채택 판정과 비교는 당시 검토 이력으로 남깁니다. 방향·동선 선택은 확정됐고 잔존 접촉 문제는 후속 수정 사항입니다. 새 저장본의 내용 동일성과 대표 렌더를 검증했습니다. B 항로는 채택하지 않았습니다.\n')
print('ADOPTION_FINALIZED',m['file'],m['sha256'])
