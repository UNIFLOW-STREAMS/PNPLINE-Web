from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1]
shutil.copyfile('C:/Users/KIMTAE~1/AppData/Local/Temp/codex-clipboard-42d7666b-3381-486f-8cc8-96f65103525c.png',R/'inputs/cloud-position-reference.png')
p=R/'review.html';html=p.read_text(encoding='utf-8');start=html.index('<section ')
section='''<section style="background:white;padding:20px;border:3px solid #278195;margin-bottom:30px"><h1>A 오른쪽 구름 위치 수정 — v007</h1>
<p>컨셉처럼 구름을 A의 뒤쪽·아래쪽에 배치했습니다. 글자의 오른쪽 가장자리에서 구름 일부만 드러납니다. 구름의 크기와 형상은 v006 그대로이며 위치만 변경했습니다.</p>
<div class="grid" style="grid-template-columns:repeat(3,minmax(0,1fr))"><figure><img src="inputs/cloud-position-reference.png" style="aspect-ratio:1"><figcaption>컨셉 위치</figcaption></figure><figure><img src="review/cloud-detail-v006.png" style="aspect-ratio:1"><figcaption>수정 전 v006</figcaption></figure><figure><img src="review/cloud-detail-v007.png" style="aspect-ratio:1"><figcaption>수정 후 v007 · Blender 직접 렌더</figcaption></figure></div>
<p><a href="review/layout-proposal-v007.blend">Blender 수정본 v007</a> · <a href="review/design-proposal-v007.png">전체 렌더</a> · <a href="review/right-cloud-green-v007.json">위치·가림 검사</a> · <a href="review/title-scope-v007.json">변경 범위 검사</a></p>
<p class="small">오른쪽 구름 루트 위치만 수정. 다른 2,622개 오브젝트 검사 항목과 48개 액션은 v006과 동일합니다. 전체 마스터 확정 전 제안본입니다.</p></section>'''
html=html[:start]+section+'<details><summary>이전 CHINA 곡률 수정 기록</summary>'+html[start:]
html=html.replace('</html>','</details></html>');p.write_text(html,encoding='utf-8')
(R/'review/cloud-revision-v007.md').write_text('''# 오른쪽 구름 위치 수정 v007

사용자 요청에 따라 컨셉의 A 오른쪽 뒤, 아래쪽 위치를 재현했다. SF_CLOUD_RIGHT.location만 변경했다. 기존 크기·나선·메시·재질은 유지했다. 원본 v006은 보존했다.

저장본을 다시 열어 f156 전체 렌더와 확대 영역을 직접 렌더했다. right_cloud_position 검사: v006 실제 가림 비율 0%로 RED, v007은 샘플 표면점 중 약 44.7%가 A 뒤에 있어 GREEN. 이 값은 픽셀 가림 면적이 아닌 표면 샘플의 광선 검사 결과이다. 높이/오른쪽 노출 검사도 통과했다. 나머지 2,622개 오브젝트의 변환·메시·가시성 검사와 48개 액션 비교 통과.

재현: layout-proposal-v006.blend에서 scripts/place_right_cloud.py -- <새 출력 경로> 실행. 카메라와 문자는 변경하지 않았으며, 기존 전체 작업의 미결 사항은 title-revision-v006.md를 참조한다.
''',encoding='utf-8')
with (R/'decision-log.md').open('a',encoding='utf-8') as f:f.write('\n\n## 구름 위치 v007\n사용자 컨셉 크롭에 맞춰 SF_CLOUD_RIGHT 위치만 수정. review/cloud-revision-v007.md 참조.\n')
