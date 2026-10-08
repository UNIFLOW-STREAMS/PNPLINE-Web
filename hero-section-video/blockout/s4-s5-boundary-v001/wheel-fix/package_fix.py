import json,hashlib
from pathlib import Path
R=Path('F:/pnpline-landing/hero-section-video/blockout/s4-s5-boundary-v001');D=R/'wheel-fix'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((D/'validation.json').read_text());m=v['metrics'];newsha=sha(R/'master-s4-s5-boundary-v001.blend')
assert v['sha256']==newsha
assert m['wheel_ground_abs_gap_max']<.002 and not v['collisions'] and not v['camera_collisions']
assert m['hitch_gap_max']<.002 and m['container_relative_drift_max']<.002
assert sha(D/'before-wheel-fix.blend')=='cdf33f07e10327c5ab3d1557f9721d37e4aca997108badf960fa5b19ec2cd3c6'
assert sha(R/'inputs/master-s4-fix.blend')=='2ba73fc3baca6b3617ac534349d0d794c2dc744b48e50ccc66b685f07572e2ff'
(D/'delivery-check.json').write_text(json.dumps({'passed':True,'blend_sha256':newsha,'metrics':m},indent=2))
report=f'''# S4–S5 차량 접지·겹침 수정 완료 — 2026-10-08

사용자 요청: 시작 시 묻혔다가 올라오는 바퀴, 차량이 겹쳐 보이는 현상 수정.
현재 작업본: `master-s4-s5-boundary-v001.blend` (SHA-256 `{newsha}`).
Blender 새 창에 이 저장본을 f596으로 열었다. 카메라 구도 선택은 기존 검토 상태를 유지한다.

## 원인과 수정

- 이전 버전은 f608 이전 바퀴가 부두에 약 0.20m 묻힌 상태였고 f608–620에서 높이 보정이 서서히 적용되었다. f620의 정상 대기 높이를 f0부터 유지하도록 수정했다.
- 트랙터 1개와 트레일러 1개로 구성된 단일 차량이다. 중복 차량을 삭제한 것이 아니다. 지름 0.8m 뒷바퀴의 축 간격이 0.5m여서 같은 쪽 타이어가 0.3m 겹쳤다. 축 간격을 1.0m로 바꿔 타이어 사이에 0.20m 틈을 확보했다.
- 운전석과 차대의 같은 평면에 겹친 측면을 정리했다. 운전석 상단과 유리 위치는 유지했다.
- 부두/도로 높이 차 및 후속 주행에서도 바퀴가 파묻히거나 떠 있지 않도록 바퀴별 로컬 Z 보정을 f648–1392에 적용했다. 1/16 프레임에서 노면을 계산하고 키 단순화 오차를 0.00001m 이하로 제한했다.
- 차량 본체의 f620 이후 경로·회전, 카메라·렌즈, 컨테이너·인양 장치·환경은 보존했다. 바퀴 간격과 운전석 형상은 차량의 전 구간에 적용된다.

## 검증

- 새 회귀 검사 5/5 통과. 수정 전 저장본에서 4개 실패를 재현했다.
- 초기 f0–648 접지 검사 최대 오차 약 0.00002331m (1/4 프레임 간격).
- f648–1392 접지 검사 최대 오차 약 0.00010032m (1/16 프레임 간격).
- 기존 Scene 회귀 검사 24/24 통과.
- f0–1392 모든 정수 프레임에서 보호 객체와 카메라·렌즈가 정확히 일치했다. f620 이후 차량 두 루트의 변환도 일치했다. 객체 목록과 비수정 객체 데이터 일치 검사 통과.
- 새 저장본 경계 검사: 차량/시설 및 카메라 충돌 각각 0건; 히치 최대 오차 {m['hitch_gap_max']:.9f}m; 화물 상대 변환 오차 {m['container_relative_drift_max']:.9f}.
- 독립 리뷰에서 f721 이후 바퀴 보정이 고정되는 문제를 발견하여 끝 프레임까지 확장했다. 재검토에서 f732·800·1392 및 추가 구간을 확인했고 미해결 구현 지적은 없다.
- 현재 저장본으로 f540–792 전체 253프레임을 렌더했다. 12fps, 768×432, 21.083333초. 전체 영상 디코딩 성공 및 초기·안착·도로 이음부·후속 주행 정지 화면을 직접 확인했다.

검사는 바퀴 메시 최하점과 중심 아래 노면의 높이를 비교하는 블록아웃 접지 검사다. 노면 단차의 실제 타이어 변형·완전한 연속 물리 시뮬레이션을 보장하지 않는다.

## 산출물

- `wheel-fix/after.mp4`: 이번 수정 검토 영상 f540–792.
- `preview/after.mp4`: 기존 비교 범위 f596–792의 수정 영상으로 갱신.
- `wheel-fix/before.mp4`, `wheel-fix/before-wheel-fix.blend`: 이번 수정 직전 백업.
- `wheel-fix/closeup.png`: f596 차량 확대 검토 이미지. 렌더 전용 임시 카메라는 저장본에 추가하지 않았다.
- `wheel-fix/green.log`, `regression.log`, `preservation.json`, `validation.json`, `delivery-check.json`: 이번 수정의 현행 검증 기록.

이 보고서가 이전 완료 보고서를 대체한다. `wheel-fix/prior-report.md`와 기존 `review/`, `tests/`, `scripts/run_final.py`의 기록·워크플로는 **수정 전 카메라 경계 후보**에 대한 이력이다. 이번 변경의 재현·검증은 아래 현행 워크플로를 사용한다.

## 재현·검증

`wheel-fix/fix_vehicle.py`는 반드시 `wheel-fix/before-wheel-fix.blend`를 Blender 백그라운드 모드로 연 상태에서 실행한다. 입력 경로와 SHA-256을 검사하며 주 작업본을 갱신한다. 현재 작업본을 입력하면 중복 적용을 차단한다.

검증: 저장된 주 작업본에서 `wheel-fix/test_vehicle.py`와 `regression/scripts/test_scene.py`를 각각 실행한다. `wheel-fix/check_preservation.py`는 수정 전 백업을 로드한 프로세스에서 실행해 두 파일을 비교한다. Blender에는 `--factory-startup -b <blend> --python-exit-code 1 --python <script>`를 사용한다.
'''
(R/'report.md').write_text(report,encoding='utf8')
(R/'README.md').write_text('''# S4–S5 boundary v001 — 차량 접지·겹침 수정본

2026-10-08 사용자 후속 요청 반영 완료.

- 작업본: `master-s4-s5-boundary-v001.blend`
- 이번 수정 영상: `wheel-fix/after.mp4` (f540–792)
- 기존 범위 영상: `preview/after.mp4` (f596–792, 갱신됨)
- 수정 직전 백업: `wheel-fix/before-wheel-fix.blend`
- 결과·범위·재현 및 검증 방법: `report.md`

현행 검증은 `wheel-fix/test_vehicle.py`, `wheel-fix/check_preservation.py`, `regression/scripts/test_scene.py` 및 `wheel-fix/validation.json`을 사용한다. 이전 `tests/`, `review/`, `scripts/run_final.py`는 수정 전 후보의 이력이며 이번 저장본을 재현하는 워크플로가 아니다.
''',encoding='utf8')
c=json.loads((R/'boundary-contract.json').read_text());c['blend_sha256']=newsha;c['wheel_fix']={'date':'2026-10-08','initial_root_height_frames':[0,620],'wheel_z_frames':[648,1392],'wheel_sampling_per_frame':16,'tandem_axle_distance_m':1.0,'report':'report.md'};(R/'boundary-contract.json').write_text(json.dumps(c,indent=2),encoding='utf8')
with (R/'progress.md').open('a',encoding='utf8') as f:f.write('\n2026-10-08 vehicle follow-up: fixed initial ground penetration, tandem tire overlap, cab/chassis coplanar strip and all later wheel support through1392. Fresh5/5 + Scene24/24, protected frames pass. Reviewer P2 corrected and rechecked; no pending finding. Current evidence: wheel-fix/. Prior scope restrictions and early penetration deferral superseded by this user request.\n')
print('CURRENT_BLEND',newsha);print(json.dumps(m,indent=2))

