# 생성 산출물 관리

렌더 프레임, 비교 영상과 검토 이미지, 자동 생성 장면 스냅샷, 중간 Blender 버전은 로컬 작업 자료로 보관하고 Git에서 제외한다. 재생성 스크립트, 설정, 문서, 입력 텍스처와 최종 채택 장면은 추적한다. 기록에 나오는 로컬 검토 경로나 과거 버전 파일은 새로 복제한 저장소에 없을 수 있다.

최종 Blender 파일은 hero-section-video/hero-section-A.blend와 hero-section-B.blend다. lookdev/hero-material-v001의 장면은 상하이 랜드마크 수정 단계 보존본이다. final/ 아래 중복 Blender 사본은 로컬에 보관한다.

스크롤 미리보기의 assets/previz-scrub.mp4와 포스터는 페이지 실행에 필요하므로 유지한다. previz-source.mp4와 QA 녹화·스크린샷은 재생성 가능한 검토 자료로 제외한다.

2026-11-02 정리 시 원격에 없는 커밋을 재작성했다. 기존 로컬 이력은 backup/before-render-cleanup-20261102-055040 브랜치에만 보존했다. 이 백업 브랜치를 원격으로 푸시하면 제거했던 대용량 객체가 다시 전송되므로 푸시 대상은 main으로 한정한다.
