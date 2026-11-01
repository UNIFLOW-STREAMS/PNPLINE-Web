# PNPLINE · existing-previz scroll pacing

기존 통합 Blender 장면의 7개 마커를 사용해 장면별 스크롤 거리와 관찰 지점을 구현한 독립 검토 페이지다. 기존 `output/hero-next`는 정적 이미지·서비스 패널 중심이므로 이번 타이밍 검토는 별도 페이지로 제공한다. 원본 Blender나 기존 사이트를 수정하지 않는다.

## 실행

```powershell
cd F:/pnpline-landing/output/scroll-previz-pacing-v001
npm start
```

브라우저: http://127.0.0.1:3096/ . 다른 포트가 필요하면 `$env:PORT = '3097'` 후 실행한다. npm 의존성 없이 Node만으로 페이지를 제공하며, `npm ci`는 자동 검증 도구 설치에만 필요하다.

- 휠·터치·PageDown·Home·End로 탐색한다.
- 상단에서 **장면별 감속 / 선형 비교**를 선택한다. 모드 변경 시 현재 프레임을 유지하도록 스크롤 위치를 변환한다.
- **측정 보기**로 목표·표시 프레임, 매핑 그래프, 현재 구간을 확인한다.
- 아래 7개 장면 버튼은 해당 구간 중앙으로 이동한다.
- 마지막 프레임 뒤에 일반 본문과 설정표가 이어진다.
- `?media=missing`은 다운로드 실패 시 정적 대체를 확인하는 검사 모드다.

## 입력과 적용 범위

`data/source-scene.json`이 작업 시작 시 실제 Blender에서 추출한 파일 해시·CAM_MASTER·마커·990개 카메라 샘플을 기록한다. `data/input-latest-lookdev.json`과 `data/input-latest-previz.json`은 입력 포인터 기록이다. 이번 소스는 lookdev 마스터의 SHA `033d58217379348e4462d5882b0449974cb9242e3bea4f83b1d26c5598613070`이다.

실제 마커: S1=0, S2=75, S3=165, S4=315, S5=465, S6=660, S7=870. 종료는 989다. 문서의 과거 6단계와 구별했다. 과거 `previz-motion-polish-v001/scroll-progress-map.json`은 24fps와 다른 해시의 장면을 기준으로 하므로 수치를 재사용하지 않았다. 2×·3.5×·4× 영상을 현재 원본으로 사용하지 않았다.

현재 장면 전체에 대응하는 검증된 기존 MP4를 찾지 못해 최신 lookdev 마스터를 새로 출력했다. 990개 원본 프레임을 각각 렌더링했다. 원본 카메라와 모든 애니메이션은 같은 소스 시간을 유지한다. 추가 배속·프레임 보간·Blender 키프레임 변경은 없다. 웹 매핑은 영상 전체의 `currentTime`만 변경한다.

## 스크롤과 감속

설정은 `pacing.json`, 엔진은 `app.mjs`, 순수 수학 매핑은 `mapping.mjs`다. 설정의 `scrollVh=1`은 **뷰포트 높이 1배**이며 CSS의 `1vh`와 다르다. 총 13H, 기준 1080px 높이에서 14,040px이다. 고정 영상의 화면 높이와 아래 본문 높이는 별도다.

| 구간 | 프레임 경계 | 거리 | 배정 이유 |
|---|---|---:|---|
| S1 선적 | 0–75 | 1.2H | 안착 관계 인지, 원본의 느린 카메라와 중첩 억제 |
| S2 중국 공개·출항 | 75–165 | 1.6H | 확장된 도시·항만 읽기 |
| S3 해상 운송 | 165–315 | 1.3H | 이동은 간결하게, 미국 공개 전 완화 |
| S4 미국 하역 | 315–465 | 1.9H | 리프트와 트레일러 접점 |
| S5 도크 진입 | 465–660 | 2.3H | 정렬과 문 개방, 원본 정지를 추가 정지로 늘리지 않음 |
| S6 창고 | 660–870 | 3.0H | 피킹·포장·상차에 가장 많은 관찰 거리 |
| S7 출고 | 870–989 | 1.7H | 두 차량 분기를 읽고 본문 연결 |

장면 경계는 공유 앵커이며 구간 소속은 `[start,end)`다. 마지막 989프레임은 포함한다. 영상은 33초이고 마지막 프레임 시작 시각은 989/30=32.9667초다. 그 프레임의 노출 1/30초까지 포함하면 33초가 된다.

scroll-world의 Step 6–8, `scroll`·`linger`의 관찰 거리 개념, Blob 재생, seek 병합, 첫 프레임 poster, 모바일 높이 변화 처리를 적용했다. 단일 연속 영상이므로 여러 clip/connector나 경계 크로스페이드를 추가하지 않았다.

기본 `linger`는 장면 중앙 감속에 한정되므로 실제 동작 프레임에 맞춘 양의 밀도 함수를 사용했다. 감속 구간의 밀도는 `1 + 2*strength*sin²(πu)`다. 장면별 적분을 scrollVh에 맞춘 후 5프레임 간격의 프레임→누적거리 앵커를 만든다. 양의 조화평균 접선을 갖는 PCHIP를 구성하고 역함수를 이분 탐색한다. 한 구간의 독립 ease-in-out으로 경계에서 정지시키지 않는다. `strength`는 스킬의 linger 숫자와 직접 호환되는 값이 아니다.

원본 카메라 중앙 프레임 이동량은 S1~S7 각각 약 0.027 / 0.565 / 1.268 / 0.647 / 0.186 / 0.161 / 0.730 장면 단위다. 서로 다른 축척의 절대 속도 비교에는 한계가 있으나 S1과 도크 정렬의 기존 감속을 재차 강하게 늘리지 않는 근거로 참고했다. 물류 접점의 관찰 효과는 실제 영상과 스크롤 녹화로 함께 검토한다.

목표 프레임에 직접 탐색하며 관성 보간은 추가하지 않는다. 디코딩 중에는 새 seek를 발행하지 않고 마지막 목표만 유지한다. 이산 30fps의 프레임 양자화는 연속 C1 매핑의 수학적 속도와 구별한다. 빠른 입력에서는 디코더가 모든 중간 프레임을 표시할 수 없으며, 입력 종료 후 최신 목표로 복구한다.

## 미디어와 한계

- `assets/previz-source.mp4`: 렌더된 990프레임의 기준 영상, H.264 CRF16/GOP60.
- `assets/previz-scrub.mp4`: 동일 PNG에서 별도로 인코딩한 웹 영상, H.264 CRF20/GOP8.
- 양쪽 모두 1280×720, 30fps, 990프레임, 33초, 무음, yuv420p, faststart. 모든 해시와 크기는 `data/media-manifest.json`에 기록한다.
- Workbench / studio light / AA8 검토용이다. Cycles의 재질 노드·제작 조명·수면·유리 투명도·DOF를 검증한 최종 영상이 아니다.
- 렌더 속도를 위해 정적 강체 메시를 메모리에서 묶었다. 오브젝트 재질 슬롯과 평가된 정적 modifier를 사용하고 움직이는 부모는 유지한다. 이 합치기는 셰이딩 법선 차이를 만들 수 있다. `.blend`를 저장하지 않는다.
- 모바일에서는 가로 영상을 `contain`으로 전체 표시한다. 세로 전용 영상이나 임의 중앙 크롭을 제공하지 않는다. 작은 화면의 레터박스와 세부 가독성은 남는 제한이다.
- 실제 iOS Safari·물리 모바일 장치는 미검증이다. Chromium 모바일 에뮬레이션을 실제 기기 검증으로 간주하지 않는다.
- 페이지는 Blob 전체를 로드하므로 초기 전송량은 웹 MP4 크기와 같다. 제작용 검토 페이지이며 운영 성능 예산이나 배포 승인을 의미하지 않는다.

## 재현과 검증

```powershell
# 원본은 읽기만 한다. GPU 렌더 실행은 한 번에 하나를 권장한다.
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --background --factory-startup 'F:/pnpline-landing/hero-section-video/lookdev/hero-material-v001/pnpline-hero-material-v001.blend' -t 8 --python-exit-code 1 --python scripts/render_previz.py -- batch animation *> review/final-render.log
& ./scripts/encode.ps1
npm test
# 별도 터미널에서 npm start를 실행한 상태
npm ci
npm run qa
node scripts/record-scroll.cjs
node scripts/mobile-extra.cjs
python scripts/report.py
```

자동 검증은 설치된 Chrome을 사용한다. Playwright의 녹화 보조 FFmpeg가 없으면 `tools/browsers/ffmpeg-1013/ffmpeg-win64.exe`에 PATH의 FFmpeg를 복사한다. 이 폴더에 현재 사용한 실행 파일을 포함했다. Playwright 코어 버전은 lockfile로 고정한다.

검사 항목은 `review/qa-inventory.md`, 수학 검사는 `review/mapping-verification.json`, 실제 최신 영상의 브라우저 결과는 `review/browser/results.json`이다. `review/fixture`는 렌더 대기 중 구형 33초 영상으로 엔진을 검사한 개발 기록으로, 최신 장면의 시각 검증 자료가 아니다. 최종 판정에는 fixture 결과를 사용하지 않는다.

실제 Chrome 기본 샌드박스 세션이 로컬 주소 접근을 거부해, 로컬 검증 스크립트는 허용된 일반 Chrome 실행 환경에서 수행했다. 운영 배포·외부 메시지 전송·유료 이미지/영상 생성은 하지 않았다.

검토 영상과 측정 요약은 `review/validation.md`를 본다. 변경 범위는 이 폴더에 한정하며, 기존 입력 파일과 사이트는 보존했다.
