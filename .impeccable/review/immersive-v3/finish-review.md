disposition: fix

미제공: 별도 QUALITY BAR 카드. 사용자 지정 Emons 캡처를 공간·타입·서비스 표현의 참고 근거로만 사용했다. 승인 comp·comp-diff·build phase는 사용자 pin/code-first 경로이므로 비적용이다.

## persistence

pass — PRODUCT.md, V3 surface contract, Chinese V4 원고, roll.json, 최종 HTML/CSS/JS, privacy 경로, provenance, qa.md와 기존 detector 결과를 읽었다. FORM의 `seed:91ef21903eaa9b05`는 제공된 roll.json과 일치한다. DESIGN.md/design.json의 V2 상태는 이번 시각 수정 뒤 문서 교체가 예정된 상태이며, 이를 시각 실패로 판정하지 않는다.

제공된 V3 캡처 10개(desktop hero/expanded/services/quote, mobile hero/services/detail/quote/quote-end, user hero)와 Emons 캡처 3개를 모두 직접 열었다. V3 이미지들은 이름에 해당하는 화면 내용을 보여 준다. mobile-detail은 상세 영역 중간의 캡처이며 문서 시작점 캡처로 해석하지 않았다. 사용자 폭 1280과 데스크톱·모바일의 첫 화면을 함께 확인했다.

판정 범위는 hero/services/quote 세 영역의 디자인 시안이다. 전체 V4 8영역 완성본, 실제 문의 접수 또는 운영 공개의 승인이 아니다. 영상의 렌더 품질·해상도·모델 정교함은 어느 판정에도 사용하지 않았다. 별도 detector는 실행하지 않았다.

## fidelity

| 대상 | 판정 | 직접 확인한 근거 |
| --- | --- | --- |
| THESIS / 첫 화면 읽기 순서 | match | 1440·1280에서 흰 intro의 제목/본문 2열과 하단 전폭 영상이 명료하게 분리된다. 모바일에서도 본문이 영상 위를 덮지 않는다. |
| TYPE | contradicted, 국소 | 제목·본문의 Noto Sans SC 400과 완만한 자간은 계약에 맞지만, mobile-services의 긴 운송 서비스명이 마지막 `输` 한 글자만 다음 줄에 남긴다. 주 탐색 제목의 의도적인 조판이 완료되지 않았다. |
| MATERIAL | match | 서비스에는 실제 PNG 일러스트가 보이며 CSS로 물성을 흉내 내지 않는다. 두 miniature의 서로 다른 crop을 사용한다. provenance는 개념 일러스트임을 기록하고 HTML은 실제 시설 증빙으로 주장하지 않는다. 영상 자체의 물성 완성도는 평가 제외다. |
| GROUND | match | 흰 첫 화면과 서비스 영역, 절제된 연한 중성색 견적 배경, 공식 cyan 액션이 OWN-WORLD를 유지한다. |
| STORY / 서비스 내용 | match | 네 서비스 제목과 공유 panel, 창고 작업 네 항목이 존재한다. desktop-services와 mobile-detail에서 창고 세부 설명이 모두 읽힌다. |
| 서비스 선택의 시각적 연결 | contradicted | mobile-services에서 첫 행 선택선과 공유 설명 사이에 두 번째 이미지 행 전체가 끼어 있다. 설명은 화면 아래에 있고 선택 반응은 얇은 밑줄뿐이다. script의 클릭 처리도 panel 내용을 교체할 뿐, 결과를 방문자의 시야에 연결하지 않는다. 접근성 속성과 키보드 동작이 있다는 사실만으로 이 시각적 단절이 해소되지는 않는다. |
| FIRST VIEWPORT / 확장 동작 | match, 증거 범위 명시 | expanded 캡처에서 intro가 사라지고 미디어가 헤더 아래로 확장된 모습을 확인했다. 선형 시간 대응·일시정지·inert는 제공된 QA 수치와 source로 확인했으며, 정지 이미지로 연속 동작을 직접 검증했다고 주장하지 않는다. |
| FORM / 견적 | match | desktop-quote의 좁아진 2열 폼과 mobile-quote/end의 1열 폼은 외부 흰 카드 없이 정리된다. 52px 입력 경계, 여섯 필드, 동의, 비전송 문구, 독립 privacy 링크가 유지된다. |
| Truth / scope | match | 검토한 세 영역에서 새 수치·자격·배송일·회신시간·시스템 지원 확약을 발견하지 않았다. 공식 로고와 V4 문구를 유지하며 privacy는 명시적인 디자인 preview다. |

Emons는 승인 comp가 아니므로 그 화면과의 일대일 재현 여부를 평가하지 않았다. 그 참고 화면이 보여 주는 선명한 서비스 선택 상태와 매체·정보 사이의 위계는 현재 모바일 selector보다 명확하다.

## ceiling

Hero의 흰 intro와 영상 경계, 제목 크기, 견적의 밀도는 계약에 맞는 분명한 구도를 형성한다. 남은 마감 격차는 서비스 탐색에 집중된다. 큰 이미지 타일을 쓴 만큼 선택 상태와 그 결과도 시각적으로 확실해야 하는데, 현재 모바일에서는 이미지 두 행이 그 관계를 끊는다. 긴 서비스명의 고립된 마지막 글자도 같은 영역의 완성도를 떨어뜨린다. 별도 카드가 제공되지 않아 가상의 세계 기준을 추가하지 않았다.

기존 detector의 cramped-padding 5건은 그대로 시각 실패로 채택하지 않는다. 네 label은 실제 캡처와 CSS에서 하단 여백을 두고 있고, quote의 배경도 내부 wrap과 section padding을 통해 내용과 떨어져 있다. 색상 advisory는 새 input 경계색 `#7b8b90`와 교체 전 V2 문서의 불일치이며, 화면의 경계를 약화시킬 이유가 아니다. 검토 캡처에서 금지된 eyebrow·가짜 재질·장식적 side stripe·glyph icon은 발견하지 않았다.

## material_fixes

1. **STORY / 서비스 선택:** 모바일에서 탭을 활성화했을 때 현재 선택과 공유 상세 결과를 같은 읽기 흐름 안에 드러내라. 두 행 뒤에 결과를 조용히 바꾸는 상태를 해소하고, 색상 2px 밑줄만으로 선택을 알리지 말라. 네 항목의 한 가지 선택 패턴과 원고는 보존하고, 첫 행·둘째 행 선택 모두에서 결과의 위치와 선택 대상을 분명히 확인할 수 있어야 한다.
2. **TYPE / 서비스명 조판:** mobile-services의 `中国出货与美国境内运输`를 의미 단위로 균형 있게 줄바꿈하여 `输` 한 글자 줄을 제거하라. 원고를 줄이거나 글자를 과도하게 축소하지 말고 390px와 320px에서 확인하라.

## keep

흰 intro와 영상의 공간 분리, 공식 로고/cyan/Noto 400, 기존 33초 영상과 선형 scroll 대응, 네 서비스와 창고 네 하위 작업, 52px 입력 경계와 간결한 견적 배치, V4 원고·동의·비전송·privacy preview를 유지한다.
