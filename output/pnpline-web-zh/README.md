# PNPLINE 중국어 사이트

현재 영문 `pnpline-web` 앱을 복제한 독립 간체 중국어 버전입니다. 원본 앱은 `C:/Users/KIM TAEHYUNG/.codex/visualizations/2026/11/01/01a19616-7090-7b72-86b1-f85ae4da029a/pnpline-web`이며, 2026-11-02의 구현을 기준으로 복제했습니다.

## 실행

```powershell
cd F:/pnpline-landing/output/pnpline-web-zh
npm ci
npm run dev
```

홈: http://127.0.0.1:3092/ · 개인정보 안내: http://127.0.0.1:3092/privacy

프로덕션 확인은 `npm run build` 후 `npm start`로 실행합니다. 영문 원본의 3091 포트와 구분됩니다.

## 구현

원본의 섹션 순서, 이미지, 영상, GSAP 모션, 서비스 선택, 고객 유형 패널, 창고 탭, 수입 준비 단계, FAQ와 문의 폼을 유지했습니다. 메뉴·본문·입력 안내·검증 메시지·접근성 이름·개인정보 안내·메타데이터·FAQ 구조화 데이터를 중국어로 옮겼습니다. 플랫폼명과 FBA, FBM, IOR, HS, FDA, FCC, API 등의 약어는 유지했습니다. 이미지 자산 속 기존 영문 레이블과 브랜드 표식은 원본 그대로입니다.

`app/zh-CN.css`에서 중국어 글꼴, 자간, 행간과 모바일 제목 줄바꿈을 조정합니다. 저장소에 있던 Noto Sans SC 글꼴과 라이선스를 `public/fonts/`에 복제했으며 시스템 중국어 글꼴을 대체 글꼴로 사용합니다. 주요 본문 너비와 브랜드 색상은 원본을 유지합니다.

월물량은 `不确定`, `未定`, `待定`, `not sure`를 미정 값으로 인식합니다. 중국어 초안은 `pnpline-inquiry-draft-zh-CN-v1` 키에 보관하며 영문 초안과 구분됩니다.

이 폼은 입력 확인용입니다. 실제 문의 접수는 연결되지 않았고, 개인정보 페이지도 이 미리보기의 저장 동작을 설명합니다. 배포·접수 연결·사업상 확정 정보는 추가하지 않았습니다.

## 확인

```powershell
npm run build
npm run typecheck
node qa.cjs
```

브라우저 검사는 실행 중인 3092 서버와 Windows에 설치된 Chrome을 사용합니다. 결과는 `review/qa-results.json`, 화면 캡처는 `review/`에 저장합니다. 1920·834·390·320px의 섹션 넘침, 중국어 메타데이터와 FAQ 구조화 데이터, 선택 UI, 폼 오류·미정 물량·초안 복원·초기화, 개인정보 페이지, 메뉴와 영상 정지 상태를 확인합니다. 모바일 크기는 Chromium 에뮬레이션이며 실제 모바일 기기 검증은 아닙니다.

## 구조화 데이터

홈의 조직·사이트·페이지·서비스 설명·FAQ 및 개인정보 페이지의 JSON-LD는 서버에서 출력합니다. 상세 점검 내용과 검증 근거는 `review/schema/SCHEMA.md`를 참고합니다.

배포 도메인이 확정되면 `.env.example`을 참고해 `.env.local`의 `SITE_URL`에 중국어 사이트의 실제 origin을 설정하고 **다시 빌드**합니다. 경로·사용자 인증정보·쿼리·fragment는 사용할 수 없습니다. 미설정 시에는 로컬 미리보기용 상대 ID를 사용하고 공식 URL·로고 URL·canonical을 추측하지 않습니다.

```powershell
node schema-check.cjs
npm run build
node schema-render-check.cjs
# 선택 사항: 테스트용 origin을 넣은 JSON-LD를 Schema.org 웹 검증기에 제출
node schema-validator.cjs
```

`schema-render-check.cjs`는 `SITE_URL`을 설정하지 않은 미리보기 빌드를 검사합니다. `schema-check.cjs`는 미설정·설정 두 경우를 모두 검사하며, 생성되는 `configured-*.json`의 `cn.example.test`는 검증 전용 예시 주소입니다. 실제 사이트에 삽입되는 주소가 아닙니다. FAQ 구조화 데이터는 의미 표현용으로 유지하며 Google FAQ 리치 결과 노출을 약속하지 않습니다.
