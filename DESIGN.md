---
name: PNPLINE 몰입형 V3
description: 흰 소개 면에서 영상으로 이어지는 중문 물류 서비스·견적 UI 시안의 코드 기반 디자인 체계.
colors:
  primary: '#00abe1'
  primary-hover: '#1db8e8'
  primary-active: '#0096c6'
  ink: '#192729'
  muted: '#536165'
  paper: '#f4f6f5'
  line: '#dce2e1'
  field-line: '#7b8b90'
  field-line-hover: '#45646c'
  focus: '#00799f'
  error: '#a33024'
  white: '#fff'
  action-ink: '#092f3b'
  placeholder: '#5e6a6e'
typography:
  display:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: clamp(44px, 3.75vw, 52px)
    fontWeight: 400
    lineHeight: 1.4
    letterSpacing: -0.008em
  display-mobile:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 30px
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: -0.008em
  headline:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 36px
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: -0.008em
  quote-headline:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 32px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: -0.008em
  service-title:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: -0.008em
  service-panel-title:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 20px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: -0.008em
  body:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.8
  body-intro:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.85
  body-detail:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.85
  label:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.6
  action:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.7
  field:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  helper:
    fontFamily: '''Noto Sans SC'', sans-serif'
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.75
rounded:
  flat: '0'
spacing:
  label-gap: 8px
  compact: 12px
  inline: 16px
  narrow-gutter: 22px
  group: 24px
  mobile-flow: 30px
  detail: 38px
  gutter: clamp(24px, 4.4vw, 72px)
components:
  button-primary:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.action-ink}'
    typography: '{typography.action}'
    rounded: '{rounded.flat}'
    padding: 11px 20px
  button-primary-hover:
    backgroundColor: '{colors.primary-hover}'
  button-primary-active:
    backgroundColor: '{colors.primary-active}'
  text-link:
    textColor: '{colors.ink}'
    rounded: '{rounded.flat}'
  navigation:
    backgroundColor: '{colors.white}'
    textColor: '{colors.ink}'
    height: 76px
    rounded: '{rounded.flat}'
  nav-quote:
    backgroundColor: '{colors.primary}'
    textColor: '{colors.action-ink}'
    padding: 9px 16px
    rounded: '{rounded.flat}'
  field:
    backgroundColor: '{colors.white}'
    textColor: '{colors.ink}'
    typography: '{typography.field}'
    height: 52px
    padding: 12px 13px
    rounded: '{rounded.flat}'
  service-tab-label:
    textColor: '{colors.ink}'
    padding: 21px 0 18px
    rounded: '{rounded.flat}'
  quote-form:
    padding: 2px 0 0
    rounded: '{rounded.flat}'
---

# Design System: PNPLINE 몰입형 V3

> 2026-11-01: 이 파일의 본문과 frontmatter는 과거 V3 구현 기록이다. 최신 전체 페이지 V5는 [PNPLINE 디자인 방향](docs/pnpline-design-direction-2026-11-01.ko.md)과 [단일 페이지 섹션 계획](docs/pnpline-single-page-section-plan-2026-11-01.ko.md)을 적용한 [로컬 구현](output/landing-reference-v5/README.md)이다. 데스크톱·모바일·페이지 모션 감소 토글의 [브라우저 검증 기록](output/landing-reference-v5/QA.md)을 참고한다. 새 이미지 대신 IMAGE 자리표시자를 사용하며 실제 문의 전송과 정식 개인정보 문안은 연결 전이다.

## Overview

**Creative North Star: "읽는 소개 면에서 확장되는 물류 장면"**

이 문서는 `output/landing-immersive-v3/`의 현재 코드와 캡처에서 확인한 UI를 기록한다. 사용자가 선택한 몰입형 방향과 Emons 참고는 유지하되, 두 번 거부된 시각 구현을 대신하는 V3 시안이다. 흰 소개 면의 제목·본문·행동을 먼저 읽고, 스크롤하면 영상이 그 공간으로 확장된다. 위 North Star는 구현을 설명하는 이름이며 새 사용자 승인을 받은 브랜드 은유가 아니다.

공식 PNPLINE 로고, 기존 청록색, 간체 중국어의 정확성은 지속되는 브랜드 기준이다. 서비스는 네 개의 큰 이미지 선택자와 한 개의 공유 설명 영역으로 연결하고, 견적은 옅은 중성 면에 별도 외곽 카드 없이 배치한다. 미니어처 이미지는 서비스 설명용 삽화다. 실제 시설·소유 자산·운영 실적의 증빙으로 취급하지 않는다.

현재 범위는 중문 V4 전체 8영역 중 히어로·서비스·견적의 3영역과 독립 개인정보 접근 경로다. 고객 유형·창고와 시스템·진행 절차·비용 설명·FAQ의 다른 5영역, 정식 개인정보 정책, 실제 폼 접수는 남아 있다. productionRelease와 wholeMvpComplete는 false이며 V3의 사용자 시각 승인은 아직 없다. 독립 마감 리뷰에서 모바일 서비스 상세 접근과 운송명 줄바꿈 2건을 수정했고, 두 수정의 확인 판정은 resolved·remaining clear·disposition ship이다. 이 판정은 두 수정 확인에 한정되며 전체 surface 재검토·운영 공개·사용자 시각 승인을 뜻하지 않는다. 사용자 지시에 따라 작업 중인 영상의 렌더 품질은 이번 디자인 평가에서 제외한다.

**History:** `output/landing-immersive-v2/`와 그 이전 비교본은 보관된 거부 시안이다. V2의 이전 마감 판정은 현재 V3 승인이나 출시 근거가 아니다. 이 파일의 현행 토큰과 규칙은 V3만 기술한다. `PRODUCT.md`의 “비교 작업 선택 전” 표현은 과거 기록의 불일치로 남아 있으며 최신 사용자 선택과 V3 surface 계약이 현재 방향을 정한다.

근거: `output/landing-immersive-v3/{index.html,style.css,script.js,privacy/index.html,assets/font.css,assets/provenance.json}`, `PRODUCT.md`, `docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md`, `.impeccable/surfaces/output-landing-immersive-v3-index-html.md`.

**Key Characteristics:**

- 흰 소개 면과 영상 영역을 공간적으로 분리하고 스크롤에 따라 영상 면을 확장한다.
- 청록색은 주 행동과 서비스 선택에, 중성 잉크는 중국어 본문과 제목에 사용한다.
- 로컬 Noto Sans SC 400 제목과 500 행동·필드 이름을 사용하고 제목 자간은 느슨하게 유지한다.
- 네 서비스는 하나의 선택 패턴을 공유하며 창고의 네 작업은 선택 영역 안에서 모두 읽힌다.
- 견적은 여섯 필드와 동의를 유지하며 명확한 필드 경계와 비전송 상태를 제공한다.

## Colors

흰색과 차가운 중성 면이 콘텐츠를 받치고 기존 청록색이 행동과 선택을 구분한다. 색상 원시값은 frontmatter가 기준이다.

### Primary

- **PNPLINE 청록 (`primary`)**: 히어로·헤더·제출 CTA와 현재 서비스의 밑줄에 사용한다. `primary-hover`와 `primary-active`는 버튼의 상태색이다.
- **집중 청록 (`focus`)**: 키보드 포커스, 입력 커서·포커스 경계, 체크박스와 서비스 문의 링크의 화살표에 사용한다.

### Neutral

- **읽기 잉크 (`ink`) / 보조 잉크 (`muted`)**: 제목·본문과 설명·도움말의 위계를 구분한다.
- **흰 면 (`white`) / 옅은 중성 면 (`paper`)**: 헤더·소개·서비스·입력의 흰색과 견적 영역의 배경을 구분한다. 견적 폼 자체에 별도 흰 카드는 없다.
- **구분선 (`line`) / 필드선 (`field-line`, `field-line-hover`)**: 서비스 선택 밑줄과 조작 가능한 입력 경계의 역할을 나눈다. 필드선은 현재 CSS에서 사용되는 어두운 경계색으로, 실제 입력 윤곽을 위한 값이다.
- **행동 잉크 (`action-ink`) / 자리표시자 (`placeholder`)**: 청록 CTA의 글자와 입력 힌트의 읽기 대비를 지원한다.
- **오류 (`error`)**: 잘못된 이메일의 경계와 안내에만 쓰는 의미 색이다.

**The Retained Identity Rule.** 공식 PNPLINE 로고와 기존 청록색을 유지한다. 참고 사이트의 자산·빨강·상업적 주장은 복제하지 않는다.

## Typography

**Display Font:** Noto Sans SC, sans-serif fallback.  
**Body Font:** Noto Sans SC, sans-serif fallback.

제목은 보통 굵기, 행동·필드 이름·창고 작업명은 중간 굵기로 읽힌다. 로컬 400·500·600·700 파일을 포함하지만 이 화면의 실제 스타일은 400·500을 사용한다. `font-display: swap`, `font-synthesis: none`과 OFL 라이선스를 유지한다. 중국어 V4 글자 subset이므로 문구를 추가할 때 글리프 포함 여부를 확인한다.

### Hierarchy

- **Display (`display`)**: 데스크톱 히어로 제목. 1190px 이하에서 44px, 1000px 이하 36px, 760px 이하 `clamp(30px, 5.5vw, 38px)`/1.45, 480px 이하 `display-mobile`, 360px 이하 27px가 적용된다. 각 span은 별도 줄이며 V2의 `white-space: nowrap` 제약은 없다.
- **Headline (`headline`)**: 서비스 제목. 1000px 이하 32px, 760px 이하 29px/1.5, 360px 이하 27px다.
- **Quote headline (`quote-headline`)**: 견적 제목. 1190px 이하 30px, 1000px 이하 27px, 760px 이하 29px, 360px 이하 27px의 cascade다.
- **Service title (`service-title`)**: 서비스 선택자 제목의 기본값. 1190px 이하 17px, 1000px 이하 16px, 480px 이하 15px, 360px 이하 14px로 바뀐다. 버튼 자체의 자간은 상위 h3에서 상속된다.
- **Body (`body`, `body-intro`, `body-detail`)**: 기본 본문, 히어로 소개, 선택 서비스 설명이다. 상세 설명은 760px 이하 16px/1.9다. 창고 작업 설명은 기본 15px/1.85, 760px 이하 14px, 480px 이하 다시 15px다. 기본 문단은 최대 72ch지만 개별 영역의 좁은 제한이 우선한다.
- **Label / Action / Field / Helper**: 필드 이름, 주 버튼, 입력, 도움말이다. 입력은 모든 화면에서 16px을 유지한다. 동의·상태·제출 보조문은 13px이며 행간은 각각 1.9·1.8·1.8이다.
- **모바일 서비스 상세 제목 (`service-panel-title`)**: 선택된 기존 서비스명을 20px/400/1.5와 제목 공통 자간으로 표시한다. 제목 아래 14px을 두고 데스크톱에서는 숨긴다.
- **기타**: 히어로 서명은 14px/0.02em에서 760px 이하 12px, 480px 이하 자간 0으로 바뀐다. 개인정보 경로의 제목은 40px이다.

**The Readable Chinese Rule.** 중국어 제목은 Noto Sans SC 400과 현재의 완만한 자간을 사용한다. 제목의 크기와 본문·행동의 간격으로 위계를 만든다.

## Layout

본문은 최대 1360px의 유동 컨테이너다. 양쪽 여백은 `spacing.gutter`, 760px 이하 24px, 480px 이하 22px, 360px 이하 18px이다. 견적 컨테이너는 최대 1120px이며 760px 이하 최대 680px다.

| 영역 | 데스크톱 | 760px 이하와 좁은 화면 |
| --- | --- | --- |
| 헤더 | 화면 상단 전체 폭의 흰 면, 높이 76px | 높이 64px; 480px 이하 서비스 링크 숨김, 견적 유지 |
| 히어로 | 여정 340svh, sticky 면 100svh·최소 650px | 여정 320svh, 최소 740px; 360px 이하 최소 760px |
| 흰 소개 면 | 제목 왼쪽·본문/행동 오른쪽, 1.03:1 열; 간격 `clamp(40px, 5vw, 80px)` | 제목·서명·본문·행동의 세로 흐름; 영상은 소개 아래 |
| 서비스 소개 | 1:0.88 열·간격 100px·아래 48px | 단일 흐름·아래 30px |
| 서비스 선택 | 4열·간격 24px, 큰 이미지 아래 서비스명·선택 밑줄 | 2×2, 480px 이하 열 간격 16px·행 간격 20px |
| 창고 설명 | 소개:작업 0.82:1.7, 간격 74px; 네 작업 2열 | 소개 아래 작업 2열, 480px 이하 한 열로 네 작업 전체 표시 |
| 견적 | 소개 300px + 최대 680px 폼, 간격 70px; 필드 2열 | 760px 이하 소개와 폼 쌓기; 480px 이하 필드 한 열 |

서비스는 상하 100px/76px, 견적은 100px/82px이다. 760px 이하에서는 각각 88px/54px와 88px/52px다. 필드 간격은 기본 행 22px·열 24px, 760px 이하 21px/20px, 480px 이하 20px다. 중간 화면에서는 1190px와 1000px 분기점에서 열 폭·간격·제목 크기를 조정한다.

히어로의 최초 소개 높이는 콘텐츠 실측값으로 갱신된다. CSS의 360px·모바일 500px는 스크립트 측정 전 초기값이며 고정 최종 높이가 아니다. 여정의 앞 18%에서 소개가 위로 이동하며 사라지고 영상의 위쪽 경계가 0으로 확장된다. 320×568에서는 최소 높이 때문에 일부 내용이 첫 viewport 아래로 이어진다. 고정 헤더의 견적 경로는 유지된다.

내부 앵커는 즉시 section 시작점으로 이동한다. `scroll-padding-top`과 `scroll-margin-top`은 모두 0이며 각 section의 위쪽 여백으로 헤더와 내용을 분리한다. 개인정보 본문은 최대 800px, 안쪽 `140px 30px 80px`다.

## Elevation & Depth

현재 V3는 그림자·반투명 정보 패널·그라디언트 scrim 없이 흰색과 옅은 중성 면, 이미지 면적, 얇은 선으로 깊이를 표현한다. 헤더 역시 그림자 없는 흰 면이다. 서비스 선택은 채움색 대신 청록 밑줄로 표시한다. 흰 입력 필드는 옅은 견적 배경 위에서 개별 경계선으로 구분된다.

**The Open Surface Rule.** 현재 시안의 깊이는 흰색과 중성 면, 이미지 크기, 구분선으로 표현한다. 큰 반투명 소개 패널과 견적 외곽 카드를 다시 추가하지 않는다.

스크롤 연결 변환과 포커스 outline의 정확한 값은 sidecar `extensions`에 기록한다. 스타일에는 일반 상태용 transition이나 CSS animation이 선언되어 있지 않다.

## Shapes

버튼·입력·영상·선택 이미지·헤더는 각진 사각형이다. 버튼과 입력은 명시적으로 `border-radius: 0`이며, 별도 카드나 pill을 추가하지 않는다. 체크박스는 브라우저 기본 형태에 집중 청록 accent를 사용한다.

inline SVG는 기본 22px, stroke 1.5와 둥근 linecap·linejoin을 사용한다. 헤더 행동은 18px, select의 배경 화살표는 20px다. 서비스 선택자에는 chevron이나 SVG가 없고 선택 상태는 밑줄과 ARIA로 표시한다.

## Components

### Buttons

주 행동은 청록 면·짙은 글자·우측 화살표다. frontmatter의 `button-primary`를 기준으로 최소 높이 48px, 글자와 화살표 간격 24px이다. hover·active는 대응 청록 상태색으로만 변한다. disabled CSS는 회색 청록 배경·짙은 회색 글자와 기본 커서이며 현재 폼에서는 사용하지 않는다.

헤더 행동은 최소 42px, 760px 이하 40px다. 모바일 히어로 행동은 최소 44px·13px·안쪽 `9px 16px`이며 360px 이하 좌우 13px다. 제출 행동은 최소 50px·좌우 22px·아이콘 간격 33px다. 일반 버튼까지 52px 높이라고 확대 기록하지 않는다. 텍스트 링크는 최소 44px·14px/500/1.6, hover 밑줄이다.

전역 포커스는 3px 집중 청록 outline·5px offset이다. 서비스 탭은 offset 7px, 공유 panel은 14px다. 변환이나 hover 이동을 추가하지 않는다.

### Inputs / Fields

input·select는 52px 높이, 16px 글자, 흰 면·전체 경계선·각진 모서리다. label 아래 8px, 내부 `12px 13px`를 사용한다. select는 오른쪽 여백 38px와 내장 SVG 화살표가 있다. hover에서 필드선을 진하게, focus에서 집중 청록 경계와 2px outline·2px offset으로 바꾼다. 체크박스는 18px다.

필드는 제품 종류·운송 방식·월 물량·목적지·IOR 필요 여부·이메일 순서이며 별도 동의를 둔다. 미정·불명 옵션을 보존한다. 비어 있지 않은 잘못된 이메일만 오류 문구·`aria-invalid`를 표시하고 submit 시 포커스를 옮긴다. 필수값·동의 강제 등 운영 검증은 확정된 규칙으로 기록하지 않는다.

폼에는 큰 외곽 카드·자체 배경·외곽 padding이 없으며 실제 padding은 상단 2px뿐이다. `method="dialog"`, `novalidate`, submit `preventDefault()`로 외부 전송을 막는다. `role="status"`/`aria-live="polite"`는 “设计预览：信息未发送。”를 유지한다. 별도 `privacy/`는 정식 정책이 아닌 중문 검토용 안내다.

### Navigation

공식 로고는 기본 폭 144px, 760px 이하 124px, 360px 이하 108px다. 서비스는 텍스트 링크, 견적은 청록 버튼이다. 헤더는 화면 위·좌·우에 붙으며 V2의 inset 형태를 계승하지 않는다. 서비스 링크는 480px 이하에서만 숨긴다.

skip link는 키보드 포커스 시 나타난다. 내부 앵커는 즉시 이동하고 `tabindex="-1"`이 있는 서비스·견적 영역으로 포커스를 옮긴다. 영상 끝을 거치지 않아도 이 경로로 견적과 서비스에 접근한다.

### Service Selection

네 서비스는 한 `tablist`와 공유 `tabpanel`을 사용한다. 선택 탭만 `tabindex="0"`이며 `aria-selected`, 본문 `hidden`, panel `aria-labelledby`가 함께 바뀐다. 창고가 기본 선택이고 창고의 네 작업은 `dl`로 모두 보인다. V2의 `details/summary`는 현재 구현에 없다.

좌우 화살표는 하나씩 이동하고, 상하 화살표는 데스크톱에서 하나씩·760px 이하 2×2 배치에서 두 칸씩 이동한다. Home·End는 처음·마지막 서비스로 이동한다. tablist의 `aria-orientation`은 현재 horizontal이다. 모바일을 단일 세로 탭이라고 기록하지 않는다.

760px 이하에서 탭을 클릭하거나 Enter·Space로 활성화하면 공유 panel로 즉시 스크롤하고 `focus({ preventScroll: true })`를 적용한다. panel의 `scroll-margin-top`은 헤더 높이 + 24px이며 선택된 기존 서비스명을 제목으로 표시한다. 화살표·Home·End 탐색은 탭 선택과 포커스만 갱신하고 강제 스크롤하지 않는다. 운송 서비스명은 모바일에서 “中国出货” / “与美国境内运输”의 두 의미 단위로 줄을 나누며, 데스크톱은 원문을 이어서 표시한다. 글자 내용은 바꾸지 않는다.

이미지 높이는 기본 `clamp(194px, 18.7vw, 270px)`, 1000px 이하 186px, 760px 이하 `clamp(142px, 37vw, 236px)`, 480px 이하 151px, 360px 이하 132px다. 창고는 contain, 나머지는 cover와 원본 이미지의 CSS 확대·crop을 쓴다. 선택은 2px 밑줄, label 안쪽은 기본 위 21px·아래 18px, 모바일 위 14px·아래 12px다.

### Scroll-linked Hero

영상 파일은 V2와 byte 동일한 33초 작업본이다. 스크롤 진행률은 여정 높이에서 sticky 높이를 뺀 실제 거리로 계산하며 `currentTime = progress × (duration − 0.001)`에 선형 대응한다. 현재 0~32.999초를 앞뒤로 탐색하고 멈추면 그 시점에 머문다. intro 레이아웃의 18% 확장은 영상 시간 매핑을 바꾸지 않는다.

소개 이동·불투명도는 `introProgress = min(1, progress / 0.18)`에 선형 대응한다. `introProgress >= 0.97`에서 `inert`를 적용해 화면 밖·헤더 아래 CTA에 포커스가 가지 않게 하고, 역방향에서 이 기준 아래로 내려가면 복원한다. 완전 소멸은 1.0이며 inert 적용 시점과 구분한다.

갱신은 requestAnimationFrame으로 묶고 seek 중에는 대기한 뒤 seeked에서 최신 목표를 적용한다. 영상은 paused 상태를 유지하며 autoplay·loop·재생 버튼을 제공하지 않는다. 모션 감소와 영상 error에서는 긴 여정과 sticky를 해제하고 poster·소개·행동을 정상 문서 흐름으로 제공한다. poster는 작업 영상 3.5초 프레임이며 0초 영상과 동일한 프레임이라는 주장은 하지 않는다.

사용자 영상은 제작 중이다. 이번 평가에서는 렌더 품질을 제외하고 스크롤과 시간 대응·paused 상태·주변 UI만 확인한다. 모션 감소와 media error는 QA에서 source 경로 확인이며 실제 OS 설정 변경·실패 주입 검증으로 확대하지 않는다.

### Asset Provenance and Review Evidence

공식 로고는 `resources/logo/PNP-LINE.webp`에서 변경 없이 사용한다. `hero-scrub.mp4`는 원본 33초 sequence의 H.264 g6/faststart 파생본이며 이번 V3에서 재인코딩하지 않았다. `hero-poster.jpg`와 로고 역시 기존 자산을 그대로 복사했다.

`warehouse-miniature.png`와 `port-miniature.png`는 각각 1448×1086의 생성 미니어처 삽화다. 창고는 기존 생성본을 재사용하고 항만은 새로 생성했다. 네 서비스는 이 두 원본의 전체 모습과 crop으로 표현한다. exact prompt는 자산 폴더의 `.prompt.txt`와 PNG metadata에, 출처·변환·SHA-256은 `assets/provenance.json`에 기록한다. QA의 자산 scan은 raster 4개·출처 누락 0개다.

문서화 과정에서 `.impeccable/review/immersive-v3/`의 desktop/mobile hero·services·quote와 `user-hero.jpg` 7개 캡처를 직접 열어 확인했다. 수정 후 `mobile-services.jpg`를 다시 확인하고 `mobile-detail.jpg`, `mobile-320-services.jpg`, `mobile-detail-second-row.jpg` 3개 추가 캡처에서 의미 단위 줄바꿈과 상세 접근 상태를 확인했다. QA 보고 viewport는 1440×900, 390×844, 320×568, 1280×720이다. 스크롤바를 제외한 캡처 폭은 각각 1430·380·1270이다. 문서화 담당은 브라우저·검출기를 추가 실행하지 않았다.

`qa.md`는 순·역방향 paused seek, intro inert와 복원, 2×2 탭 키보드, 작은 화면 overflow, 이메일 오류와 비전송을 기록한다. 마감 리뷰의 모바일 수정 2건은 원고를 바꾸지 않는 운송명 줄바꿈과 활성화 후 상세 이동·포커스로 구현했으며, 첫째·둘째 행 서비스에서 선택 제목·본문이 보이고 320px에서 수평 넘침이 없음을 QA가 확인했다. `finish-review.md`의 두 material fix는 `final-verdict.md`에서 모두 resolved로 확인됐고, 제공된 재캡처·변경 source에서 해당 수정의 새로운 회귀는 발견되지 않았다. `final-detector.json`에는 padding warning 5건과 field-line color advisory 1건이 있다. 독립 리뷰는 실제 label의 하단 여백·quote 내부 wrap과 section 여백을 근거로 padding 경고를 시각 실패로 채택하지 않았다. 색상 advisory는 V3 필드선과 교체 전 V2 문서의 차이였으며 현재 토큰은 실제 source·캡처에 맞춰 기록했다. 검출기를 재실행한 것은 아니다. 최종 disposition은 ship이며, 모바일 수정 2건의 해결 확인에만 적용된다. 전체 surface를 새로 전면 검토했다거나 운영 공개를 승인했다는 뜻은 아니다. 영상 품질은 이 판정에서도 제외했다.

**Not canonized:** 영상 품질·최종 영상 선정, 실제 접수·필수값·동의 강제·정식 정책, 사용자 시각 승인, 누락된 5영역의 완성, 낡은 PRODUCT 선택 전 문구, 자동 검출기 재실행이나 전체 surface 재검토를 수행했다는 주장을 현행 디자인 규칙으로 만들지 않았다.

## Do's and Don'ts

### Do:

- **Do** 공식 로고·청록색·로컬 Noto Sans SC와 정확한 간체 중국어 원고를 유지한다.
- **Do** 소개 문구와 영상의 공간 분리, 네 서비스의 동일한 선택 방식, 견적의 명확한 필드 경계를 보존한다.
- **Do** 키보드 포커스, 선택 상태, 역방향 스크롤 복원, 모션 감소와 미디어 실패 경로를 유지한다.
- **Do** 최종 CSS cascade와 실제 캡처를 근거로 토큰·반응형·상태 문서를 갱신한다.
- **Do** 작업 영상과 생성 미니어처의 출처, 검토 시안 범위와 실제 운영 범위를 구분한다.

### Don't:

- **Don't** 거부된 V2의 반투명 히어로 패널·좁은 제목 자간·창고 펼침과 별도 3탭·큰 흰 견적 카드를 현재 규칙으로 복원한다.
- **Don't** 사용자 작업 중인 영상의 렌더 품질을 이번 UI 개선의 평가·완료 근거로 삼는다.
- **Don't** 미니어처 삽화를 실제 PNPLINE 시설 사진이나 검증된 운영 증거로 표현한다.
- **Don't** 삭제된 스크롤 안내·콘셉트 표식·S1~S7 장면 해설표를 공개 원고에 다시 넣는다.
- **Don't** 비전송 시안을 실제 문의 접수로, 검토용 개인정보 안내를 정식 정책으로, 3영역 시안을 전체 MVP 완성으로 표현한다.
