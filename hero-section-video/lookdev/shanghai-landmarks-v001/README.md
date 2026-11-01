# Shanghai landmarks v001

## 변경

- 상하이 세계금융센터형 빌딩: 과대 직사각형 고리를 제거하고 테이퍼형 유리 몸체, 작은 사다리꼴 개구부, 개구부 안쪽 금속 마감으로 재제작. 원래 중심 위치와 높이는 유지.
- 진마오형 빌딩: 외벽 밖으로 돌출된 격자를 제거. 모서리를 깎은 8면 매스, 위로 좁아지는 12단 셋백, 층별 폭에 맞는 유리 패널과 얇은 창호, 다층 크라운 및 첨탑으로 교체.
- 동방명주: 기존 바닥 기준점을 유지하며 전체를 1.35배 확대.

## 검증

- 실제 저장된 결과 파일을 다시 읽고 Cycles OPTIX로 전체 스카이라인, 랜드마크 확대, 기존 CAM_MASTER 57프레임을 렌더링했다.
- 같은 카메라와 설정으로 원본도 렌더링했다. review/before-*.png 및 after-*.png.
- 대상 외 26,680개 오브젝트의 로컬 변환, 부모, 데이터 연결, 렌더 가시성 동일 확인. 기존 애니메이션 액션의 키·핸들·보간 정보 해시 동일 확인.
- 원래 지구 곡면 방향과 카메라/물류 애니메이션은 유지. 0–989, 30fps 유지.
- 신규 재질은 Blender 노드 기반이며 신규 외부 텍스처 의존성 없음.

## 파일

- pnpline-shanghai-landmarks-v001.blend: 결과 보관본
- ../hero-material-v001/pnpline-hero-material-v001.blend: 동일 결과를 반영한 통합 마스터
- previous-latest-lookdev.json: 변경 전 포인터
- delivery.json: 검증 및 리뷰 경로
- scripts/build.py: 변경 전 마스터에 적용하는 재현 스크립트
- scripts/review.py: 파일을 저장하지 않는 비교 렌더 스크립트

원본은 ../ocean-foam-v002/pnpline-ocean-foam-v002.blend에 보존되어 있다.
