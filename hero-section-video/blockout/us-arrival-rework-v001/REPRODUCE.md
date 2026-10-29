# v010 재현과 검증

Windows PowerShell, Blender 5.1.0(adfe2921d5f3), 기존 Python/Pillow 및 FFmpeg를 사용했습니다. 설치한 라이브러리는 없습니다. 원본 입력은 `inputs/current-v004.blend`이며, 폰트는 이미 메시로 변환되어 있습니다. 상위 `us-city-concept-v001/scripts/`의 기존 geometry/signature/safety 도우미도 필요합니다. 외부 자산 다운로드가 없습니다.

```powershell
Set-Location 'F:\pnpline-landing'
$arrivalRoot = 'F:/pnpline-landing/hero-section-video/blockout/us-arrival-rework-v001'
$blenderBin = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'

# 출력 경로는 절대 경로여야 하며 기존 파일 덮어쓰기를 거부합니다.
& $blenderBin --background --factory-startup "$arrivalRoot/inputs/current-v004.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/build_arrival.py" -- --output "$arrivalRoot/review/my-reproduction.blend"

& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/compare_reproduction.py" -- "$arrivalRoot/review/my-reproduction.blend"

& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/verify_rework.py"
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/verify_collisions.py"
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/verify_visibility.py"
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/verify_camera_path.py"

& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/tests/test_arrival.py" --python "$arrivalRoot/tests/test_support.py" --python "$arrivalRoot/tests/test_camera_motion.py" --python "$arrivalRoot/tests/test_civic_readability.py" --python "$arrivalRoot/tests/test_skyline_readability.py"
& $blenderBin --background --factory-startup "$arrivalRoot/inputs/current-v004.blend" --python-exit-code 1 --python "$arrivalRoot/tests/test_preservation_scope.py"
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/tests/test_material_signature.py"

# 기존 회귀 검사: 기준과 후보 모두 P01 cable 0 unsupported 한 건으로 exit 1.
& $blenderBin --background --factory-startup "$arrivalRoot/inputs/current-v004.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/run_inherited_regression.py"
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/run_inherited_regression.py"

# 새 이름의 폴더만 허용합니다. 기존 candidate-v010 폴더는 덮어쓰지 않습니다.
& $blenderBin --background --factory-startup "$arrivalRoot/candidate-arrival-v010.blend" --python-exit-code 1 --python "$arrivalRoot/scripts/render_sequence.py" -- --label my-preview --start 288 --end 720
ffmpeg -n -framerate 12 -start_number 288 -i "$arrivalRoot/preview/my-preview/f%04d.png" -frames:v 433 -an -c:v libx264 -preset fast -crf 20 -pix_fmt yuv420p -movflags +faststart "$arrivalRoot/preview/my-preview.mp4"

# 기존 18784 서버가 없다면 사용하지 않는 로컬 포트로 실행합니다.
& 'C:/ProgramData/miniconda3/python.exe' -m http.server 18785 --bind 127.0.0.1 --directory $arrivalRoot
# 브라우저: http://127.0.0.1:18785/review-v010.html
```

실제 실행 로그는 `review/`에 있습니다. 성공 확인은 각 프로세스 종료 코드와 로그를 함께 봅니다. 저장 시 사용자 썸네일 캐시 권한 경고가 있었으나 `.blend` 저장·별도 재개방·비교·렌더는 성공했습니다. 중간에 Windows 샌드박스 프로세스 생성 오류 `0x80070020`이 발생해 재현 비교/렌더/기준 모션 검사만 승인된 별도 실행 권한으로 수행했습니다. 이어 기본 실행 환경도 회복되어 영상 인코딩·증거 집계가 성공했습니다.
