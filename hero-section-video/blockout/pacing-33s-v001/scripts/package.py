"""Write the deliverable record only after reopened-scene and media checks pass."""
import hashlib,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cfg=json.loads((R/'config.json').read_text(encoding='utf-8'))
verify=json.loads((R/'review/verification.json').read_text())
video=json.loads((R/'review/video.json').read_text())
mapping=json.loads((R/'time-map.json').read_text(encoding='utf-8'))
log=(R/'review/regressions-final.log').read_text(encoding='utf-8')
assert 'Ran 17 tests' in log and '\nOK\n' in log.replace('\r','')
assert not any(verify['differences'].values())
assert verify['max_world_matrix_error']<.002 and verify['max_lens_and_shift_error']<.0002
assert verify['visibility_mismatches']==0 and verify['approach_camera_min_units_per_frame']>.1
result=subprocess.run(['python',str(R/'tests/test_timing.py')],capture_output=True,text=True)
(R/'review/timing-tests.log').write_text(result.stdout+result.stderr,encoding='utf-8')
assert result.returncode==0
assert video['blend_sha256']==verify['output_sha256']==mapping['output_sha256']==sha(R/cfg['output'])
paths=[cfg['output'],'preview/pnpline-33s-30fps-v001.mp4','time-map.json','frame-map.csv','config.json','review.html']
record={'version':'33s-30fps-v001','source_sha256':cfg['source_sha256'],'files':{p:sha(R/p) for p in paths},
    'fps':30,'frame_count':990,'duration_seconds':33,'resolution':[1280,720],
    'source_duration_seconds':1393/12,'sections':mapping['sections'],'verification':verify,
    'regression_tests':17,'timing_tests':5,'media_full_decode_passed':True,
    'render_method':'990 unique Blender Workbench frames; no duplicate-frame upconversion, optical flow or video speed filter',
    'source_preserved':sha((R/cfg['source']).resolve())==cfg['source_sha256'],
    'branch':'main','master_promoted':False,'committed':False}
assert record['source_preserved']
(R/'delivery.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
table='\n'.join(f"| {s['section']} | {s['description']} | {s['output_start']/30:g}–{s['output_end_exclusive']/30:g}초 | {s['duration_seconds']:g}초 | f{s['output_start']}–f{s['output_end_exclusive']-1} |" for s in mapping['sections'])
report=f'''# PNPLINE 33초 · 30fps 모션 v001

기존 v013 카메라 동선과 장면을 유지하고, 원본 12fps·1,393프레임(약116.08초)의 모든 동작을 33초·30fps·990프레임으로 재배치했습니다. main 브랜치의 동일 작업공간에서 제작했습니다.

- 작업본: `pnpline-33s-30fps-v001.blend`
- 전체 영상: `preview/pnpline-33s-30fps-v001.mp4` (1280×720, H.264, 30/1fps)
- 검토 페이지: `review.html` (구간 선택·반복 재생)
- 프레임 대응: `time-map.json`, `frame-map.csv`

## 시간 배분

| 구간 | 내용 | 영상 시간 | 길이 | 출력 프레임 |
| --- | --- | --- | --- | --- |
{table}

출력은 f0–f989를 포함합니다. 마지막 프레임은 원본 f1392의 최종 자세이며, 32.9667초부터 33초까지 표시됩니다. f990은 렌더하지 않는 종료 경계입니다.

## 리듬

전체를 약3.52배 빠르게 만들면서도 이동과 작업 확인의 속도를 구분했습니다. S5의 주행·정렬에는3.25초, 문 개방에는1.2초, 후진에는1.5초를 배정했습니다. S6의 입고·보관·피킹·포장 확인·상차 순서는 유지하고, 마지막 화물을 옮기는 동작에는0.65초를 확보했습니다. 미국 도시 공개에서 선박 측면과 트럭 추적으로 이어지는 v013 경로도 그대로 사용합니다.

모든560개 애니메이션 곡선에 단일 단조3차 시간 매핑을 적용했습니다. 구간 접점은 양수인 공통 속도를 사용하므로 시간 매핑 자체가 중간 정지를 만들지 않습니다. 카메라 위치·회전·렌즈·화면 수평 보정, 선박·차량·바퀴·문·화물·크레인·컨베이어가 같은 시각을 평가합니다. 원래 공간 경로와 지지 관계는 바꾸지 않았습니다. 기존 제작 구간의 포장 세부 동작 등은 이번에 추가하지 않았습니다.

재생속도 필터나 프레임 복제로30fps를 만든 것이 아니라, 새 출력 시점990개를 Blender에서 각각 렌더링했습니다. 편집 가능한 키프레임을 저장하며, 외부 프레임 변경 핸들러 없이 재생됩니다. 스크롤 길이는 영상 길이와 별도로 웹에서 정할 수 있습니다. `media_progress`는 영상 좌표이며 스크롤 정책이 아닙니다.

## 검증

최종 저장본을 다시 열어 원본 대응 시점과 비교했습니다. 출력990프레임과 중간 시점 등{verify['sample_times']}개 시각에서 움직이는 객체 및 하위 객체{verify['moving_objects_including_descendants']}개의 월드 행렬과 카메라 투영을 확인했습니다. 최대 행렬 성분 오차는{verify['max_world_matrix_error']:.8f}, 렌즈·shift 오차는{verify['max_lens_and_shift_error']:.8f}입니다. 표시/숨김 불일치는0건이며, 고정 객체{verify['static_objects']}개와 메시·재질·월드가 보존되었습니다.

기존 곡면·물류·창고·카메라 검사17개와 새 시간 매핑 검사5개가 통과했습니다. 창고 검사는 기존 곡면 검증과 동일한 `CV_WH_US_FRAME` 좌표계를 사용하고, 원본 프레임 번호를 새 출력 시각으로 변환하여 기존 판정식을 그대로 실행합니다. 입항 카메라의 최소 이동 속도는{verify['approach_camera_min_units_per_second']:.3f} 장면 단위/초로, 수정 구간에 정지가 없습니다.

MP4의 실제 프레임 수990개, 평균/명목 프레임률30/1, 재생시간33.000초와 전체 디코드를 확인했습니다. 검증 상세는 `review/verification.json`, `review/regressions-final.log`, `review/timing-tests.log`, `review/video.json`에 있습니다. 최종 파일 해시는 `delivery.json`에 있습니다.

## 재생성 및 보호 범위

`config.json`의 원본은 `../city-reveal-camera-v001/candidate-city-reveal-v013.blend`이고 SHA256은 `{cfg['source_sha256']}`입니다. `scripts/build.py`는 원본 해시를 검사하고 새 작업본을 생성합니다. 기존 최종 파일을 덮어쓰지 않으므로 새 버전을 만들 때는 config의 출력 이름을 바꿉니다.

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
'''
(R/'README.md').write_text(report,encoding='utf-8')
print('PACKAGED',R)
