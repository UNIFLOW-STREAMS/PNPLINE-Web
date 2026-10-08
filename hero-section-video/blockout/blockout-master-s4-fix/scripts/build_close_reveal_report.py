"""Current S4 evidence and report after the user's f502 scale correction."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parents[1];H=R.parent/'plan/pnpline-s4-camera-revision-handoff-v0.1';Q=R/'review/close-reveal'
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
D=load(R/'review/validation-final.json');A=load(R/'review/states-final.json');B=load(Q/'before-states.json')
check=load(R/'review/reopen-check.json');play=load(R/'review/playback-check.json')
before=load(Q/'red-ship-bounds.json');after=load(Q/'final-ship-bounds.json')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def grid(items,cols,tile=(480,270)):
 w,h=tile;out=Image.new('RGB',(cols*w,math.ceil(len(items)/cols)*(h+30)),'#e9eef1');draw=ImageDraw.Draw(out)
 for i,(label,p) in enumerate(items):
  x=i%cols*w;y=i//cols*(h+30);draw.text((x+8,y+5),label,fill='#18303e',font=small)
  im=ImageOps.contain(Image.open(p).convert('RGB'),tile);out.paste(im,(x+(w-im.width)//2,y+30+(h-im.height)//2))
 return out
grid([('Rejected saved version / f502',Q/'before-frames/f0502.png'),('Corrected master / f502',R/'review/final-continuity/f0502.png')],2).save(Q/'f502-before-after.png')
grid([(f'Corrected f{f}',R/f'review/final-continuity/f{f:04}.png') for f in [456,464,472,480,488,494,499,502,506,510,516,522]],3).save(Q/'approach-sequence.png')
items=[]
for report in play['reports']:items.extend([(report['label']+' / '+str(round(s['time'],2))+'s',R/'review'/s['image']) for s in report['samples']])
grid(items,4,(320,180)).save(Q/'real-time-playback-samples.png')
frames=[456,499,522,555,648];sheet=Image.new('RGB',(1500,1830),'#e9eef1');draw=ImageDraw.Draw(sheet)
regions=[(19,86,1427,981),(17,67,1430,986),(17,67,1430,985),(17,67,1430,985),(18,55,1430,987)]
for row,f in enumerate(frames):
 for col,label in enumerate([f'K{row+1} board',f'Rejected saved version / f{f}',f'Corrected master / f{f}']):draw.text((col*500+9,row*366+7),label,fill='#18303e',font=small)
 images=[Image.open(H/f'references/s4-0{row+1}.png').crop(regions[row]),Image.open(Q/f'before-frames/f{f:04}.png'),Image.open(R/f'review/final-continuity/f{f:04}.png')]
 for col,im in enumerate(images):
  tile=ImageOps.contain(im,(492,326));sheet.paste(tile,(col*500+4+(492-tile.width)//2,row*366+34+(326-tile.height)//2))
sheet.save(R/'review/K1-K5-comparison.png')
im=Image.new('RGB',(1200,980),'#edf1f3');dr=ImageDraw.Draw(im)
def xy(x,y):return int(260+(x+10)*8.5),int(520-y*8.5)
dr.text((22,16),'Corrected S4 path / approved existing S5 join',fill='#18303e',font=font)
for x in range(-20,81,10):dr.line([xy(x,-42),xy(x,56)],fill='#dbe0e4');dr.text(xy(x,-44),str(x),fill='#6b7a82',font=small)
for y in range(-40,51,10):dr.line([xy(-20,y),xy(80,y)],fill='#dbe0e4')
dr.rectangle([xy(-17,12),xy(17,4)],fill='#c4cbd0',outline='#576975',width=2)
dr.rectangle([xy(-7,2.6),xy(7,-2.6)],fill='#205472');dr.rectangle([xy(36,39),xy(68,25)],fill='#b1c7b7',outline='#42674d',width=2)
dr.line([xy(0,9),xy(26,9),xy(33,17),xy(36,29)],fill='#687b88',width=7)
for x in [-2,3.5]:
 for y in [5,12]:
  a,b=xy(x,y);dr.rectangle((a-4,b-4,a+4,b+4),fill='#b28e29')
for lo,hi,color in [(456,648,'#d75531'),(648,672,'#466acb')]:dr.line([xy(*r['us_camera'][:2]) for r in D['quarter_frames'] if lo<=r['frame']<=hi],fill=color,width=3)
for f,k in zip(frames,['K1','K2','K3','K4','K5']):
 r=next(r for r in D['quarter_frames'] if r['frame']==f);a,b=xy(*r['us_camera'][:2]);dr.ellipse((a-5,b-5,a+5,b+5),fill='#d75531');dr.text((a+8,b-12),f'{k} f{f}',fill='#9b361e',font=small)
dr.text(xy(39,35),'WAREHOUSE',fill='#264c33',font=font);dr.text(xy(-15,10),'QUAY',fill='#18303e',font=small);dr.text(xy(-6,1),'SHIP',fill='white',font=small)
dr.text((20,920),'Orange: S4   Blue: existing S5 join   Fixed asset layout retained',fill='#18303e',font=font)
dr.text((20,951),'This follow-up changes only f458-521; f522 onward is identical to the saved input.',fill='#18303e',font=small);im.save(R/'review/camera-path.png')
grid([(f'f{f} / '+label,R/f'review/final-continuity/f{f:04}.png') for f,label in [(581,'cargo / pole sweep'),(602,'cargo / receiving bed'),(618,'cab / pole sweep'),(632,'seated cargo'),(648,'spreader gap / exit road'),(672,'original S5')]],3).save(R/'review/occlusion-review.png')
(R/'camera-before-after.json').write_text(json.dumps(D,indent=2),encoding='utf-8')
changes={k:[f for f in range(1393) if A['frames'][f][k]!=B['frames'][f][k]] for k in ['camera','target','lens','noncamera']}
(Q/'correction-diff.json').write_text(json.dumps({'baseline_sha256':'85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de','final_sha256':check['final_blend_sha256'],'changes':changes,'f502':{'before_bounds':before['502'],'after_bounds':after['502']}},indent=2),encoding='utf-8')
def size(b):return f'{100*(b[2]-b[0]):.1f}% × {100*(b[3]-b[1]):.1f}%'
def dist(row):return math.dist([row['camera'][i][3] for i in range(3)],[row['ship'][i][3] for i in range(3)])
review=(Q/'final-review.md').read_text(encoding='utf-8') if (Q/'final-review.md').exists() else '독립 최종 검토 대기. 아직 최종 완료 판정을 내리지 않음.'
metrics='\n'.join(f'| {f} | {size(before[str(f)])} | {size(after[str(f)])} |' for f in [494,499,502,506,510])
text=f'''# S4 카메라 — f502 원경화 재수정

사용자가 지적한 f502의 과도한 원경화는 이전 수정에 남아 있었다. 이전 AC-2 완료 판정을 철회하고, 선박을 주요 전경으로 유지하도록 **f458–521만 다시 수정**했다. 현재 파일은 `master-s4-fix.blend`, SHA256 `{check['final_blend_sha256']}`이다.

## 결과

- `review/close-reveal/f502-before-after.png`: 지적한 정확한 프레임의 전후 비교.
- `preview/s4-after.mp4`: 현재 S4, f456–648, 12fps, 960×540, 193프레임.
- `preview/s3-tail_s4_s5-head.mp4`: f444–696, 253프레임, 12fps.
- `preview/s4-close-reveal-before.mp4`: 이번에 거부된 저장본. `s4-before.mp4`는 더 이전 최초 S4 기준본의 이력이다.
- `review/K1-K5-comparison.png`: 보드 / 이번 수정 전 / 현재 수정 후. 보드 테두리와 메모를 제외하고 비율을 유지했다.

## 원인·변경

이전 검사는 선박이 잘리지 않고 폭24% 이상인지 확인했으나, 전경의 비중을 잃는 문제를 잡지 못했다. f499 후퇴·상승 `(18,-38,28)`과 32mm 광각화가 겹쳤다. 이번에는 `(0,-30,14)`, 타깃 `(6,6,2)`, 35mm로 바꾸어 항만과 목적지를 선박 뒤로 배치했다. 줌만으로 확대하지 않고 실제 위치·고도·방향을 함께 바꿨다. f502의 카메라-선박 원점 거리는 {dist(B['frames'][502]):.2f}m에서 {dist(A['frames'][502]):.2f}m로 감소했다.

선박 투영 경계상자 폭×높이(가시 픽셀 면적과 다름):

| 프레임 | 이번 수정 전 | 수정 후 |
|---|---|---|
{metrics}

새 기준은 f494–506에서 선박 폭42%·높이35% 이상, f486–510에서 전체 경계1.5% 여백이다. 보드의 큰 전경 선박과 프록시 비례를 보고 수정 전에 정했다. 실제 렌더 및 연속 구간을 함께 검토했으며 수치 통과를 미적 판정과 혼동하지 않는다.

K1에서 기존 롤·속도를 이어받아 f480까지 줄인다. K2 내륙 타깃의 x접선을 0으로 바꿔 정박 직전에 선미가 잘리는 넘침도 제거했다. 위치는 관찰 지점에서 정지하지 않으며 f522의 기존 카메라와 접선에 합류한다.

## 보존·차이

입력은 최신 사용자 저장본 `inputs/before-close-reveal.blend`, SHA256 `85c2431c6cb26060b768d38ce1d5e3a859c000d5ae6e72a75a47ab51cccd47de`다. 이전 납품본과 평가 상태는 같았고 최신 저장 상태를 기반으로 작업했다. 최초 `inputs/base-s4.blend`도 원래 해시로 보존했다. HEAD는 기존6079b392d7de54509ed50454ddd2745273cc0078이며 되돌리지 않았다. 사용자 확인대로 19-35-47 녹화는 같은 카메라를 슬라이더로 촬영한 것이므로 녹화 초수로 리타이밍하지 않았다.

- 이번 변경은 카메라·타깃 f458–521의64프레임, 렌즈 f481–521의41프레임이다. f0–457 및 f522–1392는 이번 입력과 정확히 같다.
- 전체 S4 작업을 최초 입력과 비교하면 카메라·타깃 f458–671, 렌즈213프레임 변경. 사용자 승인된 S5 f649–671 접합을 유지하고 f672 이후 최초 원본과 정확히 같다.
- 전체1393프레임의 비카메라 변화0. 형상·재질·동작·부모관계·이벤트·FPS·구간·클립 설정 동일.
- 정박510, 인양532 이후, 상승완료555, 부두이송599, 안착632, 장치재상승637 이후, 차량출발649 보존.
- 선체는 보드보다 짧고 선교가 낮은 기존 프록시다. K2는 거의 선측 구도이며 보드의 긴 선수 사선 비례를 그대로 복제하지 않는다. 창고 오른쪽 일부가 잘리지만 창고와 연결 도로는 식별된다. 자산을 늘리거나 옮기지 않았다.
- f522 이후 카메라는 동일하다. K3 동일 화물·받을 차량, K4 인양/이송/하강, K5 장치 간격·운전석·남겨진 배·진출 도로를 유지한다. 중간 기둥 스침과 K5 창고 이탈도 기존대로 남는다. 가림 표본은 `occlusion-review.png` 및 `validation-final.json`에 있다.

## 검증

기존24 + S4 9 + 새 구도4 + 검사 유틸4 = **41개 검사**. RED는 f494 폭29.80% <42%로 실패했고 최초 후보는 f509 선미 여백1.284% <1.5%로 실패했다. 타깃 접선 수정 후 모두 GREEN. 전체 검사의 첫 실행에는 출력 라벨을 중복 전달한 호출 오류가 있어 실행 인수를 고쳐 재검사했다(`test-invocation-error.log`). 시험 기준 완화 없음.

f452–684의 1/4프레임 {len(D['quarter_frames'])}표본에서 점+0.12m OBB 충돌0, 최대 이동 {max(r.get('speed',0) for r in D['quarter_frames']):.4f}m/frame, 최대 최단 회전 {max(r.get('angular_speed',0) for r in D['quarter_frames']):.4f}deg/frame. 유한 표본 검사는 연속 충돌의 수학적 증명이 아니다. 기존 가림 기준과 전 구간 연속성 검사도 새로 통과했다.

새 Blender 프로세스의 대표 {len(check['reopen_rgb_identical'])}프레임 RGB가 출력 프레임과 완전히 일치한다. `revise_close_reveal.py` 재실행은 저장본의 전체1393 평가 상태·메타데이터와 정확히 같다. ffprobe로 네 영상의 프레임 수/해상도/12fps 확인. Chrome에서 seek 없이 1배속 완주: {', '.join(r['label']+' '+str(r['result']['decoded'])+' decoded / '+str(r['result']['dropped'])+' display drops' for r in play['reports'])}. 실제 재생 표본은 `review/close-reveal/real-time-playback-samples.png`다.

## AC

| AC | 상태·증거 |
|---|---|
| 1 기준 | 충족: 거부된 f502와 저장본 일치, 최신 저장본·해시·상태 보존 |
| 2 입항·공개 | 재수정: f502 선박 {size(before['502'])} → {size(after['502'])}, 보드 대조·연속 확인 |
| 3 준비·인양 | 충족: f522 기존 준비 구도에 연속 합류, 이후 카메라·이벤트 동일 |
| 4 인계·가림 | 기존 충족 상태 보존: f522 이후 동일, S4 9개 회귀 통과; 기둥 스침은 공개 |
| 5 출발·S5 | 승인된 접합 보존: 이번 추가 S5 변경 없음 |
| 6 동일성 | 충족: 이번 f458–521 이외 카메라, 전체 비카메라 정확히 동일 |
| 7 연속·접근 | 유한 검사 범위 충족: 전체 회귀·929개 서브프레임·1배속 재생 |
| 8 재현 | 충족: 재개방17화면 RGB·소스1393상태·ffprobe·해시 |

최종 검토 결과(`review/close-reveal/final-review.md`):

{review}

## 재현·환경

Blender5.1.0(adfe2921d5f3), 기존 Python/Pillow, ffmpeg7.1, Chrome/Playwright 사용. 추가 설치·유료 호출·Git 커밋·push·PR·웹 배포 없음. 최종 파일을 새 Blender 창의 f502에 열었다.

이 버전 폴더에서 별도 파일로 재현할 수 있다. `revise_s4.py`는 이전 단계 이력 소스이며 현재 입력은 최신 보존본이다.

```powershell
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup inputs/before-close-reveal.blend --python-exit-code 1 --python scripts/revise_close_reveal.py -- review/close-reveal/reproduced.blend
& 'C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe' --background --factory-startup master-s4-fix.blend --python-exit-code 1 --python scripts/test_close_reveal.py -- final
& 'C:\\ProgramData\\miniconda3\\python.exe' -X utf8 scripts/reopen_check.py
& 'C:\\ProgramData\\miniconda3\\python.exe' -X utf8 scripts/build_report.py
```

실제 로그: `review/close-reveal/`, 재개방 하위 프로세스 `logs/`. 결정 기록: `progress-close-reveal.md`. `hashes.json`은 최종 검토·문서 이후 갱신한다. 이전 완료 보고는 `review/close-reveal/previous-report-s4-camera.md`에 이력으로 남기며 현재 판정으로 쓰지 않는다.
'''
(R/'report-s4-camera.md').write_text(text,encoding='utf-8')
print('Current close-reveal report and evidence written')
