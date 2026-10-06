# S1 시작 프레이밍 수정 — v003

0프레임의 카메라 회전각·렌즈를 유지하면서 카메라 위치를 올렸다. 컨테이너가 화면 하단에 놓이고, 위쪽 케이블이 더 길게 보인다. 첨부 빨간 표시 이미지는 `inputs/framing-reference.png`에 보존했다.

- 시작 높이: 중국 항구의 고정된 수직 방향으로 **+0.81894 시험 단위**. 이 세계는 구면이므로 해당 수직은 월드 좌표에서 `(-0.9063, 0, +0.4226)` 방향이다. 실제 월드 위치 변화는 **X -0.74221, Y 0, Z +0.34610**이다. 월드 고도는 증가하고 항구 기준 좌우 위치는 유지한다.
- 0프레임 컨테이너 최하단: 화면 아래로부터 **26.1% → 9.0%**. 객체를 아래로 이동하거나 렌즈 시프트를 사용한 것이 아니라 카메라를 올린 결과다.
- 카메라 회전·렌즈 키는 **0–1392 전 프레임 그대로**다. 시선 기준점도 카메라와 같은 거리만큼 이동했다.
- 위치 보정은 0–95프레임에서 부드럽게 감소한다. **96프레임 S1 끝부터 이후 전 구간의 카메라 위치·회전·렌즈는 v002와 동일**하다.
- 선박·컨테이너·크레인·화물 등의 동작과 배치는 변경하지 않았다. 검토용 CAMERA_PATH와 버전/출력 메타데이터만 함께 갱신했다.

`master-v003.blend`를 열어 Space로 재생한다. `preview/S1-low-to-high.mp4`는 0–180프레임 확인 영상, `preview/master-v003.mp4`는 전체 영상이다. v002 원본은 보존했으며 기준 스냅샷은 `inputs/base-v002.blend`다.

## 검증

기존 구도에서 하단 배치/고도 조건 2개를 실패시킨 뒤 수정했다(`logs/framing-red.log`). 프레이밍 검사 4개, 기존 S1 검사 4개, 전체 회귀 검사 24개가 별도 재개방 프로세스에서 통과했다(`logs/verification.log`). 전 구간의 회전·렌즈 동일성 및 96프레임 이후 카메라 동일성을 검사한다. 0–161 구간 645개 quarter-frame 샘플에서 카메라 바운딩박스 근접 충돌은 0건이다(`review/motion-check.json`). 이는 정밀 연속 충돌 검사나 실제 물류 설비 검증은 아니다.

실제 1배속 0–180 재생 결과는 `review/playback-check.json`, 재개방 픽셀/원본 보존/영상 프레임 수는 `review/final-check.json`, 변경 값은 `review/revision.json`이다. 이후 카메라와 물류 동작이 그대로이므로 이번 시각 재생 검토는 수정 구간을 중심으로 수행했다.

## 재실행

원본은 보존된 기준 파일과 `scripts/raise_camera.py`다. 이 폴더의 v003을 수동 편집했다면 먼저 다른 이름으로 저장해야 재생성 시 보존할 수 있다.

```powershell
$p='F:\pnpline-landing\hero-section-video\blockout\blockout-master-v003'
$b='C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
& $b --background --factory-startup "$p\inputs\base-v002.blend" --python-exit-code 1 --python "$p\scripts\capture_base.py" --python "$p\scripts\raise_camera.py"
& $b --background --factory-startup "$p\master-v003.blend" --python-exit-code 1 --python "$p\scripts\test_framing.py" --python "$p\scripts\test_s1_camera.py" --python "$p\scripts\test_scene.py" --python "$p\scripts\verify_revision.py" --python "$p\scripts\render_s1.py"
& $b --background --factory-startup "$p\master-v003.blend" -s 0 -e 1392 -a
ffmpeg -y -framerate 12 -start_number 0 -i "$p\preview\frames\frame-%04d.png" -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "$p\preview\master-v003.mp4"
```

기존 Blender 5.1.0, ffmpeg, Python/Pillow 및 Playwright/Chrome만 사용했다. 커밋·게시·외부 생성은 수행하지 않았다. 기존 공간 블록아웃 범위와 상세 제작 보류는 유지된다.
