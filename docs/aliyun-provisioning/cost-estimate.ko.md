# PNPLINE Aliyun 비용 검토 — 2026-11-06

사용자 요청으로 클라우드 생성을 중단했다. 충전 및 비용 승인 후 재개한다.

## 실제 작업 상태

- 생성 완료: 리소스 그룹 `pnpline-prod`, ID `rg-aek6txm27ofwctq`. 리소스 그룹 자체는 무료다.
- OSS 미개통. 개통 화면의 초기 결제 표시액은 ¥0.00. Buy Now 클릭은 자동 승인 검토에서 차단됐으며 개통되지 않았다.
- FC 미개통. 개통 화면에서 약관/SLA 동의 및 CDT 자동 개통 안내를 확인했다.
- VPC/서브넷, 버킷, 함수, DB, ESA 사이트는 생성하지 않았다. DNS는 변경하지 않았다.
- 생성 증빙: `resource-group.jpg`.

## 산정 조건

확정 청구서가 아닌 운영 예산이다. 방문량이 주어지지 않아 방문당 20~35MB 두 경우를 계산했다. 데스크톱 영상 31,910,714 bytes, 모바일 영상 12,104,681 bytes, public 전체 62,968,581 bytes를 로컬에서 확인했다. 빌드 파일, 영상 Range 재전송 및 브라우저 캐시 때문에 실제 방문당 전송량은 달라진다.

- 상하이 원본, 중국 전국 ESA 기본형 사이트 1개.
- 월 30일, 웹 객체/이전 버전/소규모 백업 합계 평균 5GB 이내.
- 문의 1,000건, 담당자 알림 1,000통/월.
- OSS 원본 전송량은 방문자 전송량의 10%로 가정. 실측값이 아니다.
- FC 문의/알림 함수 최소 인스턴스 0, 예약/상주 없음.
- DB는 CU 사용량 과금 및 예약 읽기/쓰기 0을 전제로 예산을 잡음. 계정에서 해당 모드 생성 가능 여부 및 상하이 단가 미확정. VCU 예약 인스턴스 구매 가격과 혼용하지 않음.
- 로그 5GB/월, 30일 이내 보관. 새 사용자 무료 체험 및 기간 한정 할인은 절감액으로 반영하지 않음.

## 비용 구성

| 항목 | 요율 또는 예산 | 비고 |
|---|---|---|
| ESA 기본형 | ¥9.9/월, 50GB, 초과 ¥0.198/GB | 첫 자연월 포함량은 남은 시간에 따라 일할 발급 |
| OSS 저장 | 평균 5GB에 약 ¥0.75/월 예산 | ZRS ¥0.15/GB/월을 보수적 참고값으로 사용. 공식 사례는 2024년 단가이므로 실제 상하이 주문 가격 재확인 필요 |
| OSS 원본 전송 | ¥0.15/GB 참고값 | ESA 전송료와 별도. 콘솔의 원본 과금 분류 확인 필요 |
| OSS 요청 | ¥0.01/만 GET·PUT 참고값 | 이 예산에서는 ¥2/월 배정. Range 분할 및 캐시 재검증도 요청 발생 |
| FC 두 함수 | ¥15/월 배정 | 정가 ¥0.00011/CU. 호출/리소스 사용이 있는 함수의 시간당 최소 ¥0.01 규칙. 2개×720시간×¥0.01=¥14.4는 계산량이 최소요금 이하일 때의 보수적 예시이며 모든 워크로드의 상한이 아님 |
| Tablestore | ¥5/월 임시 예산 | 확정 단가 아님. CU 모드 소량 문의 전제. VCU 예약을 선택하면 별도 재산정 필요 |
| SLS | 5GB×¥0.4=¥2/월 | 쓰기량 과금, 30일 이내 보관 조건. 별도 처리/외부 읽기는 제외 |
| DirectMail | 1,000통×¥0.002=¥2/월 | 무료 총 2,000통(하루 최대 200통)은 계산에서 제외. 여러 수신자는 각각 계산 |
| FC 인터넷/CDT | 조건 충족 시 ¥0 | 중국 본토 공유 무료량 20GB/월. 초과 첫 구간 ¥0.8/GB. ESA/OSS 전송에는 이 무료량을 적용하지 않음 |
| VPC·vSwitch·RAM | ¥0 | NAT/EIP/유료 KMS는 사용하지 않는 초기 구성 |
| DNS·HTTPS | 무료 DNS/ESA 무료 edge 인증서/무료 ACME origin 인증서 방식으로 ¥0 목표 | 유료 인증서 주문 제외. FC 원본 인증서 별도 설치·갱신 필요 |
| 기본 모니터링 | 무료 범위 사용 | 유료 지역별 능동 탐지, 전화 알림은 별도 |

영상 전송 이외 비용은 위 소량 조건에서 월 ¥30을 예산으로 둔다. DB 등 미확정 항목을 포함하므로 확정 합계가 아니다.

## 월 예산 모델

ESA = 9.9 + max(0, 월 전송GB - 50) × 0.198

OSS 원본 = 월 전송GB × 10% × 0.15

합계 예산 = ESA + OSS 원본 + 기타 ¥30

| 월 방문 | 전송량(20~35MB/방문) | 월 합계 예산 |
|---|---|---|
| 1,000회 | 20~35GB | 약 ¥40~41 |
| 10,000회 | 200~350GB | 약 ¥73~105 |
| 50,000회 | 1,000~1,750GB | 약 ¥243~403 |
| 100,000회 | 2,000~3,500GB | 약 ¥456~776 |

캐시가 차가운 첫 배포, 자주 하는 전체 캐시 삭제, 영상 재전송이 증가하면 원본 전송량이 커진다. 위 10% 가정은 보장이 아니다. 월 10만회·35MB에서 원본 전송이 방문자 전송량과 같아지면 모델상 합계 약 ¥1,248까지 증가한다.

권장 최초 충전액: 배포 검수와 월 1만 방문 이내 초기 운영은 ¥300. 처음부터 월 10만 방문/광고 집행이면 ¥1,500을 여유 예산으로 고려한다. 충전액은 즉시 소비되는 구매 금액도, 자동 요금 상한도 아니다. 초기 ESA 선결제는 기본형 1개월 ¥9.9를 기준으로 한다.

기존 도메인 연장료, 유료 인증서, 별도 WAF/API Gateway/NAT/EIP, 교차 리전 재해복구, 관리형 DB 백업, 지역별 통신사 유료 모니터링은 이 초기 구성의 주문에 포함하지 않는다. 추가하면 재산정한다. 도메인 보유/연장 청구액은 미확인이다.

## 공식 근거

- ESA 요금: https://help.aliyun.com/zh/edge-security-acceleration/esa/product-overview/basic-package-fee
- ESA 기능/기본형 규칙: https://help.aliyun.com/zh/edge-security-acceleration/esa/product-overview/package-function-comparison
- OSS 사례 및 단가 기준일: https://help.aliyun.com/zh/oss/billing-examples
- OSS 원본 전송: https://help.aliyun.com/zh/oss/traffic-fees
- FC 정가·시간당 최소 과금: https://help.aliyun.com/zh/functioncompute/billing-overview-of-fc
- Tablestore CU: https://help.aliyun.com/zh/tablestore/table-store-service/product-overview/billable-items-and-billing-methods/
- SLS: https://help.aliyun.com/zh/sls/billing-examples
- 메일: https://help.aliyun.com/zh/direct-mail/billing-methods
- CDT: https://help.aliyun.com/zh/cdt/internet-data-transfers/
- VPC: https://help.aliyun.com/zh/vpc/vpc-product-billing
- 리소스 그룹: https://help.aliyun.com/zh/resource-management/product-overview/billing-methods
- 기본 모니터링: https://help.aliyun.com/zh/cms/cloudmonitor-1-0/product-overview/free-quota
