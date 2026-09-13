# 기술 전달 구조

## Type

`wayfinder:research`

## Status

In progress

## Research findings

현재 레포에는 package.json, 프론트엔드 소스, Next.js·Vite 설정, 배포 설정이 없다. 문서와 이미지·영상 참고자료를 중심으로 구성되어 있어 기존 앱 프레임워크를 유지해야 하는 제약은 확인되지 않았다.

## Question

32개 중국어 페이지와 scroll-world, CMS 필드, 견적 폼을 어떤 기술 구조로 구현할 것인가?

## Recommendation

초기에는 CMS를 도입하지 않고 파일 기반으로 운영한다. 주소, 창고 면적, 보관 가격, 배송 기간, WeChat QR 코드, 상담 가능 시간, 견적 회신 SLA처럼 변경되는 운영 데이터는 JSON 파일에 저장한다. 페이지 카피와 SEO 메타데이터는 Markdown 또는 코드로 버전 관리하고, JSON을 수정하면 정적 사이트를 다시 빌드·배포해 모든 페이지에 반영한다. JSON Schema 또는 빌드 단계 검증으로 필수 항목과 데이터 형식을 확인한다. 운영자가 개발자 없이 수정해야 하거나 승인·변경 이력·다국어 콘텐츠 관리가 필요해지는 시점에는 Headless CMS로 확장한다.

## Decision so far

Next.js와 TypeScript를 사용한다. 32개 라우트의 SEO와 메타데이터, scroll-world 인터랙션, 견적 폼과 운영 데이터 필드를 하나의 프로젝트 안에서 관리한다. 운영 데이터는 JSON을 단일 기준으로 사용하고, 페이지 카피와 SEO는 Markdown 또는 코드로 관리한다.

## Decision

초기 출시에서는 파일 기반 운영을 채택한다. 운영 데이터는 JSON 파일에 저장하고, 페이지 카피와 SEO는 Markdown 또는 코드로 버전 관리한다. JSON 변경 후 정적 사이트를 재빌드·배포하는 흐름을 표준으로 삼는다. Headless CMS는 운영 담당자가 직접 편집해야 하거나 콘텐츠 승인·변경 이력·다국어 관리가 필요한 시점에 도입한다.

## Deployment decision

별도 스테이징 환경 없이 개발자 로컬에서 검수한 뒤 운영 배포한다. 중국어 검수자와 운영 담당자가 실제 URL에서 확인할 수 없는 위험은 운영 배포 전 캡처 또는 임시 검수 빌드를 공유하는 QA 절차로 보완한다.

## Lead handling decision

견적 폼 제출 즉시 담당자 이메일로 알리고, 후속 관리에 필요한 최소 정보만 보호된 저장소에 보관한다. 수집 항목은 이름, 회사, 이메일, 문의 내용처럼 상담에 필요한 범위로 제한하고, 보관 기간과 삭제 기준을 개인정보 문서에 명시한다.

## Lead storage decision

Next.js 서버리스 API로 폼 제출을 처리하고, 관리형 데이터베이스에 최소 리드 정보를 저장한다. 서버리스 API는 입력 검증, 개인정보 동의 확인, 이메일 알림, 저장 실패 처리와 기본적인 스팸 방어를 담당한다. 데이터베이스 접근은 운영 담당자에게 필요한 범위로 제한한다.

## Retention decision

리드 데이터는 마지막 상담 후 12개월까지 보관한다. 이후 자동 삭제 또는 익명화하며, 사용자의 삭제 요청은 별도 절차로 먼저 처리한다. 이 기간과 삭제 방식은 공개 전 중국어 개인정보 처리 문구와 함께 법무 검토를 받는다.

## Chinese domain decision

중국어판의 대표 주소는 https://syndy.cn이다. URL에는 /cn/ 경로를 추가하지 않는다. https://www.syndy.cn으로 접속하면 https://syndy.cn으로 301 리디렉션한다. 두 도메인 모두 SSL 인증서를 적용하고, 검색엔진 등록, sitemap, canonical, Open Graph URL과 공유 URL은 대표 주소인 https://syndy.cn을 기준으로 생성한다. 리디렉션은 Aliyun DNS, CDN 또는 웹 서버 중 실제 배포 위치에서 설정한다.

## Indexing decision

콘텐츠, 개인정보 문구, 운영 데이터, 증빙 상태, canonical, sitemap, robots.txt 검수가 끝난 뒤에만 검색엔진 색인을 허용한다. 그 전에는 noindex를 적용한다. 검수 완료 후에는 sitemap과 robots.txt를 운영 주소 기준으로 교체하고 색인을 요청한다.

## Sitemap and robots decision

Next.js에서 공개 상태와 canonical을 기준으로 sitemap과 robots.txt를 자동 생성한다. noindex 페이지, 숨김 페이지, 운영 데이터가 확정되지 않아 공개하지 않는 경로는 sitemap에서 제외한다. 대표 주소는 https://syndy.cn을 사용한다.

## Launch QA decision

운영 공개 전 종합 체크리스트를 통과해야 한다. 32개 라우트, 데스크톱·모바일, scroll-world와 정적 fallback, 폼·이메일·리드 저장, 개인정보 동의, 실제 자료·AI 재구성 라벨, canonical·sitemap·robots.txt, 성능·접근성·주요 브라우저를 모두 확인한다.

## Hosting decision

Aliyun을 중심으로 정적 사이트, CDN, DNS, SSL, 리디렉션을 구성한다. 견적 폼 API와 리드 데이터베이스도 중국어판 접속 환경과 개인정보 처리 조건을 확인한 뒤 Aliyun 또는 연결 가능한 관리형 서비스에 배치한다.

## Backend location decision

중국 내 리전의 서버리스 API와 관리형 데이터베이스를 우선 검토한다. API는 폼 입력 검증, 동의 확인, 이메일 알림, 데이터 저장과 삭제 작업을 담당한다. 실제 서비스 선택과 리전은 배포 전 개인정보·보안·ICP 조건을 확인한 뒤 확정한다.

## Email notification decision

관리형 트랜잭션 이메일 서비스를 사용한다. Aliyun DirectMail 또는 호환 가능한 이메일 API를 우선 검토하며, 발신 도메인 인증, 발송 재시도, 오류 로그와 실패 알림을 포함한다.

## Notification recipient decision

담당자 이메일 주소는 JSON 또는 환경 변수로 분리한다. 담당자가 확정되기 전에는 이메일 알림을 비활성화하거나 내부 테스트 주소만 사용한다. 실제 수신자 주소를 페이지 코드에 직접 넣지 않는다.

## Review build decision

상시 스테이징 대신 접근 제한이 있는 임시 검수 URL을 사용한다. 검수 빌드는 noindex와 접근 제어를 적용하고, 검수가 끝나면 URL을 폐기한다. 검수자는 실제 데스크톱·모바일 화면과 폼·영상 동작을 확인할 수 있어야 한다.
## Spam protection decision

CAPTCHA 없이 서버 검증, 숨은 허니팟, IP·이메일별 요청 제한을 적용한다. 서버는 필수값과 개인정보 동의 여부를 확인하고, 비정상 입력과 반복 요청을 차단하거나 보류한다. 스팸이 증가할 경우 추가 방어 수단을 별도로 검토한다.

## Motion fallback decision

사용자가 모션 감소를 설정했거나 영상 재생에 실패하면 6개 대표 이미지를 순서대로 보여 준다. 장면 설명과 진행 상태를 제공하고, 사용자가 서비스·견적 영역으로 바로 이동할 수 있게 한다.

## Media loading decision

첫 장면의 대표 이미지를 우선 표시하고, 사용자의 현재 위치와 다음 이동에 필요한 장면만 프리로드한다. 전체 영상 체인을 초기 진입 시 한꺼번에 다운로드하지 않는다. 프리로드에 실패하면 해당 장면의 대표 이미지와 일반 콘텐츠를 사용한다.

## Blocked by

현재 레포의 앱 구조와 배포 환경 조사
