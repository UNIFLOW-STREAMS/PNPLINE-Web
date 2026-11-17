# iOttie 중국 소개 페이지

`www.iottie.cn`에 올릴 간체 중국어 정적 홈페이지입니다. iOttie 한국 사이트의 로고와 Treker 이미지를 사용해 새로 디자인했습니다. 아리윈 안내에 적힌 **粤ICP备19055173号**를 페이지 최하단에 표시하고 [공업정보화부 조회 사이트](https://beian.miit.gov.cn/)에 연결했습니다.

## 미리보기와 패키지 생성

이 폴더에서 아래 명령을 실행합니다. Node.js 이외의 빌드 의존성은 없습니다.

```powershell
node .\build.mjs
npx --yes http-server@14.1.1 dist -a 127.0.0.1 -p 4324 -c-1
```

브라우저에서 `http://127.0.0.1:4324/`을 엽니다. 이 미리보기 서버는 Safari가 사용하는 바이트 범위 요청을 지원합니다. 배포할 때는 `dist` **안의 파일과 하위 폴더**를 웹 문서 루트에 올립니다.

```powershell
Compress-Archive -Path .\dist\* -DestinationPath .\iottie-cn-deploy.zip -Force
```

## 영상 파일

한국 홈페이지에 표시된 영상은 iOttie 공식 채널의 Treker 제품 영상입니다. 현재 배포본에는 대표 이미지와 영상이 모두 포함되어 있으며, 페이지를 표시하고 영상을 재생하는 데 외부 서버가 필요하지 않습니다.

히어로에는 원본에서 기내 설치 장면 약 10초를 골라 만든 무음 영상이 반복 재생됩니다. 페이지에 들어올 때 화면 폭과 터치 입력에 맞춰 MP4 한 개를 선택합니다. 모션 감소가 켜져 있거나 자동재생이 제한되면 대표 이미지와 재생 버튼을 표시합니다.

| 화면 | 해상도 | 파일 크기 |
| --- | --- | --- |
| PC | 1600×900 (16:9) | 1.85 MB |
| 태블릿 | 1024×768 (4:3) | 1.04 MB |
| 모바일 | 576×720 (4:5) | 0.58 MB |

세 버전 모두 H.264 MP4, 8비트 YUV 4:2:0이며 초기 재생에 필요한 메타데이터가 파일 앞에 있습니다. `media/hero`의 인코딩 파일과 대표 이미지를 다시 생성하려면 FFmpeg를 설치하고 아래 명령을 실행합니다. 전체 60초 영상은 `media/treker-original.mp4`에 있으며, 페이지의 ‘观看完整短片’ 버튼을 선택하면 재생됩니다. [iOttie 공식 영상](https://www.youtube.com/watch?v=317mckYkLb4)

```powershell
node .\encode-hero.mjs
node .\build.mjs
```

## 아리윈 재제출 전 확인

1. 기존 연결 대상과 운영 권한을 확인합니다. 2026-11-16 작업 환경에서 공용 DNS는 `www.iottie.cn`과 `iottie.cn`의 A 레코드로 `52.83.232.132`를 반환했습니다. DNS가 응답했지만 홈페이지 HTTP 응답은 확인되지 않았습니다. 아리윈 고지에 따라 기존 접속 경로를 복구하거나, 이전한다면 새 호스팅에서 먼저 응답을 검증하고 DNS를 전환합니다.
2. 실제 운영 호스트에 패키지를 업로드하고, 루트 `/`에서 `index.html`을 응답하도록 설정합니다. HTTPS 인증서가 정상인 경우 `http://www.iottie.cn/`은 `https://www.iottie.cn/`으로 리디렉션할 수 있습니다. 고지에 명시된 HTTP 주소에서 인증 또는 차단 화면 없이 최종 홈페이지까지 도달하고, HTTPS 최종 응답이 200인지 확인합니다. MP4는 `Content-Type: video/mp4`로 제공하고 `Range: bytes=0-31` 요청이 `206 Partial Content`와 올바른 `Content-Range`를 반환하는지 확인합니다. [Apple의 Safari 영상 제공 안내](https://developer.apple.com/documentation/webkit/delivering-video-content-for-safari)
3. 중국 본토 네트워크에서 실제 주소를 열어 로고, 본문, 이미지와 푸터를 확인합니다. 맨 아래에 **粤ICP备19055173号**가 정확히 표시되고 클릭하면 `https://beian.miit.gov.cn/`으로 연결되는지 검사합니다.
4. 공개 접속을 확인한 뒤 아리윈 안내에 따라备案 신청을 다시 제출합니다. 실제 확인된 홈페이지 주소로 바꾸는 경우 신청서의 홈페이지 URL도 맞춥니다.

참고: [아리윈의 접속 장애 안내](https://help.aliyun.com/zh/dws/support/how-do-i-troubleshoot-the-failures-to-access-a-website-by-using-its-domain-name), [아리윈의备案 반려 사유 안내](https://help.aliyun.com/zh/icp-filing/basic-icp-service/support/for-the-record-to-dismiss-the-faq).

## 출처

- [iOttie 한국 홈페이지](https://www.iottie.co.kr/): [로고](https://cdn.imweb.me/thumbnail/20250812/80ab4953c9a6a.png), [아이콘](https://cdn.imweb.me/thumbnail/20220919/f723551fc5dde.png), [영상 대표 이미지](https://cdn.imweb.me/thumbnail/20251104/ecd9f898b50c5.png).
- [한국 Treker 제품 페이지](https://www.iottie.co.kr/shop_view/?idx=21): [기내 제품 사진](https://cdn.imweb.me/thumbnail/20260318/94033dd1bd1ed.png).
- [글로벌 Treker 제품 정보](https://www.iottie.com/product/treker-magnetic-airplane-mount/), [브랜드 소개](https://www.iottie.com/about-us-5/), [글로벌 고객 지원](https://www.iottie.com/contact-us/): 제품 설명, 브랜드 정보, 문의처를 확인했습니다.
