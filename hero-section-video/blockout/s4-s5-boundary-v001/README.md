# S4–S5 boundary v001 — 차량 접지·겹침 수정본

2026-10-08 사용자 후속 요청 반영 완료.

- 작업본: `master-s4-s5-boundary-v001.blend`
- 이번 수정 영상: `wheel-fix/after.mp4` (f540–792)
- 기존 범위 영상: `preview/after.mp4` (f596–792, 갱신됨)
- 수정 직전 백업: `wheel-fix/before-wheel-fix.blend`
- 결과·범위·재현 및 검증 방법: `report.md`

현행 검증은 `wheel-fix/test_vehicle.py`, `wheel-fix/check_preservation.py`, `regression/scripts/test_scene.py` 및 `wheel-fix/validation.json`을 사용한다. 이전 `tests/`, `review/`, `scripts/run_final.py`는 수정 전 후보의 이력이며 이번 저장본을 재현하는 워크플로가 아니다.
