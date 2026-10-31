# 몰입형 V2 검증 기록

대상: `output/landing-immersive-v2/`, 로컬 `http://127.0.0.1:7320/`.
주 구현 담당은 `gpt-6-astra`, `reasoning_effort: ultra`로 실행했다. 사용자 UI 모델 선택값 자체는 이 기록의 검증 대상이 아니다.

## 실제 브라우저 검증

- 데스크톱 1440×900, 모바일 390×844, 좁은 화면 320×568, 실제 사용자 viewport 1280×720에서 확인했다. 브라우저 세로 스크롤바 때문에 일부 JPEG 캡처 폭은 10px 작다.
- 데스크톱 영상 duration 33초, 시작 currentTime 0. 스크롤 y=900에서 기대 13.749583초/실제 13.749583초, y=450으로 되돌리면 6.874791초. 각 표본에서 paused=true. 견적 앵커 도착 후 32.999초.
- 모바일 320×568: y=568에서 기대 17.070520947초/실제 17.07052초, paused=true. 분모는 실제 journey 높이에서 pin 높이를 뺀 값이다.
- 모바일 320px의 document clientWidth=310/scrollWidth=310. 주요 제목·입력·버튼·header의 수평 경계 초과가 없었다. 이 작은 높이에서는 hero 최소 높이가 720px이며 설명/하단 CTA는 첫 viewport 아래로 이어지고 상단 견적 링크는 접근 가능하다.
- 서비스 details는 Enter로 펼쳐졌고, 탭은 ArrowRight → IOR, End → 재고, Home → 운송으로 선택이 바뀌었다.
- invalid-email 입력 후 원고 오류 문구와 aria-invalid=true, 정상 이메일 입력 후 aria-invalid=false를 확인했다. 제출 상태는 “设计预览：信息未发送。”이다. 외부 전송 API는 없고 form method=dialog + submit preventDefault이다.
- 개인정보 별도 경로 이동 및 로고 복귀를 확인했다. 개인정보 본문은 정식 정책을 대체하지 않는 중문 디자인 검토 안내다.
- 앵커 위에 이전 섹션 조각이 노출되던 문제를 한 배치로 수정했다. 확인: desktop services top=0/h2 top112/header bottom76, mobile quote top≈0/h2 top90/header bottom66.
- reduced-motion 및 video error는 소스/CSS 경로를 확인했다. 실제 OS 모션 설정 변경·미디어 요청 강제 실패 테스트는 수행하지 않았다.

## 캡처

`desktop-hero.jpg`, `desktop-hero-mid.jpg`, `desktop-services.jpg`, `desktop-service-explorer.jpg`, `desktop-quote.jpg`, `mobile-hero.jpg`, `mobile-services.jpg`, `mobile-service-explorer.jpg`, `mobile-quote.jpg`, `mobile-privacy.jpg`, `mobile-320-hero.jpg`, `user-width-hero.jpg`는 각 화면의 viewport 캡처다.

`desktop-full.jpg`/`mobile-full.jpg`는 문서 맨 위에서 찍었다. 이 도구의 full-page 렌더는 sticky hero의 스크롤 거리를 흰 여백으로 표시한다. 실제 스크롤에서는 그 구간 전체에 sticky 영상이 유지된다. 따라서 레이아웃 평가는 viewport 캡처와 함께 해야 한다. full-page 직후 잘못 축소된 모바일 2개 파일은 원래 viewport로 재설정하여 교체하고 직접 확인했다.

## 정적 확인과 제한

구현 담당의 확인: JS/Python 구문 통과, 19개 V4 관련 문구 보존, 견적 6필드+동의, 중복 ID 0, 참조 에셋 누락 0. 주요 3영역 시안이며 운영 게시본이 아니다. 원본 영상과 세 서비스 스틸은 작업본이며 새 창고 이미지는 생성된 미니어처다. 실제 시설 증빙으로 표시하지 않는다.

detector는 변경 HTML에 한 번 실행했다. `detector.json`: low-contrast 2, cramped-padding 2, design-system-font 2, design-system-color 9. 색상/서체는 이전 A/B DESIGN.md와의 비교이며 새 방향 문서로 갱신 예정이다. padding 항목은 전체 배경용 hero-pin/quote wrapper이다. 모바일 white hero copy 대비 항목은 이미지 위 scrim을 반영하지 않은 `#c4c4c4` 조상 배경 계산이다. 소스의 실제 scrim은 56%에서 #142028a6, 100%에서 #142028eb이며 캡처를 함께 검토한다. 독립 검토자의 판단을 대체하지 않는다.

에셋 provenance scan 최종 결과: 7 rasters, 0 missing. 생성 창고는 정확한 프롬프트를 PNG에 내장했고, 기존 WebP는 원본·추출 시점·작업 설명을 sidecar에 저장했다.

## 독립 리뷰 후 단일 수정

`finish-review.md`는 disposition fix, 서비스 탭의 하향 chevron 제거 1건을 요구했다. 세 탭의 SVG와 미사용 스타일 2개를 제거하고 동일 `desktop-service-explorer.jpg`/`mobile-service-explorer.jpg`를 재캡처했다. 실제 DOM의 `.service-tab svg`는 0개이고 선택 배경과 공용 패널은 유지됐다. `final-verdict.md`는 해당 수정 resolved, 회귀 없음, remaining clear, disposition ship이다. 이는 지적한 수정 1건의 검토 범위이다. 전체 문서 캡처는 이 작은 수정 전의 보조 자료이며 최종 탭 표시 근거는 재캡처한 두 파일이다. detector는 추가 실행하지 않았다.

전체 중문 V4의 8개 영역 중 현재 화면에는 journey/services/quote 3개만 구현되어 있다. customers/evidence/process/pricing/faq 5개는 원고에 보존된 후속 구현 범위이며 전체 MVP 구현 완료로 보고하지 않는다.
