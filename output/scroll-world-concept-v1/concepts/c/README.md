# PNPLINE 중국 홈 컨셉 · 콘텐츠 폭 수정본 V3

## 현재 규격

- GNB와 히어로가 포함된 첫 프레임: 1920px 전체 폭, 추가 좌우 여백 없음.
- 나머지 9개 섹션: 이미지 내부의 빈 영역을 표시 범위에서 제외하고 실제 콘텐츠 경계를 1440px 폭에 맞춥니다. 콘텐츠 컨테이너의 padding은 0px이며, 1920px 캔버스에서 좌우 240px 여백만 둡니다.
- 브랜드 컬러: #00ABE1. 기존 라임색 그래픽·카드·강조선·버튼은 내장 image_gen 이미지 편집 도구로 변경했습니다.
- 검토 화면 CSS의 브랜드 색상은 정확히 #00ABE1입니다. 래스터 그래픽은 생성 편집 결과이므로 음영과 질감에 따른 색상 편차가 있습니다.

index.html을 열면 최신 시안을 볼 수 있습니다. 화면에 맞춤 버튼으로 전체 폭을 축소해 볼 수 있고, 가이드선은 첫 프레임에서는 바깥 경계, 나머지 프레임에서는 240px/1680px 경계를 표시합니다.

## 파일

1. 히어로: 01-hero-blue.png / 01-hero-1920.png
2. 전체 물류 흐름: 02-logistics-flow-blue.png / 02-logistics-flow-1920.png
3. 고객 유형별 선택: 03-customer-types-blue.png / 03-customer-types-1920.png
4. 핵심 서비스: 04-services-blue.png / 04-services-1920.png
5. 직영창고·책임·시스템: 05-operations-system-blue.png / 05-operations-system-1920.png
6. 통관 안내: 06-customs-blue.png / 06-customs-1920.png
7. 비용 구성: 07-costs-blue.png / 07-costs-1920.png
8. FAQ: 08-faq-blue.png / 08-faq-1920.png
9. 견적 문의: 09-inquiry-blue.png / 09-inquiry-1920.png
10. 푸터: 10-footer-blue.png / 10-footer-1920.png

-blue.png는 수정 이미지 원본이며, -1920.png는 HTML을 브라우저에서 렌더링한 1920px 폭의 검토용 출력(히어로 높이 1080px, 나머지는 콘텐츠에 맞춘 가변 높이)입니다. 원본 내 생성 여백과 텍스트는 래스터 시안이며, 실제 웹 구현 시 컴포넌트로 재배치해야 합니다. 접미사가 없는 PNG는 이전 라임 시안으로 보존되어 있으며 현재 HTML은 사용하지 않습니다.

## 원고와 제작

중국어 원고는 docs/pnpline-china-source-content/pnpline-home-a-content-brief-v3.md를 참고했습니다. 실제 시설·WMS·가격·실적을 입증하는 자료가 아닌 컨셉 시안입니다. 이미지 내 폼과 링크는 정적 그림입니다.

brand-revision-prompts.json은 이번 내장 image_gen 편집 프롬프트와 산출물 목록입니다. 최초 생성 프롬프트는 prompts.json에 이력으로 보존합니다.

## V3 여백 수정

HTML/CSS에서 이미지의 실제 콘텐츠 경계를 기준으로 확대·위치를 조정했습니다. 래스터 원본을 다시 생성하거나 편집하지 않았습니다. content-bounds-v3.json에 각 섹션의 경계와 배율이 기록되어 있습니다. 카드와 폼 요소 자체의 가독성을 위한 내부 간격은 유지하고, 섹션 전체를 축소하던 바깥 빈 영역만 제거했습니다. 각 섹션 위아래에는 120px의 구간 여백을 두었습니다.

브라우저에서 히어로 1920px, 나머지 콘텐츠 1440px, 좌측 위치 240px, 콘텐츠 padding 0px 및 이미지 로딩을 확인했습니다.

## V4 서비스 섹션 배경

서비스 섹션의 배경을 #191B1A 차콜로 통일했습니다. 내장 image_gen으로 배경 얼룩과 밝기 차이를 제거한 04-services-flat-v4.png를 사용하며, 바깥 CSS 배경도 #191B1A입니다. 기존 1440px 콘텐츠 배치와 다른 섹션은 유지했습니다. 편집 프롬프트는 services-background-v4-prompt.txt에 있습니다.


## V5 입력폼·푸터 통합
- 입력폼과 푸터를 하나의 하단 영역으로 묶었습니다.
- 입력폼의 흰 외부 배경과 둥근 패널 경계를 제거하고, 두 영역의 이미지 배경과 1920px 전체 배경을 차콜 #191B1A로 통일했습니다.
- 콘텐츠 폭 1440px과 좌우 240px을 유지합니다. 두 콘텐츠 사이 여백은 144px입니다.
- 최신 이미지: 09-inquiry-flat-v5.png / 10-footer-flat-v5.png
- 통합 보기: index.html?section=contact-footer
