# v4 본문 점검 및 UX Writing 반영

2026-11-02. 탑바와 Hero/Journey는 점검·수정 범위에서 제외했다. 기존 영문 사이트의 언어를 유지하고 중국어 v4의 의미와 조건을 반영했다. 원고는 검토 초안이며 실제 운영 승인이나 중국어 사이트 배포를 뜻하지 않는다.

## 확인한 대상

- 원고: docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md 및 v4-handoff.md.
- 실제 앱: C:/Users/KIM TAEHYUNG/.codex/visualizations/2026/11/01/01a19616-7090-7b72-86b1-f85ae4da029a/pnpline-web.
- 실행 주소: http://127.0.0.1:3091/.
- 이전 작업 기록: SERVICE-DETAILS.ko.md, WAREHOUSE-SYSTEMS.ko.md, PROCESS-CONSULTATION.ko.md, PRICING-DETAILS.ko.md, FAQ-TOPICS.ko.md, QUOTE-INQUIRY.ko.md 및 저장소의 각 컨셉 design-notes.ko.md. 아래 현재 결과가 이전 배치 설명을 대체한다.

## 현재 순서와 v4 대조

Services → Freight options → Fulfillment options → Import planning → System connections → Customer Types → Warehouse → System requirements → Process → Pricing 기본 표 → 수입 비용 명세 → 추가 과금 조건 → FAQ → Quote → Footer.

| v4 영역 | 반영 결과 |
| --- | --- |
| Services 28–51행 | 기존 4개 서비스와 확장 화면을 유지했다. FCL/LCL/항공, 단건 출고/FBA 임시 보관·라벨·분할 보충, 반품 검품·재라벨링·재입고, B2B 조건, IOR/HS/FDA/FCC, 플랫폼/ERP/API 요구를 다룬다. 반품 재라벨링을 명시적으로 보완했다. |
| Customer Types 57–65행 | FBA/FBM, Shopify/TikTok Shop, Factories/B2B, Walmart의 포장·라벨·예약 조건과 공식 제휴가 아니라는 안내를 유지했다. 무역업체(trading companies)를 패널 설명에 명시했다. |
| Warehouse & Systems 71–81행 | 직영 운영·입고/보관/출고·수락 조건·서류·책임·재고 기록을 설명한다. 기능/권한·갱신·플랫폼/ERP 확인 3행을 창고 바로 뒤로 이동했다. 창고에서 시스템 안내로 되돌아가는 경로를 순방향으로 바꿨으며 같은 내용을 중복 생성하지 않았다. v4의 #evidence는 창고 헤더의 별칭 앵커로 지원하고 #warehouse도 유지했다. |
| Process 87–91행 | 요구 설명 → 조건 검토 → 견적 확인의 3단계를 유지했다. 필요한 서비스를 파악한 다음 상담 절차를 읽도록 도입을 연결했다. |
| Pricing 95–107행 | 복원된 기존 5행과 추가 4+3행을 유지했다. 운송 방식/체적/중량, 입고 형태/검수, 보관 방식/기간, 피킹/포장/라벨/검품/반품, 배송 형태/예약을 구체화했다. 통관/IOR/서비스비/세금의 별도 명세와 최소 요금/장기 보관/특수 작업을 함께 확인한다. |
| FAQ 113–145행 | v4 8개 문답과 기존 특수 상품 질문을 합친 9개를 유지했다. IOR 답변은 폼의 실제 Not sure 선택지와 연결한다. UI와 JSON-LD는 같은 faq-data.ts를 사용한다. |
| Quote 149–166행 | 6개 정보와 동의 항목을 유지했다. 미정 정보는 Not sure로 적을 수 있다고 안내한다. 실제 제출이 연결되지 않아 버튼을 Check inquiry details로 바꾸고 미전송 사실을 명확히 표시한다. 실제 접수와 운영 개인정보 정책은 아직 미완료다. |
| Footer 172행 | 서비스·창고·비용·FAQ·문의·개인정보 링크를 유지했다. Pricing & cost details는 #pricing으로 연결한다. |

## 문구 편집 기준

서비스 선택 → 내 판매 방식 → 실제 작업과 기록 → 상담 준비 → 비용 확인 → 남은 질문 → 문의 정보 준비의 순서로 읽히게 했다. 추상적인 next move, clarify the rest 대신 shipment, import requirements, records 같은 구체적인 대상을 사용했다. 지원 범위는 확인 대상으로 설명하며 확정 요금·일정·전면 자동 연동을 새로 약속하지 않았다.

- Import: Bring the cargo. Let’s clarify the rest. → Clarify import requirements. Before you ship.
- Systems: Agree how you use the system. → Know what you can see and manage.
- Pricing: Clear scope. A quote built around your operation. → Understand the costs. Then compare your quote.
- Quote: Let’s plan your next move. → Tell us about your shipment.
- 실제 접수가 없는 제출 버튼: Submit inquiry → Check inquiry details.

명확성, 문맥 연결, 고객 입장의 정보 탐색, 근거 없는 약속 여부를 기준으로 다시 읽었다. 수치를 만들어 구체성을 높이거나 자료에 없는 보장을 추가하지 않았다.

## 검증

실행 응답에서 섹션 순서, ID 중복 없음, 시스템 확인 영역 1개, #evidence, 반품 재라벨링 및 무역업체 문구를 확인했다. 변경 전 파일과 비교해 탑바·히어로 JSX가 동일함을 확인했다. 인앱 브라우저에서 1920×1080, 834×1112, 390×844의 가로 넘침이 없었고 데스크톱 본문은 1320px이었다. 모바일 고객 유형 전환으로 무역업체 설명을 확인했으며 Pricing 5행과 시스템 확인 3행을 유지했다. 브라우저 오류 로그는 비어 있었다. TypeScript 검사를 수행했다.

이번 검증은 콘텐츠와 배치 확인이며 실제 문의 서버 접수, 서비스 제공 가능 여부 또는 운영 개인정보 정책의 승인을 검증한 것은 아니다.
