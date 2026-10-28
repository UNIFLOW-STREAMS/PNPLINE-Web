from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];q=json.loads((R/'review/coast-verified-v032.json').read_text());assert all(q['checks'].values());blend=R/'review/layout-proposal-v032.blend';assert hashlib.sha256(blend.read_bytes()).hexdigest()==q['sha256']
report='''# 양측 해안 경사면 v032

기준: review/layout-proposal-v031.blend
수정 파일: review/layout-proposal-v032.blend

양측 해안 수직 벽의 하단을 바다 쪽으로 확장했다. 왼쪽 최대 5.8m, 오른쪽 최대 8m이며, 상단에서 부드럽게 경사가 시작되고 하단은 실제 바다 메시의 표면보다 6cm 아래에서 연결된다. 왼쪽 앞쪽 끝은 출항 선박의 통과 폭을 피해 점진적으로 줄였다.

상부 지면·건물·수로·교량·문자·크레인·카메라·애니메이션은 그대로이며 SF_COAST_FOLDED_FACE 메시만 변경했다. 원본 v031은 보존했다.

저장본 재개방 후 10개 검사 통과: 67개 액션, 전체 정수 프레임의 카메라 및 주요 동작 변환 보존, 유일한 메시 변경, 상단 이음새 0, 정면 부두 하단 보존, 양측 경사 폭, 21개 단면의 자기 교차 없음, 면적 0인 면 없음, 전체 프레임에서 새 경사면과 선체의 표면 교차 없음. 기존 원본 장면 전체의 물리적 충돌 검사나 파도 시뮬레이션을 뜻하지 않는다.

coast-wide-v031.png / coast-wide-v032.png는 양쪽 끝을 한 화면에서 비교하도록 렌더 때만 렌즈를 0.8배로 넓힌 확인용 이미지다. Blender 저장본의 렌즈와 카메라는 변경하지 않았다. coast-full-v032.png는 원래 카메라 구도의 렌더다.

재현: v031을 열어 scripts/slope_outer_coast.py 실행 후 verify_coast_slopes.py로 저장본을 검사한다.
'''
(R/'review/coast-revision-v032.md').write_text(report,encoding='utf-8')
section='''<section id="coast-v032" style="padding:24px;background:white;border:3px solid #257c8c;margin-bottom:32px"><h1>양측 해안 경사면 v032</h1><p>양쪽 수직 벽을 바다 쪽으로 내려가는 경사면으로 변경했습니다. 상부 도시와 카메라·애니메이션은 유지했습니다.</p><div class="grid"><figure><img src="inputs/coast-left-reference.png" style="width:100%;max-height:440px;object-fit:contain;aspect-ratio:auto"><figcaption>스타일프레임 · 왼쪽</figcaption></figure><figure><img src="inputs/coast-right-reference.png" style="width:100%;max-height:440px;object-fit:contain;aspect-ratio:auto"><figcaption>스타일프레임 · 오른쪽</figcaption></figure></div><div class="grid"><figure><a href="review/coast-wide-v031.png"><img src="review/coast-wide-v031.png" style="width:100%;aspect-ratio:auto"></a><figcaption>수정 전 v031 · 수직 해안</figcaption></figure><figure><a href="review/coast-wide-v032.png"><img src="review/coast-wide-v032.png" style="width:100%;aspect-ratio:auto"></a><figcaption>수정 후 v032 · 양측 경사면</figcaption></figure></div><p>위 비교는 양쪽 끝을 보기 위한 넓은 렌즈의 확인용 렌더입니다. 저장본 카메라는 그대로입니다. 왼쪽 앞부분은 선박 출항 경로를 피해 경사 폭을 줄였습니다.</p><p><a href="review/layout-proposal-v032.blend"><b>Blender: layout-proposal-v032.blend</b></a> · <a href="review/coast-verified-v032.json">검증 10/10</a> · <a href="review/coast-revision-v032.md">변경 기록</a> · <a href="review/coast-full-v032.png">원래 카메라 구도</a></p></section>'''
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ');p.write_text(html[:start]+section+html[start:],encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8')as f:f.write('\n\n## 양측 해안 경사면 v032\n양쪽 외벽을 바다 방향 경사면으로 변경. 왼쪽 출항 경로를 피해 앞끝 폭 조정. 10개 검사 통과. 파일 review/layout-proposal-v032.blend.\n')
paths=[blend,R/'review/coast-full-v032.png',R/'review/coast-wide-v032.png'];assert all(p.exists()for p in paths)
(R/'review/coast-delivery-v032.json').write_text(json.dumps({'checks':q['checks'],'hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}},indent=2))
print('Packaged coast-v032')
