# Footer 컨셉
2026-11-01

## 판단
현재Footer의 서비스/섹션/문의/개인정보 링크를 유지한다.
Explore 그룹의 How it works와 FAQ 사이에 Pricing & cost details → #pricing 링크1개를 추가한다.
정보 증가가1행이므로 새섹션이나새페이지 없이 기존Footer 안에 통합한다.
링크목록은 탐색용이므로4열 메뉴그리드를 유지하고 bento카드·추가이미지·가격설명 문단으로 확장하지 않는다.

## 원고 근거
docs/pnpline-china-source-content/pnpline-landing-mvp-copy-v4.zh-CN.md 마지막행의 费用说明 → #pricing.
기존사이트는 영어이므로 Pricing & cost details로 표현한다. 새요율표나세금상세페이지가 아니라 기존비용설명 섹션으로 이동한다.
원고는 #evidence를 쓰고 현재구현은 #warehouse를 쓴다. 이번컨셉에서는 현재정상동작하는 #warehouse를 유지하며 앵커명 변경은 별도소스작업이다.

## 보존할 항목
브랜드로고, 직영창고 설명, China→US 경로표기.
서비스4개 — Freight coordination / US warehousing / Order fulfillment / US distribution.
기존Explore4개 — Who we help / Warehouse & systems / How it works / FAQ.
Contact our team / English / Copyright / Privacy information / Back to top.
서비스링크 선택시 기존 서비스행을 선택하는 동작도 유지할 대상으로 한다.

## 스타일과 상태
White·#F4F6F7·#172126·#00ABE1, 기존타이포·1px구분선·4열구조를 이어간다.
서비스상자/탐색나침반/문의말풍선은 그룹제목에16–20px 선아이콘. 비용링크는 문서/영수증18px 아이콘. Privacy는 문서, Back to top은 위쪽화살표.
아이콘은 텍스트를보조하며 접근성이름은 실제링크텍스트를사용한다.
이미지의비용링크 시안색·밑줄은 hover/focus 상태 예시다. 항목을영구선택된현재페이지로표시할 필요는없다.
기본링크는기존본문색, hover/focus는 시안색·밑줄. 클릭/키보드로 #pricing 이동. 스크롤이동은 모션감소설정에서즉시수행.
고정헤더높이를고려한 앵커오프셋을기존섹션에 적용한다.

## 반응형과 제작 기준
1920px본문 max-width1320px/양측300px, 실제Footer높이약360–440px.
브랜드폭174px정도, 그룹제목12px, 링크16px안팎, 최소44px터치영역 확보. 생성이미지의글자크기/여백을실제CSS기준으로역산하지 않는다.
태블릿은 브랜드+메뉴를2열로 재배치하고 모바일은 브랜드전체폭후 메뉴그룹을2열 또는1열로 적층한다. 링크를숨기지 않는다.
맨아래저작권/개인정보/위로이동은 모바일에서줄바꿈하고 충분한간격을둔다.

## 산출물
footer-pricing-link.png는 정지컨셉이며 SVG아이콘은이미지에포함된표현이다.
index.html은이미지검토와 링크대응표다. links.json은새링크와보존링크의대상이다.
실제Next.jsFooter소스는수정하지 않았다.
