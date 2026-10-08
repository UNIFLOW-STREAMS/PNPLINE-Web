# S4–S5 경계 검토본

구현 기준은 `inputs/master-s4-fix.blend`입니다. 원본 SHA-256은 `config.json`에 고정했고 원본은 덮어쓰지 않았습니다. `master-with-s5-test-v001.blend`의 차량·카메라·애니메이션은 가져오지 않았습니다.

- 작업본: `master-s4-s5-boundary-v001.blend`, Scene `PNPLINE_MASTER_v005`, Camera `CAM_MASTER`.
- 대표 구도: f648. 다음 S5 작업의 인계 상태: f720.
- 최종 비교: `preview/before.mp4`, `preview/after.mp4`. 둘 다 f596–792, 12fps, 768×432, 197프레임, 약 16.42초.
- 주 검토 대상은 S4 후반~부두 출발입니다. f733–792는 사용자가 승인한 후속 카메라 재접합의 증거로 포함한 기존 주행 구간입니다. 새 선회/후진/문 개방 동작은 제작하지 않았습니다.
- 상세 판정과 한계: `report.md`. 측정 기반 인계 데이터: `boundary-contract.json`.
- `review/camera-only-before-scope-approval.blend`, `preview/camera-only-before-approval.mp4`는 범위 확대 승인 전 조사본이며 최종 후보가 아닙니다.

## 수정 범위

카메라/주시점/렌즈: f608–780. 차량·컨테이너·내부 팔레트: f608–744. 실제 높이 보정은 f720에서 원본으로 복귀하며, f733.25–738.5에 있던 원본의 서브프레임 견인부 간격 약 4.7mm만 추가로 보정합니다. 인양 장치·4개 케이블: f608–666. 각 경계의 원본 키·핸들을 복원하고 범위 밖 평가 결과를 비교했습니다.

부두 접지 높이와 컨테이너 안착·인양 장치, f720 이후 카메라 연결까지 수정하는 범위는 사용자 승인 후 적용했습니다. 차량의 XY 주행 경로, 기존 출발/정박/문 개방 시각, 도로·부두·창고 형상과 위치는 유지했습니다. 견인부 정렬을 위한 5mm 미만의 보정은 별도로 기록했습니다.

## 재현

현재 설치 환경: Blender 5.1.0 (`adfe2921d5f3`), Python 3.13.9, FFmpeg 7.1. 아래 PowerShell 명령은 저장소 루트에서 실행합니다. 스크립트는 원본과 출력 경로가 같으면 거부합니다. 실행 중인 GUI의 미저장 상태를 사용하지 않습니다.

```powershell
$r = 'F:/pnpline-landing/hero-section-video/blockout/s4-s5-boundary-v001'
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$python = 'C:/ProgramData/miniconda3/python.exe'
& $blender -b "$r/inputs/master-s4-fix.blend" --python-exit-code 1 --python "$r/scripts/revise_boundary.py" -- --input "$r/inputs/master-s4-fix.blend" --output "$r/master-s4-s5-boundary-v001.blend" --config "$r/config.json" --scene PNPLINE_MASTER_v005
& $python -X utf8 "$r/scripts/run_final.py" verify
& $python -X utf8 "$r/scripts/run_final.py" reproduce
& $python -X utf8 "$r/scripts/run_final.py" before
& $python -X utf8 "$r/scripts/run_final.py" after
& $blender -b "$r/master-s4-s5-boundary-v001.blend" --python-exit-code 1 --python "$r/tests/test_frame_visibility.py"
& $python -X utf8 "$r/tests/test_preservation.py"
& $python -X utf8 "$r/tests/test_acceptance.py"
& $python -X utf8 "$r/scripts/package_delivery.py"
```

기준 서명을 처음부터 다시 확보할 때:

```powershell
& $blender -b "$r/inputs/master-s4-fix.blend" --python-exit-code 1 --python "$r/scripts/capture_scope.py" -- --scene PNPLINE_MASTER_v005 --config "$r/config.json" --output "$r/review/before-signature.json"
```

1배속 재생 검증은 설치된 Chrome/Playwright를 사용했습니다. 새 라이브러리를 설치하지 않습니다.

```powershell
$runtime = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
$env:PNPLINE_PLAYWRIGHT_PATH = Join-Path $runtime 'node_modules/playwright'
$env:PNPLINE_CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
& (Join-Path $runtime 'bin/node.exe') "$r/scripts/playback_review.cjs"
```

`logs/commands-*.json`에는 실행 인자·실제 종료 코드가 있습니다. 로컬 애드온의 background GPU/등록·해제 경고는 장면 검사 실패와 구분합니다. `test_boundary.py`의 `test_baseline_departure_support`는 원본의 실패를 보존하는 진단이며 최종 후보 수용 검사는 `test_acceptance.py`입니다.

## 검증 한계

시설 충돌은 메시의 방향 있는 바운딩박스(SAT), 카메라는 0.1m 구와 메시 박스로 근사했습니다. 바닥은 모든 8개 바퀴 아래의 BVH 광선과 평가된 다각형 바퀴의 최저점으로 조사했습니다. 0.25프레임 샘플이며 연속 충돌을 수학적으로 보장하지 않습니다. 바다 구체는 속이 찬 시설 박스가 아니므로 시설 충돌에서 제외했고, 부두/도로/마당은 별도의 접지 검사에 포함했습니다. 내부 팔레트는 차량과 함께 움직이는 화물로 분류했습니다.

건물/도로 가시성은 유한한 표면 광선 샘플과 실제 렌더를 함께 확인합니다. 면적 가중 가시율이나 모든 픽셀의 가시성 보장이 아닙니다. 단순 중심점 투영으로 수용하지 않습니다.

커밋·push·PR·원본 덮어쓰기·S5 전체 통합·S6 수정·외부 업로드는 하지 않았습니다. 출력 폴더는 현재 체크아웃에 추가된 독립 산출물이며 Git 기록 대신 스크립트·로그·서명·해시로 재현 근거를 보관합니다.
