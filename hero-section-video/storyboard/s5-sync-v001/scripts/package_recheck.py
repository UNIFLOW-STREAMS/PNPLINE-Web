from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw,ImageFont
from contracts import digest
R=Path(__file__).resolve().parents[1];Q=R/'review/s4-s5-recheck';rec=json.loads((Q/'camera-only-record.json').read_text(encoding='utf8'));run=Path(rec['frames'][0]['after']).parent.parent
assert rec['status']=='complete' and [i['frame'] for i in rec['frames']]==list(range(552,841))
for i in rec['frames']:
 for k in ['before','after']:assert digest(i[k])==i[k+'_sha256']
video=R/'preview/camera-only-diagnostic.mp4';cmd=['ffmpeg','-y','-framerate','12','-start_number','552','-i',str(run/'before/%04d.png'),'-framerate','12','-start_number','552','-i',str(run/'after/%04d.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-frames:v','289','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
with (R/'logs/camera-only-encode.log').open('w') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
c=Image.new('RGB',(1440,960),'white');d=ImageDraw.Draw(c);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
refpath=R.parents[0]/'section-04/s4-05.png';ref=Image.open(refpath).convert('RGB');ref.thumbnail((696,522));c.paste(ref,(12,52));d.text((12,10),'기준: 기존 S4-05 콘티',font=font,fill='black');im=Image.open(run/'after/0648.png').resize((696,392));c.paste(im,(732,52));d.text((732,10),'카메라만 조정한 시험안 · 미채택',font=font,fill='black')
notes=['선박·창고를 함께 담을 수는 있으나 차량이 작아짐.','선박의 화면 점유율과 차량의 후면 관찰 관계가 다름.','현재 배치에서 기존 콘티를 충족한 수정안으로 판정하지 않음.']
for i,t in enumerate(notes):d.text((732,470+i*33),t,font=small,fill='black')
d.text((20,600),'현재 공간 배치 (US_FRAME 평면도) · 실제 좌표에 따른 도식',font=font,fill='black');origin=(70,910);scale=7.1
def pt(x,y):return(origin[0]+x*scale,origin[1]-y*scale)
d.rectangle((*pt(-7,2.6),*pt(7,-2.6)),fill='#487886');d.text((20,933),'선박 중심 (0, 0)',font=small,fill='black')
d.rectangle((*pt(-1.6,10),*pt(5.7,8)),fill='#357ca6');d.line([pt(5.7,9),pt(15,9)],fill='#bb4539',width=5);d.polygon([pt(15,9),pt(13.5,9.7),pt(13.5,8.3)],fill='#bb4539');d.text(pt(0,15),'차량 → +X 출발',font=small,fill='black')
d.rectangle((*pt(36,39),*pt(68,25)),outline='#38513e',width=3);d.text(pt(42,34),'물류센터',font=small,fill='black')
for j,t in enumerate(['선박 중심 (0, 0)','트레일러 시작 (0, 9)','창고 중심 (52, 32)','車·船 약9m / 車·창고 중심 약57m']):d.text((760,675+j*42),t,font=small,fill='black')
img=Q/'recheck-summary.png';c.save(img)
(Q/'review-record.json').write_text(json.dumps({'status':'diagnostic rejected, no master modification','base_sha256':rec['input_base_sha256'],'render_record_sha256':digest(Q/'camera-only-record.json'),'video':str(video),'video_sha256':digest(video),'video_command':cmd,'image':str(img),'image_sha256':digest(img),'reference':str(refpath),'reference_sha256':digest(refpath),'script_sha256':digest(__file__)},indent=2),encoding='utf8')
print('Recheck diagnostic packaged; not an accepted fix')
