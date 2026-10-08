# S5 잠정 통합본 v001

작업 파일: `master-s5-integration-v001.blend` (기존 PNPLINE_MASTER_v005 Scene / CAM_MASTER).
연속 확인: `preview/main.mp4`, 동일 시간축 진단: `preview/top.mp4`.
두 영상 모두 f624–948, 12fps, 960×540, 325프레임, 27.083초. 정지 구간 포함, 컷·배속 변경 없음.
S5 관찰 후보: `review/candidates.jpg`, 개별 PNG와 `frame-manifest.json`.
세부 검증·제약: `report.md`. 원본 두 blend는 보존됨.

## 재현 (PowerShell, 레포 루트)

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$r = 'F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001'
$base = 'F:/pnpline-landing/hero-section-video/blockout/s4-s5-boundary-v001/master-s4-s5-boundary-v001.blend'
$donor = 'F:/pnpline-landing/hero-section-video/blockout/s5-dock-test-v001/master-with-s5-test-v001.blend'
& $blender --factory-startup -b --python-exit-code 1 --python "$r/scripts/integrate.py" -- --base $base --donor $donor --config "$r/config.json" --output "$r/review/reproduced.blend"
if ($LASTEXITCODE -ne 0) { throw 'Integration failed' }
foreach ($test in @('integration','master_regression','wheel_regression')) {
  & $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/tests/$test.py"
  if ($LASTEXITCODE -ne 0) { throw "Failed: $test" }
}
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/check_preservation.py" -- --base $base --output "$r/review/preservation.json"
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/check_reproduction.py" -- --other "$r/review/reproduced.blend" --output "$r/review/reproduction.json"
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/audit_motion.py"
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/validate_space.py" -- --config "$r/config.json" --output-dir "$r/review"
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/check_visibility.py"
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/render_review.py" -- --output "$r/preview/main-frames" --frames '624:949'
& $blender --factory-startup -b "$r/master-s5-integration-v001.blend" --python-exit-code 1 --python "$r/scripts/render_review.py" -- --output "$r/preview/top-frames" --frames '624:949' --top
ffmpeg -y -framerate 12 -start_number 624 -i "$r/preview/main-frames/%04d.png" -frames:v 325 -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "$r/preview/main.mp4"
ffmpeg -y -framerate 12 -start_number 624 -i "$r/preview/top-frames/%04d.png" -frames:v 325 -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "$r/preview/top.mp4"
& 'C:/ProgramData/miniconda3/python.exe' "$r/scripts/package_evidence.py"
```

`integrate.py`는 입력·출력 동일 경로 및 입력 해시 불일치를 거부한다. 실행은 기존 sibling donor의 검증된 `kinematics.py`, `geometry.py`에 의존한다. 플러그인/패키지 설치는 없다. 재생 페이지가 필요하면 `scripts/serve_review.py` 실행 후 `http://127.0.0.1:8766/review.html`을 연다. localhost만 사용한다.

GUI에서 예전 통합본을 이미 열었다면 별도로 열린 최신 창의 경로와 파일 해시를 확인한다. 다른 창의 미저장 작업을 자동으로 덮어쓰거나 닫지 않았다.
