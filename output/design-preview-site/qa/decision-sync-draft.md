# #61 의사결정 정합성 수정 초안 — 미게시

이 파일은 검토 초안이다. GitHub 본문·댓글을 변경하지 않았다.

## 근거

- 현재 HEAD와 지시서 기준 HEAD는 동일한 `89f99568d3216814d1b57334bf467a3fdca8ddca`이다.
- #61 본문 및 결정 댓글 `5662675845`는 작은 표식·대형 로고 금지·블루 제한을 유지하고 있었다. 이슈 갱신 시각은 2026-09-14T10:42:35Z이다.
- 이번 실행 입력 `D61-ART-BRAND-20260914`는 브랜드 강조형 미니어처와 공식 원본 로고를 지정한다. 이 변경은 GitHub에 이미 반영됐다는 뜻이 아니다.

## 제안 본문 교체 문구

Brand signal: retain the official PNPLINE blue #00ABE1 on the physical route and selected brand panels, containers and vehicles. Do not tint the whole environment or compete with the core logistics process and UI copy.

Branding: use the user-designated REF-LOGO-01 original wordmark with preserved alpha, proportions, shape and colors. A prominent primary mark on a natural logistics surface is allowed. Composite the original after generating blank surfaces; never generate replacement brand lettering. Avoid repetitive branding and any obstruction of process or copy.

References: REF-STYLE-01 guides layered industrial space, material and brand-surface emphasis only. Its green paint, double-diagonal symbol, alternate wordmark and specific layout are excluded. User-provided source use is limited to local review until redistribution rights are confirmed.

## 변경표

| 이전 규칙 | 이번 변경 | 이유·적용 범위 |
|---|---|---|
| 소형 표식만, 대형 로고 금지 | 대표 공정 객체에서 공식 로고를 읽을 수 있는 주 표면 허용 | 사용자가 지정한 브랜드 강조형 #61 정지 콘셉트 |
| 블루는 경로·절제된 강조 | 선별한 컨테이너·차량·브랜드 면까지 허용 | 공간에서 브랜드 인지 확보. 배경 전체 틴팅 금지 유지 |
| 브랜드 일반 금지의 모호한 표현 | 비공식·변형·제3자 로고를 금지하고 제공된 공식 로고 후합성 허용 | 원본 보존과 공정 가독성 동시 확보 |

밝은 낮, 6장면 순서, 독립 모바일, 전진·가림, 정적 대체, 운영 사실 구분은 유지한다. 디자인 토큰·성공 상태 녹색은 변경하지 않는다. #24의 2장면 실제 영상 파일럿, #62의 실측 기반 규격, #42의 홈 구현은 후속 범위다.

관련 문서의 이전 '대표 1장면 시험'은 사전 시험이며 #24 전체의 2장면 파일럿 완료와 구별해야 한다. 디자인 시스템 원문은 이 작업에서 수정하지 않았다. 문서 정합성 정리 시 이 설명을 덧붙일 것을 제안한다.

#62의 Depends on에서 #61을 GRILLING으로 부르는 표기도 현재 TASK 상태와 맞추는 것을 제안한다. 이 변경 역시 게시하지 않았다.
