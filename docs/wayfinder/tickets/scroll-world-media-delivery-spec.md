# 홈 scroll-world 미디어 전달 명세

## Type

`wayfinder:grilling` → `wayfinder:task`

## Status

Blocked

## Question

6개 scroll-world 장면을 어떤 파일 구조와 재생 계약으로 전달해 데스크톱·모바일에서 의도한 경험과 성능 예산을 함께 지킬 것인가?

## Decision areas

- 단일 영상 체인과 장면별 분할 영상 중 전달 구조
- 데스크톱·모바일의 정확한 비율, 해상도, fps, 코덱, 비트레이트와 최대 파일 크기
- 장면별 영상 길이, 스크롤 거리와 재생 시간의 매핑, 장면 경계의 연결 방식
- poster 이미지와 정적 fallback의 파일 매핑
- 영상·poster의 파일명, 디렉터리, manifest 구조와 버전 규칙
- 현재·다음 장면 preload, 오류·저대역폭·재생 불가 상황의 fallback
- 알파 채널 또는 별도 레이어 합성이 필요한지 여부

## Recommended starting point

장면별 분할 영상과 장면별 정적 poster를 기본으로 한다. 알파 채널은 별도 웹 합성이 확정되지 않는 한 사용하지 않는다. 현재 장면과 다음 장면만 preload하고, 재생 또는 다운로드에 실패하면 해당 poster와 일반 콘텐츠를 표시한다.

scroll-world는 스크롤 위치에 맞춰 영상 시간을 제어하므로, 반복 재생 여부보다 장면별 스크롤 거리와 재생 시간의 매핑을 우선 확정한다.

## Deliverables

1. 브레이크포인트별 미디어 매트릭스
2. 장면별 영상·poster·fallback manifest
3. 파일명·경로·버전 규칙
4. 스크롤-시간 매핑표와 preload·오류 처리 규칙
5. Lighthouse·실기기 기준의 성능 예산과 검수 결과

## Completion criteria

- 각 장면의 데스크톱·모바일 파일과 poster가 일대일로 매핑됐다.
- 구현자가 별도 해석 없이 asset manifest와 스크롤-시간 매핑을 적용할 수 있다.
- 성능 예산, 네트워크 실패 대응, 모션 감소 fallback이 검수 기준으로 확정됐다.

## Blocked by

홈 scroll-world 영상 컨셉·키 비주얼·스타일 가이드
