# S1 카메라 수정 — v002

사용자 요청: 0프레임 로우앵글에서 시작해 S1 종료 시 첨부한 하이앵글 구도로 전환.

`master-v002.blend`를 열면 0프레임에서 시작한다. Space로 재생한다. `preview/S1-low-to-high.mp4`는 변경 구간과 S2 연결까지 0–180프레임을 담는다. 전체 영상은 `preview/master-v002.mp4`다.

## 변경

- S1: **0–96프레임**. 컨테이너 중심 기준 약 **-20.12° → +20.05°**로 전환한다. 카메라가 상승하며 조금 후퇴한다. 96프레임에서는 컨테이너 윗면, 주변 적재열, 분리된 스프레더가 보인다.
- S2 연결: 97–159프레임을 보간하고 **160–1392프레임은 기존 카메라/시선 목표와 정확히 동일**하다. 96프레임과 160프레임 전후에 위치 도약이 없는지 검사했다.
- 시작 프레임과 S1 마커를 1→0으로 변경했다. 선박·컨테이너·크레인 등의 기존 이벤트 프레임은 그대로다. 전체 출력은 1393프레임, 12fps, 약116.083초다.
- `CAMERA_PATH` 검토 가이드와 버전/출력 메타데이터를 함께 갱신했다. 렌즈는 기존 값을 유지했다.

## 보존 기준

이전 인계 이후 사용자가 저장한 현재 v001 파일을 기준으로 적용했다. 기본 장면을 재생성하지 않았다. 원본 v001은 덮어쓰지 않았으며 `inputs/base-user-saved-v001.blend`에 기준 스냅샷도 보존했다.

기준 SHA-256: `d7b31e3869b8a50344a59df6866f8783430b17e0ccc8d1368d68105abf5f5076`.

첨부 이미지는 `inputs/s1-end-reference.png`. 이번 S1 종료 구도에 적용한 직접 사용자 기준이다. 나머지 구간의 기존 보드 미대조 상태와 별개다. 촬영 각도·프레이밍을 참고했으며 Blender UI까지 픽셀 복제한 결과는 아니다.

비카메라 오브젝트의 변환·렌더 표시 상태는 17개 프레임에서 수정 전후 서명이 동일하다. 이후 카메라/목표는 160–1392 전 프레임에서 행렬/위치 오차 0이다. `review/preservation.json` 참조.

## 검증

- 기존 파일에서 시작 프레임·상승 동작 검사를 먼저 실패시킨 뒤 수정했다: `logs/s1-red.log`.
- 수정 파일을 별도 Blender 프로세스로 재개방하여 S1 검사 4개와 기존 회귀 검사 24개 실행: `logs/verification.log`.
- 0–161 구간을 0.25프레임 간격으로 검사한 카메라 근접/회전/이동 기록: `review/motion-check.json`. 바운딩박스에 대한 점 검사이며 정밀 연속 메시 충돌 해석은 아니다.
- f0/24/48/72/96과 S2 연결 관찰 스틸: `review/camera-f*.png`. 실제 카메라 좌표와 앵글: `review/camera-states.json`.
- 실제 1배속 변경 구간 재생: `review/playback-check.json`. 전체 영상은 재인코딩했으며 이번 실제 재생 검토 범위는 0–180프레임이다.
- 재개방 스틸 동일성과 ffprobe: `review/final-check.json`. 최종 파일 해시: `hashes.json`.

## 재현

Blender 5.1.0과 기존 ffmpeg/Python/Pillow/Playwright 환경을 사용한다. `revise_s1.py`는 보존된 기준 파일에만 적용하도록 제한되어 있다. 다음 명령은 생성된 v002를 덮어쓰므로 v002에서 새로 수동 편집한 경우 먼저 다른 이름으로 저장한다.

```powershell
$p='F:\pnpline-landing\hero-section-video\blockout\blockout-master-v002'
$b='C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
& $b --background --factory-startup "$p\inputs\base-user-saved-v001.blend" --python-exit-code 1 --python "$p\scripts\revise_s1.py"
& $b --background --factory-startup "$p\master-v002.blend" --python-exit-code 1 --python "$p\scripts\test_s1_camera.py" --python "$p\scripts\test_scene.py" --python "$p\scripts\verify_revision.py" --python "$p\scripts\render_s1.py"
& $b --background --factory-startup "$p\master-v002.blend" -s 0 -e 1392 -a
ffmpeg -y -framerate 12 -start_number 0 -i "$p\preview\frames\frame-%04d.png" -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "$p\preview\master-v002.mp4"
```

카메라 수정의 기준은 저장된 사용자 장면과 `revise_s1.py`다. 기존 v001 생성기를 실행하면 이번 카메라 수정은 반영되지 않는다. 7구간 공간 블록아웃 범위, 기존 #61 승인안과의 구분 및 상세 제작 보류는 유지된다.
