# 선박 추적 카메라 연속성 개선

미국 입항 전에 카메라가 선박을 앞서 보여주다가 기다리는 구도를, 선박과 함께 전진하는 구도로 수정했다. 선박의 이동 좌표계를 기준으로 카메라 간격을 잡고, 도시가 드러나는 동안 높이와 시선 방향을 연속적으로 바꾼다. 선박 전체가 화면에 유지되며 도시 공개 뒤에는 기존 측면 구도로 연결된다.

- Blender: `pnpline-33s-ship-camera-v001.blend`
- 전체 영상: `preview/pnpline-33s-ship-camera-v001.mp4`
- 전후 비교: `review.html`
- 1280×720 · 30fps · 990프레임 · 33초

`python scripts/serve.py`를 실행하면 `http://127.0.0.1:18790/review.html`에서 검토할 수 있다.

## 범위와 보존

현재 30fps 기준 f210–f350 사이의 카메라만 수정했다. f210–f235에 진입하고 f330–f350에 기존 측면 경로로 돌아간다. 주 추적 구간 f235–f330에서는 선박 표면의 수직 방향을 기준으로 롤을 거의 0°로 유지한다. 구면에 놓인 도시 건물의 기울기와 원근은 유지된다.

이전 트럭 카메라 수정본 `../truck-camera-smooth-v001/pnpline-33s-truck-camera-v001.blend`에서 이어 작업했다. 카메라 부모 `S3_SHIP_FOLLOW_CAMERA` 하나를 추가하며, 기존 카메라 키·렌즈·시프트, 선박·차량·화물·문 동작, 모델과 재질, 타임라인은 유지된다. 수정 범위 밖 851프레임의 카메라 행렬과 투영값을 원본과 비교한다. 기존 프레임 대응표는 `frame-map.csv`로 함께 제공한다.

## 재현과 검증

1. Blender 5.1에서 `scripts/inspect_camera.py`로 원본 구간을 측정한다.
2. `scripts/build.py`가 선박 기준의 경로를 만들고 1/8프레임 선형 보정 키를 저장한다.
3. `scripts/measure.py`로 두 파일을 다시 열어 반 프레임 간격으로 속도·가속도·회전·롤·선박 화면 경계를 비교한다.
4. `python -m unittest discover -s tests -v`와 Blender의 `scripts/verify_preservation.py`를 실행한다.
5. `scripts/render.py`로 f211–f349를 렌더링한다. `scripts/encode.py`는 보존이 확인된 이전 프레임과 합쳐 전체 영상 및 비교 영상을 만들고 전체 디코딩을 검사한다.

검증 요약과 파일 SHA-256은 `delivery.json`에 기록한다. 렌더 프레임, 로그, 시행 결과, Blender 백업은 `.gitignore`로 제외한다.
