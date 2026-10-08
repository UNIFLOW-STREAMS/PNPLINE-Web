from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
d=json.loads((R/'review/validation-target.json').read_text(encoding='utf-8'))
im=Image.new('RGB',(1440,848),'#edf1f3');draw=ImageDraw.Draw(im)
for i,(label,folder) in enumerate([('Original B45 / fixed-boundary alternative','before'),('Target B45 / S5 join approval required','after')]):
 draw.text((i*720+12,10),label,fill='#182d3a',font=font);im.paste(Image.open(R/'review'/folder/'f0648.png').resize((720,405)),(i*720,40))
draw.text((18,465),'Top view in US local space: fixed assets; dashed S5 path remains original',fill='#182d3a',font=font)
def p(x,y):return (int(80+(x+25)*13),int(800-(y+20)*4))
draw.rectangle([p(-17,12),p(17,4)],fill='#c6cbd0',outline='#666e74',width=2)
draw.rectangle([p(-7,2.6),p(7,-2.6)],fill='#194d69')
draw.rectangle([p(36,39),p(68,25)],fill='#a2b7aa',outline='#356045',width=2)
for x in [-2,3.5]:
 for y in [5,12]:
  px,py=p(x,y);draw.ellipse((px-4,py-4,px+4,py+4),fill='#b6972c')
draw.line([p(0,9),p(26,9),p(33,17),p(36,29)],fill='#657984',width=4)
pts=[p(*r['us_camera'][:2]) for r in d['quarter_frames'] if r['frame']>=456]
draw.line(pts,fill='#e55333',width=3)
for f,label in [(456,'K1 456'),(499,'K2 499'),(522,'K3 522'),(555,'K4 555'),(648,'K5 648')]:
 r=next(r for r in d['quarter_frames'] if r['frame']==f);x,y=p(*r['us_camera'][:2]);draw.ellipse((x-4,y-4,x+4,y+4),fill='#e55333');draw.text((x+8,y-10),label,fill='#9c3420',font=font)
draw.text(p(37,36),'WAREHOUSE',fill='#234933',font=font);draw.text(p(-16,7),'QUAY',fill='#354550',font=font)
im.save(R/'review/b45-proposal.png')
text='''# S4 카메라 수정 — S5 접합 승인용 검토

판정: **재작업 진행 중 / 통합 완료 아님**. 지정 master-s4-fix.blend 원본은 아직 덮어쓰지 않았다. 사용자가 현재 확인할 수 있도록 목표 후보를 별도 Blender 창에 열었다.

## 확인 가능한 결과

- `review/candidate-target.blend`: S4 f458–648 카메라·타깃·렌즈만 변경한 목표안. S5는 원본이므로 f648→649에는 아직 불연속이 있다. Blender 프리뷰 범위는 f456–648이다.
- `preview/s4-target-review.mp4`: 목표안 S4 전체, 960×540 / 12fps / 193프레임 / 16.083초. 양 경계를 포함해 경계 간 시간 16초보다 1프레임 길다.
- `review/candidate-limited.blend`, `preview/s4-boundary-limited.mp4`: f632부터 원본 경로를 유지하는 제한안. 마지막 한 프레임 급복귀가 아니라 f582부터 완만하게 원본 f632에 연결하나, 종료 운전석 가림과 진출 방향 문제는 남는다. AC-5 미충족.
- `preview/s4-before.mp4`, `review/b45-proposal.png`: 같은 조건의 원본과 종료 비교.

## 필요한 추가 수정 범위

**S5 f649–671의 카메라 위치·시선 타깃·렌즈만 접합 조정하고 f672부터 원본으로 정확히 복귀하는 안을 제안한다.** B45에서 목표안은 원본 대비 위치 약 15.906m, 타깃 5.017m, 렌즈 40→32mm 차이다. 접합 전체는 24프레임 간격 = 2초다. f649–671은 23개 수정 키다.

수치 비교: 20프레임 접합 최대 위치 가속도 0.182m/frame², 24프레임 접합 0.130m/frame². 기존 경계 검사 기준 0.15를 고려해 24프레임을 선택했다. 24프레임안 최대 이동 0.825m/frame, 최대 회전 0.958도/frame. 이는 위치·시선 수치 제안이며 **S5 실제 키 수정, 렌더·충돌 검증은 아직 하지 않았다.** 승인 후 접합을 적용하고 S3 말미→S4→S5 연결 영상으로 재검증한다.

선박·크레인·화물·차량·도로·창고의 배치와 동작, f632 안착 / f637 이후 장치 상승 / f649 차량 출발, FPS와 구간 경계는 모두 보존한다.

지시서 6항: “승인 전에는 S3/S5를 바꾸거나 통합 완료로 보고하지 않는다.” 이에 따라 이 범위만 추가 승인 대상으로 남긴다. S3 변경은 필요하지 않다.

## 현재 검증

원본 SHA256: 63e95f15f9ad5b223001021251982266ebe06957a297a5a03e72d732358df976. 입력 14/14 해시 일치, 녹화 상태 동일·슬라이더 촬영 사용자 확인. 기존 테스트 24/24 통과.

새 S4 검사: 원본 5개 실패 → 목표안 8/8 통과. 장비 내부 면을 외부 가림으로 잘못 집계하던 검사 오류는 별도 재현 후 수정했으며 2/2 회귀 시험 통과. 수용 수치는 완화하지 않았다. 수정된 검사로 원본 실패도 다시 확인했다.

전1393프레임 비교에서 비카메라 변화 0, S3/S5 카메라 평가값 변화 0. S4 f452–648의 1/4프레임 간격 카메라 점+0.12m 대 OBB 검사에서 충돌 0. 이 검사는 완전한 연속 체적 충돌 증명은 아니다.

인양 이후 f532–648 모든 정수 프레임에서 화물·트랙터·트레일러 경계상자 크롭 0. f631–648 운전석의 가중 기둥 가림 0%, 화물 최대 3.28%. 표면 레이 표본 수치이며 픽셀 점유율이 아니다. 대표 렌더와 함께 판단했다. S4 전체 최대 이동 1.593m/frame, 최소 회전각 기준 최대 5.533도/frame. 쿼터니언 부호가 바뀌는 행의 raw rotation_difference 값은 360도 동치 문제이므로 원시 1437도/frame 수치를 실제 회전으로 해석하지 않는다.

원본/목표안/제한안 세 영상은 설치된 Chrome에서 seek 없이 1배속 끝까지 재생: 각각 193프레임 디코딩, 드롭 0. 실제 동작의 미적 판정은 대표·연속 프레임 육안 대조와 구분한다.

## AC 상태

AC-1 충족. AC-2~4 S4 후보의 수치·대표 화면 확인, 최종 통합본 확인 예정. AC-5 S5 접합 승인 대기, 미충족. AC-6 현재 후보에서 보존 확인. AC-7 S4 내부 검사 통과, B45 미접합. AC-8 최종 재개방·소스 재현·검토·해시 묶음 대기.

완료 판정은 추가 승인과 최종 통합 검증 후 갱신한다. 커밋·push·PR·배포 없음.
'''
(R/'report-s4-camera.md').write_text(text,encoding='utf-8')
print('Wrote proposal report and B45 comparison')
