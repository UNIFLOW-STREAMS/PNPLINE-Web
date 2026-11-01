# PNPLINE 중국·미국 통합 작업본

`pnpline-cn-us-integrated-v001.blend`는 미국 도시·항만 개선본과 중국 항만·카메라 수정본을 통합한 작업 파일입니다. 두 원본은 덮어쓰지 않습니다. 검증 상태와 최종 파일 해시는 `delivery.json`에 기록합니다.

## 통합 기준

- 기반 파일: `../port-densification-v001/pnpline-port-densification-v001.blend`
- 중국 수정분: `../cn-port-camera-v001/master-cn-port-camera-v001.blend`
- 시간축: 미국 개선본의 33초, 30fps, f0–989를 유지합니다.
- 중국 수정본의 12fps 프레임은 기존 `pacing-33s-v001`의 단조 시간 매핑으로 변환합니다. 단순 프레임 배율을 적용하지 않습니다.

중국 항만의 컨테이너 127개, 크레인 3기, 안벽·수면·주변 시설 배치와 기존 크레인의 선적 동작을 반영합니다. 미국 도시·항만·하역·트럭·창고·배송 모델과 원래 애니메이션 액션은 유지합니다.

중국 카메라는 f0–165에서 해당 시점의 원본 구도를 유지합니다. f165–253에서 기존 미국 항해 카메라로 부드럽게 연결하고, f253 이후에는 미국 개선본의 카메라를 그대로 사용합니다. 렌즈와 렌즈 보정 드라이버는 미국 개선본을 유지합니다.

화물과 팔레트는 미국 구간의 곡면 운송 보정을 유지하는 별도 연결 객체를 거칩니다. 중국 접안·수면 보정은 항해 중 사라지며 미국 입항 전에 기존 동작으로 복귀합니다. 트랙터와 트레일러의 기존 연결은 유지합니다.

## 검토 자료

- `review/geometry-manifest.json`: 공통 원본을 기준으로 비교한 중국·미국 변경 목록.
- `review/build.json`: 통합 대상, 프레임 연결 구간과 생성 기록.
- `review/geometry-verification.json`: 미국 모델·액션·재질 보존과 중국 항만·수면·충돌 검사.
- `review/animation-verification.json`: 시간축, 선적·운송 동작, 카메라 연결과 후반 보존 검사.
- `review/after-contact-sheet.png`: 통합본 전체 경로의 주요 장면 30개.
- `review/us-reference-live-contact-sheet.png`: 미국 원본을 직접 다시 렌더한 비교 장면.
- `review/us-live-pixel-comparison.json`: 미국 주요 장면의 카메라와 렌더 픽셀 비교.

`review/review.html`에서 전체 주요 장면과 연결 구간 검토 영상을 볼 수 있습니다. 검토 영상은 변경된 도입·항해 연결 구간 9초를 15fps로 표시합니다. Blender 작업본은 전체 33초·30fps를 유지합니다.

상위 폴더의 `latest-previz.json`도 통합본을 가리키도록 갱신합니다. 이전 포인터는 `review/previous-latest-previz.json`에 보관합니다.

검토 이미지·영상은 실제 장면 카메라의 Workbench 렌더입니다. 검토용 그림자 설정은 중국 곡면에서 나타나는 미리보기 줄무늬를 피하도록 조정할 수 있으며, 작업 파일의 재질·조명 설정과 구분됩니다.

## 재현

Blender 5.1에서 `scripts/audit_geometry.py`로 원본 비교 자료를 생성한 뒤 `scripts/build.py`를 실행합니다. 모든 모델·카메라 보정은 편집 가능한 Blender 객체와 키프레임으로 저장되며 재생에 외부 스크립트나 프레임 핸들러가 필요하지 않습니다.
