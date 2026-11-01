# PNPLINE 33초 · 30fps 모션 v001

기존 v013 카메라 동선과 장면을 유지하고, 원본 12fps·1,393프레임(약116.08초)의 모든 동작을 33초·30fps·990프레임으로 재배치했습니다. main 브랜치의 동일 작업공간에서 제작했습니다.

- 작업본: `pnpline-33s-30fps-v001.blend`
- 전체 영상: `preview/pnpline-33s-30fps-v001.mp4` (1280×720, H.264, 30/1fps)
- 검토 페이지: `review.html` (구간 선택·반복 재생)
- 프레임 대응: `time-map.json`, `frame-map.csv`

## 시간 배분

| 구간 | 내용 | 영상 시간 | 길이 | 출력 프레임 |
| --- | --- | --- | --- | --- |
| S1 | 컨테이너 선적 | 0–2.5초 | 2.5초 | f0–f74 |
| S2 | 중국 항구 공개·출항 | 2.5–5.5초 | 3초 | f75–f164 |
| S3 | 미니어처 지구 항해 | 5.5–10.5초 | 5초 | f165–f314 |
| S4 | 미국 입항·하역 | 10.5–15.5초 | 5초 | f315–f464 |
| S5 | 트럭 이동·정렬·문 개방·도크 진입 | 15.5–22초 | 6.5초 | f465–f659 |
| S6 | 창고 입고·보관·피킹·포장·상차 | 22–29초 | 7초 | f660–f869 |
| S7 | 출고·배송 분기 | 29–33초 | 4초 | f870–f989 |

출력은 f0–f989를 포함합니다. 마지막 프레임은 원본 f1392의 최종 자세이며, 32.9667초부터 33초까지 표시됩니다. f990은 렌더하지 않는 종료 경계입니다.

## 리듬

전체를 약3.52배 빠르게 만들면서도 이동과 작업 확인의 속도를 구분했습니다. S5의 주행·정렬에는3.25초, 문 개방에는1.2초, 후진에는1.5초를 배정했습니다. S6의 입고·보관·피킹·포장 확인·상차 순서는 유지하고, 마지막 화물을 옮기는 동작에는0.65초를 확보했습니다. 미국 도시 공개에서 선박 측면과 트럭 추적으로 이어지는 v013 경로도 그대로 사용합니다.

모든560개 애니메이션 곡선에 단일 단조3차 시간 매핑을 적용했습니다. 구간 접점은 양수인 공통 속도를 사용하므로 시간 매핑 자체가 중간 정지를 만들지 않습니다. 카메라 위치·회전·렌즈·화면 수평 보정, 선박·차량·바퀴·문·화물·크레인·컨베이어가 같은 시각을 평가합니다. 원래 공간 경로와 지지 관계는 바꾸지 않았습니다. 기존 제작 구간의 포장 세부 동작 등은 이번에 추가하지 않았습니다.

재생속도 필터나 프레임 복제로30fps를 만든 것이 아니라, 새 출력 시점990개를 Blender에서 각각 렌더링했습니다. 편집 가능한 키프레임을 저장하며, 외부 프레임 변경 핸들러 없이 재생됩니다. 스크롤 길이는 영상 길이와 별도로 웹에서 정할 수 있습니다. `media_progress`는 영상 좌표이며 스크롤 정책이 아닙니다.

## 검증

최종 저장본을 다시 열어 원본 대응 시점과 비교했습니다. 출력990프레임과 중간 시점 등1194개 시각에서 움직이는 객체 및 하위 객체464개의 월드 행렬과 카메라 투영을 확인했습니다. 최대 행렬 성분 오차는0.00007439, 렌즈·shift 오차는0.00000381입니다. 표시/숨김 불일치는0건이며, 고정 객체9625개와 메시·재질·월드가 보존되었습니다.

기존 곡면·물류·창고·카메라 검사17개와 새 시간 매핑 검사5개가 통과했습니다. 창고 검사는 기존 곡면 검증과 동일한 `CV_WH_US_FRAME` 좌표계를 사용하고, 원본 프레임 번호를 새 출력 시각으로 변환하여 기존 판정식을 그대로 실행합니다. 입항 카메라의 최소 이동 속도는6.598 장면 단위/초로, 수정 구간에 정지가 없습니다.

MP4의 실제 프레임 수990개, 평균/명목 프레임률30/1, 재생시간33.000초와 전체 디코드를 확인했습니다. 검증 상세는 `review/verification.json`, `review/regressions-final.log`, `review/timing-tests.log`, `review/video.json`에 있습니다. 최종 파일 해시는 `delivery.json`에 있습니다.

## 재생성 및 보호 범위

`config.json`의 원본은 `../city-reveal-camera-v001/candidate-city-reveal-v013.blend`이고 SHA256은 `99361028c1463fe4fdeb085146e0f00e64df1f9796e5b4b3dfe79bdf0815d6cf`입니다. `scripts/build.py`는 원본 해시를 검사하고 새 작업본을 생성합니다. 기존 최종 파일을 덮어쓰지 않으므로 새 버전을 만들 때는 config의 출력 이름을 바꿉니다.

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$root = 'F:/pnpline-landing/hero-section-video/blockout/pacing-33s-v001'
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/build.py"
& $blender --background --factory-startup --python-exit-code 1 --python "$root/scripts/verify.py"
& $blender --background --factory-startup "$root/pnpline-33s-30fps-v001.blend" --python-exit-code 1 --python "$root/scripts/run_regressions.py"
& $blender --background --factory-startup "$root/pnpline-33s-30fps-v001.blend" -t 6 --python-exit-code 1 --python "$root/scripts/render.py" -- --start 0 --end 494
& $blender --background --factory-startup "$root/pnpline-33s-30fps-v001.blend" -t 6 --python-exit-code 1 --python "$root/scripts/render.py" -- --start 495 --end 989
python "$root/scripts/encode.py"
python "$root/scripts/serve.py"
```

원본 v013과 기존 마스터 지정 파일은 보존했습니다. 커밋·푸시·외부 업로드는 수행하지 않았습니다. 렌더 PNG, 검사 로그, 작업 중간 영상과 캐시는 이 디렉터리의 `.gitignore`로 제외합니다.
