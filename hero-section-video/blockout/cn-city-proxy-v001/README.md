# 중국 도시·항구 프록시 v001

**전체 판정: 재작업 필요 — 카메라 재설계 선행.** 프록시는 제작했지만 현재 S2 카메라에서는 주요 타워의 상부가 잘립니다.

- 결과: `master-cn-city-proxy-v001.blend`
- 기준: `../s5-integration-v001/master-s5-integration-v001.blend`의 12fps 원본. 모션 폴리싱/배속 후보는 별도로 보존했습니다.
- 검토: `review.html` 또는 `http://127.0.0.1:8772/review.html`
- 본편: `preview/after-s2.mp4`, `preview/after-connection.mp4`
- 형태 확인: `review/diagnostic/overview.png`, `top.png`, `shore.png`
- 판정·명령·한계: `report.md`

Blender의 `CN_CITY_PROXY_V001` 컬렉션에서 8개 형태군을 개별 편집할 수 있습니다. `CN_PROXY_ROOT`는 기존 `CN_FRAME` 아래에 있으며 지역 +Z가 위입니다. 모든 프록시는 정적이며, 별도 스크립트 없이 재개방·렌더됩니다. 원본의 단순 도시5개는 삭제하지 않고 결과 복사본에서만 숨겼습니다.

재생성은 `proxy-config.json`과 `scripts/build_proxy.py`를 사용합니다. 입력 원본과 같은 경로 또는 이미 존재하는 출력은 거부합니다. 새 버전을 만들어 비교하고, 열려 있는 GUI의 미저장 작업을 덮어쓰지 마세요. 사용 명령은 보고서와 `review/*commands.json`에 있습니다.

조감도는 형상 점검용이며 S2 가시성 성공 증거가 아닙니다. 카메라·항로·타이밍 변경, 스타일프레임, 외부 생성 서비스와 공개는 이번에 실행하지 않았습니다.
