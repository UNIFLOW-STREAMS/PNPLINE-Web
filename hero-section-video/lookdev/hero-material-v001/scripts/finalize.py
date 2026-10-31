import json,hashlib,statistics
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parents[1];V=R/'review'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
verify=read(V/'preservation-verification.json');pack=read(V/'packaging.json');settings=read(V/'render-settings.json');temporal=read(V/'temporal-compression.json');materials=read(V/'material-manifest.json')
sha=hashlib.sha256((R/'pnpline-hero-material-v001.blend').read_bytes()).hexdigest();assert verify['passed'] and verify['result_sha256']==sha==pack['packed_file_sha256']==settings['sha256'];assert len(temporal)==3
assert not settings['libraries'];assert all(f['packed'] or f['path']=='<builtin>' for f in settings['fonts'])
allmetrics=[];groups={}
for label in ['after','water-glass','us-port','warehouse']:
 m=read(V/label/'render-metrics.json');assert all(x['source_sha256']==pack['render_source_sha256'] for x in m)
 allmetrics+=m;steady=[x['seconds'] for x in m[1:]];groups[label]=dict(frames=len(m),mean_seconds=statistics.mean(steady),min_seconds=min(steady),max_seconds=max(steady),first_frame_seconds=m[0]['seconds'])
times=[x['seconds'] for x in allmetrics];mean=statistics.mean(times);median=statistics.median(times)
bench=read(V/'clips-benchmarks.json')+read(V/'styles-benchmarks.json');peak=max(x['peak_process_rss_gib'] for x in bench);gpu=max(x['system_gpu_memory_mib_peak'] for x in bench)
estimate=dict(profile='RTX4070 OptiX, 1920x1080, 128 max samples, adaptive .02/min32, OIDN, six CPU threads',measured_images=len(times),mean_seconds=mean,median_seconds=median,groups=groups,peak_process_rss_gib=peak,peak_whole_gpu_mib=gpu,whole_gpu_note='Includes other running applications; not isolated renderer VRAM.',estimated_990_frames_hours=mean*990/3600,estimated_range_hours=[min(g['mean_seconds'] for g in groups.values())*990/3600,max(g['mean_seconds'] for g in groups.values())*990/3600],estimate_note='Extrapolation from sampled scenes, not a measured full render. Rendering PNG16 or using saved adaptive .015 may take longer. GPU contention and thermal behavior also affect time.')
(V/'render-estimate.json').write_text(json.dumps(estimate,indent=2),encoding='utf8')
status=dict(file=str(R/'pnpline-hero-material-v001.blend'),sha256=sha,source=read(V/'survey.json')['file'],source_sha256=verify['source_sha256'],render_source_sha256=pack['render_source_sha256'],review=str(R/'review.html'),preservation=str(V/'preservation-verification.json'),materials=str(V/'material-manifest.json'),settings=str(V/'render-settings.json'),timing=str(R/'time-map.json'),fps=30,frame_start=0,frame_end=989,completed=['Blender material/light/color edits','8 matched 1080p Cycles before/after frames','3 x 30-frame 1080p Cycles sequences and H264 compression comparisons','990-frame camera/motion comparison','Embedded existing font; no external texture or library dependencies'],pending=['Real-time UI playback review: Computer Use ended because current Windows browser URL could not be verified.','Live website hero composite review: configured target output/scroll-world-concept-v1/index.html is missing. 1440px and 390px image-size checks delivered.'],status='Lookdev files and production-render evidence delivered; real-time UI playback review pending')
(R/'delivery.json').write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding='utf8');(R.parent/'latest-lookdev.json').write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding='utf8')
rows='\n'.join(f"| {r['title']} | {r['start']}–{r['end']} | {r['ssim_vs_png']:.4f} | {r['web_bytes']/1024:.0f} KiB | {r['max_adjacent_global_luma_step']:.3f}/255 |" for r in temporal)
families=', '.join(f'{k} {v}' for k,v in Counter(m['family'] for m in materials['materials']).items())
text=f'''# PNPLINE Hero material v001

실제 통합 Blender 파일의 재질·조명·월드·색 관리를 보강하고 Cycles에서 렌더했습니다. 원본 형상과 카메라·물류 애니메이션은 보존했습니다. 최종 사용 파일은 `pnpline-hero-material-v001.blend`입니다.

## 파일과 검토 상태

- 원본: `{status['source']}`
- 원본 SHA256: `{status['source_sha256']}`
- 최종 파일 SHA256: `{sha}`
- 검토 렌더 원본 SHA256: `{pack['render_source_sha256']}`
- 렌더 후 기존 Arial Bold 폰트를 바이트 그대로 내장했습니다. 형상·재질·조명·카메라는 변경하지 않았습니다. 렌더 당시 파일은 `inputs/render-source-unpacked.blend`에 보관했습니다.
- `review.html`: 동일 카메라 전후 비교, 대표 프레임, 고품질/웹압축 MP4, 확대 연속 프레임.
- `lookdev/latest-lookdev.json`은 이 파일을 가리킵니다. `blockout/latest-previz.json`과 원본 파일은 변경하지 않았습니다.
- **실시간 UI 재생 검토는 미완료**입니다. 로컬 검토 페이지를 열 때 Computer Use가 현재 Windows 브라우저 URL을 검증하지 못해 UI 제어를 중단했습니다. 우회하지 않았습니다. 영상은 30fps/30프레임/1초임을 디코딩 검사했으며, 확대 연속 프레임을 직접 확인했습니다. 전체 밝기·압축 수치는 시간적 깜빡임이 전혀 없음을 증명하지 않습니다.
- 현재 배포 설정의 `output/scroll-world-concept-v1/index.html`이 없어 운영 페이지 합성 검증은 하지 못했습니다. 1440×810과 390×219 축소 이미지로 가로 영상의 가독성을 확인했습니다. 세로 크롭 시 랜드마크가 잘리는 문제는 별도 레이아웃 검토 대상입니다.

## 룩과 재질

컨셉의 절제된 미니어처 표현, 밝은 확산광, 국가 상징색과 PNPLINE 청색을 기준으로 작업했습니다. 형상 보강으로 범위를 넓히지 않았습니다.

- 기존 185개 재질을 조사하고 표면별 노드로 재구성했습니다. 일부 기본 셰이더의 회색과 뷰포트의 청색 불일치를 바로잡았습니다.
- 재료 분류: {families}.
- 재사용 그룹 `LD_Stable_Surface_v1`: 같은 절차형 필드에서 약한 색 변화와 거칠기 변화, 미세 범프를 생성합니다. World 좌표 대신 오브젝트 로컬 좌표를 사용하며 시간·프레임 랜덤 입력이 없습니다.
- 컨테이너의 기존 평면 블록에는 Generated 좌표의 골판 법선을 추가했습니다. 돌출·변위는 사용하지 않아 접점과 외곽선은 동일합니다. PNPLINE 문자 메시를 유지했습니다.
- 건축 유리는 기존 솔리드 빌딩에 맞춘 불투명 백킹 유리 표현입니다. IOR 1.48, roughness 약 .24, 약한 coat를 사용합니다. 실제 창 내부나 유리 두께는 추가하지 않았습니다.
- 바다/수로는 IOR 1.333, roughness 약 .28, coat .5, 어두운 청록 색과 미세 범프를 사용한 불투명 수면 근사입니다. 굴절/볼륨 깊이 시뮬레이션이나 파도 지오메트리는 추가하지 않았습니다.
- 금속은 metallic 약 .9, 거칠기 .29로 구분하고 도장은 metallic 0, 거칠기 .34와 coat를 사용했습니다. 석재 .60, 콘크리트 .72, 아스팔트 .87, 고무 .82, 종이 .78을 기준으로 미세 변화를 줬습니다.
- 창과 지붕이 공유하던 `SF_roof`는 창 오브젝트에 유리 슬롯을 지정했습니다. 팔레트에 쓰이던 테이프 재질은 목재로 분리했습니다. 오브젝트 슬롯 변경 내역은 `review/material-manifest.json`에 있습니다.
- 외부 이미지 텍스처와 링크된 라이브러리는 없습니다. 입력 색은 scene-linear, 거칠기/법선 필드는 비색상 데이터입니다. 기존 Windows Arial Bold만 원본과 동일한 바이트로 내장했으며 출처/해시는 `review/packaging.json`에 있습니다. 네 컨셉 이미지는 색·재료 참고용이며 텍스처로 삽입하지 않았습니다.

## 조명과 색 관리

- 중국/미국에 대형 Area key와 fill/rim 총 4개를 추가했습니다. 기존 비교용 키의 energy를 0으로, 창고의 기존 Area 4개를 420W로 조정했습니다. 위치/크기는 `review/render-settings.json`에 기록했습니다.
- World 조명은 차분한 청색 계열, strength .45입니다. 카메라 배경만 밝은 회색으로 분리했습니다.
- AgX / Medium High Contrast, exposure +.3, gamma 1. 노출 키프레임을 추가하지 않았습니다.
- Cycles / OptiX / RTX4070 12GB, 1920×1080, 최대128샘플, 최소32, OIDN, 고정 seed29, animated seed off, indirect clamp3, filter1.5px, glossy blur .7.
- 검토 및 재현 스크립트는 adaptive threshold .02를 사용합니다. `.blend`에 저장된 기본값은 더 엄격한 .015이며 PNG16 출력입니다. 아래 실행 스크립트는 실제 검토와 같은 .02를 명시적으로 적용하고 PNG16을 저장합니다.

## 대표 프레임과 검증

45(중국 하역), 110(중국 도시·항만), 200(해상 전환), 315(미국 도시·항만), 390(미국 크레인 이동), 530(트럭 인입), 720(창고 입고/랙), 820(창고 피킹/이동)의 1080p 전후 이미지를 제공했습니다. 전후 모두 실제 CAM_MASTER이며, 원본은 저장하지 않고 검토 렌더 엔진과 출력 품질만 맞췄습니다.

보존 검증: 원본 {verify['objects']:,}개 오브젝트, {verify['actions']}개 액션, 움직이는 오브젝트·카메라 {verify['tracked_objects']}개 ×990프레임. 최대 변환 오차 {verify['max_motion_error']}. 카메라 광학 설정, 형상/토폴로지, 리그·제약·드라이버, 표시 여부, 타임라인 마커, 시간 매핑이 동일합니다. 변경 허용 필드는 재질 슬롯과 조명 데이터이며, 추가 오브젝트는 조명 4개입니다. 세부 결과는 `review/preservation-verification.json`에 있습니다.

각 연속 구간은 1초입니다. CRF12 검토본과 CRF24 웹 압축본을 같은 30fps로 만들었습니다. 반복 재생 시 끝→처음 점프는 잘라낸 검토 구간의 경계입니다.

| 구간 | 프레임 | 웹 SSIM vs PNG | 웹 파일 크기 | 최대 인접 프레임 전체 밝기 차 |
|---|---|---:|---:|---:|
{rows}

글로벌 밝기는 카메라 이동에도 달라지므로 위 수치는 진단용입니다. 창문 격자·수면·크레인 선재의 확대 연속 이미지를 확인했고, 검토 프레임에서 큰 노출 급변이나 과도한 범프는 보이지 않았습니다. 실시간 재생 판정은 남아 있습니다.

## 측정과 예상

- 실제 렌더한 보강본: 대표8장 + 연속90장. 원본 비교8장은 별도입니다.
- 프레임 평균 {mean:.2f}초, 중앙값 {median:.2f}초(장면 초기화가 포함된 첫 프레임 포함).
- Blender 프로세스 최대 Working Set/RSS: {peak:.2f} GiB.
- GPU 전체 사용량 최대: {gpu:,} MiB. 다른 앱 사용량이 포함되므로 Blender 단독 VRAM으로 해석하면 안 됩니다.
- 같은 검토 프로파일로 990프레임 예상: 약 {estimate['estimated_990_frames_hours']:.2f}시간. 측정 구간 평균의 범위로 환산하면 {estimate['estimated_range_hours'][0]:.2f}–{estimate['estimated_range_hours'][1]:.2f}시간입니다. 전체 영상의 실측 시간이 아니며 PNG16 저장·다른 앱 GPU 점유·엄격한 .015 설정에 따라 늘어날 수 있습니다.
- 전체 33초 최종 영상은 아직 렌더하지 않았습니다. 원본/결과 프레임, 원시 로그와 측정 JSON을 보관했습니다.

## 재현 가능한 최종 렌더

PowerShell에서 다음 스크립트를 실행합니다.

```powershell
& 'F:/pnpline-landing/hero-section-video/lookdev/hero-material-v001/render-final.ps1'
```

Blender 5.1의 factory-startup으로 부가 애드온 영향을 배제하고, OptiX를 설정한 뒤 0–989를 렌더합니다. 결과는 `review/production/f0000.png`부터 PNG16으로 저장되고, FFmpeg가 H.264 CRF20 / yuv420p / faststart / 무음 MP4를 만듭니다. 웹용 인코딩은 필요시 CRF24와 비교할 수 있습니다. 기존 프레임 일부를 다시 만들 때는 `scripts/render.py --frames 시작:종료`를 사용하며 종료는 포함하지 않습니다.

보강 재현은 `scripts/build.py`를 불변 원본 파일에 실행한 뒤 `scripts/seal.py`를 결과에 실행하는 방식입니다. `scripts/verify.py`는 원본을 저장하지 않고 전체 보존 조건을 대조합니다.
'''
(R/'README.md').write_text(text,encoding='utf8');print(json.dumps(estimate,indent=2),flush=True)
