import json,hashlib,argparse,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--handoff',required=True);a=p.parse_args();r=Path(__file__).resolve().parents[1];source=Path(a.source);handoff=Path(a.handoff)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cfg=read(r/'config.json');motion=read(r/'review/motion-validation.json');space=read(r/'review/space-validation.json');repro=read(r/'review/reproduction-validation.json');preserve=read(r/'review/preservation-comparison.json');bounds=read(r/'review/boundary-states.json')
assert digest(source)==cfg['source_sha256'];assert all([motion['pass_all'],space['pass_all'],repro['pass_all'],preserve['equal']])
frames=[648,746,810,826,842,849,890,900];matches={}
for view in ['oblique','top']:
 (r/'review'/view).mkdir(exist_ok=True)
 for f in frames:
  png=r/'preview'/view/f'{f:04d}.png';shutil.copy2(png,r/'review'/view/png.name);matches[f'{view}-{f}']=Image.open(png).tobytes()==Image.open(r/'review/reopen'/view/png.name).tobytes()
assert all(matches.values());(r/'review/reopen-pixel-compare.json').write_text(json.dumps(matches,indent=2))
sheet=Image.new('RGB',(960,len(frames)*290),'white');draw=ImageDraw.Draw(sheet)
for j,f in enumerate(frames):
 for x,view in enumerate(['oblique','top']):sheet.paste(Image.open(r/'preview'/view/f'{f:04d}.png').resize((480,270)),(x*480,j*290+20));draw.text((x*480+5,j*290+3),f'{view} f{f}',fill='black')
sheet.save(r/'review/contact-sheet.png')
clips={}
for view in ['oblique','top']:
 clips[view]=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,duration','-of','json',str(r/f'preview/s5-{view}.mp4')],text=True))
survey=read(r/'review/baseline-survey.json')
manifest=dict(schema_version=1,head='6079b392d7de54509ed50454ddd2745273cc0078',branch='codex/s5-dock-test',worktree=str(r.parents[2]),source=str(source),source_sha256=digest(source),source_bytes=source.stat().st_size,output='master-with-s5-test-v001.blend',output_sha256=digest(r/'master-with-s5-test-v001.blend'),scenes=[cfg['source_scene'],cfg['test_scene']],blender='5.1.0 adfe2921d5f3',python='3.13.9',ffmpeg='7.1',parent_model='Current session model is not introspectable or switchable through available tools; no claimed model change',reviewer_model='gpt-6-astra/high requested for one fresh-context read-only review',references={p.name:digest(p) for p in handoff.iterdir() if p.is_file()},fps=12,frame_range=[648,900],source_frame_mapping=cfg['source_frames'],US_FRAME_local_to_world=survey['us_matrix'],axes=dict(vehicle_front='+local X',rear='-local X',regional_up='+local Z',dock_plane='US_FRAME x=36',dock_center=[36,29,1.8],docked_vehicle_front='US_FRAME -X',rear_toward='US_FRAME +X'),mapping=dict(A03_TRACTOR='tractor rear axle at root, front axle +1.65m',A03_TRAILER='representative tandem axle midpoint at root',TRAILER_HITCH='+2m along trailer forward, height1.4m',DOCK_TARGET='single existing dock, not four reference-image docks',E08_WAREHOUSE='existing open south/west-side floor, no gates/fences invented',INBOUND_WAIT_ZONE='existing receiving floor pad',RACK_='existing rack silhouettes'),proxy_repairs=cfg['proxy_repairs'],clips=clips,assumptions=cfg['assumptions'])
(r/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
entry=bounds['master'][1]['objects'];end=bounds['master'][4]['objects'];te=bounds['test'][1]['objects'];td=bounds['test'][4]['objects']
proposal=f'''# 마스터 통합 제안 — 적용하지 않음

테스트 후보는 독립 검토용이다. 원본 `{cfg['source_scene']}` 및 파일은 변경하지 않았다.

| 항목 | 원본 마스터 | 테스트 후보 |
|---|---|---|
| f648 트레일러 US 위치 | {entry['A03_TRAILER']['location']} | {te['A03_TRAILER']['location']} |
| f900 트레일러 US 위치 | {end['A03_TRAILER']['location']} | {td['A03_TRAILER']['location']} |
| f648 렌즈 | {entry['CAM_MASTER']['lens']}mm | {te['CAM_OBLIQUE']['lens']}mm |
| f900 렌즈 | {end['CAM_MASTER']['lens']}mm | {td['CAM_OBLIQUE']['lens']}mm |

진입은 **원본 f720의 접근 위치를 테스트 f648로 앞당긴 도크 전용 구간**이다. 항구 출발을 대체하는 안이 아니다. 원본 f648 위치와 바로 이어 붙이면 이동이 끊긴다. 전진 종료810, 문811–842, 후진849–890, 종료900은 유지했다. f648과 f900의 모든 차량·컨테이너·문·카메라·주시점 행렬, 중심 차분 속도, quaternion 변화율, 렌즈 변화율은 `review/boundary-states.json`에 있다.

선회 진입4m/종료8m 안에서 기존 타원 경로를 C3 다항식으로 연결했다. 경로의 다른 부분과 C/D 위치는 유지한다. 견인부 방향은 연결점 이동 접선으로 계산하며 바퀴 조향과 전진/후진 회전도 함께 저장한다.

테스트 객체만 변경: tandem half-spacing0.25→0.45m; 후면 문 경첩x−1.6→−1.65m; 문짝 높이1.5→1.24m(프레임 안 여유); 받침판 폭1.48→1.32m, 중심z1.82→1.88m. 원본 mesh/material을 수정하지 않고 독립 Object의 위치/scale로 적용했다. 전체 컨테이너 크기와 트레일러 대비 중심높이2.55m는 동일하다. 이는 원본에서도 관찰된 두 바퀴 및 문/바닥 겹침을 해소하는 시험용 보정이다.

S6 시작 차량·컨테이너 중심은 일치하지만 문짝 크기/경첩, 바퀴 간격, 받침판 및 **카메라·렌즈·주시점은 다르다**. 원본 S6 카메라로 즉시 전환하면 컷이 발생한다. 통합하려면 원본 항구 출발→접근 구간의 시간 배분과 S6 앞부분 카메라 접합, 프록시 보정의 적용 범위를 별도로 승인해야 한다. 이번에는 적용하지 않았다.

원본 항구의 타이어/부두 높이 겹침은 도크 테스트 범위 밖이며 원본 보존 상태에 남는다. 참조의 네 도크·게이트·화살표 배치는 실제 단일 도크와 다르므로 새 시설로 복제하지 않았다.
'''
(r/'integration-proposal.md').write_text(proposal,encoding='utf8')
metrics='\n'.join(f'- {k}: {v:.8f}' for k,v in motion['maximum'].items())
report=f'''# S5 도크 테스트 검토 기록

판정: 최종 독립 검토 대기. 마스터 통합은 수행하지 않았다.

입력 SHA256 `{digest(source)}` / 결과 SHA256 `{digest(r/'master-with-s5-test-v001.blend')}`.
기준 HEAD와 도구·참조 해시는 manifest.json. 현재 세션 모델은 도구로 확인/변경할 수 없어 변경했다고 주장하지 않는다. 마지막 검토는 가용 모델 GPT-6 Astra/high로 요청한다.

## 변경과 원인

원본 타원 경로 접속부의 견인부 방향/이동 접선 최대 오차19.018°를 재현했다. 후진 거리도 원본 바퀴 회전에 누락돼 있었다. 범위를 한정한 경로 연결, 연결점 유도 방향, 실제 바퀴 위치의 이동량/조향으로 보정했다. 원본은 그대로 두었다.

첫 복제본의 QUATERNION 모드에 Euler 키를 넣어 발생한 차량 뒤틀림은 저장본 검사에서 재현 후 XYZ 모드와 연속 각도로 수정했다. 사용자 첨부의 뒤틀린 차체·바퀴도 이 오류에 해당한다. 원본 tandem 바퀴/문/받침판의 겹침은 작은 Object 보정으로 해소했다. 재실행 시 미사용 Action12개가 남는 문제도 소유 데이터 정리로 수정했다.

## 검증

| AC | 판정 | 증거 |
|---|---|---|
| 1 입력 | 통과 | manifest.json, config.json, baseline-survey.json |
| 2 마스터 보존 | 통과 | 원본 해시 불변, 304객체/1393프레임 의미 서명 일치, 기존24검사, S1 RGB3쌍 동일 |
| 3 격리 | 통과 | test_isolation.py, 실제 차량/문/렌즈 임시 변이 후 원본 서명 동일 |
| 4 전진 | 통과 | 1009개 0.25프레임 표본, 연결점·차축/바퀴 접선·조향·컨테이너 관계 검사 |
| 5 정렬·문 | 통과 | f810정지,811–842개방,849까지 정지, 문/차체 간섭 검사 |
| 6 후진·접안 | 통과 | 5.2m 직선 후진, 후면x36/y29, 문 고정, 내부 두 팔레트 유지 |
| 7 공간·카메라 | 통과(프록시 범위) | space-validation.json, 사선 영상·접안 스틸 |
| 8 재개방·재실행 | 통과 | 새 프로세스 검증, 원본과 재생성 의미 동일, 데이터 수426객체/61Action/2Scene 유지 |
| 9 산출물 | 통과 예정 | 12fps253프레임 영상2개, 재개방 RGB16쌍, 정상속도 재생 기록, hashes.json |
| 10 경계 | 통과 | integration-proposal.md, boundary-states.json; 통합 미실행 |

실행 명령과 종료 코드: `review/check-runs.json`. 단위 검사7개 + 기존 회귀24개; 동작·공간 검사는 별도. 테스트 assertion과 허용 오차를 완화하지 않았다. 접지 검사는 회전된 wheel bounding box 대신 실제 정점과 지면 BVH 레이로 개선했다. 의미 서명은 프로세스마다 달라지는 session_uid/users를 제외하고 실제 속성·메시·Action·재질·표시·프레임 행렬을 비교한다.

### 동작 최대 측정값
{metrics}

공간 검사 {space['pair_checks']:,}쌍, 금지 겹침 최대 {space['maximum_forbidden_overlap']:.8f}m(수치 오차), 카메라 최소 여유 {space['camera_min_clearance']:.3f}m.

### 방법과 한계

전체648–900을0.25프레임 간격으로 검사했다. 실제 박스/메시 정점의 OBB 축·교차축·중심 분리축 투영을 사용했다. 박스는 정확하고 바퀴 등은 보수적 근사이며 연속 시간 정밀 충돌/타이어 동역학을 주장하지 않는다. 대표 트레일러 차축은 tandem 중점; tandem 타이어의 미세 scrub은 모델 범위 밖이다.

검사 쌍: 차량/컨테이너/문/화물 대 창고 바닥·벽·기둥·랙·받침판; 문 대 컨테이너 벽·바닥·지붕; 모든 바퀴끼리; 견인부 몸체 대 컨테이너 외피. 내부 제작 연결(차대·hitch·화물/팔레트), 도로·지면 접촉, 고정 시설끼리의 연결은 금지 충돌 쌍에서 제외했다. 지면 접지는 별도 BVH 검사다. 받침판과 컨테이너 바닥의 두께 겹침0.08m는 같은 높이1.92m의 지정 접속면으로 별도 기록했다. 창고 바닥1.86m와의 단차0.06m는 기존 상징 모델의 높이 관계이며 산업 기준이 아니다.

정적 Mesh/Material/World는 읽기 전용 공유, Object/Action/Camera/Curve/Collection은 독립이다. 새 Scene에서 원본의 움직이는 객체를 참조하지 않는다. 소유권 충돌, 외부 Scene에 재연결된 테스트 데이터, 미지원 driver/NLA/constraint는 변경 전에 거부한다.

원본 f648과 테스트 진입은 다르므로 단독 수용과 마스터 교체 가능성은 별개다. 관련 선택과 비용은 progress.md의 Ruling에 기록했다. 웹 코드·npm 빌드·실차 안전 검증·원본 통합·외부 업로드·커밋·push·PR는 실행하지 않았다.

시각 검토: 최종 접안 사선에서 차량, 열린 후면, 받침판, 입고 바닥을 함께 확인했다. 탑뷰 첫 프레임의 잘림을 보정했다. A/B/C/D 및 개방 전후는 review/oblique, review/top, contact-sheet.png에 있다. 최종 정상속도 재생 결과는 playback-check.json에 기록한다.

변경 파일: 이 폴더의 scripts, tests, config, source-map, manifest, 문서, 검토 .blend 및 증거. 원본 S4 폴더는 읽기 전용; 기존 테스트는 byte-identical staging 복사본으로만 실행했다. 최종 코드 검토 결과는 review/final-code-review.md에 추가한다.
'''
(r/'report.md').write_text(report,encoding='utf8')
(r/'README.md').write_text('''# S5 도크 테스트 후보

`master-with-s5-test-v001.blend`를 열면 테스트 Scene이 선택된다. 원본 `PNPLINE_MASTER_v005`도 같은 파일에 보존되어 있다. 테스트는648–900,12fps다. 사선은 `S5T__CAM_OBLIQUE`, 진단 탑뷰는 `S5T__CAM_TOP`이다.

- 영상: preview/s5-oblique.mp4, preview/s5-top.mp4
- 핵심 스틸: review/contact-sheet.png 및 review/oblique·top
- 검증: report.md, review/check-runs.json
- 원본과 차이/통합 범위: integration-proposal.md

재현은 설치된 Blender5.1.0과 Python3.13.9, ffmpeg7.1에서 수행했다. Pillow는 보고 이미지 비교에만 사용한다. 새 라이브러리/플러그인 설치는 없다. 아래 PowerShell 변수는 실행 환경에 맞춰 지정한다. `$r`은 이 폴더, `$source`는 최신 S4 원본, `$blender`는 설치된 Blender 실행 파일이다. 소스와 출력 파일이 같으면 빌더가 거부한다.

```powershell
& $blender --background --factory-startup $source --python-exit-code 1 --python "$r/scripts/build_s5_test.py" -- --config "$r/config.json" --output "$r/master-with-s5-test-v001.blend"
python -X utf8 "$r/scripts/run_checks.py" --blender $blender --source $source --candidate "$r/master-with-s5-test-v001.blend"
& $blender --background --factory-startup "$r/master-with-s5-test-v001.blend" --python-exit-code 1 --python "$r/scripts/render_s5_review.py" -- --scene S5_DOCK_TEST_v01 --output-dir "$r/preview" --camera oblique --animation
& $blender --background --factory-startup "$r/master-with-s5-test-v001.blend" --python-exit-code 1 --python "$r/scripts/render_s5_review.py" -- --scene S5_DOCK_TEST_v01 --output-dir "$r/preview" --camera top --animation
ffmpeg -framerate 12 -start_number 648 -i "$r/preview/oblique/%04d.png" -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart "$r/preview/s5-oblique.mp4"
```

재생성은 명시한 원본 파일 기준으로 권장한다. 현재 검토본에서 함수 `build(config)`를 실행해도 테스트 소유 데이터만 교체하며, 외부 참조/이름 충돌은 거부한다. `check_reproduction.py`가 실제 변이 및 재실행을 수행하되 파일에는 저장하지 않는다.

소스 생성기의 전체 삭제 코드나 orphan purge를 실행하지 않는다. 마스터 통합과 커밋은 이 산출물에 포함되지 않는다. `progress.md`에는 선택한 기준·설계 이탈·검토 판단과 비용이 남아 있다.
''',encoding='utf8')
print('REPORT WRITTEN',manifest['output_sha256'])
