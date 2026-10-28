from pathlib import Path
import json,sys,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from contracts import *
record=json.loads((R/'render-record.json').read_text(encoding='utf8'));selection=json.loads((R/'storyboard-selection.json').read_text(encoding='utf8'))
validate_run(record);validate_selection(selection,record)
font=Path('C:/Windows/Fonts/malgun.ttf');bold=Path('C:/Windows/Fonts/malgunbd.ttf')
def f(size,b=False):return ImageFont.truetype(str(bold if b else font),size)
panels=[];images={i['frame']:i for i in record['images']};rp=Path(record['output_dir'])/'render-record.json'
for p in selection['panels']:
 i=images[p['frame']];validate_role(p['id'],i['state']['metrics']);im=Image.open(i['path']).convert('RGB');w,h=im.size
 panel=Image.new('RGB',(w+32,h+160),'white');panel.paste(im,(16,16));d=ImageDraw.Draw(panel);d.rectangle((15,15,w+16,h+16),outline='#202020',width=1)
 d.text((18,h+29),f"{p['id']}  /  {p['role']}",font=f(23,True),fill='#101010')
 d.text((18,h+66),p['action'],font=f(17),fill='#202020')
 d.text((18,h+98),f"f{p['frame']}  ·  본편 {p['master_seconds']:.3f}s  ·  프리뷰 {p['preview_seconds']:.3f}s  ·  CAM_MASTER",font=f(16),fill='#555555')
 d.text((18,h+124),'구조 검토용 원본 프레임 초안 · 선화/최종 승인 전',font=f(15),fill='#6b552d')
 path=R/'panels'/f"{p['id']}-draft-f{p['frame']}.png";panel.save(path)
 item={**p,'path':str(path),'sha256':digest(path),'raw_path':i['path'],'raw_sha256':i['sha256'],'source':record['source'],'scene':i['scene'],'camera':i['camera'],'camera_state':i['camera_state'],'actual_state':i['state'],'git_head':record['git_head'],'fps':record['fps'],'fps_base':record['fps_base'],'preview_start':record['preview_start'],'render_record':{'path':str(rp),'sha256':digest(rp)},'image_region':[16,16,w,h],'scaling':[1,1],'padding':[16,16,16,144],'resolution':[w,h],'pixel_aspect':record['render']['pixel_aspect'],'expression':{'method':'unaltered colored raw structural draft','line_art':None,'config_path':str(R/'config.json'),'config_sha256':digest(R/'config.json')},'approved':False}
 validate_panel(item,record);panels.append(item)
contact=Image.new('RGB',(1440,1640),'#eeeeea');d=ImageDraw.Draw(contact);d.text((28,20),'S5 실제 프레임 · 구조 검토 후보',font=f(32,True),fill='#222222');d.text((28,69),'마스터 동작 무수정 / 03·03A 역할 재선정 / 선택·표현 방향 확인 전',font=f(20),fill='#555555')
for n,p in enumerate(panels):
 im=Image.open(p['path']);im.thumbnail((688,496));contact.paste(im,(24+(n%2)*716,112+(n//2)*504))
contact.save(R/'review/candidates.png')
manifest={'status':'frame candidates awaiting user selection','source':record['source'],'run_id':record['run_id'],'selection_path':str(R/'storyboard-selection.json'),'selection_sha256':digest(R/'storyboard-selection.json'),'panels':panels,'packager_sha256':digest(__file__),'font_sha256':{str(font):digest(font),str(bold):digest(bold)}}
(R/'storyboard-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
rate=f"{record['fps']}/{record['fps_base']}"
video=R/'preview/main.mp4'
cmd=['ffmpeg','-y','-framerate',str(record['fps']/record['fps_base']),'-start_number',str(record['preview_start']),'-i',str(Path(record['output_dir'])/'%04d.png'),'-frames:v',str(len(record['expected_frames'])),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
with (R/'logs/encode.log').open('w',encoding='utf8') as log:subprocess.run(cmd,stdout=log,stderr=log,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
(R/'review/video-probe.json').write_text(json.dumps(probe,indent=2),encoding='utf8')
(R/'preview/video-record.json').write_text(json.dumps({'path':str(video),'sha256':digest(video),'command':cmd,'source':record['source'],'render_record_sha256':digest(rp),'frames':record['expected_frames'],'fps':record['fps'],'fps_base':record['fps_base'],'preview_start':record['preview_start'],'ffmpeg_version':subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0]},indent=2),encoding='utf8')
print('PACKAGED',len(panels),'roles validated; preview',video)
