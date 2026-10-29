# PNPLINE warehouse handoff

최종 파일: `candidate-warehouse-v008.blend` (Blender 5.1.0).
기존 저장소의 `main`에서 작업. 별도 워크트리 없음. 원본은 `inputs/arrival-v010.blend`.

## 다시 생성

PowerShell, 저장소 루트에서 실행. 출력 파일이 이미 있으면 덮어쓰지 않고 중단합니다.

```powershell
$r = 'F:/pnpline-landing/hero-section-video/blockout/warehouse-rework-v001'
$b = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $b --background --factory-startup --python-exit-code 1 --python "$r/scripts/build_warehouse.py" -- --output "$r/rebuilt-warehouse.blend"
```

## 검증

```powershell
& $b --background --factory-startup "$r/rebuilt-warehouse.blend" --python-exit-code 1 --python "$r/tests/test_warehouse.py" --python "$r/tests/test_operations.py" --python "$r/scripts/audit_clearance.py" --python "$r/scripts/audit_preservation.py"
& $b --background --factory-startup "$r/rebuilt-warehouse.blend" --python-exit-code 1 --python "$r/scripts/run_inherited_regression.py"
```

첫 명령은 창고 계약·동작·충돌·보존 검사입니다. 보존 스크립트는 마지막에 원본 파일을 열기 때문에 반드시 명령 끝에 둡니다. 기존 24개 회귀 검사는 원본에도 있던 `P01 cable 0 unsupported` 1건이 실패합니다. 창고 작업 범위 밖의 크레인 결함입니다.

## 렌더링

```powershell
& $b --background --factory-startup "$r/rebuilt-warehouse.blend" --python-exit-code 1 --python "$r/scripts/render.py" -- --label my-stills --frames 768,930,1020,1075,1158,1200 --overview
& $b --background --factory-startup "$r/rebuilt-warehouse.blend" --python-exit-code 1 --python "$r/scripts/render.py" -- --label my-material --frames 1075 --overview --material
& $b --background --factory-startup "$r/rebuilt-warehouse.blend" --python-exit-code 1 --python "$r/scripts/render.py" -- --label my-sequence --sequence
```

동작 비교 영상은 f744–1248의 505프레임 전체를 12fps로 재생합니다. 진단용 정면/전체 카메라는 렌더 실행 중에만 생성하며 저장된 원본 카메라는 바꾸지 않습니다. `.blend`에는 실제 모델과 애니메이션이 포함됩니다. 이 단계의 영상은 최종 광고용 조명/합성 영상이 아닌 동작 검토용입니다.

`report.md`, `decision-log.md`, `review/final-review.md`, `inventory.json`에 변경 범위와 검증 근거를 기록합니다. `review-warehouse.html`을 로컬 HTTP 서버로 열면 전후 영상과 최종 모델 이미지를 볼 수 있습니다.
