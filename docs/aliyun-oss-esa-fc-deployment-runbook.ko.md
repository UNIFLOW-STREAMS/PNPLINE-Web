# PNPLINE 중국 본토 OSS·ESA·FC 배포 실행 절차

- 작성일: 2026-11-06
- 상태: 실행 전 구성 제안. 이 문서를 작성하면서 애플리케이션 코드를 변경하거나 클라우드 리소스를 생성하지 않았다.
- 기준: 현재 로컬 `F:/pnpline-landing/output/pnpline-web-zh`의 코드와 설치된 Next.js 16.4.3 문서.
- 사용자 확인 사항: 중국 본토 법인이 있으며 사이트 도메인의 ICP备案을 완료했다.
- 범위: `/`, `/privacy/`, 스크롤 영상, 견적 문의 접수와 알림. 로그인·고객 포털·WMS 연동은 이번 배포 범위에 포함하지 않는다.
- 별도 디자인 비교본을 운영본으로 선택하면 그 디렉터리에 같은 변경을 적용한다. 여러 비교본을 한꺼번에 배포하지 않는다.

## 1. 무엇부터 해야 하는가

첫 작업은 서버 구매가 아니라 **운영할 앱을 확정하고 정적 export 빌드를 검증하는 것**이다. 현재 코드는 Next.js 서버 실행을 기준으로 설정되어 있다. 정적 파일 생성과 문의 API를 분리한 다음 클라우드 설정에 들어간다.

권장 순서는 다음과 같다.

1. 운영 앱·도메인·공개 경로를 고정한다.
2. 프런트엔드의 정적 export와 운영용 폼을 구현한다.
3. 독립된 문의 API와 알림 함수를 구현하고 로컬에서 저장·오류·중복 처리를 검증한다.
4. Aliyun에서 리소스 그룹·VPC·Tablestore·OSS를 준비한다.
5. FC와 발신 이메일을 연결하고 원본 API를 검증한다.
6. ESA에 도메인을 추가하고 원본·HTTPS·라우팅·캐시·보안을 설정한다.
7. DNS를 전환하고 색인을 막은 상태에서 중국 내 실제 도메인 검수를 수행한다.
8. 검수 통과 후 색인을 허용하는 빌드를 배포한다.

DNS 전환은 트래픽을 보내는 작업이다. NS 접속 방식에서는 ESA 활성화에 DNS 변경이 필요할 수 있으므로, 모든 원격 검수를 DNS 전환 전에 끝낼 수 있다고 가정하지 않는다. 로컬 검수와 원본 검수를 먼저 끝내고, 기존 서비스가 있다면 점검 시간과 원복 값을 확보한다.

## 2. 현재 코드에서 확인한 내용

| 구현 확인 | 근거 | 배포에 미치는 영향 |
|---|---|---|
| `output: 'export'`가 없고 이미지 최적화와 `headers()`를 사용한다. | `next.config.ts` | OSS에 프로젝트를 그대로 올려서는 실행되지 않는다. |
| `SITE_URL`은 빌드 과정에서 메타데이터와 구조화 데이터에 반영된다. | `app/site-data.ts`, `app/page.tsx`, `app/structured-data.ts` | 도메인 변경 후 재빌드가 필요하다. |
| API 주소를 설정하면 폼이 FC에 접수 요청을 보낸다. 주소가 비어 있으면 미리보기로 동작한다. | `app/quote-inquiry.tsx`, `app/inquiry-config.ts` | FC 검수 후 실제 주소를 지정해 다시 빌드한다. |
| 폼 초안과 재시도 키는 현재 탭의 `sessionStorage`에 보관된다. | `app/quote-inquiry.tsx` | 접수 성공 시 초안이 지워지고 응답 실패 시 입력과 키가 유지된다. |
| 개인정보 본문과 메타 설명은 미리보기와 접수 모드에 따라 달라진다. | `app/privacy/page.tsx`, `app/site-data.ts` | 공개 전에 실제 처리 주체·수신처·보관 기준을 확인한다. |
| 개인정보 링크는 `/privacy`와 `/privacy/`가 혼재한다. | `app/landing.tsx`, `app/quote-inquiry.tsx`, `app/structured-data.ts` | 이번 배포에서는 `/privacy/`로 통일한다. |
| 데스크톱 1080p·모바일 720p MP4를 브라우저에서 선택한다. | `app/hero-journey.ts` | 같은 URL 경로를 유지하고 ESA에서 Range와 캐시를 설정한다. |
| 기존 QA는 3092 서버와 미리보기 동작을 검사한다. | `qa.cjs`, `schema-render-check.cjs` | 정적 산출물·운영 canonical·실제 접수 검증으로 변경해야 한다. |

설치된 Next.js 문서 `node_modules/next/dist/docs/01-app/02-guides/static-exports.md`에서 정적 export 설정과 제한을 확인했다. 정적 export에서는 기본 이미지 최적화 서버, `headers()`, 서버 POST API를 사용할 수 없다. 실제 전환 빌드는 아직 실행하지 않았다.

## 3. 주소와 리소스 이름

아래 리소스 이름은 제안이다. OSS 이름은 전역 중복을 피하도록 실제 생성 시 접미사를 붙인다. `<...>` 값은 콘솔에서 생성된 값을 복사하고 추측하지 않는다.

| 용도 | 주소·리소스 제안 | 연결 |
|---|---|---|
| 대표 사이트 | `https://pnpline.cn` | ESA → 비공개 OSS |
| www | `https://www.pnpline.cn` | ESA에서 대표 사이트로 301, 경로·쿼리 유지 |
| 브라우저용 문의 API | `https://api.pnpline.cn/v1/inquiries` | ESA → FC 원본 도메인 |
| FC 원본 | `https://fc-origin.pnpline.cn` | DNS 전용 → FC가 안내하는 접속점, ESA 프록시 제외 |
| 발신 전용 도메인 | `notify.pnpline.cn` | DirectMail 도메인 검증 |
| 기본 리전 | `cn-shanghai` | OSS·FC·Tablestore·VPC를 같은 리전에 생성 |
| 리소스 그룹 | `pnpline-prod` | 비용·권한·태그 관리 |
| 웹 버킷 | `pnpline-web-prod-<unique>` | 공개 가능한 정적 파일만 저장 |
| 문의 함수 | `pnpline-inquiry` | HTTP Web 함수 |
| 알림 함수 | `pnpline-notify` | 이벤트 함수 |
| 문의 테이블 | `inquiries` | 문의 내용과 알림 상태를 한 행에 저장 |

`fc-origin.pnpline.cn`을 별도로 두는 이유는 API가 자기 자신의 ESA 주소로 다시 요청되는 순환을 피하고, FC 원본의 Host·TLS 인증서를 명확하게 맞추기 위해서다.

## 4. 프런트엔드 코드 수정

### 4.1 정적 export 설정

`next.config.ts`의 목표 설정은 다음과 같다. 코드 조각은 제안이며 아직 적용하지 않았다.

```ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
  poweredByHeader: false,
};

export default nextConfig;
```

- 기존 `headers()`는 제거하고 ESA 및 OSS 객체 메타데이터에서 설정한다.
- 별도 `distDir`은 제거하여 중간 빌드는 `.next`, 배포 산출물은 `out`으로 구분한다.
- 초기에는 이미지를 빌드 전에 WebP·AVIF 등으로 최적화하고 `unoptimized: true`로 서버 의존성을 없앤다. 이 설정 자체가 이미지를 압축하는 것은 아니다.
- GSAP와 스크롤 영상은 브라우저 동작을 유지한다.
- `app/api`에 POST 핸들러를 추가하지 않는다. 정적 사이트와 독립된 FC 패키지를 사용한다.
- 운영에 `next start`를 사용하지 않는다. 로컬 정적 검수용 서버는 `out`을 제공한다.

### 4.2 파일별 변경 목록

| 파일 | 필요한 변경 |
|---|---|
| `next.config.ts` | 위 정적 export 설정을 적용한다. |
| `.env.example` | 접수 API URL·정책 버전·공개 문의처를 빌드에 제공한다. `SITE_INDEXING`은 정적 배포 설정과 함께 반영한다. 실제 비밀값은 넣지 않는다. |
| `app/quote-inquiry.tsx` | 접수와 재시도를 구현했다. 실제 ESA·FC 환경에서 다시 검증한다. |
| `app/privacy/page.tsx` | 실제 처리 주체·목적·항목·수신자·보관 기간·삭제 요청·국외 제공 여부·문의처를 반영한다. canonical을 `/privacy/`로 통일한다. |
| `app/site-data.ts` | 개인정보 메타 설명을 교체하고 운영 도메인 누락 시 배포 빌드가 실패하도록 검증한다. |
| `app/structured-data.ts` | 개인정보 URL과 `@id`를 `/privacy/`, `/privacy/#webpage`로 통일한다. |
| `app/landing.tsx` | 푸터 개인정보 링크를 `/privacy/`로 바꾸고 실제 ICP 등록번호와 공식 조회 링크를 넣는다. |
| `app/layout.tsx` | 검수 빌드에는 robots 메타 `noindex, nofollow`를, 운영 공개 빌드에는 색인 허용 설정을 적용한다. |
| `app/sitemap.ts` 신규 | 공개가 확정된 `/`, `/privacy/`만 생성한다. 정적 생성 설정을 적용한다. |
| `app/robots.ts` 신규 | `SITE_INDEXING`에 따라 정책을 생성한다. 정적 생성 설정을 적용한다. |
| `app/hero-journey.ts` | 현재 영상 경로를 유지한다. 원격 검수에서 과도한 초기 다운로드가 확인되면 프리로드 시점을 조정한다. |
| `qa.cjs` | 기본 URL을 환경 변수로 받아 로컬 정적 서버와 실제 도메인에서 실행할 수 있게 한다. 미전송 검사를 접수 계약 검사로 교체한다. |
| `schema-render-check.cjs` | `out/index.html`, `out/privacy/index.html`을 검사하고 운영 canonical이 존재하는 경우를 검증한다. |
| `schema-check.cjs` | `/privacy/`로 바뀐 URL과 개인정보 메타데이터를 반영한다. |
| `package.json`, `README.md` | 정적 검수·배포 절차를 기록하고 `next start`를 운영 실행 명령으로 안내하지 않도록 수정한다. |

`robots.txt`의 수집 차단만으로 `noindex`를 대신하지 않는다. API 응답에는 `X-Robots-Tag: noindex`를 적용한다. 접근 제한이 필요한 임시 검수 URL은 인증도 적용한다.

### 4.3 빌드 환경 변수

```dotenv
SITE_URL=https://pnpline.cn
NEXT_PUBLIC_INQUIRY_API_URL=https://api.pnpline.cn/v1/inquiries
NEXT_PUBLIC_INQUIRY_CONSENT_VERSION=<공개하는 개인정보 안내 버전>
NEXT_PUBLIC_INQUIRY_PRIVACY_EMAIL=<공개 가능한 개인정보 문의 주소>
SITE_INDEXING=block
```

- 검수 후 공개할 때 `SITE_INDEXING=allow`로 바꾸고 **다시 빌드**한다.
- `NEXT_PUBLIC_*`는 브라우저에 포함되는 공개 설정이다. AccessKey·이메일 비밀번호·원본 인증 비밀값은 넣지 않는다.
- `.env.local`, `.env.production.local`과 로컬 자격증명이 Git과 OSS 업로드 대상에서 제외되는지 확인한다.
- 검수할 때는 알림 함수의 `DM_RECIPIENT`를 테스트 업무용 주소로 지정한다.

수정 후 실행할 빌드 명령 예시는 다음과 같다. 이 명령들은 아직 실행하지 않았다.

```powershell
Set-Location 'F:\pnpline-landing\output\pnpline-web-zh'
$env:SITE_URL = 'https://pnpline.cn'
$env:NEXT_PUBLIC_INQUIRY_API_URL = 'https://api.pnpline.cn/v1/inquiries'
$env:NEXT_PUBLIC_INQUIRY_CONSENT_VERSION = '<공개하는 개인정보 안내 버전>'
$env:NEXT_PUBLIC_INQUIRY_PRIVACY_EMAIL = '<공개 가능한 개인정보 문의 주소>'
$env:SITE_INDEXING = 'block'
npm ci
npm run typecheck
npm run build
```

배포 산출물에서 최소한 `index.html`, `privacy/index.html`, `404.html`, `_next/`, `assets/`, `fonts/`, `robots.txt`, `sitemap.xml`을 확인한다. Next.js가 추가로 생성한 라우트 데이터와 `.txt` 파일도 배포한다. 소스 저장소, `node_modules`, `.next`, 검수 캡처, 환경 변수 파일을 웹 버킷에 업로드하지 않는다.

## 5. 문의 API 구현 계약

접수와 알림 함수 코드는 `functions/inquiry/`에 있다. 같은 코드 패키지를 두 FC 함수에 배포하고 실행 역할과 진입점을 구분한다. [구현 및 배포 설정](../functions/inquiry/README.ko.md)을 참고한다.

### 5.1 요청과 응답

```http
POST https://api.pnpline.cn/v1/inquiries
Content-Type: application/json
Idempotency-Key: <브라우저가 만든 UUID>
```

```json
{
  "cargo": "服装",
  "shipping": "海运拼箱",
  "volume": "不确定",
  "unit": "",
  "otherUnit": "",
  "destination": "FBA 仓库",
  "ior": "不确定",
  "email": "customer@example.com",
  "consent": true,
  "consentVersion": "<공개한 개인정보 정책 버전>",
  "website": ""
}
```

`website`는 화면에서 숨기고 접근성·자동완성 설정을 고려한 허니팟 필드다. 서버에서도 기존 필수값·길이·열거값·수량 조건·동의 버전을 검증한다. 월 물량의 미정 표현을 서버에서 일관된 값으로 정규화한다. 초기 요청 본문 제한은 16 KiB를 제안한다.

| 결과 | 응답 계약 | 화면 동작 |
|---|---|---|
| 최초 저장 성공 | `201 { "inquiryId": "...", "status": "accepted" }` | 접수번호 표시, 초안 삭제 |
| 같은 키·같은 내용 재시도 | `200`, 같은 접수번호 | 이미 접수된 결과로 처리 |
| 같은 키·다른 내용 | `409` | 입력을 유지하고 새 요청으로 다시 제출하도록 안내 |
| 입력 오류 | `422`, 필드별 오류 | 해당 입력으로 포커스 이동 |
| 허용 크기 초과 | `413` | 입력을 유지하고 오류 표시 |
| 요청 제한 | `429`, `Retry-After` | 안내된 시간 후 재시도 |
| 저장 실패·일시 장애 | `503`, 추적용 request ID | 입력 유지, 성공 문구 금지 |
| 응답을 받지 못한 타임아웃 | 클라이언트에서 결과 미확정 | 같은 키·같은 내용으로 재시도 |

한 번 제출한 내용에 대해 재시도할 때 같은 키를 유지한다. 오류 후 사용자가 내용을 바꾸면 새 키를 생성한다. 키와 제출 내용의 연결을 세션에서 관리하고, API는 정규화한 내용의 해시를 저장해 잘못된 키 재사용을 판별한다.

### 5.2 저장과 알림

`inquiries`의 문자열 기본키는 `inquiryId`로 하고, 검증된 UUID 요청 키를 이용해 동일 요청이 같은 행을 가리키게 한다. 사용자에게 다른 문의의 내용을 반환하지 않는다.

저장할 주요 속성은 문의 필드, `receivedAt`, `consentVersion`, `consentAcceptedAt`, `payloadHash`, `notificationStatus`, `notificationAttempts`, `nextNotificationAt`, `lastConsultedAt`, `deleteAfter`다. 시간은 서버가 생성한다.

1. Tablestore의 행 부재 조건으로 문의와 `notificationStatus=pending`을 같은 행에 저장한다.
2. 저장 성공 후 브라우저에 접수번호를 반환한다.
3. 매분 실행되는 알림 FC가 발송 대기 행과 만료된 발송 잠금을 찾는다.
4. 알림 함수는 조건부 상태 변경으로 작업을 확보한다. 지정한 업무용 메일함으로 접수번호, 화물, 운송 방식, 월 물량, 목적지, IOR, 고객 이메일을 담은 메일을 보낸 뒤 `sent`를 기록한다.
5. 발송 실패 시 1분·5분·30분 후 재시도한다. 모두 실패하면 `failed`와 운영 알림용 로그를 남긴다.
6. 운영 담당자는 수신함을 확인한 뒤 필요하면 실패한 행을 수동으로 재처리한다.

메일 시스템까지 포함한 정확히 한 번의 발송을 보장한다고 표현하지 않는다. 발송 직후 프로세스가 종료되면 중복 메일이 생길 수 있으므로 접수번호로 식별한다. 문의 저장의 중복 방지와 메일 재시도는 별도 책임이다. 처리량이 증가하면 알림 상태·재시도 시각 조회에 인덱스를 적용한다.

현재 내부 계획의 보관 기준은 **마지막 상담 후 12개월**이며 공개 정책으로 최종 확정할 항목이다. 단순히 제출 후 365일 TTL을 설정하면 이 기준과 다르다. `lastConsultedAt`·`deleteAfter`를 관리하고 정기 삭제 작업에 반영하며, 백업과 로그 보존도 정책에 맞춘다.

## 6. Aliyun 콘솔 설정 순서

아래 중국어 메뉴명은 공식 문서의 현재 경로를 기준으로 한다. 계정·콘솔 버전에 따라 배치가 다르면 같은 기능명을 검색한다.

### 1단계: 리소스 그룹과 권한

- 리소스 그룹 `pnpline-prod`와 `project=pnpline`, `env=prod` 태그를 만든다.
- 배포 담당자와 FC 실행용 RAM 역할을 구분한다.
- 배포 권한은 웹 버킷 업로드·해당 함수 배포·ESA 갱신에 한정한다.
- FC 역할에는 문의 테이블 읽기·쓰기, 해당 로그 저장소 기록, 필요한 메일 발송 권한을 부여한다. SDK는 함수 역할의 임시 자격증명을 사용한다.
- 월 예산과 실제 사용량 알림 수신처를 설정한다.

완료 조건: 테스트 역할로 허용한 리소스에만 접근할 수 있다.

### 2단계: VPC와 데이터 저장소

1. 상하이에 기존 VPC를 재사용하거나 `pnpline-prod-vpc`를 만든다. 기존 사내망·VPN과 CIDR이 겹치지 않게 한다.
2. FC가 지원하는 서로 다른 가용 영역에 vSwitch 2개를 준비하고, 전용 보안 그룹을 만든다. 외부에서 ECS처럼 함수를 직접 연결하는 인바운드 규칙은 필요하지 않다.
3. Tablestore에서 상하이 인스턴스를 만든다. 현재 구매 화면은 VCU 방식도 안내하므로, 소규모 시작에는 **예약 VCU 0·탄력 사용**이 가능한지와 최소 비용을 구매 화면에서 확인한다.
4. `inquiries` 테이블을 만들고 기본키 `inquiryId: STRING`, 최대 버전 수 1로 설정한다. 보관 정책은 앞 절의 상담 기준에 맞춘다.
5. 인스턴스의 네트워크 관리에서 사용할 VPC를 연결하고, FC에는 콘솔에 표시되는 **VPC Endpoint**를 설정한다. 공개 DB 접속을 열어 초기 연결 문제를 해결하는 방식은 사용하지 않는다.
6. 현재 알림 구현은 타이머로 동작하므로 Stream 설정은 필요 없다.

Tablestore의 VPC 접근은 SDK 인증을 대체하지 않는다. 네트워크와 RAM 권한을 모두 설정한다. 실제 기본 리전과 구매 가능 옵션은 생성 화면을 기준으로 확정한다.

완료 조건: 연결한 VPC와 함수 역할에서 테스트 행을 쓰고 읽을 수 있다.

### 3단계: OSS 웹 버킷

1. `对象存储 OSS → Bucket列表 → 创建Bucket`에서 상하이 버킷을 만든다.
2. Standard 저장소와 비공개 ACL을 선택한다. 해당 리전에서 지원하면 ZRS를 우선 검토한다.
3. 버전 관리를 켜고 이전 객체 버전의 보존·정리 기준을 정한다.
4. 최초 `out`의 **내용물**을 버킷 루트에 올린다. `out` 폴더 자체가 한 단계 더 생기지 않도록 한다.
5. HTML·JS·CSS·JSON·TXT·MP4·글꼴의 Content-Type을 확인한다. MP4는 `video/mp4`로 제공하고 강제 첨부 다운로드 헤더를 적용하지 않는다.
6. 정적 홈페이지의 기본 문서 기능에 의존하지 않는다. 이 구성은 ESA에서 `/index.html` 등 실제 객체 경로로 내부 재작성한다.

완료 조건: 권한을 가진 도구로 `index.html`, `privacy/index.html`, 영상 객체와 산출물을 확인할 수 있다. 버킷을 공개 읽기로 바꾸지 않는다.

### 4단계: DirectMail

1. `邮件推送 DirectMail → 发信域名`에서 `notify.pnpline.cn`을 추가한다. 기존 회사 이메일 도메인의 MX를 덮어쓰지 않는다.
2. 콘솔이 제시하는 소유권·SPF·DKIM·DMARC·MX 등의 레코드를 현재 권한 있는 DNS에 추가한다. 필요한 레코드는 해당 계정 화면의 값을 따른다.
3. 발신 주소를 등록·검증하고 테스트 수신처로 메일을 보낸다.
4. 문의 내용과 연락 이메일을 받을 운영 업무용 메일함을 확정한다. 메일함의 저장 위치와 접근 범위를 실제 공개 정책에 반영한다.

구현은 항저우 DirectMail의 공개 API 주소 `dm.aliyuncs.com`을 사용한다.

완료 조건: 테스트 메일을 실제 수신하고 발신 인증 결과를 확인한다.

### 5단계: Function Compute

1. `函数计算 FC → 函数管理 → 函数列表 → 创建函数`에서 상하이를 선택한다.
2. 문의 API는 **Web函数**로 만든다. Node.js 20 이상을 사용할 수 있는 사용자 지정 런타임에서 `node server.cjs`를 시작 명령으로 지정한다.
3. HTTP 서버는 `0.0.0.0:9000`으로 수신하고 콘솔의 수신 포트도 9000으로 맞춘다. 기존 프런트엔드 개발 서버의 127.0.0.1 바인딩을 복사하지 않는다.
4. 초기 검토값은 0.5 vCPU·1 GiB, 요청 타임아웃 15초, 예약 인스턴스 0이다. 실제 선택 가능한 사양과 저장 지연을 확인하여 조정한다. SDK 호출에는 이보다 짧은 개별 타임아웃을 둔다.
5. VPC 접근을 허용하고 앞서 만든 VPC·vSwitch·보안 그룹을 지정한다. 여러 vSwitch를 사용하도록 설정할 수 있으면 적용한다.
6. DirectMail 등 공개 API 접근이 필요하면 `允许函数默认网卡访问公网`을 켠다. 이 구성의 비GPU 함수는 VPC로 DB에 연결하면서 FC 기본 네트워크로 인터넷에 접근할 수 있어, 고정 출구 IP가 필요하지 않은 초기에는 NAT Gateway를 추가할 필요가 없다.
7. ESA에서 들어와야 하므로 함수의 진입을 `仅允许指定VPC调用函数`로 제한하지 않는다. DB로 나가는 VPC 설정과 인터넷에서 들어오는 API 설정을 구분한다.
8. 실행 RAM 역할과 SLS 로그를 연결한다. 원문 요청 본문·이메일·원본 인증값은 로그에 남기지 않는다.
9. HTTP 트리거는 POST·OPTIONS를 허용한다. 방문자 로그인은 없지만 아래의 서버 측 원본 인증을 반드시 구현한다.
10. 버전을 발행하고 `prod` 별칭으로 연결한다. 도메인은 `$LATEST` 대신 검증한 버전을 가리키게 한다.
11. 알림용 이벤트 함수는 관리형 Node.js 런타임에서 `notify.handler`로 지정하고 1분 간격의 정기 트리거를 연결한다.

FC 환경 변수는 [구현 및 배포 설정](../functions/inquiry/README.ko.md)에서 함수별로 확인한다.

```dotenv
INQUIRY_ORIGINS=https://pnpline.cn
OTS_ENDPOINT=<콘솔의 VPC Endpoint>
OTS_INSTANCE=<실제 인스턴스 이름>
OTS_TABLE=inquiries
INQUIRY_ORIGIN_TOKEN=<별도 생성한 서버 간 인증값>
INQUIRY_CONSENT_VERSION=<공개한 정책 버전>
DM_RECIPIENT=<검수 또는 운영 수신자>
DM_SENDER=<검증한 발신 주소>
```

### 6단계: FC 원본 도메인과 인증

1. FC의 `自定义域名`에 `fc-origin.pnpline.cn`을 등록한다.
2. `/v1/inquiries`를 문의 함수의 `prod` 별칭에 매핑한다.
3. 이 도메인용 인증서를 FC에 설정하고 HTTPS를 사용한다.
4. 현재 DNS에 `fc-origin`을 FC 콘솔이 안내하는 대상에 CNAME으로 연결한다. 이 레코드는 ESA 프록시 대상에서 제외한다.
5. 사용자 입력과 별개인 `X-Pnpline-Origin-Token` 헤더를 FC 코드에서 검증한다. 잘못된 값은 403으로 차단한다. 값은 `INQUIRY_ORIGIN_TOKEN`과 일치해야 한다.
6. 가능하면 HTTP 트리거의 기본 공개 URL을 비활성화한다. 공식 문서에 따르면 이 설정은 사용자 지정 도메인 접근과 별개다. 원본 사용자 지정 도메인에도 인증 검사를 계속 적용한다.
7. 테스트 클라이언트에서만 원본 인증 헤더를 넣어 저장·중복·오류 응답을 확인한다. 해당 값을 웹 코드나 공개 문서에 기록하지 않는다.

외부 방문자는 이 비밀값을 알 필요가 없다. ESA가 API를 원본으로 전달할 때 추가한다. 이는 로그인 인증이 아니라 ESA 원본 우회 방지이며, 폼 자체의 스팸 방어와 요청 제한은 별도로 필요하다.

### 7단계: ESA 사이트·DNS

1. `边缘安全加速 ESA → 站点管理 → 新增站点`에서 `pnpline.cn`을 추가한다.
2. 중국 본토 가속 영역을 선택한다. 해외 방문도 서비스 대상이면 본토가 포함된 Global 영역을 검토한다.
3. **NS接入**를 기본안으로 선택한다. 실제 필요한 요청 헤더 변환·재작성·요청 제한 규칙 수를 기준으로 요금제를 결정한다. 기존 CDN 흐름과 요금제를 중복 구매하지 않는다.
4. 기존 A·CNAME·MX·TXT·CAA·검증용 레코드를 옮긴다. 특히 `fc-origin`, 기존 회사 이메일, DirectMail 레코드를 확인한다.
5. 대표 도메인 `@`는 원본 유형 OSS로 설정하고 웹 버킷의 **외부 Endpoint**를 선택한다. ESA 원본에 OSS VPC·내부 Endpoint를 넣지 않는다.
6. 비공개 원본 접근은 OSS 모드의 STS 임시 토큰을 우선 사용한다. 최초 기본 권한이 같은 계정의 OSS 버킷 전체 읽기를 포함할 수 있으므로 실제 부여 범위를 확인하고, 웹 버킷과 문의·내부 파일을 분리한다.
7. `www`에도 웹 원본을 연결하고 호스트가 www이면 대표 도메인으로 301을 반환하도록 설정한다.
8. `api`는 원본 도메인을 `fc-origin.pnpline.cn`으로 지정해 프록시를 켠다. 원본 프로토콜 HTTPS, 원본 Host와 TLS SNI는 `fc-origin.pnpline.cn`으로 맞춘다. FC 원본을 api 자체로 지정하지 않는다.
9. `SSL/TLS → 边缘证书`에서 대표·www·api에 유효한 인증서를 준비한다. 자동 발급이 활성 DNS를 요구한다면 기존 인증서 업로드 또는 콘솔의 검증 순서로 HTTPS 중단을 피한다.
10. 아래 라우팅·캐시·보안 규칙을 설정한다.
11. 도메인 등록기관에서 NS를 ESA가 안내한 값으로 바꾼다. DNS를 다른 업체로 옮기는 작업이므로 도메인 소유권 이전과 구분한다.
12. NS·인증서·원본 연결의 실제 응답을 확인한다. 기존 서비스가 있으면 이전 NS·레코드와 기존 원본을 유지한다. DNS 복구도 TTL 때문에 즉시 끝난다고 가정하지 않는다.

### 8단계: ESA 라우팅과 캐시 규칙

`规则 → 转换规则 → 重写URL`에서 다음과 같이 설정한다. HTTP 리디렉션과 원본 요청 경로만 바꾸는 내부 재작성을 구분한다.

| 호스트·요청 | 처리 | 주의점 |
|---|---|---|
| www의 모든 경로 | `https://pnpline.cn`의 같은 경로·쿼리로 301 | 반복 리디렉션 방지 |
| 대표 `/privacy` | `/privacy/`로 301 | canonical과 일치 |
| 대표 `/` | 원본 경로 `/index.html`로 내부 재작성 | 주소창은 `/` 유지 |
| 대표 `/privacy/` | 원본 경로 `/privacy/index.html`로 내부 재작성 | 주소창은 `/privacy/` 유지 |
| 대표 `/_next/*`, `/assets/*`, `/fonts/*`, 라우트 데이터·TXT | 요청한 객체로 전달 | 포괄적인 홈 재작성 금지 |
| 존재하지 않는 경로 | 정상 404 유지 | 홈으로 200 응답을 반환하지 않음 |
| API 호스트 | FC 원본으로 전달 | 웹사이트 HTML 재작성 규칙에서 제외 |

비공개 OSS의 기본 홈페이지 자동 변환에 의존하지 않는다. 이 구성에서는 ESA 내부 재작성이 실제 객체 이름을 지정한다. 사용자에게 친숙한 404 본문까지 제공하려면 사용 요금제의 오류 응답 기능을 검증하여 추가하되, 상태 코드 404를 유지한다.

캐시 정책 초기 제안:

| 대상 | 브라우저 | ESA |
|---|---|---|
| HTML·Next.js 라우트 데이터·TXT | `no-cache`로 재검증 | 명시적으로 캐시 허용, TTL 60초부터 검토 |
| 해시가 붙은 `/_next/static/*` | 1년·immutable | 1년 |
| 버전이 포함된 영상·이미지·글꼴 | 1년·immutable | 1년 |
| 파일명 버전이 없는 공개 자산 | 짧은 TTL 또는 재검증 | 변경 주기에 맞춤 |
| robots·sitemap | 짧은 TTL | 60초, 공개 전환 시 갱신 |
| API와 오류 응답 | `no-store` | API 호스트 캐시 우회, 오류 장기 캐시 금지 |

캐시 설정은 실제 응답 헤더·규칙 우선순위·반복 요청에서 확인한다. 확장자 기본값만으로 HTML 캐시가 켜졌다고 판단하지 않는다.

추가 설정:

- `规则 → 回源规则`에서 MP4에 Range 분할 원본 요청을 켠다. `206`, `Content-Range`, 전체 파일 길이를 검사한다.
- 텍스트에 Brotli·gzip을 적용하고 MP4에 불필요한 재압축을 하지 않는다.
- API 호스트에 요청 헤더 추가 규칙을 설정해 `X-Pnpline-Origin-Token`을 서버 비밀값으로 **덮어쓴다**. 이미 존재하는 헤더만 변경하는 동작으로 설정하지 않는다.
- 실제 IP가 필요하면 ESA가 확인한 `ip.src` 값으로 전용 헤더를 덮어쓴다. 클라이언트가 보낸 `X-Forwarded-For`를 그대로 신뢰하지 않는다.
- IP별 요청 제한은 API 호스트와 문의 경로에만 적용한다. 초기 후보는 IP당 분당 10회이며 회사·학교의 공유 IP에서 오탐이 없는지 측정한다. 이메일별 제한은 서버의 공유 저장소에서 처리하고 각 FC 인스턴스 메모리에만 두지 않는다.
- API의 브라우저 교차 출처 설정은 허용 Origin `https://pnpline.cn`, 메서드 POST·OPTIONS, 헤더 Content-Type·Idempotency-Key로 제한한다. 쿠키가 필요 없으므로 credentials를 사용하지 않는다.
- OPTIONS가 저장을 수행하지 않게 하고, 정상 preflight는 204로 응답한다. CORS는 봇이나 직접 HTTP 요청의 인증을 대신하지 않는다.
- API 요청에 HTML 슬라이더 챌린지를 무조건 적용하지 않는다. JSON 대신 HTML을 받는 상황을 검수한다.

## 7. 업로드·검수·공개

### 최초 업로드와 후속 배포

1. 로컬에서 타입 검사·정적 빌드·스키마·폼 계약 검사를 통과한다.
2. 배포 ID, 빌드 시각, 소스 버전, 공개 환경 변수, FC 버전과 별칭을 기록한다. 비밀값은 기록하지 않는다.
3. 새 해시 자산과 버전이 바뀐 영상·이미지를 먼저 업로드한다.
4. 해당 빌드의 HTML·라우트 데이터·TXT·robots·sitemap을 올린다.
5. 이전 `/_next/static` 파일을 즉시 삭제하지 않는다. 기존 페이지가 참조하는 파일이 유효해야 한다. 내용이 바뀐 장기 캐시 자산에는 새 파일명을 사용한다.
6. ESA에서 HTML·라우트 데이터·robots·sitemap을 갱신한다. 자산 전체 갱신은 기본 작업으로 삼지 않는다.
7. 실제 응답과 접수를 확인한다. OSS 객체 여러 개의 덮어쓰기는 원자적 배포가 아니므로, 페이지·라우트 데이터 교체 중 잠깐의 버전 차이가 허용되는 저트래픽 시간에 수행한다.

OSS 업로드 도구는 콘솔 또는 `ossutil`을 사용할 수 있다. 업로드 대상은 `out` 산출물로 고정하고, 초기에는 원격 삭제를 동반하는 동기화 옵션을 사용하지 않는다.

### 출시 검증표

| 영역 | 실행할 확인 | 완료 조건 |
|---|---|---|
| 기본 페이지 | `/`, `/privacy/`, 새로고침·직접 진입 | HTTPS 200, 콘텐츠와 메타데이터 일치 |
| 주소 | www, `/privacy`, canonical | 301 대상 정확, 루프 없음, `/privacy/`로 통일 |
| 미공개 경로 | 무작위 경로와 보류 경로 | 홈 200이 아닌 404 |
| 정적 산출물 | JS·CSS·글꼴·라우트 데이터 | 누락 없음, 올바른 Content-Type |
| 영상 | 순방향·역방향 빠른 스크롤 | Range 206, 화면 정지·검은 화면 여부 확인 |
| 모바일 | iPhone·Android·WeChat, 절약·모션 감소 | 대표 이미지·본문·문의 접근 가능 |
| 접수 | 동의 포함 정상 입력 | DB에 1행, 접수번호 일치, 알림 수신 |
| 중복·통신 | 같은 키 재전송, 응답 유실 후 재시도 | 문의 중복 없음, 같은 접수번호 |
| 오류 | DB 거부, 메일 실패, 잘못된 필드, 제한 | 성공 오표시 없음, 입력 유지, 알림 실패 재처리 |
| 원본 우회 | 원본 도메인에 인증 없이 POST | 403, DB 저장 없음 |
| CORS | 정상·비허용 Origin, OPTIONS | 허용 출처만 브라우저 호출, OPTIONS 저장 없음 |
| 보안·로그 | 프런트 산출물과 로그 점검 | 서버 비밀값·이메일 원문 노출 없음 |
| 지역 | 베이징·상하이·광저우·청두, 3대 통신사 | 페이지·영상·API 결과와 지연 분리 기록 |
| 복구 | 이전 HTML·라우트 데이터와 FC 버전 복원 | 이전 화면·접수로 복귀 가능 |

PowerShell 환경에서는 alias 혼동을 피하도록 `curl.exe`로 헤더를 검사할 수 있다. 아래 GET은 응답 헤더만 출력하고 Range 본문은 버린다.

```powershell
curl.exe -I https://pnpline.cn/
curl.exe -I https://pnpline.cn/privacy/
curl.exe -I https://www.pnpline.cn/privacy/
curl.exe -I https://pnpline.cn/not-a-real-page
curl.exe -sS -D - -o NUL -H 'Range: bytes=0-1023' https://pnpline.cn/assets/video/hero-b-v002-720p.mp4
curl.exe -i -X OPTIONS https://api.pnpline.cn/v1/inquiries -H 'Origin: https://pnpline.cn' -H 'Access-Control-Request-Method: POST' -H 'Access-Control-Request-Headers: content-type,idempotency-key'
```

영상 GET은 `206 Partial Content`, `Content-Range: bytes 0-1023/<전체 길이>`와 해당 구간의 응답을 기대한다. 기존 `preload=auto`가 실제 얼마를 받는지는 개발자 도구에서 별도로 측정한다.

검수 종료 후 `SITE_INDEXING=allow`로 재빌드하고 HTML·robots·sitemap을 갱신한다. 사이트 본문·폼·개인정보·확정 등록번호·canonical·sitemap까지 확인한 뒤 검색엔진에 제출한다.

## 8. 장애 처리와 원복

| 상황 | 우선 확인 | 복구 |
|---|---|---|
| 홈만 403 | 비공개 원본 권한, `/` 내부 재작성 | `/index.html` 객체와 규칙 수정 |
| API 403 | 원본 인증값, Host, CORS, FC 진입 제한 | ESA·FC 설정을 대조하고 인증 헤더 노출 없이 확인 |
| API 502·504 | TLS SNI·인증서·기동 포트·타임아웃 | 0.0.0.0:9000, 원본 도메인과 함수 로그 확인 |
| DB 접속 실패 | VPC Endpoint·바인딩·RAM·보안 그룹 | 해당 연결과 권한 수정, 접수 성공 표시 금지 |
| 메일만 실패 | 발신 인증·리전·수신처·권한 | 문의 기록 유지, 알림 상태를 재처리 |
| 화면 배포 회귀 | 배포 ID·객체 버전·이전 정적 자산 | 이전 HTML·라우트 데이터를 세트로 복원하고 ESA 갱신 |
| API 배포 회귀 | `prod` 별칭과 DB 호환성 | 별칭을 이전 함수 버전으로 되돌림 |
| DNS·TLS 전환 장애 | NS·MX·CAA·인증서·원본 | 이전 설정으로 복원, DNS 캐시 전파 중 관측 지속 |

웹 파일 원복과 문의 DB 복원은 분리한다. 화면 원복 때문에 이미 접수한 문의를 삭제하거나 과거 스냅샷으로 덮어쓰지 않는다. API 스키마는 이전 프런트엔드와 함께 동작하도록 확장하고, 필드 삭제는 별도 단계로 진행한다.

초기 기본 리전은 하나이므로 리전 전체 장애에서 API가 계속 동작한다고 보장하지 않는다. OSS 버전 관리는 다른 리전의 재해 복구 사본을 대신하지 않는다. 지역 장애의 복구 시간·허용 데이터 유실 기준이 확정되면 다른 본토 리전에 사이트 아티팩트와 문의 데이터의 복구 사본을 마련하고 복원 훈련을 추가한다.

## 9. 운영 알림과 확정할 값

초기에는 API 5xx·저장 실패·알림 재시도 소진·오래된 pending·함수 제한·인증서 만료·예산 및 ESA 전송량을 알린다. 비용 임계값의 예시는 예산의 50%·80%·100%다. 자동 전송량 제한은 홈페이지나 문의 기능을 느리게 할 수 있으므로, 기본 운영 정책은 먼저 알림을 받고 원인을 판단하는 방식으로 둔다.

배포 전에 확정해야 할 값은 최종 앱 경로, 실제 ICP 등록번호, Aliyun 계정·리전별 생성 가능 옵션, 버킷 이름, 운영 수신 이메일, 개인정보 정책 버전·보관·국외 처리 조건, 월 방문·다운로드량과 예산, 백업·복구 목표다. 법인과 ICP 완료 여부는 이미 확인되었으므로 다시 신청하는 작업을 기본 일정에 넣지 않는다.

## 10. 공식 자료와 저장소 근거

아래 자료는 2026-11-06에 확인했다. 메뉴·규칙 개수·가격·구매 가능한 사양은 실행 시 해당 계정 콘솔에서도 확인한다.

- [Next.js 공식 정적 export 설명](https://nextjs.org/docs/app/guides/static-exports): `output: 'export'`와 정적 호스팅 제한. 설치 버전의 번들 문서도 대조했다.
- [ESA 도메인 접속](https://help.aliyun.com/zh/edge-security-acceleration/esa/getting-started/add-your-website-to-esa): NS 접속과 인증서 준비.
- [ESA 비공개 OSS 원본](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/use-esa-to-accelerate-oss-resource-access): STS 원본 접근과 기본 권한 범위.
- [ESA DNS 원본 유형](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/introduction-of-dns-related-parameters): OSS 외부 Endpoint 사용.
- [비공개 OSS 기본 홈페이지 충돌](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/after-enabling-the-private-oss-bucket-to-return-to-the-source-the-you-are-forbidden-to-list-buckets-error-is-prompted-when-accessing-the-domain-name): 실제 객체 경로로 재작성할 필요.
- [ESA URL·헤더 변환](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/conversion-rules-overview//): 내부 URL 재작성.
- [ESA 요청 헤더 추가](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/modifying-inbound-request-header): 원본 인증·실제 IP 헤더 덮어쓰기.
- [ESA 원본 규칙](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/back-to-source-rule-overview/): Range 분할 원본 요청.
- [ESA 기본 캐시 정책](https://help.aliyun.com/zh/edge-security-acceleration/esa/user-guide/default-cache-rule): HTML·상태 코드·원본 헤더와 규칙의 동작.
- [FC Web 함수 생성](https://help.aliyun.com/zh/functioncompute/creating-a-web-function): 시작 명령·수신 포트·리소스 설정.
- [FC 네트워크](https://help.aliyun.com/zh/functioncompute/configure-network-settings): VPC·인터넷 출구·진입 설정의 차이.
- [FC HTTP 트리거](https://help.aliyun.com/zh/functioncompute/configure-an-http-trigger-for-a-function-and-invoke-the-function-by-using-http-requests): 메서드·기본 공개 URL 비활성화.
- [FC 사용자 지정 도메인](https://help.aliyun.com/zh/functioncompute/configure-custom-domain-names): 라우팅과 HTTPS.
- [Tablestore 생성](https://help.aliyun.com/zh/tablestore/table-store-service/product-overview/getting-started/): VCU와 네트워크 초기 설정.
- [Tablestore 네트워크](https://help.aliyun.com/zh/tablestore/table-store-service/network-security-management): VPC 접근 제어.
- [Tablestore 조건부 갱신](https://help.aliyun.com/zh/tablestore/table-store-service/conditional-update): 중복 저장 방지.
- [Tablestore Stream과 FC](https://help.aliyun.com/zh/tablestore/table-store-service/use-function-compute): 같은 리전의 변경 이벤트 후속 처리.
- [DirectMail 발신 도메인](https://help.aliyun.com/zh/direct-mail/user-guide/how-to-configure-sending-domain-names): 발신 전용 하위 도메인과 DNS 검증.

저장소의 주요 근거는 `output/pnpline-web-zh/next.config.ts`, `app/quote-inquiry.tsx`, `app/site-data.ts`, `app/privacy/page.tsx`, `app/structured-data.ts`, `app/landing.tsx`, `app/hero-journey.ts`, `qa.cjs`, `schema-render-check.cjs`, `schema-check.cjs`이며, 내부 운영 결정은 `docs/wayfinder/tickets/technical-delivery-architecture.md`를 참고했다. 이 문서는 제안 절차이며 배포 성공이나 전환 빌드 통과의 증거가 아니다.
