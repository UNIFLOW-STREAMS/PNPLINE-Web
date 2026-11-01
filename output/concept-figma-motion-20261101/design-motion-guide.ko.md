# PNPLINE — One connected journey

작성일: 2026-11-01  
산출물: 영문 랜딩페이지 컨셉 이미지 10장, 검토용 HTML 갤러리, 모션 스터디, 레이아웃·인터랙션 명세, 생성 프롬프트  
제작: imagegen-frontend-web 스킬 및 기본 내장 image_gen 도구

## 컨셉

중국 출고부터 미국 주문 이행까지 하나의 시안 블루 경로가 이어진다. 항만의 컨테이너, 해상의 선박, 미국 창고의 재고, 최종 배송의 상자가 같은 미니어처 세계에 속한다. 비주얼은 업무 구간을 설명하고 본문은 작업 조건과 견적 준비사항을 명확하게 안내한다.

짧은 타이포 문장과 실제로 만질 수 있을 듯한 물류 모형을 중심으로 구성한다. 선으로 나눈 서비스, 고객 유형 확장 패널, 창고 단면, 가로 프로세스, 비용 구성표, FAQ, 문의 폼을 섞어 섹션마다 읽는 방식을 바꾼다. 고객 유형의 시안 블루와 견적의 차콜 배경 사이에 차분한 흰색 정보 구간을 둔다.

이 폴더는 시각·동작 방향을 검토하는 컨셉 산출물이다. 이미지 속 링크·폼은 정지 이미지이며 실제 접수 기능이 아니다. HTML의 세 가지 모션 스터디만 직접 작동한다. 개별 이미지의 글자·여백은 생성 결과이므로 정확한 구현 수치는 아래 레이아웃 명세를 따른다.

## 피그마에서 확인한 근거

참고: [Setby Figma motion — node 6:172](https://www.figma.com/design/zwdpAYgoPQLVHUHAM8IVws/figma-motion-setby-ayz-z-the-designer?node-id=6-172)

공식 Figma 도구로 디자인 컨텍스트, 애니메이션 트랙 57개, 약 20.164초의 반복 타임라인을 읽고 MP4로 확인했다. 원본 타임라인과 클릭·hover 인터랙션은 구분한다. 아래 서비스 선택·탭·FAQ의 동작은 PNPLINE을 위한 제안이며 원본에 구현되어 있음을 주장하지 않는다.

| 확인 항목 | 원본 근거 | PNPLINE 적용 |
| --- | --- | --- |
| 글자별 등장 | 6:179–6:186, opacity 0→1, y 32→0, 약 40ms 순차 지연 | 영문 제목의 단어별 등장, 최대 72px |
| 큰 오브젝트의 이동과 스케일 | 6:188, scale .8→1, 큰 y 이동 | 항만·선박·창고를 연결하는 카메라 흐름 |
| 흐림에서 선명해지는 문장 | 6:240, blur 10.5→0 | 짧은 전환 문장에만 약하게 적용, 본문은 항상 선명하게 표시 |
| 컬러 커튼 | 6:335–6:340, 수직 패널 퇴장 | 원본 오렌지를 PNPLINE 시안 블루로 변경 |
| 서비스 행과 이미지 확대 | 6:271–6:320, 선으로 나눈 행과 이미지 스케일 트랙 | 읽기 쉬운 행과 작은 선택 상태로 절제 |
| 이징 | 다수 트랙 cubic-bezier(.241,0,.138,1.017) | 일반 UI에서는 끝값을 1로 줄인 곡선 사용 |

원본에서 가져오는 것은 동작 언어와 편집 방식이다. 원본의 Setby 문구·운영 수치·오렌지·398px 제목은 PNPLINE 정보로 사용하지 않는다.

## 레이아웃 수치

| 항목 | 구현 기준 |
| --- | --- |
| 기준 화면 | 1920px 데스크톱 |
| 본문 최대 폭 | 1320px |
| 1920px 좌우 여백 | 각 300px |
| 그리드 | 12열, 열 간격 24px, 열 너비 88px |
| 본문 컨테이너 | width: min(1320px, calc(100% - 48px)); margin-inline: auto |
| 히어로·섹션 배경 | 화면 전체 너비 |
| H1 | 68–72px, 줄 높이 1.08–1.12, 2줄 이내 |
| H2 | 44–56px, 줄 높이 1.12–1.2 |
| 본문 | 18–20px, 줄 높이 1.5–1.65 |
| 행 제목 | 22–26px |
| 보조 문구 | 14–16px, 주요 설명에는 작은 캡션 크기 사용 금지 |
| 버튼 | 높이 48–52px, 좌우 패딩 22–28px, 모서리 2px |
| 주요 섹션 여백 | 상하 100–140px, 정보 밀도에 맞게 조절 |
| 기본 서체 방향 | 정돈된 산세리프, 영문 Inter 계열과 간체 Noto Sans SC 계열 |
| 헤어라인 | 1px, 밝은 회색 |
| 색상 | White #FFFFFF / Light gray #F4F6F7 / Charcoal #172126 / Cyan #00ABE1 |

화면이 1440px이면 본문 좌우 여백은 각 60px이 된다. 데스크톱에서 콘텐츠 최대 폭을 900px 등으로 축소하지 않는다. 정확한 수치는 생성 이미지의 픽셀을 역산하지 않고 이 표를 기준으로 정한다.

이미지 파일은 섹션별 가로형 스토리보드다. 실제 웹페이지의 모든 섹션 높이를 이미지의 16:9 비율로 통일하지 않는다. Navigation은 약 80–88px, Hero는 약 900–1000px, Services·Warehouse는 약 850–1000px, Customer Types·Process·Pricing·FAQ는 약 650–850px, Quote는 약 850–950px, Footer는 약 360–440px에서 콘텐츠에 맞게 조정한다. 내비게이션 이미지에는 열린 메뉴 상태도 함께 보인다.

## 섹션 설계

| 순서 | 섹션 | 역할 | 형태 |
| --- | --- | --- | --- |
| 01 | Navigation | 서비스·운영 범위와 견적에 즉시 접근 | 작은 로고, 앵커 링크, 확장 메뉴 |
| 02 | Hero | 중국 출고와 미국 주문 이행의 연결을 설명 | 전체 너비 물류 장면, 짧은 제목 |
| 03 | Services | 필요한 업무 구간을 선택 | 컨테이너 이미지와 확장 행 |
| 04 | Customer Types | 판매자·공장·무역업체의 요구를 구분 | 시안 블루, 60/20/20 연속 패널 |
| 05 | Warehouse & Systems | 입고·재고·출고를 이해 | 3D 단면, 탭과 작업 핀 |
| 06 | Process | 문의 준비부터 미국 출고까지 순서 안내 | 하나의 가로 경로와 4단계 |
| 07 | Pricing | 비용 항목과 견적 기준을 이해 | 단일 비용 구성표 |
| 08 | FAQ | 인계·출고 방식·문의 준비 질문 해소 | 5개 아코디언 |
| 09 | Quote | 요구 정보를 한 번에 전달 | 차콜 배경, 밝은 2열 폼 |
| 10 | Footer | 페이지 이동과 문의 경로 정리 | 작은 로고와 4열 링크 |

공통 컴포넌트는 확장 패널, 얇은 구분선, 비대칭 편집 배치, 넓은 이미지 프레임의 네 가지로 제한한다. 박스에 인쇄된 CN→US 경로를 마지막 문의 구간의 작은 발견 요소로 사용한다.

## 모션과 인터랙션

### 공통

- 기본 UI 이징: cubic-bezier(.241, 0, .138, 1).
- 링크·선택 피드백은 160–220ms, 펼침은 240–300ms, 큰 이미지 전환은 450–600ms.
- 제목은 단어 단위로 16–32px 아래에서 등장한다. 단어별 지연은 40ms, 한 문장 전체가 900ms 안에 읽힌다.
- 일반 본문·가격 구성·폼을 애니메이션이 끝날 때까지 숨기지 않는다.
- 컬러 커튼은 최초 장면 전환이나 제한된 구간 한 번에만 사용한다. 매 섹션마다 화면을 가리지 않는다.
- prefers-reduced-motion에서는 이동·흐림·패널 커튼을 생략한다. 최종 장면과 내용은 즉시 표시한다.
- 이미지 지연이나 영상 실패에도 제목, 서비스 링크와 견적 버튼에 접근할 수 있어야 한다.

### Hero

스크롤 진행률 0–28%는 중국 항만과 선적, 28–50%는 해상 이동, 50–76%는 미국 창고 도착, 76–100%는 주문 준비와 미국 출고 장면으로 제안한다. 이 구간 배분은 원본 타임라인 복제가 아닌 PNPLINE 연출안이다.

스크롤 위치가 영상 시점 또는 카메라 시점을 결정한다. 아래로 이동하면 진행하고 위로 이동하면 되돌아가며 정지하면 현재 장면을 유지한다. 자동 반복을 기본 동작으로 사용하지 않는다. 제목은 초반에 완성하고 중간 장면에서 필요한 짧은 문장만 교체한다. 서비스·견적 앵커는 영상 끝을 기다리지 않고 사용할 수 있다.

### Services / Customer Types

Services는 한 행만 확장한다. hover에서는 포인트 색과 화살표를 예고하고 클릭·키보드로 선택한다. Customer Types는 선택한 패널만 넓히고 텍스트가 잘리지 않도록 최소 폭을 확보한다. 키보드와 터치에서도 같은 정보가 보인다.

### Warehouse / Process

창고의 Receiving / Inventory / Dispatch 탭은 각 작업 핀·경로·설명을 함께 바꾼다. 실제 업무 시스템 연동이나 재고 수치처럼 보이는 가짜 대시보드를 만들지 않는다. Process 경로는 섹션 스크롤에 맞춰 순차 강조하되 설명은 처음부터 읽을 수 있게 한다.

### Pricing / FAQ / Quote / Footer

Pricing 표는 고정 정보로 유지한다. FAQ는 한 질문을 열되 닫힌 질문의 제목과 초점을 명확하게 유지한다. Quote는 라벨을 항상 표시하고 필수값, 오류, 제출 진행, 완료 상태를 구분한다. 제출 성공 상태는 실제 서버 응답이 있을 때만 표시한다. Footer의 페이지 위 이동은 모션 감소 설정에서 즉시 수행한다.

## 영문 문구 보완

### FAQ의 닫힌 답변 제안

**Do you support individual orders and replenishment?**  
Tell us whether you need parcel orders, marketplace replenishment or bulk distribution. We will confirm the handling scope for your operation.

**What information do you need for a quote?**  
Share your product, shipment size, origin, US destination, monthly volume and services needed. If a detail is undecided, mark it as not sure.

**Can you handle special products or packing requirements?**  
Describe the product and any storage, labeling or packing requirements. Suitability and additional handling need to be confirmed before receiving goods.

**How are storage and fulfillment charges calculated?**  
Your quotation sets out the agreed receiving, storage, order preparation and delivery scope. The basis depends on the cargo profile and operating requirements.

### Quote

화면의 필드 구성은 컨셉 제안이다. 최종 접수 필수값과 개인정보 고지는 운영 검토 후 확정한다. 미정 정보 입력을 허용하고, 출발지·출고 방식·IOR 필요 여부 등은 실제 운영 요구에 따라 추가한다. 시안의 이미지 속 예시 이메일은 플레이스홀더다.

## 모바일 재배치

- 1024px 이하에서는 2열 구성을 먼저 줄이고, 768px 이하에서는 본문 좌우 20–24px을 확보한다.
- H1은 약 36–42px, H2는 약 30–36px, 본문은 16–18px.
- 내비게이션은 로고·견적·메뉴 버튼 순서로 줄이고 메뉴는 세로 목록으로 연다.
- 히어로는 주요 물류 흐름이 보이는 별도 세로 안전 구도로 재편집한다. 데스크톱 장면 전체를 작은 폭에 축소하지 않는다.
- 서비스와 고객 유형은 세로 아코디언으로 바꾼다. 작은 화면에서 얇은 세로 슬라이스를 유지하지 않는다.
- 창고는 선택한 작업 구역과 설명을 함께 보여준다.
- 프로세스는 세로 경로로, 가격 구성표는 항목별 정의 목록으로 재배치한다.
- 문의 폼은 1열로 바꾸고 라벨을 유지한다.
- 모든 선택 기능은 hover 없이도 사용할 수 있게 한다.

## 자료의 의미

미니어처 항만·선박·창고·패키지는 생성한 설명용 비주얼이다. 실제 PNPLINE 시설 사진·운영 수치·지리 지도·지원 시스템 증빙으로 사용하지 않는다. 확인되지 않은 주소·면적·처리량·고객 로고·인증·확정 요율·배송일·API 지원을 추가하지 않았다. 요금은 고정 숫자 대신 비용 구성으로 제시했다.

기존 프로젝트의 중문 V4와 별도로, 이번 요청의 영문과 10개 섹션 구성을 우선한 독립 컨셉이다. 기존 랜딩페이지 파일을 수정하지 않고 별도 폴더에 저장했다.

## 파일

- index.html: 전체 검토 갤러리와 세 가지 모션 스터디.
- sections/: 최종 가로형 컨셉 PNG 10장.
- sections.json: 섹션별 의도와 제안 인터랙션.
- prompts.json: 공통·섹션별·수정 생성 프롬프트.
- reference/figma-motion.json: 원본에서 읽은 모션 트랙 근거.
- reference/setby-motion.mp4: 내부 검토용으로 내려받은 원본 모션.
- reference/hero-draft.png: 초기 큰 타이포 시안, 최종 갤러리에서는 제외.

갤러리는 로컬에서 index.html을 열면 작동한다. 웹 서버, 설치, 외부 CDN이 필요하지 않다.

