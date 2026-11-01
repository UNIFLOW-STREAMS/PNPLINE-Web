# 확장 항만 카메라 동선

`master-cn-port-camera-v001.blend`는 확장 항만을 기준으로 카메라와 출항 연결을 조정한 작업본입니다. 원본은 `../cn-port-layout-v001/master-cn-port-layout-v001.blend`이며, 원본 파일을 덮어쓰지 않습니다.

기존 하역 클로즈업 → 도시 전경 공개 → 출항 선박 추적의 순서, 40mm 렌즈와 시간축을 유지합니다. 하역 카메라를 새 접안 위치로 평행 이동하고, 전경 구간은 넓어진 부두에 맞춰 중심과 거리를 조정합니다. 항만에서는 도시의 수직 방향을, 항해에서는 지구 곡면에 맞는 선박의 원래 수직 방향을 사용합니다.

카메라 위치와 목표점에는 시간 지연이 없는 대칭 필터를, 회전에는 부호가 연속된 쿼터니언 보간을 적용합니다. 하역 클로즈업이 끝나는 f72부터 f84까지는 양쪽 속도와 가속도를 연결하는 5차 곡선을 사용합니다. 실제 원본 액션을 보존하고 별도의 부모 오브젝트에 보정을 저장합니다. f360 이후 카메라와 물류 동작은 원본에 다시 정확히 연결됩니다. 원본 12fps 시간축은 바꾸지 않습니다.

이전 임시 출항 연결에서 남았던 선수의 수면 이탈은 선박·컨테이너·팔레트를 함께 움직이는 수면 보정으로 해결합니다. f216까지와 f360 이후에는 이 보정이 없으며, 하역 구간은 유지됩니다. 항만의 배치·정점 좌표와 수면 지오메트리는 유지하며, 생성된 항만 모델에서 안쪽을 향하던 닫힌 면의 방향만 바로잡았습니다.

## 검토 자료

- `review/reference-contact-sheet.png`: 항만 확장 전 카메라의 구도와 연출입니다.
- `review/after-contact-sheet.png`: 새 항만 카메라의 주요 장면입니다.
- `review/cn-port-camera-review.mp4`: 실제 카메라의 f0–400을 12fps로 렌더한 33.42초 영상입니다.
- `review/review.html`: 검토 영상과 동일 시점의 수정 전후 이미지를 확인하는 페이지입니다.
- `review/camera-verification.json`: 원본 보존, 카메라 수평과 이동·회전 연속성, 시야와 통과 구간을 검사한 결과입니다.
- `delivery.json`: 원본·최종 파일 해시와 작업 범위를 기록합니다.

검토 이미지는 임시 카메라가 아닌 작업본의 실제 활성 카메라로 렌더합니다. Workbench의 월드 그림자 방향이 중국 지형의 수평선 아래에 있어 길게 늘어지는 사선 무늬를 만들기 때문에, 검토 렌더에서만 투영 그림자를 끕니다. Studio 음영·캐비티·재질은 유지하며, 원본 Cycles 씬 조명은 바꾸지 않습니다.

## 재현

Blender 5.1에서 `scripts/build.py`를 실행하면 고정된 원본을 읽어 카메라 작업본을 저장합니다. `ship_support.py`와 `fix_port_normals.py`를 같은 디렉터리에 두어야 합니다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/blockout/cn-port-camera-v001/scripts/build.py'
```
