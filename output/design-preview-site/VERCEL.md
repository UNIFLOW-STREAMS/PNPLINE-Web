# Vercel 배포

이 폴더 하나에 통합 메뉴와 시안 A–D, 키프레임 데모, 실행에 필요한 공용 자산이 모두 들어 있습니다.

- Framework Preset: `Other`
- Root Directory: `output/design-preview-site`
- Build Command: 비워 둠
- Output Directory: 비워 둠

순수 HTML, CSS, JavaScript 구성이라 빌드 과정이 없습니다. 배포 후 `/`에서 `index.html`이 열립니다.

Vercel Hobby의 업로드 제한을 맞추기 위해 `.vercelignore`가 제작 중간 산출물과 보존용 원본 PNG를 제외합니다. 화면과 배포에는 WebP 사본을 사용하며, 중복 원본 PNG와 QA 산출물은 정리했습니다.

## 포함 구조

- `concepts/a`: 영상 기반 홈 시안
- `concepts/b`: #63 시안 A 전체 이미지
- `concepts/c`: 블루 시스템 홈 시안
- `concepts/d`: 32px 그리드 전체 이미지
- `keyframes.html`: 시안 A 히어로 키프레임
- `assets`: 로고, 디자인 토큰, 검토 문서
