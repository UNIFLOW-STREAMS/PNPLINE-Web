# PNPLINE 문의 API 배포

사이트가 `POST /v1/inquiries`로 문의를 보내면 상하이 Tablestore에 문의와 알림 대기 상태를 한 행에 저장한다. 저장에 성공한 뒤 접수번호를 반환한다. 같은 요청 키와 같은 내용으로 재시도하면 기존 번호를 돌려주고, 같은 키로 내용을 바꾸면 409를 반환한다.

별도 Function Compute 함수가 매분 발송할 행을 찾는다. 문의의 전체 입력값과 고객 이메일은 PNPLINE 로고를 넣은 HTML로 `contact@inquiry.pnpline.cn`에만 발송한다. 중국 국내 SMS에는 문의 유형과 접수번호만 전달한다. 접수 화면, 메일, 문자에는 같은 32자리 접수번호를 사용한다. 고객에게는 자동 알림을 발송하지 않는다. 문의 본문, 이메일 및 수신 휴대폰 번호는 애플리케이션 로그에 남기지 않는다.

## 콘솔에서 만들 순서

1. **Tablestore**: 기존 `pnpline-prod` 그룹의 상하이 인스턴스에 `inquiries` 테이블을 만든다. 기본키 `inquiryId`는 STRING, 최대 버전 수는 1이다. 테이블 전체에 고정 TTL을 설정하지 않는다. 상하이 FC와 VPC를 연결하고, Tablestore 콘솔에 표시되는 VPC 접속 주소를 사용한다. 이번 구성에는 Stream이 필요 없다.
2. **메일함**: [기업메일 콘솔](https://alimail.console.aliyun.com/)에서 `inquiry.pnpline.cn`을 연결해 `contact` 수신함을 만든다. 검증과 MX 레코드는 공급자가 안내한 값으로 서브도메인에만 추가한다. `pnpline.cn`의 기존 MX와 `notify.pnpline.cn`의 발신 인증 레코드는 유지한다. DirectMail은 수신함이 준비된 뒤 항저우에서 인증된 발신 주소로 `dm.aliyuncs.com`을 호출한다.
3. **국내 SMS**: [SMS 콘솔](https://dysms.console.aliyun.com/overview)에서 서비스를 개통하고 발신 서명과 통지 템플릿을 승인받는다. 템플릿 문구: `PNPLINE网站收到新咨询，类型：${type}，受理编号：${number}。` `type`은 중국어 분류명(예: 物流询价), `number`는 영숫자 32자리 접수번호(변수 속성: 其他号码)다. [통지 템플릿 규격](https://help.aliyun.com/zh/sms/user-guide/notification-template-specifications)을 따른다. 임시 테스트 번호는 테스트 전송에서만 사용하고 운영 함수 환경에는 넣지 않는다.
4. **RAM**: 두 FC 함수에 별도 실행 역할을 지정한다. 접수 함수는 해당 Tablestore 테이블의 `ots:PutRow`, `ots:GetRow`만 사용한다. 알림 함수는 같은 테이블의 `ots:GetRange`, `ots:UpdateRow` 및 발송 API `dm:SingleSendMail`, `dysms:SendSms`만 사용한다. 함수의 임시 자격증명을 사용하므로 AccessKey를 환경 변수에 넣지 않는다.
5. **FC**: 이 디렉터리를 코드 패키지로 만들어 아래 두 함수에 업로드한다. 둘 다 상하이에 둔다. 접수 함수는 [Web 함수](https://help.aliyun.com/zh/functioncompute/creating-a-web-function), 알림 함수는 [Node.js 이벤트 함수](https://help.aliyun.com/zh/functioncompute/request-handlers)로 만든다. 테스트할 동안 합성 문의만 제출한다.
6. **ESA**: API 호스트의 `/v1/inquiries`에서 POST와 OPTIONS를 FC HTTPS 원본으로 전달하고, 해당 경로의 캐시를 끈다. 클라이언트가 보낸 동명의 헤더를 그대로 전달하지 말고 ESA가 `X-Pnpline-Origin-Token`을 서버 설정값으로 **덮어써서** 원본에 보낸다. 사용 중인 요금제에서 규칙 적용이 가능한지 확인한다. POST에 IP 기준 요청 제한을 적용하고, 원본 직접 호출이 403인지 확인한다. 임시 미리보기 호스트를 테스트에 쓰면 테스트 기간에만 허용 목록에 추가한다.
7. **웹사이트**: API, 수신 메일함, 문자, 개인정보 안내를 검수한 뒤 `output/pnpline-web-framer-zh-cn-v1/.env.example`의 공개 설정을 빌드 시점에 지정하고 OSS 정적 파일을 다시 빌드한다. API URL은 예를 들어 `https://api.pnpline.cn/v1/inquiries`다. 개인정보 안내 버전은 FC와 일치시킨다. API URL을 비우면 미리보기 폼을 유지한다.

| FC 함수 | 설정 |
| --- | --- |
| `pnpline-inquiry-api` | [사용자 지정 런타임 Debian 10](https://help.aliyun.com/zh/functioncompute/custom-runtime/)을 선택하면 Node.js 20 내장 경로를 사용해 시작 명령을 `/var/fc/lang/nodejs20/bin/node server.cjs`로 설정할 수 있다. Node.js 20 이상이 제공되는 다른 런타임도 가능하다. 수신 포트 9000, 타임아웃 15초. HTTP 트리거 또는 사용자 지정 원본 도메인에서 POST·OPTIONS를 전달한다. |
| `pnpline-inquiry-notify` | 관리형 Node.js 20 이상, 핸들러 `notify.handler`, 타임아웃 60초. 공개 HTTP 트리거 없이 [定时触发器](https://help.aliyun.com/zh/functioncompute/time-triggers)를 1분 간격으로 설정한다. Tablestore VPC와 DirectMail 및 SMS 공개 API에 접속할 수 있어야 한다. |

| 환경 변수 | 범위 | 예시 또는 의미 |
| --- | --- | --- |
| `OTS_ENDPOINT` | 두 함수 | Tablestore 콘솔의 HTTPS VPC 접속 주소 |
| `OTS_INSTANCE` | 두 함수 | 실제 인스턴스 이름 |
| `OTS_TABLE` | 두 함수 | `inquiries` |
| `INQUIRY_ORIGINS` | 접수 | `https://pnpline.cn`. 여러 개는 쉼표로 구분하며 경로와 끝 슬래시는 제외 |
| `INQUIRY_ORIGIN_TOKEN` | 접수 | 32바이트 이상 무작위 비밀값. ESA 원본 요청 헤더와 동일하게 설정 |
| `INQUIRY_CONSENT_VERSION` | 접수 | 공개하는 개인정보 안내의 실제 버전 |
| `DM_SENDER` | 알림 | 항저우 DirectMail에서 검증한 발신 주소 |
| `INQUIRY_SMS_PHONE` | 알림 | 운영 담당자의 중국 내 11자리 번호. 서버에만 설정 |
| `INQUIRY_SMS_SIGN` | 알림 | 국내 통지 SMS에 승인된 발신 서명 |
| `INQUIRY_SMS_TEMPLATE` | 알림 | 승인된 통지 템플릿 코드 |

Linux 또는 FC와 같은 환경에서 `npm ci --omit=dev` 후 `server.cjs`, `core.cjs`, `inquiry-email.cjs`, `notification-format.cjs`, `aliyun.cjs`, `notify.js`, `package.json`, `package-lock.json`, `node_modules/`를 ZIP 루트에 넣는다. 로컬 검증은 `npm ci`와 `npm test`로 실행한다.

## 운영 확인

- 접수 API는 개인정보 안내 버전과 동의를 검사하고, 수락한 버전과 서버 UTC 시각을 기록한다. 이전 알림 경로로 접수된 행을 새 경로에서 자동 발송하지 않는다. 운영 빌드 전에 실제 처리 지역과 접근 범위, 권리 행사 절차, DB와 메일함 보관·삭제 기준을 고지에 반영한다.
- 합성 문의로 201, 같은 내용의 재시도에서 같은 번호로 200, 같은 키에 다른 내용으로 409가 오는지 확인한다. 메일함과 테스트 휴대폰에서 접수번호가 일치하고, 문자에는 두 변수만 들어 있는지 확인한다. API 발송 수락과 실제 수신은 따로 확인한다.
- 메일과 문자 중 실패한 채널만 1분, 5분, 30분 후 재시도한다. 잠금 만료 후 다른 실행이 다시 처리할 수 있다. 제공업체가 요청을 수락한 직후 결과 기록에 실패하면 같은 접수번호의 중복 알림이 생길 수 있다.
- SLS에서 `inquiry_mail_failed`, `inquiry_sms_failed`, 채널별 `_worker_error`와 `_not_configured`, `inquiry_notification_worker_error`를 감시한다. 실패한 행은 보존한다. 수동 재발송이 필요하면 해당 채널의 상태만 초기화한다. 메일은 `notificationStatus/notificationAttempts/nextNotificationAt/notificationRevision`, 문자는 `smsStatus/smsAttempts/nextSmsAt/smsRevision`을 각각 `pending/0/현재 UTC ISO 시각/새 UUID`로 설정한다.
- 사이트의 개인정보 안내는 검수용 초안이다. 운영 전에 처리 주체, 담당 업무용 메일함, 문의 권리 요청 주소, 보관 기준을 확정한다. 현재 코드에는 접수 시각을 기준으로 초기 `lastConsultedAt`과 `deleteAfter`를 기록한다. 운영 담당자가 마지막 상담 후 두 값을 갱신하고, 만료된 DB 행과 업무 메일 사본을 정리하는 절차를 공개 전 마련한다. 자동 삭제 작업은 이 패키지에 포함되어 있지 않다.
