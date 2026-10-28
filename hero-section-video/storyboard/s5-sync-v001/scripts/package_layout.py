from pathlib import Path
import json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];P=R/'layout-proposal-v001';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=json.loads((P/'render-full.json').read_text());assert rec['status']=='complete';assert rec['blend_sha256']==sha(P/'s4-s5-layout-proposal-v001.blend');assert [r['frame'] for r in rec['frames']]==list(range(552,949))
for r in rec['frames']:assert sha(r['path'])==r['sha256']
run=Path(rec['frames'][0]['path']).parent
cmd=['ffmpeg','-y','-framerate','12','-start_number','552','-i',str(run/'%04d.png'),'-frames:v','397','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(P/'preview.mp4')]
with (R/'logs/layout-encode.log').open('w') as log:subprocess.run(cmd,check=True,stdout=log,stderr=log)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(P/'preview.mp4')],text=True));st=probe['streams'][0];assert int(st['nb_frames'])==397 and st['r_frame_rate']=='12/1'
(P/'video-probe.json').write_text(json.dumps(probe,indent=2));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
sheet=Image.new('RGB',(1440,960),'#f5f5f2');d=ImageDraw.Draw(sheet)
reference=R.parent/'section-04/s4-05.png'
def place(path,x,y,w,h):
 im=Image.open(path).convert('RGB');im.thumbnail((w,h));sheet.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
place(reference,12,46,696,445);d.text((12,10),'기준: 기존 S4-05 콘티',font=font,fill='black')
place(run/'0648.png',732,46,696,392);d.text((732,10),'새 배치 제안 · S4 종료 f648',font=font,fill='black')
place(run/'0672.png',12,534,696,392);d.text((12,497),'연결 확인 · S5 출발 f672',font=font,fill='black')
place(run/'0766.png',732,534,696,392);d.text((732,497),'동선 확인 · 선회 중 f766',font=font,fill='black')
d.text((18,933),'원본 보존 · 실제 3D 배치 재작업 · f552–948 검토용 · 최종 마스터 미채택',font=small,fill='#333333');sheet.save(P/'comparison.png')
contact=Image.new('RGB',(1440,4*290),'white');d=ImageDraw.Draw(contact)
for i,f in enumerate([552,576,600,624,648,672,720,766,810,842,890,948]):
 x=(i%3)*480;y=(i//3)*290;im=Image.open(run/f'{f:04d}.png').resize((480,270));contact.paste(im,(x,y));d.text((x+8,y+270),f'f{f}',font=small,fill='black')
contact.save(P/'contact.png')
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>S4→S5 배치·동선 제안</title><style>body{margin:24px auto;max-width:1100px;background:#16191d;color:#eee;font:17px/1.6 sans-serif}h1{font-size:26px}video,img{width:100%;display:block;margin:18px 0}a{color:#9ed5ff}.note{padding:14px;background:#30383f}video{max-height:70vh}</style><h1>S4-05 기준 · 별도 배치·동선 제안</h1><p>선박 왼쪽 / 차량 후면 가운데 오른쪽 / 연결 도로와 창고 오른쪽 위. 영상은 저장된 제안본의 f552–948, 12fps 원속도입니다.</p><p class="note">원본 마스터는 보존했습니다. 이 파일은 해당 구간 검토용이며, S1–S3·후속 S6–S7과의 전체 마스터 접합은 포함하지 않습니다. 최종 채택 대기.</p><video id="proposal" controls preload="metadata" src="preview.mp4"></video><p><a href="s4-s5-layout-proposal-v001.blend">Blender 제안본</a> · <a href="report.md">검증 보고서</a></p><img src="comparison.png"><img src="contact.png"></html>'''
html=html.replace('<video id="proposal"', '<button type="button" onclick="const v=document.getElementById(\'proposal\');v.currentTime=0;v.playbackRate=1;v.dataset.started=performance.now();v.onended=()=>{v.dataset.elapsed=(performance.now()-Number(v.dataset.started))/1000};v.play();">처음부터 원속도 재생</button><video id="proposal"')
(P/'review.html').write_text(html,encoding='utf8')
(P/'package-record.json').write_text(json.dumps({'blend_sha256':rec['blend_sha256'],'render_record_sha256':sha(P/'render-full.json'),'video_sha256':sha(P/'preview.mp4'),'video_frames':397,'video_duration_s':float(st['duration']),'video_command':cmd,'reference_sha256':sha(reference),'comparison_sha256':sha(P/'comparison.png'),'contact_sha256':sha(P/'contact.png'),'script_sha256':sha(__file__)},indent=2),encoding='utf8')
print('PACKAGED',P)
