# PNPLINE 미니어처 홈 V2

히어로는 V1 그대로 유지하고, 나머지 9개 섹션에 ShipMonk에서 관찰한 UI 패턴과 타이포그래피 비례를 적용한 컨셉 시안입니다.

## 보기
- 로컬 미리보기: http://127.0.0.1:8761/output/pnpline-miniature-home-v2/
- index.html: 섹션 이동, 화면 맞춤, 1920px 원본, 1440px 가이드, FAQ 펼치기 제공
- overview.jpg: 전체 섹션 축소 개요
- 01–10 PNG: 섹션별 최종 1920px 이미지

## 디자인
- 모든 섹션 폭 1920px, 콘텐츠 폭 1440px, 좌우 여백 240px.
- 히어로 DOM과 기존 concept.css/concept.js, hero-harbor.jpg는 V1과 동일합니다. 최종 01-hero-1920.png 역시 원본 파일을 그대로 사용했습니다.
- redesign.css / redesign.js는 히어로 이외의 섹션에만 적용됩니다.
- 흰색 카드, 넓은 곡률, 연한 시안 배경, 간결한 아이콘과 이미지 중심 구성.
- 비히어로 제목: Montserrat / Noto Sans SC. 본문: Open Sans / Noto Sans SC. 로컬 글꼴이 없으면 Microsoft YaHei / sans-serif 사용.
- 기존 브랜드 색상 유지: cyan #00ABE1, teal #007FA8, navy #122C3D. 공식 PNP-LINE.webp 사용.
- 참조: https://www.shipmonk.com/ 의 UI, 여백, 카드와 버튼, 타이포그래피. 해당 사이트의 기업 수치나 인증 문구는 사용하지 않았습니다.

## 섹션 높이
| 섹션 | 크기 |
|---|---|
| 히어로 (유지) | 1920 × 1080 |
| 물류 흐름 | 1920 × 920 |
| 고객 유형 | 1920 × 920 |
| 서비스 | 1920 × 1100 |
| 창고 운영 | 1920 × 980 |
| 통관 | 1920 × 780 |
| 비용 | 1920 × 960 |
| FAQ | 1920 × 1080 |
| 문의 | 1920 × 1060 |
| 푸터 | 1920 × 660 |

## 이미지 제작
imagegen-frontend-web 스킬에 따라 image_gen.imagegen으로 비히어로 9개 섹션을 개별 생성했습니다. 전체 페이지를 한 장으로 생성하지 않았습니다. 공통 아트 디렉션과 개별 프롬프트는 prompts.json에 있습니다. studies/는 생성 원본이며, 최종 PNG는 원본의 미니어처 시각 자료에 HTML 문구와 공식 로고를 합성하여 렌더링했습니다.

내용은 docs/pnpline-china-source-content/pnpline-home-a-content-brief-v3.md를 기반으로 간결하게 정리했습니다. 미국 자영 창고 설명을 유지했으며, 비용 시나리오는 계산 예시입니다. 문의 폼은 디자인 데모이며 외부 전송을 하지 않습니다.

## 검증
Chrome에서 10개 섹션의 폭, 콘텐츠 폭, 여백, 텍스트 넘침, 이미지 로딩과 0 크기 이미지 영역을 확인했습니다. 히어로 DOM 동일성, 가이드, 화면 배율 버튼, FAQ 전환을 검증했습니다. validation.json 참고.

export.cjs는 이 작업 환경의 Playwright/Chrome/Sharp 경로와 실행 중인 로컬 서버를 사용합니다. 히어로 원본을 가져오기 위해 인접 V1 폴더가 필요합니다. 완성 PNG와 HTML은 이 스크립트 실행 없이 열 수 있습니다.
