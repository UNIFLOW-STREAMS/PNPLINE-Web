"""Compose measured evidence and board comparisons, retaining the approval proposal."""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1];H=R.parent/'plan/pnpline-s4-camera-revision-handoff-v0.1'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
D=load(R/'review/validation-final.json');A=load(R/'review/states-final.json');B=load(R/'review/baseline-full.json');check=load(R/'review/reopen-check.json');play=load(R/'review/playback-check.json')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
frames=[456,499,522,555,648];sheet=Image.new('RGB',(1500,1830),'#e9eef1');draw=ImageDraw.Draw(sheet)
for row,f in enumerate(frames):
 for col,label in enumerate([f'K{row+1} board (no frame / notes)',f'Original f{f}',f'Final f{f}']):draw.text((col*500+10,row*366+7),label,fill='#18303e',font=font)
 images=[Image.open(H/f'references/s4-0{row+1}.png').crop((17,55,1430,987)),Image.open(R/f'review/before/f{f:04}.png'),Image.open(R/f'review/final-continuity/f{f:04}.png')]
 for col,img in enumerate(images):
  tile=ImageOps.contain(img,(492,326));sheet.paste(tile,(col*500+4+(492-tile.width)//2,row*366+34+(326-tile.height)//2))
sheet.save(R/'review/K1-K5-comparison.png')
# Top view: actual sampled camera route and fixed relationships in US local frame.
im=Image.new('RGB',(1200,980),'#edf1f3');dr=ImageDraw.Draw(im)
def xy(x,y):return (int(260+(x+10)*8.5),int(520-y*8.5))
dr.text((22,16),'S4 camera path + approved S5 join (US local top view)',fill='#18303e',font=font)
for x in range(-20,81,10):dr.line([xy(x,-42),xy(x,56)],fill='#dbe0e4');dr.text(xy(x,-44),str(x),fill='#6b7a82',font=small)
for y in range(-40,51,10):dr.line([xy(-20,y),xy(80,y)],fill='#dbe0e4')
dr.rectangle([xy(-17,12),xy(17,4)],fill='#c4cbd0',outline='#576975',width=2)
dr.rectangle([xy(-7,2.6),xy(7,-2.6)],fill='#205472')
dr.rectangle([xy(36,39),xy(68,25)],fill='#b1c7b7',outline='#42674d',width=2)
dr.line([xy(0,9),xy(26,9),xy(33,17),xy(36,29)],fill='#687b88',width=7)
for x in [-2,3.5]:
 for y in [5,12]:
  a,b=xy(x,y);dr.rectangle((a-4,b-4,a+4,b+4),fill='#b28e29')
points=[xy(*r['us_camera'][:2]) for r in D['quarter_frames'] if 456<=r['frame']<=648];dr.line(points,fill='#d75531',width=3)
points=[xy(*r['us_camera'][:2]) for r in D['quarter_frames'] if 648<=r['frame']<=672];dr.line(points,fill='#466acb',width=4)
for f,k in zip(frames,['K1','K2','K3','K4','K5']):
 r=next(r for r in D['quarter_frames'] if r['frame']==f);a,b=xy(*r['us_camera'][:2]);dr.ellipse((a-5,b-5,a+5,b+5),fill='#d75531');dr.text((a+8,b-12),f'{k} f{f}',fill='#9b361e',font=small)
dr.text(xy(39,35),'WAREHOUSE',fill='#264c33',font=font);dr.text(xy(-15,10),'QUAY',fill='#18303e',font=small);dr.text(xy(-6,1),'SHIP',fill='white',font=small)
dr.text((20,920),'Orange: S4   Blue: approved f649-671 join   All asset geometry/routes unchanged',fill='#18303e',font=font)
dr.text((20,951),'Guide only. Actual camera height, lens and aim are in camera-before-after.json.',fill='#18303e',font=small);im.save(R/'review/camera-path.png')
occ=Image.new('RGB',(1440,918),'#edf1f3');od=ImageDraw.Draw(occ)
for i,(f,label) in enumerate([(581,'Transient cargo / pole'),(602,'Transfer / bed still readable'),(618,'Transient cab / bed clear'),(632,'Seat / no cab pole occlusion'),(648,'Separated spreader / exit road'),(672,'Original S5 restored')]):
 x=(i%3)*480;y=(i//3)*459;od.text((x+8,y+8),f'f{f}: {label}',fill='#18303e',font=small);tile=Image.open(R/f'review/final-continuity/f{f:04}.png').resize((480,270));occ.paste(tile,(x,y+37))
 od.text((x+8,y+324),'Finite ray estimates accompany actual renders.',fill='#405663',font=small)
occ.save(R/'review/occlusion-review.png')
entry=Image.new('RGB',(960,1176),'#edf1f3');ed=ImageDraw.Draw(entry)
for row,f in enumerate([457,458,459,470]):
 for col,(label,folder) in enumerate([('Before roll fix','after'),('Final smooth entry','final-continuity')]):
  ed.text((col*480+8,row*294+3),f'{label} / f{f}',fill='#18303e',font=small)
  entry.paste(Image.open(R/f'review/{folder}/f{f:04}.png').resize((480,270)),(col*480,row*294+24))
entry.save(R/'review/entry-roll-comparison.png')
(R/'camera-before-after.json').write_text(json.dumps(D,indent=2),encoding='utf-8')
if not (R/'review/approval-proposal.md').exists():(R/'review/approval-proposal.md').write_text((R/'report-s4-camera.md').read_text(encoding='utf-8'),encoding='utf-8')
def vec(v):return '('+', '.join(f'{a:.3f}' for a in v)+')'
def ranges(items):
 out=[]
 for i in items:
  if out and i==out[-1][1]+1:out[-1][1]=i
  else:out.append([i,i])
 return ', '.join(str(a) if a==b else f'{a}–{b}' for a,b in out) or '없음'
rows=[]
for f in frames:
 q=next(q for q in D['quarter_frames'] if q['frame']==f);obs=next((o for o in D['observations'] if o['frame']==f),None)
 rows.append(f'| {f} / {f/12:.3f}s | {vec(q["us_camera"])} | {vec(q["t"])} | {q["lens"]:.3f} |')
metrics=[]
for f in frames[1:]:
 o=next(o for o in D['observations'] if o['frame']==f)
 for n in ['A02_SHIP','A01_CONTAINER','A03_TRACTOR','A03_TRAILER','E08_WAREHOUSE']:
  b=o['bounds'][n];metrics.append(f'| {f} | {n} | {vec(b)} | {(b[2]-b[0])*100:.1f}% |')
boundary=[]
for f in ['456','648','672']:
 for tag in ['before','after']:
  b=D['boundaries'][f][tag];boundary.append(f'| {f} {tag} | {vec(b["position"])} | {vec(b["incoming_velocity"])} | {vec(b["outgoing_velocity"])} | {b["incoming_angle"]:.3f} / {b["outgoing_angle"]:.3f} | {b["lens"]:.1f} |')
sha=check['final_blend_sha256'];obs=D['observations'];sweeps={n:ranges([o['frame'] for o in obs if 532<=o['frame']<=648 and o[n]['crane_fraction']>.15]) for n in ['cab','cargo']}
text=f'''# S4 카메라 수정 결과

판정: **기술적 수용 가능**. 지정한 `master-s4-fix.blend`에 S4 수정과 사용자가 승인한 S5 초반 접합을 저장했다. 독립 검토에서 발견한 진입 롤 급변을 수정했으며, 보강한 회귀 검사를 포함해 37개 검사를 통과했다. 운영 공개·상세 자산 제작 승인이 아니다.

## 결과와 재생

- 최종 Blender: `master-s4-fix.blend` — SHA256 `{sha}`.
- 최종 S4: `preview/s4-after.mp4` — 960×540, 12fps, f456–648 포함 193프레임 / 16.083초.
- S3 말미→S4→S5: `preview/s3-tail_s4_s5-head.mp4` — f444–696 포함 253프레임 / 21.083초.
- 원본: `preview/s4-before.mp4`. 보드 대조: `review/K1-K5-comparison.png`. 실제 경로: `review/camera-path.png`. 가림 검토: `review/occlusion-review.png`.
- `review/candidate-target.blend`와 `s4-target-review.mp4`는 **승인 전 S4 검토안**이다. S5 미접합 상태이므로 최종 재생에는 사용하지 않는다. `candidate-limited.blend`는 원래 B45 유지로 AC-5가 미충족인 대안이다. 이력 보존용이다.

## 기준과 범위

작업 기준은 사용자 지정 저장본 SHA256 `63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976`이며 `inputs/base-s4.blend`로 보존했다. HEAD `6079b392d7de54509ed50454ddd2745273cc0078`, 기존 S2/S3·사용자 변경을 되돌리지 않았다. 녹화 19-35-47은 같은 카메라 상태를 슬라이더로 촬영했다는 사용자 확인을 받았다. 30fps 녹화의 초수를 12fps Master로 매핑하거나 리타이밍하지 않았다. 입력 자료 14/14 해시 일치.

Master 범위0–1392, fps12, B34=456/B45=648. 실제 이벤트: 정박510, 인양532 이후, 상승끝555, 수평이송끝599, 안착632, 스프레더 재상승637 이후, 차량출발649. 모두 동일하다.

사용자는 “승인: S5 초반 접합까지 수정”으로 f649–671 카메라·타깃·렌즈 변경을 허용했다(`review/approval-s5-join.json`). f672부터 카메라·타깃·렌즈가 원본 평가값과 정확히 같다. S3 변경은 없다. 변경 키: 위치·회전/타깃 f458–671의214프레임, 렌즈213프레임. 비카메라 전1393프레임 변화0; 형상·재질·동작·환경·프레임 경계·카메라 클립 설정 동일. `master_version=v005`는 기준 씬 이력을 유지하며 새 `s4_camera_source`와 `s4_review_status`가 이번 수정을 식별한다.

Blender5.1.0 / hash adfe2921d5f3, Windows PowerShell, Python기존설치, ffmpeg7.1. 추가 설치·유료 서비스·커밋·push·PR·웹빌드·배포 없음. 사용자가 볼 수 있도록 최종 파일을 Blender에 열었다.

## 원인과 수정

원본은 f510의 큰 후퇴·상승과 32mm 광각화 뒤 부두 내륙의 근경으로 돌아와, 전경에서 선박이 잘리고 하역 대상 재확대가 커졌다. 실제 렌더에서 준비 중 화물·받을 차량 크롭, 후반 운전석 기둥 가림, 마지막 진출 도로 이탈을 확인했다. 초기 가설을 실제 상태·렌더로 검증했으며 장비를 옮기거나 숨기지 않았다.

카메라는 f499에서 선박 전체와 부두→도로→물류센터 관계를 공개하고 f522 정박 상태에 접근한다. K3→K4는 바다 쪽에서 선수 바깥을 돌아 부두 쪽으로 연속 이동한다. 마지막은 원래보다 넓고 높은 구도로 운전석·적재 화물·분리 장치·배·진출 도로를 함께 남긴다. 위치/시선 40mm 후보를 먼저 시험한 뒤 공개32mm→준비40mm→후반32mm를 채택했다. 줌만으로 대체하지 않았고 센서36×24/AUTO·shift0·clip.08–1500은 보존했다.

S4는 f457 원본 위치와 접선을 받아 US지역의 Hermite 경로를 매 프레임 LINEAR 키로 베이크했다. 원본의 롤과 롤 속도도 이어받아 f480까지 부드럽게 줄였다. 관찰 지점마다 정지시키는 ease를 넣지 않았다. f648 종료와 원본 S5 사이의 차이는 f649–671에서 국소 Hermite 오프셋으로 줄이고 f672에서 0이 된다. S4 바깥 전역 spline을 재계산하지 않았다.

## K1–K5 대조

| 관찰 상태 | 결과 | 남은 보드/형상 차이 |
|---|---|---|
| K1 f456–480 | S3 종료 구도를 그대로 받아 선수·갑판·선측을 유지하며 항만 공개로 이동 | f456은 경계 보존을 우선했으며 보드의 큰 선체·높은 선교 비례는 복제하지 않음 |
| K2 f499 | 선박 전체가 테두리 안에 남고 부두·도로 굴곡·창고가 동시 식별됨 | 창고 오른쪽 끝은 일부 잘림. 모든 내부 작업 공개는 요구되지 않음 |
| K3 f510–532 | 정박 후 f522부터 동일 화물·스프레더·받을 차량이 동시 관찰 가능, f532 인양 시작도 이어짐 | 원래 갑판의 이웃 적재물과 스프레더가 화물 일부를 가리지만 화물과 받을 대상의 관계는 읽힘 |
| K4 f533–632 | 화물·차량·적재면 경계상자 크롭 없음, 연속 인양·이송·하강 추적 | 회전 중 짧은 기둥 스침은 남음. 아래 실제 가림 범위를 공개함 |
| K5 f638–648 | 화물이 차량에 안착하고 스프레더만 올라가는 간격, 운전석과 트레일러, 남겨진 배와 화면 왼쪽 진출 도로가 읽힘 | 창고 건물은 카메라 뒤로 벗어나지만 K2에서 확인한 진출 도로 방향은 남음. 보드의 상세 항만 규모·간판은 범위 밖 |

실제 위치와 렌즈(타깃 world; 위치 US지역; 전체 world/회전은 JSON):

| 원본 프레임 / 절대시간 | 위치 US지역 | 타깃 world | 렌즈mm |
|---|---|---|---|
{chr(10).join(rows)}

투영 경계상자는 가시 픽셀 점유율이 아니다. `[xmin,ymin,xmax,ymax]`, 화면 아래쪽이y0이며0–1범위 밖 값은 잘림을 뜻한다. K2에서 선박 폭이 약24% 이상이고 전체가화면내에 남는다. 아래 원시값과 렌더를 함께 대조한다.

| 프레임 | 대상 | 정규화 경계 | 투영 폭 |
|---|---|---|---|
{chr(10).join(metrics)}

## 가림과 연결 검사

f532–648 모든 정수 프레임에서 화물·트랙터·트레일러 크롭0. K3 준비 f522–532, 인양 f533–555, 이송 f556–599, 하강 f600–632, 분리 f638–648을 정상 FPS 영상과 사건 상태로 대조했다.

외부 기둥/붐의 가중 표면 레이 가림이15%를 넘는 구간: 화물 **{sweeps['cargo']}** (4/12초와9/12초, 최대38.4%), 운전석 **{sweeps['cab']}** (14/12초, 최대40.2%). 실제 렌더 f581/f602/f618에서 화물 또는 받는 적재면은 계속 추적 가능하다. 기둥 스침은 남지만 인양 시작f532, 접촉 전후f631–632 및 분리f638–648에는 운전석 기둥 가림0, 화물최대3.28%이며 접촉 관계가 보인다. `occlusion-review.png`에 가장 가린 장면과 핵심 순간을 함께 제시했다. 물체명별 기여는 JSON `blockers`에 있다.

S5 f649–671은 부드럽게 기존 추적에 접합된다. f672 이후 원본 S5에서 움직이는 화물 앞을 기둥이 스치는 구간은 그대로다. 이는 승인한 접합 밖의 기존 구도이며 S4의 안착·분리 시점을 가리지 않는다.

카메라 f452–684의 1/4프레임 간격 검사에서 점+0.12m 여유 OBB 충돌은 0회이며, 최대 이동은 1.593m/frame, 최대 최단 회전은 {max(r.get('angular_speed',0) for r in D['quarter_frames']):.3f}도/frame이다. 정수 전 구간의 기존 연속성 검사도 통과했다. 각속도는 q와 -q가 같은 회전이라는 점을 반영하며, 해당 검사 오류는 별도 RED→GREEN 회귀 시험으로 고쳤다. 유한 표본/OBB 검사는 정확한 연속 체적 충돌의 수학적 증명은 아니다.

독립 검토에서 지적한 첫 수정 프레임 f458의 롤 급변도 해소했다. 원래 US 업벡터로 즉시 바뀌던 동작을 원본 롤과 속도를 이어받는 방식으로 바꿨다. f457→458 회전량은 약 5.532도에서 0.79도로 낮아졌으며, 첫 진입 구간의 프레임당 회전량 변화가 1도를 넘지 않는 회귀 검사를 추가했다. 검사 실패값은 4.838도였고 수정 후 통과했다. `review/entry-roll-comparison.png`에 실제 수정 전후 프레임을 비교했다.

| 경계 | 위치 world | 진입속도 world/frame | 이탈속도 world/frame | 진입/이탈 각도 deg/frame | 렌즈mm |
|---|---|---|---|---|---|
{chr(10).join(boundary)}

B34 이전·이후 값은 원본과 동일. B45 원본 대비 위치15.906m, 타깃5.017m, 렌즈-8mm의 변경은 승인된 S5 접합으로 연결했다. 20프레임 후보 가속도.182m/frame²보다24프레임 후보.130이 기존.15기준을 만족해2초 접합을 채택했다. 이웃키 보존과 복귀 지점의 평가값은 `camera-before-after.json`에 기록했다.

## AC 판정

| AC | 상태 | 증거 |
|---|---|---|
| AC-1 기준식별 | 충족 | baseline-inspection.json, input-verification.json, 사용자 동일상태 확인 |
| AC-2 입항·연결 공개 | 충족 | K1/K2 비교, f456–522 연속 렌더, K2 선박/도로/창고 검사 |
| AC-3 정박·준비·인양 | 충족 | f510–555 같은 화물/차량 동시 관찰 및 원본 이벤트 동일 |
| AC-4 인계·가림 | 충족, 중간 스침 공개 | 모든 정수프레임 크롭0, 접촉·분리 무운전석가림, 실제 가림 비교 |
| AC-5 출발·S5 | 충족 | 사용자 f649–671 승인, f648전후 연결 영상, f672 정확복귀 |
| AC-6 범위·동일성 | 충족 | 전체1393프레임 noncamera0차이, 미승인카메라0차이, 정적 형상/재질 동일 |
| AC-7 연속·접근 | 충족(유한 검사 범위) | 기존 전구간 연속성/경계가속도,{len(D['quarter_frames'])}개 1/4프레임 표본, OBB0 |
| AC-8 재현·증거 | 충족 | 새 프로세스 재개방13개 RGB완전동일, 소스재실행 전1393상태 완전동일, 영상ffprobe/재생 |

## 실행과 테스트

실행 예시(PowerShell, 이 버전 폴더에서; 모든 실제 로그는 `logs/`):

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup inputs/base-s4.blend --python-exit-code 1 --python scripts/revise_s4.py -- final
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup master-s4-fix.blend --python-exit-code 1 --python scripts/test_scene.py
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup master-s4-fix.blend --python-exit-code 1 --python scripts/test_s4.py -- final
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup master-s4-fix.blend --python-exit-code 1 --python scripts/validate_s4.py -- final
& 'C:\\ProgramData\\miniconda3\\python.exe' -X utf8 scripts/reopen_check.py
```

1. 기존 기준본 24/24 통과. S4 검사에서 기준본은 5개가 실패했고, 수정한 카메라는 8개를 통과했다. 이후 독립 검토의 진입 롤 문제를 재현하는 검사를 추가해 최종 S4 검사 9/9가 통과했다.
2. 내부 벽을 외부 가림으로 집계하던 레이 검사 결함: 별도 panel 회귀RED→2/2GREEN; 원본실패도 수정된 검사로 다시 확인. 허용수치 완화없음.
3. 회전 부호 동치 검사RED→2/2GREEN.
4. 승인 전 목표안의 기존연속성 f649에서15.727m점프 FAIL → 승인후 최종24/24GREEN.
5. 최종 저장본의 신규·기존·검사 유틸 테스트 총 37개가 통과했다. 롤 수정 후 새로 재개방한 13개 화면의 RGB, 소스 재실행의 전체 평가 상태, 원본 백업 해시가 모두 일치했다.
6. 설치된 Chrome에서 seek 없이 실제 1배속으로 완주했다. 디코딩 프레임은 before 193 / after 193 / connection 253개다. 최종 재생의 표시 드롭은 {', '.join(r['label']+' '+str(r['result']['dropped'])+'개' for r in play['reports'])}였다. 원본 영상의 표시 드롭은 파일 프레임 유실과 다르며 ffprobe상 원본 193개 프레임은 정상이다. 로그와 `playback-check.json`의 디코딩 확인을 영상의 미적 판정과 구분한다.

최종 독립 검토는 Critical 0건, Important 1건, Minor 0건이었으며 Important인 진입 롤 문제를 한 차례 수정했다. 새 회귀 검사의 RED→GREEN과 전체 37개 검사, 재개방 및 소스 재현으로 수정 결과를 확인했다. 별도 재검토 에이전트는 호출하지 않았다. 결과와 판단 내역은 `review/final-review.md` 및 progress.md에 기록했다. `hashes.json`은 모든 최종 문서 갱신 후 생성한다. 사용자 미저장 변경 덮어쓰기, 장비 숨김, 형상/이벤트 변경, 운영 배포는 수행하지 않았다.
'''
(R/'report-s4-camera.md').write_text(text,encoding='utf-8')
print('Final evidence/report composed')
