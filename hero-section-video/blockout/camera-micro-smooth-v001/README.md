# f330–f366 카메라 미세 보정

첨부 녹화의 구간을 현재 30fps 프레임과 대조하고, f330–f366 안에서 카메라 위치·회전의 미세한 급변만 보정했다. 선박을 따라가는 기존 경로와 구도를 유지한다.

- 작업본: `pnpline-33s-camera-micro-smooth-v001.blend`
- 전체 영상: `preview/pnpline-33s-camera-micro-smooth-v001.mp4` — 1280×720, 30fps, 990프레임, 33초
- 비교: `review.html` — 원속도와 0.5배속 비교
- 실행: `python scripts/serve.py` → `http://127.0.0.1:18791/review.html`

## 변경 범위

f330과 f366은 기존 카메라와 같고, 실제 변경된 정수 프레임은 f331–f365의 35개다. 시간 지연이 없는 대칭 필터로 위치와 회전만 보정하고, 양끝 6프레임에서는 보정량을 완만하게 줄인다. 렌즈·시프트·줌, 모델·재질, 선박·컨테이너·차량·문 동작, 장면 길이와 프레임 대응표는 유지한다.

카메라 보정 오브젝트 `S4_CAMERA_MICRO_SMOOTH`를 추가한다. 원본 카메라의 로컬 변환을 재분해하지 않아 범위 밖 프레임에 불필요한 수치 변화를 만들지 않는다. 파일 원본은 `../ship-camera-continuity-v001/pnpline-33s-ship-camera-v001.blend`이며 SHA-256은 `config.json`에서 고정한다.

## 검증

Blender 5.1에서 `scripts/inspect_camera.py`, `scripts/build.py`, `scripts/measure.py`, `scripts/verify_preservation.py`를 사용한다. Python의 `tests/test_camera.py`는 급격한 변화의 감소, 구도 차이, 광학 설정과 경계 프레임의 보존을 검사한다. `scripts/render.py`로 35프레임만 다시 렌더링하고 `scripts/encode.py`로 나머지 955프레임을 재사용한다. 전체 디코딩과 프레임 수·재생률·길이를 검증한다.

최종 해시와 검증 결과는 `delivery.json`에 기록한다. 렌더 프레임, 로그, 시행 파일은 `.gitignore`로 커밋 대상에서 제외한다.
