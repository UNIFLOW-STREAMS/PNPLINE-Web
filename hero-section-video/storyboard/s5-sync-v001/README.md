> 현재 전체 마스터: [S1–S7 통합 결과](../../blockout/full-layout-master-v001/README.md). 사용자 통합 지시를 반영했으며, 아래 내용은 이전 단계의 기록입니다. 선화 후보의 최종 선택은 별개입니다.

> 최신 제출: [S4-05 기준 별도 배치·동선 제안](layout-proposal-v001/report.md) — [영상·비교 검토](layout-proposal-v001/review.html). f552–948 검토용, 원본 보존, 최종 마스터 미채택. 아래의 기존 Stage③ 후보/카메라 진단은 이전 기준 자료입니다.

# S5 storyboard synchronization — review candidates

상태: **재작업 필요 / 기준 콘티 미충족**. 사용자는 기존 S4-05를 기준으로 연결 구도 재검토를 선택했습니다. 카메라 한정 시험안도 미채택이며, 범위를 확대하는 별도 제안본 작업 전에 확인이 필요합니다. 앞선 6장 일괄 채택은 보류되었습니다. ③ 전체 완료나 콘티 최종 승인이 아닙니다.

최신 결과: `review/s4-s5-recheck/recheck.md`, `review/s4-s5-recheck/recheck-summary.png`, `preview/camera-only-diagnostic.mp4`. 비교 영상은 왼쪽 저장본 / 오른쪽 미채택 카메라 시험입니다.

검토 페이지: http://127.0.0.1:8767/review.html

- `review/s4-s5-start-comparison.png`: 실제 f648, 제안 f672, 기존 S4-05 대조. 기존 콘티는 선박 왼쪽·물류센터 오른쪽이고 저장본은 반대 관계입니다. f648→672 영상 연속성과 기존 콘티 충실도는 다른 판정입니다.
- `review/candidates.png`: 여섯 원본 프레임과 영상 밖 하단 메모.
- `preview/main.mp4`: 현재 저장본에서 새로 렌더한 f624–948, 12 fps, 325 frames, 27.083333초.
- `review/style-comparison.png`: f766 원본과 동일 상태의 Freestyle 최소 샘플. 전체 선화 제작은 선택 후입니다.
- `storyboard-selection.json`: 후보 매핑. 01 f672 / 02 f720 / 03 f732 / 03A f766 / 04 f842 / 05 f900.
- `storyboard-manifest.json`, `render-record.json`: 실제 렌더 당시 출처와 개별 PNG 연결.
- `review-decisions.json`: 기준·프레임·표현·최종 승인을 별도 기록.
- `report.md`: 검사 결과, 한계, 미완료 단계.

## 기준 파일

원본: `F:/pnpline-landing/hero-section-video/blockout/s5-integration-v001/master-s5-integration-v001.blend`

SHA-256: `8c76f0e184bc742309cf66dcf9f3f5fa7072e02b54b58e6985a91ff1ae57b665`

`master/source-current.blend`는 원본의 **바이트가 같은 복사본**입니다. 새 카메라 수정본이 아닙니다. 어떤 Blender 프로세스도 이번 작업에서 .blend를 저장하지 않았습니다. GUI 검토용으로 이 복사본을 열었습니다.

## 재현

루트에서 아래 명령을 실행합니다. Python에는 기존 Pillow가 필요하고 Blender 5.1, ffmpeg가 이미 설치되어 있습니다. `bootstrap.py`는 최초 입력 고정용으로 두 번 실행하지 않습니다. GUI에서 복사본을 저장하면 출처 검사가 실패하며 새 기준 선택이 필요합니다.

```powershell
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/tests/test_contracts.py'
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' --factory-startup -b 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/master/source-current.blend' --python-exit-code 1 --python 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/scripts/render.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/scripts/package_draft.py'
& 'C:/ProgramData/miniconda3/python.exe' -X utf8 'F:/pnpline-landing/hero-section-video/storyboard/s5-sync-v001/scripts/verify_artifacts.py'
```

렌더 실행마다 고유 raw 폴더를 만듭니다. 중단된 렌더·누락된 프레임·섞인 PNG·변경된 입력/표현 설정을 패키지 생성 시 거부합니다. 프레임 선택 변경 후에는 해당 선택으로 다시 렌더하며 과거 기록을 새 출처로 덮어쓰지 않습니다. 선화 샘플은 `scripts/style_sample.py`로 별도 메모리 안에서 렌더합니다. 실제 기존 회귀 검사는 `scripts/inspect_source.py`가 새 로그 경로에서 재실행합니다.

서버를 다시 열려면 `python scripts/serve_review.py`를 이 폴더에서 실행합니다. 로컬 주소에만 바인딩합니다. 웹 페이지 재생 로그는 기술 검토 기록이며 사용자 승인으로 사용하지 않습니다.
