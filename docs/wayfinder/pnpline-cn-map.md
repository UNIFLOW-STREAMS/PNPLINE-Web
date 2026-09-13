# PNPLINE 중국어 웹사이트 제작 명세 Wayfinder Map

## Destination

중국어권 고객을 대상으로 하는 PNPLINE 웹사이트 32개 페이지의 제작 명세를 확정한다. 명세에는 중국어 콘텐츠, 중국 시장용 SEO, 페이지 IA, 디자인 시스템, 홈 인터랙션, 기술 구조, 운영 정보가 들어갈 자리, 개인정보·규제 검수, QA와 공개 기준을 포함한다. 이 문서가 확정되면 개발자가 바로 스테이징 사이트를 구현할 수 있어야 한다.

## Notes

- 현재 단계는 제작 전 의사결정과 명세 확정 단계다. Wayfinder 지도가 끝나기 전에는 전체 사이트 구현과 유료 미디어 생성을 시작하지 않는다.
- 중국어 사이트는 기존 sitemap과 IA의 32개 페이지를 기준으로 한다.
- 홈은 `scroll-world` 방식의 인터랙티브 물류 세계를 사용하되, 첫 화면 이후에는 일반적인 증빙·서비스·요금·FAQ·견적 흐름을 제공한다.
- 중국어 상담 인력, WeChat, 공개 요율, 창고 운영 수치와 사진은 운영 데이터가 확정되기 전까지 컴포넌트와 CMS 필드로 분리한다.
- 실제 창고·자격·서비스 증빙은 확인된 실자료만 사용한다. 자료가 부족해 AI로 재구성한 경우에는 실제 증빙이 아니라 설명용 이미지라는 점을 명확히 표시한다.
- 관련 기준: `scroll-world`, `site-architecture`, `grilling`, `domain-modeling`, `fluent-korean`.

## Decisions so far

- [제작 명세의 목표와 범위](tickets/production-spec-scope.md): 32개 전 페이지를 개발 전달 가능한 전체 제작 명세로 만든다.
- [출시 순서와 홈 경험 구조](tickets/release-and-home-experience.md): 10개 핵심 페이지와 개인정보 페이지를 먼저 공개 가능한 MVP로 만들고, 나머지 페이지를 단계적으로 추가한다. 홈은 5~7개 장면의 scroll-world 뒤에 증빙·요금·FAQ·견적 영역을 둔다.
- [중국어 브랜드 시스템과 시각 자료 경계](tickets/brand-and-visual-evidence.md): PNPLINE 로고와 핵심 색상은 유지하고 중국어권 디지털 사용성을 위한 별도 시스템을 만든다. 생성 비주얼은 홈의 상징적 물류 세계와 전환 장면에 사용한다. 증빙 영역에서는 실제 자료를 우선하며, AI 재구성 자료는 실제 자료처럼 제시하지 않는다.
- [홈 미술 방향](tickets/scroll-world-art-direction.md): 정밀 산업형 미니어처 디오라마를 채택한다. 첨부 이미지는 참고자료로만 사용하고, 최종 스타일을 고정하는 지시나 공개 자산으로 취급하지 않는다.
- [홈 카메라 이동 방식](tickets/scroll-world-camera-and-journey.md): 카메라는 항구에서 운송, 미국 입고, 보관, 주문 처리, 출고로 이어지는 하나의 세계를 한 방향으로 계속 전진한다.
- [홈 물류 여정](tickets/scroll-world-camera-and-journey.md): 중국 상품 출발, 국제 운송, 미국 도착 및 입고 준비, 창고 입고·보관, 주문 처리·피킹·패킹, FBA 입고 또는 최종 배송 출고의 6단계로 구성한다.
- [모바일 미디어 전략](tickets/scroll-world-mobile-and-budget.md): 데스크톱용 가로 영상과 모바일용 세로 영상을 각각 제작한다. 전체 생성 전에 대표 장면으로 품질과 비용을 시험한다.
- [미디어 제작 승인 방식](tickets/scroll-world-mobile-and-budget.md): 대표 장면 1개 시험, 2개 장면 파일럿, 전체 6개 장면 제작 순서로 단계별 승인한다. 실제 지출 상한은 별도로 확정한다.
- [중국어 콘텐츠와 운영 정보 승인](tickets/content-and-evidence-approval.md): SEO 초안, 중국어 검수, PNPLINE 사실 확인, 법무·규제 확인의 4단계로 승인한다.
- [기술 구현 기반](tickets/technical-delivery-architecture.md): Next.js와 TypeScript를 사용해 32개 라우트, 중국어 SEO, scroll-world, 견적 폼, 운영 데이터 필드를 하나의 프로젝트에서 관리한다.
- [콘텐츠와 운영 데이터 관리](tickets/technical-delivery-architecture.md): 운영 데이터는 JSON, 페이지 카피와 SEO는 Markdown 또는 코드로 관리한다. JSON 수정 후 정적 사이트를 재빌드·배포하고, 향후 운영 필요가 커지면 Headless CMS를 도입한다.
- [배포 검수 방식](tickets/technical-delivery-architecture.md): 별도 스테이징 환경 없이 개발자 로컬에서 검수한 뒤 운영 배포한다. 실제 URL에서 검수할 수 없는 위험은 캡처 또는 임시 검수 빌드 절차로 보완한다.
- [견적 폼 리드 처리](tickets/technical-delivery-architecture.md): 제출 즉시 담당자 이메일로 알리고, 후속 관리에 필요한 최소 정보만 보호된 저장소에 보관한다. 보관 기간과 삭제 기준을 명시한다.
- [견적 리드 저장 기술](tickets/technical-delivery-architecture.md): Next.js 서버리스 API와 관리형 데이터베이스를 사용해 폼 제출, 이메일 알림, 최소 리드 저장을 처리한다.
- [견적 리드 보관 정책](tickets/technical-delivery-architecture.md): 마지막 상담 후 12개월까지 보관하고, 이후 자동 삭제 또는 익명화한다. 사용자 삭제 요청은 별도로 처리한다. 최종 공개 문구는 법무 검토 후 확정한다.
- [견적 폼 스팸 방지](tickets/technical-delivery-architecture.md): CAPTCHA 없이 서버 검증, 숨은 허니팟, IP·이메일별 요청 제한을 적용한다.
- [scroll-world 접근성 fallback](tickets/technical-delivery-architecture.md): 모션 감소 설정이나 영상 재생 실패 시 6개 대표 이미지를 순서대로 보여 주고, 서비스·견적 영역으로 건너뛸 수 있게 한다.
- [scroll-world 미디어 로딩](tickets/technical-delivery-architecture.md): 첫 장면을 먼저 표시하고 현재 장면과 다음 장면만 프리로드한다. 전체 미디어를 한꺼번에 내려받지 않는다.
- [증빙 자료 공개 기준](tickets/content-and-evidence-approval.md): 확인된 실제 자료, 자료 기반 AI 재구성 이미지, 공개하지 않는 미확인 정보를 구분한다. 재구성 이미지는 概念示意 또는 资料重构示意로 표시한다.
- [증빙 자료 출처 관리](tickets/content-and-evidence-approval.md): 자료별 출처, 확인일, 사용 권한, 적용 페이지, 승인 상태를 별도 JSON manifest로 관리하고 승인된 자료만 페이지에 불러온다.
- [증빙 상태 화면 표시](tickets/content-and-evidence-approval.md): 실제 자료에는 实景资料 또는 已核实资料, AI 재구성 자료에는 概念示意 또는 资料重构示意 라벨을 이미지 가까이에 표시한다.
- [중국어 개인정보 동의 구조](tickets/content-and-evidence-approval.md): 견적 폼에 필수 동의 체크박스와 핵심 안내를 제공하고, 상세 개인정보 페이지로 연결한다. 최종 중국어 문구는 법무 검토 후 확정한다.
- [중국어 사이트 언어 범위](tickets/content-and-evidence-approval.md): 중국어판은 간체 중국어 단일 언어로 제공하고, 한국어 사이트는 별도로 유지한다.
- [중국어판 도메인](tickets/technical-delivery-architecture.md): 중국어판의 대표 주소는 https://syndy.cn이다. https://www.syndy.cn은 대표 주소로 301 리디렉션하며, 두 주소 모두 SSL을 적용한다. 검색엔진 등록, sitemap, canonical은 대표 주소 하나로 통일한다.
- [검색엔진 색인 공개 시점](tickets/technical-delivery-architecture.md): 콘텐츠·개인정보·운영 데이터·증빙·canonical·sitemap·robots.txt 검수가 끝난 뒤에만 색인을 허용한다. 그 전에는 noindex를 적용한다.
- [sitemap·robots.txt 생성](tickets/technical-delivery-architecture.md): Next.js에서 공개 상태와 canonical을 기준으로 자동 생성하고, noindex·숨김 페이지는 제외한다.
- [운영 공개 승인 기준](tickets/technical-delivery-architecture.md): 32개 라우트, 데스크톱·모바일, scroll-world와 fallback, 폼·이메일·리드 저장, 개인정보 동의, 증빙 라벨, canonical·sitemap·robots.txt, 성능·접근성·주요 브라우저를 종합 검수한다.
- [운영 호스팅 방향](tickets/technical-delivery-architecture.md): Aliyun을 중심으로 정적 사이트, CDN, DNS, SSL, 리디렉션을 구성하고, 폼 API와 데이터베이스도 중국어판 접속 환경에 맞춰 배치한다.
- [폼 API·리드 데이터베이스 위치](tickets/technical-delivery-architecture.md): 중국 내 리전의 서버리스 API와 관리형 데이터베이스를 우선 검토한다. 실제 배포 전 개인정보·보안·ICP 조건을 확인한다.
- [견적 이메일 알림](tickets/technical-delivery-architecture.md): 관리형 트랜잭션 이메일 서비스로 발송하고, 도메인 인증·재시도·발송 로그를 포함한다.
- [견적 알림 수신자 관리](tickets/technical-delivery-architecture.md): 담당자 이메일은 JSON 또는 환경 변수로 분리한다. 담당자 확정 전에는 알림을 비활성화하거나 내부 테스트 주소만 사용한다.
- [임시 검수 빌드 공유](tickets/technical-delivery-architecture.md): 접근 제한이 있는 임시 검수 URL을 사용하고, 검수 후 URL을 폐기한다. 검수 빌드는 검색엔진 색인을 차단한다.

## Not yet specified

- 접근성·모션 감소 동작, 데스크톱·모바일 영상 생성의 실제 지출 상한과 재생 성능 기준
- 실제 운영 증빙의 목록, 공개 가능한 정보와 비공개 정보
- 실제 미디어 제작 도구·비용 조사, 실제 운영 증빙 목록, 개인정보·규제 문구의 법무 확정, Aliyun 배포 조건 확인
- 개인정보 공개 문구와 견적 폼 동의 문구의 법무 확정, Aliyun 배포 위치에 맞춘 canonical·리디렉션 설정

## Out of scope

- 이 지도에서 사이트 전체를 바로 구현하는 일
- 미술 방향·카메라·예산 승인 전 전체 영상과 이미지를 생성하는 일
- 확인되지 않은 주소, 창고 수치, 가격, 배송 기한, 통관·규제 책임을 사실처럼 공개하는 일

## Ticket order

1. [모바일 전략과 미디어 예산](tickets/scroll-world-mobile-and-budget.md)
2. [기술 전달 구조의 남은 항목](tickets/technical-delivery-architecture.md)
