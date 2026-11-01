# PNPLINE 미국 컨테이너 항만 v001

미국 항만을 컨셉 이미지의 적재 밀도에 맞춰 보강한 Blender 작업본입니다.

- `pnpline-port-densification-v001.blend`: 편집 가능한 최종 작업본.
- `preview/pnpline-port-densification-v001.mp4`: 전체 33초, 30fps, 990프레임, 1280×720 검토 영상.
- `review.html`: 같은 카메라의 수정 전후 비교, 전체 영상, 하역·트럭 구간 바로가기.
- 원본: `../city-expansion-v002/pnpline-city-expansion-v002.blend`. 원본 파일은 덮어쓰지 않습니다.

## 변경 내용

컨테이너 **88개**를 추가했습니다. 새 적재 블록 26곳에 74개를 2~3단으로 쌓고, 기존 14개 적재 블록에 상단 컨테이너를 하나씩 추가했습니다. 기존 컨테이너와 함께 연속적인 적재 구역이 보이도록 배치했습니다.

각 컨테이너에는 골판 측면·지붕, 상하 프레임, 모서리 부품, 이중문과 잠금봉을 모델링했습니다. 시안·블루·네이비·화이트·그레이를 사용했습니다.

대형 크레인 **2기**를 추가하고 기존 주 하역 크레인의 상부 트러스, 지지 케이블, 운전실, 사다리, 장비실을 보강했습니다. 카메라가 트럭을 추적하는 시야를 고려해 동쪽 크레인의 뒷기둥을 육지 쪽으로 옮겼습니다. 안벽에는 방충재, 계선주, 조명, 레일과 통행 표시를 추가했습니다.

접안부는 기존 작업 면을 사용하며, 육지 쪽 적재 블록은 실제 곡면 지형과 만나는 기초 위에 놓았습니다. 곡면 구역에서는 지구 표면 법선에 맞춰 블록 전체가 정렬됩니다. 중앙 하역 공간과 y=9 트럭 통로를 확보했습니다.

## 보존 및 검증

기존 도시, 창고, 선박, 차량, 화물과 카메라를 유지하며 `PT_` 접두어의 정적 모델만 추가합니다. 원본의 사용하지 않는 재질도 저장 후 유지되도록 보존합니다. 기존 카메라와 애니메이션의 키프레임, 경로, 렌즈, 33초·30fps 타이밍은 변경하지 않습니다.

- `review/preservation.json`: 원본 오브젝트 11,656개와 재질·액션·지오메트리 비교, 전체 990프레임 카메라 행렬 및 렌즈 정확 일치 검사.
- `review/clearance.json`: 990프레임에서 이동 메시 265개와 새 항만 구조물 사이 삼각형 표면 교차 검사. 기초와 바닥 도색은 의도한 접촉면으로 제외합니다.
- `review/static-clearance.json`: 새 컨테이너끼리, 새 크레인·안벽 시설 및 기존 적재물·철도와의 표면 교차 검사.
- `review/camera-passage.json`: 0.25프레임 간격으로 카메라 위치를 샘플링하고 샘플 사이 선분의 새 구조물 관통 여부 검사.
- `delivery.json`: 최종 파일 해시, 검증 결과와 영상 메타데이터. 영상 생성 후 기록됩니다.

검토 영상은 기존 Blender Workbench 룩을 유지한 미리보기입니다. GPU 타이밍은 측정하지 않았습니다. 삼각형 교차 검사는 출력 프레임에서의 표면 교차를 검사하며 연속 시간 강체 물리 시뮬레이션을 대신하지 않습니다.

## 재현

Blender 5.1에서 `scripts/build.py`를 실행하면 원본을 읽고 작업본과 배치 명세를 생성합니다. `--factory-startup`을 사용해 사용자 애드온 영향을 분리합니다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup -t 6 --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/blockout/port-densification-v001/scripts/build.py'
python 'F:/pnpline-landing/hero-section-video/blockout/port-densification-v001/scripts/serve.py' --port 18794
```

`scripts/render.py`는 최종 작업본을 연 상태에서 `-- --start 0 --end 494` 또는 `-- --start 495 --end 989`로 실행합니다. `scripts/package.py`는 검증 결과와 990장 전체 프레임의 해시 대응을 확인한 뒤 영상을 인코딩합니다. 렌더 프레임, 로그, `.blend1` 백업은 중간 산출물입니다.
