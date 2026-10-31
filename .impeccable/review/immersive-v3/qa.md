# V3 UI 검증

Scope: hero/services/quote 디자인 시안. 사용자의 최신 지시대로 영상 품질은 평가하지 않았다. 영상·poster 파일은 구현 담당이 V2와 byte 동일함을 확인했다. 이 기록의 영상 검증은 scroll/time 동작만 다룬다.

## 실제 브라우저

- 1440×900: 첫 화면의 흰 intro/영상 분리, 스크롤 y540에서 currentTime 8.24975(계산값 동일), paused true, 영상 top0으로 확장, intro inert 속성 존재. y180으로 역방향 이동 시 2.749916초로 복귀. 시작점으로 돌아오면 intro 표시와 서비스/견적 CTA 접근이 복원됨.
- 390×844: 네 서비스가 2×2로 배치됨. ArrowDown으로 창고→IOR, End로 inventory, Home으로 warehouse 선택; 공유 panel의 aria-labelledby도 선택과 일치함.
- 320×568: clientWidth310/scrollWidth310, 제목·input·select·button 경계의 수평 초과 0. 작은 높이에서는 hero 최소 높이 때문에 일부 내용이 viewport 아래로 이어진다.
- 이메일 invalid 입력/submit: aria-invalid true와 원고 오류 표시, 비전송 preview 상태 확인. 유효값/동의의 운영 필수 정책은 확정하지 않는다.
- anchor 중복 offset(scroll-padding+scroll-margin)을 한 배치 수정 후 desktop services top0 확인. mobile section 자체 top padding은 header+24px으로 확보.
- 혼동을 주는 서비스 탭 chevron 4개 제거 후 DOM SVG 개수0 확인. 선택 밑줄 보존.
- 최종 native viewport 캡처: desktop-hero/services/quote/expanded.jpg, mobile-hero/services/detail/quote/quote-end.jpg, user-hero.jpg. 사용자 viewport1280×720. 파일들을 직접 열어 구도·내용을 확인했다. 브라우저가 scrollbar를 제외하고 저장하여 JPEG 폭은 각각1430/380/1270이다.
- reduced-motion과 media failure는 source/CSS 경로 확인이며 OS preference 변경이나 실패 주입을 수행하지 않았다.

## 정적·자동 근거

구현 담당: 원고19항목 누락0, 서명/견적마무리 보존, 6필드+동의 순서일치, 중복ID0, anchor/aria-controls/HTML CSS참조asset누락0, node --check 통과. 원본영상교체/재인코딩/프레임수정없음.

V3 final-detector.json은 이 후보 HTML에 1회 실행했다. cramped-padding5, design-system-color1. wrapper/image선택버튼의테두리와실제문자padding을캡처로분별해야한다. 상세항목은원본JSON에있다. A/B critique detector는V2를평가한별도실행이다.

asset provenance scan: 4 rasters, 0 missing. 새항만PNG는네이티브imagegen 신규생성, exactprompt내장. 창고PNG/로고/poster는기존출처메타데이터를유지했다.

## 제외·남은 제품 범위

영상 렌더 품질을 근거로 디자인 점수나 완료 여부를 판단하지 않는다. 최신 사용자 지시가 A의 이전영상관련평가에우선한다. 다른5개V4콘텐츠영역,정식privacy정책,실제문의접수는이번3영역UI개선의완료범위가아니다.

## 독립 검토 수정 확인

finish-review.md의 fix2건에 따라 mobile 활성화 시 상세로 이동·focus하고 선택 서비스 제목을 표시했다. 390px에서 첫 행 운송을 click한 결과 focus=service-detail, header top0/bottom64, panel top87.708로 제목·본문이 바로 보였다. 둘째 행 IOR를 Enter로 활성화했을 때도 같은 panel 위치와 focus, 선택 상태가 확인됐다. mobile-detail.jpg 및 mobile-detail-second-row.jpg에 두 경우를 저장했다. 이전 상세 캡처의 헤더 잘림은 새 파일에서 재현되지 않았으며, 당시 원인은 단정하지 않는다.

mobile-services.jpg와 새 mobile-320-services.jpg에서 운송 제목을 中国出货 / 与美国境内运输 두 의미 단위로 재캡처했다. 320px에서 두 줄 각각 높이21px이며 전체 원문 동일, clientWidth310/scrollWidth310이었다. detector는 재실행하지 않았다. 영상 파일과 time mapping은 이 수정에서 변경하지 않았다.
