# PNPLINE S4 카메라 수정본

현재 작업 파일은 [master-s4-fix.blend](master-s4-fix.blend)입니다. 사용자 지적에 따라 f502에서 배가 작아지던 구도를 추가 수정했습니다. **이번 변경은 f458–521에만 적용**했고, f522 이후 하역과 승인된 S5 접합은 직전 저장본과 같습니다. Blender의 프리뷰 범위는 f444–696이며 전체 장면은 f0–1392 / 12fps입니다.

- [S4 수정 영상](preview/s4-after.mp4)
- [f502 전후 비교](review/close-reveal/f502-before-after.png)
- [이번 수정 전 영상](preview/s4-close-reveal-before.mp4)
- [S3 말미 → S4 → S5 연결 영상](preview/s3-tail_s4_s5-head.mp4)
- [보드·원본·수정본 비교](review/K1-K5-comparison.png)
- [검증 보고서](report-s4-camera.md)
- [카메라 경로](review/camera-path.png)와 [가림 검토](review/occlusion-review.png)

카메라·타깃·렌즈의 변경 범위는 f458–671입니다. 사용자가 승인한 S5 접합은 f649–671이며 f672부터 원본으로 정확히 복귀합니다. 선박, 차량, 화물, 크레인, 도로, 창고의 형상·배치·동작과 이벤트 시점은 보존했습니다.

중간 이동에는 일부 기둥 스침이 남습니다. 핵심 안착·분리 구간에서는 운전석의 기둥 가림을 해소했습니다. 프레임별 범위와 검사 한계는 보고서에 명시했습니다.

`inputs/before-close-reveal.blend`는 이번 수정 직전 최신 사용자 저장본입니다. **현재 재현 소스는 `scripts/revise_close_reveal.py`**이며 이 백업을 입력으로 사용합니다. `inputs/base-s4.blend`와 `scripts/revise_s4.py`는 이전 S4 단계 이력입니다. 재개방·소스 재현 결과는 `review/reopen-check.json`, 이번 전체 상태 차이는 `review/close-reveal/correction-diff.json`, 해시는 `hashes.json`에서 확인할 수 있습니다.

`review/candidate-target.blend`, `review/candidate-limited.blend`, `preview/s4-target-review.mp4`, `preview/s4-boundary-limited.mp4`는 승인 전 비교 이력입니다. `preview/s4-before.mp4`는 최초 S4 기준본입니다. 현재 결과는 위의 master와 s4-after, 연결 영상입니다. 종전 완료 판정은 사용자 피드백으로 재검토했으며 현재 상태는 `progress-close-reveal.md` 및 최신 보고서를 따릅니다.

재실행 명령과 환경은 보고서에 있습니다. 생성 소스는 원본 백업의 해시와 출력 경로를 검사하고, master가 외부에서 변경되면 덮어쓰기를 중단합니다. 실행 전에 Blender의 사용자 변경을 먼저 저장해야 합니다.
