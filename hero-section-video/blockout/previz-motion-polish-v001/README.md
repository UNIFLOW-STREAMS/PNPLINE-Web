# PNPLINE S1–S7 모션 폴리싱 v001

속도·이징 검증 후보 수용 가능 / 사용자 리듬 선택 대기

- A: `master-motion-polish-A.blend`, `preview/candidate-A.mp4` — 24fps / 1,393프레임 / 58.041667초.
- B: `master-motion-polish-B.blend`, `preview/candidate-B.mp4` — 24fps / 1,306프레임 / 54.416667초.
- `review.html`: 원본116.08초·기존2배속58.04초·A/B 비교, S5 및 구간 경계 실제 렌더.
- `event-map.csv`, `time-map-A/B.json` 및 CSV: 사건·모든 베이크 시점 대응.
- `s5-storyboard-map.json`: 원본 f672·720·732·766·842·900의 정확한 소수 프레임 대응과 가장 가까운 영상 프레임.
- `scroll-progress-map.json`: 최초–마지막 프레임 시간에 대한0–1 진행률. 최종 MP4의 마지막 프레임 노출1/24초는 별도.

Blender에서 A/B 중 하나를 열어 24fps, Frame Dropping으로 전체 재생합니다. 재생기에 추가 2배속을 적용하지 않습니다. 밀집 LINEAR 키는 원본 경로를 유지하기 위한 편집 가능한 베이크입니다. 설계 변경은 `config.json` 후 `scripts/build_candidates.py` 재실행으로 재현합니다. 접지 키는 Blender의 `FCurve.update()`가 가까운 키를 삭제할 수 있으므로 일괄 정리하지 마세요.

원본은 `../s5-integration-v001/master-s5-integration-v001.blend`이며 이 폴더의 `inputs/source.blend`와 SHA256이 같습니다. 원본은 수정하지 않았습니다. 사용자 승인으로 새 후보에만 도로 폭·경사와 바퀴 고도를 보정했습니다. 수평 동선, 차량/컨테이너 루트, 문 동작, 여섯 카메라 구도를 보존했습니다.

`review/master-contact-proposal.blend`, `failed-wheel-key-*.blend`, `*-failed-*`, `*-center-only.json`, `*-vertex-v1.json`은 **실패 원인 추적용 과거 시험 자료**입니다. 최종 파일이나 검증 근거로 사용하지 마세요. `hashes.json`, `validation-A/B.json`, `render-record-A/B.json`이 현재 후보를 식별합니다.

재현 순서(Blender5.1): `--factory-startup -b --python-exit-code 1 --python scripts/build_candidates.py`, 각 변형에 대해 `scripts/validate_candidates.py -- A` 또는 `-- B`, 통과 후 `scripts/render_candidates.py -- A B`, Python으로 `scripts/package_media.py A B`. 비교 스틸은 `scripts/render_stills.py`, 대응표는 `scripts/write_maps.py`, 인계는 `scripts/finalize.py`입니다. 실행 스크립트는 자신의 위치에서 출력 루트를 찾습니다.

상세 검사·한계는 `report.md` 참조. 공개용 Scroll World 속도/사용자 경험 승인은 별도입니다.
