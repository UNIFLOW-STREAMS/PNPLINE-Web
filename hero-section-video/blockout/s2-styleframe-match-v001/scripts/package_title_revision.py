from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=R/'review.html';html=p.read_text(encoding='utf-8')
start=html.index('<section ');end=html.index('</section>',start)+len('</section>')
section='''<section style="background:white;padding:20px;border:3px solid #278195;margin-bottom:30px">
<h1>CHINA 곡률 보강 · C를 수로 가까이 — v006</h1>
<p>C를 수로 쪽으로 당기고, CHINA 전체의 원호 반경을 38 → 28로 줄였습니다. C의 정면이 지나치게 좁아지지 않도록 원호 방향을 함께 조정했습니다. 양쪽 구름도 끝 글자의 위치에 맞춰 옮겼으며, 앞서 확대한 오른쪽 구름 크기를 유지했습니다.</p>
<div class="grid"><figure><img src="review/design-proposal-v004.png"><figcaption>수정 전 v004 · 곡률이 완만하고 C가 뒤에 있음</figcaption></figure><figure><img src="review/design-proposal-v006.png"><figcaption>수정 후 v006 · C가 수로 가장자리에서 도시를 감쌈</figcaption></figure></div>
<details><summary>컨셉 원본 전체 보기</summary><img src="inputs/s2-styleframe-001.png"></details>
<p><a href="review/layout-proposal-v006.blend">Blender 수정 제안본 v006</a> · <a href="review/design-proposal-v006.png">렌더 원본</a> · <a href="review/title-arc-verified-v006.json">원호·A·구름 검사</a> · <a href="review/title-scope-v006.json">변경 범위 검증</a></p>
<p class="small">이번 변경은 문자와 양쪽 구름에 한정했습니다. 나머지 2,606개 오브젝트의 검사 항목과 48개 애니메이션 액션은 v004와 동일합니다. 전체 스타일프레임 작업의 최종 마스터는 아닙니다. 기존 카메라 f104 회전 연속성 검사 실패와 크레인·전체 구도 정합은 별도 미결 사항입니다.</p>
</section>'''
p.write_text(html[:start]+section+html[end:],encoding='utf-8')
report='''# CHINA / C 곡률 수정 v006

사용자 최신 피드백: C가 수로에 가까이 와서 도시를 더 깊게 감싸야 함.

v004를 직접 읽어 CHINA 공통 원호 반경 38 → 28, 방향 -18° → -8°, 중점 Y 29 → 28로 변경했다. 원호를 역변환한 다음 새로운 원호로 모든 금색·붉은 문자 메시를 재변형했다. C의 위치는 (-20.378, 30.576, 1.25) → (-20.144, 25.452, 1.25). 양쪽 구름을 끝 글자의 변위에 맞춰 이동했다. 카메라와 도시·항만·선박은 이번 수정에서 변경하지 않았다.

v005의 반경 24 안은 C 정면이 너무 좁게 보여 v006으로 조정했다. 새 저장본을 별도 Blender 프로세스로 다시 열고 Cycles CPU 24 samples로 f156을 렌더했다. 컨셉 이미지와 수정 전후 이미지는 review.html에서 비교할 수 있다.

검증: c_wrap baseline RED 후 v006 GREEN; title_arc 3/3 PASS. verify_title_scope에서 나머지 오브젝트 2,606개와 액션 48개 비교 통과. 수로까지의 하단 테두리 최소 평면 거리 검사는 배치 접근의 증거이며, 모든 지지면 접촉 검사를 대체하지 않는다.

전체 작업 미결: v004에서 물려받은 f104 카메라 회전 연속성 실패(29개 검사 중 1개 실패), 크레인 비중 및 전체 컨셉 정합, 최종 전체 영상·접촉 검증. 이번 문자 수정 완료를 전체 마스터 완료로 해석하지 않는다.

재현: review/layout-proposal-v004.blend를 열고 scripts/recurve_title.py -- <새 출력 경로> 실행. v006 config는 review/title-arc-v006-config.json에 기록. 원본 마스터와 기존 제안본은 보존.
'''
(R/'review/title-revision-v006.md').write_text(report,encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8') as f:f.write('\n\n## 사용자 피드백 반영: CHINA v006\nC를 수로에 가깝게 하고 전체 곡률을 키움. 수정 및 검증 상세: review/title-revision-v006.md. S2 카메라 조정안 작성은 사용자 승인됨. 이번 v004→v006 변경은 문자·구름만 해당.\n')
# Normalize the active v004 generator camera config to UTF-8 without BOM.
q=R/'camera-settings.json';q.write_text(json.dumps({'position':[22,47,32],'target':[4,-12,5]}),encoding='utf-8')
