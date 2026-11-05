# 중국어 사이트 구조화 데이터 점검

2026-11-02. 대상은 `output/pnpline-web-zh`의 `/` 및 `/privacy`입니다.

## 발견 사항과 반영 결과

| 발견 사항 | 반영 결과 |
| --- | --- |
| Organization을 WebSite.publisher 안에 반복 정의 | 공통 `@id`로 참조하고 각 문서 안에서는 한 번만 정의 |
| 홈페이지 자체 WebPage 정보와 사이트 소속 관계 누락 | 제목·설명·zh-CN·isPartOf·about·publisher 및 콘텐츠 영역 연결 추가 |
| 서비스 화면과 별도 구조화 원고의 불일치 가능성 | 서비스 선택자와 WebPageElement 4개가 `app/service-data.ts`를 공유 |
| FAQPage가 홈/사이트와 연결되지 않음 | `/#faq`를 홈페이지의 FAQ 영역으로 연결하고 질문·답변 ID를 실제 DOM ID와 맞춤 |
| 개인정보 페이지에 JSON-LD가 없고 홈 제목·설명을 상속 | 미리보기 안내에 맞는 독립 WebPage, 제목·설명 추가 |
| 확정되지 않은 배포 도메인 | SITE_URL 설정 전에는 상대 ID만 출력. 설정 후 공식 URL·로고 절대 URL·페이지별 canonical 생성 |
| SITE_URL에 인증정보 등이 허용될 가능성 | HTTP(S) origin만 허용하며 경로·인증정보·쿼리·fragment를 거부 |

홈페이지의 FAQ 9개는 기존 화면 원고 `app/faq-data.ts`를 그대로 사용합니다. 기존 질문과 답변을 새 사업 주장으로 바꾸지 않았습니다. 서비스는 페이지 안의 설명 영역으로 표현했으며 상품·확정 가격·온라인 접수 Action·후기·평점·시설 주소·연락처·인증·법인명은 만들지 않았습니다. 개인정보 페이지는 정식 운영 정책이 아닌 미전송 미리보기의 동작을 설명합니다.

## 검증

- `node schema-check.cjs`: 통과. 미설정/설정 origin, ID 중복·미해결 참조, FAQ 9개와 서비스 4개 데이터 일치, URL 입력 거부, JSON 구문 및 script 종료 문자열 이스케이프를 검사했습니다.
- `npm run typecheck`: 통과.
- `npm run build`: 통과. 샌드박스에서 생성 디렉터리 EPERM이 반복되어 같은 명령을 일반 로컬 실행 권한으로 검증했습니다.
- `node schema-render-check.cjs`: 통과. 실제 프로덕션 HTML의 JSON-LD 한 개, 페이지별 제목·설명·언어, DOM에 출력된 질문·답변 9개와 서비스 설명 4개를 대조했습니다. 원고 생성 함수만 검사한 결과와 구분됩니다.
- Schema.org Markup Validator: 홈·개인정보 JSON-LD 코드 검사에서 각각 **오류 0개, 경고 0개**. 증거는 `validator-home.txt/png`, `validator-privacy.txt/png`입니다. 검증에는 의도적으로 `https://cn.example.test/`라는 테스트 origin을 사용했으며 실제 도메인의 접근성이나 로고 URL 크롤링을 검사한 결과가 아닙니다.
- Google Rich Results Test와 배포 도메인의 Search Console URL 검사는 실행하지 않았습니다. 실제 origin과 공개 배포가 확정된 후 별도로 확인해야 합니다.

완전한 JSON-LD는 `preview-home.json`, `preview-privacy.json`에 있습니다. `configured-home.json` 및 `configured-privacy.json`은 SITE_URL 설정 시의 구조를 확인하는 테스트용 데이터로, 배포 파일로 복사하지 않습니다. 실제 문서는 `app/structured-data.ts`가 빌드 시 생성합니다.

## 최신 문서 확인

- [Google Organization 가이드](https://developers.google.com/search/docs/appearance/structured-data/organization): 확인된 조직 정보와 실제 로고를 표현합니다. 미확인 주소나 전화번호를 경고 제거 목적으로 채우지 않습니다.
- [Google 변경 기록](https://developers.google.com/search/updates#may-2026): FAQ 리치 결과는 2026-05-07부터 표시되지 않으며 관련 문서도 제거됐습니다. 정부·의료 사이트에만 허용된다는 예전 기준을 현재 기준으로 적용하지 않았습니다.
- [Schema.org FAQPage](https://schema.org/FAQPage), [WebPage](https://schema.org/WebPage), [WebPageElement](https://schema.org/WebPageElement): 기존 FAQ 및 서비스 설명 영역의 의미 표현에 사용합니다. 검색 결과 노출 자격과 Schema.org 어휘 유효성은 별개의 검사입니다.
- Next.js 설치본 `node_modules/next/dist/docs/01-app/02-guides/json-ld.md`에 따라 서버 페이지의 기본 script 요소와 `<` 이스케이프를 사용합니다.

공식 도메인을 SITE_URL로 설정한 후 다시 빌드해야 canonical과 절대 URL이 반영됩니다. 도메인·법인·시설·접수 정보가 아직 미확정인 점은 이번 코드 수정으로 확정된 것으로 간주하지 않습니다.
