# PNPLINE Master v001

**7구간 연출안 검증용 / 기존 #61 승인안 대체 아님.**

`master-v001.blend`를 Blender 5.1에서 열고 카메라 보기(숫자패드 0), Space로 재생한다. 타임라인은 1–1392프레임, 12fps다. GUI 재생 속도는 장치 성능에 따라 달라질 수 있으므로 일정 속도의 검토에는 `preview/master-v001.mp4`를 사용한다.

편집 가능한 단일 씬, 304개 오브젝트, 한 본편 카메라와 7구간 마커가 들어 있다. `08_REVIEW_GUIDES` 컬렉션은 배치 검토용이고 본편 렌더에서는 숨겨져 있다. 지구·부두·도로·창고는 고정되어 있다. `DETAIL_DEFERRED_*` 마커는 미구현 상세 작업을 표시한다.

## 파일

- `report.md`: AC-1~10 판정, 시간대, 검증 한계, 후속 조건.
- `manifest.json`: 입력, 시험 설정, 32개 애셋 ID·개체·컬렉션·구간·보강 사항.
- `boundary-states.json`: 여섯 경계의 실제 평가 상태, 전후 속도·회전·렌즈·지지 관계. 행렬과 중첩 개체를 보존하기 위해 CSV 대신 JSON을 사용했다.
- `validation.json`, `review/all-frame-states.json`, `review/subframe-states.json`: 전 프레임 및 근접 구간 샘플.
- `review/`: 본편 관찰 스틸, 세계/항만/창고 배치, S5 탑뷰·측면, 경계 전후, 실제 재생 화면과 증거.
- `inputs/N0.json`~`N7.json`: 조회한 원문 스냅샷. 원본 애셋 목록은 `../plan/inputs/asset-inventory-source-v0.1.txt`.
- `scripts/`: 생성·검증·렌더·재생·해시 도구. `logs/*-final.log`는 최종 실행 기록이다. RED 로그는 수정 전 실패 증거다.
- `hashes.json`: 인계 파일 SHA-256 및 1392개 PNG 시퀀스의 결합 해시. `.blend1`, smoke 파일과 중간 로그는 최종 인계 대상이 아니다.

## 재현

아래 명령은 PowerShell에서 실행한다. 새 Blender 백그라운드 프로세스를 사용하므로 열려 있는 GUI의 미저장 편집에는 적용되지 않는다. 생성 명령은 **이 폴더의 생성 산출물을 덮어쓴다**. 사용자가 `.blend`를 직접 수정한 뒤에는 다른 폴더로 복사해 보존하고 재생성한다. 스크립트가 제작 원본이며 현재 `.blend`에 수동 편집은 없다.

```powershell
$p = 'F:\pnpline-landing\hero-section-video\blockout\blockout-master-v001'
$b = 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe'
$py = 'C:\ProgramData\miniconda3\python.exe'

# 재생성 없이 저장 파일 검사
& $b --background --factory-startup "$p\master-v001.blend" --python-exit-code 1 --python "$p\scripts\test_scene.py" --python "$p\scripts\export_validation.py"

# 생성부터 재현할 때만 실행
& $b --background --factory-startup --python-exit-code 1 --python "$p\scripts\build_master.py"
& $b --background --factory-startup "$p\master-v001.blend" --python-exit-code 1 --python "$p\scripts\test_scene.py" --python "$p\scripts\export_validation.py"

# 검토 스틸과 애니메이션은 별도 프로세스로 출력
& $b --background --factory-startup "$p\master-v001.blend" --python-exit-code 1 --python "$p\scripts\render_review.py"
& $b --background --factory-startup "$p\master-v001.blend" -s 1 -e 1392 -a
ffmpeg -hide_banner -y -framerate 12 -i "$p\preview\frames\frame-%04d.png" -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart "$p\preview\master-v001.mp4"
& $b --background --factory-startup "$p\master-v001.blend" --python-exit-code 1 --python "$p\scripts\verify_reopen.py"
```

각 명령의 종료 코드가 0일 때 다음 단계로 진행한다. `--factory-startup`은 사용자 애드온의 백그라운드 GPU 오류를 피하기 위한 실행 옵션이며 환경설정을 저장하지 않는다. 새 패키지를 설치할 필요가 없다. ffmpeg 7.1, Python의 기존 Pillow, Codex에 포함된 Playwright와 설치된 Chrome을 사용했다.

실제 1배속 재생 검사는 별도 터미널에서 로컬 서버를 실행한 뒤 수행한다. 같은 포트의 기존 검토 서버가 있으면 중복 실행하지 않는다.

```powershell
& $py -m http.server 8766 --bind 127.0.0.1 --directory $p
```

다른 터미널:

```powershell
$env:PNPLINE_PLAYWRIGHT_PATH = 'C:\Users\KIM TAEHYUNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules\playwright'
$env:PNPLINE_CHROME_PATH = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
& 'C:\Users\KIM TAEHYUNG\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' "$p\scripts\playback_qa.cjs"
& $py "$p\scripts\make_playback_sheets.py"
& $py "$p\scripts\finalize_handoff.py"
```

`finalize_handoff.py`는 원본 입력 해시, 재개방 PNG 동일성, ffprobe를 확인하고 매니페스트를 보강한다. 파일을 바꾼 뒤에는 이전 해시/검증 결과가 더 이상 현재 파일의 증거가 아니다. 원문 조회를 재실행하면 `inputs` 스냅샷과 보고서를 함께 갱신한다.

텍스트 입력에 대한 공간 후보이며 보드 대조·최종 손동작·최종 룩·모바일·웹 카피/CTA·실제 물류 안전성은 별도 작업이다.
