# PNPLINE 디자인 컨셉 v2

2026-09-14 · 기존 v1 스타일을 유지한 중국 → 미국 랜딩 컨셉

## 먼저 볼 파일

- [전체 페이지 PNG — 1440 × 10568](00-fullpage.png)
- [전체 페이지 브라우저 시안](index.html)
- [섹션별 검토 화면](review.html)
- [폼 상태 보드](states.html)
- [폼 상태 PNG](review/form-states-1440.png)

본문은 13개 가로형 이미지로 각각 생성한 뒤, 한 번의 헤더와 푸터를 갖는 연속 페이지로 연결했습니다. S3는 고객 유형 3개의 진입 구조로 조정했고, S5는 직영창고·책임 근거와 WMS 시스템으로 분리했으며, WMS와 비용 사이에 정책·통관 섹션을 배치했습니다.

## 유지한 스타일

v1의 사진 중심 구성, 깊이 있는 창고 구도, 네이비 타이포그래피, 큰 여백, 둥근 사진 프레임, 겹쳐진 WMS 패널, 짙은 배경의 견적 섹션을 유지했습니다.

주요 시각 요소는 큰 사진 프레임 / 사진 안의 업무 설명 / 가느다란 경로선과 번호 / 겹친 기능 패널입니다. 파란 포장 테이프를 사진 간 공통 요소로 사용했습니다. 추가 요청에 따라 히어로의 배너·테이프·박스·작업복·트럭에 공식 로고를 참조한 브랜드 표현을 복원했습니다. 배경 문구는 중국 → 미국으로 통일했으며 중앙 카피는 유지했습니다. 경로 진행과 FAQ 펼침을 연상시키는 구성이며 실제 애니메이션 구현은 아닙니다.

## 1–7 보완 내용

| 기존 부족한 점 | v2 반영 |
| --- | --- |
| 한국 출발 흐름 | 히어로와 5단계 물류 흐름을 중국 출발 → 미국 이행으로 변경. 미국 통관을 독립 단계로 표시하고 한국·인천 및 한국 출발 문구 제거 |
| 녹색·세이지 팔레트 | PNPLINE 블루 #00ABE1, CTA #007FA8, 네이비, 흰색과 옅은 아이스 블루로 통일 |
| 독립된 가로형 이미지 | 서로 다른 섹션 비율의 13개 이미지 + 연결된 전체 페이지 HTML/PNG 제공 |
| 현재 A안 내용 부족 | 업무·대상 고객이 있는 서비스 4개, 비용 5항목, FAQ 8개와 답변, 현재 폼 항목, 개인정보 안내, 오류·제출 중·성공·실패·불확실 상태 추가 |
| 생성 창고 사진을 실제 시설 증빙으로 오인 | 사진에 개념 시각화 및 실제 시설 영상이 아님을 표시. Gardena/Katy 소유·규모·시설 증빙 주장 제거 |
| 가상의 WMS 화면 | 실제 재고 데이터나 화면을 꾸미지 않고 기능 흐름으로 재구성. ‘非实际系统截图’ 표시 |
| 비공식 로고·포장 그래픽, 교체 대상 히어로 | 지정한 공식 로고를 생성 참조로 사용. 전체 페이지와 보드에서는 실제 WebP 원본을 직접 렌더링. 히어로는 중국 흐름·블루 팔레트로 새로 제작 |

사진은 계속 **생성된 개념 이미지**입니다. 실제 Gardena/Katy 시설 사진으로 대체한 결과가 아닙니다. WMS 역시 실제 제품 화면이 아닌 기능 개념도입니다. 실제 증빙이 필요한 영역에서는 승인된 원본 자료로 교체해야 합니다.

## 파일 구성

| 이미지 | 내용 |
| --- | --- |
| 01-hero.png | 공식 로고 참조, 중국 판매자, 미국 해외창고·주문 이행 |
| 02-services.png | 첫 카드가 펼쳐진 사진 아코디언 / 핵심 서비스 4개 |
| 02-services-details.png | 이미지 없는 2×2 핵심 서비스 상세 카드 |
| 02-services-support.png | 추가 서비스 링크 4개 / 4단계 창고 작업 타임라인 |
| 03-flow.png | 중국 공장 → 국제운송 → 미국 통관 → 미국 직영 해외창고 → 미국 내 배송 5단계 |
| 04-channels.png | Amazon FBA·FBM 판매자 / 독립몰·TikTok Shop 판매자 / 공장·무역상 |
| 05-warehouse-responsibility.png | 미국 직영창고 운영, 작업 범위, IOR·Bond와 서비스 책임 자료 확인 |
| 05-wms-system.png | 재고 조회, 입고 기록, 출고 지시, 주문·작업 상태, 출고 이력 |
| 06-policy-customs.png | 상품 자료 / IOR 필요 / 책임 경계와 통관 서비스 적용 조건 |
| 06-cost.png | 운송 / 통관·수입 / 보관 / 창고 작업 / 미국 내 배송 |
| 07-faq.png | v3 FAQ 8개 / 전체 답변 / 관련 서비스 링크 |
| 08-quote.png | 5개 입력 그룹, 미선택 동의, 개인정보 |
| 08-footer.png | 서비스 / PNPLINE 소개 / 견적·연락 / 정책 / 언어 5개 그룹 |
| 09-form-states.png | 검증 오류, 제출 중, 성공, 실패, 결과 불확실 |

본문 섹션 이미지와 폼 상태 보드는 built-in image_gen의 원본 출력입니다. 생성 이미지의 색상·로고·문자에는 미세한 편차가 생길 수 있습니다. 검토 기준은 실제 로고와 CSS 색상을 적용한 **index.html / 00-fullpage.png / states.html**입니다. 상태 보드의 불필요한 생성 장식 문구는 브라우저 구성에서 제거했습니다.

공식 로고: assets/PNP-LINE.webp  
원본: F:/pnpline-landing/resources/logo/PNP-LINE.webp  
SHA-256: 051a5181409ba202f6cbfe7d967582016413d57cf9c2b1a9665eaffe1a2a843c

## 콘텐츠와 상태

- [A안 중국어 기준 문구](content.zh-CN.md), [기준 JSON](content.zh-CN.json)
- [생성 프롬프트 전체와 출력 원본 경로](prompts.json)
- [렌더링과 브랜드 검증 기록](review/capture-report.json)
- [파일 무결성 목록](manifest.json)

현재 S4는 서비스 전체 원고를 반영했으며, 일부 폼 레이블은 이미지 해상도에 맞춰 축약했습니다. 구현 시 문구의 최종 기준은 중국어 원문 파일입니다. 폼은 디자인 검토용 이미지이며 입력이나 외부 전송 기능이 없습니다. ‘提交咨询’ 링크는 상태 보드로 이동합니다. 개인정보 동의는 초기 이미지에서 미선택이며, 12개월 보관·삭제/익명화·삭제 신청 안내를 포함했습니다. 상태 보드의 이메일 seller@는 오류 표현용 가상 값입니다.

## 제작·검증

이미지 생성은 built-in image_gen으로 각 섹션을 따로 수행했습니다. 로컬 이미지 참조 도구의 파일 읽기 오류가 있어, 읽기 전용으로 확인한 대화 내 이미지 참조를 사용했습니다. 외부 유료 API로 전환하지 않았습니다.

전체 페이지는 생성 이미지를 이어 붙이는 브라우저 구성에 실제 로고와 정확한 CTA 색상을 적용해 캡처했습니다. 원본 생성 이미지에 픽셀 후처리를 하지 않았습니다.

확인 사항: 13개 본문 이미지 로딩, 데스크톱 가로 넘침 없음, 실제 로고 파일 해시 일치, 주요 채움 CTA #007FA8, 외부 요청 없음. 개별 생성 시안에서 콘텐츠와 개념 표시를 확인했습니다.

이는 데스크톱 컨셉 디자인입니다. 모바일 상세 화면, 실제 FAQ 조작, 폼 전송, 운영 사이트 적용은 포함하지 않습니다.

로컬 재캡처: 프로젝트의 이 폴더에서 `node src/capture.cjs`  
미리보기 서버: `node src/serve.cjs` — 출력되는 127.0.0.1 URL로 열기.



## 히어로 브랜드 요소 추가 수정

사용자가 표시한 v1 배너, 작업복, 트럭, 박스 위치에 공식 로고 기반 표현을 복원했습니다. 왼쪽 배너는 From China to the USA, 가운데 배너는 FROM CHINA TO THE USA / A BRIGHTER TOMORROW, 오른쪽 배너는 CHINA TO USA FULFILLMENT로 변경했습니다. 중앙 카피와 하단 경로는 v2 그대로입니다.

- 현재 히어로: [01-hero.png](01-hero.png)
- 수정본 별도 파일: [01-hero-branded.png](01-hero-branded.png)
- 수정 전 보존본: [review/01-hero-before-branding.png](review/01-hero-before-branding.png)
- 이번 수정의 image_gen 프롬프트: [hero-branding-edit.json](hero-branding-edit.json)

사진 속 로고는 제공된 공식 원본을 참조해 표면과 원근에 맞춰 생성한 표현입니다. 웹 헤더의 로고는 원본 WebP를 직접 사용합니다.


## 이전 수정 기록 — 서비스 섹션의 v1 아코디언 레이아웃

이전 단계에서 02-services.png를 v1의 한 줄 사진 아코디언 구성으로 변경했습니다. 첫 카드만 넓게 펼치고 나머지 세 카드는 축약된 상태였습니다.

- 당시 v1 레이아웃 이미지: [02-services-v1-layout.png](02-services-v1-layout.png)
- 수정 전 보존본: [review/02-services-before-v1-layout.png](review/02-services-before-v1-layout.png)
- built-in image_gen 수정 프롬프트: [services-v1-layout-edit.json](services-v1-layout-edit.json)
- 전체 페이지 캡처도 새 비율에 맞춰 갱신했습니다.


## 이전 수정 기록 — 채널 섹션의 4개 사진 카드 디자인

이전 단계에서 04-channels.png의 텍스트 열 구성을 네 개의 동일한 사진 카드로 바꿨습니다. 카드마다 사진을 크게 배치하고 흰색 하단 영역에 채널명과 핵심 업무 두 줄을 넣었습니다. Amazon은 FBA·주문 출고 준비, 독립몰·Shopify는 개별 포장, TikTok Shop은 상품 콘텐츠와 배송 준비, B2B·소매는 팔레트 단위 출고 장면으로 구분했습니다. 기존 중국어 채널 설명과 개념 이미지 표시는 유지했습니다.

- 당시 4카드 이미지: [04-channels-cards.png](04-channels-cards.png)
- 수정 전 보존본: [review/04-channels-before-cards.png](review/04-channels-before-cards.png)
- built-in image_gen 수정 프롬프트: [channels-card-edit.json](channels-card-edit.json)
- 전체 페이지와 섹션별 캡처를 갱신했으며 이미지 로딩과 데스크톱 가로 넘침 검사를 통과했습니다.


## S6 정책·통관 섹션 추가

WMS와 비용 사이에 어두운 사진 중심의 정책·통관 안내를 추가했습니다. 저장소에서는 IOR·De Minimis 기사 경로의 기획 기록만 확인됐으며, 검수·게시된 중국어 기사 파일은 확인되지 않았습니다. 따라서 브리프가 지정한 안전한 대체안인 통관 서비스 범위 블록을 사용했습니다. 시행일·관세율·행정명령·IOR 또는 Bond 보유 사실을 표시하지 않았습니다.

- 이미지: [06-policy-customs.png](06-policy-customs.png)
- 적용 문구: [policy-customs-content.zh-CN.md](policy-customs-content.zh-CN.md)
- built-in image_gen 프롬프트와 생성 기록: [policy-customs-addition.json](policy-customs-addition.json)
- 사진은 개념 이미지이며 실제 신고 서류가 아닙니다.



## S5 직영창고·책임 근거와 WMS 시스템 분리

기존 S5의 서로 다른 근거 유형을 두 개의 독립된 가로형 섹션으로 분리했습니다. 첫 섹션은 미국 창고의 직영 운영과 창고 작업 범위를 확인 사항으로 보여 주고, IOR·Bond·자격·책임 범위는 검수할 자료와 서비스 범위로 구분합니다. 실제 시설로 오인될 사진·주소·거점명·시설 수치·인증 배지는 사용하지 않았습니다.

둘째 섹션은 WMS 기능 후보 5개를 별도 시스템 화면으로 구성했습니다. 고객 데이터·실시간 수치·자동화 또는 AI 기능을 만들지 않았으며, 실제 화면이 아닌 개념 예시임을 표시했습니다.

- 직영창고·책임 근거: [05-warehouse-responsibility.png](05-warehouse-responsibility.png)
- WMS 시스템: [05-wms-system.png](05-wms-system.png)
- 적용 문구: [s5-split-content.zh-CN.md](s5-split-content.zh-CN.md)
- built-in image_gen 생성 기록: [s5-split-imagegen.json](s5-split-imagegen.json)
- 이전 WMS 이미지 `05-platform.png`는 비교용으로 보존하고 전체 페이지에서는 사용하지 않습니다.


## 채널 섹션의 S3 고객 유형 구조 적용

현재 04-channels.png를 판매 채널 4개에서 S3 고객 유형 3개로 조정했습니다. Amazon FBA·FBM 판매자, 독립몰·TikTok Shop 판매자, 공장·무역상을 서로 다른 고객 진입점으로 보여 줍니다. Amazon을 먼저 배치하면서 B2B도 독립된 세 번째 선택지로 유지했습니다.

독립몰과 TikTok Shop은 하나의 고객 유형으로 묶되 Shopify와 TikTok Shop의 이동 경로를 각각 표시했습니다. 플랫폼 로고·공식 제휴·인증 표시는 사용하지 않았으며 사진은 개념 이미지입니다.

- 현재 이미지: [04-channels.png](04-channels.png)
- 수정본 별도 파일: [04-channels-s3-customer-types.png](04-channels-s3-customer-types.png)
- 수정 전 4카드 시안: [review/04-channels-before-s3-customer-types.png](review/04-channels-before-s3-customer-types.png)
- 적용 문구: [channels-s3-content.zh-CN.md](channels-s3-content.zh-CN.md)
- built-in image_gen 생성 기록: [channels-s3-edit.json](channels-s3-edit.json)



## S2 중국→미국 물류 흐름 5단계 재구성

기존 6단계에서 미국 도착·입고 준비, 입고·보관, 주문 처리로 분산됐던 중간 구간을 브리프의 5단계로 다시 구성했습니다. 미국 통관을 세 번째 독립 관문으로 표시하고, 미국 직영 해외창고 단계에는 입고 검수·재고 관리·출고 작업을 통합했습니다.

직영 운영으로 확정된 것은 미국 창고 단계이며 다른 물류 단계까지 모두 직접 수행한다는 의미로 확대하지 않았습니다. 실제 항로·거리·기간·시설·통관 결과도 표시하지 않았습니다.

- 현재 이미지: [03-flow.png](03-flow.png)
- 수정본 별도 파일: [03-flow-five-stage.png](03-flow-five-stage.png)
- 수정 전 6단계 시안: [review/03-flow-before-five-stage.png](review/03-flow-before-five-stage.png)
- 적용 문구: [flow-five-stage-content.zh-CN.md](flow-five-stage-content.zh-CN.md)
- built-in image_gen 생성 기록: [flow-five-stage-edit.json](flow-five-stage-edit.json)



## 이전 수정 기록 — S4 전체 카드 확장

기존 아코디언에서 축약됐던 네 핵심 서비스를 모두 열린 패널로 바꾸고, 각 서비스의 설명·적합 대상·작업 요약·CTA를 복원했습니다. 일건 배송에는 Amazon FBM만 포함하고 FBA 중계·보충은 별도 서비스로 유지했습니다.

하단에는 창고·재고, 반품·라벨·검품, 미국 B2B 배송, 기타 물류 문의 링크를 별도 위계로 추가했습니다. 창고 작업 절차도 입고 검수부터 출고 배송 또는 FBA 보충까지 한 줄 흐름으로 표시했습니다.

- 현재 이미지: [02-services.png](02-services.png)
- 완성형 별도 파일: [02-services-complete.png](02-services-complete.png)
- 수정 전 아코디언 시안: [review/02-services-before-content-completion.png](review/02-services-before-content-completion.png)
- 적용 문구: [services-complete-content.zh-CN.md](services-complete-content.zh-CN.md)
- built-in image_gen 생성 기록: [services-complete-edit.json](services-complete-edit.json)

## 이전 수정 기록 — S4 아코디언 복원과 높이 확장

첫 카드가 넓게 펼쳐지고 나머지 세 카드가 좁게 놓인 기존 사진 아코디언 구도를 복원했습니다. 사진 아래에는 네 서비스의 설명·적합 대상·작업 요약·CTA를 단순한 텍스트 열로 배치했습니다. 보조 링크 4개와 창고 작업 절차는 하단에 분리했습니다.

새 이미지 크기는 1448 × 1086px입니다. 16:9에서 4:3으로 높이를 늘렸으며 사진은 비율을 유지합니다. 아코디언은 정적 시안으로, 펼침·접힘 동작은 구현하지 않았습니다.

- 현재 시안: [02-services.png](02-services.png)
- 별도 파일: [02-services-accordion-expanded.png](02-services-accordion-expanded.png)
- 이전 전체 카드 버전: [review/02-services-before-accordion-restoration.png](review/02-services-before-accordion-restoration.png)
- 전체 원고: [services-complete-content.zh-CN.md](services-complete-content.zh-CN.md)
- 전체 생성 프롬프트: [services-accordion-expanded-edit.json](services-accordion-expanded-edit.json)


## S4 사진 아코디언과 상세 카드 분리

사진 아코디언을 독립된 이미지로 유지하고, 상세 정보를 이미지 없는 2×2 카드 섹션으로 분리했습니다. 카드의 큰 서비스명, 본문, 파란 필드명(적합 대상·작업 내용), CTA 순서로 글자 크기와 간격을 구분했습니다. 카드별로 설명·대상·작업·CTA를 유지했고 하단에는 보조 링크 4개와 창고 작업 절차를 배치했습니다.

- 사진 아코디언: [02-services.png](02-services.png)
- 상세 카드: [02-services-details.png](02-services-details.png)
- 분리 전 보존본: [review/02-services-before-detail-split.png](review/02-services-before-detail-split.png)
- 원고: [services-complete-content.zh-CN.md](services-complete-content.zh-CN.md)
- 생성 기록: [services-details-split-edit.json](services-details-split-edit.json)

두 이미지는 전체 페이지에서 연속 배치합니다. 정적 이미지 시안이며 아코디언이나 카드 CTA의 실제 인터랙션은 구현하지 않았습니다.


## S4 상세 카드 여백·타이포 조정

2×2 상세 카드 구조와 전체 문구를 유지하면서 카드 사이의 간격과 내부 패딩을 확대했습니다. 서비스 제목·본문·필드명·값·CTA의 글자 크기와 무게를 낮추고, 그림자와 그라데이션 없이 얇은 테두리와 평면 CTA를 사용해 시각적 밀도를 줄였습니다.

- 현재 이미지: [02-services-details.png](02-services-details.png)
- 수정 전 보존본: [review/02-services-details-before-airy-spacing.png](review/02-services-details-before-airy-spacing.png)
- 생성 기록: [services-details-airy-edit.json](services-details-airy-edit.json)


## S4 하단 정보 구조 개선

추가 서비스 4개를 번호가 있는 독립 링크 타일로 구성하고, 창고 작업 절차를 연결선과 단계 번호가 있는 4단계 타임라인으로 변경했습니다. 적용 조건 문구는 흐름에서 분리해 별도 각주로 배치했습니다.

- 현재 이미지: [02-services-details.png](02-services-details.png)
- 수정 전 보존본: [review/02-services-details-before-bottom-redesign.png](review/02-services-details-before-bottom-redesign.png)
- 생성 기록: [services-details-bottom-redesign.json](services-details-bottom-redesign.json)


## S4 추가 서비스·창고 작업 흐름 독립

핵심 서비스 상세 카드에서 추가 서비스와 창고 작업 흐름을 제거하고, 이를 넉넉한 상하 여백을 가진 별도의 16:9 섹션으로 분리했습니다. 전체 페이지에서는 사진 아코디언, 핵심 서비스 상세 카드, 추가 서비스·창고 작업 흐름 순서로 연결합니다.

- 핵심 서비스 상세: [02-services-details.png](02-services-details.png)
- 독립 보조 섹션: [02-services-support.png](02-services-support.png)
- 분리 전 보존본: [review/02-services-details-before-support-split.png](review/02-services-details-before-support-split.png)
- 생성 기록: [services-support-split.json](services-support-split.json)


## FAQ v3 8개 확장

기존 6개 문답을 v3 기준 문구로 교체하고 미국 직영창고와 WMS 재고·출고 조회 질문을 추가했습니다. Q3–Q8에는 브리프의 관련 서비스 링크를 배치했습니다. 시설 자료가 준비되지 않은 Q7은 조건부 대체 경로 /contact/를 사용하며, 검수된 IOR 기사가 확인되지 않은 Q6은 /customs/ior/만 연결합니다.

- 현재 이미지: [07-faq.png](07-faq.png)
- 전체 원고와 링크: [faq-v3-content.zh-CN.md](faq-v3-content.zh-CN.md)
- 수정 전 보존본: [review/07-faq-before-v3-eight.png](review/07-faq-before-v3-eight.png)
- 생성 기록: [faq-v3-eight-edit.json](faq-v3-eight-edit.json)


## 푸터 v3 5개 그룹 확장

기존 견적 이미지 하단의 가격·연락·개인정보 3링크 푸터를 제거하고, 푸터를 별도 가로형 섹션으로 분리했습니다. 새 푸터는 서비스, PNPLINE 소개, 견적·연락, 정책, 언어의 5개 그룹을 포함합니다. 언어 목적지는 승인 전이라 URL을 표시하지 않았고 공개 연락처·법인정보·인증 배지도 추가하지 않았습니다. 전체 페이지에서는 공식 PNP-LINE.webp를 빈 로고 플레이트에 직접 렌더링합니다.

- 견적 전용 이미지: [08-quote.png](08-quote.png)
- 푸터 배경 이미지: [08-footer.png](08-footer.png)
- 공식 로고 포함 푸터 캡처: [review/footer-1440.png](review/footer-1440.png)
- 푸터 원고와 IA 경로: [footer-v3-content.zh-CN.md](footer-v3-content.zh-CN.md)
- 분리 전 보존본: [review/08-quote-before-footer-split.png](review/08-quote-before-footer-split.png)
- 생성 기록: [footer-v3-five-groups-edit.json](footer-v3-five-groups-edit.json)


## 견적 섹션 공식 PNPLINE 로고 추가

첨부된 공식 PNP-LINE.webp를 참조해 견적 섹션 좌측 상단의 어두운 여백에 흰색 로고 플레이트를 추가했습니다. 로고는 한 번만 배치했으며 기존 창고 이미지, 중국어 카피, 폼 구성과 개인정보 문구는 유지했습니다.

- 현재 이미지: [08-quote.png](08-quote.png)
- 수정 전 보존본: [review/08-quote-before-logo.png](review/08-quote-before-logo.png)
- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)
- 생성 기록: [quote-logo-addition.json](quote-logo-addition.json)


## 견적 섹션 상자 로고 배치 수정

좌측 상단의 로고 플레이트를 제거하고 공식 PNPLINE 로고를 전경 상자의 전면에 인쇄된 포장 그래픽으로 옮겼습니다. 로고는 파란 테이프 오른쪽의 골판지 면에 원근, 표면 질감, 조명을 반영해 한 번만 배치했습니다.

- 현재 이미지: [08-quote.png](08-quote.png)
- 좌측 상단 배치 보존본: [review/08-quote-before-box-logo-correction.png](review/08-quote-before-box-logo-correction.png)
- 최초 무로고 보존본: [review/08-quote-before-logo.png](review/08-quote-before-logo.png)
- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)
- 생성 기록: [quote-box-logo-correction.json](quote-box-logo-correction.json)


## 견적 섹션 상자 전면 로고 위치 확정

사용자가 표시한 영역에 맞춰 공식 PNPLINE 로고를 전경 상자의 넓은 전면으로 이동했습니다. 로고는 파란 테이프 왼쪽의 골판지 면에 인쇄되며, 좌측 상단 플레이트와 오른쪽 측면 로고, 빨간 위치 표시는 제거했습니다.

- 현재 이미지: [08-quote.png](08-quote.png)
- 오른쪽 측면 배치 보존본: [review/08-quote-before-front-panel-logo.png](review/08-quote-before-front-panel-logo.png)
- 공식 로고 원본: [../../resources/logo/PNP-LINE.webp](../../resources/logo/PNP-LINE.webp)
- 생성 기록: [quote-front-panel-logo.json](quote-front-panel-logo.json)


## 입력폼–푸터 블렌딩과 푸터 여백 조정

입력폼 이미지 하단을 푸터의 딥 네이비(#082A45)로 점진 전환해 수평 경계를 완화했습니다. 푸터는 기존 텍스트와 5개 정보 그룹을 유지하면서 상하 빈 영역을 제거해 1672 × 455px로 축소했습니다. 공식 로고 오버레이도 새 크롭 좌표에 맞춰 이동했습니다.

- 블렌딩된 입력폼: [08-quote.png](08-quote.png)
- 압축된 푸터: [08-footer.png](08-footer.png)
- 입력폼 수정 전: [review/08-quote-before-footer-blend.png](review/08-quote-before-footer-blend.png)
- 푸터 수정 전: [review/08-footer-before-compact-spacing.png](review/08-footer-before-compact-spacing.png)
- 작업 기록: [quote-footer-blend-spacing.json](quote-footer-blend-spacing.json)


## 입력폼–푸터 이음선 제거

입력폼 하단의 장면을 더 긴 범위에서 딥 네이비로 전환하고, 브라우저 조립 단계에서 양쪽 경계를 동일한 #082A45로 고정했습니다. 입력폼 하단 10%에는 투명도 그라데이션을 적용하고 푸터 상단 13%는 같은 단색으로 덮었으며, 분수 픽셀 리사이징으로 생기는 선을 막기 위해 두 섹션을 1px 겹쳤습니다.

- 현재 입력폼: [08-quote.png](08-quote.png)
- 현재 푸터: [08-footer.png](08-footer.png)
- 수정 전 입력폼: [review/08-quote-before-seamless-join.png](review/08-quote-before-seamless-join.png)
- 작업 기록: [quote-footer-seamless-join.json](quote-footer-seamless-join.json)


## 1920px 전체 페이지 레이아웃

전체 페이지 캔버스를 1920px로 확장하고, 모든 섹션에 1440px 콘텐츠 래퍼를 적용했습니다. 콘텐츠는 좌우 240px 중앙 여백 안에서 가로폭을 빈 공간 없이 채우며, 각 섹션에는 상단 32px과 하단 32px 여백을 둡니다. CTA와 공식 로고 오버레이는 1440px 콘텐츠 좌표계를 유지합니다.

- 전체 페이지: [00-fullpage.png](00-fullpage.png)
- 브라우저 시안: [index.html](index.html)
- 검증 기록: [review/capture-report.json](review/capture-report.json)
- 적용 전 소스: [review/layout-before-1920](review/layout-before-1920)


## 입력폼 1920px 풀블리드와 푸터 색상

입력폼 섹션은 1440px 콘텐츠 제한의 예외로 처리해 배경 이미지가 1920px 전체 폭을 채우도록 변경했습니다. 상하 32px 여백은 유지합니다. 푸터 외곽과 내부 이미지 배경은 #082A45로 통일했으며, 텍스트·구분선·공식 로고의 밝기는 유지합니다.

- 전체 페이지: [00-fullpage.png](00-fullpage.png)
- 입력폼 검토: [review/quote-1920.png](review/quote-1920.png)
- 푸터 검토: [review/footer-1920.png](review/footer-1920.png)
- 검증 기록: [review/capture-report.json](review/capture-report.json)
- 작업 기록: [quote-fullbleed-footer-color.json](quote-fullbleed-footer-color.json)


## FAQ–입력폼 64px 간격

FAQ와 입력폼 사이에 보이던 긴 네이비 바를 제거했습니다. FAQ 하단 32px과 입력폼 상단 32px을 같은 아이스 블루(#F3F8FA)로 연결해 콘텐츠 간 간격을 정확히 64px로 설정했습니다. 입력폼 하단 여백은 #082A45로 유지해 푸터 전환은 보존합니다.

- 전체 페이지: [00-fullpage.png](00-fullpage.png)
- 입력폼 검토: [review/quote-1920.png](review/quote-1920.png)
- 검증 기록: [review/capture-report.json](review/capture-report.json)
- 작업 기록: [faq-quote-gap.json](faq-quote-gap.json)
