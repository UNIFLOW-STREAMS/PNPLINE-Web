# S5 도크 테스트 후보

`master-with-s5-test-v001.blend`를 열면 테스트 Scene이 선택된다. 원본 `PNPLINE_MASTER_v005`도 같은 파일에 보존되어 있다. 테스트는648–900,12fps다. 사선은 `S5T__CAM_OBLIQUE`, 진단 탑뷰는 `S5T__CAM_TOP`이다.

- 영상: preview/s5-oblique.mp4, preview/s5-top.mp4
- 핵심 스틸: review/contact-sheet.png 및 review/oblique·top
- 검증: report.md, review/check-runs.json
- 원본과 차이/통합 범위: integration-proposal.md

재현은 설치된 Blender5.1.0과 Python3.13.9, ffmpeg7.1에서 수행했다. Pillow는 보고 이미지 비교에만 사용한다. 새 라이브러리/플러그인 설치는 없다. 아래 PowerShell 변수는 실행 환경에 맞춰 지정한다. `$r`은 이 폴더, `$source`는 최신 S4 원본, `$blender`는 설치된 Blender 실행 파일이다. 소스와 출력 파일이 같으면 빌더가 거부한다.

```powershell
& $blender --background --factory-startup $source --python-exit-code 1 --python "$r/scripts/build_s5_test.py" -- --config "$r/config.json" --output "$r/master-with-s5-test-v001.blend"
python -X utf8 "$r/scripts/run_checks.py" --blender $blender --source $source --candidate "$r/master-with-s5-test-v001.blend"
& $blender --background --factory-startup "$r/master-with-s5-test-v001.blend" --python-exit-code 1 --python "$r/scripts/render_s5_review.py" -- --scene S5_DOCK_TEST_v01 --output-dir "$r/preview" --camera oblique --animation
& $blender --background --factory-startup "$r/master-with-s5-test-v001.blend" --python-exit-code 1 --python "$r/scripts/render_s5_review.py" -- --scene S5_DOCK_TEST_v01 --output-dir "$r/preview" --camera top --animation
ffmpeg -framerate 12 -start_number 648 -i "$r/preview/oblique/%04d.png" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart "$r/preview/s5-oblique.mp4"
```

재생성은 명시한 원본 파일 기준으로 권장한다. 현재 검토본에서 함수 `build(config)`를 실행해도 테스트 소유 데이터만 교체하며, 외부 참조/이름 충돌은 거부한다. `check_reproduction.py`가 실제 변이 및 재실행을 수행하되 파일에는 저장하지 않는다.

소스 생성기의 전체 삭제 코드나 orphan purge를 실행하지 않는다. 마스터 통합과 커밋은 이 산출물에 포함되지 않는다. `progress.md`에는 선택한 기준·설계 이탈·검토 판단과 비용이 남아 있다.
