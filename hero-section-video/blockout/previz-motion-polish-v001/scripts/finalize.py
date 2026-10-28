from pathlib import Path
import json,hashlib,sys
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));from motion import TimeMap
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cfg=json.loads((R/'config.json').read_text());results={v:json.loads((R/'review'/f'validation-{v}.json').read_text()) for v in ['A','B']}
for v,r in results.items():
 assert r['pass_all'] and r['blend_sha256']==sha(R/f'master-motion-polish-{v}.blend')
 assert json.loads((R/'review'/f'media-{v}.json').read_text())['blend_sha256']==r['blend_sha256']
for name,frames in [('s5-comparison',cfg['storyboard_source_frames']),('boundary-comparison',[96,216,456,648,900,1200]),('contact-comparison',[700.5450141107419,708.75,776.5])]:
 sheet=Image.new('RGB',(1440,len(frames)*294),(20,27,33));draw=ImageDraw.Draw(sheet)
 for row,f in enumerate(frames):
  for col,v in enumerate(['source','A','B']):
   im=Image.open(R/'review/stills'/v/f'source-{f:g}.png').resize((480,270))
   sheet.paste(im,(col*480,row*294+24));draw.text((col*480+8,row*294+6),f'{v} | source f{f:g}',fill='white')
 sheet.save(R/'review'/f'{name}.jpg',quality=92)
rows=[]
for i,(a,b) in enumerate(zip([0,96,216,456,648,900,1200],[96,216,456,648,900,1200,1392])):
 ms=[TimeMap(1392,cfg['easing'],cfg['compression_B'] if v=='B' else []) for v in ['A','B']]
 rows.append(f'| S{i+1} | {a}–{b} | {(b-a)/12:.3f} | {(b-a)/24:.3f} | '+ ' | '.join(f'{(m.forward(b)-m.forward(a))/24:.3f}' for m in ms)+' |')
metricrows=[]
for k,label in [('max_tyre_penetration_m','타이어 최대 관통'),('max_tyre_support_gap_m','타이어 최대 부양'),('max_wheel_xy_drift_m','바퀴 수평 위치 차이'),('max_hitch_error_m','견인점 오차'),('max_container_support_translation_error_m','컨테이너 지지 상대 위치'),('max_door_body_penetration_m','문–차체 관통'),('max_cargo_hand_support_error_m','화물–손 지지 오차')]:
 metricrows.append(f'| {label} | {results["A"]["metrics"][k]*1000:.4f} | {results["B"]["metrics"][k]*1000:.4f} |')
visual=R/'review/visual-review.json';complete=visual.exists() and json.loads(visual.read_text()).get('full_1x_playback_pass',False)
verdict='속도·이징 검증 후보 수용 가능 / 사용자 리듬 선택 대기' if complete else '증거 부족으로 판정 보류 — 전체 영상 재생 검토 대기'
readme=f'''# PNPLINE S1–S7 모션 폴리싱 v001

{verdict}

- A: `master-motion-polish-A.blend`, `preview/candidate-A.mp4` — 24fps / 1,393프레임 / 58.041667초.
- B: `master-motion-polish-B.blend`, `preview/candidate-B.mp4` — 24fps / 1,306프레임 / 54.416667초.
- `review.html`: 원본116.08초·기존2배속58.04초·A/B 비교, S5 및 구간 경계 실제 렌더.
- `event-map.csv`, `time-map-A/B.json` 및 CSV: 사건·모든 베이크 시점 대응.
- `s5-storyboard-map.json`: 원본 f672·720·732·766·842·900의 정확한 소수 프레임 대응과 가장 가까운 영상 프레임.
- `scroll-progress-map.json`: 최초–마지막 프레임 시간에 대한0–1 진행률. 최종 MP4의 마지막 프레임 노출1/24초는 별도.

Blender에서 A/B 중 하나를 열어 24fps, Frame Dropping으로 전체 재생합니다. 재생기에 추가 2배속을 적용하지 않습니다. 밀집 LINEAR 키는 원본 경로를 유지하기 위한 편집 가능한 베이크입니다. 설계 변경은 `config.json` 후 `scripts/build_candidates.py` 재실행으로 재현합니다. 접지 키는 Blender의 `FCurve.update()`가 가까운 키를 삭제할 수 있으므로 일괄 정리하지 마세요.

원본은 `../s5-integration-v001/master-s5-integration-v001.blend`이며 이 폴더의 `inputs/source.blend`와 SHA256이 같습니다. 원본은 수정하지 않았습니다. 사용자 승인으로 새 후보에만 도로 폭·경사와 바퀴 고도를 보정했습니다. 수평 동선, 차량/컨테이너 루트, 문 동작, 여섯 카메라 구도를 보존했습니다.

`review/master-contact-proposal.blend`, `failed-wheel-key-*.blend`, `*-failed-*`, `*-center-only.json`, `*-vertex-v1.json`은 **실패 원인 추적용 과거 시험 자료**입니다. 최종 파일이나 검증 근거로 사용하지 마세요. `hashes.json`, `validation-A/B.json`, `render-record-A/B.json`이 현재 후보를 식별합니다.

재현 순서(Blender5.1): `--factory-startup -b --python-exit-code 1 --python scripts/build_candidates.py`, 각 변형에 대해 `scripts/validate_candidates.py -- A` 또는 `-- B`, 통과 후 `scripts/render_candidates.py -- A B`, Python으로 `scripts/package_media.py A B`. 비교 스틸은 `scripts/render_stills.py`, 대응표는 `scripts/write_maps.py`, 인계는 `scripts/finalize.py`입니다. 실행 스크립트는 자신의 위치에서 출력 루트를 찾습니다.

상세 검사·한계는 `report.md` 참조. 공개용 Scroll World 속도/사용자 경험 승인은 별도입니다.
'''
(R/'README.md').write_text(readme,encoding='utf8')
report=f'''# 모션 폴리싱 검증 보고서

판정: **{verdict}**

## 기준과 보존
HEAD4993e2f5ce299e7e119eb7b57a4098d7922a7c1f. 기준 SHA256 `{cfg['source_sha256']}`. 입력 비교4종은 Action·형상·계층·마커 및1,393정수프레임 평가에서 동일했습니다(`review/source-comparison.json`). 기존34개 회귀 검사 통과(`review/baseline-tests.log`). 기존 무관한 변경은 `inputs/baseline-status.txt`에 기록. 원본·기존2배속 영상은 기존 렌더의 이미지별 해시를 검증한 뒤 재사용했고 새 후보 프레임과 섞지 않았습니다.

## 시간 설계
| 구간 | 원본 프레임 | 원본12fps 초 | 기존24fps 초 | A 초 | B 초 |
|---|---|---:|---:|---:|---:|
{chr(10).join(rows)}

구간 표는 경계 간 시간입니다. 전체 MP4는 마지막 프레임 노출1/24초를 포함합니다. A58.041667초, B54.416667초. B는 원본 이동 구간150–216,236–440,466–510,672–732,966–985,1074–1090,1268–1392에서 총87프레임 상당을 단축합니다. 공통 단조 증가 시간 사상으로 카메라·차량·문·화물·장비를 함께 평가합니다. 전체 Linear→Bezier 변환이나 단순 FPS 조작으로 폴리싱을 대체하지 않았습니다.

## 구현과 원인 분석
원본은 이미 일부 cubic easing을 베이크했습니다. 실제 시작·종료 동작의 시간 밀도만 선택적으로 조절했고, 카메라에는 제한된 Hermite 접합을 적용했습니다. f648–649의 원본 정지는 실패 재현 후 수정했습니다. S5 여섯 시점의 비바퀴 오브젝트 행렬과 렌즈는 원본과 동일합니다. 바퀴 고도는 아래 명시한 승인 범위입니다.

사용자가 추가 승인한 접지 수정: 부두→도로16.5cm 단차, 선회 시 좁은 도로 이탈, 도크 진입 단차를 연속 노면으로 연결했습니다. 도로 폭은2.5→5m. 원본 메시를 보존하고 새 `MP_CONTINUOUS_ROAD`를 표시합니다. 차량 수평 궤적과 루트를 바꾸지 않고 전체 부모 변환을 역산하여 바퀴의 월드 수직 위치만 보정합니다. 기존 부모 pitch 때문에 localZ 단독 보정은 잘못된 접근이었습니다. 경사 경계에는 정확한 분할선을 넣어 미세 단차를 없앴습니다.

바퀴 중심점 아래 높이 비교는 경사에서 타이어 관통을 놓쳤습니다. 이를 과거 진단값으로 보존하고 실제 하부 타이어 꼭짓점과 **표시되는** 노면의 최소 간격에 동일2mm 기준을 적용했습니다. f776.5에서16.2336mm 관통의 RED 기록 후 수정했습니다. Blender5.1 `FCurve.update()`는1/128간격 키를 삭제하므로 이미 정렬된 고유 float32 LINEAR 키는 재정리하지 않습니다. 재개방 시 밀집 키의 유지도 독립 검토했습니다.

## 저장본 검사
A {results['A']['samples']:,}시점, B {results['B']['samples']:,}시점. 원본1/4프레임, 모든 출력 정수프레임, S5 원본1/16프레임, 사건±2프레임의1/16 및 별도 발견한 단차 실패 시점을 포함합니다. 저장본은 독립 Blender 프로세스에서 다시 열었습니다. 원래 마스터의24개 동작 회귀 검사를 원본 시간→출력 시간 어댑터로 A/B 각각 실행했고 모든 기존 단언을 그대로 통과했습니다(`review/master-regression-A/B.json`).

| 항목 | A mm | B mm |
|---|---:|---:|
{chr(10).join(metricrows)}

카메라 구간 및 패치 접합에는 비영속도·급격한 위치 변화 검사를 적용했습니다. 추가 독립 검토에서 회전·렌즈 변화도 조사했습니다. 선박 선저/갑판의 구면 수면 관계, 카메라–오브젝트 경계 상자 여유, 사건 순서, 승인 외 메시 동일성도 통과했습니다. 자세한 값은 `review/validation-A.json`, `review/validation-B.json`에 있습니다.

추가 독립 검토는 변형별4,053시점에서 전체 타이어 꼭짓점을 조사했습니다. 경계 인접 추가 시점을 포함한 최대 관통은 A0.1443mm/B0.1215mm로2mm 이내였습니다. 위 표는 주 검증 스크립트의 표본 결과이며 연속시간 전체 상한이 아닙니다. 별도 검토 기록은 `review/independent-review.md`입니다. 최종 A/B MP4는 브라우저에서 추가 배속 없이 전체 재생되었고 played 범위0–끝 및 ended=true, error=null을 확인했습니다. 대표 재생 화면과 실제 렌더 스틸을 시각 점검했습니다(`review/visual-review.json`).

## 수용 기준과 증거
| AC | 결과/증거 |
|---|---|
|1|원본4종 비교 및 입력 해시 / source-comparison.json|
|2|원본·기존2배속·A/B 4영상 / preview, media-*.json|
|3|카메라 정지 RED→GREEN, 구간·패치 연결 / camera_joins|
|4|시간 사상9개 단위검사 RED→GREEN, 양의 시간 도함수 / tdd-red.log, tdd-green.log|
|5|타이어 형상 접지·견인점·문·컨테이너·화물·수면 / validation-A/B.json|
|6|6개 정확한 소수 프레임 대조 / s5-storyboard-map.json, review/s5-comparison.jpg|
|7|동일 시간 사상 및 사건별 대응 / event-map.csv, boundary-comparison.jpg|
|8|독립 프로세스 재개방 및 전체 영상1x 재생 / validate-A/B.log, visual-review.json|
|9|전체 영상·시간/사건/스크롤 표 / review.html 및 대응표|
|10|Blender·스크립트·설정·검증·이미지별 렌더 해시 / build-A/B.json, render-record-A/B.json, hashes.json|

## 실행 환경 및 한계
Windows, Blender5.1.0, Workbench960×540, MP4 H.264/yuv420p24fps. 부가 기능의 백그라운드 GPU 오류를 피하도록 독립 검사는 `--factory-startup` 사용. Python 단위검사, Blender `--python-exit-code 1`, FFmpeg 인코딩 후 FFprobe 프레임/길이 확인과 전체 디코드. 자동 검사와 영상 재생은 유한 표본 검사이며 연속시간 전체의 수학적 무충돌 증명은 아닙니다. 접지 검사는 저폴리 타이어 하부 꼭짓점 기준이고 자잘한 표면 접촉 전체를 물리 시뮬레이션한 결과가 아닙니다.

원본의 포장 접기/테이프·세부 손 동작은 이미 deferred 상태입니다. 구현된 동작의 타이밍을 다듬었으며 미구현 디테일을 완성했다고 주장하지 않습니다. 밀집 베이크는 재현 가능하지만 소수 키 애니메이션보다 수동 편집이 번거롭습니다. Git worktree 생성은 환경 권한 문제로 실패하여 전용 새 폴더 격리를 사용했습니다. 커밋·푸시·배포는 하지 않았습니다.
'''
(R/'report.md').write_text(report,encoding='utf8')
manifest={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in R.rglob('*') if p.is_file() and (p.suffix in ['.py','.md','.json','.csv','.html','.mp4','.jpg'] or p.name in ['master-motion-polish-A.blend','master-motion-polish-B.blend']) and p.name!='hashes.json' and '__pycache__' not in str(p)}
(R/'hashes.json').write_text(json.dumps({'algorithm':'SHA256','source_sha256':sha(R/'inputs/source.blend'),'files':manifest},indent=2),encoding='utf8');print(verdict)

