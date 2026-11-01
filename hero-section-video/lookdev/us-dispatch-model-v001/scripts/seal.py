"""Publish the audited candidate to the explicitly requested lookdev master."""
from pathlib import Path
import hashlib,json,shutil,re
R=Path(__file__).resolve().parents[1]
L=R.parent
target=L/'hero-material-v001/pnpline-hero-material-v001.blend'
source=R/'inputs/before-dispatch.blend'
candidate=R/'candidate.blend'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
audit=json.loads((R/'audit/preservation-verification.json').read_text())
assert audit['passed'],audit['checks']
truck=json.loads((R/'audit/truck-clearance.json').read_text())
assert truck['passed'] and truck['candidate_sha256']==audit['result_sha256']
assert all((R/'review'/p).is_file() for p in ['render-overview.png','before/render-overview.png','before/render-900.png','render-870.png','render-900.png','render-930.png','render-950.png','render-989.png'])
assert sha(candidate)==audit['result_sha256']
assert sha(source)==audit['source_sha256']
assert sha(target)==sha(source),'Requested master changed concurrently; do not overwrite.'
version=R/'pnpline-us-dispatch-model-v001.blend'
shutil.copy2(candidate,version)
stage=target.with_name('pnpline-hero-material-v001.dispatch-staged.blend')
assert not stage.exists()
shutil.copy2(candidate,stage)
assert sha(stage)==audit['result_sha256']
stage.replace(target)
assert sha(version)==sha(target)==audit['result_sha256']
pointer=L/'latest-lookdev.json'
shutil.copy2(pointer,R/'inputs/previous-latest-lookdev.json')
ref=Path('F:/pnpline-landing/hero-section-video/concept-design/us-dispatch-campus-v001/01-dispatch-district-concept.png')
shutil.copy2(ref,R/'inputs/approved-concept.png')
build=json.loads((R/'review/build.json').read_text())
times=dict((a,float(b)) for a,b in re.findall(r'RENDERED (\w+) ([\d.]+)',(R/'render.log').read_text()))
delivery={'file':str(target),'versioned_copy':str(version),'sha256':sha(target),'source':str(source),'source_sha256':sha(source),'concept':str(R/'inputs/approved-concept.png'),'concept_sha256':sha(ref),'build':build,'verification':str(R/'audit/preservation-verification.json'),'review_frames':[870,900,930,950,989],'overview_frame':890,'review_renderer':'Cycles / OptiX / 64 samples / adaptive .025 / denoise','review_render_seconds':times,'preserved_timeline':{'fps':30,'start':0,'end':989},'truck_clearance_report':str(R/'audit/truck-clearance.json')}
(R/'delivery.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2),encoding='utf-8')
pointer.write_text(json.dumps({'file':str(target),'sha256':sha(target),'versioned_copy':str(version),'source':str(source),'source_sha256':sha(source),'review':str(R/'review.html'),'preservation':str(R/'audit/preservation-verification.json'),'delivery':str(R/'delivery.json'),'previous_lookdev_record':str(R/'inputs/previous-latest-lookdev.json'),'fps':30,'frame_start':0,'frame_end':989,'status':'US dispatch district modeling applied; Cycles frames and 990-frame preservation verified'},ensure_ascii=False,indent=2),encoding='utf-8')
readme=f'''# 미국 출고·배송 분기 구역 모델링 v001

승인된 컨셉을 실제 Blender 메시로 제작하여 지정된 `lookdev/hero-material-v001/pnpline-hero-material-v001.blend`에 반영했다. `pnpline-us-dispatch-model-v001.blend`는 동일 바이트의 버전 보관본이다.

- 결과 SHA256: `{sha(target)}`
- 수정 전 파일: `inputs/before-dispatch.blend`
- 수정 전 SHA256: `{sha(source)}`
- 승인 컨셉: `inputs/approved-concept.png`

## 구현

- 기존 창고·출고 마당·Y자 차량 경로를 중심으로 2–3층 석재/벽돌 상가 8동을 양쪽에 배치했다. 창틀, 코니스, 파라펫, 상가 차양, 서비스 출입구, 옥상 HVAC·루버·환기구를 메시로 제작했다.
- 활엽수 {len(build['trees'])}그루, 낮은 관목, 분기 중앙 녹지, 창고 측면의 낮은 정원과 산책로, 해안 보도·벤치·가로등·석재 호안을 추가했다. 분기 꼭짓점은 낮은 식재로 유지했다.
- 기존 중복 도로 표면을 숨기고 동일 중심선·접점 높이의 세분화된 Y자 표면과 차선·연석·보도·배수구를 추가했다. 지면과 녹지는 `mapping.graded`에 맞추고 구조물은 해당 면의 법선에 정렬했다.
- 창고 패널 배튼·지붕 이음·옥상 설비와 출고 마당 줄눈을 추가했다. 두 기존 출고 차량에는 유리창·미러·그릴·등화·범퍼·휠 디테일을 자식 메시로 연결했다.
- 새 오브젝트 {build['new_objects']:,}개는 `DSP_DISPATCH_DISTRICT` 컬렉션과 `DSP_` 접두사로 구분했다. 원래 목적지 프록시 4개와 겹치던 도로/지지 표면 4개만 가시성을 껐다. 원래 메시 데이터는 보존했다.
- 새 재질은 로컬 좌표를 사용하는 절차형 셰이더이며 외부 이미지 텍스처를 추가하지 않았다. 기존 PNPLINE 문자, 도시·항만, 재질·조명·색 관리는 유지했다.

## 확인

- `audit/preservation-verification.json`: 원본 23,851개 오브젝트, 101개 액션, 추적 대상 100개의 0–989프레임 변환과 카메라 광학값 대조. 선언한 가시성 변경 외 원본 형상·애니메이션 변경 없음, 변환 오차 0.
- 전체 카메라 이동과 근접 평면에 새 구조물의 교차 없음. S7 카메라–타깃 선분의 새 장애물 없음.
- `audit/truck-clearance.json`: S7 출고 차량과 새 고정 구조물의 삼각형 및 코너 이동 검사. 검사 방식·한계와 결과는 해당 보고서에 기록했다.
- 실제 CAM_MASTER의 870/900/930/950/989프레임을 1920×1080 Cycles로 확인했다. 별도 검토용 카메라의 전체 조감도는 1200×1400이며 최종 파일에는 이 카메라를 저장하지 않았다.
- 동일 검토 카메라·프레임의 수정 전 렌더는 `review/before/`, 결과는 `review/`에 있다. `review.html`에서 비교할 수 있다.
- 이번 검토는 모델링과 정지 프레임 검토다. 전체 영상을 새로 렌더하거나 이전 룩개발의 미완료 UI 재생 검토를 완료한 것으로 표기하지 않는다. 컨셉의 생성 이미지와 최종 카메라 투영은 다르며 기존 도로 동작·구면 지형을 우선했다.

## 재현

Blender 5.1 / Windows. `scripts/build.py`는 수정 전 백업에서 실행하며 `candidate.blend`를 만든다. 반복 실행 시에도 항상 백업에서 시작한다. 프로젝트의 기존 `blockout/curvature-rework-v001/scripts/mapping.py`와 `blockout/cn-shanghai-density-v001/scripts/citykit.py`를 사용한다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup '{source.as_posix()}' -t 6 --python-exit-code 1 --python '{(R/'scripts/build.py').as_posix()}'
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup '{version.as_posix()}' -t 6 --python-exit-code 1 --python '{(R/'scripts/render.py').as_posix()}' -- overview 870 900 930 950 989
```

최종 파일의 렌더 설정과 30fps/0–989 시간 구간은 원본 그대로다. 검토 스크립트만 일시적으로 64샘플을 사용하며 파일을 저장하지 않는다. 실행 시간은 `delivery.json`에 기록했다.
'''
(R/'README.md').write_text(readme,encoding='utf-8')
frames=''.join(f'<figure><img loading="lazy" src="review/render-{f}.png"><figcaption>CAM_MASTER · {f}F</figcaption></figure>' for f in [870,900,930,950,989])
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PNPLINE · Dispatch model v001</title><style>body{margin:0;background:#111b23;color:#f0f3f5;font:16px system-ui;line-height:1.6}main{max-width:1500px;margin:auto;padding:32px}h1{font-size:30px}p{color:#c2cdd5}figure{margin:0 0 28px}img{display:block;width:100%;border-radius:8px}figcaption{padding:8px 0}.compare{display:grid;grid-template-columns:1fr 1fr;gap:20px}a{color:#65c7e8}@media(max-width:650px){.compare{grid-template-columns:1fr}}</style><main><h1>미국 출고·배송 분기 구역</h1><p>상가 8동 · 수목 67그루 · Y자 도로와 중앙 녹지 · 출고 차량 디테일. 실제 Blender / Cycles 결과.</p><div class="compare"><figure><img src="review/before/render-overview.png"><figcaption>수정 전 · 조감도 890F</figcaption></figure><figure><img src="review/render-overview.png"><figcaption>모델링 반영 · 같은 검토 카메라 890F</figcaption></figure></div><p>기존 카메라와 0–989프레임 애니메이션은 보존했다. 다음 이미지는 기존 CAM_MASTER의 실제 프레임이다.</p>'''+frames+'''<p><a href="README.md">작업·검증 기록</a> · <a href="audit/preservation-verification.json">990프레임 대조</a> · <a href="pnpline-us-dispatch-model-v001.blend">버전 보관본</a></p></main></html>'''
(R/'review.html').write_text(html,encoding='utf-8')
old=L/'hero-material-v001/README.md'
old.write_text('> **후속 모델링 반영:** 미국 출고·배송 구역이 이 폴더의 `.blend`에 추가되었습니다. 현재 해시: `'+sha(target)+'`. 최신 기록: [us-dispatch-model-v001](../us-dispatch-model-v001/README.md). 아래 재질·조명 작업 기록과 해시는 모델링 추가 전의 기록입니다. 해당 파일은 `../us-dispatch-model-v001/inputs/before-dispatch.blend`에 보존했습니다.\n\n'+old.read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'published':str(target),'sha256':sha(target),'backup':str(source),'trees':len(build['trees']),'objects':build['new_objects']},indent=2))
