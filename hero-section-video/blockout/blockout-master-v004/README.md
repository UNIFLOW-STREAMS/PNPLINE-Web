# PNPLINE S2 카메라 — 승인 통합 v004

**master-v004.blend가 최종 승인 범위의 통합 작업본입니다.**

- S2 후방 추적 후보와 승인된 f217–251 S3 접합을 적용했습니다. f252부터 원래 카메라로 복귀합니다.
- 전체 검사35개 통과, 서브프레임 관통0건, 정상 재생/재개방 픽셀 일치 확인. 형상 차이는 report-s2-camera.md 참조.
- preview/s2-after.mp4: 최종 S2. preview/s1-tail_s2_s3-head.mp4: f84–276 연결 검토.
- review/K1-K5-comparison.png: 보드/원본/최종 비교.
- GUI 검토 preview 범위84–276 저장. 전체 타임라인0–1392와12fps는 그대로입니다.
- limited-v004.blend 및 s2-target-candidate-v004.blend는 승인 전 이력이며 후자는 미접합 후보입니다. 최종 작업에는 master-v004.blend를 사용하세요.
- inputs/base-v003.blend: 원본 보존. scripts/: 재현/검사 소스. hashes.json: 파일 해시.

기존 CAMERA_PATH는 이전 가이드입니다. 새 카메라 경로는 review/camera-path-top.png와 camera-path-oblique.png를 참고하세요. .blend1은 Blender 자동 이전 저장 백업입니다.
