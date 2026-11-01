# PNPLINE 미국 도시 확장 v001

사용자가 표시한 세 영역에 랜드마크 중심의 도시 지구를 추가하고, 기존 현수교를 오른쪽 섬까지 이어지는 다리로 교체했습니다. 같은 main 작업공간에서 제작했습니다.

## 결과물

- `pnpline-city-expansion-v001.blend`: 편집 가능한 최종 장면
- `review.html`: 전체 영상, 위쪽·사선 배치, 랜드마크 상세 및 다리 보기
- `preview/pnpline-city-expansion-v001.mp4`: 33초 / 30fps / 990프레임 / 1280×720 미리보기
- `scripts/build.py`, `architecture.py`, `dense_layout.json`: 재현 가능한 제작 코드와 배치
- `review/build.json`, `geometry.json`, `preservation.json`: 제작 및 검증 기록

## 디자인

왼쪽에는 크라이슬러 빌딩을 참고한 26단위 높이의 아르데코 타워를 배치했습니다. 은색 겹아치 크라운, 삼각형 창, 첨탑, 단계적으로 좁아지는 몸체를 강조했습니다. 주변 건물 60개의 본체 높이는 3.22~6.99단위입니다.

오른쪽 섬에는 트랜스아메리카 피라미드를 참고한 24단위 높이의 타워와 주변 건물 44개를 배치했습니다. 주변 건물의 본체 높이는 3.34~5.49단위이며, 중앙 공원과 낮은 건물들이 피라미드 실루엣을 강조합니다. 두 랜드마크는 실측 복제보다 미니어처에서의 식별성을 우선했습니다. 주변 건물의 옥상 장비와 지붕은 본체 높이보다 조금 높습니다.

새로운 도시군에는 도로·보도·해안 산책로·가로수와 침엽수 70그루·벤치·가로등·정차 차량을 포함했습니다. 다리의 폭은 3.8단위이며, US 구면 매핑 좌표 `(30, 8.8)`에서 `(30, -22)`까지 기존 도로와 섬 도로를 연결합니다.

지형의 상단은 기존 지구와 같은 중심 및 반지름을 사용하는 `R=140.68` 구면입니다. 건물은 각 기단 위치의 표면 법선에 맞춰 세운 강체이며, 구면 하부와 평평한 상부를 가진 기단으로 지면에 접합니다. 교량 상판은 구면과 완만한 종단 곡선을 따라가고, 두 주탑은 각각 해당 지점의 법선에 맞춰 서 있습니다.

도로가 넓어 보인다는 후속 요청을 반영해 도로를 8개에서 4개로 줄이고, 주변 건물을 40개에서 104개로 늘렸습니다. 다리·산책로를 제외한 도로와 보도의 대략적인 평면 면적은 2,004에서 707로 약 65% 감소했습니다. 새 건물의 기단끼리, 기단과 보도 사이에는 최소 0.5단위의 간격을 확보했습니다.

새 메시 중 열린 창문·도로 면은 WORKBENCH 그림자 계산에서 제외해 긴 줄무늬 오류를 방지합니다. 닫힌 건물 몸체는 계속 그림자를 드리우며, 기존 객체와 전역 렌더 설정은 그대로 유지했습니다.

오른쪽 섬 바깥으로 추가 지정된 영역에는 윌리스 타워를 참고한 28단위 높이의 랜드마크와 저층 건물 44개를 더했습니다. 사각 튜브 9개를 묶은 단계형 몸체와 안테나 두 개로 기존 피라미드와 형태를 구별했습니다. 최종 건물 수는 랜드마크 3개와 주변 건물 148개를 합한 151개입니다. 확장 구역의 도로 2개를 더해 최종 도로는 6개입니다. 기존 106개 건물 중 105개는 배치를 그대로 유지했고, 연결로를 막던 소형 건물 한 채만 새 구역으로 옮겼습니다. 기존 다리와 섬의 지형은 그대로 유지했습니다.

## 검증

- 새 건물 151개의 표면 법선 정렬, 세 지형과 광장의 구면 반지름 검사
- 건물 기단끼리, 건물과 보도, 물류 보호 구역의 겹침 및 육지 경계 이탈 검사
- 교량 양 끝과 실제 도로 메시 사이의 접속 간격 검사
- 기존 다리 객체 60개만 교체하고, 보호 대상 원본 객체 10,032개의 데이터 보존 검사
- 전체 f0~989의 카메라 행렬·변환·렌즈·데이터 및 원본 액션의 정확 일치 검사
- 같은 WORKBENCH 표현에서 전체 배치, 두 랜드마크, 교량, 기존 카메라 구간을 확인

검증 결과의 자세한 수치와 출력 파일 해시는 `delivery.json`에 기록합니다. 원본 카메라와 애니메이션을 유지했으므로 기존 USA 글자가 일부 시점에서 뒤쪽 크라이슬러 몸체를 가립니다. 상세 뷰와 위쪽 뷰에서 전체 형태를 확인할 수 있습니다.

## 재현

Blender 5.1에서 `scripts/build.py`를 실행하면 최신 카메라 보정본 `../camera-micro-smooth-v001/pnpline-33s-camera-micro-smooth-v001.blend`를 읽습니다. 입력 SHA256은 코드에 고정돼 있습니다. 원본은 덮어쓰지 않습니다.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup -t 6 --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/blockout/city-expansion-v001/scripts/build.py'
```

렌더링 또는 검증이 실행 중일 때는 작업본을 다시 생성하지 마세요. `render.py -- --start 0 --end 989`로 PNG를 생성하고 `scripts/package.py`로 30fps 영상과 전달 기록을 만들 수 있습니다. `scripts/serve.py --port 18792`는 동영상 탐색을 지원하는 로컬 검토 서버입니다.

## 적용한 스킬과 참고 자료

`threejs-procedural-architecture`, `threejs-procedural-planets`, `threejs-visual-validation`의 모듈식 형상, 재질별 메시 배치, 단일 구면 좌표계, 고정 시점 검증 원칙을 Blender 제작 과정에 적용했습니다. Three.js 런타임이나 새 후처리 효과를 추가한 작업은 아닙니다.

- [뉴욕시 LPC 크라이슬러 빌딩 지정 보고서](https://www.artdeco.org/_files/ugd/cfca41_b6cf603aa7cb4039a879d362b221c677.pdf)
- [SEAONC 트랜스아메리카 피라미드 기록](https://legacy.seaonc.org/structure/transamerica-pyramid/)
- [설계사 SOM의 Willis Tower 구조 설명](https://www.som.com/projects/willis-tower-formerly-sears-tower/)
- [Transamerica Pyramid와 Redwood Park](https://transamericapyramid.com/transamerica-pyramid)

Git에 포함할 원본은 `.blend`, 제작·검증 스크립트, `dense_layout.json`, 이 문서, 검토 HTML 및 전달 기록입니다. PNG 렌더 프레임, 로그, `.blend1`, 중간 조사 및 시험 산출물은 제외합니다.
