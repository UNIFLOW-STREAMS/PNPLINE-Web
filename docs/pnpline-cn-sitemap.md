# PNPLINE 중국어 사이트맵

기준일: 2026-09-13  
대상 도메인: `https://www.pnpline.cn`  
근거: [중국어 사이트 콘텐츠 인벤토리](chinese-localization-content-inventory.md), [간체 중국어 로컬라이징 및 바이두 SEO 전략](chinese-market-localization-seo-strategy.md)  
페이지별 구조: [중국어 사이트 페이지별 IA](pnpline-cn-page-ia.md)

## 사이트 구조 원칙

`pnpline.cn`은 한국어 사이트의 경로를 번역해 옮긴 하위 언어 사이트가 아닙니다. 중국 크로스보더 셀러가 서비스명으로 검색하고 비교하는 과정을 기준으로, `해외창고`, `국제운송`, `통관`, `플랫폼 솔루션`을 독립된 상위 주제로 구성합니다.

모든 공개 페이지는 자기 자신을 canonical URL로 사용하고, `https://www.pnpline.cn`의 단일 URL만 색인합니다. `.co.kr`, `.com`과의 `hreflang` 연결은 사용하지 않습니다. URL은 영문 슬러그와 소문자, 마지막 슬래시(`/`) 규칙으로 통일합니다.

## 사용자 탐색 구조

```text
首页 /
├─ 美国海外仓 /warehouse/
│  ├─ 一件代发 /warehouse/dropship/
│  ├─ FBA中转·贴标 /warehouse/fba/
│  ├─ 退货换标·检品 /warehouse/returns/
│  ├─ B2B分销配送 /warehouse/b2b/
│  └─ 仓储与库存 /warehouse/storage/
├─ 头程运输 /freight/
│  ├─ 海运整柜 /freight/fcl/
│  ├─ 海运拼箱 /freight/lcl/
│  ├─ 空运·快船 /freight/air/
│  └─ 美国卡派·尾程 /freight/trucking/
├─ 清关与合规 /customs/
│  ├─ IOR进口商服务 /customs/ior/
│  ├─ 关税与HS归类 /customs/tariff/
│  └─ FDA·FCC注册 /customs/fda-fcc/
├─ 平台方案
│  ├─ 亚马逊 /solutions/amazon/
│  ├─ TikTok Shop美区 /solutions/tiktok/
│  ├─ Shopify独立站 /solutions/shopify/
│  └─ 沃尔玛 /solutions/walmart/
├─ 系统
│  ├─ WMS库存系统 /system/wms/
│  └─ API·ERP对接 /system/api/
├─ 价格与报价 /pricing/
├─ 关于我们
│  ├─ 公司简介 /about/
│  ├─ 自营仓库实景 /about/facilities/
│  └─ 资质与合规 /about/compliance/
├─ 资讯 /news/
│  ├─ 2026 IOR新规解读 /news/ior-2026/
│  └─ T86与De Minimis政策解读 /news/de-minimis/
├─ 联系我们 /contact/
├─ 合作伙伴 /partner/ [주 내비게이션 제외]
└─ 隐私政策 /privacy/ [푸터 전용]
```

## 주 내비게이션

| 순서 | 메뉴 | URL | 하위 메뉴 |
| --- | --- | --- | --- |
| 1 | 美国海外仓 | `/warehouse/` | 一件代发, FBA中转·贴标, 退货换标·检品, B2B分销配送, 仓储与库存 |
| 2 | 头程运输 | `/freight/` | 海运整柜, 海运拼箱, 空运·快船, 美国卡派·尾程 |
| 3 | 清关与合规 | `/customs/` | IOR进口商服务, 关税与HS归类, FDA·FCC注册 |
| 4 | 平台方案 | `/solutions/amazon/` | 亚马逊, TikTok Shop美区, Shopify独立站, 沃尔玛 |
| 5 | 系统 | `/system/wms/` | WMS库存系统, API·ERP对接 |
| 6 | 价格与报价 | `/pricing/` | 없음 |
| 7 | 关于我们 | `/about/` | 自营仓库实景, 资质与合规 |
| 8 | 资讯 | `/news/` | 없음 |
| 9 | 联系我们 | `/contact/` | 없음 |

`合作伙伴`은 중국 현지 포워더에게만 필요한 별도 랜딩이므로 주 내비게이션에 넣지 않습니다. `隐私政策`은 푸터와 견적 폼 동의 문구에서만 연결합니다.

## URL·색인 명세

아래 `변경 빈도`와 `우선순위`는 검색엔진의 보장값이 아니라 XML 사이트맵 생성 기준입니다. 실제 `lastmod`는 각 페이지가 배포 또는 수정된 날짜로 자동 생성해야 하며, 이 문서의 작성일을 일괄 삽입하면 안 됩니다.

| URL | 중국어 제목 | 단계 | 색인 | 변경 빈도 | 우선순위 |
| --- | --- | --- | --- | --- | --- |
| `/` | 首页 | MVP | index | weekly | 1.0 |
| `/warehouse/` | 美国海外仓 | P1 | index | monthly | 0.9 |
| `/warehouse/dropship/` | 一件代发 | MVP | index | monthly | 0.9 |
| `/warehouse/fba/` | FBA中转·贴标 | MVP | index | monthly | 0.9 |
| `/warehouse/returns/` | 退货换标·检品 | P1 | index | monthly | 0.8 |
| `/warehouse/b2b/` | B2B分销配送 | P2 | index | monthly | 0.7 |
| `/warehouse/storage/` | 仓储与库存 | MVP | index | monthly | 0.8 |
| `/freight/` | 头程运输 | P1 | index | monthly | 0.8 |
| `/freight/fcl/` | 海运整柜 | MVP | index | monthly | 0.8 |
| `/freight/lcl/` | 海运拼箱 | MVP | index | monthly | 0.8 |
| `/freight/air/` | 空运·快船 | P2 | index | monthly | 0.7 |
| `/freight/trucking/` | 美国卡派·尾程 | P2 | index | monthly | 0.7 |
| `/customs/` | 清关与合规 | P1 | index | monthly | 0.8 |
| `/customs/ior/` | IOR进口商服务 | MVP | index | weekly | 0.9 |
| `/customs/tariff/` | 关税与HS归类 | P2 | index | monthly | 0.7 |
| `/customs/fda-fcc/` | FDA·FCC注册 | P2 | index | monthly | 0.7 |
| `/solutions/amazon/` | 亚马逊 | P1 | index | monthly | 0.8 |
| `/solutions/tiktok/` | TikTok Shop美区 | P1 | index | monthly | 0.8 |
| `/solutions/shopify/` | Shopify独立站 | P2 | index | monthly | 0.7 |
| `/solutions/walmart/` | 沃尔玛 | P2 | index | monthly | 0.7 |
| `/system/wms/` | WMS库存系统 | P2 | index | monthly | 0.7 |
| `/system/api/` | API·ERP对接 | P2 | index | monthly | 0.6 |
| `/pricing/` | 价格与报价 | MVP | index | weekly | 0.9 |
| `/about/` | 关于我们 | P1 | index | monthly | 0.7 |
| `/about/facilities/` | 自营仓库实景 | MVP | index | monthly | 0.9 |
| `/about/compliance/` | 资质与合规 | P2 | index | monthly | 0.7 |
| `/news/` | 资讯 | P1 | index | weekly | 0.8 |
| `/news/ior-2026/` | 2026 IOR新规解读 | P1 | index | weekly | 0.8 |
| `/news/de-minimis/` | T86与De Minimis政策解读 | P1 | index | weekly | 0.8 |
| `/contact/` | 联系我们 | MVP | index | monthly | 0.8 |
| `/partner/` | 合作伙伴 | P2 | index | monthly | 0.4 |
| `/privacy/` | 隐私政策 | MVP | index | yearly | 0.2 |

## 콘텐츠 허브 규칙

`/news/`의 개별 정책 해설, 사례, FAQ 글은 공개 후 모두 XML 사이트맵에 포함합니다. 다음 조건을 충족하지 못한 초안, 태그·분류 목록, 내부 검색 결과, 빈 페이지, 중복된 인쇄용 URL은 `noindex`로 설정하고 사이트맵에서 제외합니다.

1. 제목, 작성자 또는 검수 담당자, 게시일, 최종 수정일이 있습니다.
2. 정책·관세·통관 글은 미국 통관팀이 사실을 검수했습니다.
3. 고유한 본문과 최소 한 개 이상의 관련 서비스 페이지 내부 링크가 있습니다.
4. FAQ는 해당 서비스 페이지와 중복되지 않는 독립 질문·답변을 제공합니다.

## 배포용 XML 생성 규칙

배포 시에는 실제로 공개되고 canonical 상태인 URL만 `https://www.pnpline.cn` 기준으로 출력합니다. 정적 페이지와 뉴스 글을 하나의 `sitemap.xml`에 포함해도 되지만, URL이 늘어나면 아래처럼 분리합니다.

```text
/sitemap.xml
├─ /sitemap-pages.xml
└─ /sitemap-news.xml
```

`/robots.txt`에는 아래 한 줄을 포함합니다.

```text
Sitemap: https://www.pnpline.cn/sitemap.xml
```

XML의 `lastmod`는 콘텐츠 관리 시스템 또는 배포 메타데이터에서 생성합니다. `changefreq`와 `priority`는 이 문서의 값을 기본값으로 사용할 수 있지만, 검색 순위를 직접 올리는 기능으로 취급하지 않습니다.

## MVP 배포 순서

1. 홈, 一件代发, FBA中转·贴标, IOR进口商服务, FCL, LCL, 仓储与库存, 自营仓库实景, 价格与报价, 联系我们을 배포합니다.
2. 각 MVP URL의 canonical, `lang="zh-CN"`, robots 허용 여부, 내부 링크, Organization·Service·FAQPage JSON-LD를 검수합니다.
3. MVP URL만 담은 `sitemap.xml`을 Baidu Webmaster Tools에 제출하고 快速收录 API를 연결합니다.
4. P1·P2 페이지를 공개할 때마다 XML 사이트맵을 갱신합니다.
